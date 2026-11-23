"""Formularios manuales (entradas siempre legibles, sin autocorrección)."""
import tkinter as tk
from tkinter import ttk

from . import tema, textos

# ErrorRSA.campo -> campos del formulario que se resaltan
CAMPOS_ERROR = {"n": ("p", "q"), "bloque": ("C",)}


class CampoTexto(ttk.Frame):
    def __init__(self, master, etiqueta, ayuda="", ancho=34):
        super().__init__(master)
        self.var = tk.StringVar()
        ttk.Label(self, text=etiqueta).grid(row=0, column=0, sticky="w")
        self.entry = ttk.Entry(self, textvariable=self.var, width=ancho, font=tema.FUENTE_MONO)
        self.entry.grid(row=0, column=1, sticky="ew", padx=4)
        self.lbl_error = ttk.Label(self, text=ayuda, style="Ayuda.TLabel", wraplength=380)
        self.lbl_error.grid(row=1, column=0, columnspan=2, sticky="w")
        self._ayuda = ayuda
        self.columnconfigure(1, weight=1)

    def valor(self):
        return self.var.get()      # sin modificar

    def set(self, texto):
        self.var.set(texto)

    def set_error(self, msg):
        self.entry.config(style="Error.TEntry")
        self.lbl_error.config(text=msg, style="Error.TLabel")

    def limpiar_error(self):
        self.entry.config(style="TEntry")
        self.lbl_error.config(text=self._ayuda, style="Ayuda.TLabel")


class Salida(ttk.Frame):
    """Salida de solo lectura, copiable."""

    def __init__(self, master, etiqueta, ancho=34):
        super().__init__(master)
        self.var = tk.StringVar()
        ttk.Label(self, text=etiqueta).grid(row=0, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.var, state="readonly", width=ancho,
                  font=tema.FUENTE_MONO).grid(row=0, column=1, sticky="ew", padx=4)
        self.columnconfigure(1, weight=1)

    def set(self, texto):
        self.var.set(texto)


class _FormularioBase(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=6)
        self.campos: dict[str, CampoTexto] = {}
        self.lbl_msg = ttk.Label(self, text="", style="Error.TLabel", wraplength=520)

    def _agregar(self, clave, etiqueta, ayuda=""):
        campo = CampoTexto(self, etiqueta, ayuda)
        self.campos[clave] = campo
        return campo

    def datos(self):
        return {k: c.valor() for k, c in self.campos.items()}

    def limpiar_errores(self):
        for c in self.campos.values():
            c.limpiar_error()
        self.lbl_msg.config(text="")

    def mostrar_error(self, err):
        self.limpiar_errores()
        self.lbl_msg.config(text=err.mensaje)
        for clave in CAMPOS_ERROR.get(err.campo, (err.campo,)):
            if clave in self.campos:
                self.campos[clave].set_error(err.mensaje)


class FormularioEncriptar(_FormularioBase):
    def __init__(self, master, al_ejecutar):
        super().__init__(master)
        self._agregar("M", textos.ETIQUETAS["M"], textos.AYUDA_M).grid(row=0, column=0, columnspan=2, sticky="ew")
        self._agregar("p", textos.ETIQUETAS["p"]).grid(row=1, column=0, sticky="ew")
        self._agregar("q", textos.ETIQUETAS["q"]).grid(row=1, column=1, sticky="ew")
        self._agregar("e", textos.ETIQUETAS["e"]).grid(row=2, column=0, sticky="ew")
        ttk.Button(self, text="Encriptar",
                   command=lambda: al_ejecutar(self.datos())).grid(row=2, column=1, sticky="e")
        self.lbl_msg.grid(row=3, column=0, columnspan=2, sticky="w")
        self.s_C = Salida(self, "C")
        self.s_L = Salida(self, "L")
        self.s_llave = Salida(self, "(e, n)")
        self.s_C.grid(row=4, column=0, columnspan=2, sticky="ew")
        self.s_L.grid(row=5, column=0, sticky="ew")
        self.s_llave.grid(row=5, column=1, sticky="ew")
        self.columnconfigure((0, 1), weight=1)

    def mostrar_resultado(self, res):
        self.limpiar_errores()
        self.s_C.set(res.C)
        self.s_L.set(str(res.L))
        self.s_llave.set(f"({res.llave_publica[0]}, {res.llave_publica[1]})")

    def limpiar_salidas(self):
        for s in (self.s_C, self.s_L, self.s_llave):
            s.set("")


class FormularioDesencriptar(_FormularioBase):
    def __init__(self, master, al_ejecutar):
        super().__init__(master)
        self._agregar("C", textos.ETIQUETAS["C"], textos.AYUDA_C).grid(row=0, column=0, columnspan=2, sticky="ew")
        self._agregar("L", textos.ETIQUETAS["L"], textos.AYUDA_L).grid(row=1, column=0, sticky="ew")
        self._agregar("e", textos.ETIQUETAS["e"]).grid(row=1, column=1, sticky="ew")
        self._agregar("p", textos.ETIQUETAS["p"]).grid(row=2, column=0, sticky="ew")
        self._agregar("q", textos.ETIQUETAS["q"]).grid(row=2, column=1, sticky="ew")
        ttk.Button(self, text="Desencriptar",
                   command=lambda: al_ejecutar(self.datos())).grid(row=3, column=1, sticky="e")
        self.lbl_msg.grid(row=4, column=0, columnspan=2, sticky="w")
        self.s_d = Salida(self, "d")
        self.s_M = Salida(self, "M")
        self.s_Mq = Salida(self, "M entre comillas")
        self.s_d.grid(row=5, column=0, sticky="ew")
        self.s_M.grid(row=6, column=0, columnspan=2, sticky="ew")
        self.s_Mq.grid(row=7, column=0, columnspan=2, sticky="ew")
        self.columnconfigure((0, 1), weight=1)

    def autocompletar(self, C, L, p=None, q=None, e=None):
        """Llena C y L (siguen editables para probar errores)."""
        self.campos["C"].set(C)
        self.campos["L"].set(str(L))
        for clave, valor in (("p", p), ("q", q), ("e", e)):
            if valor is not None:
                self.campos[clave].set(str(valor))

    def mostrar_resultado(self, res):
        self.limpiar_errores()
        self.s_d.set(str(res.d))
        self.s_M.set(res.M)
        self.s_Mq.set(f'"{res.M}"')

    def limpiar_salidas(self):
        for s in (self.s_d, self.s_M, self.s_Mq):
            s.set("")


class FormularioLlaves(_FormularioBase):
    def __init__(self, master, al_ejecutar):
        super().__init__(master)
        fila = ttk.Frame(self)
        fila.grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(fila, text="Usuario").pack(side="left")
        self.var_usuario = tk.StringVar(value="Alice")
        ttk.Combobox(fila, textvariable=self.var_usuario, values=("Alice", "Bob"),
                     state="readonly", width=8).pack(side="left", padx=4)
        self._agregar("p", textos.ETIQUETAS["p"]).grid(row=1, column=0, sticky="ew")
        self._agregar("q", textos.ETIQUETAS["q"]).grid(row=1, column=1, sticky="ew")
        self._agregar("e", textos.ETIQUETAS["e"]).grid(row=2, column=0, sticky="ew")
        ttk.Button(self, text="Actualizar llaves",
                   command=lambda: al_ejecutar(self.datos())).grid(row=2, column=1, sticky="e")
        self.lbl_msg.grid(row=3, column=0, columnspan=2, sticky="w")
        self.lbl_ok = ttk.Label(self, text="")
        self.lbl_ok.grid(row=4, column=0, columnspan=2, sticky="w")
        self.columnconfigure((0, 1), weight=1)

    def datos(self):
        d = super().datos()
        d["usuario"] = self.var_usuario.get()
        return d

    def mostrar_confirmacion(self, texto):
        self.limpiar_errores()
        self.lbl_ok.config(text=texto)


class Formularios(ttk.Notebook):
    def __init__(self, master, al_encriptar, al_desencriptar, al_actualizar_llaves):
        super().__init__(master)
        self.encriptar = FormularioEncriptar(self, al_encriptar)
        self.desencriptar = FormularioDesencriptar(self, al_desencriptar)
        self.llaves = FormularioLlaves(self, al_actualizar_llaves)
        self.add(self.encriptar, text="Encriptar")
        self.add(self.desencriptar, text="Desencriptar")
        self.add(self.llaves, text="Llaves (chat)")
