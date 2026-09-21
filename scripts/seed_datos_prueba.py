
import io
import json
import os
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402

from config import Config  # noqa: E402
from database import query_db, execute_db  # noqa: E402
from Modelo.product import get_or_create_producto, insert_archivo  # noqa: E402



CAMPESINO_2 = {
    'nombre': 'María Fernanda Rojas',
    'email': 'mariarojas.campesina@coagrix.com',
    'password': 'campesina2025',
    'telefono': '3187654321',
    'descripcion': 'Productora de hortalizas, lácteos y productos apícolas en el oriente antioqueño.',
    'ubicacion': {'departamento': 'Antioquia', 'municipio': 'Marinilla', 'direccion': 'Vereda La Esperanza'},
}


UBICACION_CAMPESINO_1_DEFECTO = {
    'departamento': 'Huila', 'municipio': 'Neiva', 'direccion': 'Vereda El Triunfo'
}

PRODUCTOS_PRUEBA = [
    ("Mango Tommy de Exportación", "Mango Tommy", "Frutas",
     "Mango Tommy maduro, calibre grande, ideal para exportación.", 3200, 300, "Kilogramos (kg)", (237, 106, 90), 1),
    ("Naranja Valencia Dulce", "Naranja Valencia", "Frutas",
     "Naranjas jugosas recién cosechadas, sin químicos.", 1800, 500, "Kilogramos (kg)", (245, 166, 35), 1),
    ("Espinaca Fresca de Vereda", "Espinaca", "Verduras",
     "Espinaca fresca cosechada el mismo día de entrega.", 2500, 80, "Kilogramos (kg)", (60, 128, 62), 0),
    ("Zanahoria Criolla Seleccionada", "Zanahoria", "Hortalizas",
     "Zanahoria fresca lavada y clasificada por tamaño.", 1600, 400, "Kilogramos (kg)", (230, 126, 34), 1),
    ("Tomate Chonto de Invernadero", "Tomate Chonto", "Hortalizas",
     "Tomate chonto rojo, cultivado bajo invernadero.", 2200, 350, "Kilogramos (kg)", (192, 57, 43), 1),
    ("Papa Pastusa Primera Calidad", "Papa Pastusa", "Tubérculos",
     "Papa pastusa lavada, ideal para consumo y venta al detal.", 1900, 800, "Bultos", (196, 164, 111), 1),
    ("Yuca Fresca Recién Cosechada", "Yuca", "Tubérculos",
     "Yuca de buena calidad, tamaño uniforme.", 1500, 600, "Bultos", (222, 202, 165), 0),
    ("Fríjol Cargamanto Rojo", "Fríjol Cargamanto", "Legumbres",
     "Fríjol cargamanto seco, seleccionado a mano.", 6800, 200, "Kilogramos (kg)", (139, 51, 45), 1),
    ("Garbanzo Nacional Seco", "Garbanzo", "Legumbres",
     "Garbanzo seco de cosecha reciente, libre de impurezas.", 7200, 150, "Kilogramos (kg)", (222, 190, 106), 0),
    ("Maíz Amarillo Trillado", "Maíz Amarillo", "Cereales",
     "Maíz amarillo trillado, apto para consumo animal y humano.", 1700, 1000, "Bultos", (241, 196, 15), 1),
    ("Arroz Blanco de Primera", "Arroz Blanco", "Cereales",
     "Arroz blanco de primera calidad, grano largo.", 3200, 700, "Bultos", (245, 245, 235), 1),
    ("Café Pergamino Seco de Altura", "Café Pergamino", "Café",
     "Café pergamino seco cultivado a más de 1700 msnm.", 15500, 400, "Arrobas", (94, 63, 42), 1),
    ("Café Tostado Premium en Grano", "Café Tostado Premium", "Café",
     "Café tostado artesanalmente, notas achocolatadas.", 22000, 100, "Kilogramos (kg)", (61, 39, 24), 0),
    ("Cacao en Grano Fermentado", "Cacao en Grano", "Cacao",
     "Cacao fermentado y secado al sol, listo para procesar.", 13500, 250, "Kilogramos (kg)", (79, 46, 30), 1),
    ("Rosas Rojas de Corte Fresco", "Rosas Rojas", "Flores",
     "Rosas rojas de tallo largo, recién cortadas.", 900, 1200, "Docenas", (200, 30, 60), 1),
    ("Claveles Surtidos de Vivero", "Claveles", "Flores",
     "Claveles de colores surtidos, cultivados en sabana.", 700, 1500, "Docenas", (230, 160, 190), 0),
    ("Suculentas en Maceta Pequeña", "Suculentas", "Plantas",
     "Suculentas variadas listas para venta en vivero.", 4500, 250, "Unidades", (100, 160, 100), 0),
    ("Albahaca Aromática Fresca", "Albahaca", "Aromáticas",
     "Albahaca fresca cortada, ideal para cocina y aromaterapia.", 2000, 120, "Unidades", (70, 140, 60), 0),
    ("Cilantro Fresco de Cosecha Diaria", "Cilantro", "Aromáticas",
     "Cilantro fresco cosechado a diario en huerta propia.", 1200, 200, "Unidades", (85, 150, 70), 0),
    ("Almendras Naturales sin Sal", "Almendras", "Frutos secos",
     "Almendras naturales, sin sal ni conservantes.", 28000, 60, "Kilogramos (kg)", (196, 154, 108), 1),
    ("Nueces de Nogal Criollo", "Nueces", "Frutos secos",
     "Nueces de nogal criollo, cosecha de temporada.", 32000, 45, "Kilogramos (kg)", (110, 76, 51), 0),
    ("Queso Campesino Fresco", "Queso Campesino", "Lácteos",
     "Queso campesino elaborado el mismo día, sabor suave.", 14500, 90, "Kilogramos (kg)", (250, 240, 210), 1),
    ("Leche Fresca de Vaca", "Leche Fresca", "Lácteos",
     "Leche fresca de vaca, entera y sin procesar.", 2600, 300, "Litros", (255, 250, 240), 1),
    ("Huevos Campesinos AA", "Huevos AA", "Huevos",
     "Huevos frescos de gallinas criadas en campo abierto.", 13000, 150, "Docenas", (222, 184, 135), 1),
    ("Pollo Campestre de Levante", "Pollo Campestre", "Carnes",
     "Pollo campestre criado en libertad, carne firme.", 11500, 80, "Unidades", (200, 150, 100), 1),
    ("Miel de Abejas 100% Pura", "Miel de Abejas", "Miel",
     "Miel de abejas pura, sin procesar ni mezclar.", 24000, 100, "Litros", (214, 158, 46), 0),
    ("Trucha Arcoíris Fresca", "Trucha Arcoíris", "Pescados",
     "Trucha arcoíris de criadero, entera y fresca.", 16500, 70, "Kilogramos (kg)", (150, 180, 200), 1),
    ("Semillas de Girasol Seleccionadas", "Semillas de Girasol", "Semillas",
     "Semillas de girasol seleccionadas para siembra.", 9500, 120, "Kilogramos (kg)", (241, 205, 30), 0),
    ("Pimienta Negra en Grano", "Pimienta Negra", "Especias",
     "Pimienta negra en grano, secada tradicionalmente.", 26000, 50, "Kilogramos (kg)", (60, 50, 45), 0),
    ("Compost Orgánico para Cultivos", "Compost Orgánico", "Abonos Orgánicos",
     "Compost orgánico 100% natural, mejora la fertilidad del suelo.", 8500, 200, "Bultos", (92, 64, 40), 1),
]

assert len(PRODUCTOS_PRUEBA) == 30, "Deben ser exactamente 30 registros de prueba."

BUSQUEDA_IMAGEN_REAL = {
    "Mango Tommy": "mango fruit",
    "Naranja Valencia": "orange fruit citrus",
    "Espinaca": "spinach leaves",
    "Zanahoria": "carrot vegetable",
    "Tomate Chonto": "tomato vegetable",
    "Papa Pastusa": "potato",
    "Yuca": "cassava yuca root",
    "Fríjol Cargamanto": "red beans legume",
    "Garbanzo": "chickpeas",
    "Maíz Amarillo": "yellow corn maize",
    "Arroz Blanco": "white rice grain",
    "Café Pergamino": "coffee beans",
    "Café Tostado Premium": "roasted coffee beans",
    "Cacao en Grano": "cacao beans",
    "Rosas Rojas": "red roses flowers",
    "Claveles": "carnation flowers",
    "Suculentas": "succulent plant pot",
    "Albahaca": "basil herb",
    "Cilantro": "coriander cilantro herb",
    "Almendras": "almonds nuts",
    "Nueces": "walnuts",
    "Queso Campesino": "fresh white cheese",
    "Leche Fresca": "fresh milk glass",
    "Huevos AA": "chicken eggs carton",
    "Pollo Campestre": "free range chicken",
    "Miel de Abejas": "honey jar",
    "Trucha Arcoíris": "rainbow trout fish",
    "Semillas de Girasol": "sunflower seeds",
    "Pimienta Negra": "black pepper spice",
    "Compost Orgánico": "organic compost soil",
}


def _get_font(size):
    """Intenta usar una fuente TrueType legible; si no encuentra ninguna
    en el sistema, usa la fuente por defecto de Pillow (siempre disponible,
    aunque más simple) para que el script nunca falle por falta de fuentes."""
    candidatos = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    for ruta in candidatos:
        if os.path.isfile(ruta):
            try:
                return ImageFont.truetype(ruta, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _texto_centrado(draw, texto, y, ancho_imagen, font, color):
    bbox = draw.textbbox((0, 0), texto, font=font)
    ancho_texto = bbox[2] - bbox[0]
    x = (ancho_imagen - ancho_texto) / 2
    draw.text((x, y), texto, font=font, fill=color)


def _descargar_foto_real(termino_busqueda, carpeta_destino, timeout=6):
    """Busca en Wikimedia Commons (repositorio de imágenes de licencia
    libre) una fotografía real para `termino_busqueda`, la descarga y la
    guarda en carpeta_destino con un nombre único.

    Devuelve (ruta_relativa, url_origen) si tuvo éxito, o (None, None) si
    algo falla (sin internet, sin resultados, tiempo agotado, formato no
    soportado, etc.) — cualquier error aquí es silencioso a propósito:
    quien llama a esta función siempre tiene la imagen generada como
    respaldo, así que una foto real es un bono, nunca un requisito.
    """
    api = "https://commons.wikimedia.org/w/api.php"
    headers = {"User-Agent": "CoAgrix-SeedScript/1.0 (uso educativo/desarrollo)"}

    def _get_json(params):
        url = api + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    try:

        busqueda = _get_json({
            "action": "query", "list": "search", "srnamespace": "6",
            "srsearch": f"{termino_busqueda} filetype:bitmap",
            "srlimit": "5", "format": "json",
        })
        resultados = busqueda.get("query", {}).get("search", [])
        titulos_validos = [
            r["title"] for r in resultados
            if re.search(r"\.(jpe?g|png)$", r.get("title", ""), re.IGNORECASE)
        ]
        if not titulos_validos:
            return None, None


        info = _get_json({
            "action": "query", "titles": titulos_validos[0], "prop": "imageinfo",
            "iiprop": "url|extmetadata", "iiurlwidth": "800", "format": "json",
        })
        paginas = info.get("query", {}).get("pages", {})
        pagina = next(iter(paginas.values()), {})
        imageinfo = (pagina.get("imageinfo") or [{}])[0]
        url_imagen = imageinfo.get("thumburl") or imageinfo.get("url")
        if not url_imagen:
            return None, None


        req_img = urllib.request.Request(url_imagen, headers=headers)
        with urllib.request.urlopen(req_img, timeout=timeout) as resp:
            data = resp.read()

        ext = "png" if url_imagen.lower().endswith(".png") else "jpg"
        os.makedirs(carpeta_destino, exist_ok=True)
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(carpeta_destino, filename)

        with Image.open(io.BytesIO(data)) as img:
            img.verify()
        with open(filepath, "wb") as f:
            f.write(data)

        return f"uploads/{filename}", url_imagen

    except (urllib.error.URLError, urllib.error.HTTPError, socket.timeout,
            json.JSONDecodeError, KeyError, OSError, ValueError):
        return None, None


def obtener_imagen_para_producto(producto_nombre, categoria, color_rgb, carpeta_destino):
    """Intenta primero una foto real (Wikimedia Commons); si no lo logra,
    genera la imagen de respaldo. Siempre devuelve una ruta relativa
    utilizable, nunca None."""
    termino = BUSQUEDA_IMAGEN_REAL.get(producto_nombre)
    if termino:
        ruta, url_origen = _descargar_foto_real(termino, carpeta_destino)
        if ruta:
            print(f"      -> foto real descargada (Wikimedia Commons): {url_origen}")
            return ruta
    return generar_imagen_prueba(producto_nombre, categoria, color_rgb, carpeta_destino)


def generar_imagen_prueba(nombre_producto, categoria, color_rgb, carpeta_destino):
    """Genera una imagen JPEG de 800x600 con un color de fondo apropiado
    al producto y su nombre/categoría escritos encima, y la guarda con un
    nombre único en carpeta_destino. Devuelve la ruta relativa
    'uploads/xxxx.jpg' lista para guardar en la base de datos."""
    ancho, alto = 800, 600
    r, g, b = color_rgb
    img = Image.new('RGB', (ancho, alto), color=(r, g, b))
    draw = ImageDraw.Draw(img)


    franja_alto = 160
    franja_color = tuple(max(0, c - 60) for c in (r, g, b))
    draw.rectangle([0, alto - franja_alto, ancho, alto], fill=franja_color)

    font_titulo = _get_font(46)
    font_categoria = _get_font(28)

    _texto_centrado(draw, nombre_producto, alto - franja_alto + 30, ancho, font_titulo, (255, 255, 255))
    _texto_centrado(draw, categoria.upper(), alto - franja_alto + 95, ancho, font_categoria, (255, 255, 255))

    os.makedirs(carpeta_destino, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(carpeta_destino, filename)
    img.save(filepath, format='JPEG', quality=88)
    return f"uploads/{filename}"


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


def get_categoria_id(nombre):
    row = query_db("SELECT id FROM categorias WHERE nombre = %s", (nombre,), one=True)
    if row:
        return row['id']

    return execute_db("INSERT INTO categorias (nombre) VALUES (%s)", (nombre,))


def get_primer_campesino_existente():
    """Campesino 1: el primero que ya exista en el proyecto (no se crea
    ninguno nuevo para este rol, tal como pide la tarea: 'usuario
    existente del proyecto')."""
    return query_db(
        """
        SELECT c.*, u.nombre AS usuario_nombre, u.email
        FROM campesinos c
        JOIN usuarios u ON c.usuario_id = u.id
        ORDER BY c.id ASC
        LIMIT 1
        """,
        one=True
    )


def get_or_create_campesino_2():
    usuario = query_db("SELECT * FROM usuarios WHERE email = %s", (CAMPESINO_2['email'],), one=True)
    if usuario:
        campesino = query_db("SELECT * FROM campesinos WHERE usuario_id = %s", (usuario['id'],), one=True)
        if campesino:
            print(f"  - Campesino 2 ya existe (usuario_id={usuario['id']}, campesino_id={campesino['id']}). Se reutiliza.")
            return campesino

    rol_campesino = query_db("SELECT id FROM roles WHERE nombre = 'Campesino'", one=True)
    if not rol_campesino:
        raise RuntimeError("No existe el rol 'Campesino' en la tabla roles. Revisa sql/coagrix.sql.")

    ubicacion_id = get_or_create_ubicacion(**CAMPESINO_2['ubicacion'])

    password_hash = generate_password_hash(CAMPESINO_2['password'])
    usuario_id = execute_db(
        "INSERT INTO usuarios (nombre, email, password, rol_id, estado) VALUES (%s, %s, %s, %s, 'Activo')",
        (CAMPESINO_2['nombre'], CAMPESINO_2['email'], password_hash, rol_campesino['id'])
    )
    if not usuario_id:
        raise RuntimeError("No se pudo crear el usuario del Campesino 2.")

    campesino_id = execute_db(
        "INSERT INTO campesinos (usuario_id, telefono, foto_perfil, ubicacion_id, descripcion) "
        "VALUES (%s, %s, NULL, %s, %s)",
        (usuario_id, CAMPESINO_2['telefono'], ubicacion_id, CAMPESINO_2['descripcion'])
    )
    print(f"  - Campesino 2 creado: usuario_id={usuario_id}, campesino_id={campesino_id}, email={CAMPESINO_2['email']}")
    return query_db("SELECT * FROM campesinos WHERE id = %s", (campesino_id,), one=True)


def publicacion_ya_existe(titulo, campesino_id):
    return query_db(
        "SELECT id FROM publicaciones WHERE titulo = %s AND campesino_id = %s",
        (titulo, campesino_id), one=True
    )


def main():
    upload_folder = Config.UPLOAD_FOLDER
    print("=== Seed de datos de prueba CoAgrix ===")
    print(f"Carpeta de imágenes: {upload_folder}")

    campesino_1 = get_primer_campesino_existente()
    if not campesino_1:
        print(
            "\nNo se encontró ningún campesino existente en la base de datos.\n"
            "Crea primero una cuenta de campesino desde la app (registro) o\n"
            "carga sql/coagrix.sql (que ya incluye uno), y vuelve a ejecutar este script."
        )
        sys.exit(1)
    print(f"  - Campesino 1 (existente): usuario={campesino_1['usuario_nombre']} "
          f"({campesino_1['email']}), campesino_id={campesino_1['id']}")

    if not campesino_1.get('ubicacion_id'):
        ubicacion_id = get_or_create_ubicacion(**UBICACION_CAMPESINO_1_DEFECTO)
        execute_db("UPDATE campesinos SET ubicacion_id = %s WHERE id = %s", (ubicacion_id, campesino_1['id']))
        print("  - Campesino 1 no tenía ubicación asignada; se le asignó una por defecto.")

    campesino_2 = get_or_create_campesino_2()

    campesinos = [campesino_1['id'], campesino_2['id']]

    creadas = 0
    saltadas = 0

    for i, (titulo, producto_nombre, categoria_nombre, descripcion, precio, cantidad,
            unidad, color_rgb, transporte) in enumerate(PRODUCTOS_PRUEBA):
        campesino_id = campesinos[0] if i < 15 else campesinos[1]

        if publicacion_ya_existe(titulo, campesino_id):
            print(f"  [omitido] Ya existe: \"{titulo}\" (campesino_id={campesino_id})")
            saltadas += 1
            continue

        categoria_id = get_categoria_id(categoria_nombre)
        producto_id = get_or_create_producto(producto_nombre, categoria_id, descripcion)

        imagen = obtener_imagen_para_producto(producto_nombre, categoria_nombre, color_rgb, upload_folder)

        publicacion_id = execute_db(
            """
            INSERT INTO publicaciones
                (campesino_id, producto_id, titulo, descripcion, precio_empresa, precio_comerciante,
                 cantidad_disponible, unidad_medida, imagen, transporte, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Activa')
            """,
            (campesino_id, producto_id, titulo, descripcion, precio, precio, cantidad, unidad, imagen, transporte)
        )
        if not publicacion_id:
            print(f"  [ERROR] No se pudo crear la publicación \"{titulo}\".")
            continue

        execute_db(
            "INSERT INTO historial_precios (publicacion_id, tipo_precio, precio_anterior, precio_nuevo) VALUES (%s, 'empresa', %s, %s)",
            (publicacion_id, precio, precio)
        )
        execute_db(
            "INSERT INTO historial_precios (publicacion_id, tipo_precio, precio_anterior, precio_nuevo) VALUES (%s, 'comerciante', %s, %s)",
            (publicacion_id, precio, precio)
        )
        insert_archivo(publicacion_id, imagen)

        print(f"  [creado] \"{titulo}\" -> publicacion_id={publicacion_id}, imagen={imagen}, campesino_id={campesino_id}")
        creadas += 1

    print("\n=== Resumen ===")
    print(f"Publicaciones creadas nuevas: {creadas}")
    print(f"Publicaciones ya existentes (omitidas): {saltadas}")
    print(f"Total de publicaciones de prueba definidas: {len(PRODUCTOS_PRUEBA)}")
    print("Listo. Vuelve a ejecutar este script cuando quieras: no duplica nada.")


if __name__ == '__main__':
    main()
