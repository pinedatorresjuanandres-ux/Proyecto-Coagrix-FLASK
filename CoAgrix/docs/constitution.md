# Constitución — CoAgrix
Principios innegociables. Toda spec, plan y tarea debe cumplirlos.

1. **La spec manda**: nada se implementa si no está en la spec activa. Si falta una
   decisión, se para y se pregunta.
2. **MVC limpio**: el SQL solo vive en `Modelo/`; los controladores son delgados; las
   plantillas no contienen lógica de negocio.
3. **Seguridad primero**: CSRF en cada POST, consultas parametrizadas, rol y propiedad
   verificados en cada ruta protegida, contraseñas con hash, sin secretos en el repositorio.
4. **Tests como puerta**: todo comportamiento nuevo tiene prueba con `pytest` (modelos
   mockeados). Prohibido avanzar con tests en rojo.
5. **Los datos del usuario son sagrados**: las migraciones en `sql/` son aditivas e
   idempotentes. Nunca se borran ni se alteran datos sin una spec que lo apruebe.
6. **Sin dependencias nuevas** sin aprobación explícita del usuario.
7. **Idioma**: interfaz y documentación en español; código nuevo en inglés.
