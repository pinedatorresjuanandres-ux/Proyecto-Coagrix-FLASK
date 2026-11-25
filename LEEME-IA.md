# Cómo instalar el kit de IA en CoAgrix

1. Copia **todo el contenido** de esta carpeta (incluidas las carpetas ocultas `.agents` y
   `.opencode`) a la raíz del proyecto, junto a `app.py`.
   En PowerShell: `Copy-Item -Recurse -Force .\CoAgrix-IA\* D:\ruta\CoAgrix\ ; Copy-Item -Recurse -Force .\CoAgrix-IA\.* D:\ruta\CoAgrix\`
2. Si ya tienes `AGENTS.md` o `MEMORY.md`, revisa antes de sobrescribir.
3. Define tu clave de Context7 como variable de entorno (no en el repositorio):
   `setx CONTEXT7_API_KEY "tu-clave"` y reinicia la terminal.
4. Abre OpenCode **en la raíz del proyecto** (si no, no carga skills ni comandos).
5. Prueba: `/sdd-status`, y para empezar `/sdd-clarify specs/001-endurecer-sesion`.

Añade a `.gitignore` si no está: `.env`, `.flask_session_data/`, `static/uploads/*`.
