"""Panel de detalle del proceso (guarda el último resultado; nunca relee el Treeview)."""
import tkinter as tk
from tkinter import ttk

from . import adaptadores, tema, textos


class _Detalle(ttk.Frame):
    COLUMNAS: tuple = ()
    ANCHOS: tuple = ()

    def __init__(self, master):
        super().__init__(master, padding=4)
        self._ultimo = None
        self._error = None
        self._privado_error = True
        self.txt_params = tk.Text(self, height=4, font=tema.FUENTE_MONO, state="disabled", wrap="word")
        self.lbl_aviso = ttk.Label(self, text="", style="Ayuda.TLabel", wraplength=700)
        self.tabla = ttk.Treeview(self, columns=self.COLUMNAS, show="headings", height=5)
        for col, ancho in zip(self.COLUMNAS, self.ANCHOS):
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho, anchor="center", stretch=False)
        barra_x = ttk.Scrollbar(self, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(xscrollcommand=barra_x.set)
        self.txt_log = tk.Text(self, height=6, font=tema.FUENTE_MONO, state="disabled", wrap="word")
        self.txt_log.tag_configure("ok", foreground=tema.VERDE)
        self.txt_log.tag_configure("error", foreground=tema.ROJO)
        self.txt_log.tag_configure("info", foreground=tema.AZUL)
        self.txt_params.grid(row=0, column=0, sticky="ew")
        self.lbl_aviso.grid(row=1, column=0, sticky="ew")
        self.tabla.grid(row=2, column=0, sticky="nsew")
        barra_x.grid(row=3, column=0, sticky="ew")
        self.txt_log.grid(row=4, column=0, sticky="nsew")
        self.rowconfigure(2, weight=2)
        self.rowconfigure(4, weight=1)
        self.columnconfigure(0, weight=1)

    # --- API pública ---
    def mostrar(self, res, mostrar_proceso: bool, mostrar_privado: bool):
        self._ultimo = res
        self._error = None
        self.refrescar(mostrar_proceso, mostrar_privado)

    def mostrar_error(self, err, mostrar_privado: bool = True):
        self._ultimo = None
        self._error = err
        self._privado_error = mostrar_privado
        self.refrescar(True, mostrar_privado)

    def limpiar(self):
        self._ultimo = None
        self._error = None
        self._borrar()

    def refrescar(self, mostrar_proceso: bool, mostrar_privado: bool):
        self._borrar()
        if self._error is not None:
            self._escribir(self.txt_log, adaptadores.lineas_pasos(self._error.pasos, self._privado_error))
            return
        res = self._ultimo
        if res is None:
            return
        if not mostrar_proceso:
            filas = adaptadores.filas_publicas(res.params, res.C, res.L)
            self._escribir(self.txt_params, [("   ".join(f"{k} = {v}" for k, v in filas), "info")])
            self.lbl_aviso.config(text=textos.AVISO_REAL)
            return
        filas = adaptadores.filas_parametros(res.params, self._d(res), mostrar_privado)
        filas += [("C", res.C), ("L", str(res.L))] + self._relleno(res)
        self._escribir(self.txt_params, [("   ".join(f"{k} = {v}" for k, v in filas), "info")])
        for fila in self._filas(res):
            self.tabla.insert("", "end", values=fila)
        self._escribir(self.txt_log, adaptadores.lineas_pasos(res.pasos, mostrar_privado))

    # --- internos ---
    def _d(self, res):
        return None

    def _relleno(self, res):
        return []

    def _filas(self, res):
        return []

    def _borrar(self):
        self.lbl_aviso.config(text="")
        self.tabla.delete(*self.tabla.get_children())
        for t in (self.txt_params, self.txt_log):
            t.config(state="normal")
            t.delete("1.0", "end")
            t.config(state="disabled")

    @staticmethod
    def _escribir(widget, lineas):
        widget.config(state="normal")
        for texto, tag in lineas:
            widget.insert("end", texto + "\n", tag)
        widget.config(state="disabled")


class DetalleEncriptacion(_Detalle):
    COLUMNAS = adaptadores.COLUMNAS_ENC
    ANCHOS = (30, 60, 100, 80, 80, 80, 80, 90)

    def _relleno(self, res):
        return adaptadores.filas_relleno_enc(res)

    def _filas(self, res):
        return adaptadores.filas_encriptacion(res)


class DetalleDesencriptacion(_Detalle):
    COLUMNAS = adaptadores.COLUMNAS_DES
    ANCHOS = (30, 70, 90, 80, 60, 60, 60, 70, 140)

    def _d(self, res):
        return res.d

    def _relleno(self, res):
        return adaptadores.filas_relleno_des(res)

    def _filas(self, res):
        return adaptadores.filas_desencriptacion(res)


class PanelDetalle(ttk.Notebook):
    def __init__(self, master):
        super().__init__(master)
        self.enc = DetalleEncriptacion(self)
        self.des = DetalleDesencriptacion(self)
        self.add(self.enc, text="Detalle de encriptación")
        self.add(self.des, text="Detalle de desencriptación")
