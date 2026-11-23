"""Paleta, fuentes y estilos ttk (PENDIENTE: diseño final)."""
from tkinter import ttk

FUENTE_MONO = ("Consolas", 10)
FUENTE_UI = ("Segoe UI", 10)
FONDO = "#f4f4f4"
ROJO = "#c0392b"
VERDE = "#1e8449"
GRIS = "#666666"
AZUL = "#1f4e79"
CAMPO_ERROR = "#ffd6d6"


def aplicar(root):
    root.configure(bg=FONDO)
    estilo = ttk.Style(root)
    estilo.theme_use("clam")
    estilo.configure("Error.TEntry", fieldbackground=CAMPO_ERROR)
    estilo.configure("Ayuda.TLabel", foreground=GRIS)
    estilo.configure("Error.TLabel", foreground=ROJO)
