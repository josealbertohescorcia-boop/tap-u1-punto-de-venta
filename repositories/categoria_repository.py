import sqlite3
from typing import List, Optional
from db.connection import obtener_conexion
from models.categoria import Categoria

class CategoriaRepository:
    def __init__(self, db_path: str = None):
        self.db_path = db_path

    def _mapear_fila(self, fila: sqlite3.Row) -> Categoria:
        return Categoria(
            id=fila["id"],
            nombre=fila["nombre"],
            activo=fila["activo"]
        )

    def obtener_por_id(self, cat_id: int) -> Optional[Categoria]:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categorias WHERE id = ?;", (cat_id,))
            fila = cursor.fetchone()
            return self._mapear_fila(fila) if fila else None

    def obtener_por_nombre(self, nombre: str) -> Optional[Categoria]:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categorias WHERE LOWER(nombre) = LOWER(?);", (nombre.strip(),))
            fila = cursor.fetchone()
            return self._mapear_fila(fila) if fila else None

    def listar_todas(self, solo_activas: bool = False, busqueda: str = None) -> List[Categoria]:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM categorias WHERE 1=1"
            params = []

            if solo_activas:
                query += " AND activo = 1"
            if busqueda:
                query += " AND LOWER(nombre) LIKE ?"
                params.append(f"%{busqueda.strip().lower()}%")

            query += " ORDER BY nombre ASC;"
            cursor.execute(query, params)
            return [self._mapear_fila(f) for f in cursor.fetchall()]

    def crear(self, categoria: Categoria) -> int:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO categorias (nombre, activo)
                VALUES (?, ?);
            """, (categoria.nombre, categoria.activo))
            conn.commit()
            return cursor.lastrowid

    def actualizar(self, categoria: Categoria) -> bool:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE categorias
                SET nombre = ?, activo = ?
                WHERE id = ?;
            """, (categoria.nombre, categoria.activo, categoria.id))
            conn.commit()
            return cursor.rowcount > 0

    def cambiar_estado(self, cat_id: int, activo: int) -> bool:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE categorias SET activo = ? WHERE id = ?;", (activo, cat_id))
            conn.commit()
            return cursor.rowcount > 0

    def eliminar(self, cat_id: int) -> bool:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categorias WHERE id = ?;", (cat_id,))
            conn.commit()
            return cursor.rowcount > 0

    def contar_productos_asociados(self, cat_id: int) -> int:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM productos WHERE categoria_id = ?;", (cat_id,))
            return cursor.fetchone()[0]

    def contar_productos_activos_asociados(self, cat_id: int) -> int:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM productos WHERE categoria_id = ? AND activo = 1;", (cat_id,))
            return cursor.fetchone()[0]
