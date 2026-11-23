import unittest

from rsa_core import USUARIOS_DEMO, UsuarioRSA


class TestUsuario(unittest.TestCase):
    def setUp(self):
        self.alice = UsuarioRSA("Alice", *USUARIOS_DEMO["Alice"])
        self.bob = UsuarioRSA("Bob", *USUARIOS_DEMO["Bob"])

    def test_llaves(self):
        self.assertEqual(self.bob.llave_publica, (17, 136891))
        self.assertEqual(self.alice.llave_publica, (7, 154433))
        self.assertEqual(self.bob.vista_privada()["d"], 8009)
        self.assertEqual(self.bob.vista_privada()["phi"], 136152)
        self.assertEqual(self.alice.vista_privada()["d"], 87799)

    def test_encapsulacion(self):
        for attr in ("p", "q", "phi", "d"):
            self.assertFalse(hasattr(self.bob, attr))
        r = repr(self.bob)
        for secreto in ("367", "373", "8009", "136152"):
            self.assertNotIn(secreto, r)

    def test_flujo_bidireccional(self):
        # Alice -> Bob: se cifra con la llave pública de Bob; Bob descifra.
        env = self.bob.cifrar_con_su_llave_publica("Hola Bob")
        self.assertEqual(self.bob.descifrar(env.C, env.L).M, "Hola Bob")
        env = self.alice.cifrar_con_su_llave_publica("  Hola Alice ")
        self.assertEqual(self.alice.descifrar(env.C, env.L).M, "  Hola Alice ")


if __name__ == "__main__":
    unittest.main()
