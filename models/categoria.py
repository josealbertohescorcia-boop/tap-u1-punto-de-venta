class Categoria:
    """Representa una categoría de productos en el catálogo."""
    def __init__(self, id: int = None, nombre: str = "", activo: int = 1):
        self.id = id
        self.nombre = nombre.strip() if nombre else ""
        self.activo = activo

    @property
    def esta_activa(self) -> bool:
        return bool(self.activo)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "activo": self.activo
        }

    def __repr__(self) -> str:
        return f"<Categoria id={self.id} nombre='{self.nombre}' activo={self.activo}>"
