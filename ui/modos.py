"""Estado y barra de modos Ser Alice / Funcionamiento real / Ser Bob."""
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk

from . import textos


@dataclass
class EstadoModos:
    alice: bool = False
    bob: bool = False

    def puede_ver_emisor(self, emisor: str) -> bool:
        return self.alice if emisor == "Alice" else self.bob

    def puede_ver_receptor(self, receptor: str) -> bool:
        return self.alice if receptor == "Alice" else self.bob


def ventana_explicativa(master, quien: str):
    """Modal de 2 páginas: aviso + explicación."""
    top = tk.Toplevel(master)
    top.title(f"Modo {quien}")
    top.transient(master.winfo_toplevel())
    top.resizable(False, False)
    lbl = ttk.Label(top, text=textos.POPUP_ALICE if quien == "Alice" else textos.POPUP_BOB,
                    wraplength=420, justify="left", padding=16)
    lbl.pack()
    boton = ttk.Button(top, text="Siguiente →")
    boton.pack(pady=(0, 12))

    def siguiente():
        lbl.config(text=textos.POPUP_EXPLICACION)
        boton.config(text="Entendido", command=top.destroy)

    boton.config(command=siguiente)
    top.grab_set()
    return top


class BotonModo(tk.Canvas):
    """Botón redondeado con sombra (estilo de la barra de modos)."""
    FONDO_BARRA = "#dcdad5"

    def __init__(self, master, texto, comando, ancho=125, alto=28):
        super().__init__(master, width=ancho + 6, height=alto + 6, bg=self.FONDO_BARRA,
                         highlightthickness=0, cursor="hand2")
        self.texto, self.comando, self.ancho, self.alto = texto, comando, ancho, alto
        self.activo = False
        self.bind("<Button-1>", lambda e: self.comando())
        self.bind("<Enter>", lambda e: self._pintar(hover=True))
        self.bind("<Leave>", lambda e: self._pintar())
        self._pintar()

    def _redondo(self, x0, y0, x1, y1, r, **kw):
        pts = [x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r, x1, y1 - r, x1, y1,
               x1 - r, y1, x0 + r, y1, x0, y1, x0, y1 - r, x0, y0 + r, x0, y0]
        return self.create_polygon(pts, smooth=True, **kw)

    def set_activo(self, activo):
        self.activo = activo
        self._pintar()

    def _pintar(self, hover=False):
        self.delete("all")
        a, h = self.ancho, self.alto
        self._redondo(3, 4, a + 3, h + 4, 7, fill="#b3b1ac", outline="")           # sombra
        relleno = "#cfe2f3" if self.activo else ("#f5f5f5" if hover else "#ffffff")
        self._redondo(1, 1, a + 1, h + 1, 7, fill=relleno, outline="#9a9a9a")
        self.create_text(a / 2 + 1, h / 2 + 1, text=self.texto,
                         font=("Segoe UI", 9, "bold" if self.activo else "normal"))


class BarraModos(tk.Frame):
    def __init__(self, master, estado: EstadoModos, al_cambiar):
        super().__init__(master, bg=BotonModo.FONDO_BARRA)
        self.estado = estado
        self.al_cambiar = al_cambiar
        self._visto = {"Alice": False, "Bob": False}
        self.b_alice = BotonModo(self, textos.BTN_ALICE, lambda: self._alternar("Alice"))
        self.b_real = BotonModo(self, textos.BTN_REAL, self._real, ancho=165)
        self.b_bob = BotonModo(self, textos.BTN_BOB, lambda: self._alternar("Bob"))
        self.b_alice.grid(row=0, column=0, pady=6)
        self.b_real.grid(row=0, column=1, pady=6)
        self.b_bob.grid(row=0, column=2, pady=6)
        self.columnconfigure((0, 1, 2), weight=1)
        self._pintar()

    def _alternar(self, quien):
        if quien == "Alice":
            self.estado.alice = not self.estado.alice
            activo = self.estado.alice
        else:
            self.estado.bob = not self.estado.bob
            activo = self.estado.bob
        if activo and not self._visto[quien]:
            self._visto[quien] = True
            ventana_explicativa(self, quien)
        self._cambio()

    def _real(self):
        self.estado.alice = False
        self.estado.bob = False
        self._cambio()

    def _cambio(self):
        self._pintar()
        self.al_cambiar(self.estado)

    def _pintar(self):
        self.b_alice.set_activo(self.estado.alice)
        self.b_bob.set_activo(self.estado.bob)
        self.b_real.set_activo(not (self.estado.alice or self.estado.bob))
