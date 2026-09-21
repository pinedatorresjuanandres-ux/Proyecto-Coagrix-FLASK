"""Datos de demostración para CoAgrix.

Complementa a seed_datos_prueba.py (que ya deja publicaciones creadas)
agregando lo necesario para que se pueda VER la aplicación funcionando con
datos realistas: más compradores (comerciante/empresa), historial de
precios variado (antiguos y actuales) para el gráfico de "Comparar
Precios", pedidos en distintos estados, conversaciones de mensajes,
citas agendadas, favoritos y reseñas.

Es idempotente: se puede volver a correr sin duplicar datos (cada sección
verifica si ya existe algo antes de insertar).

Uso:
    python scripts/seed_datos_demo.py
"""
import os
import sys
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from werkzeug.security import generate_password_hash  # noqa: E402

from database import query_db, execute_db  # noqa: E402
from Modelo.user import (  # noqa: E402
    get_user_by_email, create_user, create_merchant_profile, create_company_profile,
)
from Modelo.order import create_order, add_order_detail  # noqa: E402
from Modelo.product import decrease_stock  # noqa: E402
from Modelo.appointment import (  # noqa: E402
    create_appointment, accept_appointment, complete_appointment, reject_appointment,
)
from Modelo.favorite import is_favorite, add_favorite  # noqa: E402
from Modelo.review import user_has_reviewed, create_review  # noqa: E402


NUEVOS_COMPRADORES = [
    {
        'tipo': 'Comerciante', 'nombre': 'Laura Gómez', 'email': 'lauragomez.comerciante@coagrix.com',
        'password': 'comerciante2025', 'telefono': '3201234567',
        'ubicacion': {'departamento': 'Antioquia', 'municipio': 'Medellín', 'direccion': 'Plaza Minorista'},
    },
    {
        'tipo': 'Empresa', 'nombre': 'Frutas del Valle S.A.S', 'email': 'frutasdelvalle@coagrix.com',
        'password': 'empresa2025', 'telefono': '3109876543', 'nit': '900123456-7',
        'sector': 'Distribución de alimentos',
        'ubicacion': {'departamento': 'Valle del Cauca', 'municipio': 'Cali', 'direccion': 'Zona Industrial Acopi'},
    },
]


def get_or_create_ubicacion(departamento, municipio, direccion=None):
    existente = query_db(
        "SELECT * FROM ubicaciones WHERE departamento = %s AND municipio = %s",
        (departamento, municipio), one=True
    )
    if existente:
        return existente['id']
    return execute_db(
        "INSERT INTO ubicaciones (departamento, municipio, direccion) VALUES (%s, %s, %s)",
        (departamento, municipio, direccion)
    )


def get_rol_id(nombre_rol):
    row = query_db("SELECT id FROM roles WHERE nombre = %s", (nombre_rol,), one=True)
    return row['id'] if row else None


def seed_compradores():
    """Crea comerciantes/empresas adicionales (si no existen ya) para que
    haya varios contactos con quién probar mensajes, pedidos, citas, etc."""
    ids = []
    for comprador in NUEVOS_COMPRADORES:
        existente = get_user_by_email(comprador['email'])
        if existente:
            print(f"  [omitido] Ya existe: {comprador['nombre']} ({comprador['email']})")
            ids.append(existente['id'])
            continue

        rol_id = get_rol_id(comprador['tipo'])
        usuario_id = create_user(comprador['nombre'], comprador['email'], comprador['password'], rol_id)
        ubicacion_id = get_or_create_ubicacion(**comprador['ubicacion'])

        if comprador['tipo'] == 'Empresa':
            create_company_profile(usuario_id, nit=comprador.get('nit'), telefono=comprador['telefono'],
                                    ubicacion_id=ubicacion_id, sector=comprador.get('sector'))
        else:
            create_merchant_profile(usuario_id, telefono=comprador['telefono'], ubicacion_id=ubicacion_id)

        print(f"  [creado] {comprador['tipo']}: {comprador['nombre']} ({comprador['email']}) -> usuario_id={usuario_id}")
        ids.append(usuario_id)
    return ids


def get_publicacion_por_titulo(titulo):
    return query_db("SELECT * FROM publicaciones WHERE titulo = %s LIMIT 1", (titulo,), one=True)


def seed_historial_precios(titulo, tendencia):
    """Agrega 3 puntos históricos (90, 60 y 30 días atrás) antes del punto
    base que ya dejó create_publication, para que el gráfico de evolución
    de precios en 'Comparar Precios' muestre una tendencia real."""
    pub = get_publicacion_por_titulo(titulo)
    if not pub:
        print(f"  [omitido] Publicación no encontrada: {titulo}")
        return

    ya_enriquecido = query_db(
        "SELECT COUNT(*) as c FROM historial_precios WHERE publicacion_id = %s AND tipo_precio = 'empresa'",
        (pub['id'],), one=True
    )
    if ya_enriquecido and ya_enriquecido['c'] > 1:
        print(f"  [omitido] Ya tiene historial variado: {titulo}")
        return

    factores = [0.80, 0.90, 1.00] if tendencia == 'up' else [1.20, 1.10, 1.00]
    dias_atras = [90, 60, 30]
    anterior_empresa = anterior_comerciante = None

    for dias, factor in zip(dias_atras, factores):
        nuevo_empresa = round(float(pub['precio_empresa']) * factor / 50) * 50
        nuevo_comerciante = round(float(pub['precio_comerciante']) * factor / 50) * 50
        if anterior_empresa is None:
            anterior_empresa, anterior_comerciante = nuevo_empresa, nuevo_comerciante
        fecha = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d %H:%M:%S')

        execute_db(
            "INSERT INTO historial_precios (publicacion_id, tipo_precio, precio_anterior, precio_nuevo, fecha_cambio) "
            "VALUES (%s, 'empresa', %s, %s, %s)",
            (pub['id'], anterior_empresa, nuevo_empresa, fecha)
        )
        execute_db(
            "INSERT INTO historial_precios (publicacion_id, tipo_precio, precio_anterior, precio_nuevo, fecha_cambio) "
            "VALUES (%s, 'comerciante', %s, %s, %s)",
            (pub['id'], anterior_comerciante, nuevo_comerciante, fecha)
        )
        anterior_empresa, anterior_comerciante = nuevo_empresa, nuevo_comerciante

    print(f"  [creado] Historial de precios variado para: {titulo} (tendencia {tendencia})")


def seed_pedido(comprador_id, campesino_publicaciones, estado, dias_atras, campo_precio):
    """Crea un pedido con 1-2 productos de un mismo campesino, en el estado
    indicado, y descuenta stock (igual que hace el checkout real)."""
    items = []
    for pub, cantidad in campesino_publicaciones:
        precio_unitario = pub[campo_precio]
        items.append({'publicacion_id': pub['id'], 'cantidad': cantidad, 'precio_unitario': precio_unitario})

    total = sum(float(i['precio_unitario']) * i['cantidad'] for i in items)
    pedido_id = create_order(comprador_id, total)
    if not pedido_id:
        return None

    for item in items:
        add_order_detail(pedido_id, item['publicacion_id'], item['cantidad'], item['precio_unitario'])
        decrease_stock(item['publicacion_id'], item['cantidad'])

    fecha = (datetime.now() - timedelta(days=dias_atras)).strftime('%Y-%m-%d %H:%M:%S')
    execute_db("UPDATE pedidos SET estado = %s, fecha_pedido = %s WHERE id = %s", (estado, fecha, pedido_id))
    return pedido_id


def seed_pedidos(comerciante_id, empresa_id, comerciante2_id, empresa2_id):
    ya_hay = query_db("SELECT COUNT(*) as c FROM pedidos", one=True)
    if ya_hay and ya_hay['c'] > 0:
        print("  [omitido] Ya existen pedidos, no se crean más.")
        return

    manzana = get_publicacion_por_titulo('Manzana Roja')
    mango = get_publicacion_por_titulo('Mango Tommy')
    cafe = get_publicacion_por_titulo('Café Tostado Premium')
    queso = get_publicacion_por_titulo('Queso Campesino')
    trucha = get_publicacion_por_titulo('Trucha Arcoíris')
    frijol = get_publicacion_por_titulo('Fríjol Cargamanto')

    creados = 0
    if manzana and mango:
        seed_pedido(comerciante_id, [(manzana, 20), (mango, 15)], 'Completado', 18, 'precio_comerciante')
        creados += 1
    if cafe:
        seed_pedido(empresa_id, [(cafe, 10)], 'Completado', 12, 'precio_empresa')
        creados += 1
    if frijol:
        seed_pedido(comerciante_id, [(frijol, 8)], 'Aceptado', 5, 'precio_comerciante')
        creados += 1
    if queso and trucha:
        seed_pedido(empresa2_id, [(queso, 12), (trucha, 6)], 'Aceptado', 3, 'precio_empresa')
        creados += 1
    if mango:
        seed_pedido(comerciante2_id, [(mango, 25)], 'Pendiente', 0, 'precio_comerciante')
        creados += 1
    if manzana:
        seed_pedido(empresa2_id, [(manzana, 10)], 'Rechazado', 7, 'precio_empresa')
        creados += 1

    print(f"  [creado] {creados} pedidos de prueba con distintos estados.")


def seed_mensaje(remitente_id, destinatario_id, contenido, dias_atras, horas, leido=True):
    fecha = (datetime.now() - timedelta(days=dias_atras, hours=-horas)).strftime('%Y-%m-%d %H:%M:%S')
    execute_db(
        "INSERT INTO mensajes (remitente_id, destinatario_id, contenido, fecha, leido) VALUES (%s, %s, %s, %s, %s)",
        (remitente_id, destinatario_id, contenido, fecha, leido)
    )


def seed_conversacion(usuario_a, usuario_b, mensajes, ultimo_no_leido_para=None):
    """`mensajes` es una lista de (autor, texto); `autor` es 'a' o 'b'."""
    existentes = query_db(
        "SELECT COUNT(*) as c FROM mensajes WHERE (remitente_id=%s AND destinatario_id=%s) OR (remitente_id=%s AND destinatario_id=%s)",
        (usuario_a, usuario_b, usuario_b, usuario_a), one=True
    )
    if existentes and existentes['c'] > 0:
        print(f"  [omitido] Ya hay mensajes entre {usuario_a} y {usuario_b}.")
        return

    dias_atras = 3
    for i, (autor, texto) in enumerate(mensajes):
        remitente = usuario_a if autor == 'a' else usuario_b
        destinatario = usuario_b if autor == 'a' else usuario_a
        es_ultimo = (i == len(mensajes) - 1)
        leido = not (es_ultimo and ultimo_no_leido_para == destinatario)
        seed_mensaje(remitente, destinatario, texto, dias_atras, i, leido=leido)
        dias_atras = max(0, dias_atras - 1) if i % 2 == 1 else dias_atras

    print(f"  [creado] Conversación entre usuario {usuario_a} y usuario {usuario_b} ({len(mensajes)} mensajes).")


def seed_mensajes(juan_id, maria_id, pedro_id, agroexport_id, laura_id, frutas_id):
    seed_conversacion(juan_id, pedro_id, [
        ('b', 'Hola Juan, vi tu publicación de Manzana Roja, ¿tienes disponibilidad para 20 libras semanales?'),
        ('a', '¡Hola Pedro! Sí, con gusto. Puedo dejarte reservado ese volumen cada semana.'),
        ('b', 'Perfecto, ¿manejas algún descuento por volumen?'),
        ('a', 'Claro, para pedidos recurrentes puedo mejorar un poco el precio. Te escribo la propuesta.'),
        ('b', '¡Excelente, quedo atento!'),
    ], ultimo_no_leido_para=juan_id)

    seed_conversacion(juan_id, agroexport_id, [
        ('b', 'Buenas, somos AgroExport. Nos interesa tu Café Tostado Premium para un contrato mensual.'),
        ('a', 'Hola, con gusto. ¿Qué cantidad mensual estarían necesitando?'),
        ('b', 'Estimamos unos 100 kg mensuales, ¿podrías sostener ese volumen?'),
        ('a', 'Sí, podemos organizarlo. Te propongo agendar una cita para revisar los detalles.'),
    ])

    seed_conversacion(maria_id, laura_id, [
        ('b', 'Hola María, ¿tienes Queso Campesino disponible esta semana?'),
        ('a', 'Hola Laura, sí tengo disponible. ¿Cuánto necesitas?'),
        ('b', 'Unos 12 kg, para el próximo miércoles si es posible.'),
        ('a', 'Perfecto, te lo puedo tener listo para esa fecha.'),
        ('b', '¡Genial, muchas gracias!'),
    ], ultimo_no_leido_para=maria_id)

    seed_conversacion(maria_id, frutas_id, [
        ('b', 'Buen día, queremos cotizar Trucha Arcoíris para nuestro punto de distribución.'),
        ('a', 'Hola, con gusto te comparto precios. ¿Qué volumen manejan normalmente?'),
        ('b', 'Entre 30 y 50 kg por pedido, dependiendo de la temporada.'),
    ])


def seed_citas(juan_id, maria_id, pedro_id, agroexport_id, laura_id, frutas_id):
    ya_hay = query_db("SELECT COUNT(*) as c FROM citas", one=True)
    if ya_hay and ya_hay['c'] > 0:
        print("  [omitido] Ya existen citas, no se crean más.")
        return

    hoy = datetime.now().date()

    cita1 = create_appointment(pedro_id, juan_id, hoy + timedelta(days=5), '10:00:00',
                                'Finca El Triunfo, Neiva', 'Visita para conocer el cultivo de manzana',
                                'Quisiera ver el proceso de cosecha antes de cerrar el pedido recurrente.')

    cita2 = create_appointment(agroexport_id, juan_id, hoy + timedelta(days=10), '15:00:00',
                                'Oficina AgroExport, Bogotá', 'Negociación de contrato de suministro mensual', None)
    if cita2:
        accept_appointment(cita2)

    cita3 = create_appointment(laura_id, maria_id, hoy - timedelta(days=10), '09:00:00',
                                'Vereda La Esperanza, Marinilla', 'Recogida de pedido de quesos y lácteos', None)
    if cita3:
        accept_appointment(cita3)
        complete_appointment(cita3)

    cita4 = create_appointment(frutas_id, maria_id, hoy + timedelta(days=3), '11:00:00',
                                'Planta de procesamiento, Cali', 'Visita para certificación de calidad', None)
    if cita4:
        reject_appointment(cita4)

    print(f"  [creado] 4 citas de prueba: {cita1 and 'Pendiente'}, Aceptada, Completada, Rechazada.")


def seed_favoritos(pedro_id, agroexport_id, laura_id, frutas_id):
    pares = [
        (pedro_id, 'Café Tostado Premium'),
        (pedro_id, 'Fríjol Cargamanto'),
        (agroexport_id, 'Cacao en Grano'),
        (laura_id, 'Mango Tommy'),
        (frutas_id, 'Queso Campesino'),
        (frutas_id, 'Trucha Arcoíris'),
    ]
    creados = 0
    for usuario_id, titulo in pares:
        pub = get_publicacion_por_titulo(titulo)
        if not pub or is_favorite(usuario_id, pub['id']):
            continue
        add_favorite(usuario_id, pub['id'])
        creados += 1
    print(f"  [creado] {creados} favoritos nuevos.")


def seed_resenas(pedro_id, agroexport_id, laura_id, frutas_id):
    reseñas = [
        (pedro_id, 'Manzana Roja', 5, 'Excelente calidad, siempre llega fresca y a tiempo.'),
        (agroexport_id, 'Mango Tommy', 4, 'Buen producto y entrega puntual, seguiremos comprando.'),
        (laura_id, 'Café Tostado Premium', 5, 'El mejor café que he comprado en la plataforma.'),
        (frutas_id, 'Queso Campesino', 3, 'Buen sabor, pero el último pedido llegó con algo de retraso.'),
    ]
    creadas = 0
    for usuario_id, titulo, calificacion, comentario in reseñas:
        pub = get_publicacion_por_titulo(titulo)
        if not pub or user_has_reviewed(usuario_id, pub['id']):
            continue
        create_review(usuario_id, pub['id'], calificacion, comentario)
        creadas += 1
    print(f"  [creado] {creadas} reseñas nuevas.")


def main():
    print("=== Seed de datos de demostración CoAgrix ===")

    juan = get_user_by_email('campesino@coagrix.com')
    maria = get_user_by_email('mariarojas.campesina@coagrix.com')
    pedro = get_user_by_email('comerciante@coagrix.com')
    agroexport = get_user_by_email('empresa@coagrix.com')

    if not (juan and pedro and agroexport):
        print(
            "\nFaltan las cuentas base (campesino@coagrix.com / comerciante@coagrix.com / "
            "empresa@coagrix.com). Carga primero sql/coagrix (3).sql.\n"
        )
        sys.exit(1)
    if not maria:
        print(
            "\nNo se encontró el segundo campesino (mariarojas.campesina@coagrix.com).\n"
            "Corre primero scripts/seed_datos_prueba.py y vuelve a intentar.\n"
        )
        sys.exit(1)

    print("\n1) Compradores adicionales (Comerciante/Empresa)")
    laura_id, frutas_id = seed_compradores()

    print("\n2) Historial de precios (antiguos y actuales)")
    seed_historial_precios('Manzana Roja', 'up')
    seed_historial_precios('Mango Tommy', 'down')
    seed_historial_precios('Café Tostado Premium', 'up')
    seed_historial_precios('Queso Campesino', 'down')

    print("\n3) Pedidos en distintos estados")
    seed_pedidos(pedro['id'], agroexport['id'], laura_id, frutas_id)

    print("\n4) Conversaciones de mensajes")
    seed_mensajes(juan['id'], maria['id'], pedro['id'], agroexport['id'], laura_id, frutas_id)

    print("\n5) Citas agendadas")
    seed_citas(juan['id'], maria['id'], pedro['id'], agroexport['id'], laura_id, frutas_id)

    print("\n6) Favoritos")
    seed_favoritos(pedro['id'], agroexport['id'], laura_id, frutas_id)

    print("\n7) Reseñas")
    seed_resenas(pedro['id'], agroexport['id'], laura_id, frutas_id)

    print("\n=== Listo. Ya puedes navegar la app con datos de demostración. ===")
    print("Usuarios de compradores nuevos (contraseña entre paréntesis):")
    print("  lauragomez.comerciante@coagrix.com (comerciante2025)")
    print("  frutasdelvalle@coagrix.com (empresa2025)")


if __name__ == '__main__':
    main()
