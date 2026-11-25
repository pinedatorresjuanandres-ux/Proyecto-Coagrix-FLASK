---
name: colombia-locale
description: Úsala siempre que trabajes con precios, monedas, fechas, horas, teléfonos, NIT o ubicaciones (departamento y municipio) en CoAgrix.
---
# Particularidades de Colombia en CoAgrix
## Moneda
- Los precios son pesos colombianos (COP), enteros, con punto de miles: `$25.000 COP`.
- Usa siempre el filtro `|cop` definido en `app.py`. No formatees precios a mano.
## Fechas y horas
- Colombia está en UTC-5 todo el año (sin horario de verano), zona `America/Bogota`.
- Un servidor en la nube suele estar en UTC: no asumas que `datetime.now()` es hora local.
  Si una regla depende del día o la hora (pedidos de hoy, citas), defínelo en la spec y
  calcula con zona horaria explícita.
- Formato visible al usuario: día/mes/año.
## Datos de contacto
- Teléfono: `[0-9+() -]{7,20}`. NIT: `[0-9]{6,12}(-[0-9])?`. Son las regex de `auth_controller.py`;
  reutilízalas, no crees otras.
## Ubicaciones
- Departamento y municipio salen de `Modelo/ubicaciones.py` (`get_ubicaciones_colombia`).
  Valida siempre con `is_valid_location(departamento, municipio)`.
- Reutiliza el componente `components/location_select.html`.
## Checklist
- [ ] ¿Algún precio sin el filtro `|cop`?
- [ ] ¿Alguna fecha que dependa de la zona horaria del servidor?
- [ ] ¿Se valida la ubicación contra la lista oficial?
