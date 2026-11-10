class Producto:
    """Representa un producto dentro del inventario."""
    def __init__(self, id: int = None, codigo: str = "", nombre: str = "", categoria_id: int = None,
                 precio: float = 0.0, stock: int = 0, activo: int = 1, categoria_nombre: str = ""):
        self.id = id
        self.codigo = codigo.strip().upper() if codigo else ""
        self.nombre = nombre.strip() if nombre else ""
        self.categoria_id = categoria_id
        self.precio = float(precio)
        self.stock = int(stock)
        self.activo = activo
        # Campo auxiliar para presentación o consultas con JOIN
        self.categoria_nombre = categoria_nombre

    @property
    def esta_activo(self) -> bool:
        return bool(self.activo)

    @property
    def tiene_stock_bajo(self, umbral: int = 5) -> bool:
        return self.stock <= umbral

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "codigo": self.codigo,
            "nombre": self.nombre,
            "categoria_id": self.categoria_id,
            "categoria_nombre": self.categoria_nombre,
            "precio": self.precio,
            "stock": self.stock,
            "activo": self.activo
        }

    def __repr__(self) -> str:
        return f"<Producto id={self.id} codigo='{self.codigo}' nombre='{self.nombre}' stock={self.stock}>"
