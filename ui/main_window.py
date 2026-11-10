import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable
from datetime import datetime

from models.usuario import Usuario
from services.auth_service import AuthService
from services.usuario_service import UsuarioService
from services.categoria_service import CategoriaService
from services.producto_service import ProductoService
from services.venta_service import VentaService
from services.reporte_service import ReporteService

from ui.styles import aplicar_estilos, COLOR_PRIMARIO, COLOR_TARJETA, COLOR_FONDO
from ui.categoria_view import CategoriaView
from ui.producto_view import ProductoView
from ui.venta_view import VentaView
from ui.venta_historial_view import VentaHistorialView
from ui.reporte_view import ReporteView
from ui.usuario_view import UsuarioView

class MainWindow:
    def __init__(self, root: tk.Tk, usuario: Usuario, auth_service: AuthService, on_logout: Callable[[], None]):
        self.root = root
        self.usuario = usuario
        self.auth_service = auth_service
        self.on_logout = on_logout

        # Inicialización de servicios
        self.usuario_service = UsuarioService()
        self.categoria_service = CategoriaService()
        self.producto_service = ProductoService()
        self.venta_service = VentaService()
        self.reporte_service = ReporteService()

        self.root.title(f"Sistema Punto de Venta - [{usuario.username.upper()} - {usuario.rol.upper()}]")
        self.root.geometry("1120x720")
        self.root.minsize(980, 640)
        self.centrar_ventana(1120, 720)

        aplicar_estilos(self.root)
        self._construir_menu()
        self._construir_ui()

    def centrar_ventana(self, ancho: int, alto: int) -> None:
        self.root.update_idletasks()
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = (pantalla_ancho - ancho) // 2
        y = (pantalla_alto - alto) // 2
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _construir_menu(self) -> None:
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menú Archivo
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Cerrar Sesión", command=self._confirmar_cerrar_sesion)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.root.destroy)

        # Menú Módulos
        menu_modulos = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Módulos", menu=menu_modulos)
        menu_modulos.add_command(label="Punto de Venta", command=lambda: self.notebook.select(self.tab_venta))
        menu_modulos.add_command(label="Productos", command=lambda: self.notebook.select(self.tab_productos))
        menu_modulos.add_command(label="Categorías", command=lambda: self.notebook.select(self.tab_categorias))
        menu_modulos.add_command(label="Historial de Ventas (JOIN)", command=lambda: self.notebook.select(self.tab_historial))
        menu_modulos.add_command(label="Reportes (Stock Bajo)", command=lambda: self.notebook.select(self.tab_reportes))

        # Menú Administración (Solo para rol administrador)
        if self.usuario.es_administrador:
            menu_admin = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Administración", menu=menu_admin)
            menu_admin.add_command(label="Gestión de Personal / Usuarios", command=lambda: self.notebook.select(self.tab_usuarios))

        # Menú Ayuda
        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)
        menu_ayuda.add_command(label="Acerca del Proyecto...", command=self._mostrar_acerca_de)

    def _construir_ui(self) -> None:
        # Barra superior con información del usuario conectado
        top_bar = tk.Frame(self.root, bg=COLOR_PRIMARIO, height=50)
        top_bar.pack(fill="x", side="top")

        lbl_app = tk.Label(
            top_bar,
            text="🏪 Mini Punto de Venta e Inventario",
            font=("Segoe UI", 12, "bold"),
            bg=COLOR_PRIMARIO,
            fg="#ffffff"
        )
        lbl_app.pack(side="left", padx=15, pady=10)

        # Info de usuario y botón de cerrar sesión
        right_info = tk.Frame(top_bar, bg=COLOR_PRIMARIO)
        right_info.pack(side="right", padx=15, pady=10)

        rol_badge = "👑 ADMINISTRADOR" if self.usuario.es_administrador else "👤 OPERADOR"
        lbl_user = tk.Label(
            right_info,
            text=f"Conectado como: {self.usuario.username} ({rol_badge})  |  ",
            font=("Segoe UI", 9),
            bg=COLOR_PRIMARIO,
            fg="#e0e0e0"
        )
        lbl_user.pack(side="left")

        btn_logout = ttk.Button(right_info, text="Cerrar Sesión", command=self._confirmar_cerrar_sesion)
        btn_logout.pack(side="left")

        # Contenedor con pestañas (Notebook)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(8, 0))

        # 1. Pestaña Venta (Movimiento de Negocio)
        self.tab_venta = VentaView(
            self.notebook,
            venta_service=self.venta_service,
            producto_service=self.producto_service,
            usuario_actual_getter=lambda: self.usuario,
            on_venta_realizada=self._refrescar_vistas_tras_venta
        )
        self.notebook.add(self.tab_venta, text="  🛒 Registrar Venta  ")

        # 2. Pestaña Productos (Catálogo A)
        self.tab_productos = ProductoView(
            self.notebook,
            producto_service=self.producto_service,
            categoria_service=self.categoria_service
        )
        self.notebook.add(self.tab_productos, text="  📦 Catálogo Productos  ")

        # 3. Pestaña Categorías (Catálogo B)
        self.tab_categorias = CategoriaView(
            self.notebook,
            categoria_service=self.categoria_service
        )
        self.notebook.add(self.tab_categorias, text="  🏷️ Categorías  ")

        # 4. Pestaña Historial de Movimientos con JOIN
        self.tab_historial = VentaHistorialView(
            self.notebook,
            venta_service=self.venta_service
        )
        self.notebook.add(self.tab_historial, text="  📜 Historial (JOIN)  ")

        # 5. Pestaña Reportes (Stock bajo + CSV)
        self.tab_reportes = ReporteView(
            self.notebook,
            reporte_service=self.reporte_service
        )
        self.notebook.add(self.tab_reportes, text="  📊 Reportes y Alertas  ")

        # 6. Pestaña Usuarios (RF-2: Solo administrador tiene acceso)
        if self.usuario.es_administrador:
            self.tab_usuarios = UsuarioView(
                self.notebook,
                usuario_service=self.usuario_service,
                usuario_actual_getter=lambda: self.usuario
            )
            self.notebook.add(self.tab_usuarios, text="  👥 Personal / Usuarios  ")

        # Barra de estado inferior
        status_bar = ttk.Frame(self.root, padding=(10, 4))
        status_bar.pack(fill="x", side="bottom")

        lbl_status = ttk.Label(
            status_bar,
            text=f"Base de Datos: SQLite3 Conectada | FK Activas | Usuario: {self.usuario.username} ({self.usuario.rol})",
            style="Muted.TLabel"
        )
        lbl_status.pack(side="left")

        fecha_str = datetime.now().strftime("%Y-%m-%d")
        lbl_fecha = ttk.Label(status_bar, text=f"Fecha: {fecha_str}", style="Muted.TLabel")
        lbl_fecha.pack(side="right")

    def _refrescar_vistas_tras_venta(self) -> None:
        """Se ejecuta cuando se realiza una venta para mantener sincronizadas todas las tablas."""
        self.tab_productos.cargar_datos()
        self.tab_historial.cargar_datos()
        self.tab_reportes.cargar_datos()

    def _confirmar_cerrar_sesion(self) -> None:
        if messagebox.askyesno("Cerrar Sesión", "¿Está seguro de que desea cerrar la sesión actual?", parent=self.root):
            self.auth_service.cerrar_sesion()
            self.on_logout()

    def _mostrar_acerca_de(self) -> None:
        info = (
            "TÓPICOS AVANZADOS DE PROGRAMACIÓN\n"
            "Unidad 1 · Proyecto Final: Aplicación de Escritorio con Tkinter\n"
            "Opción 2: Inventario / Mini Punto de Venta\n\n"
            "Arquitectura en capas:\n"
            "• UI (Tkinter / ttk modular)\n"
            "• Services (Reglas de negocio y transacciones)\n"
            "• Repositories (SQL relacional y mapeo)\n"
            "• Models (Clases POO puras)\n"
            "• DB (SQLite3 con PRAGMA foreign_keys = ON)\n\n"
            "Extras implementados:\n"
            "• Exportación de reportes a archivo CSV (con formato UTF-8)\n"
            "• Interfaz ttk moderna y control de permisos por roles"
        )
        messagebox.showinfo("Acerca del Proyecto", info, parent=self.root)
