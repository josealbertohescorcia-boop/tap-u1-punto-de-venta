import tkinter as tk
from tkinter import ttk

# Paleta de colores profesional
COLOR_FONDO = "#f4f6f9"
COLOR_TARJETA = "#ffffff"
COLOR_PRIMARIO = "#1f4b82"       # Azul corporativo
COLOR_PRIMARIO_HOVER = "#173a66"
COLOR_SECUNDARIO = "#495057"
COLOR_EXITO = "#27ae60"          # Verde acción
COLOR_PELIGRO = "#c0392b"        # Rojo alerta/cancelar
COLOR_ADVERTENCIA = "#d35400"    # Naranja stock bajo
COLOR_TEXTO = "#212529"
COLOR_TEXTO_MUTED = "#6c757d"
COLOR_BORDE = "#dee2e6"

def aplicar_estilos(root: tk.Tk) -> ttk.Style:
    """Configura los estilos globales de ttk para dar una apariencia moderna y limpia."""
    estilo = ttk.Style(root)

    # Intentar usar temas modernos si están disponibles
    temas_disponibles = estilo.theme_names()
    if "clam" in temas_disponibles:
        estilo.theme_use("clam")

    # Configuración base
    estilo.configure(".",
                     background=COLOR_FONDO,
                     foreground=COLOR_TEXTO,
                     font=("Segoe UI", 10))

    # Notebook (pestañas)
    estilo.configure("TNotebook", background=COLOR_FONDO, borderwidth=0)
    estilo.configure("TNotebook.Tab",
                     background="#e9ecef",
                     foreground=COLOR_TEXTO,
                     padding=(14, 8),
                     font=("Segoe UI", 10, "bold"))
    estilo.map("TNotebook.Tab",
               background=[("selected", COLOR_PRIMARIO), ("active", "#d0d7de")],
               foreground=[("selected", "#ffffff"), ("active", COLOR_TEXTO)])

    # Frames
    estilo.configure("TFrame", background=COLOR_FONDO)
    estilo.configure("Card.TFrame", background=COLOR_TARJETA, relief="flat", borderwidth=1)

    # Labels
    estilo.configure("TLabel", background=COLOR_FONDO, foreground=COLOR_TEXTO)
    estilo.configure("Card.TLabel", background=COLOR_TARJETA, foreground=COLOR_TEXTO)
    estilo.configure("Titulo.TLabel", font=("Segoe UI", 14, "bold"), foreground=COLOR_PRIMARIO, background=COLOR_FONDO)
    estilo.configure("CardTitulo.TLabel", font=("Segoe UI", 12, "bold"), foreground=COLOR_PRIMARIO, background=COLOR_TARJETA)
    estilo.configure("Muted.TLabel", font=("Segoe UI", 9), foreground=COLOR_TEXTO_MUTED, background=COLOR_FONDO)

    # Botones generales
    estilo.configure("TButton",
                     font=("Segoe UI", 9, "bold"),
                     padding=(10, 5),
                     background="#e9ecef",
                     foreground=COLOR_TEXTO)
    estilo.map("TButton",
               background=[("active", "#dbe2e8"), ("disabled", "#f1f3f5")],
               foreground=[("disabled", "#adb5bd")])

    # Botón Primario
    estilo.configure("Primary.TButton",
                     font=("Segoe UI", 9, "bold"),
                     padding=(12, 6),
                     background=COLOR_PRIMARIO,
                     foreground="#ffffff")
    estilo.map("Primary.TButton",
               background=[("active", COLOR_PRIMARIO_HOVER), ("disabled", "#a0b5cf")],
               foreground=[("disabled", "#ffffff")])

    # Botón Éxito
    estilo.configure("Success.TButton",
                     font=("Segoe UI", 9, "bold"),
                     padding=(12, 6),
                     background=COLOR_EXITO,
                     foreground="#ffffff")
    estilo.map("Success.TButton",
               background=[("active", "#1e8449"), ("disabled", "#a3e4d7")],
               foreground=[("disabled", "#ffffff")])

    # Botón Peligro
    estilo.configure("Danger.TButton",
                     font=("Segoe UI", 9, "bold"),
                     padding=(10, 5),
                     background=COLOR_PELIGRO,
                     foreground="#ffffff")
    estilo.map("Danger.TButton",
               background=[("active", "#962d22"), ("disabled", "#f5b7b1")],
               foreground=[("disabled", "#ffffff")])

    # Entradas de texto y combos
    estilo.configure("TEntry", fieldbackground="#ffffff", padding=5)
    estilo.configure("TCombobox", fieldbackground="#ffffff", padding=5)

    # Treeview (Tablas de datos)
    estilo.configure("Treeview",
                     background="#ffffff",
                     fieldbackground="#ffffff",
                     foreground=COLOR_TEXTO,
                     rowheight=26,
                     font=("Segoe UI", 9))
    estilo.configure("Treeview.Heading",
                     background="#e2e8f0",
                     foreground="#1e293b",
                     font=("Segoe UI", 9, "bold"),
                     padding=5)
    estilo.map("Treeview",
               background=[("selected", "#cfe2ff")],
               foreground=[("selected", "#084298")])

    # LabelFrames
    estilo.configure("TLabelframe", background=COLOR_FONDO, padding=10)
    estilo.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"), foreground=COLOR_PRIMARIO, background=COLOR_FONDO)

    return estilo
