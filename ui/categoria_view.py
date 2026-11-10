import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from models.categoria import Categoria
from services.categoria_service import CategoriaService

class CategoriaView(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, categoria_service: CategoriaService):
        super().__init__(parent, padding=15)
        self.categoria_service = categoria_service
        self._construir_ui()
        self.cargar_datos()

    def _construir_ui(self) -> None:
        # Barra superior con título y buscador
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(header_frame, text="Catálogo de Categorías", style="Titulo.TLabel").pack(side="left")

        # Filtro de búsqueda
        filtro_frame = ttk.LabelFrame(self, text=" Búsqueda y Filtros ", padding=10)
        filtro_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(filtro_frame, text="Buscar:").pack(side="left", padx=(0, 5))
        self.txt_buscar = ttk.Entry(filtro_frame, width=28)
        self.txt_buscar.pack(side="left", padx=(0, 15))
        self.txt_buscar.bind("<KeyRelease>", lambda event: self.cargar_datos())

        self.var_solo_activas = tk.BooleanVar(value=False)
        chk_activas = ttk.Checkbutton(filtro_frame, text="Mostrar solo activas", variable=self.var_solo_activas, command=self.cargar_datos)
        chk_activas.pack(side="left", padx=(0, 15))

        btn_limpiar = ttk.Button(filtro_frame, text="Limpiar Filtro", command=self._limpiar_filtro)
        btn_limpiar.pack(side="left")

        # Tabla (Treeview)
        tabla_frame = ttk.Frame(self)
        tabla_frame.pack(fill="both", expand=True)

        columnas = ("id", "nombre", "estado")
        self.tree = ttk.Treeview(tabla_frame, columns=columnas, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre de Categoría")
        self.tree.heading("estado", text="Estado")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("nombre", width=350, anchor="w")
        self.tree.column("estado", width=120, anchor="center")

        scroll_y = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Barra de botones de acción
        btn_frame = ttk.Frame(self, padding=(0, 10))
        btn_frame.pack(fill="x")

        ttk.Button(btn_frame, text="➕ Nueva Categoría", style="Primary.TButton", command=self._abrir_modal_crear).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="✏️ Editar", command=self._abrir_modal_editar).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="🔄 Activar / Desactivar", command=self._alternar_estado).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="🗑️ Eliminar", style="Danger.TButton", command=self._eliminar_categoria).pack(side="right")

    def _limpiar_filtro(self) -> None:
        self.txt_buscar.delete(0, tk.END)
        self.var_solo_activas.set(False)
        self.cargar_datos()

    def cargar_datos(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        busqueda = self.txt_buscar.get().strip()
        solo_activas = self.var_solo_activas.get()

        categorias = self.categoria_service.listar_categorias(solo_activas=solo_activas, busqueda=busqueda)

        for c in categorias:
            estado_txt = "Activa" if c.esta_activa else "Inactiva"
            self.tree.insert("", "end", values=(c.id, c.nombre, estado_txt))

    def _obtener_categoria_seleccionada(self) -> Optional[int]:
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione una categoría de la lista para continuar.", parent=self)
            return None
        valores = self.tree.item(seleccion[0], "values")
        return int(valores[0])

    def _abrir_modal_crear(self) -> None:
        self._mostrar_formulario("Nueva Categoría")

    def _abrir_modal_editar(self) -> None:
        cat_id = self._obtener_categoria_seleccionada()
        if not cat_id:
            return
        cat = self.categoria_service.obtener_categoria(cat_id)
        if not cat:
            messagebox.showerror("Error", "No se encontró la categoría seleccionada.", parent=self)
            return
        self._mostrar_formulario("Editar Categoría", categoria=cat)

    def _mostrar_formulario(self, titulo: str, categoria: Optional[Categoria] = None) -> None:
        modal = tk.Toplevel(self)
        modal.title(titulo)
        modal.geometry("400x230")
        modal.resizable(False, False)
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        # Centrar relativo a ventana principal
        modal.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - 400) // 2
        y = self.winfo_rooty() + (self.winfo_height() - 230) // 2
        modal.geometry(f"+{x}+{y}")

        frame = ttk.Frame(modal, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Nombre de la categoría:").pack(anchor="w", pady=(0, 5))
        txt_nombre = ttk.Entry(frame, width=35)
        txt_nombre.pack(fill="x", pady=(0, 15))
        txt_nombre.focus_set()

        var_activo = tk.BooleanVar(value=True)
        if categoria:
            txt_nombre.insert(0, categoria.nombre)
            var_activo.set(categoria.esta_activa)

        chk_activo = ttk.Checkbutton(frame, text="Categoría Activa (disponible para productos)", variable=var_activo)
        chk_activo.pack(anchor="w", pady=(0, 20))

        btn_box = ttk.Frame(frame)
        btn_box.pack(fill="x")

        def guardar():
            nombre = txt_nombre.get().strip()
            activo = 1 if var_activo.get() else 0

            try:
                if categoria:
                    self.categoria_service.actualizar_categoria(categoria.id, nombre, activo)
                    messagebox.showinfo("Éxito", "Categoría actualizada correctamente.", parent=modal)
                else:
                    self.categoria_service.crear_categoria(nombre, activo)
                    messagebox.showinfo("Éxito", "Categoría registrada correctamente.", parent=modal)
                modal.destroy()
                self.cargar_datos()
            except ValueError as err:
                messagebox.showerror("Validación", str(err), parent=modal)
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}", parent=modal)

        ttk.Button(btn_box, text="Guardar", style="Primary.TButton", command=guardar).pack(side="left", padx=(0, 8))
        ttk.Button(btn_box, text="Cancelar", command=modal.destroy).pack(side="left")

    def _alternar_estado(self) -> None:
        cat_id = self._obtener_categoria_seleccionada()
        if not cat_id:
            return
        cat = self.categoria_service.obtener_categoria(cat_id)
        if not cat:
            return

        nuevo_estado = 0 if cat.esta_activa else 1
        accion = "desactivar" if cat.esta_activa else "activar"

        confirmar = messagebox.askyesno(
            "Confirmación",
            f"¿Está seguro de que desea {accion} la categoría '{cat.nombre}'?",
            parent=self
        )
        if not confirmar:
            return

        try:
            self.categoria_service.alternar_estado(cat_id, nuevo_estado)
            self.cargar_datos()
            messagebox.showinfo("Éxito", f"Categoría {accion}da con éxito.", parent=self)
        except ValueError as err:
            messagebox.showwarning("Atención", str(err), parent=self)

    def _eliminar_categoria(self) -> None:
        cat_id = self._obtener_categoria_seleccionada()
        if not cat_id:
            return
        cat = self.categoria_service.obtener_categoria(cat_id)
        if not cat:
            return

        confirmar = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Desea eliminar definitivamente la categoría '{cat.nombre}'?\n\nEsta acción no se puede deshacer.",
            parent=self
        )
        if not confirmar:
            return

        try:
            self.categoria_service.eliminar_categoria(cat_id)
            self.cargar_datos()
            messagebox.showinfo("Éxito", "Categoría eliminada con éxito.", parent=self)
        except ValueError as err:
            messagebox.showwarning("Integridad de Datos", str(err), parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la categoría: {e}", parent=self)
