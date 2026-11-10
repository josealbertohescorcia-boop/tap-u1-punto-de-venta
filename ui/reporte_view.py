import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from services.reporte_service import ReporteService

class ReporteView(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, reporte_service: ReporteService):
        super().__init__(parent, padding=15)
        self.reporte_service = reporte_service
        self._datos_actuales = []
        self._tipo_reporte_actual = "stock_bajo"
        self._construir_ui()
        self.cargar_datos()

    def _construir_ui(self) -> None:
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(header_frame, text="Reportes del Dominio y Estadísticas", style="Titulo.TLabel").pack(side="left")

        # Barra de control y filtros del reporte
        control_frame = ttk.LabelFrame(self, text=" Configuración del Reporte ", padding=10)
        control_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(control_frame, text="Seleccionar Reporte:").pack(side="left", padx=(0, 5))

        self.cbo_tipo = ttk.Combobox(control_frame, state="readonly", width=34)
        self.cbo_tipo["values"] = [
            "⚠️ Caso Problemático: Stock Bajo / Agotado (RF-8)",
            "🏆 Productos Más Vendidos"
        ]
        self.cbo_tipo.current(0)
        self.cbo_tipo.pack(side="left", padx=(0, 15))
        self.cbo_tipo.bind("<<ComboboxSelected>>", lambda e: self.cargar_datos())

        # Umbral para stock bajo
        self.lbl_umbral = ttk.Label(control_frame, text="Umbral stock ≤:")
        self.lbl_umbral.pack(side="left", padx=(0, 5))
        self.spn_umbral = ttk.Spinbox(control_frame, from_=0, to=100, width=5)
        self.spn_umbral.set(5)
        self.spn_umbral.pack(side="left", padx=(0, 15))
        self.spn_umbral.bind("<KeyRelease>", lambda e: self.cargar_datos())
        self.spn_umbral.bind("<<Increment>>", lambda e: self.after(50, self.cargar_datos))
        self.spn_umbral.bind("<<Decrement>>", lambda e: self.after(50, self.cargar_datos))

        btn_actualizar = ttk.Button(control_frame, text="🔄 Actualizar", command=self.cargar_datos)
        btn_actualizar.pack(side="left", padx=(0, 10))

        # Botón Extra de Exportar a CSV
        btn_csv = ttk.Button(control_frame, text="📥 Exportar Reporte a CSV (Extra A.6)", style="Success.TButton", command=self._exportar_csv)
        btn_csv.pack(side="right")

        # Tabla de visualización del reporte
        self.tabla_frame = ttk.LabelFrame(self, text=" Resultados del Reporte ", padding=10)
        self.tabla_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(self.tabla_frame, show="headings", selectmode="browse")
        self.tree.tag_configure("critico", foreground="#c0392b")
        self.tree.tag_configure("bajo", foreground="#d35400")

        sc_y = ttk.Scrollbar(self.tabla_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sc_y.set)

        self.tree.pack(side="left", fill="both", expand=True)
        sc_y.pack(side="right", fill="y")

        # Pie con conteo
        self.lbl_resumen = ttk.Label(self, text="Total de registros encontrados: 0", font=("Segoe UI", 9, "bold"), foreground="#495057")
        self.lbl_resumen.pack(anchor="w", pady=(8, 0))

    def cargar_datos(self) -> None:
        idx = self.cbo_tipo.current()

        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        if idx == 0:
            self._tipo_reporte_actual = "stock_bajo"
            self.lbl_umbral.pack(side="left", padx=(0, 5))
            self.spn_umbral.pack(side="left", padx=(0, 15))
            self._cargar_reporte_stock_bajo()
        else:
            self._tipo_reporte_actual = "mas_vendidos"
            self.lbl_umbral.pack_forget()
            self.spn_umbral.pack_forget()
            self._cargar_reporte_mas_vendidos()

    def _cargar_reporte_stock_bajo(self) -> None:
        try:
            umbral = int(self.spn_umbral.get())
        except ValueError:
            umbral = 5

        cols = ("codigo", "nombre", "categoria", "precio", "stock", "estado", "severidad")
        self.tree["columns"] = cols

        self.tree.heading("codigo", text="Código")
        self.tree.heading("nombre", text="Nombre del Producto")
        self.tree.heading("categoria", text="Categoría")
        self.tree.heading("precio", text="Precio ($)")
        self.tree.heading("stock", text="Stock Actual")
        self.tree.heading("estado", text="Estado")
        self.tree.heading("severidad", text="Nivel de Alerta")

        self.tree.column("codigo", width=100, anchor="center")
        self.tree.column("nombre", width=250, anchor="w")
        self.tree.column("categoria", width=180, anchor="w")
        self.tree.column("precio", width=90, anchor="e")
        self.tree.column("stock", width=90, anchor="center")
        self.tree.column("estado", width=90, anchor="center")
        self.tree.column("severidad", width=140, anchor="center")

        datos = self.reporte_service.obtener_stock_bajo(umbral=umbral)
        self._datos_actuales = datos

        for p in datos:
            estado_str = "Activo" if p["activo"] else "Inactivo"
            stock = p["stock"]
            if stock == 0:
                severidad = "🚨 Agotado (0)"
                tag = "critico"
            else:
                severidad = f"⚠️ Stock Bajo ({stock})"
                tag = "bajo"

            self.tree.insert("", "end", values=(
                p["codigo"],
                p["nombre"],
                p["categoria_nombre"],
                f"${p['precio']:,.2f}",
                stock,
                estado_str,
                severidad
            ), tags=(tag,))

        self.lbl_resumen.config(text=f"Total de productos en condición crítica o baja: {len(datos)} producto(s)")

    def _cargar_reporte_mas_vendidos(self) -> None:
        cols = ("codigo", "nombre", "categoria", "unidades", "total")
        self.tree["columns"] = cols

        self.tree.heading("codigo", text="Código")
        self.tree.heading("nombre", text="Nombre del Producto")
        self.tree.heading("categoria", text="Categoría")
        self.tree.heading("unidades", text="Unidades Vendidas")
        self.tree.heading("total", text="Total Recaudado ($)")

        self.tree.column("codigo", width=100, anchor="center")
        self.tree.column("nombre", width=260, anchor="w")
        self.tree.column("categoria", width=180, anchor="w")
        self.tree.column("unidades", width=130, anchor="center")
        self.tree.column("total", width=140, anchor="e")

        datos = self.reporte_service.obtener_mas_vendidos(limite=20)
        self._datos_actuales = datos

        for r in datos:
            self.tree.insert("", "end", values=(
                r["codigo"],
                r["nombre"],
                r["categoria_nombre"],
                r["total_vendido"],
                f"${r['total_recaudado']:,.2f}"
            ))

        self.lbl_resumen.config(text=f"Total de productos con ventas registradas: {len(datos)} producto(s)")

    def _exportar_csv(self) -> None:
        if not self._datos_actuales:
            messagebox.showwarning("Atención", "No hay datos en el reporte actual para exportar.", parent=self)
            return

        nombre_sugerido = f"reporte_{self._tipo_reporte_actual}.csv"
        ruta = filedialog.asksaveasfilename(
            parent=self,
            title="Guardar Reporte como CSV",
            initialfile=nombre_sugerido,
            defaultextension=".csv",
            filetypes=[("Archivos CSV (*.csv)", "*.csv"), ("Todos los archivos", "*.*")]
        )

        if not ruta:
            return

        try:
            if self._tipo_reporte_actual == "stock_bajo":
                campos = ["codigo", "nombre", "categoria_nombre", "precio", "stock", "activo"]
                encabezados = ["Código", "Nombre", "Categoría", "Precio", "Stock Actual", "Activo (1=Sí/0=No)"]
            else:
                campos = ["codigo", "nombre", "categoria_nombre", "total_vendido", "total_recaudado"]
                encabezados = ["Código", "Nombre", "Categoría", "Unidades Vendidas", "Total Recaudado ($)"]

            self.reporte_service.exportar_csv(self._datos_actuales, campos, encabezados, ruta)
            messagebox.showinfo("Exportación Exitosa", f"El archivo CSV se guardó correctamente en:\n{ruta}", parent=self)
        except Exception as e:
            messagebox.showerror("Error al Exportar", f"No se pudo guardar el archivo CSV: {e}", parent=self)
