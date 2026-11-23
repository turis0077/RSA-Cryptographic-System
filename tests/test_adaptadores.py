import unittest

from rsa_core import desencriptar, encriptar
from ui import adaptadores


class TestAdaptadores(unittest.TestCase):
    def test_visible(self):
        self.assertEqual(adaptadores.visible("A "), "A␣")

    def test_filas_encriptacion(self):
        res = encriptar("RSA", 367, 373, 17)
        filas = adaptadores.filas_encriptacion(res)
        self.assertEqual(filas[0], ("1", "RS", "082 083", "082083", "82083", "26054", "026054", ""))
        self.assertEqual(filas[1], ("2", "A␣", "065 032", "065032", "65032", "123875", "123875", "relleno 032"))
        self.assertEqual(len(filas[0]), len(adaptadores.COLUMNAS_ENC))

    def test_filas_desencriptacion(self):
        res = desencriptar("026054 123875", 3, 367, 373, 17)
        filas = adaptadores.filas_desencriptacion(res)
        self.assertEqual(filas[0][3], "082083")
        self.assertEqual(filas[1][-1], "espacio de relleno retirado")
        self.assertEqual(len(filas[0]), len(adaptadores.COLUMNAS_DES))
        for fila in filas:
            for celda in fila:
                self.assertIsInstance(celda, str)

    def test_mascara_privada(self):
        res = desencriptar("026054 123875", 3, 367, 373, 17)
        oculto = dict(adaptadores.filas_parametros(res.params, res.d, False))
        self.assertEqual((oculto["p"], oculto["q"], oculto["φ"], oculto["d"]), ("••••",) * 4)
        self.assertEqual((oculto["n"], oculto["e"]), ("136891", "17"))
        visible = dict(adaptadores.filas_parametros(res.params, res.d, True))
        self.assertEqual((visible["p"], visible["d"]), ("367", "8009"))

    def test_pasos_sin_privado_no_filtran_secretos(self):
        res = encriptar("RSA", 367, 373, 17)
        textos = " ".join(t for t, _ in adaptadores.lineas_pasos(res.pasos, mostrar_privado=False))
        self.assertNotIn("367", textos)
        self.assertNotIn("136152", textos)


if __name__ == "__main__":
    unittest.main()
