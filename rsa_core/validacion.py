"""Validación estricta de entradas (sin autocorrección)."""
from .algoritmos import es_primo, menor_divisor, mcd_euclides
from .constantes import N_MIN, N_MAX, ASCII_MIN, ASCII_MAX
from .errores import ErrorRSA
from .modelos import Paso, ParametrosRSA

DIGITOS = "0123456789"


def _fallo(pasos, etapa, campo, mensaje):
    pasos.append(Paso(etapa, "error", mensaje))
    raise ErrorRSA(campo, mensaje, pasos=pasos)


def parsear_entero(valor, campo: str, pasos: list | None = None) -> int:
    if pasos is None:
        pasos = []
    if isinstance(valor, bool):
        _fallo(pasos, "validacion", campo, f"{campo} debe ser un número entero")
    if isinstance(valor, int):
        return valor
    if isinstance(valor, str):
        if valor == "":
            _fallo(pasos, "validacion", campo, f"{campo} debe ser un número entero (no puede estar vacío)")
        cuerpo = valor[1:] if valor[0] == "-" else valor
        if cuerpo == "" or any(ch not in DIGITOS for ch in cuerpo):
            _fallo(pasos, "validacion", campo, f"{campo} debe ser un número entero")
        try:
            return int(valor)
        except ValueError:
            _fallo(pasos, "validacion", campo, f"{campo} es demasiado grande")
    _fallo(pasos, "validacion", campo, f"{campo} debe ser un número entero")


def validar_parametros(p, q, e) -> ParametrosRSA:
    pasos: list[Paso] = []
    p = parsear_entero(p, "p", pasos)
    q = parsear_entero(q, "q", pasos)
    e = parsear_entero(e, "e", pasos)
    pasos.append(Paso("validacion", "ok", f"p = {p}, q = {q}, e = {e} son enteros"))

    if p < 2:
        _fallo(pasos, "validacion", "p", "p debe ser mayor o igual que 2")
    if q < 2:
        _fallo(pasos, "validacion", "q", "q debe ser mayor o igual que 2")
    if p == q:
        _fallo(pasos, "validacion", "q", "p y q deben ser primos distintos")
    pasos.append(Paso("validacion", "ok", "p y q son distintos"))

    # El rango de n se verifica ANTES de probar primalidad (evita bloqueos con p enormes).
    n = p * q
    if not (N_MIN < n < N_MAX):
        _fallo(pasos, "calculo", "n",
               f"n = {n} está fuera de rango (debe estar entre {N_MIN + 1} y {N_MAX - 1})")
    pasos.append(Paso("calculo", "ok", f"n = p·q = {p}·{q} = {n}, dentro del rango {N_MIN + 1}..{N_MAX - 1}"))

    if not es_primo(p):
        _fallo(pasos, "validacion", "p", f"{p} no es primo (divisible entre {menor_divisor(p)})")
    if not es_primo(q):
        _fallo(pasos, "validacion", "q", f"{q} no es primo (divisible entre {menor_divisor(q)})")
    pasos.append(Paso("validacion", "ok", f"{p} y {q} son primos"))

    phi = (p - 1) * (q - 1)
    pasos.append(Paso("calculo", "ok", f"φ = (p-1)(q-1) = {p - 1}·{q - 1} = {phi}"))

    if e <= 1:
        _fallo(pasos, "validacion", "e", "e debe ser mayor que 1")
    g = mcd_euclides(e, phi)
    if g != 1:
        _fallo(pasos, "validacion", "e", f"MCD(e, phi) = {g}, debe ser 1")
    pasos.append(Paso("validacion", "ok", f"MCD(e, φ) = MCD({e}, {phi}) = 1"))
    return ParametrosRSA(p, q, e, n, phi, g, pasos)


def validar_mensaje(M, pasos: list | None = None) -> list:
    if pasos is None:
        pasos = []
    if not isinstance(M, str) or M == "":
        _fallo(pasos, "validacion", "M", "El mensaje no puede estar vacío")
    for i, ch in enumerate(M, 1):
        if not (ASCII_MIN <= ord(ch) <= ASCII_MAX):
            _fallo(pasos, "validacion", "M",
                   f"Carácter no admitido {repr(ch)} (código {ord(ch)}) en la posición {i}")
    pasos.append(Paso("validacion", "ok", f"Mensaje válido: {len(M)} carácter(es) ASCII imprimibles"))
    return pasos
