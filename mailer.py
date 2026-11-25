import json
import smtplib
import urllib.error
import urllib.request
from email.message import EmailMessage

from config import Config


def _send_via_google_script(to, subject, body):
    """Envía el correo a través de un Google Apps Script publicado como
    aplicación web (ver docs/correo_google_apps_script.md). Va por HTTPS
    (puerto 443), así que funciona aunque el hosting bloquee SMTP, como el
    plan gratis de Render."""
    payload = json.dumps({
        'secret': Config.MAIL_SCRIPT_SECRET,
        'to': to,
        'subject': subject,
        'body': body,
    }).encode('utf-8')
    req = urllib.request.Request(
        Config.MAIL_SCRIPT_URL, data=payload,
        headers={'Content-Type': 'application/json'}, method='POST',
    )
    try:
        # Google responde con una redirección; urllib la sigue sola.
        with urllib.request.urlopen(req, timeout=20) as resp:
            respuesta = resp.read().decode('utf-8', 'replace')
    except (urllib.error.URLError, OSError) as e:
        print(f"Error enviando correo a {to} (Google Script): {e}")
        return False
    if '"ok":true' in respuesta.replace(' ', ''):
        return True
    print(f"Error enviando correo a {to} (Google Script): {respuesta[:300]}")
    return False


def _send_via_smtp(to, subject, body):
    msg = EmailMessage()
    msg['From'] = Config.SMTP_FROM
    msg['To'] = to
    msg['Subject'] = subject
    msg.set_content(body)
    try:
        if Config.SMTP_USE_SSL:
            server = smtplib.SMTP_SSL(Config.SMTP_HOST, Config.SMTP_PORT, timeout=10)
        else:
            server = smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=10)
            server.starttls()
        with server:
            if Config.SMTP_USER:
                server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except (smtplib.SMTPException, OSError) as e:
        print(f"Error enviando correo a {to}: {e}")
        return False


def send_email(to, subject, body):
    """Envía un correo de texto plano. Orden de preferencia:
    1. Google Apps Script (si MAIL_SCRIPT_URL está configurada).
    2. SMTP (si SMTP_HOST está configurado).
    3. Ninguno: imprime el mensaje en la consola (desarrollo), para poder
       copiar el enlace.
    Nunca lanza excepciones: si el envío falla lo registra y devuelve False,
    para no tumbar la petición."""
    if Config.MAIL_SCRIPT_URL:
        return _send_via_google_script(to, subject, body)

    if not Config.SMTP_HOST or (Config.SMTP_USER and not Config.SMTP_PASSWORD):
        print(f"\n--- CORREO (SMTP no configurado) ---\nPara: {to}\nAsunto: {subject}\n\n{body}\n------------------------------------\n")
        return True

    return _send_via_smtp(to, subject, body)
