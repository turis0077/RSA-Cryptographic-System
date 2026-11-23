"""Conversión de bloques numéricos a texto."""


def bloque_a_codigos(m: int) -> tuple[int, int]:
    return (m // 1000, m % 1000)


def codigos_a_par(a: int, b: int) -> str:
    return chr(a) + chr(b)


def quitar_relleno(texto: str, L: int) -> str:
    if L % 2 == 1:
        return texto[:-1]
    return texto
