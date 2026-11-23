"""Transformación pura de modelos a filas/líneas (sin tkinter, sin importar rsa_core)."""

COLUMNAS_ENC = ("#", "Pareja", "Códigos ASCII", "m (6 díg.)", "m (entero)", "c (entero)",
                "c (6 díg.)", "Nota")
COLUMNAS_DES = ("#", "c (6 díg.)", "m = c^d mod n", "m (6 díg.)", "Código 1", "Código 2",
                "¿32-126?", "Caracteres", "Nota")
MASCARA = "••••"
ETAPAS_PUBLICAS = ("conversion", "cifrado")


def visible(texto: str) -> str:
    """Solo para mostrar en tabla: hace visibles los espacios."""
    return texto.replace(" ", "␣")


def filas_parametros(params, d=None, mostrar_privado=False) -> list[tuple[str, str]]:
    filas = [("n", str(params.n)), ("e", str(params.e))]
    if mostrar_privado:
        filas += [("p", str(params.p)), ("q", str(params.q)), ("φ", str(params.phi)),
                  ("d", str(d) if d is not None else "—")]
    else:
        filas += [("p", MASCARA), ("q", MASCARA), ("φ", MASCARA), ("d", MASCARA)]
    return filas


def filas_publicas(params, C, L) -> list[tuple[str, str]]:
    return [("n", str(params.n)), ("e", str(params.e)), ("C", str(C)), ("L", str(L))]


def filas_relleno_enc(res) -> list[tuple[str, str]]:
    """Presencia de relleno y mensaje con relleno (encriptación)."""
    return [("Relleno", "sí (032 al final)" if res.relleno else "no"),
            ("Mensaje con relleno", f'"{res.mensaje_relleno}"')]


def filas_relleno_des(res) -> list[tuple[str, str]]:
    """k, presencia de relleno y texto antes de retirarlo (desencriptación)."""
    return [("k", str(res.k)),
            ("Relleno", "sí (se retira 1 espacio)" if res.relleno else "no"),
            ("Texto con relleno", f'"{res.texto_con_relleno}"')]


def filas_usuario(nombre: str, vista_publica: dict, vista_privada: dict | None) -> list[tuple[str, str]]:
    """Panel interno de un usuario. vista_privada=None enmascara p, q, φ y d."""
    filas = [("Usuario", nombre), ("e", str(vista_publica["e"])), ("n", str(vista_publica["n"]))]
    if vista_privada is None:
        filas += [("p", MASCARA), ("q", MASCARA), ("φ", MASCARA), ("d", MASCARA)]
    else:
        filas += [("p", str(vista_privada["p"])), ("q", str(vista_privada["q"])),
                  ("φ", str(vista_privada["phi"])), ("d", str(vista_privada["d"]))]
    return filas


def filas_encriptacion(res) -> list[tuple[str, ...]]:
    filas = []
    for f in res.filas:
        filas.append((str(f.indice), visible(f.par), f"{f.codigos[0]} {f.codigos[1]}",
                      f.m_texto, str(f.m), str(f.c), f.c_texto,
                      "relleno 032" if f.tiene_relleno else ""))
    return filas


def filas_desencriptacion(res) -> list[tuple[str, ...]]:
    filas = []
    for f in res.filas:
        filas.append((str(f.indice), f.c_texto, str(f.m), f.m_texto,
                      f.codigos_texto[0], f.codigos_texto[1],
                      "sí" if f.codigos_validos else "no", visible(f.caracteres),
                      "espacio de relleno retirado" if f.es_relleno_retirado else ""))
    return filas


def lineas_pasos(pasos, mostrar_privado=True) -> list[tuple[str, str]]:
    """(texto, tag). Sin permiso privado solo se muestran pasos que no revelan p, q, φ ni d."""
    simbolo = {"ok": "✓", "error": "✗", "info": "•"}
    lineas = []
    for paso in pasos:
        if not mostrar_privado and paso.estado != "error" and paso.etapa not in ETAPAS_PUBLICAS:
            continue
        lineas.append((f"{simbolo.get(paso.estado, '•')} {paso.texto}", paso.estado))
    return lineas
