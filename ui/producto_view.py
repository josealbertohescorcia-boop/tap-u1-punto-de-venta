import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from models.producto import Producto
from services.producto_service import ProductoService
from services.categoria_service import CategoriaService

class ProductoView(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, producto_service: ProductoService, categoria_service: CategoriaService):
        super().__init__(parent, padding=15)
        self.producto_service = producto_service
        self.categoria_service = categoria_service
        self._construir_ui()
        self.cargar_datos()

    def _construir_ui(self) -> None:
        # Título
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(header_frame, text="Catálogo de Productos e Inventario", style="Titulo.TLabel").pack(side="left")

        # Filtros de búsqueda
        filtro_frame = ttk.LabelFrame(self, text=" Búsqueda y Filtros ", padding=10)
        filtro_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(filtro_frame, text="Buscar:").pack(side="left", padx=(0, 5))
        self.txt_buscar = ttk.Entry(filtro_frame, width=22)
        self.txt_buscar.pack(side="left", padx=(0, 12))
        self.txt_buscar.bind("<KeyRelease>", lambda event: self.cargar_datos())

        ttk.Label(filtro_frame, text="Categoría:").pack(side="left", padx=(0, 5))
        self.cbo_filtro_cat = ttk.Combobox(filtro_frame, state="readonly", width=22)
        self.cbo_filtro_cat.pack(side="left", padx=(0, 12))
        self.cbo_filtro_cat.bind("<<ComboboxSelected>>", lambda event: self.cargar_datos())

        self.var_solo_activos = tk.BooleanVar(value=False)
        chk_activos = ttk.Checkbutton(filtro_frame, text="Solo activos", variable=self.var_solo_activos, command=self.cargar_datos)
        chk_activos.pack(side="left", padx=(0, 15))

        btn_limpiar = ttk.Button(filtro_frame, text="Limpiar Filtros", command=self._limpiar_filtros)
        btn_limpiar.pack(side="left")

        # Tabla de productos (Treeview)
        tabla_frame = ttk.Frame(self)
        tabla_frame.pack(fill="both", expand=True)

        columnas = ("id", "codigo", "nombre", "categoria", "precio", "stock", "estado", "alerta")
        self.tree = ttk.Treeview(tabla_frame, columns=columnas, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("codigo", text="Código")
        self.tree.heading("nombre", text="Nombre del Producto")
        self.tree.heading("categoria", text="Categoría")
        self.tree.heading("precio", text="Precio ($)")
        self.tree.heading("stock", text="Stock")
        self.tree.heading("estado", text="Estado")
        self.tree.heading("alerta", text="Alerta Stock")

        self.tree.column("id", width=45, anchor="center")
        self.tree.column("codigo", width=100, anchor="center")
        self.tree.column("nombre", width=260, anchor="w")
        self.tree.column("categoria", width=170, anchor="w")
        self.tree.column("precio", width=90, anchor="e")
        self.tree.column("stock", width=70, anchor="center")
        self.tree.column("estado", width=85, anchor="center")
        self.tree.column("alerta", width=120, anchor="center")

        # Tags para color en stock bajo o agotado
        self.tree.tag_configure("stock_agotado", foreground="#c0392b")
        self.tree.tag_configure("stock_bajo", foreground="#d35400")
        self.tree.tag_configure("inactivo", foreground="#7f8c8d")

        scroll_y = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Barra de botones
        btn_frame = ttk.Frame(self, padding=(0, 10))
        btn_frame.pack(fill="x")

        ttk.Button(btn_frame, text="➕ Nuevo Producto", style="Primary.TButton", command=self._abrir_modal_crear).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="✏️ Editar", command=self._abrir_modal_editar).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="🔄 Activar / Desactivar", command=self._alternar_estado).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="🗑️ Eliminar", style="Danger.TButton", command=self._eliminar_producto).pack(side="right")

    def _actualizar_combo_categorias(self) -> None:
        categorias = self.categoria_service.listar_categorias()
        opciones = ["-- Todas las Categorías --"] + [c.nombre for c in categorias]
        self._map_categorias = {c.nombre: c.id for c in categorias}
        self.cbo_filtro_cat["values"] = opciones
        if not self.cbo_filtro_cat.get():
            self.cbo_filtro_cat.current(0)

    def _limpiar_filtros(self) -> None:
        self.txt_buscar.delete(0, tk.END)
        self.var_solo_activos.set(False)
        self.cbo_filtro_cat.current(0)
        self.cargar_datos()

    def cargar_datos(self) -> None:
        self._actualizar_combo_categorias()

        for item in self.tree.get_children():
            self.tree.delete(item)

        busqueda = self.txt_buscar.get().strip()
        solo_activos = self.var_solo_activos.get()

        cat_sel = self.cbo_filtro_cat.get()
        categoria_id = self._map_categorias.get(cat_sel, None) if cat_sel != "-- Todas las Categorías --" else None

        productos = self.producto_service.listar_productos(
            solo_activos=solo_activos,
            busqueda=busqueda,
            categoria_id=categoria_id
        )

        for p in productos:
            estado_txt = "Activo" if p.esta_activo else "Inactivo"
            precio_fmt = f"${p.precio:,.2f}"

            if not p.esta_activo:
                alerta_txt = "Inactivo"
                tag = "inactivo"
            elif p.stock == 0:
                alerta_txt = "⚠️ Agotado (0)"
                tag = "stock_agotado"
            elif p.stock <= 5:
                alerta_txt = f"⚠️ Stock Bajo ({p.stock})"
                tag = "stock_bajo"
            else:
                alerta_txt = "✓ Normal"
                tag = ""

            self.tree.insert("", "end", values=(
                p.id,
                p.codigo,
                p.nombre,
                p.categoria_nombre,
                precio_fmt,
                p.stock,
                estado_txt,
                alerta_txt
            ), tags=(tag,) if tag else ())

    def _obtener_producto_seleccionado(self) -> Optional[int]:
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un producto de la lista para continuar.", parent=self)
            return None
        valores = self.tree.item(seleccion[0], "values")
        return int(valores[0])

    def _abrir_modal_crear(self) -> None:
        self._mostrar_formulario("Nuevo Producto")

    def _abrir_modal_editar(self) -> None:
        prod_id = self._obtener_producto_seleccionado()
        if not prod_id:
            return
        prod = self.producto_service.obtener_producto(prod_id)
        if not prod:
            messagebox.showerror("Error", "No se encontró el producto seleccionado.", parent=self)
            return
        self._mostrar_formulario("Editar Producto", producto=prod)

    def _mostrar_formulario(self, titulo: str, producto: Optional[Producto] = None) -> None:
        modal = tk.Toplevel(self)
        modal.title(titulo)
        modal.geometry("450x420")
        modal.resizable(False, False)
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        # Centrar relativo a la ventana principal
        modal.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - 450) // 2
        y = self.winfo_rooty() + (self.winfo_height() - 420) // 2
        modal.geometry(f"+{x}+{y}")

        frame = ttk.Frame(modal, padding=20)
        frame.pack(fill="both", expand=True)

        # Campos
        ttk.Label(frame, text="Código del Producto:").pack(anchor="w", pady=(0, 2))
        txt_codigo = ttk.Entry(frame)
        txt_codigo.pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="Nombre del Producto:").pack(anchor="w", pady=(0, 2))
        txt_nombre = ttk.Entry(frame)
        txt_nombre.pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="Categoría:").pack(anchor="w", pady=(0, 2))
        cbo_cat = ttk.Combobox(frame, state="readonly")
        categorias_activas = self.categoria_service.listar_categorias(solo_activas=True)
        cat_dict = {c.nombre: c.id for c in categorias_activas}
        id_to_cat = {c.id: c.nombre for c in categorias_activas}
        cbo_cat["values"] = list(cat_dict.keys())
        cbo_cat.pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="Precio de Venta ($):").pack(anchor="w", pady=(0, 2))
        txt_precio = ttk.Entry(frame)
        txt_precio.pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="Existencias (Stock):").pack(anchor="w", pady=(0, 2))
        txt_stock = ttk.Entry(frame)
        txt_stock.pack(fill="x", pady=(0, 10))

        var_activo = tk.BooleanVar(value=True)
        chk_activo = ttk.Checkbutton(frame, text="Producto Activo (disponible para venta)", variable=var_activo)
        chk_activo.pack(anchor="w", pady=(0, 15))

        # Cargar datos si estamos editando
        if producto:
            txt_codigo.insert(0, producto.codigo)
            txt_nombre.insert(0, producto.nombre)
            txt_precio.insert(0, str(producto.precio))
            txt_stock.insert(0, str(producto.stock))
            var_activo.set(producto.esta_activo)

            # Seleccionar la categoría en el combo
            nombre_cat_actual = id_to_cat.get(producto.categoria_id, "")
            if not nombre_cat_actual:
                # Si la categoría del producto está inactiva, añadirla temporalmente a la lista para no perderla
                cat_obj = self.categoria_service.obtener_categoria(producto.categoria_id)
                if cat_obj:
                    nombre_cat_actual = f"{cat_obj.nombre} (Inactiva)"
                    cat_dict[nombre_cat_actual] = cat_obj.id
                    cbo_cat["values"] = list(cat_dict.keys())
            cbo_cat.set(nombre_cat_actual)
        elif categorias_activas:
            cbo_cat.current(0)

        txt_codigo.focus_set()

        btn_box = ttk.Frame(frame)
        btn_box.pack(fill="x")

        def guardar():
            codigo = txt_codigo.get().strip()
            nombre = txt_nombre.get().strip()
            cat_nombre = cbo_cat.get()
            categoria_id = cat_dict.get(cat_nombre)
            precio_str = txt_precio.get().strip()
            stock_str = txt_stock.get().strip()
            activo = 1 if var_activo.get() else 0

            try:
                if producto:
                    self.producto_service.actualizar_producto(
                        producto.id, codigo, nombre, categoria_id, precio_str, stock_str, activo
                    )
                    messagebox.showinfo("Éxito", "Producto actualizado correctamente.", parent=modal)
                else:
                    self.producto_service.crear_producto(
                        codigo, nombre, categoria_id, precio_str, stock_str, activo
                    )
                    messagebox.showinfo("Éxito", "Producto registrado correctamente.", parent=modal)
                modal.destroy()
                self.cargar_datos()
            except ValueError as err:
                messagebox.showerror("Error de Validación", str(err), parent=modal)
            except Exception as e:
                messagebox.showerror("Error Inesperado", f"Ocurrió un error al guardar: {e}", parent=modal)

        ttk.Button(btn_box, text="Guardar", style="Primary.TButton", command=guardar).pack(side="left", padx=(0, 8))
        ttk.Button(btn_box, text="Cancelar", command=modal.destroy).pack(side="left")

    def _alternar_estado(self) -> None:
        prod_id = self._obtener_producto_seleccionado()
        if not prod_id:
            return
        prod = self.producto_service.obtener_producto(prod_id)
        if not prod:
            return

        nuevo_estado = 0 if prod.esta_activo else 1
        accion = "desactivar" if prod.esta_activo else "activar"

        confirmar = messagebox.askyesno(
            "Confirmación",
            f"¿Está seguro de que desea {accion} el producto '{prod.nombre}'?",
            parent=self
        )
        if not confirmar:
            return

        try:
            self.producto_service.alternar_estado(prod_id, nuevo_estado)
            self.cargar_datos()
            messagebox.showinfo("Éxito", f"Producto {accion}do con éxito.", parent=self)
        except ValueError as err:
            messagebox.showwarning("Atención", str(err), parent=self)

    def _eliminar_producto(self) -> None:
        prod_id = self._obtener_producto_seleccionado()
        if not prod_id:
            return
        prod = self.producto_service.obtener_producto(prod_id)
        if not prod:
            return

        confirmar = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Desea eliminar definitivamente el producto '{prod.nombre}'?\n\n"
            "Nota: Si el producto tiene ventas registradas, el sistema protegerá la integridad y no permitirá borrarlo.",
            parent=self
        )
        if not confirmar:
            return

        try:
            self.producto_service.eliminar_producto(prod_id)
            self.cargar_datos()
            messagebox.showinfo("Éxito", "Producto eliminado con éxito.", parent=self)
        except ValueError as err:
            messagebox.showwarning("Integridad de Datos", str(err), parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el producto: {e}", parent=self)
