"""Envío del correo de recuperación de contraseña.

El proyecto no trae un servidor de correo propio, así que este módulo
envía por SMTP usando las variables de entorno MAIL_* (ver .env.example).
Si esas variables no están configuradas -no es obligatorio para poder
probar el flujo localmente- la función simplemente no envía nada y lo
avisa por consola; el controlador se encarga de mostrar el enlace de
recuperación en pantalla en ese caso (solo fuera de producción), para
que el "olvidé mi contraseña" quede funcional también sin SMTP.
"""
import os
import smtplib
from email.mime.text import MIMEText


def is_mail_configured():
    """True si hay credenciales SMTP suficientes para intentar enviar."""
    return bool(os.environ.get('MAIL_USERNAME') and os.environ.get('MAIL_PASSWORD'))


def send_reset_email(destinatario, nombre, enlace):
    """Envía el correo de recuperación de contraseña.

    Devuelve True si el correo se envió correctamente, False si no había
    configuración de correo o si falló el envío (en ambos casos se
    registra el motivo en consola, sin interrumpir el flujo de la app).
    """
    if not is_mail_configured():
        print(
            "[mailer] MAIL_USERNAME/MAIL_PASSWORD no configurados: "
            "no se envió correo de recuperación (modo desarrollo)."
        )
        return False

    servidor = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    puerto = int(os.environ.get('MAIL_PORT', 587))
    usuario = os.environ.get('MAIL_USERNAME')
    password = os.environ.get('MAIL_PASSWORD')
    remitente = os.environ.get('MAIL_DEFAULT_SENDER', usuario)

    cuerpo = (
        f"Hola {nombre},\n\n"
        "Recibimos una solicitud para restablecer tu contraseña en CoAgrix.\n\n"
        "Si fuiste tú, entra al siguiente enlace (válido por 1 hora) para "
        "elegir una nueva contraseña:\n"
        f"{enlace}\n\n"
        "Si no solicitaste este cambio, puedes ignorar este correo: tu "
        "contraseña actual seguirá funcionando con normalidad.\n\n"
        "— El equipo de CoAgrix"
    )

    mensaje = MIMEText(cuerpo, 'plain', 'utf-8')
    mensaje['Subject'] = 'CoAgrix - Restablecer tu contraseña'
    mensaje['From'] = remitente
    mensaje['To'] = destinatario

    try:
        with smtplib.SMTP(servidor, puerto, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(usuario, password)
            smtp.sendmail(remitente, [destinatario], mensaje.as_string())
        return True
    except Exception as e:
        print(f"[mailer] Error enviando correo de recuperación: {e}")
        return False
