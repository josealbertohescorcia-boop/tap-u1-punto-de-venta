# Guía de Preparación para la Defensa del Proyecto
**Tópicos Avanzados de Programación · Unidad 1**
**Opción 2: Inventario / Mini Punto de Venta**

Esta guía contiene las respuestas técnicas detalladas a las preguntas oficiales de defensa estipuladas en la rúbrica del proyecto (Página 9 del enunciado).

---

### 1. ¿Dónde vive la regla de negocio y por qué no está en el botón?

**Respuesta:**
Las reglas de negocio viven exclusivamente en la capa de servicios (`services/`), específicamente en:
- `services/venta_service.py` (verificación de stock suficiente, validación de productos activos, cálculo de importes y coordinación transaccional de venta con descuento de existencias).
- `services/producto_service.py` (validación de precio > 0, stock >= 0, unicidad de código, regla de no eliminar productos con historial de ventas).
- `services/categoria_service.py` (validación de nombres únicos y regla de no eliminar categorías con productos asociados).
- `services/auth_service.py` (hashing SHA-256 de contraseñas y restricción de acceso para usuarios inactivos).

**Por qué no está en el botón:**
En la arquitectura en capas (Separación de Responsabilidades / *Separation of Concerns*):
- Los botones de la interfaz gráfica (`ui/`) pertenecen únicamente a la capa de presentación. Su única responsabilidad es capturar eventos del usuario, recolectar datos de las entradas y delegar la ejecución a los servicios correspondientes.
- Si colocáramos la lógica o consultas SQL dentro del manejador del botón (`command=...`), acoplaríamos la lógica del negocio con la librería gráfica Tkinter. Esto impediría reutilizar el código (por ejemplo, si quisiéramos crear una versión de consola, una API web o pruebas unitarias automatizadas) y dificultaría el mantenimiento y las pruebas del software.

---

### 2. Muestre el JOIN y explique cada tabla

**Respuesta:**
La consulta relacional con `JOIN` vive en `repositories/venta_repository.py` y se muestra visualmente en la pestaña **"Historial (JOIN)"** mediante el botón *"Ver Consulta SQL con JOIN Completo (RF-7)"*.

```sql
SELECT 
    dv.id AS detalle_id,
    v.id AS folio_venta,
    v.fecha AS fecha_venta,
    u.username AS vendedor,
    p.codigo AS codigo_producto,
    p.nombre AS nombre_producto,
    c.nombre AS categoria,
    dv.cantidad,
    dv.precio_unitario,
    dv.subtotal
FROM detalle_venta dv
INNER JOIN ventas v ON dv.venta_id = v.id
INNER JOIN productos p ON dv.producto_id = p.id
INNER JOIN categorias c ON p.categoria_id = c.id
INNER JOIN usuarios_sistema u ON v.usuario_id = u.id
ORDER BY v.id DESC, dv.id ASC;
```

**Explicación de cada tabla involucrada:**
1. **`detalle_venta` (dv)**: Tabla detalle del movimiento. Almacena cada renglón vendido (cantidad, precio unitario congelado y subtotal). Actúa como tabla pivote del `JOIN`.
2. **`ventas` (v)**: Tabla maestra del movimiento. Contiene el folio general (`v.id`), la fecha y hora de la transacción, y la llave foránea del usuario que cobró. Se une mediante `dv.venta_id = v.id`.
3. **`productos` (p)**: Catálogo maestro A. Contiene el código, nombre y existencias. Se une mediante `dv.producto_id = p.id`.
4. **`categorias` (c)**: Catálogo maestro B. Provee el nombre de la categoría a la que pertenece el producto. Se une mediante `p.categoria_id = c.id`.
5. **`usuarios_sistema` (u)**: Usuarios del sistema con acceso. Provee el nombre de usuario (`username`) del vendedor responsable. Se une mediante `v.usuario_id = u.id`.

---

### 3. ¿Qué pasa si intentan un movimiento que viola stock, cupo u horario?

**Respuesta:**
1. **En la interfaz (`ui/venta_view.py`)**: Al intentar agregar una cantidad superior al stock disponible de un producto, el sistema detecta de inmediato la insuficiencia y muestra una advertencia al usuario (`messagebox.showwarning`), impidiendo agregar existencias inexistentes al carrito.
2. **En el servicio (`services/venta_service.py`)**: Antes de interactuar con la base de datos, valida que ningún producto solicitado supere el stock actual en inventario.
3. **En la transacción atómica de SQLite (`repositories/venta_repository.py`)**:
   - Todo el proceso de venta ocurre dentro de una transacción (`BEGIN TRANSACTION`).
   - Si por concurrencia el stock no es suficiente, se lanza una excepción `ValueError`.
   - El bloque `except Exception:` ejecuta de inmediato un `conn.rollback()`, garantizando atomicidad: **o se descuenta el inventario y se guardan todos los renglones, o no se guarda absolutamente nada**. La base de datos nunca queda en un estado corrupto o inconsistente.

---

### 4. ¿Por qué desactivar en lugar de DELETE?

**Respuesta:**
Por **integridad referencial e integridad histórica**:
- Si un producto o categoría ya tiene registros asociados en tablas hijas (como `detalle_venta`), ejecutar un `DELETE` físico violaría la restricción de llave foránea (`ON DELETE RESTRICT`) o, si se usara borrado en cascada, destruiría el historial contable de las ventas pasadas (quedarían ventas huérfanas o se perdería el registro de qué se vendió y a qué precio).
- Mediante el **borrado lógico (soft delete)** usando el campo `activo = 0`:
  1. Se preserva el 100% de la trazabilidad y auditoría histórica de folios pasados.
  2. El registro queda oculto o bloqueado para nuevas transacciones operativas.
  3. Puede ser reactivado en cualquier momento si vuelve a haber disponibilidad.

---

### 5. Si mañana cambian SQLite por PostgreSQL, ¿qué archivos tocarían?

**Respuesta:**
Gracias a la arquitectura en capas implementada, **solo se modificarían los archivos de la capa de acceso a datos**:
1. `db/connection.py`: Reemplazar la conexión de `sqlite3.connect()` por la librería de PostgreSQL (por ejemplo `psycopg2` o `asyncpg`), configurando host, puerto, usuario, contraseña y base de datos.
2. `db/database.py`: Adaptar la sintaxis de creación de tablas (por ejemplo `SERIAL` o `BIGSERIAL` en lugar de `INTEGER PRIMARY KEY AUTOINCREMENT`).
3. `repositories/*.py`: Ajustar los marcadores de parámetros de consultas (cambiar `?` por `%s` según el driver de PostgreSQL) y el método para obtener el último ID insertado (`RETURNING id` en lugar de `cursor.lastrowid`).

**Archivos que NO se tocarían en absoluto:**
- **Ningún archivo de `ui/`**: Las vistas no contienen SQL ni conocen qué motor de base de datos existe.
- **Ningún archivo de `services/`**: Las reglas del negocio (descuento de stock, validaciones, roles, totales) son exactamente las mismas.
- **Ningún archivo de `models/`**: Los objetos de dominio (`Producto`, `Categoria`, `Venta`, etc.) son clases de Python independientes del motor.
