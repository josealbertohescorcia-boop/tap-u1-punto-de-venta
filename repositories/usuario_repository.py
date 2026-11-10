import sqlite3
from typing import List, Optional
from db.connection import obtener_conexion
from models.usuario import Usuario

class UsuarioRepository:
    def __init__(self, db_path: str = None):
        self.db_path = db_path

    def _mapear_fila(self, fila: sqlite3.Row) -> Usuario:
        return Usuario(
            id=fila["id"],
            username=fila["username"],
            password_hash=fila["password_hash"],
            rol=fila["rol"],
            activo=fila["activo"]
        )

    def obtener_por_id(self, user_id: int) -> Optional[Usuario]:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios_sistema WHERE id = ?;", (user_id,))
            fila = cursor.fetchone()
            return self._mapear_fila(fila) if fila else None

    def obtener_por_username(self, username: str) -> Optional[Usuario]:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios_sistema WHERE username = ?;", (username.strip(),))
            fila = cursor.fetchone()
            return self._mapear_fila(fila) if fila else None

    def listar_todos(self) -> List[Usuario]:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios_sistema ORDER BY id ASC;")
            return [self._mapear_fila(f) for f in cursor.fetchall()]

    def crear(self, usuario: Usuario) -> int:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usuarios_sistema (username, password_hash, rol, activo)
                VALUES (?, ?, ?, ?);
            """, (usuario.username, usuario.password_hash, usuario.rol, usuario.activo))
            conn.commit()
            return cursor.lastrowid

    def actualizar(self, usuario: Usuario) -> bool:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE usuarios_sistema
                SET username = ?, rol = ?, activo = ?
                WHERE id = ?;
            """, (usuario.username, usuario.rol, usuario.activo, usuario.id))
            conn.commit()
            return cursor.rowcount > 0

    def cambiar_password(self, user_id: int, nuevo_hash: str) -> bool:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE usuarios_sistema
                SET password_hash = ?
                WHERE id = ?;
            """, (nuevo_hash, user_id))
            conn.commit()
            return cursor.rowcount > 0

    def cambiar_estado(self, user_id: int, activo: int) -> bool:
        with obtener_conexion(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE usuarios_sistema
                SET activo = ?
                WHERE id = ?;
            """, (activo, user_id))
            conn.commit()
            return cursor.rowcount > 0
