import unittest

from rsa_core import ErrorRSA, desencriptar, encriptar

BOB = (367, 373, 17)
ALICE = (389, 397, 7)

# (M, L, relleno, bloques m, C, llave)
EXITO = [
    ("RSA", 3, True, "082083 065032", "026054 123875", BOB),
    ("Hola", 4, False, "072111 108097", "109641 028621", BOB),
    ("Hi ", 3, True, "072105 032032", "051670 038557", BOB),
    ("  A", 3, True, "032032 065032", "038557 123875", BOB),
    ("  Hi  ", 6, False, "032032 072105 032032", "038557 051670 038557", BOB),
    ("a   b", 5, True, "097032 032032 098032", "021860 038557 013282", BOB),
    ("Hello, World! 123~", 18, False,
     "072101 108108 111044 032087 111114 108100 033032 049050 051126",
     "044551 088850 042975 118406 133410 087403 127769 126442 107378", BOB),
    ("A", 1, True, "065032", "123875", BOB),
    ("~~", 2, False, "126126", "051700", BOB),
    ("Hola Bob", 8, False, "072111 108097 032066 111098",
     "111232 007472 050240 091028", ALICE),
]

# (campo, fragmento, C, L, llave)
ERRORES_DES = [
    ("C", "6 dígitos", "26054 123875", 3, BOB),
    ("C", "6 dígitos", "026054  123875", 3, BOB),
    ("C", "dígitos", "02605a 123875", 3, BOB),
    ("C", "menor que n", "999999 123875", 3, BOB),
    ("L", "3 o 4", "026054 123875", 5, BOB),
    ("L", "entero", "026054 123875", "tres", BOB),
    ("L", "positivo", "026054 123875", -3, BOB),
    ("L", "positivo", "026054 123875", 0, BOB),
    ("bloque", "fuera del rango", "000000", 2, BOB),
    ("bloque", "fuera del rango", "026054 123875", 3, ALICE),
]


class TestRSA(unittest.TestCase):
    def test_exito(self):
        for M, L, relleno, bloques, C, llave in EXITO:
            with self.subTest(M=M):
                r = encriptar(M, *llave)
                self.assertEqual(r.L, L)
                self.assertEqual(r.relleno, relleno)
                self.assertEqual(" ".join(f.m_texto for f in r.filas), bloques)
                self.assertEqual(r.C, C)
                x = desencriptar(r.C, L, *llave)
                self.assertEqual(x.M, M)

    def test_ejemplo_oficial(self):
        r = encriptar("RSA", *BOB)
        self.assertEqual(r.llave_publica, (17, 136891))
        x = desencriptar("026054 123875", 3, *BOB)
        self.assertEqual((x.d, x.M), (8009, "RSA"))
        self.assertEqual(desencriptar("026054 123875", 4, *BOB).M, "RSA ")

    def test_errores_desencriptar(self):
        for campo, frag, C, L, llave in ERRORES_DES:
            with self.subTest(C=C, L=L):
                with self.assertRaises(ErrorRSA) as cm:
                    desencriptar(C, L, *llave)
                self.assertEqual(cm.exception.campo, campo)
                self.assertIn(frag, cm.exception.mensaje)

    def test_D7_relleno_no_es_espacio(self):
        C = encriptar("RSA!", *BOB).C
        with self.assertRaises(ErrorRSA) as cm:
            desencriptar(C, 3, *BOB)
        self.assertEqual(cm.exception.campo, "L")
        self.assertIn("'!'", cm.exception.mensaje)

    def test_encriptar_rechaza_entradas_invalidas(self):
        for M in ("", "Canción", "a\tb"):
            with self.assertRaises(ErrorRSA):
                encriptar(M, *BOB)


if __name__ == "__main__":
    unittest.main()
