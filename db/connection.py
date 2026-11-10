import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "tienda.db")

def obtener_conexion(db_path: str = None) -> sqlite3.Connection:
    """
    Retorna una conexión a SQLite con soporte de Foreign Keys activo
    y filas accesibles por nombre de columna.
    """
    ruta = db_path or DEFAULT_DB_PATH
    conexion = sqlite3.connect(ruta)
    conexion.execute("PRAGMA foreign_keys = ON;")
    conexion.row_factory = sqlite3.Row
    return conexion
