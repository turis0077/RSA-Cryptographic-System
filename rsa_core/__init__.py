"""API pública del núcleo RSA (sin dependencias de interfaz)."""
from .constantes import N_MIN, N_MAX, ASCII_MIN, ASCII_MAX, USUARIOS_DEMO
from .errores import ErrorRSA
from .modelos import (
    Paso, ParametrosRSA, FilaEncriptacion, ResultadoEncriptacion,
    FilaDesencriptacion, ResultadoDesencriptacion,
)
from .validacion import validar_parametros
from .encriptacion import encriptar
from .desencriptacion import desencriptar
from .usuario import UsuarioRSA
