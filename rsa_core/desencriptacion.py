"""Procedimiento de desencriptación RSA."""
from .algoritmos import bezout_matricial, inverso_modular, exponenciacion_modular
from .codificacion import a_digitos
from .decodificacion import bloque_a_codigos, codigos_a_par, quitar_relleno
from .errores import ErrorRSA
from .modelos import Paso, FilaDesencriptacion, ResultadoDesencriptacion
from .validacion import validar_parametros
from .validacion_cifrado import validar_cifrado, validar_longitud


def desencriptar(C: str, L, p, q, e) -> ResultadoDesencriptacion:
    params = validar_parametros(p, q, e)
    pasos = list(params.pasos)
    bloques = validar_cifrado(C, params.n, pasos)
    k = len(bloques)
    L_int, relleno = validar_longitud(L, k, pasos)

    try:
        x, y = bezout_matricial(params.e, params.phi)
        d = inverso_modular(params.e, params.phi)
    except ValueError as exc:
        pasos.append(Paso("inverso", "error", str(exc)))
        raise ErrorRSA("e", str(exc), pasos=pasos)
    pasos.append(Paso("inverso", "ok", f"Bézout: {params.e}·({x}) + {params.phi}·({y}) = 1"))
    pasos.append(Paso("inverso", "ok", f"d = x mod φ = {x} mod {params.phi} = {d}"))
    pasos.append(Paso("inverso", "ok",
                      f"Comprobación: (e·d) mod φ = ({params.e}·{d}) mod {params.phi} = {(params.e * d) % params.phi}"))

    filas = []
    texto = ""
    for i, (c_texto, c) in enumerate(bloques, 1):
        m = exponenciacion_modular(c, d, params.n)
        m_texto = a_digitos(m, 6)
        if len(m_texto) != 6:
            msg = f"Bloque {i}: m = {m} no cabe en 6 dígitos"
            pasos.append(Paso("descifrado", "error", msg))
            raise ErrorRSA("bloque", msg, bloque=i, pasos=pasos)
        a, b = bloque_a_codigos(m)
        codigos_texto = (a_digitos(a, 3), a_digitos(b, 3))
        pasos.append(Paso("descifrado", "ok",
                          f"m_{i} = {c}^{d} mod {params.n} = {m} -> {m_texto} -> códigos {codigos_texto[0]} y {codigos_texto[1]}"))
        validos = 32 <= a <= 126 and 32 <= b <= 126
        if not validos:
            msg = f"Bloque {i}: códigos {a} y {b} fuera del rango ASCII 32-126"
            pasos.append(Paso("descifrado", "error", msg))
            raise ErrorRSA("bloque", msg, bloque=i, pasos=pasos)
        par = codigos_a_par(a, b)
        texto += par
        filas.append(FilaDesencriptacion(i, c_texto, c, m, m_texto, (a, b), codigos_texto,
                                         validos, par, relleno and i == k))
    pasos.append(Paso("texto", "ok", "Todos los bloques tienen 6 dígitos y códigos en 32-126"))

    if relleno:
        if texto[-1] != " ":
            msg = (f"L = {L_int} es impar pero el último carácter recuperado es {repr(texto[-1])} "
                   "y no un espacio de relleno")
            pasos.append(Paso("texto", "error", msg))
            raise ErrorRSA("L", msg, pasos=pasos)
        M = quitar_relleno(texto, L_int)
        pasos.append(Paso("texto", "ok", "Se retiró exactamente un espacio de relleno (032)"))
    else:
        M = texto
        pasos.append(Paso("texto", "ok", "L es par: no hay relleno que retirar"))
    pasos.append(Paso("texto", "ok", f'Mensaje recuperado M = "{M}" (L = {len(M)})'))
    return ResultadoDesencriptacion(C, L_int, k, relleno, params, d, x, filas, texto, M, pasos)
