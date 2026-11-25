---
name: flask-security
description: Úsala siempre que escribas o revises rutas, formularios, login, sesiones, subida de archivos o consultas SQL en CoAgrix; también para auditorías de seguridad.
---
# Seguridad en CoAgrix
## Checklist de revisión
- [ ] **SQL**: ¿todo dato del usuario va con `%s` y tupla de argumentos? Solo se permite
      interpolar nombres de columna fijos escritos en el código.
- [ ] **CSRF**: ¿cada `<form method="post">` incluye
      `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`?
- [ ] **Métodos**: ¿toda acción que cambia estado (logout, borrar, aprobar) es POST?
- [ ] **Rol**: ¿la ruta comprueba `session['role_name']`? Los blueprints sensibles usan
      `@bp.before_request` como `check_admin` en `admin_controller.py`.
- [ ] **Propiedad (IDOR)**: si la URL trae un `id`, ¿se verifica que pertenece al usuario
      (`order_belongs_to_farmer`, etc.) y se responde 403 si no?
- [ ] **Sesión**: al iniciar sesión, ¿se hace `session.clear()` antes de guardar `user_id`?
- [ ] **Contraseñas**: solo `generate_password_hash` / `check_password_hash`. Nunca en claro.
- [ ] **Uploads**: extensión permitida + formato real con Pillow + `secure_filename` +
      límite de tamaño (ya en `farmer_controller.py`; reutilízalo).
- [ ] **Rate limit**: login, registro y reset llevan `@limiter.limit(...)`.
- [ ] **Secretos**: nada de claves en el código ni en el repo; todo viene de `.env`.
- [ ] **Errores**: no mostrar trazas ni datos internos al usuario.
## Al terminar
Indica qué puntos del checklist comprobaste y cómo (test, lectura de código o prueba manual).
