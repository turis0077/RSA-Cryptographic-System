"""Usuario RSA con atributos privados encapsulados."""
from .algoritmos import inverso_modular
from .desencriptacion import desencriptar
from .encriptacion import encriptar
from .validacion import validar_parametros


class UsuarioRSA:
    def __init__(self, nombre: str, p, q, e):
        params = validar_parametros(p, q, e)
        self.nombre = nombre
        self.e = params.e
        self.n = params.n
        self.__p = params.p
        self.__q = params.q
        self.__phi = params.phi
        self.__d = inverso_modular(params.e, params.phi)

    @property
    def llave_publica(self) -> tuple[int, int]:
        return (self.e, self.n)

    def vista_publica(self) -> dict:
        return {"nombre": self.nombre, "e": self.e, "n": self.n}

    def vista_privada(self) -> dict:
        return {"p": self.__p, "q": self.__q, "phi": self.__phi, "d": self.__d}

    def cifrar_con_su_llave_publica(self, M: str):
        # D-4: reutiliza la firma encriptar(M, p, q, e) exigida por el enunciado.
        return encriptar(M, self.__p, self.__q, self.e)

    def descifrar(self, C: str, L):
        return desencriptar(C, L, self.__p, self.__q, self.e)

    def __repr__(self) -> str:
        return f"UsuarioRSA({self.nombre!r}, e={self.e}, n={self.n})"
