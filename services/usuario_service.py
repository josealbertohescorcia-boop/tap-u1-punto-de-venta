import sqlite3
from typing import List, Optional
from models.usuario import Usuario
from repositories.usuario_repository import UsuarioRepository
from services.auth_service import AuthService

class UsuarioService:
    def __init__(self, usuario_repo: UsuarioRepository = None):
        self.usuario_repo = usuario_repo or UsuarioRepository()

    def listar_usuarios(self) -> List[Usuario]:
        return self.usuario_repo.listar_todos()

    def crear_usuario(self, username: str, password: str, rol: str, activo: int = 1) -> int:
        username = (username or "").strip()
        password = (password or "").strip()
        rol = (rol or "operador").strip().lower()

        if not username:
            raise ValueError("El nombre de usuario no puede estar vacío.")
        if len(username) < 3:
            raise ValueError("El nombre de usuario debe tener al menos 3 caracteres.")
        if not password:
            raise ValueError("La contraseña no puede estar vacía.")
        if len(password) < 4:
            raise ValueError("La contraseña debe tener al menos 4 caracteres.")
        if rol not in ("administrador", "operador"):
            raise ValueError("El rol debe ser 'administrador' u 'operador'.")

        existente = self.usuario_repo.obtener_por_username(username)
        if existente:
            raise ValueError(f"Ya existe un usuario con el nombre '{username}'.")

        pass_hash = AuthService.hash_password(password)
        nuevo_usuario = Usuario(
            username=username,
            password_hash=pass_hash,
            rol=rol,
            activo=int(activo)
        )
        try:
            return self.usuario_repo.crear(nuevo_usuario)
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Error de integridad en base de datos: {e}")

    def actualizar_usuario(self, user_id: int, username: str, rol: str, activo: int) -> bool:
        username = (username or "").strip()
        rol = (rol or "").strip().lower()

        if not username:
            raise ValueError("El nombre de usuario no puede estar vacío.")
        if rol not in ("administrador", "operador"):
            raise ValueError("El rol debe ser 'administrador' u 'operador'.")

        existente = self.usuario_repo.obtener_por_username(username)
        if existente and existente.id != user_id:
            raise ValueError(f"Ya existe otro usuario con el nombre '{username}'.")

        usuario = Usuario(id=user_id, username=username, rol=rol, activo=int(activo))
        return self.usuario_repo.actualizar(usuario)

    def cambiar_password(self, user_id: int, nuevo_password: str) -> bool:
        nuevo_password = (nuevo_password or "").strip()
        if not nuevo_password or len(nuevo_password) < 4:
            raise ValueError("La nueva contraseña debe tener al menos 4 caracteres.")
        nuevo_hash = AuthService.hash_password(nuevo_password)
        return self.usuario_repo.cambiar_password(user_id, nuevo_hash)

    def alternar_estado(self, user_id: int, nuevo_estado: int) -> bool:
        return self.usuario_repo.cambiar_estado(user_id, int(nuevo_estado))
