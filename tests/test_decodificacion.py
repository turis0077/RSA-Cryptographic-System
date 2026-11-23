import unittest

from rsa_core.codificacion import par_a_bloque
from rsa_core.decodificacion import bloque_a_codigos, codigos_a_par, quitar_relleno


class TestDecodificacion(unittest.TestCase):
    def test_basicas(self):
        self.assertEqual(bloque_a_codigos(82083), (82, 83))
        self.assertEqual(codigos_a_par(82, 83), "RS")
        self.assertEqual(quitar_relleno("RSA ", 3), "RSA")
        self.assertEqual(quitar_relleno("RSA ", 4), "RSA ")
        self.assertEqual(quitar_relleno("Hi  ", 3), "Hi ")

    def test_ida_y_vuelta_exhaustiva(self):
        for a in range(32, 127):
            for b in range(32, 127):
                par = chr(a) + chr(b)
                _, _, m = par_a_bloque(par)
                self.assertEqual(codigos_a_par(*bloque_a_codigos(m)), par)


if __name__ == "__main__":
    unittest.main()
