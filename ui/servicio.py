"""Frontera única entre la interfaz y el núcleo RSA."""
from rsa_core import (  # noqa: F401
    encriptar, desencriptar, validar_parametros, UsuarioRSA, ErrorRSA, USUARIOS_DEMO,
)

USANDO_NUCLEO = True
