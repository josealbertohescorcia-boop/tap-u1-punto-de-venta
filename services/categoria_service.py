import sqlite3
from typing import List, Optional
from models.categoria import Categoria
from repositories.categoria_repository import CategoriaRepository

class CategoriaService:
    def __init__(self, categoria_repo: CategoriaRepository = None):
        self.categoria_repo = categoria_repo or CategoriaRepository()

    def listar_categorias(self, solo_activas: bool = False, busqueda: str = None) -> List[Categoria]:
        return self.categoria_repo.listar_todas(solo_activas=solo_activas, busqueda=busqueda)

    def obtener_categoria(self, cat_id: int) -> Optional[Categoria]:
        return self.categoria_repo.obtener_por_id(cat_id)

    def crear_categoria(self, nombre: str, activo: int = 1) -> int:
        nombre = (nombre or "").strip()
        if not nombre:
            raise ValueError("El nombre de la categoría es obligatorio.")
        if len(nombre) < 3:
            raise ValueError("El nombre de la categoría debe tener al menos 3 caracteres.")

        existente = self.categoria_repo.obtener_por_nombre(nombre)
        if existente:
            raise ValueError(f"Ya existe una categoría registrada con el nombre '{nombre}'.")

        categoria = Categoria(nombre=nombre, activo=int(activo))
        try:
            return self.categoria_repo.crear(categoria)
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Error al registrar la categoría: {e}")

    def actualizar_categoria(self, cat_id: int, nombre: str, activo: int) -> bool:
        nombre = (nombre or "").strip()
        if not nombre:
            raise ValueError("El nombre de la categoría es obligatorio.")

        existente = self.categoria_repo.obtener_por_nombre(nombre)
        if existente and existente.id != cat_id:
            raise ValueError(f"Ya existe otra categoría registrada con el nombre '{nombre}'.")

        # Si se intenta desactivar, verificar si tiene productos activos
        if int(activo) == 0:
            activos = self.categoria_repo.contar_productos_activos_asociados(cat_id)
            if activos > 0:
                raise ValueError(f"No se puede desactivar la categoría porque tiene {activos} producto(s) activo(s) asociados. Desactive primero los productos.")

        categoria = Categoria(id=cat_id, nombre=nombre, activo=int(activo))
        return self.categoria_repo.actualizar(categoria)

    def alternar_estado(self, cat_id: int, nuevo_estado: int) -> bool:
        if int(nuevo_estado) == 0:
            activos = self.categoria_repo.contar_productos_activos_asociados(cat_id)
            if activos > 0:
                raise ValueError(f"No se puede desactivar la categoría porque contiene {activos} producto(s) activo(s).")
        return self.categoria_repo.cambiar_estado(cat_id, int(nuevo_estado))

    def eliminar_categoria(self, cat_id: int) -> bool:
        """
        Regla de integridad: No eliminar un registro padre si tiene hijos asociados;
        usar desactivar o mostrar error.
        """
        total_productos = self.categoria_repo.contar_productos_asociados(cat_id)
        if total_productos > 0:
            raise ValueError(
                f"Integridad referencial: No es posible eliminar esta categoría porque tiene {total_productos} "
                "producto(s) asociado(s). En su lugar, desactívela."
            )
        try:
            return self.categoria_repo.eliminar(cat_id)
        except sqlite3.IntegrityError:
            raise ValueError("No se puede eliminar la categoría debido a restricciones de integridad de base de datos.")
