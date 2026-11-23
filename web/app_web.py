"""Puente Python <-> navegador (se ejecuta con Pyodide).

Toda la lógica RSA sigue siendo Python propio (rsa_core). Este módulo solo guarda el
estado de la sesión y entrega a la página resultados ya listos para dibujar, en JSON.
No importa tkinter.
"""
import json

from rsa_core import (ErrorRSA, UsuarioRSA, USUARIOS_DEMO, desencriptar, encriptar)
from ui import adaptadores, textos

CAMPOS_ERROR = {"n": ("p", "q"), "bloque": ("C",)}

usuarios = {n: UsuarioRSA(n, *USUARIOS_DEMO[n]) for n in ("Alice", "Bob")}
_ultimo = {"enc": None, "des": None}
_error = {"enc": None, "des": None}
_error_privado = {"enc": True, "des": True}
_pendiente = None      # (destino, resultado de encriptación) a la espera de llegar


def _salida(obj):
    return json.dumps(obj, ensure_ascii=False)


def _error_dict(err):
    campos = list(CAMPOS_ERROR.get(err.campo, (err.campo,))) if err.campo else []
    return {"campo": err.campo, "mensaje": err.mensaje, "campos": campos}


def _publica(nombre):
    return usuarios[nombre].vista_publica()


# ---------------------------------------------------------------- inicio
def iniciar():
    return _salida({
        "textos": {
            "titulo": textos.TITULO_VENTANA, "popup_alice": textos.POPUP_ALICE,
            "popup_bob": textos.POPUP_BOB, "popup_explicacion": textos.POPUP_EXPLICACION,
            "status": textos.STATUS, "etiquetas": textos.ETIQUETAS,
            "ayuda_m": textos.AYUDA_M, "ayuda_c": textos.AYUDA_C, "ayuda_l": textos.AYUDA_L,
        },
        "usuarios": {n: _publica(n) for n in usuarios},
    })


# ---------------------------------------------------------------- render del detalle
def _vacio(log=None):
    return {"params": "", "aviso": "", "columnas": [], "filas": [], "log": log or []}


def render(tipo, proceso, privado):
    """Equivale a Detalle.refrescar: decide qué se muestra según los modos."""
    err = _error[tipo]
    if err is not None:
        return _salida(_vacio(adaptadores.lineas_pasos(err.pasos, _error_privado[tipo])))
    res = _ultimo[tipo]
    if res is None:
        return _salida(_vacio())
    if not proceso:
        filas = adaptadores.filas_publicas(res.params, res.C, res.L)
        out = _vacio()
        out["params"] = "   ".join(f"{k} = {v}" for k, v in filas)
        out["aviso"] = textos.AVISO_REAL
        return _salida(out)
    if tipo == "enc":
        d, extra = None, adaptadores.filas_relleno_enc(res)
        columnas, filas_t = adaptadores.COLUMNAS_ENC, adaptadores.filas_encriptacion(res)
    else:
        d, extra = res.d, adaptadores.filas_relleno_des(res)
        columnas, filas_t = adaptadores.COLUMNAS_DES, adaptadores.filas_desencriptacion(res)
    filas = adaptadores.filas_parametros(res.params, d, privado)
    filas += [("C", res.C), ("L", str(res.L))] + extra
    return _salida({
        "params": "   ".join(f"{k} = {v}" for k, v in filas),
        "aviso": "", "columnas": list(columnas),
        "filas": [list(f) for f in filas_t],
        "log": adaptadores.lineas_pasos(res.pasos, privado),
    })


# ---------------------------------------------------------------- chat
def enviar(origen, texto):
    """El emisor cifra con la llave pública del receptor (el dueño de la llave)."""
    global _pendiente
    destino = "Bob" if origen == "Alice" else "Alice"
    try:
        res = usuarios[destino].cifrar_con_su_llave_publica(texto)
    except ErrorRSA as err:
        _ultimo["enc"], _error["enc"], _error_privado["enc"] = None, err, False
        return _salida({"ok": False, "error": _error_dict(err)})
    _ultimo["enc"], _error["enc"] = res, None
    _pendiente = (destino, res)
    e, n = usuarios[destino].llave_publica
    return _salida({"ok": True, "origen": origen, "destino": destino,
                    "C": res.C, "L": res.L, "e": e, "n": n})


def llegar():
    """El receptor descifra con su d privado."""
    destino, res = _pendiente
    try:
        rx = usuarios[destino].descifrar(res.C, res.L)
    except ErrorRSA as err:
        _ultimo["des"], _error["des"] = None, err
        return _salida({"ok": False, "destino": destino, "error": _error_dict(err),
                        "C": res.C, "L": res.L})
    _ultimo["des"], _error["des"] = rx, None
    return _salida({"ok": True, "destino": destino, "M": rx.M, "C": res.C, "L": res.L})


def privado_usuario(nombre, visible):
    """Panel interno: p, q, φ y d solo si el modo del dueño está activo."""
    u = usuarios[nombre]
    filas = adaptadores.filas_usuario(nombre, u.vista_publica(),
                                      u.vista_privada() if visible else None)
    return _salida([list(f) for f in filas[1:]])


# ---------------------------------------------------------------- formularios manuales
def encriptar_manual(M, p, q, e):
    try:
        res = encriptar(M, p, q, e)
    except ErrorRSA as err:
        _ultimo["enc"], _error["enc"], _error_privado["enc"] = None, err, True
        return _salida({"ok": False, "error": _error_dict(err)})
    _ultimo["enc"], _error["enc"] = res, None
    return _salida({"ok": True, "C": res.C, "L": res.L,
                    "llave": f"({res.llave_publica[0]}, {res.llave_publica[1]})"})


def desencriptar_manual(C, L, p, q, e):
    try:
        res = desencriptar(C, L, p, q, e)
    except ErrorRSA as err:
        _ultimo["des"], _error["des"], _error_privado["des"] = None, err, True
        return _salida({"ok": False, "error": _error_dict(err)})
    _ultimo["des"], _error["des"] = res, None
    return _salida({"ok": True, "d": res.d, "M": res.M})


def actualizar_llaves(usuario, p, q, e):
    try:
        nuevo = UsuarioRSA(usuario, p, q, e)
    except ErrorRSA as err:
        return _salida({"ok": False, "error": _error_dict(err)})
    usuarios[usuario] = nuevo
    return _salida({"ok": True, "mensaje":
                    f"Llaves de {nuevo.nombre} actualizadas: (e, n) = ({nuevo.e}, {nuevo.n})"})
