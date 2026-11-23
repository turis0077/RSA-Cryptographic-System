"""Procedimiento de encriptación RSA."""
from .algoritmos import exponenciacion_modular
from .codificacion import a_digitos, preparar_mensaje, separar_pares, par_a_bloque
from .errores import ErrorRSA
from .modelos import Paso, FilaEncriptacion, ResultadoEncriptacion
from .validacion import validar_parametros, validar_mensaje


def encriptar(M: str, p, q, e) -> ResultadoEncriptacion:
    params = validar_parametros(p, q, e)
    pasos = list(params.pasos)
    validar_mensaje(M, pasos)
    try:
        M_relleno, L, relleno = preparar_mensaje(M)
        if relleno:
            pasos.append(Paso("conversion", "info", f"L = {L} es impar: se agrega un espacio de relleno (032)"))
        else:
            pasos.append(Paso("conversion", "info", f"L = {L} es par: no se agrega relleno"))
        pares = separar_pares(M_relleno)
        filas, textos_c = [], []
        for i, par in enumerate(pares, 1):
            codigos, m_texto, m = par_a_bloque(par)
            pasos.append(Paso("conversion", "info",
                              f'Pareja {i} "{par}" -> {codigos[0]} {codigos[1]} -> m_{i} = {m_texto}'))
            c = exponenciacion_modular(m, params.e, params.n)
            c_texto = a_digitos(c, 6)
            filas.append(FilaEncriptacion(i, par, codigos, m_texto, m, c, c_texto,
                                          relleno and i == len(pares)))
            textos_c.append(c_texto)
            pasos.append(Paso("cifrado", "ok",
                              f"c_{i} = {m}^{params.e} mod {params.n} = {c} -> {c_texto}"))
    except ValueError as exc:
        pasos.append(Paso("cifrado", "error", str(exc)))
        raise ErrorRSA(None, str(exc), pasos=pasos)
    C = " ".join(textos_c)
    pasos.append(Paso("texto", "ok", f"C = {C}; L = {L}; llave pública (e, n) = ({params.e}, {params.n})"))
    return ResultadoEncriptacion(M, L, relleno, M_relleno, params, filas, C,
                                 (params.e, params.n), pasos)
