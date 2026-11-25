# MEMORY.md — CoAgrix
Memoria del proyecto entre sesiones. Máximo ~50 líneas.

## Estado actual
- App Flask funcionando: registro y login por rol, publicaciones, catálogo, carrito y
  pedidos, citas, favoritos, reseñas, comentarios, chat y recuperación de contraseña.
- Suite de tests con pytest (15 archivos, modelos mockeados).
- Setup de IA instalado: AGENTS.md, constitución, skills en `.agents/skills`, agentes y
  comandos `/sdd-*` en `.opencode`.

## Historial
- Setup SDD adaptado desde el curso (Diario de Estudio) a Flask.
- Spec 001-endurecer-sesion redactada (borrador).

## Decisiones (y por qué)
- Spec-Driven Development: cada cambio nace en una spec, para no improvisar.
- La API key de Context7 va en la variable de entorno `CONTEXT7_API_KEY`, no en el repo.

## Aprendizajes y errores a evitar
- El `.env` y `.flask_session_data/` ya viajaron en un zip: no volver a empaquetarlos.
- El venv se recreó con Python 3.14.6 (el viejo apuntaba al usuario SENA y estaba roto).
  Se instalaron versiones recientes de las dependencias porque los pins de
  requirements.txt (p. ej. Pillow 10.4.0) no compilan en Python 3.14. `venv_roto/` es
  el venv viejo, se puede borrar.
- Los comandos y skills solo se cargan si OpenCode se abre en la raíz del proyecto.

## Próximos pasos
- Revisar y aprobar la spec 001; después clarificar, planificar y crear tareas.
