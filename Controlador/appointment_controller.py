from datetime import date, datetime

from flask import Blueprint, abort, flash, redirect, request, session, url_for

from Modelo.appointment import (accept_appointment, cancel_appointment, complete_appointment,
    create_appointment, create_notification, get_appointment, has_schedule_conflict,
    reject_appointment, user_participates)
from Modelo.user import get_user_by_id

appointment_bp = Blueprint('appointment', __name__, url_prefix='/citas')
MAX_APPOINTMENTS_PER_REQUEST = 10


def _conversation_redirect(user_id):
    return redirect(url_for('message.conversation_route', otro_usuario_id=user_id))


@appointment_bp.route('/crear/<int:otro_usuario_id>', methods=['POST'])
def create_route(otro_usuario_id):
    if not session.get('user_id'):
        return redirect(url_for('auth.login_page'))
    user_id = session['user_id']
    if user_id == otro_usuario_id or not get_user_by_id(otro_usuario_id):
        abort(403)
    dates = request.form.getlist('fecha'); times = request.form.getlist('hora')
    places = request.form.getlist('lugar'); reasons = request.form.getlist('motivo')
    notes = request.form.getlist('mensaje')
    total = len(dates)
    if not total or total > MAX_APPOINTMENTS_PER_REQUEST or not (len(times) == len(reasons) == total):
        flash(f'Envía entre 1 y {MAX_APPOINTMENTS_PER_REQUEST} citas.', 'error'); return _conversation_redirect(otro_usuario_id)
    places += [''] * (total - len(places)); notes += [''] * (total - len(notes))

    # Se valida todo antes de guardar: si una cita falla, no se crea ninguna.
    parsed, seen = [], set()
    for n in range(total):
        label = f'Cita {n + 1}: ' if total > 1 else ''
        try:
            appointment_date = datetime.strptime(dates[n], '%Y-%m-%d').date()
            appointment_time = datetime.strptime(times[n], '%H:%M').time()
        except (TypeError, ValueError):
            flash(f'{label}Fecha u hora inválidas.', 'error'); return _conversation_redirect(otro_usuario_id)
        reason = (reasons[n] or '').strip()
        if appointment_date <= date.today() or not reason:
            flash(f'{label}Completa los datos de la cita correctamente.', 'error'); return _conversation_redirect(otro_usuario_id)
        if (appointment_date, appointment_time) in seen:
            flash(f'{label}Repites fecha y hora con otra cita del mismo envío.', 'error'); return _conversation_redirect(otro_usuario_id)
        seen.add((appointment_date, appointment_time))
        if has_schedule_conflict(user_id, otro_usuario_id, appointment_date, appointment_time):
            flash(f'{label}Hay un conflicto con una cita aceptada en ese horario.', 'error'); return _conversation_redirect(otro_usuario_id)
        parsed.append((appointment_date, appointment_time, (places[n] or '').strip() or None,
                       reason, (notes[n] or '').strip() or None))

    created = sum(1 for args in parsed if create_appointment(user_id, otro_usuario_id, *args))
    if created:
        create_notification(otro_usuario_id, 'Tienes una nueva solicitud de cita pendiente.' if created == 1
                            else f'Tienes {created} nuevas solicitudes de cita pendientes.')
        flash('Cita propuesta correctamente.' if created == 1 else f'{created} citas propuestas correctamente.', 'success')
    if created < total:
        flash('No fue posible crear la cita.' if total == 1 else f'No fue posible crear {total - created} de las citas.', 'error')
    return _conversation_redirect(otro_usuario_id)


def _change_status(cita_id, action):
    if not session.get('user_id'): return redirect(url_for('auth.login_page'))
    cita = get_appointment(cita_id); user_id = session['user_id']
    if not user_participates(cita, user_id): abort(403)
    if action in ('aceptar', 'rechazar') and (cita['receptor_id'] != user_id or cita['estado'] != 'Pendiente'): abort(403)
    if action in ('cancelar', 'completar') and (cita['estado'] != 'Aceptada'): abort(403)
    if action == 'aceptar' and has_schedule_conflict(cita['solicitante_id'], cita['receptor_id'], cita['fecha'], cita['hora']):
        flash('No puedes aceptar la cita porque ahora existe un conflicto de horario.', 'error')
        return _conversation_redirect(cita['solicitante_id'])
    operations = {'aceptar': (accept_appointment, 'Aceptada'), 'rechazar': (reject_appointment, 'Rechazada'), 'cancelar': (cancel_appointment, 'Cancelada'), 'completar': (complete_appointment, 'Completada')}
    fn, label = operations[action]; fn(cita_id)
    other_user = cita['receptor_id'] if user_id == cita['solicitante_id'] else cita['solicitante_id']
    create_notification(other_user, f'La cita #{cita_id} fue marcada como {label}.')
    flash(f'Cita {label.lower()}.', 'success')
    return _conversation_redirect(other_user)


@appointment_bp.route('/<int:cita_id>/aceptar', methods=['POST'])
def accept_route(cita_id): return _change_status(cita_id, 'aceptar')
@appointment_bp.route('/<int:cita_id>/rechazar', methods=['POST'])
def reject_route(cita_id): return _change_status(cita_id, 'rechazar')
@appointment_bp.route('/<int:cita_id>/cancelar', methods=['POST'])
def cancel_route(cita_id): return _change_status(cita_id, 'cancelar')
@appointment_bp.route('/<int:cita_id>/completar', methods=['POST'])
def complete_route(cita_id): return _change_status(cita_id, 'completar')
