"""Controlador central de la aplicación."""
import tkinter as tk
import traceback
from tkinter import messagebox, ttk

from . import tema, textos
from .canal import CanalFrame
from .detalle import PanelDetalle
from .formularios import Formularios
from .modos import BarraModos, EstadoModos
from .privado import PanelUsuario
from .servicio import ErrorRSA, UsuarioRSA, USUARIOS_DEMO, desencriptar, encriptar
from .telefono import TelefonoFrame


class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(textos.TITULO_VENTANA)
        self.geometry("1280x760")
        self.minsize(1000, 640)
        tema.aplicar(self)

        self.usuarios = {n: UsuarioRSA(n, *USUARIOS_DEMO[n]) for n in ("Alice", "Bob")}
        self.estado = EstadoModos()
        self.ultimo_emisor = None
        self.ultimo_receptor = None
        self.ocupado = False
        self._manual = {"enc": False, "des": False}
        self.var_status = tk.StringVar(value=textos.STATUS["listo"])

        self.barra = BarraModos(self, self.estado, self._aplicar_modos)
        self.barra.grid(row=0, column=0, columnspan=3, sticky="ew")

        self.tel = {
            "Alice": TelefonoFrame(self, "Alice", "Bob", self._enviar),
            "Bob": TelefonoFrame(self, "Bob", "Alice", self._enviar),
        }
        self.tel["Alice"].grid(row=1, column=0, sticky="nsew")
        self.tel["Bob"].grid(row=1, column=2, sticky="nsew")
        self.privado = {n: PanelUsuario(self, n) for n in ("Alice", "Bob")}
        self.privado["Alice"].grid(row=2, column=0, sticky="ew", padx=4, pady=4)
        self.privado["Bob"].grid(row=2, column=2, sticky="ew", padx=4, pady=4)

        centro = ttk.Frame(self)
        centro.grid(row=1, column=1, rowspan=2, sticky="nsew")
        ttk.Label(centro, textvariable=self.var_status, wraplength=560).grid(row=0, column=0, sticky="ew")
        self.canal = CanalFrame(centro)
        self.canal.grid(row=1, column=0, sticky="ew")
        self.formularios = Formularios(centro, self._encriptar_manual, self._desencriptar_manual,
                                       self._actualizar_llaves_usuario)
        self.formularios.grid(row=2, column=0, sticky="ew")
        self.detalle = PanelDetalle(centro)
        self.detalle.grid(row=3, column=0, sticky="nsew")
        self.detalle_enc = self.detalle.enc
        self.detalle_des = self.detalle.des
        centro.rowconfigure(3, weight=1)
        centro.columnconfigure(0, weight=1)

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=5)
        self.columnconfigure(2, weight=3)
        self.rowconfigure(1, weight=1)
        self._refrescar_privados()

    def report_callback_exception(self, exc, val, tb):
        traceback.print_exception(exc, val, tb)
        messagebox.showerror("Error inesperado", f"{exc.__name__}: {val}")

    # ---------- chat ----------
    def _enviar(self, origen, texto):
        if self.ocupado:
            return
        destino = "Bob" if origen == "Alice" else "Alice"
        self.tel[origen].limpiar_error()
        try:
            res = self.usuarios[destino].cifrar_con_su_llave_publica(texto)
        except ErrorRSA as err:
            self.tel[origen].mostrar_error(err.mensaje)
            self._manual["enc"] = False
            self.detalle_enc.mostrar_error(err, mostrar_privado=False)
            self.detalle.select(self.detalle_enc)
            self.var_status.set(textos.STATUS["error"].format(mensaje=err.mensaje))
            return
        self.ocupado = True
        for t in self.tel.values():
            t.set_bloqueado(True)
        self.ultimo_emisor, self.ultimo_receptor = origen, destino
        self.tel[origen].agregar_burbuja(texto, propio=True)
        self.tel[origen].limpiar_entrada()
        self._manual["enc"] = False
        self.detalle_enc.mostrar(res, mostrar_proceso=self.estado.puede_ver_emisor(origen),
                                 mostrar_privado=self.estado.puede_ver_receptor(destino))
        self.detalle.select(self.detalle_enc)
        e, n = self.usuarios[destino].llave_publica
        fmt = {"origen": origen, "destino": destino, "e": e, "n": n}

        def enviar_sobre():
            self.var_status.set(textos.STATUS["sobre"])
            self.canal.enviar_sobre(res.C, destino,
                                    lambda: self._al_llegar(origen, destino, res))

        def mostrar_llave():
            self.canal.mostrar_llave(e, n)
            self.var_status.set(textos.STATUS["cifrando"].format(**fmt))
            self.after(400, enviar_sobre)

        self.var_status.set(textos.STATUS["llave"].format(**fmt))
        self.canal.mostrar_pasos_llave(
            [textos.STATUS["llave"].format(**fmt), textos.STATUS["llave_ok"].format(**fmt)],
            mostrar_llave)

    def _al_llegar(self, origen, destino, res):
        try:
            form_des = self.formularios.desencriptar
            form_des.limpiar_errores()
            form_des.limpiar_salidas()
            form_des.autocompletar(res.C, res.L)
            self.var_status.set(textos.STATUS["descifrando"].format(destino=destino))
            try:
                rx = self.usuarios[destino].descifrar(res.C, res.L)
            except ErrorRSA as err:
                self.tel[destino].mostrar_error(err.mensaje)
                self._manual["des"] = False
                self.detalle_des.mostrar_error(err, mostrar_privado=self.estado.puede_ver_receptor(destino))
                self.var_status.set(textos.STATUS["error"].format(mensaje=err.mensaje))
                return
            self.tel[destino].agregar_burbuja(rx.M, propio=False)
            self._manual["des"] = False
            visible = self.estado.puede_ver_receptor(destino)
            self.detalle_des.mostrar(rx, mostrar_proceso=visible, mostrar_privado=visible)
            self.var_status.set(textos.STATUS["entregado"].format(destino=destino))
        finally:
            self.ocupado = False
            for t in self.tel.values():
                t.set_bloqueado(False)

    def _aplicar_modos(self, estado):
        """Refresca los paneles de detalle sin recalcular nada."""
        self._refrescar_privados()
        if self._manual["enc"]:
            self.detalle_enc.refrescar(True, True)
        elif self.ultimo_emisor is not None:
            self.detalle_enc.refrescar(estado.puede_ver_emisor(self.ultimo_emisor),
                                       estado.puede_ver_receptor(self.ultimo_receptor))
        if self._manual["des"]:
            self.detalle_des.refrescar(True, True)
        elif self.ultimo_receptor is not None:
            visible = estado.puede_ver_receptor(self.ultimo_receptor)
            self.detalle_des.refrescar(visible, visible)

    def _refrescar_privados(self):
        """Cada panel interno muestra p, q, φ, d solo si el modo de su dueño está activo."""
        activos = {"Alice": self.estado.alice, "Bob": self.estado.bob}
        for nombre, panel in self.privado.items():
            u = self.usuarios[nombre]
            panel.actualizar(u.vista_publica(), u.vista_privada() if activos[nombre] else None)

    # ---------- formularios manuales ----------
    def _encriptar_manual(self, datos):
        form = self.formularios.encriptar
        form.limpiar_errores()
        self._manual["enc"] = True
        try:
            res = encriptar(datos["M"], datos["p"], datos["q"], datos["e"])
        except ErrorRSA as err:
            form.limpiar_salidas()
            form.mostrar_error(err)
            self.detalle_enc.mostrar_error(err, mostrar_privado=True)
        else:
            form.mostrar_resultado(res)
            self.detalle_enc.mostrar(res, mostrar_proceso=True, mostrar_privado=True)
        self.detalle.select(self.detalle_enc)

    def _desencriptar_manual(self, datos):
        form = self.formularios.desencriptar
        form.limpiar_errores()
        self._manual["des"] = True
        try:
            res = desencriptar(datos["C"], datos["L"], datos["p"], datos["q"], datos["e"])
        except ErrorRSA as err:
            form.limpiar_salidas()
            form.mostrar_error(err)
            self.detalle_des.mostrar_error(err, mostrar_privado=True)
        else:
            form.mostrar_resultado(res)
            self.detalle_des.mostrar(res, mostrar_proceso=True, mostrar_privado=True)
        self.detalle.select(self.detalle_des)

    def _actualizar_llaves_usuario(self, datos):
        form = self.formularios.llaves
        try:
            nuevo = UsuarioRSA(datos["usuario"], datos["p"], datos["q"], datos["e"])
        except ErrorRSA as err:
            form.mostrar_error(err)
            return
        self.usuarios[datos["usuario"]] = nuevo
        self._refrescar_privados()
        form.mostrar_confirmacion(
            f"Llaves de {nuevo.nombre} actualizadas: (e, n) = ({nuevo.e}, {nuevo.n})")
