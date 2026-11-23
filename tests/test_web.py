"""Pruebas del puente web (web/app_web.py) ejecutado en CPython."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "web"))
import app_web


def j(texto):
    return json.loads(texto)


class TestWeb(unittest.TestCase):
    def test_encriptar_y_desencriptar_manual(self):
        r = j(app_web.encriptar_manual("RSA", "367", "373", "17"))
        self.assertEqual((r["ok"], r["C"], r["L"], r["llave"]), (True, "026054 123875", 3, "(17, 136891)"))
        d = j(app_web.desencriptar_manual("026054 123875", "3", "367", "373", "17"))
        self.assertEqual((d["d"], d["M"]), (8009, "RSA"))
        self.assertEqual(j(app_web.desencriptar_manual("026054 123875", "4", "367", "373", "17"))["M"], "RSA ")

    def test_errores_resaltan_campos(self):
        r = j(app_web.desencriptar_manual("26054 123875", "3", "367", "373", "17"))
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["campos"], ["C"])
        r = j(app_web.encriptar_manual("RSA", "11", "13", "7"))
        self.assertEqual(r["error"]["campos"], ["p", "q"])
        r = j(app_web.encriptar_manual("Canción", "367", "373", "17"))
        self.assertEqual(r["error"]["campos"], ["M"])

    def test_chat_conserva_espacios(self):
        env = j(app_web.enviar("Alice", "  Hola Bob "))
        self.assertTrue(env["ok"])
        self.assertEqual((env["destino"], env["e"], env["n"]), ("Bob", 17, 136891))
        rx = j(app_web.llegar())
        self.assertEqual(rx["M"], "  Hola Bob ")

    def test_visibilidad_del_detalle(self):
        j(app_web.enviar("Bob", "Hi "))
        j(app_web.llegar())
        real = j(app_web.render("enc", False, False))
        self.assertEqual(real["filas"], [])
        self.assertIn("proceso interno oculto", real["aviso"])
        emisor = j(app_web.render("enc", True, False))
        self.assertGreater(len(emisor["filas"]), 0)
        self.assertIn("••••", emisor["params"])
        texto = emisor["params"] + " ".join(t for t, _ in emisor["log"])
        self.assertNotIn("389", texto)       # p de Alice (receptora) no se revela
        completo = j(app_web.render("des", True, True))
        self.assertIn("87799", completo["params"])

    def test_panel_privado(self):
        oculto = j(app_web.privado_usuario("Bob", False))
        self.assertIn(["p", "••••"], oculto)
        visible = dict(j(app_web.privado_usuario("Bob", True)))
        self.assertEqual((visible["p"], visible["d"]), ("367", "8009"))

    def test_actualizar_llaves(self):
        self.assertFalse(j(app_web.actualizar_llaves("Bob", "11", "13", "7"))["ok"])
        self.assertTrue(j(app_web.actualizar_llaves("Bob", "367", "373", "17"))["ok"])


if __name__ == "__main__":
    unittest.main()
