# Documentación de Pantallas y Flujos de Usuario
**Sistema de Mini Punto de Venta e Inventario**

La aplicación está construida sobre una arquitectura modular con componentes de interfaz en `ui/`, estilizados mediante `ttk` y organizados en una ventana principal con menús nativos y panel de pestañas (`Notebook`).

---

## 1. Pantalla de Inicio de Sesión (`LoginWindow`)
* **Archivo**: `ui/login_window.py`
* **Acceso**: Primera pantalla mostrada al iniciar el ejecutable o script.
* **Elementos**:
  * Campos de entrada: `Usuario` y `Contraseña` (con enmascaramiento de caracteres `•`).
  * Botón interactivo: `Iniciar Sesión` (o presionar la tecla `Enter`).
  * Indicador de tarjetas con las credenciales por defecto para el evaluador:
    * Administrador: `admin` / `admin123`
    * Operador: `operador` / `operador123`
* **Validaciones**:
  * Campos vacíos: Muestra advertencia clara.
  * Credenciales erróneas: Notifica fallo sin revelar detalles sensibles.
  * Usuario inactivo: Bloquea el acceso indicando que la cuenta está desactivada.

---

## 2. Pantalla Principal (`MainWindow`)
* **Archivo**: `ui/main_window.py`
* **Elementos**:
  * **Barra de Menú Superior**: Acceso directo a `Archivo` (Cerrar sesión, Salir), `Módulos`, `Administración` y `Ayuda` (Acerca del proyecto).
  * **Barra de Identificación**: Muestra en tiempo real el nombre del usuario logueado, su rol (`ADMINISTRADOR` u `OPERADOR`) y botón de cerrar sesión.
  * **Panel de Pestañas**:
    1. `🛒 Registrar Venta` (Punto de Venta)
    2. `📦 Catálogo Productos` (Entidad A)
    3. `🏷️ Categorías` (Entidad B)
    4. `📜 Historial (JOIN)` (Movimientos y consultas relacionales)
    5. `📊 Reportes y Alertas` (Stock bajo y más vendidos)
    6. `👥 Personal / Usuarios` (Gestión de usuarios del sistema, **exclusiva del administrador**).
  * **Barra de Estado Inferior**: Indica el estado de la conexión SQLite3 y la fecha del sistema.

---

## 3. Módulo de Punto de Venta (`VentaView`)
* **Archivo**: `ui/venta_view.py`
* **Propósito**: Ejecución del proceso de negocio principal (Movimiento).
* **Flujo**:
  1. El usuario selecciona productos del catálogo disponible (panel izquierdo).
  2. Ajusta la cantidad deseada mediante el selector numérico y pulsa `➕ Agregar al Carrito`.
  3. El panel derecho (carrito) calcula dinámicamente el precio unitario y subtotal.
  4. El panel de cobro totaliza el importe acumulado en tiempo real.
  5. Al pulsar `💳 CONFIRMAR Y REGISTRAR VENTA`, el sistema solicita confirmación mediante un cuadro de diálogo (`messagebox.askyesno`), realiza la transacción atómica en SQLite, descuenta el stock de las existencias y emite un folio único de venta.
  6. Todas las demás pantallas del sistema actualizan sus existencias de forma sincronizada.

---

## 4. Módulo de Productos (`ProductoView`)
* **Archivo**: `ui/producto_view.py`
* **Propósito**: CRUD completo de la Entidad A.
* **Funciones**:
  * **Buscador en tiempo real**: Filtra instantáneamente por código, nombre o categoría.
  * **Filtros combinados**: Selector por categoría y casilla para mostrar u ocultar inactivos.
  * **Alertas visuales de existencias**:
    * Agotado: `🚨 Agotado (0)` (texto en rojo).
    * Bajo: `⚠️ Stock Bajo (≤ 5)` (texto en naranja).
    * Normal: `✓ Normal`.
  * **Operaciones**:
    * `➕ Nuevo Producto`: Modal con validación de código único, precio > 0 y stock >= 0.
    * `✏️ Editar`: Modal para modificar datos o existencias.
    * `🔄 Activar / Desactivar`: Desactivación lógica (*soft delete*) con confirmación.
    * `🗑️ Eliminar`: Intento de borrado físico. Si el producto ya cuenta con ventas registradas en el historial, el sistema rechaza la eliminación protegiendo la integridad referencial y solicita desactivarlo.

---

## 5. Módulo de Categorías (`CategoriaView`)
* **Archivo**: `ui/categoria_view.py`
* **Propósito**: CRUD completo de la Entidad B.
* **Funciones**:
  * Alta, edición, desactivación/activación y eliminación.
  * Protección de integridad: No permite eliminar ni desactivar una categoría si contiene productos activos vinculados.

---

## 6. Módulo de Historial y Consultas Relacionales (`VentaHistorialView`)
* **Archivo**: `ui/venta_historial_view.py`
* **Propósito**: Consulta de ventas realizadas con demostración visual de `JOIN` relacional (Cumplimiento de **RF-7**).
* **Vistas disponibles**:
  1. **Vista Maestro-Detalle**: Al seleccionar una venta de la tabla superior, la tabla inferior carga inmediatamente los renglones correspondientes uniendo `detalle_venta` con `productos`.
  2. **Vista con JOIN Completo**: Botón interactivo que despliega una cuadrícula que ejecuta la consulta de cinco tablas (`detalle_venta ⋈ ventas ⋈ productos ⋈ categorias ⋈ usuarios_sistema`).

---

## 7. Módulo de Reportes y Exportación CSV (`ReporteView`)
* **Archivo**: `ui/reporte_view.py`
* **Propósito**: Análisis del caso problemático del dominio (Cumplimiento de **RF-8** y Extra opcional **A.6**).
* **Reportes integrados**:
  1. `⚠️ Caso Problemático: Stock Bajo / Agotado`: Lista todos los productos cuyas existencias sean menores o iguales a un umbral configurable (por defecto 5 unidades).
  2. `🏆 Productos Más Vendidos`: Acumula unidades vendidas e importe generado por artículo.
* **Extra Funcional**: Botón `📥 Exportar Reporte a CSV` que permite al usuario guardar el reporte en un archivo `.csv` compatible con Microsoft Excel mediante codificación UTF-8 con BOM.
