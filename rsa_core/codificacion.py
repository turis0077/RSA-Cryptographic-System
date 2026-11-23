"""Conversión de texto a bloques numéricos."""


def a_digitos(x: int, ancho: int) -> str:
    return f"{x:0{ancho}d}"


def preparar_mensaje(M: str) -> tuple[str, int, bool]:
    L = len(M)
    relleno = (L % 2 == 1)
    M_relleno = M + " " if relleno else M
    return (M_relleno, L, relleno)


def separar_pares(texto: str) -> list[str]:
    return [texto[i:i + 2] for i in range(0, len(texto), 2)]


def par_a_bloque(par: str) -> tuple[tuple[str, str], str, int]:
    c1 = a_digitos(ord(par[0]), 3)
    c2 = a_digitos(ord(par[1]), 3)
    m_texto = c1 + c2
    return ((c1, c2), m_texto, int(m_texto))
