/* Chat de CoAgrix: enviar, editar, eliminar, responder y actualizarse solo.
   El servidor manda cada mensaje ya listo (ver serialize_message en
   message_controller.py); aquí solo se dibuja. Todo el texto entra al DOM con
   textContent, nunca como HTML. */
(() => {
    const root = document.getElementById('chat-root');
    if (!root) return;

    const cfg = {
        otro: root.dataset.otroId,
        otroNombre: root.dataset.otroNombre,
        base: root.dataset.baseUrl,
        csrf: root.dataset.csrf,
        editWindow: Number(root.dataset.editWindow) || 15,
    };
    const box = document.getElementById('chat-box');
    const list = document.getElementById('messages');
    const convList = document.getElementById('conversation-list');
    const form = document.getElementById('chat-form');
    const input = form.elements.contenido;
    const sendBtn = form.querySelector('button[type="submit"]');
    const ctxBar = document.getElementById('composer-context');
    const ctxTitle = ctxBar.querySelector('strong');
    const ctxText = ctxBar.querySelector('span');

    const state = { messages: [], conversations: [] };
    let replyTo = null;
    let editing = null;
    let busy = false;
    let lastSig = '';
    let lastConvSig = '';
    let requestSeq = 0;
    let appliedSeq = 0;

    /* ---------- utilidades ---------- */
    function el(tag, cls, text) {
        const node = document.createElement(tag);
        if (cls) node.className = cls;
        if (text != null) node.textContent = text;
        return node;
    }
    const pad = n => String(n).padStart(2, '0');
    const hhmm = d => `${pad(d.getHours())}:${pad(d.getMinutes())}`;
    const parse = s => new Date(s);

    function dayLabel(d) {
        const today = new Date();
        const yesterday = new Date();
        yesterday.setDate(today.getDate() - 1);
        if (d.toDateString() === today.toDateString()) return 'Hoy';
        if (d.toDateString() === yesterday.toDateString()) return 'Ayer';
        return d.toLocaleDateString('es-CO', { day: 'numeric', month: 'long', year: 'numeric' });
    }

    function notify(message) {
        let toast = document.getElementById('chat-toast');
        if (!toast) {
            toast = el('div', 'chat-toast');
            toast.id = 'chat-toast';
            toast.setAttribute('role', 'alert');
            document.body.append(toast);
        }
        toast.textContent = message;
        toast.classList.add('show');
        clearTimeout(notify.timer);
        notify.timer = setTimeout(() => toast.classList.remove('show'), 4000);
    }

    /* ---------- red ---------- */
    async function api(path, params, method = 'POST') {
        const options = {
            method,
            credentials: 'same-origin',
            headers: { 'X-CSRFToken': cfg.csrf, 'X-Requested-With': 'fetch' },
        };
        if (params) options.body = new URLSearchParams(params);
        const res = await fetch(cfg.base + path, options);
        if (res.redirected) { location.reload(); throw new Error('Sesión expirada.'); }
        let payload = null;
        try { payload = await res.json(); } catch (_) { /* respuesta no JSON */ }
        if (!res.ok) throw new Error((payload && payload.error) || 'Ocurrió un error. Intenta de nuevo.');
        return payload;
    }

    /* Pide el estado del chat y lo aplica, descartando respuestas viejas que
       lleguen después de otra más reciente. */
    async function sync(path, params, method, forceScroll) {
        const seq = ++requestSeq;
        const payload = await api(path, params, method);
        if (seq < appliedSeq) return payload;
        appliedSeq = seq;
        apply(payload, forceScroll);
        return payload;
    }

    function apply(payload, forceScroll) {
        const nearBottom = box.scrollHeight - box.scrollTop - box.clientHeight < 90;
        const sig = JSON.stringify(payload.messages);
        if (sig !== lastSig) {
            lastSig = sig;
            state.messages = payload.messages;
            renderMessages();
            if (forceScroll || nearBottom) box.scrollTop = box.scrollHeight;
        }
        const convSig = JSON.stringify(payload.conversations);
        if (convSig !== lastConvSig) {
            lastConvSig = convSig;
            state.conversations = payload.conversations;
            renderConversations();
        }
    }

    /* ---------- dibujo ---------- */
    function emptyState() {
        const wrap = el('div', 'empty-conversation');
        wrap.append(el('span', null, '💬'), el('h2', null, 'Aún no hay mensajes'),
            el('p', null, 'Escribe el primero para iniciar la conversación.'));
        return wrap;
    }

    function renderMessages() {
        closeMenu();
        list.replaceChildren();
        if (!state.messages.length) { list.append(emptyState()); return; }
        let lastDay = null;
        state.messages.forEach(m => {
            const date = parse(m.fecha);
            if (date.toDateString() !== lastDay) {
                lastDay = date.toDateString();
                list.append(el('div', 'date-divider', dayLabel(date)));
            }
            list.append(bubble(m, date));
        });
    }

    function bubble(m, date) {
        const b = el('div', 'bubble' + (m.mio ? ' me' : '') + (m.eliminado ? ' deleted' : ''));
        b.id = 'msg-' + m.id;

        if (m.respuesta) {
            const quote = el('button', 'bubble-quote');
            quote.type = 'button';
            quote.append(el('strong', null, m.respuesta.autor),
                el('span', null, m.respuesta.eliminado ? '🚫 Mensaje eliminado' : m.respuesta.contenido));
            quote.addEventListener('click', () => jumpTo(m.respuesta.id));
            b.append(quote);
        }

        const text = m.eliminado
            ? (m.mio ? '🚫 Eliminaste este mensaje' : '🚫 Este mensaje fue eliminado')
            : m.contenido;
        b.append(el('div', 'bubble-text', text));

        const meta = el('small', 'bubble-meta');
        if (m.editado) meta.append(el('span', 'edited', 'editado'));
        meta.append(el('time', null, hhmm(date)));
        if (m.mio && !m.eliminado) {
            const ticks = el('span', 'ticks' + (m.leido ? ' read' : ''), m.leido ? '✓✓' : '✓');
            ticks.title = m.leido ? 'Leído' : 'Enviado';
            meta.append(ticks);
        }
        b.append(meta);

        const menuBtn = el('button', 'bubble-menu-btn', '▾');
        menuBtn.type = 'button';
        menuBtn.setAttribute('aria-label', 'Opciones del mensaje');
        menuBtn.addEventListener('click', e => { e.stopPropagation(); showMenu(menuBtn, messageActions(m)); });
        b.append(menuBtn);
        return b;
    }

    function renderConversations() {
        convList.replaceChildren();
        state.conversations.forEach(c => {
            const active = String(c.otro_usuario_id) === cfg.otro;
            const link = el('a', 'message-card' + (active ? ' active' : '') + (c.fijado ? ' pinned' : ''));
            link.href = cfg.base + c.otro_usuario_id;
            const head = el('span', 'message-head');
            const when = c.ultima_fecha ? parse(c.ultima_fecha) : null;
            head.append(el('strong', null, (c.fijado ? '📌 ' : '') + c.nombre),
                el('time', null, when ? `${pad(when.getDate())}/${pad(when.getMonth() + 1)}` : ''));
            const copy = el('span', 'message-copy');
            copy.append(head, el('small', null, (c.fijado ? 'Administración · ' : '') + c.email),
                el('p', null, c.ultimo_mensaje || 'Sin mensajes todavía.'));
            link.append(el('span', 'message-avatar', (c.nombre || '?')[0].toUpperCase()), copy);
            if (c.no_leidos && !active) link.append(el('span', 'unread-badge', c.no_leidos));
            convList.append(link);
        });
    }

    function jumpTo(id) {
        const target = document.getElementById('msg-' + id);
        if (!target) return;
        target.scrollIntoView({ block: 'center', behavior: 'smooth' });
        target.classList.add('flash');
        setTimeout(() => target.classList.remove('flash'), 1400);
    }

    /* ---------- menú flotante ---------- */
    let menu = null;

    function closeMenu() {
        if (menu) { menu.remove(); menu = null; }
    }

    function showMenu(anchor, items) {
        closeMenu();
        menu = el('div', 'chat-menu');
        menu.setAttribute('role', 'menu');
        items.forEach(item => {
            const option = el('button', 'chat-menu-item' + (item.danger ? ' danger' : ''), item.label);
            option.type = 'button';
            option.setAttribute('role', 'menuitem');
            option.addEventListener('click', () => { closeMenu(); item.run(); });
            menu.append(option);
        });
        document.body.append(menu);
        const a = anchor.getBoundingClientRect();
        const m = menu.getBoundingClientRect();
        const left = Math.min(Math.max(8, a.right - m.width), window.innerWidth - m.width - 8);
        const top = a.bottom + m.height + 8 > window.innerHeight ? a.top - m.height - 4 : a.bottom + 4;
        menu.style.left = left + 'px';
        menu.style.top = Math.max(8, top) + 'px';
    }

    document.addEventListener('click', closeMenu);
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(); });
    box.addEventListener('scroll', closeMenu);
    window.addEventListener('resize', closeMenu);

    /* ---------- acciones sobre mensajes ---------- */
    function messageActions(m) {
        const items = [];
        if (!m.eliminado) {
            items.push({ label: 'Responder', run: () => startReply(m) });
            items.push({ label: 'Copiar', run: () => copyText(m.contenido) });
            if (m.puede_editar) items.push({ label: 'Editar', run: () => startEdit(m) });
        }
        items.push({ label: 'Eliminar para mí', danger: true, run: () => removeMessage(m, 'mi') });
        if (m.mio && !m.eliminado) {
            items.push({ label: 'Eliminar para todos', danger: true, run: () => removeMessage(m, 'todos') });
        }
        return items;
    }

    async function removeMessage(m, modo) {
        const question = modo === 'todos'
            ? '¿Eliminar este mensaje para todos? La otra persona ya no podrá leerlo.'
            : '¿Eliminar este mensaje solo para ti? La otra persona lo seguirá viendo.';
        if (!confirm(question)) return;
        try {
            if ((editing && editing.id === m.id) || (replyTo && replyTo.id === m.id)) clearContext(true);
            await sync(`mensaje/${m.id}/eliminar`, { modo }, 'POST', false);
        } catch (err) { notify(err.message); }
    }

    function copyText(text) {
        const fallback = () => {
            const area = el('textarea');
            area.value = text;
            document.body.append(area);
            area.select();
            try { document.execCommand('copy'); notify('Mensaje copiado.'); } catch (_) { notify('No se pudo copiar.'); }
            area.remove();
        };
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(() => notify('Mensaje copiado.'), fallback);
        } else {
            fallback();
        }
    }

    /* ---------- caja de escritura (responder / editar) ---------- */
    function autosize() {
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 140) + 'px';
    }

    function showContext(title, text) {
        ctxTitle.textContent = title;
        ctxText.textContent = text;
        ctxBar.hidden = false;
    }

    function clearContext(clearText) {
        if (editing && clearText !== false) input.value = '';
        replyTo = null;
        editing = null;
        ctxBar.hidden = true;
        sendBtn.textContent = 'Enviar';
        autosize();
    }

    function startReply(m) {
        if (editing) input.value = '';
        editing = null;
        replyTo = m;
        sendBtn.textContent = 'Enviar';
        showContext(`Respondiendo a ${m.mio ? 'Tú' : cfg.otroNombre}`, m.contenido);
        input.focus();
    }

    function startEdit(m) {
        replyTo = null;
        editing = m;
        input.value = m.contenido;
        sendBtn.textContent = 'Guardar';
        showContext('Editando mensaje', `Tienes ${cfg.editWindow} minutos desde que lo enviaste`);
        autosize();
        input.focus();
        input.setSelectionRange(input.value.length, input.value.length);
    }

    ctxBar.querySelector('button').addEventListener('click', () => { clearContext(true); input.focus(); });

    input.addEventListener('input', autosize);
    input.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
            e.preventDefault();
            form.requestSubmit();
        } else if (e.key === 'Escape' && (editing || replyTo)) {
            clearContext(true);
        }
    });

    form.addEventListener('submit', async e => {
        e.preventDefault();
        const text = input.value.trim();
        if (!text || busy) return;
        busy = true;
        sendBtn.disabled = true;
        try {
            if (editing) {
                await sync(`mensaje/${editing.id}/editar`, { contenido: text }, 'POST', false);
            } else {
                const params = { contenido: text };
                if (replyTo) params.respuesta_a_id = replyTo.id;
                await sync(`${cfg.otro}/enviar`, params, 'POST', true);
            }
            input.value = '';
            clearContext(false);
        } catch (err) {
            notify(err.message);
        } finally {
            busy = false;
            sendBtn.disabled = false;
            input.focus();
        }
    });

    /* ---------- menú ⋮ del encabezado: historial de citas y vaciar conversación ---------- */
    const historyModal = document.getElementById('history-modal');
    if (historyModal) {
        const close = () => { historyModal.hidden = true; };
        historyModal.querySelector('[data-history-close]').addEventListener('click', close);
        historyModal.addEventListener('click', e => { if (e.target === historyModal) close(); });
        document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
    }

    const optionsBtn = document.getElementById('chat-options');
    if (optionsBtn) {
        optionsBtn.addEventListener('click', e => {
            e.stopPropagation();
            const items = [];
            if (historyModal) {
                const pending = Number(historyModal.dataset.pending) || 0;
                items.push({
                    label: `Historial de citas (${historyModal.dataset.count})` + (pending ? ` · ${pending} pendiente${pending === 1 ? '' : 's'}` : ''),
                    run: () => { historyModal.hidden = false; },
                });
            }
            items.push({
                label: 'Vaciar conversación', danger: true, run: async () => {
                    if (!confirm('¿Vaciar la conversación? Solo se borrará para ti; la otra persona conserva sus mensajes.')) return;
                    try { clearContext(true); await sync(`${cfg.otro}/vaciar`, {}, 'POST', true); } catch (err) { notify(err.message); }
                },
            });
            showMenu(optionsBtn, items);
        });
    }

    /* ---------- actualización automática ---------- */
    let polling = false;
    async function poll() {
        if (document.hidden || polling || busy) return;
        polling = true;
        try { await sync(`${cfg.otro}/lista`, null, 'GET', false); } catch (_) { /* se reintenta en el próximo ciclo */ } finally { polling = false; }
    }
    setInterval(poll, 3000);
    document.addEventListener('visibilitychange', () => { if (!document.hidden) poll(); });

    /* ---------- arranque ---------- */
    apply(JSON.parse(document.getElementById('chat-data').textContent), true);
    autosize();
})();
