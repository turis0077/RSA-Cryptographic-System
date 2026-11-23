import random
import unittest

from rsa_core.algoritmos import (bezout_matricial, es_primo, exponenciacion_modular,
                                 inverso_modular, mcd_euclides, menor_divisor)


def mcd_ingenuo(a, b):
    return max(d for d in range(1, min(a, b) + 1) if a % d == 0 and b % d == 0)


class TestAlgoritmos(unittest.TestCase):
    def test_mcd(self):
        for a, b in [(12, 18), (17, 136152), (100, 75), (7, 7), (1, 9)]:
            self.assertEqual(mcd_euclides(a, b), mcd_ingenuo(a, b))
        with self.assertRaises(ValueError):
            mcd_euclides(0, 5)

    def test_primos(self):
        for p in (2, 3, 367, 373, 1009):
            self.assertTrue(es_primo(p))
        for x in (0, 1, -7, 4, 9, 369):
            self.assertFalse(es_primo(x))
        self.assertEqual(menor_divisor(369), 3)
        self.assertIsNone(menor_divisor(373))

    def test_exponenciacion(self):
        self.assertEqual(exponenciacion_modular(82083, 17, 136891), 26054)
        self.assertEqual(exponenciacion_modular(65032, 17, 136891), 123875)
        self.assertEqual(exponenciacion_modular(0, 5, 100), 0)
        for args in ((-1, 5, 10), (2, 0, 10), (2, 5, 1)):
            with self.assertRaises(ValueError):
                exponenciacion_modular(*args)
        rnd = random.Random(1)
        for _ in range(200):
            b, e, n = rnd.randrange(0, 10**6), rnd.randrange(1, 10**4), rnd.randrange(2, 10**6)
            self.assertEqual(exponenciacion_modular(b, e, n), pow(b, e, n))

    def test_bezout_e_inverso(self):
        self.assertEqual(bezout_matricial(17, 136152), (8009, -1))
        self.assertEqual(bezout_matricial(13, 3220)[0], -743)
        self.assertEqual(inverso_modular(13, 3220), 2477)
        self.assertEqual(inverso_modular(17, 136152), 8009)
        with self.assertRaises(ValueError):
            inverso_modular(6, 9)
        rnd = random.Random(2)
        hechos = 0
        while hechos < 1000:
            a, m = rnd.randrange(1, 10**6), rnd.randrange(2, 10**6)
            if mcd_euclides(a, m) == 1:
                d = inverso_modular(a, m)
                self.assertTrue(1 <= d < m)
                self.assertEqual((a * d) % m, 1)
                hechos += 1


if __name__ == "__main__":
    unittest.main()
