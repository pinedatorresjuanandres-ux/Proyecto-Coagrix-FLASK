# Documentación de CoAgrix

Organizada por fases del proyecto. Última revisión: 25/11/2026.

| Carpeta | Contenido |
|---|---|
| `01_Planeacion/` | Anteproyecto (APA), términos de referencia, propuesta técnica y ficha técnica del equipo. |
| `02_Requisitos/` | Especificación de requisitos (RF-1 a RF-19, RNF-1 a RNF-12), SRS v1.1 e historias de usuario por rol. |
| `03_Diseno/` | Diccionario de datos (base implementada + diseño inicial) y diagramas en draw.io. `Diagramas/Versiones_anteriores/` conserva los diagramas previos a la corrección. |
| `04_Seguimiento/` | Actas de reunión quincenal en orden cronológico. |
| `05_Pruebas_y_Calidad/` | Plan de Aseguramiento de la Calidad (Word y PDF), matrices de calidad (Excel, 11 hojas), pruebas de integración del equipo y `Evidencias/`. |
| `06_Manuales/` | Manual de instalación y manual de usuario. |
| `constitution.md`, `correo_google_apps_script.md` | Guías técnicas. Se quedan en la raíz de `docs/` porque el código las referencia por esta ruta. |

## Evidencias de calidad (`05_Pruebas_y_Calidad/Evidencias/`)

- `pytest_resultados_2026-11-25.*`: suite automatizada del proyecto (146 de 146 aprobadas).
- `verificacion_qa/`: 22 verificaciones de criterios de aceptación y sus resultados. Para volver a ejecutarlas, desde la raíz del proyecto:

  ```
  venv\Scripts\python -m pytest docs/05_Pruebas_y_Calidad/Evidencias/verificacion_qa -v
  ```

- `verificacion_produccion_2026-11-25.txt`: tiempos de respuesta y controles de seguridad medidos en https://coagrix.onrender.com, sin crear cuentas ni datos.
- `verificacion_produccion_roles_2026-11-25.txt`: recorrido de solo lectura por los cuatro roles en producción. No contiene contraseñas.
- `Capturas_pruebas_integracion/`: capturas exportadas de las pruebas de integración del equipo, nombradas con el ID de cada prueba.

## Diagramas

Los archivos `.drawio` se abren en https://app.diagrams.net o en la extensión de draw.io para VS Code.
