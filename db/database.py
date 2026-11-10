import os
import hashlib
import sqlite3
from datetime import datetime
from db.connection import obtener_conexion

def hashear_password(password: str) -> str:
    """Genera el hash SHA-256 de una contraseña en texto plano."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def inicializar_base_datos(db_path: str = None) -> None:
    """
    Crea las tablas si no existen y llena datos iniciales (semilla)
    cumpliendo con la rúbrica y datos de prueba.
    """
    conexion = obtener_conexion(db_path)
    cursor = conexion.cursor()

    try:
        # 1. Tabla usuarios_sistema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios_sistema (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                rol TEXT NOT NULL CHECK(rol IN ('administrador', 'operador')),
                activo INTEGER NOT NULL DEFAULT 1 CHECK(activo IN (0, 1))
            );
        """)

        # 2. Tabla categorias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                activo INTEGER NOT NULL DEFAULT 1 CHECK(activo IN (0, 1))
            );
        """)

        # 3. Tabla productos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                categoria_id INTEGER NOT NULL,
                precio REAL NOT NULL CHECK(precio > 0),
                stock INTEGER NOT NULL CHECK(stock >= 0),
                activo INTEGER NOT NULL DEFAULT 1 CHECK(activo IN (0, 1)),
                FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE RESTRICT
            );
        """)

        # 4. Tabla ventas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                usuario_id INTEGER NOT NULL,
                total REAL NOT NULL CHECK(total >= 0),
                FOREIGN KEY (usuario_id) REFERENCES usuarios_sistema(id) ON DELETE RESTRICT
            );
        """)

        # 5. Tabla detalle_venta
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalle_venta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL CHECK(cantidad > 0),
                precio_unitario REAL NOT NULL CHECK(precio_unitario >= 0),
                subtotal REAL NOT NULL CHECK(subtotal >= 0),
                FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
                FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE RESTRICT
            );
        """)

        conexion.commit()

        # Semilla de datos si la base está recién creada
        cursor.execute("SELECT COUNT(*) FROM usuarios_sistema;")
        total_usuarios = cursor.fetchone()[0]

        if total_usuarios == 0:
            _insertar_datos_semilla(conexion)

    finally:
        conexion.close()

def _insertar_datos_semilla(conexion: sqlite3.Connection) -> None:
    """Inserta los datos mínimos de prueba exigidos por la rúbrica."""
    cursor = conexion.cursor()

    # Usuarios requeridos: admin y operador
    admin_pass = hashear_password("admin123")
    operador_pass = hashear_password("operador123")

    cursor.execute("""
        INSERT INTO usuarios_sistema (username, password_hash, rol, activo)
        VALUES 
            ('admin', ?, 'administrador', 1),
            ('operador', ?, 'operador', 1);
    """, (admin_pass, operador_pass))

    # Categorías de prueba (mínimo 5, más una inactiva)
    categorias = [
        ("Papelería y Cuadernos", 1),
        ("Bebidas y Refrescos", 1),
        ("Snacks y Botanas", 1),
        ("Artículos de Oficina", 1),
        ("Dulces y Golosinas", 1),
        ("Temporada Pasada (Inactiva)", 0),
    ]
    cursor.executemany("INSERT INTO categorias (nombre, activo) VALUES (?, ?);", categorias)

    # Obtenemos los IDs de las categorías insertadas
    cursor.execute("SELECT id, nombre FROM categorias;")
    cat_map = {row["nombre"]: row["id"] for row in cursor.fetchall()}

    # Productos de prueba (mínimo 8 registros, con casos normales, stock bajo y uno inactivo)
    productos = [
        ("PROD-001", "Cuaderno Profesional Rayado", cat_map["Papelería y Cuadernos"], 35.50, 25, 1),
        ("PROD-002", "Bolígrafo Gel Tinta Negra", cat_map["Papelería y Cuadernos"], 12.00, 48, 1),
        ("PROD-003", "Paquete Hojas Blancas 500u", cat_map["Papelería y Cuadernos"], 115.00, 3, 1),  # Stock bajo (<= 5)
        ("PROD-004", "Agua Purificada 600ml", cat_map["Bebidas y Refrescos"], 15.00, 30, 1),
        ("PROD-005", "Jugo de Naranja 500ml", cat_map["Bebidas y Refrescos"], 22.50, 12, 1),
        ("PROD-006", "Papas Fritas Onduladas 45g", cat_map["Snacks y Botanas"], 20.00, 4, 1),        # Stock bajo (<= 5)
        ("PROD-007", "Grapadora Metálica Estándar", cat_map["Artículos de Oficina"], 88.00, 10, 1),
        ("PROD-008", "Calculadora Científica 240F", cat_map["Artículos de Oficina"], 249.99, 0, 1),   # Stock crítico (0)
        ("PROD-009", "Chocolate con Almendras 50g", cat_map["Dulces y Golosinas"], 18.00, 35, 1),
        ("PROD-010", "Sacapuntas de Manivela Retro", cat_map["Temporada Pasada (Inactiva)"], 45.00, 8, 0), # Inactivo
    ]

    cursor.executemany("""
        INSERT INTO productos (codigo, nombre, categoria_id, precio, stock, activo)
        VALUES (?, ?, ?, ?, ?, ?);
    """, productos)

    # Obtenemos los IDs de productos y usuarios para crear al menos 3 ventas históricas
    cursor.execute("SELECT id, username FROM usuarios_sistema;")
    usr_map = {row["username"]: row["id"] for row in cursor.fetchall()}

    cursor.execute("SELECT id, codigo, precio FROM productos;")
    prod_map = {row["codigo"]: (row["id"], row["precio"]) for row in cursor.fetchall()}

    admin_id = usr_map["admin"]
    operador_id = usr_map["operador"]

    # Venta 1: Realizada por el operador (2 bolígrafos + 1 cuaderno)
    v1_items = [
        (prod_map["PROD-002"][0], 2, prod_map["PROD-002"][1], 2 * prod_map["PROD-002"][1]),
        (prod_map["PROD-001"][0], 1, prod_map["PROD-001"][1], 1 * prod_map["PROD-001"][1]),
    ]
    total_v1 = sum(item[3] for item in v1_items)
    cursor.execute("""
        INSERT INTO ventas (fecha, usuario_id, total)
        VALUES ('2026-11-01 10:30:00', ?, ?);
    """, (operador_id, total_v1))
    v1_id = cursor.lastrowid
    for p_id, cant, precio_u, subt in v1_items:
        cursor.execute("""
            INSERT INTO detalle_venta (venta_id, producto_id, cantidad, precio_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?);
        """, (v1_id, p_id, cant, precio_u, subt))

    # Venta 2: Realizada por admin (1 grapadora + 2 chocolates)
    v2_items = [
        (prod_map["PROD-007"][0], 1, prod_map["PROD-007"][1], 1 * prod_map["PROD-007"][1]),
        (prod_map["PROD-009"][0], 2, prod_map["PROD-009"][1], 2 * prod_map["PROD-009"][1]),
    ]
    total_v2 = sum(item[3] for item in v2_items)
    cursor.execute("""
        INSERT INTO ventas (fecha, usuario_id, total)
        VALUES ('2026-11-05 14:15:00', ?, ?);
    """, (admin_id, total_v2))
    v2_id = cursor.lastrowid
    for p_id, cant, precio_u, subt in v2_items:
        cursor.execute("""
            INSERT INTO detalle_venta (venta_id, producto_id, cantidad, precio_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?);
        """, (v2_id, p_id, cant, precio_u, subt))

    # Venta 3: Realizada por operador (venta que redujo paquete hojas blancas a stock bajo)
    v3_items = [
        (prod_map["PROD-003"][0], 5, prod_map["PROD-003"][1], 5 * prod_map["PROD-003"][1]),
        (prod_map["PROD-004"][0], 3, prod_map["PROD-004"][1], 3 * prod_map["PROD-004"][1]),
    ]
    total_v3 = sum(item[3] for item in v3_items)
    cursor.execute("""
        INSERT INTO ventas (fecha, usuario_id, total)
        VALUES ('2026-11-09 16:45:00', ?, ?);
    """, (operador_id, total_v3))
    v3_id = cursor.lastrowid
    for p_id, cant, precio_u, subt in v3_items:
        cursor.execute("""
            INSERT INTO detalle_venta (venta_id, producto_id, cantidad, precio_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?);
        """, (v3_id, p_id, cant, precio_u, subt))

    conexion.commit()
