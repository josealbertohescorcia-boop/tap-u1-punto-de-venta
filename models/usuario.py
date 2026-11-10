class Usuario:
    """Representa a un usuario con credenciales en el sistema."""
    def __init__(self, id: int = None, username: str = "", password_hash: str = "", rol: str = "operador", activo: int = 1):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.rol = rol
        self.activo = activo

    @property
    def es_administrador(self) -> bool:
        return self.rol == "administrador"

    @property
    def esta_activo(self) -> bool:
        return bool(self.activo)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "rol": self.rol,
            "activo": self.activo
        }

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} username='{self.username}' rol='{self.rol}' activo={self.activo}>"
