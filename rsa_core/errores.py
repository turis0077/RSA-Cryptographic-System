"""Excepción del núcleo RSA."""


class ErrorRSA(Exception):
    def __init__(self, campo: str | None, mensaje: str, bloque: int | None = None, pasos: list | None = None):
        super().__init__(mensaje)
        self.campo = campo          # "M" | "p" | "q" | "e" | "n" | "C" | "L" | "bloque" | "texto"
        self.mensaje = mensaje
        self.bloque = bloque        # Índice base 1 si falla un bloque
        self.pasos = list(pasos) if pasos else []
