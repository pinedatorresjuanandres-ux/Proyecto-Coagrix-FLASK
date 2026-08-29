"""Instancias compartidas de extensiones de Flask.

Se definen aquí (sin `app` todavía) para que tanto app.py como los
blueprints en routes/ puedan importarlas sin crear un import circular.
app.py las inicializa con init_app(app) una vez creada la aplicación.
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=[])
