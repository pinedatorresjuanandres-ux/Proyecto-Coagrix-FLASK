"""Prueba rápida y aislada de la configuración de correo.

Uso:
    1. Pon tu contraseña de aplicación de Gmail en el .env (MAIL_PASSWORD).
    2. Ejecuta:  python verificar_correo.py
    3. Revisa la bandeja de MAIL_USERNAME (te llega un correo de prueba).

No forma parte de la app: es solo una herramienta de diagnóstico, se
puede borrar sin problema una vez confirmes que el envío funciona.
"""
from dotenv import load_dotenv
load_dotenv()

from utils.mailer import is_mail_configured, send_reset_email

if not is_mail_configured():
    print("❌ MAIL_USERNAME o MAIL_PASSWORD no están configurados en el .env.")
    print("   Revisa que hayas guardado el archivo y que la clave no tenga espacios de más.")
    raise SystemExit(1)

print("✅ Variables de correo detectadas. Enviando correo de prueba...")

ok = send_reset_email(
    destinatario="pinedatorresjuanandres@gmail.com",
    nombre="Juan Andrés",
    enlace="http://localhost:5000/restablecer-password/token-de-prueba"
)

if ok:
    print("✅ ¡Correo enviado! Revisa tu bandeja de entrada (y spam).")
else:
    print("❌ Falló el envío. Revisa el mensaje de error impreso arriba:")
    print("   - Usuario/clave incorrectos -> vuelve a generar la contraseña de aplicación")
    print("   - 'Less secure app' o 2FA no activado -> activa verificación en 2 pasos primero")
