from typing import List
from models.detalle_venta import DetalleVenta

class Venta:
    """Representa el encabezado de una venta realizada."""
    def __init__(self, id: int = None, fecha: str = "", usuario_id: int = None,
                 total: float = 0.0, usuario_nombre: str = "", detalles: List[DetalleVenta] = None):
        self.id = id
        self.fecha = fecha
        self.usuario_id = usuario_id
        self.total = float(total)
        # Campo auxiliar para JOIN
        self.usuario_nombre = usuario_nombre
        self.detalles: List[DetalleVenta] = detalles if detalles is not None else []

    def calcular_total(self) -> float:
        self.total = sum(d.subtotal for d in self.detalles)
        return self.total

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "fecha": self.fecha,
            "usuario_id": self.usuario_id,
            "usuario_nombre": self.usuario_nombre,
            "total": self.total,
            "detalles": [d.to_dict() for d in self.detalles]
        }

    def __repr__(self) -> str:
        return f"<Venta id={self.id} fecha='{self.fecha}' total={self.total} items={len(self.detalles)}>"
