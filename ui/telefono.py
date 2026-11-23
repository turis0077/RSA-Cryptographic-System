"""Teléfono (chat) reutilizable para Alice y Bob."""
import tkinter as tk
from tkinter import ttk

from . import tema


class TelefonoFrame(ttk.Frame):
    def __init__(self, master, propietario: str, contacto: str, al_enviar):
        super().__init__(master, padding=4)
        self.propietario = propietario
        self.al_enviar = al_enviar
        ttk.Label(self, text=f"Teléfono de {propietario}  —  @{contacto}",
                  font=(tema.FUENTE_UI[0], 11, "bold")).grid(row=0, column=0, columnspan=2, sticky="ew")

        self.canvas = tk.Canvas(self, bg="#ffffff", highlightthickness=1)
        barra = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=barra.set)
        self.interior = ttk.Frame(self.canvas)
        self._ventana = self.canvas.create_window((0, 0), window=self.interior, anchor="nw")
        self.interior.bind("<Configure>",
                           lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfigure(self._ventana, width=e.width))
        self.canvas.grid(row=1, column=0, sticky="nsew")
        barra.grid(row=1, column=1, sticky="ns")

        self.lbl_error = ttk.Label(self, text="", style="Error.TLabel", wraplength=260)
        self.lbl_error.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.var = tk.StringVar()
        self.entrada = ttk.Entry(self, textvariable=self.var)
        self.entrada.grid(row=3, column=0, sticky="ew")
        self.boton = ttk.Button(self, text=">", width=3, command=self._enviar)
        self.boton.grid(row=3, column=1)
        self.entrada.bind("<Return>", lambda e: self._enviar())
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

    def _enviar(self):
        # El texto se entrega TAL CUAL (sin strip).
        self.al_enviar(self.propietario, self.entrada.get())

    def agregar_burbuja(self, texto, propio, cifrado=False):
        fila = ttk.Frame(self.interior)
        fila.pack(fill="x", padx=4, pady=2)
        burbuja = tk.Label(fila, text=texto, wraplength=220, justify="left",
                           bg="#dcf8c6" if propio else "#eeeeee", padx=8, pady=4,
                           font=tema.FUENTE_MONO if cifrado else tema.FUENTE_UI)
        burbuja.pack(side="right" if propio else "left")
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def mostrar_error(self, msg):
        self.lbl_error.config(text=msg)

    def limpiar_error(self):
        self.lbl_error.config(text="")

    def limpiar_entrada(self):
        self.var.set("")

    def set_bloqueado(self, bloqueado: bool):
        estado = "disabled" if bloqueado else "normal"
        self.entrada.config(state=estado)
        self.boton.config(state=estado)

    def limpiar(self):
        for w in self.interior.winfo_children():
            w.destroy()
        self.limpiar_error()
