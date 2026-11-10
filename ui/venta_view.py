import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any, Callable, Optional
from models.usuario import Usuario
from models.producto import Producto
from services.venta_service import VentaService
from services.producto_service import ProductoService
from ui.styles import COLOR_EXITO, COLOR_PRIMARIO, COLOR_PELIGRO

class VentaView(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, venta_service: VentaService, producto_service: ProductoService,
                 usuario_actual_getter: Callable[[], Usuario], on_venta_realizada: Optional[Callable[[], None]] = None):
        super().__init__(parent, padding=12)
        self.venta_service = venta_service
        self.producto_service = producto_service
        self.usuario_actual_getter = usuario_actual_getter
        self.on_venta_realizada = on_venta_realizada

        # Carrito en memoria: lista de diccionarios con info de la venta
        self.carrito: List[Dict[str, Any]] = []

        self._construir_ui()
        self.cargar_catalogo_disponible()

    def _construir_ui(self) -> None:
        # Título superior
        lbl_titulo = ttk.Label(self, text="Punto de Venta · Registrar Nueva Venta", style="Titulo.TLabel")
        lbl_titulo.pack(anchor="w", pady=(0, 10))

        # Contenedor dividido en 2 columnas: izquierda (productos disponibles) y derecha (carrito y pago)
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True)

        # ----------------- PANEL IZQUIERDO: SELECCIÓN DE PRODUCTOS -----------------
        frame_izq = ttk.Frame(paned, padding=5)
        paned.add(frame_izq, weight=3)

        box_izq = ttk.LabelFrame(frame_izq, text=" 1. Catálogo de Productos Disponibles ", padding=10)
        box_izq.pack(fill="both", expand=True)

        # Buscador rápido
        search_box = ttk.Frame(box_izq)
        search_box.pack(fill="x", pady=(0, 8))

        ttk.Label(search_box, text="Buscar:").pack(side="left", padx=(0, 5))
        self.txt_buscar_prod = ttk.Entry(search_box)
        self.txt_buscar_prod.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.txt_buscar_prod.bind("<KeyRelease>", lambda e: self.cargar_catalogo_disponible())

        btn_refrescar = ttk.Button(search_box, text="🔄", width=3, command=self.cargar_catalogo_disponible)
        btn_refrescar.pack(side="left")

        # Tabla de productos disponibles
        cols_disp = ("id", "codigo", "nombre", "categoria", "precio", "stock")
        self.tree_disp = ttk.Treeview(box_izq, columns=cols_disp, show="headings", selectmode="browse")
        self.tree_disp.heading("id", text="ID")
        self.tree_disp.heading("codigo", text="Código")
        self.tree_disp.heading("nombre", text="Producto")
        self.tree_disp.heading("categoria", text="Categoría")
        self.tree_disp.heading("precio", text="Precio")
        self.tree_disp.heading("stock", text="Stock")

        self.tree_disp.column("id", width=35, anchor="center")
        self.tree_disp.column("codigo", width=85, anchor="center")
        self.tree_disp.column("nombre", width=180, anchor="w")
        self.tree_disp.column("categoria", width=120, anchor="w")
        self.tree_disp.column("precio", width=70, anchor="e")
        self.tree_disp.column("stock", width=55, anchor="center")

        scroll_disp = ttk.Scrollbar(box_izq, orient="vertical", command=self.tree_disp.yview)
        self.tree_disp.configure(yscrollcommand=scroll_disp.set)

        self.tree_disp.pack(side="top", fill="both", expand=True)
        scroll_disp.pack(side="right", fill="y")

        # Panel de agregar cantidad
        add_box = ttk.Frame(box_izq, padding=(0, 10))
        add_box.pack(fill="x")

        ttk.Label(add_box, text="Cantidad a vender:", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))
        self.spn_cantidad = ttk.Spinbox(add_box, from_=1, to=999, width=7)
        self.spn_cantidad.set(1)
        self.spn_cantidad.pack(side="left", padx=(0, 12))

        btn_add = ttk.Button(add_box, text="➕ Agregar al Carrito", style="Primary.TButton", command=self._agregar_al_carrito)
        btn_add.pack(side="left")

        # ----------------- PANEL DERECHO: CARRITO Y CIERRE DE VENTA -----------------
        frame_der = ttk.Frame(paned, padding=5)
        paned.add(frame_der, weight=4)

        box_der = ttk.LabelFrame(frame_der, text=" 2. Carrito de Compra ", padding=10)
        box_der.pack(fill="both", expand=True)

        # Tabla del carrito
        cols_cart = ("codigo", "nombre", "cantidad", "precio_u", "subtotal")
        self.tree_cart = ttk.Treeview(box_der, columns=cols_cart, show="headings", selectmode="browse")
        self.tree_cart.heading("codigo", text="Código")
        self.tree_cart.heading("nombre", text="Descripción")
        self.tree_cart.heading("cantidad", text="Cant.")
        self.tree_cart.heading("precio_u", text="P. Unitario")
        self.tree_cart.heading("subtotal", text="Subtotal")

        self.tree_cart.column("codigo", width=85, anchor="center")
        self.tree_cart.column("nombre", width=160, anchor="w")
        self.tree_cart.column("cantidad", width=50, anchor="center")
        self.tree_cart.column("precio_u", width=80, anchor="e")
        self.tree_cart.column("subtotal", width=85, anchor="e")

        scroll_cart = ttk.Scrollbar(box_der, orient="vertical", command=self.tree_cart.yview)
        self.tree_cart.configure(yscrollcommand=scroll_cart.set)

        self.tree_cart.pack(side="top", fill="both", expand=True)
        scroll_cart.pack(side="right", fill="y")

        # Botones para modificar carrito
        cart_actions = ttk.Frame(box_der, padding=(0, 8))
        cart_actions.pack(fill="x")

        ttk.Button(cart_actions, text="❌ Quitar Seleccionado", command=self._quitar_seleccionado).pack(side="left", padx=(0, 8))
        ttk.Button(cart_actions, text="🗑️ Vaciar Carrito", command=self._vaciar_carrito).pack(side="left")

        # Tarjeta de totalización
        card_total = ttk.LabelFrame(box_der, text=" Resumen y Cobro ", padding=12)
        card_total.pack(fill="x", pady=(10, 0))

        self.lbl_articulos = ttk.Label(card_total, text="Artículos en carrito: 0 unidades", font=("Segoe UI", 9))
        self.lbl_articulos.pack(anchor="w")

        total_frame = ttk.Frame(card_total)
        total_frame.pack(fill="x", pady=(8, 12))

        ttk.Label(total_frame, text="TOTAL A PAGAR:", font=("Segoe UI", 12, "bold"), foreground=COLOR_PRIMARIO).pack(side="left")
        self.lbl_total_monto = ttk.Label(total_frame, text="$0.00", font=("Segoe UI", 18, "bold"), foreground=COLOR_EXITO)
        self.lbl_total_monto.pack(side="right")

        btn_confirmar = ttk.Button(card_total, text="💳 CONFIRMAR Y REGISTRAR VENTA", style="Success.TButton", command=self._confirmar_venta)
        btn_confirmar.pack(fill="x", ipady=4)

    def cargar_catalogo_disponible(self) -> None:
        """Carga solo productos activos en el panel izquierdo."""
        for item in self.tree_disp.get_children():
            self.tree_disp.delete(item)

        busqueda = self.txt_buscar_prod.get().strip()
        productos = self.producto_service.listar_productos(solo_activos=True, busqueda=busqueda)

        for p in productos:
            # Mostramos el stock restando lo que ya esté apartado en el carrito local
            stock_en_carrito = sum(c["cantidad"] for c in self.carrito if c["producto_id"] == p.id)
            stock_disponible = p.stock - stock_en_carrito

            self.tree_disp.insert("", "end", values=(
                p.id,
                p.codigo,
                p.nombre,
                p.categoria_nombre,
                f"${p.precio:,.2f}",
                stock_disponible
            ))

    def _agregar_al_carrito(self) -> None:
        seleccion = self.tree_disp.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un producto del catálogo para agregar.", parent=self)
            return

        valores = self.tree_disp.item(seleccion[0], "values")
        prod_id = int(valores[0])

        try:
            cant_ingresada = int(self.spn_cantidad.get())
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero mayor a 0.", parent=self)
            return

        if cant_ingresada <= 0:
            messagebox.showerror("Error", "La cantidad debe ser mayor que 0.", parent=self)
            return

        producto = self.producto_service.obtener_producto(prod_id)
        if not producto or not producto.esta_activo:
            messagebox.showerror("Error", "El producto no está disponible para venta.", parent=self)
            return

        # Calcular cuánto se tiene ya en el carrito
        ya_en_carrito = sum(c["cantidad"] for c in self.carrito if c["producto_id"] == prod_id)
        total_deseado = ya_en_carrito + cant_ingresada

        if total_deseado > producto.stock:
            messagebox.showwarning(
                "Stock Insuficiente",
                f"No hay suficientes existencias de '{producto.nombre}'.\n"
                f"Stock disponible total: {producto.stock}\n"
                f"En carrito: {ya_en_carrito}\n"
                f"Intentando agregar: {cant_ingresada}",
                parent=self
            )
            return

        # Si ya existe en el carrito, sumamos la cantidad
        encontrado = False
        for c in self.carrito:
            if c["producto_id"] == prod_id:
                c["cantidad"] += cant_ingresada
                c["subtotal"] = round(c["cantidad"] * c["precio_unitario"], 2)
                encontrado = True
                break

        if not encontrado:
            self.carrito.append({
                "producto_id": producto.id,
                "codigo": producto.codigo,
                "nombre": producto.nombre,
                "cantidad": cant_ingresada,
                "precio_unitario": producto.precio,
                "subtotal": round(cant_ingresada * producto.precio, 2)
            })

        self.spn_cantidad.set(1)
        self._actualizar_vista_carrito()
        self.cargar_catalogo_disponible()

    def _actualizar_vista_carrito(self) -> None:
        for item in self.tree_cart.get_children():
            self.tree_cart.delete(item)

        total = 0.0
        articulos = 0

        for item in self.carrito:
            self.tree_cart.insert("", "end", values=(
                item["codigo"],
                item["nombre"],
                item["cantidad"],
                f"${item['precio_unitario']:,.2f}",
                f"${item['subtotal']:,.2f}"
            ))
            total += item["subtotal"]
            articulos += item["cantidad"]

        self.lbl_articulos.config(text=f"Artículos en carrito: {articulos} unidades")
        self.lbl_total_monto.config(text=f"${total:,.2f}")

    def _quitar_seleccionado(self) -> None:
        seleccion = self.tree_cart.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un producto del carrito para quitarlo.", parent=self)
            return

        index = self.tree_cart.index(seleccion[0])
        del self.carrito[index]
        self._actualizar_vista_carrito()
        self.cargar_catalogo_disponible()

    def _vaciar_carrito(self) -> None:
        if not self.carrito:
            return
        if messagebox.askyesno("Confirmación", "¿Desea vaciar todos los productos del carrito actual?", parent=self):
            self.carrito.clear()
            self._actualizar_vista_carrito()
            self.cargar_catalogo_disponible()

    def _confirmar_venta(self) -> None:
        if not self.carrito:
            messagebox.showwarning("Carrito Vacío", "No hay productos en el carrito para registrar la venta.", parent=self)
            return

        usuario = self.usuario_actual_getter()
        if not usuario:
            messagebox.showerror("Error", "No hay un usuario activo identificado para registrar la venta.", parent=self)
            return

        total_venta = sum(item["subtotal"] for item in self.carrito)
        total_arts = sum(item["cantidad"] for item in self.carrito)

        confirmar = messagebox.askyesno(
            "Confirmar Venta",
            f"¿Desea registrar esta venta por un total de ${total_venta:,.2f}?\n"
            f"Artículos: {total_arts} unidades.\n\n"
            "El sistema descontará las existencias del inventario de forma inmediata.",
            parent=self
        )
        if not confirmar:
            return

        # Preparar ítems para el servicio
        items_servicio = [
            {
                "producto_id": item["producto_id"],
                "cantidad": item["cantidad"],
                "precio_unitario": item["precio_unitario"]
            }
            for item in self.carrito
        ]

        try:
            venta_id = self.venta_service.registrar_venta(usuario.id, items_servicio)

            messagebox.showinfo(
                "¡Venta Exitosa!",
                f"Venta registrada exitosamente con Folio #{venta_id}.\n"
                f"Vendedor: {usuario.username}\n"
                f"Total cobrado: ${total_venta:,.2f}\n\n"
                "El inventario ha sido actualizado.",
                parent=self
            )

            # Limpiar carrito
            self.carrito.clear()
            self._actualizar_vista_carrito()
            self.cargar_catalogo_disponible()

            # Notificar callback para actualizar otras pestañas (como catálogo e historial)
            if self.on_venta_realizada:
                self.on_venta_realizada()

        except ValueError as err:
            messagebox.showerror("Error en Venta", str(err), parent=self)
            self.cargar_catalogo_disponible()
        except Exception as e:
            messagebox.showerror("Error Crítico", f"Ocurrió un error al procesar la transacción: {e}", parent=self)
            self.cargar_catalogo_disponible()
