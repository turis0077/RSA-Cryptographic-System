import time
import unittest

from rsa_core import ErrorRSA, validar_parametros
from rsa_core.validacion import parsear_entero, validar_mensaje


class TestValidacion(unittest.TestCase):
    def fallo(self, p, q, e):
        with self.assertRaises(ErrorRSA) as cm:
            validar_parametros(p, q, e)
        return cm.exception

    def test_validos(self):
        r = validar_parametros(367, 373, 17)
        self.assertEqual((r.n, r.phi, r.mcd), (136891, 136152, 1))
        self.assertEqual(validar_parametros("367", "373", "17").n, 136891)
        validar_parametros(367, 373, 136153)   # e > phi permitido (D-6)

    def test_errores_E1_E6(self):
        x = self.fallo(367, 367, 17)
        self.assertEqual((x.campo, x.mensaje), ("q", "p y q deben ser primos distintos"))
        x = self.fallo(369, 373, 17)
        self.assertEqual(x.campo, "p")
        self.assertIn("369 no es primo (divisible entre 3)", x.mensaje)
        self.assertEqual(self.fallo(11, 13, 7).campo, "n")
        self.assertEqual(self.fallo(1009, 997, 7).campo, "n")
        x = self.fallo(367, 373, 6)
        self.assertEqual(x.campo, "e")
        self.assertIn("MCD(e, phi) = 6", x.mensaje)
        for e in (1, 0, -5):
            x = self.fallo(367, 373, e)
            self.assertEqual((x.campo, x.mensaje), ("e", "e debe ser mayor que 1"))

    def test_E7_no_enteros(self):
        for e in ("abc", "17.5", "", "1_0", " 5 ", "²", True, False, "-"):
            x = self.fallo(367, 373, e)
            self.assertEqual(x.campo, "e")
            self.assertIn("debe ser un número entero", x.mensaje)
        self.assertEqual(parsear_entero("-5", "e"), -5)

    def test_E10_numero_gigante_es_instantaneo(self):
        t = time.time()
        x = self.fallo(10**30, 373, 17)
        self.assertEqual(x.campo, "n")
        self.assertLess(time.time() - t, 1)

    def test_mensajes_E8_E9(self):
        with self.assertRaises(ErrorRSA) as cm:
            validar_mensaje("Canción")
        self.assertEqual(cm.exception.campo, "M")
        self.assertIn("'ó'", cm.exception.mensaje)
        self.assertIn("243", cm.exception.mensaje)
        self.assertIn("posición 6", cm.exception.mensaje)
        for m in ("", "a\tb", "a\nb", None):
            with self.assertRaises(ErrorRSA):
                validar_mensaje(m)

    def test_pasos_en_error(self):
        x = self.fallo(367, 367, 17)
        self.assertEqual(x.pasos[-1].estado, "error")


if __name__ == "__main__":
    unittest.main()
