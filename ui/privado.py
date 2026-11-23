"""Panel interno de un usuario (Alice o Bob): se revela solo con su modo activo."""
from tkinter import ttk

from . import adaptadores, tema


class PanelUsuario(ttk.LabelFrame):
    def __init__(self, master, nombre: str):
        super().__init__(master, text=f"Datos internos de {nombre}", padding=4)
        self.nombre = nombre
        self.lbl = ttk.Label(self, text="", font=tema.FUENTE_MONO, justify="left")
        self.lbl.pack(anchor="w")

    def actualizar(self, vista_publica: dict, vista_privada: dict | None):
        """vista_privada=None => p, q, φ y d enmascarados."""
        filas = adaptadores.filas_usuario(self.nombre, vista_publica, vista_privada)
        self.lbl.config(text="\n".join(f"{k} = {v}" for k, v in filas[1:]))
