import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable
from models.usuario import Usuario
from services.auth_service import AuthService
from ui.styles import aplicar_estilos, COLOR_PRIMARIO, COLOR_FONDO

class LoginWindow:
    def __init__(self, root: tk.Tk, auth_service: AuthService, on_login_success: Callable[[Usuario], None]):
        self.root = root
        self.auth_service = auth_service
        self.on_login_success = on_login_success

        self.root.title("Inicio de Sesión - Sistema Punto de Venta")
        self.root.geometry("440x480")
        self.root.resizable(False, False)
        self.centrar_ventana(440, 480)

        aplicar_estilos(self.root)
        self._construir_ui()

    def centrar_ventana(self, ancho: int, alto: int) -> None:
        self.root.update_idletasks()
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = (pantalla_ancho - ancho) // 2
        y = (pantalla_alto - alto) // 2
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _construir_ui(self) -> None:
        contenedor = ttk.Frame(self.root, padding=30)
        contenedor.pack(fill="both", expand=True)

        # Encabezado visual
        lbl_icono = ttk.Label(contenedor, text="🏪", font=("Segoe UI", 36))
        lbl_icono.pack(pady=(5, 5))

        lbl_titulo = ttk.Label(contenedor, text="Mini Punto de Venta", font=("Segoe UI", 16, "bold"), foreground=COLOR_PRIMARIO)
        lbl_titulo.pack()

        lbl_subtitulo = ttk.Label(contenedor, text="Gestión de Inventario y Ventas", style="Muted.TLabel")
        lbl_subtitulo.pack(pady=(2, 20))

        # Tarjeta de formulario
        frame_form = ttk.LabelFrame(contenedor, text=" Ingrese sus credenciales ", padding=15)
        frame_form.pack(fill="x", pady=5)

        ttk.Label(frame_form, text="Usuario:").pack(anchor="w", pady=(2, 4))
        self.txt_username = ttk.Entry(frame_form, font=("Segoe UI", 10))
        self.txt_username.pack(fill="x", pady=(0, 10))
        self.txt_username.focus_set()

        ttk.Label(frame_form, text="Contraseña:").pack(anchor="w", pady=(2, 4))
        self.txt_password = ttk.Entry(frame_form, show="•", font=("Segoe UI", 10))
        self.txt_password.pack(fill="x", pady=(0, 15))

        # Acciones
        btn_login = ttk.Button(frame_form, text="Iniciar Sesión", style="Primary.TButton", command=self._intentar_login)
        btn_login.pack(fill="x", pady=(0, 5))

        # Enlazar la tecla Enter al login
        self.root.bind("<Return>", lambda event: self._intentar_login())

        # Tarjeta informativa para el docente / evaluador
        frame_info = ttk.Frame(contenedor, padding=(5, 10))
        frame_info.pack(fill="x", pady=(10, 0))

        lbl_guia = ttk.Label(frame_info, text="Usuarios de prueba (Evaluación):", font=("Segoe UI", 8, "bold"), foreground="#495057")
        lbl_guia.pack(anchor="w")

        lbl_datos = ttk.Label(frame_info,
                              text="• Administrador: admin  /  admin123\n• Operador: operador  /  operador123",
                              font=("Segoe UI", 8),
                              foreground="#6c757d")
        lbl_datos.pack(anchor="w", pady=(2, 0))

    def _intentar_login(self) -> None:
        username = self.txt_username.get().strip()
        password = self.txt_password.get().strip()

        try:
            usuario = self.auth_service.iniciar_sesion(username, password)
            self.root.unbind("<Return>")
            self.on_login_success(usuario)
        except ValueError as err:
            messagebox.showerror("Error de Autenticación", str(err), parent=self.root)
            self.txt_password.delete(0, tk.END)
            self.txt_password.focus_set()
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error al intentar iniciar sesión: {e}", parent=self.root)
