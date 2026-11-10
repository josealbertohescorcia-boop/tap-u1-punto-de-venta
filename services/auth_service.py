import hashlib
import sqlite3
from typing import Optional
from models.usuario import Usuario
from repositories.usuario_repository import UsuarioRepository

class AuthService:
    def __init__(self, usuario_repo: UsuarioRepository = None):
        self.usuario_repo = usuario_repo or UsuarioRepository()
        self.usuario_actual: Optional[Usuario] = None

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def iniciar_sesion(self, username: str, password: str) -> Usuario:
        """
        Valida las credenciales de un usuario.
        Lanza ValueError si faltan datos, si las credenciales son incorrectas
        o si el usuario se encuentra inactivo.
        """
        user_clean = (username or "").strip()
        pass_clean = (password or "").strip()

        if not user_clean or not pass_clean:
            raise ValueError("Por favor ingrese su usuario y contraseña.")

        usuario = self.usuario_repo.obtener_por_username(user_clean)
        if not usuario:
            raise ValueError("Usuario o contraseña incorrectos.")

        if not usuario.esta_activo:
            raise ValueError("El usuario se encuentra inactivo. Contacte al administrador.")

        pass_hash = self.hash_password(pass_clean)
        if usuario.password_hash != pass_hash:
            raise ValueError("Usuario o contraseña incorrectos.")

        self.usuario_actual = usuario
        return usuario

    def cerrar_sesion(self) -> None:
        self.usuario_actual = None

    def get_usuario_actual(self) -> Optional[Usuario]:
        return self.usuario_actual
