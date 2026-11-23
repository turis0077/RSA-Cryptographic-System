"""Constantes del sistema RSA."""
N_MIN = 126126       # Estricto: N_MIN < n < N_MAX
N_MAX = 1000000
ASCII_MIN = 32
ASCII_MAX = 126
ANCHO_CODIGO = 3
ANCHO_BLOQUE = 6
ETAPAS = ("validacion", "calculo", "conversion", "cifrado", "inverso", "descifrado", "texto")
USUARIOS_DEMO = {
    "Alice": (389, 397, 7),
    "Bob": (367, 373, 17),
}
