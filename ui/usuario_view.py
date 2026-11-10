import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from models.usuario import Usuario
from services.usuario_service import UsuarioService

class UsuarioView(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, usuario_service: UsuarioService, usuario_actual_getter: Callable[[], Usuario]):
        super().__init__(parent, padding=15)
        self.usuario_service = usuario_service
        self.usuario_actual_getter = usuario_actual_getter
        self._construir_ui()
        self.cargar_datos()

    def _construir_ui(self) -> None:
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(header_frame, text="Gestión de Cuentas de Personal (Solo Administrador)", style="Titulo.TLabel").pack(side="left")

        # Tabla de usuarios
        tabla_frame = ttk.LabelFrame(self, text=" Cuentas del Sistema ", padding=10)
        tabla_frame.pack(fill="both", expand=True)

        columnas = ("id", "username", "rol", "estado")
        self.tree = ttk.Treeview(tabla_frame, columns=columnas, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("username", text="Nombre de Usuario")
        self.tree.heading("rol", text="Rol Asignado")
        self.tree.heading("estado", text="Estado de Cuenta")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("username", width=220, anchor="w")
        self.tree.column("rol", width=180, anchor="center")
        self.tree.column("estado", width=140, anchor="center")

        sc_y = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sc_y.set)

        self.tree.pack(side="left", fill="both", expand=True)
        sc_y.pack(side="right", fill="y")

        # Botones de acción
        btn_frame = ttk.Frame(self, padding=(0, 10))
        btn_frame.pack(fill="x")

        ttk.Button(btn_frame, text="➕ Nuevo Usuario", style="Primary.TButton", command=self._abrir_modal_crear).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="✏️ Editar Rol / Datos", command=self._abrir_modal_editar).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="🔑 Cambiar Contraseña", command=self._abrir_modal_password).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="🔄 Activar / Desactivar", command=self._alternar_estado).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Actualizar Lista", command=self.cargar_datos).pack(side="right")

    def cargar_datos(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        usuarios = self.usuario_service.listar_usuarios()
        for u in usuarios:
            estado_txt = "Activo" if u.esta_activo else "Inactivo"
            rol_txt = "Administrador" if u.es_administrador else "Operador"
            self.tree.insert("", "end", values=(u.id, u.username, rol_txt, estado_txt))

    def _obtener_usuario_seleccionado(self) -> Optional[int]:
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un usuario de la lista.", parent=self)
            return None
        valores = self.tree.item(seleccion[0], "values")
        return int(valores[0])

    def _abrir_modal_crear(self) -> None:
        modal = tk.Toplevel(self)
        modal.title("Nuevo Usuario del Sistema")
        modal.geometry("380x320")
        modal.resizable(False, False)
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        frame = ttk.Frame(modal, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Nombre de Usuario:").pack(anchor="w", pady=(0, 2))
        txt_user = ttk.Entry(frame)
        txt_user.pack(fill="x", pady=(0, 10))
        txt_user.focus_set()

        ttk.Label(frame, text="Contraseña inicial:").pack(anchor="w", pady=(0, 2))
        txt_pass = ttk.Entry(frame, show="•")
        txt_pass.pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="Rol del Usuario:").pack(anchor="w", pady=(0, 2))
        cbo_rol = ttk.Combobox(frame, values=["operador", "administrador"], state="readonly")
        cbo_rol.current(0)
        cbo_rol.pack(fill="x", pady=(0, 15))

        var_act = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Usuario Activo", variable=var_act).pack(anchor="w", pady=(0, 20))

        btn_box = ttk.Frame(frame)
        btn_box.pack(fill="x")

        def guardar():
            username = txt_user.get().strip()
            password = txt_pass.get().strip()
            rol = cbo_rol.get()
            activo = 1 if var_act.get() else 0

            try:
                self.usuario_service.crear_usuario(username, password, rol, activo)
                messagebox.showinfo("Éxito", f"Usuario '{username}' creado exitosamente.", parent=modal)
                modal.destroy()
                self.cargar_datos()
            except ValueError as err:
                messagebox.showerror("Validación", str(err), parent=modal)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo crear el usuario: {e}", parent=modal)

        ttk.Button(btn_box, text="Crear Usuario", style="Primary.TButton", command=guardar).pack(side="left", padx=(0, 8))
        ttk.Button(btn_box, text="Cancelar", command=modal.destroy).pack(side="left")

    def _abrir_modal_editar(self) -> None:
        user_id = self._obtener_usuario_seleccionado()
        if not user_id:
            return

        usuario = self.usuario_service.usuario_repo.obtener_por_id(user_id)
        if not usuario:
            return

        modal = tk.Toplevel(self)
        modal.title(f"Editar Usuario #{usuario.id}")
        modal.geometry("380x280")
        modal.resizable(False, False)
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        frame = ttk.Frame(modal, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Nombre de Usuario:").pack(anchor="w", pady=(0, 2))
        txt_user = ttk.Entry(frame)
        txt_user.insert(0, usuario.username)
        txt_user.pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="Rol Asignado:").pack(anchor="w", pady=(0, 2))
        cbo_rol = ttk.Combobox(frame, values=["operador", "administrador"], state="readonly")
        cbo_rol.set(usuario.rol)
        cbo_rol.pack(fill="x", pady=(0, 15))

        var_act = tk.BooleanVar(value=usuario.esta_activo)
        ttk.Checkbutton(frame, text="Usuario Activo", variable=var_act).pack(anchor="w", pady=(0, 20))

        btn_box = ttk.Frame(frame)
        btn_box.pack(fill="x")

        def guardar():
            username = txt_user.get().strip()
            rol = cbo_rol.get()
            activo = 1 if var_act.get() else 0

            # Proteger contra auto-desactivación del usuario logueado
            usr_logueado = self.usuario_actual_getter()
            if usr_logueado and usr_logueado.id == usuario.id and activo == 0:
                messagebox.showerror("Operación Denegada", "No puede desactivar su propio usuario mientras tiene la sesión activa.", parent=modal)
                return

            try:
                self.usuario_service.actualizar_usuario(usuario.id, username, rol, activo)
                messagebox.showinfo("Éxito", "Usuario actualizado correctamente.", parent=modal)
                modal.destroy()
                self.cargar_datos()
            except ValueError as err:
                messagebox.showerror("Validación", str(err), parent=modal)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {e}", parent=modal)

        ttk.Button(btn_box, text="Guardar Cambios", style="Primary.TButton", command=guardar).pack(side="left", padx=(0, 8))
        ttk.Button(btn_box, text="Cancelar", command=modal.destroy).pack(side="left")

    def _abrir_modal_password(self) -> None:
        user_id = self._obtener_usuario_seleccionado()
        if not user_id:
            return

        usuario = self.usuario_service.usuario_repo.obtener_por_id(user_id)
        if not usuario:
            return

        modal = tk.Toplevel(self)
        modal.title(f"Cambiar Contraseña - {usuario.username}")
        modal.geometry("360x220")
        modal.resizable(False, False)
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        frame = ttk.Frame(modal, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=f"Nueva contraseña para '{usuario.username}':").pack(anchor="w", pady=(0, 2))
        txt_pass = ttk.Entry(frame, show="•")
        txt_pass.pack(fill="x", pady=(0, 10))
        txt_pass.focus_set()

        ttk.Label(frame, text="Confirmar nueva contraseña:").pack(anchor="w", pady=(0, 2))
        txt_conf = ttk.Entry(frame, show="•")
        txt_conf.pack(fill="x", pady=(0, 15))

        btn_box = ttk.Frame(frame)
        btn_box.pack(fill="x")

        def guardar():
            p1 = txt_pass.get().strip()
            p2 = txt_conf.get().strip()
            if p1 != p2:
                messagebox.showerror("Error", "Las contraseñas no coinciden.", parent=modal)
                return
            try:
                self.usuario_service.cambiar_password(usuario.id, p1)
                messagebox.showinfo("Éxito", "Contraseña cambiada exitosamente.", parent=modal)
                modal.destroy()
            except ValueError as err:
                messagebox.showerror("Validación", str(err), parent=modal)

        ttk.Button(btn_box, text="Actualizar Contraseña", style="Primary.TButton", command=guardar).pack(side="left", padx=(0, 8))
        ttk.Button(btn_box, text="Cancelar", command=modal.destroy).pack(side="left")

    def _alternar_estado(self) -> None:
        user_id = self._obtener_usuario_seleccionado()
        if not user_id:
            return

        usuario = self.usuario_service.usuario_repo.obtener_por_id(user_id)
        if not usuario:
            return

        usr_logueado = self.usuario_actual_getter()
        if usr_logueado and usr_logueado.id == usuario.id:
            messagebox.showerror("Operación Denegada", "No puede desactivar su propia cuenta mientras esté conectado.", parent=self)
            return

        nuevo_estado = 0 if usuario.esta_activo else 1
        accion = "desactivar" if usuario.esta_activo else "activar"

        if not messagebox.askyesno("Confirmación", f"¿Está seguro de que desea {accion} la cuenta de '{usuario.username}'?", parent=self):
            return

        self.usuario_service.alternar_estado(user_id, nuevo_estado)
        self.cargar_datos()
        messagebox.showinfo("Éxito", f"Usuario {accion}do correctamente.", parent=self)
