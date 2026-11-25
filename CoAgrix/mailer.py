import smtplib
from email.message import EmailMessage

from config import Config


def send_email(to, subject, body):
    """Envía un correo de texto plano por SMTP. Si SMTP_HOST no está
    configurado, o falta la contraseña (desarrollo), no envía nada: imprime
    el mensaje en la consola para poder copiar el enlace. Nunca lanza
    excepciones: si el envío falla lo registra y devuelve False, para no
    tumbar la petición."""
    if not Config.SMTP_HOST or (Config.SMTP_USER and not Config.SMTP_PASSWORD):
        print(f"\n--- CORREO (SMTP no configurado) ---\nPara: {to}\nAsunto: {subject}\n\n{body}\n------------------------------------\n")
        return True

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
