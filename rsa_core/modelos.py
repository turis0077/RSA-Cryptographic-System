"""Dataclasses del contrato entre núcleo e interfaz."""
from dataclasses import dataclass


@dataclass
class Paso:
    etapa: str
    estado: str                     # "ok" | "error" | "info"
    texto: str


@dataclass
class ParametrosRSA:
    p: int
    q: int
    e: int
    n: int
    phi: int
    mcd: int
    pasos: list[Paso]


@dataclass
class FilaEncriptacion:
    indice: int
    par: str
    codigos: tuple[str, str]
    m_texto: str
    m: int
    c: int
    c_texto: str
    tiene_relleno: bool


@dataclass
class ResultadoEncriptacion:
    mensaje: str
    L: int
    relleno: bool
    mensaje_relleno: str
    params: ParametrosRSA
    filas: list[FilaEncriptacion]
    C: str
    llave_publica: tuple[int, int]
    pasos: list[Paso]


@dataclass
class FilaDesencriptacion:
    indice: int
    c_texto: str
    c: int
    m: int
    m_texto: str
    codigos: tuple[int, int]
    codigos_texto: tuple[str, str]
    codigos_validos: bool
    caracteres: str
    es_relleno_retirado: bool


@dataclass
class ResultadoDesencriptacion:
    C: str
    L: int
    k: int
    relleno: bool
    params: ParametrosRSA
    d: int
    x_bezout: int
    filas: list[FilaDesencriptacion]
    texto_con_relleno: str
    M: str
    pasos: list[Paso]
