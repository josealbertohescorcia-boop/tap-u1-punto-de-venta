import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
from db.connection import obtener_conexion
from models.venta import Venta
from models.detalle_venta import DetalleVenta

class VentaRepository:
    def __init__(self, db_path: str = None):
        self.db_path = db_path

    def registrar_venta_transaccional(self, usuario_id: int, items: List[Dict[str, Any]], fecha_iso: str = None) -> int:
        """
        Registra una venta y sus detalles de forma atómica (transacción SQLite),
        descontando el stock correspondiente.
        Si la cantidad supera el stock o hay algún fallo, revierte todo (ROLLBACK).
        """
        fecha = fecha_iso or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_venta = sum(item["cantidad"] * item["precio_unitario"] for item in items)

        conn = obtener_conexion(self.db_path)
        try:
            conn.execute("BEGIN TRANSACTION;")
            cursor = conn.cursor()

            # 1. Validar y descontar stock para cada producto
            for item in items:
                prod_id = item["producto_id"]
                cantidad = item["cantidad"]

                cursor.execute("SELECT stock, nombre, activo FROM productos WHERE id = ?;", (prod_id,))
                prod_row = cursor.fetchone()
                if not prod_row:
                    raise ValueError(f"El producto con ID {prod_id} no existe.")

                if not prod_row["activo"]:
                    raise ValueError(f"El producto '{prod_row['nombre']}' se encuentra inactivo y no puede venderse.")

                stock_actual = prod_row["stock"]
                if cantidad > stock_actual:
                    raise ValueError(f"Stock insuficiente para '{prod_row['nombre']}'. Disponible: {stock_actual}, Solicitado: {cantidad}.")

                cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?;", (cantidad, prod_id))

            # 2. Insertar encabezado de venta
            cursor.execute("""
                INSERT INTO ventas (fecha, usuario_id, total)
                VALUES (?, ?, ?);
            """, (fecha, usuario_id, total_venta))
            venta_id = cursor.lastrowid

            # 3. Insertar detalle de la venta (precio_unitario se congela en el detalle)
            for item in items:
                subtotal = round(item["cantidad"] * item["precio_unitario"], 2)
                cursor.execute("""
                    INSERT INTO detalle_venta (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?);
                """, (venta_id, item["producto_id"], item["cantidad"], item["precio_unitario"], subtotal))

            conn.commit()
            return venta_id

        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def listar_ventas(self, busqueda: str = None) -> List[Dict[str, Any]]:
        """Retorna lista de ventas con información del usuario (JOIN)."""
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT v.id, v.fecha, v.total, v.usuario_id, u.username AS usuario_nombre
                FROM ventas v
                INNER JOIN usuarios_sistema u ON v.usuario_id = u.id
                WHERE 1=1
            """
            params = []
            if busqueda:
                query += " AND (CAST(v.id AS TEXT) LIKE ? OR LOWER(u.username) LIKE ? OR v.fecha LIKE ?)"
                like_t = f"%{busqueda.strip().lower()}%"
                params.extend([like_t, like_t, like_t])

            query += " ORDER BY v.id DESC;"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def obtener_detalles_por_venta(self, venta_id: int) -> List[Dict[str, Any]]:
        """JOIN de detalles de venta con el producto para mostrar códigos y nombres."""
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT dv.id, dv.venta_id, dv.producto_id, dv.cantidad, dv.precio_unitario, dv.subtotal,
                       p.codigo AS producto_codigo, p.nombre AS producto_nombre
                FROM detalle_venta dv
                INNER JOIN productos p ON dv.producto_id = p.id
                WHERE dv.venta_id = ?
                ORDER BY dv.id ASC;
            """
            cursor.execute(query, (venta_id,))
            return [dict(row) for row in cursor.fetchall()]

    def listar_detalles_con_join(self, busqueda: str = None) -> List[Dict[str, Any]]:
        """
        JOIN obligatorio: detalle + nombre del producto + folio de venta + vendedor.
        """
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                    dv.id AS detalle_id,
                    v.id AS folio_venta,
                    v.fecha AS fecha_venta,
                    u.username AS vendedor,
                    p.codigo AS codigo_producto,
                    p.nombre AS nombre_producto,
                    c.nombre AS categoria,
                    dv.cantidad,
                    dv.precio_unitario,
                    dv.subtotal
                FROM detalle_venta dv
                INNER JOIN ventas v ON dv.venta_id = v.id
                INNER JOIN productos p ON dv.producto_id = p.id
                INNER JOIN categorias c ON p.categoria_id = c.id
                INNER JOIN usuarios_sistema u ON v.usuario_id = u.id
                WHERE 1=1
            """
            params = []
            if busqueda:
                term = f"%{busqueda.strip().lower()}%"
                query += """
                    AND (CAST(v.id AS TEXT) LIKE ? 
                         OR LOWER(p.nombre) LIKE ? 
                         OR LOWER(p.codigo) LIKE ? 
                         OR LOWER(u.username) LIKE ?)
                """
                params.extend([term, term, term, term])

            query += " ORDER BY v.id DESC, dv.id ASC;"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def obtener_reporte_stock_bajo(self, umbral: int = 5) -> List[Dict[str, Any]]:
        """Consulta reporte de productos con stock <= umbral (caso problemático)."""
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT p.id, p.codigo, p.nombre, c.nombre AS categoria_nombre, 
                       p.precio, p.stock, p.activo
                FROM productos p
                INNER JOIN categorias c ON p.categoria_id = c.id
                WHERE p.stock <= ?
                ORDER BY p.stock ASC, p.nombre ASC;
            """
            cursor.execute(query, (umbral,))
            return [dict(row) for row in cursor.fetchall()]

    def obtener_reporte_mas_vendidos(self, limite: int = 15) -> List[Dict[str, Any]]:
        """Consulta productos más vendidos con total unidades y monto generado."""
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT p.id, p.codigo, p.nombre, c.nombre AS categoria_nombre,
                       SUM(dv.cantidad) AS total_vendido,
                       ROUND(SUM(dv.subtotal), 2) AS total_recaudado
                FROM detalle_venta dv
                INNER JOIN productos p ON dv.producto_id = p.id
                INNER JOIN categorias c ON p.categoria_id = c.id
                GROUP BY p.id, p.codigo, p.nombre, c.nombre
                ORDER BY total_vendido DESC
                LIMIT ?;
            """
            cursor.execute(query, (limite,))
            return [dict(row) for row in cursor.fetchall()]
