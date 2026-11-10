import os
import sys
import tkinter as tk

# Asegurar que la raíz del proyecto esté en sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import inicializar_base_datos
from services.auth_service import AuthService
from models.usuario import Usuario
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

class AppController:
    """Controlador principal del ciclo de vida de la aplicación."""
    def __init__(self, root: tk.Tk):
        self.root = root
        self.auth_service = AuthService()
        self.usuario_actual = None
        self.mostrar_login()

    def limpiar_pantalla(self) -> None:
        """Destruye widgets y limpia el menú de la ventana antes de cambiar de vista."""
        self.root.config(menu="")
        for widget in self.root.winfo_children():
            widget.destroy()

    def mostrar_login(self) -> None:
        """Presenta la pantalla de login."""
        self.limpiar_pantalla()
        self.root.unbind("<Return>")
        self.root.title("Inicio de Sesión - Mini Punto de Venta")
        LoginWindow(
            root=self.root,
            auth_service=self.auth_service,
            on_login_success=self.on_login_exitoso
        )

    def on_login_exitoso(self, usuario: Usuario) -> None:
        """Transición al panel principal una vez que el usuario se autenticó."""
        self.usuario_actual = usuario
        self.limpiar_pantalla()
        MainWindow(
            root=self.root,
            usuario=self.usuario_actual,
            auth_service=self.auth_service,
            on_logout=self.mostrar_login
        )

def main():
    # 1. Requisito RF-1: Inicializar base de datos SQLite y tablas si no existen
    inicializar_base_datos()

    # 2. Inicializar ventana principal de Tkinter
    root = tk.Tk()
    app = AppController(root)
    root.mainloop()

if __name__ == "__main__":
    main()
