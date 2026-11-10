from typing import List, Dict, Any, Optional
from repositories.venta_repository import VentaRepository
from repositories.producto_repository import ProductoRepository

class VentaService:
    def __init__(self, venta_repo: VentaRepository = None, producto_repo: ProductoRepository = None):
        self.venta_repo = venta_repo or VentaRepository()
        self.producto_repo = producto_repo or ProductoRepository()

    def registrar_venta(self, usuario_id: int, items_carrito: List[Dict[str, Any]]) -> int:
        """
        Regla de negocio principal de venta:
        1. Debe tener al menos un producto en el carrito.
        2. Cada producto debe estar activo.
        3. Cantidad > 0 para cada ítem.
        4. Stock suficiente para cada ítem (no vender si cantidad > stock).
        5. Inserción atómica del folio, detalle y descuento de existencias.
        """
        if not usuario_id:
            raise ValueError("No se ha identificado el usuario vendedor.")

        if not items_carrito or len(items_carrito) == 0:
            raise ValueError("El carrito de venta está vacío. Agregue al menos un producto.")

        # Validaciones de cada producto previo a la transacción
        for item in items_carrito:
            prod_id = item.get("producto_id")
            cantidad = item.get("cantidad", 0)

            if not prod_id:
                raise ValueError("Elemento del carrito sin identificador de producto.")

            if cantidad <= 0:
                raise ValueError("La cantidad a vender debe ser mayor que 0.")

            producto = self.producto_repo.obtener_por_id(prod_id)
            if not producto:
                raise ValueError(f"El producto con ID {prod_id} no fue encontrado.")

            if not producto.esta_activo:
                raise ValueError(f"El producto '{producto.nombre}' está inactivo y no puede venderse.")

            if cantidad > producto.stock:
                raise ValueError(
                    f"Existencias insuficientes para '{producto.nombre}'. "
                    f"Stock disponible: {producto.stock}, Cantidad solicitada: {cantidad}."
                )

        # Ejecución atómica en el repositorio
        return self.venta_repo.registrar_venta_transaccional(usuario_id, items_carrito)

    def listar_ventas(self, busqueda: str = None) -> List[Dict[str, Any]]:
        return self.venta_repo.listar_ventas(busqueda=busqueda)

    def obtener_detalles_venta(self, venta_id: int) -> List[Dict[str, Any]]:
        return self.venta_repo.obtener_detalles_por_venta(venta_id)

    def listar_detalles_con_join(self, busqueda: str = None) -> List[Dict[str, Any]]:
        return self.venta_repo.listar_detalles_con_join(busqueda=busqueda)
