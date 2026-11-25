# Spec 001 — Endurecer el cierre e inicio de sesión

Estado: borrador

## Contexto y objetivo
Hoy cualquier página externa puede cerrar la sesión de un usuario (el cierre de sesión se
hace con un simple enlace) y el inicio de sesión no renueva la sesión previa. Queremos
cerrar estas dos brechas para proteger a campesinos, compradores y administradores.

## Usuarios
- Campesino, Empresa, Comerciante y Administrador (todos los que inician sesión).

## Historias de usuario
- HU-1. Como usuario autenticado, quiero que solo yo pueda cerrar mi sesión para que un
  sitio externo no me desconecte sin querer.
- HU-2. Como usuario, quiero que al iniciar sesión se cree una sesión nueva para que nadie
  pueda reutilizar un identificador de sesión anterior.

## Requisitos funcionales
- RF-1: CUANDO el usuario pulsa "Cerrar sesión", EL SISTEMA envía una petición POST con
  token CSRF, borra la sesión y redirige a la página de inicio.
- RF-2: SI llega una petición GET a la ruta de cierre de sesión, ENTONCES EL SISTEMA no
  cierra la sesión y responde 405.
- RF-3: CUANDO un usuario inicia sesión con credenciales válidas, EL SISTEMA descarta
  cualquier dato de la sesión anterior antes de guardar los datos del usuario.
- RF-4: EL SISTEMA muestra el botón "Cerrar sesión" en todas las pantallas donde hoy
  aparece el enlace, con el mismo texto.

## Requisitos no funcionales
- Los cambios no deben alterar mensajes ni redirecciones existentes del login.
- Se ve bien en móvil (375 px).

## Casos límite
- Usuario ya sin sesión que envía el cierre de sesión: redirige a inicio sin error.
- Token CSRF ausente o inválido: la petición se rechaza con 400.
- Cuenta inactiva: sigue sin poder iniciar sesión, igual que hoy.

## Fuera de alcance
- Cambiar la política de contraseñas.
- Cierre de sesión en todos los dispositivos.

## Criterios de finalización
- Tests con `pytest` para RF-1, RF-2 y RF-3. RF-4 con Chrome DevTools en escritorio y móvil.
- `pytest` completo en verde.

## Dudas abiertas
- [NECESITA ACLARACIÓN] ¿El botón de cerrar sesión debe verse igual que el enlace actual o puede
  cambiar de estilo?
