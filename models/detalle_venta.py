class DetalleVenta:
    """Representa una línea o ítem de una venta."""
    def __init__(self, id: int = None, venta_id: int = None, producto_id: int = None,
                 cantidad: int = 1, precio_unitario: float = 0.0, subtotal: float = 0.0,
                 producto_codigo: str = "", producto_nombre: str = ""):
        self.id = id
        self.venta_id = venta_id
        self.producto_id = producto_id
        self.cantidad = int(cantidad)
        self.precio_unitario = float(precio_unitario)
        self.subtotal = float(subtotal if subtotal > 0 else self.cantidad * self.precio_unitario)
        # Campos auxiliares provenientes del JOIN
        self.producto_codigo = producto_codigo
        self.producto_nombre = producto_nombre

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "venta_id": self.venta_id,
            "producto_id": self.producto_id,
            "producto_codigo": self.producto_codigo,
            "producto_nombre": self.producto_nombre,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "subtotal": self.subtotal
        }

    def __repr__(self) -> str:
        return f"<DetalleVenta producto_id={self.producto_id} cant={self.cantidad} subt={self.subtotal}>"
