"""Canal público: dibujo vectorial y animación con after() (nunca recibe p, q, φ ni d)."""
import tkinter as tk
from pathlib import Path
from tkinter import ttk

PUBLIC = Path(__file__).resolve().parent / "public"


class CanalFrame(ttk.Frame):
    PASOS_ANIMACION = 24
    MS_PASO = 30
    MS_TEXTO = 600

    def __init__(self, master):
        super().__init__(master)
        self.canvas = tk.Canvas(self, height=130, bg="#fafafa", highlightthickness=1)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self._dibujar())
        # Se conservan las referencias para que Tk no libere las imágenes.
        self._img = {}
        for nombre in ("Alice", "Bob"):
            try:
                self._img[nombre] = tk.PhotoImage(file=str(PUBLIC / f"{nombre}.png"))
            except tk.TclError:
                self._img[nombre] = None      # respaldo: círculo con la inicial
        self.reiniciar()

    def reiniciar(self):
        self._texto = ""
        self._llave = None
        self._sobre = None        # (fracción x, texto)
        self._dibujar()

    def _dibujar(self):
        c = self.canvas
        c.delete("all")
        w = max(c.winfo_width(), 300)
        x1, x2 = w * 0.22, w * 0.78
        c.create_text(w / 2, 12, text="Canal público", font=("Segoe UI", 9, "bold"))
        c.create_line(x1, 24, x1, 120)
        c.create_line(x2, 24, x2, 120)
        for x, nombre in ((w * 0.1, "Alice"), (w * 0.9, "Bob")):
            if self._img[nombre] is not None:
                c.create_image(x, 66, image=self._img[nombre])
            else:
                c.create_oval(x - 22, 44, x + 22, 88, fill="#cfe2f3")
                c.create_text(x, 66, text=nombre[0], font=("Segoe UI", 14, "bold"))
            c.create_text(x, 106, text=nombre)
        if self._llave:
            c.create_text(w / 2, 36, text=f"Llave pública (e, n) = ({self._llave[0]}, {self._llave[1]})",
                          font=("Consolas", 10))
        if self._sobre:
            frac, texto = self._sobre
            x = w * frac
            c.create_rectangle(x - 70, 58, x + 70, 90, fill="#fff2cc")
            c.create_text(x, 74, text=texto, font=("Consolas", 8))
        if self._texto:
            c.create_text(w / 2, 114, text=self._texto, font=("Segoe UI", 9))

    def mostrar_pasos_llave(self, textos, al_terminar):
        textos = list(textos)

        def paso():
            if textos:
                self._texto = textos.pop(0)
                self._dibujar()
                self.after(self.MS_TEXTO, paso)
            else:
                al_terminar()
        paso()

    def mostrar_llave(self, e, n):
        self._llave = (e, n)
        self._dibujar()

    def enviar_sobre(self, texto_cifrado, hacia, al_terminar):
        etiqueta = texto_cifrado if len(texto_cifrado) <= 22 else texto_cifrado[:21] + "…"
        ini, fin = (0.22, 0.78) if hacia == "Bob" else (0.78, 0.22)
        total = self.PASOS_ANIMACION

        def frame(i):
            self._sobre = (ini + (fin - ini) * i / total, etiqueta)
            self._dibujar()
            if i < total:
                self.after(self.MS_PASO, lambda: frame(i + 1))
            else:
                self._sobre = None
                self._dibujar()
                al_terminar()
        frame(0)
