import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from services.venta_service import VentaService

class VentaHistorialView(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, venta_service: VentaService):
        super().__init__(parent, padding=15)
        self.venta_service = venta_service
        self._modo_join_completo = False
        self._construir_ui()
        self.cargar_datos()

    def _construir_ui(self) -> None:
        # Encabezado
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(header_frame, text="Historial de Ventas y Movimientos", style="Titulo.TLabel").pack(side="left")

        # Filtros de búsqueda
        filtro_frame = ttk.LabelFrame(self, text=" Búsqueda y Modo de Visualización ", padding=10)
        filtro_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(filtro_frame, text="Buscar:").pack(side="left", padx=(0, 5))
        self.txt_buscar = ttk.Entry(filtro_frame, width=28)
        self.txt_buscar.pack(side="left", padx=(0, 12))
        self.txt_buscar.bind("<KeyRelease>", lambda e: self.cargar_datos())

        btn_buscar = ttk.Button(filtro_frame, text="🔍 Buscar", command=self.cargar_datos)
        btn_buscar.pack(side="left", padx=(0, 8))

        btn_limpiar = ttk.Button(filtro_frame, text="Limpiar", command=self._limpiar_filtro)
        btn_limpiar.pack(side="left", padx=(0, 15))

        # Selector de modo
        self.btn_toggle_join = ttk.Button(
            filtro_frame,
            text="🔀 Ver Consulta SQL con JOIN Completo (RF-7)",
            command=self._alternar_modo_vista
        )
        self.btn_toggle_join.pack(side="right")

        # Contenedor dinámico de vistas
        self.contenedor_vistas = ttk.Frame(self)
        self.contenedor_vistas.pack(fill="both", expand=True)

        self._construir_vista_maestro_detalle()
        self._construir_vista_join_completo()

        # Mostrar por defecto maestro-detalle
        self.frame_maestro_detalle.pack(fill="both", expand=True)

    def _construir_vista_maestro_detalle(self) -> None:
        self.frame_maestro_detalle = ttk.Frame(self.contenedor_vistas)

        # Panel superior: Ventas
        box_ventas = ttk.LabelFrame(self.frame_maestro_detalle, text=" Folios de Venta Realizados ", padding=8)
        box_ventas.pack(fill="both", expand=True, pady=(0, 8))

        cols_v = ("folio", "fecha", "vendedor", "total")
        self.tree_ventas = ttk.Treeview(box_ventas, columns=cols_v, show="headings", selectmode="browse", height=7)
        self.tree_ventas.heading("folio", text="Folio #")
        self.tree_ventas.heading("fecha", text="Fecha y Hora")
        self.tree_ventas.heading("vendedor", text="Vendedor (JOIN usuarios_sistema)")
        self.tree_ventas.heading("total", text="Total Cobrado ($)")

        self.tree_ventas.column("folio", width=80, anchor="center")
        self.tree_ventas.column("fecha", width=200, anchor="center")
        self.tree_ventas.column("vendedor", width=220, anchor="w")
        self.tree_ventas.column("total", width=140, anchor="e")

        sc_v = ttk.Scrollbar(box_ventas, orient="vertical", command=self.tree_ventas.yview)
        self.tree_ventas.configure(yscrollcommand=sc_v.set)

        self.tree_ventas.pack(side="left", fill="both", expand=True)
        sc_v.pack(side="right", fill="y")

        self.tree_ventas.bind("<<TreeviewSelect>>", self._on_venta_seleccionada)

        # Panel inferior: Detalle de la venta seleccionada
        self.box_detalles = ttk.LabelFrame(self.frame_maestro_detalle, text=" Artículos de la Venta (JOIN detalle_venta + productos) ", padding=8)
        self.box_detalles.pack(fill="both", expand=True)

        cols_d = ("codigo", "producto", "cantidad", "precio_u", "subtotal")
        self.tree_detalles = ttk.Treeview(self.box_detalles, columns=cols_d, show="headings", selectmode="browse", height=5)
        self.tree_detalles.heading("codigo", text="Código")
        self.tree_detalles.heading("producto", text="Nombre del Producto")
        self.tree_detalles.heading("cantidad", text="Cantidad")
        self.tree_detalles.heading("precio_u", text="Precio Unitario ($)")
        self.tree_detalles.heading("subtotal", text="Subtotal ($)")

        self.tree_detalles.column("codigo", width=100, anchor="center")
        self.tree_detalles.column("producto", width=280, anchor="w")
        self.tree_detalles.column("cantidad", width=80, anchor="center")
        self.tree_detalles.column("precio_u", width=120, anchor="e")
        self.tree_detalles.column("subtotal", width=120, anchor="e")

        sc_d = ttk.Scrollbar(self.box_detalles, orient="vertical", command=self.tree_detalles.yview)
        self.tree_detalles.configure(yscrollcommand=sc_d.set)

        self.tree_detalles.pack(side="left", fill="both", expand=True)
        sc_d.pack(side="right", fill="y")

    def _construir_vista_join_completo(self) -> None:
        self.frame_join_completo = ttk.Frame(self.contenedor_vistas)

        # Banner explicativo para la rúbrica / defensa
        banner = ttk.Frame(self.frame_join_completo, padding=6)
        banner.pack(fill="x", pady=(0, 6))

        ttk.Label(
            banner,
            text="📌 Consulta SQL con JOIN: detalle_venta ⋈ ventas ⋈ productos ⋈ categorias ⋈ usuarios_sistema",
            font=("Segoe UI", 9, "bold"),
            foreground="#1f4b82"
        ).pack(side="left")

        cols_join = ("detalle_id", "folio", "fecha", "vendedor", "codigo", "producto", "categoria", "cant", "precio_u", "subtotal")
        self.tree_join = ttk.Treeview(self.frame_join_completo, columns=cols_join, show="headings", selectmode="browse")

        self.tree_join.heading("detalle_id", text="ID Detalle")
        self.tree_join.heading("folio", text="Folio")
        self.tree_join.heading("fecha", text="Fecha")
        self.tree_join.heading("vendedor", text="Vendedor")
        self.tree_join.heading("codigo", text="Código")
        self.tree_join.heading("producto", text="Producto")
        self.tree_join.heading("categoria", text="Categoría")
        self.tree_join.heading("cant", text="Cant.")
        self.tree_join.heading("precio_u", text="P. Unitario")
        self.tree_join.heading("subtotal", text="Subtotal")

        self.tree_join.column("detalle_id", width=65, anchor="center")
        self.tree_join.column("folio", width=60, anchor="center")
        self.tree_join.column("fecha", width=140, anchor="center")
        self.tree_join.column("vendedor", width=100, anchor="w")
        self.tree_join.column("codigo", width=85, anchor="center")
        self.tree_join.column("producto", width=190, anchor="w")
        self.tree_join.column("categoria", width=130, anchor="w")
        self.tree_join.column("cant", width=50, anchor="center")
        self.tree_join.column("precio_u", width=85, anchor="e")
        self.tree_join.column("subtotal", width=85, anchor="e")

        sc_j = ttk.Scrollbar(self.frame_join_completo, orient="vertical", command=self.tree_join.yview)
        self.tree_join.configure(yscrollcommand=sc_j.set)

        self.tree_join.pack(side="left", fill="both", expand=True)
        sc_j.pack(side="right", fill="y")

    def _alternar_modo_vista(self) -> None:
        self._modo_join_completo = not self._modo_join_completo
        if self._modo_join_completo:
            self.frame_maestro_detalle.pack_forget()
            self.frame_join_completo.pack(fill="both", expand=True)
            self.btn_toggle_join.config(text="📋 Ver Vista Maestro - Detalle")
        else:
            self.frame_join_completo.pack_forget()
            self.frame_maestro_detalle.pack(fill="both", expand=True)
            self.btn_toggle_join.config(text="🔀 Ver Consulta SQL con JOIN Completo (RF-7)")
        self.cargar_datos()

    def _limpiar_filtro(self) -> None:
        self.txt_buscar.delete(0, tk.END)
        self.cargar_datos()

    def cargar_datos(self) -> None:
        busqueda = self.txt_buscar.get().strip()

        if self._modo_join_completo:
            for item in self.tree_join.get_children():
                self.tree_join.delete(item)

            filas = self.venta_service.listar_detalles_con_join(busqueda=busqueda)
            for f in filas:
                self.tree_join.insert("", "end", values=(
                    f["detalle_id"],
                    f["folio_venta"],
                    f["fecha_venta"],
                    f["vendedor"],
                    f["codigo_producto"],
                    f["nombre_producto"],
                    f["categoria"],
                    f["cantidad"],
                    f"${f['precio_unitario']:,.2f}",
                    f"${f['subtotal']:,.2f}"
                ))
        else:
            for item in self.tree_ventas.get_children():
                self.tree_ventas.delete(item)
            for item in self.tree_detalles.get_children():
                self.tree_detalles.delete(item)

            ventas = self.venta_service.listar_ventas(busqueda=busqueda)
            for v in ventas:
                self.tree_ventas.insert("", "end", values=(
                    v["id"],
                    v["fecha"],
                    v["usuario_nombre"],
                    f"${v['total']:,.2f}"
                ))

            # Seleccionar automáticamente la primera si existe
            hijos = self.tree_ventas.get_children()
            if hijos:
                self.tree_ventas.selection_set(hijos[0])
                self._on_venta_seleccionada()

    def _on_venta_seleccionada(self, event=None) -> None:
        seleccion = self.tree_ventas.selection()
        if not seleccion:
            return

        valores = self.tree_ventas.item(seleccion[0], "values")
        folio = int(valores[0])

        for item in self.tree_detalles.get_children():
            self.tree_detalles.delete(item)

        detalles = self.venta_service.obtener_detalles_venta(folio)
        for d in detalles:
            self.tree_detalles.insert("", "end", values=(
                d["producto_codigo"],
                d["producto_nombre"],
                d["cantidad"],
                f"${d['precio_unitario']:,.2f}",
                f"${d['subtotal']:,.2f}"
            ))

        self.box_detalles.config(text=f" Artículos de la Venta Folio #{folio} (JOIN detalle_venta + productos) ")
