"""Validación de C y L para desencriptar."""
from .errores import ErrorRSA
from .modelos import Paso
from .validacion import parsear_entero, DIGITOS


def _fallo(pasos, campo, mensaje, bloque=None):
    pasos.append(Paso("validacion", "error", mensaje))
    raise ErrorRSA(campo, mensaje, bloque=bloque, pasos=pasos)


def validar_cifrado(C, n: int, pasos: list) -> list[tuple[str, int]]:
    if not isinstance(C, str) or C == "":
        _fallo(pasos, "C", "C no puede estar vacío")
    resultado = []
    for i, b in enumerate(C.split(" "), 1):
        if len(b) != 6:
            _fallo(pasos, "C", f"Bloque {i}: debe tener exactamente 6 dígitos (tiene {len(b)}); "
                               "separe los bloques con un solo espacio", bloque=i)
        if any(ch not in DIGITOS for ch in b):
            _fallo(pasos, "C", f"Bloque {i}: solo admite dígitos decimales 0-9", bloque=i)
        c = int(b)
        if not (0 <= c < n):
            _fallo(pasos, "C", f"Bloque {i}: c = {c} debe ser menor que n = {n}", bloque=i)
        resultado.append((b, c))
    pasos.append(Paso("validacion", "ok", f"C válido: {len(resultado)} bloque(s) de 6 dígitos con 0 ≤ c < n"))
    return resultado


def validar_longitud(L, k: int, pasos: list) -> tuple[int, bool]:
    L = parsear_entero(L, "L", pasos)
    if L <= 0:
        _fallo(pasos, "L", "L debe ser un entero positivo")
    if L == 2 * k:
        pasos.append(Paso("validacion", "ok", f"L = {L} = 2k: longitud par, sin relleno"))
        return (L, False)
    if L == 2 * k - 1:
        pasos.append(Paso("validacion", "ok", f"L = {L} = 2k-1: longitud impar, hay espacio de relleno"))
        return (L, True)
    _fallo(pasos, "L", f"L = {L} es inconsistente con {k} bloque(s): debe ser {2 * k - 1} o {2 * k}")
