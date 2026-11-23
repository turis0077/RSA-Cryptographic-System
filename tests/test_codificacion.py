import unittest

from rsa_core.codificacion import a_digitos, par_a_bloque, preparar_mensaje, separar_pares


class TestCodificacion(unittest.TestCase):
    def test_digitos(self):
        self.assertEqual(a_digitos(5, 3), "005")
        self.assertEqual(a_digitos(26054, 6), "026054")

    def test_preparar(self):
        self.assertEqual(preparar_mensaje("RSA"), ("RSA ", 3, True))
        self.assertEqual(preparar_mensaje("Hola"), ("Hola", 4, False))
        self.assertEqual(preparar_mensaje("Hi "), ("Hi  ", 3, True))
        self.assertEqual(preparar_mensaje("  A"), ("  A ", 3, True))

    def test_pares(self):
        self.assertEqual(separar_pares("RSA "), ["RS", "A "])

    def test_bloque(self):
        self.assertEqual(par_a_bloque("RS"), (("082", "083"), "082083", 82083))
        self.assertEqual(par_a_bloque("A "), (("065", "032"), "065032", 65032))
        self.assertEqual(par_a_bloque("~~")[1], "126126")


if __name__ == "__main__":
    unittest.main()
