# Correo de recuperación con Google Apps Script

Render (plan gratis) bloquea los puertos de correo SMTP. Este script de Google
recibe la petición de la app por HTTPS y envía el correo desde tu Gmail.
Límite: 100 correos al día (cuenta Gmail normal).

## Código del script (pegar en script.google.com)

```javascript
// Clave compartida con la app (variable MAIL_SCRIPT_SECRET en Render).
const SECRET = 'CAMBIA_ESTA_CLAVE';

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    if (data.secret !== SECRET) {
      return respuesta({ ok: false, error: 'clave incorrecta' });
    }
    MailApp.sendEmail({
      to: data.to,
      subject: data.subject,
      body: data.body,
      name: 'CoAgrix',
    });
    return respuesta({ ok: true });
  } catch (err) {
    return respuesta({ ok: false, error: String(err) });
  }
}

function respuesta(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

// Ejecutar UNA vez desde el editor para dar el permiso de enviar correos.
function probar() {
  MailApp.sendEmail(Session.getActiveUser().getEmail(), 'Prueba CoAgrix', 'Funciona.');
}
```

## Publicarlo
1. Implementar → Nueva implementación → tipo **Aplicación web**.
2. Ejecutar como: **Yo**. Quién tiene acceso: **Cualquier usuario**.
3. Copiar la URL (termina en `/exec`).

## Variables en Render
```
MAIL_SCRIPT_URL=https://script.google.com/macros/s/XXXX/exec
MAIL_SCRIPT_SECRET=la misma clave que pusiste en SECRET
```
Si cambias el código del script, hay que volver a implementar
(Implementar → Gestionar implementaciones → editar → Nueva versión).
