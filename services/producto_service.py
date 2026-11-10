import sqlite3
from typing import List, Optional
from models.producto import Producto
from repositories.producto_repository import ProductoRepository
from repositories.categoria_repository import CategoriaRepository

class ProductoService:
    def __init__(self, producto_repo: ProductoRepository = None, categoria_repo: CategoriaRepository = None):
        self.producto_repo = producto_repo or ProductoRepository()
        self.categoria_repo = categoria_repo or CategoriaRepository()

    def listar_productos(self, solo_activos: bool = False, busqueda: str = None, categoria_id: int = None) -> List[Producto]:
        return self.producto_repo.listar_todos(solo_activos=solo_activos, busqueda=busqueda, categoria_id=categoria_id)

    def obtener_producto(self, prod_id: int) -> Optional[Producto]:
        return self.producto_repo.obtener_por_id(prod_id)

    def crear_producto(self, codigo: str, nombre: str, categoria_id: int, precio: float, stock: int, activo: int = 1) -> int:
        codigo = (codigo or "").strip().upper()
        nombre = (nombre or "").strip()

        if not codigo:
            raise ValueError("El código del producto es obligatorio.")
        if not nombre:
            raise ValueError("El nombre del producto es obligatorio.")
        if not categoria_id:
            raise ValueError("Debe seleccionar una categoría válida.")

        try:
            precio = float(precio)
        except (ValueError, TypeError):
            raise ValueError("El precio debe ser un número válido.")

        if precio <= 0:
            raise ValueError("El precio debe ser mayor que 0.")

        try:
            stock = int(stock)
        except (ValueError, TypeError):
            raise ValueError("El stock inicial debe ser un número entero.")

        if stock < 0:
            raise ValueError("El stock no puede ser negativo.")

        # Validar categoría
        cat = self.categoria_repo.obtener_por_id(categoria_id)
        if not cat:
            raise ValueError("La categoría seleccionada no existe.")
        if not cat.esta_activa:
            raise ValueError("No se pueden agregar productos a una categoría inactiva.")

        # Validar código único
        existente = self.producto_repo.obtener_por_codigo(codigo)
        if existente:
            raise ValueError(f"Ya existe un producto registrado con el código '{codigo}'.")

        producto = Producto(
            codigo=codigo,
            nombre=nombre,
            categoria_id=categoria_id,
            precio=precio,
            stock=stock,
            activo=int(activo)
        )
        try:
            return self.producto_repo.crear(producto)
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Error de integridad al guardar producto: {e}")

    def actualizar_producto(self, prod_id: int, codigo: str, nombre: str, categoria_id: int,
                            precio: float, stock: int, activo: int) -> bool:
        codigo = (codigo or "").strip().upper()
        nombre = (nombre or "").strip()

        if not codigo:
            raise ValueError("El código del producto es obligatorio.")
        if not nombre:
            raise ValueError("El nombre del producto es obligatorio.")
        if not categoria_id:
            raise ValueError("Debe seleccionar una categoría válida.")

        try:
            precio = float(precio)
        except (ValueError, TypeError):
            raise ValueError("El precio debe ser un número válido.")

        if precio <= 0:
            raise ValueError("El precio debe ser mayor que 0.")

        try:
            stock = int(stock)
        except (ValueError, TypeError):
            raise ValueError("El stock debe ser un número entero.")

        if stock < 0:
            raise ValueError("El stock no puede ser negativo.")

        existente = self.producto_repo.obtener_por_codigo(codigo)
        if existente and existente.id != prod_id:
            raise ValueError(f"Ya existe otro producto registrado con el código '{codigo}'.")

        cat = self.categoria_repo.obtener_por_id(categoria_id)
        if not cat:
            raise ValueError("La categoría seleccionada no existe.")

        producto = Producto(
            id=prod_id,
            codigo=codigo,
            nombre=nombre,
            categoria_id=categoria_id,
            precio=precio,
            stock=stock,
            activo=int(activo)
        )
        return self.producto_repo.actualizar(producto)

    def alternar_estado(self, prod_id: int, nuevo_estado: int) -> bool:
        return self.producto_repo.cambiar_estado(prod_id, int(nuevo_estado))

    def eliminar_producto(self, prod_id: int) -> bool:
        """
        Regla de negocio RF-10:
        'No eliminar un producto con ventas; desactivar.'
        """
        ventas_asociadas = self.producto_repo.contar_ventas_asociadas(prod_id)
        if ventas_asociadas > 0:
            raise ValueError(
                f"Integridad referencial: El producto tiene {ventas_asociadas} venta(s) registrada(s) "
                "en el historial. No se puede eliminar para no romper los folios de venta. "
                "Por favor, desactívelo en su lugar."
            )

        try:
            return self.producto_repo.eliminar(prod_id)
        except sqlite3.IntegrityError:
            raise ValueError("No se puede eliminar el producto debido a restricciones de integridad en base de datos.")
