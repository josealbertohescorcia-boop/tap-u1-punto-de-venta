import csv
from typing import List, Dict, Any
from repositories.venta_repository import VentaRepository

class ReporteService:
    def __init__(self, venta_repo: VentaRepository = None):
        self.venta_repo = venta_repo or VentaRepository()

    def obtener_stock_bajo(self, umbral: int = 5) -> List[Dict[str, Any]]:
        return self.venta_repo.obtener_reporte_stock_bajo(umbral=umbral)

    def obtener_mas_vendidos(self, limite: int = 15) -> List[Dict[str, Any]]:
        return self.venta_repo.obtener_reporte_mas_vendidos(limite=limite)

    def exportar_csv(self, datos: List[Dict[str, Any]], campos: List[str], nombres_columnas: List[str], ruta_archivo: str) -> None:
        """
        Exporta una lista de diccionarios a un archivo CSV con codificación UTF-8 con BOM
        para que abra correctamente en Microsoft Excel.
        """
        if not datos:
            raise ValueError("No hay datos para exportar a CSV.")

        with open(ruta_archivo, mode="w", newline="", encoding="utf-8-sig") as f:
            escritor = csv.writer(f)
            # Escribir encabezados legibles
            escritor.writerow(nombres_columnas)

            # Escribir filas
            for fila in datos:
                fila_csv = [fila.get(campo, "") for campo in campos]
                escritor.writerow(fila_csv)
