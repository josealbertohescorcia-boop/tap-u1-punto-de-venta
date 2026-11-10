import sqlite3
from typing import List, Optional
from db.connection import obtener_conexion
from models.producto import Producto

class ProductoRepository:
    def __init__(self, db_path: str = None):
        self.db_path = db_path

    def _mapear_fila(self, fila: sqlite3.Row) -> Producto:
        cat_nombre = fila["categoria_nombre"] if "categoria_nombre" in fila.keys() else ""
        return Producto(
            id=fila["id"],
            codigo=fila["codigo"],
            nombre=fila["nombre"],
            categoria_id=fila["categoria_id"],
            precio=fila["precio"],
            stock=fila["stock"],
            activo=fila["activo"],
            categoria_nombre=cat_nombre
        )

    def obtener_por_id(self, prod_id: int) -> Optional[Producto]:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, c.nombre AS categoria_nombre
                FROM productos p
                INNER JOIN categorias c ON p.categoria_id = c.id
                WHERE p.id = ?;
            """, (prod_id,))
            fila = cursor.fetchone()
            return self._mapear_fila(fila) if fila else None

    def obtener_por_codigo(self, codigo: str) -> Optional[Producto]:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, c.nombre AS categoria_nombre
                FROM productos p
                INNER JOIN categorias c ON p.categoria_id = c.id
                WHERE LOWER(p.codigo) = LOWER(?);
            """, (codigo.strip(),))
            fila = cursor.fetchone()
            return self._mapear_fila(fila) if fila else None

    def listar_todos(self, solo_activos: bool = False, busqueda: str = None, categoria_id: int = None) -> List[Producto]:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT p.*, c.nombre AS categoria_nombre
                FROM productos p
                INNER JOIN categorias c ON p.categoria_id = c.id
                WHERE 1=1
            """
            params = []

            if solo_activos:
                query += " AND p.activo = 1"
            if categoria_id:
                query += " AND p.categoria_id = ?"
                params.append(categoria_id)
            if busqueda:
                query += " AND (LOWER(p.codigo) LIKE ? OR LOWER(p.nombre) LIKE ? OR LOWER(c.nombre) LIKE ?)"
                like_term = f"%{busqueda.strip().lower()}%"
                params.extend([like_term, like_term, like_term])

            query += " ORDER BY p.nombre ASC;"
            cursor.execute(query, params)
            return [self._mapear_fila(f) for f in cursor.fetchall()]

    def crear(self, producto: Producto) -> int:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO productos (codigo, nombre, categoria_id, precio, stock, activo)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (producto.codigo, producto.nombre, producto.categoria_id, producto.precio, producto.stock, producto.activo))
            conn.commit()
            return cursor.lastrowid

    def actualizar(self, producto: Producto) -> bool:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE productos
                SET codigo = ?, nombre = ?, categoria_id = ?, precio = ?, stock = ?, activo = ?
                WHERE id = ?;
            """, (producto.codigo, producto.nombre, producto.categoria_id, producto.precio, producto.stock, producto.activo, producto.id))
            conn.commit()
            return cursor.rowcount > 0

    def cambiar_estado(self, prod_id: int, activo: int) -> bool:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE productos SET activo = ? WHERE id = ?;", (activo, prod_id))
            conn.commit()
            return cursor.rowcount > 0

    def eliminar(self, prod_id: int) -> bool:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM productos WHERE id = ?;", (prod_id,))
            conn.commit()
            return cursor.rowcount > 0

    def contar_ventas_asociadas(self, prod_id: int) -> int:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM detalle_venta WHERE producto_id = ?;", (prod_id,))
            return cursor.fetchone()[0]

    def descontar_stock(self, conn: sqlite3.Connection, prod_id: int, cantidad: int) -> bool:
        """
        Descuenta stock dentro de una transacción activa.
        Lanza ValueError si el stock resulta insuficiente.
        """
        cursor = conn.cursor()
        cursor.execute("SELECT stock FROM productos WHERE id = ?;", (prod_id,))
        fila = cursor.fetchone()
        if not fila:
            raise ValueError(f"El producto con ID {prod_id} no existe.")

        stock_actual = fila["stock"]
        if stock_actual < cantidad:
            raise ValueError(f"Stock insuficiente. Disponible: {stock_actual}, Solicitado: {cantidad}.")

        cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?;", (cantidad, prod_id))
        return True
