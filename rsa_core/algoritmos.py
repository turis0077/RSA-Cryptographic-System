"""Matemática base con implementación propia (sin math ni pow modular)."""


def mcd_euclides(a: int, b: int) -> int:
    if a == 0 or b == 0:
        raise ValueError("mcd_euclides requiere enteros distintos de cero")
    a, b = abs(a), abs(b)
    while b != 0:
        a, b = b, a % b
    return a


def menor_divisor(n: int) -> int | None:
    """Menor divisor propio de n (>1), o None si n es primo (o n <= 1)."""
    if n <= 1:
        return None
    limite = int(n ** 0.5) + 1
    for i in range(2, limite):
        if n % i == 0:
            return i
    return None


def es_primo(n: int) -> bool:
    if n <= 1:
        return False
    return menor_divisor(n) is None


def exponenciacion_modular(b: int, e: int, n: int) -> int:
    """Cuadrados repetidos: b^e mod n, reduciendo en cada paso."""
    if b < 0 or e <= 0 or n < 2:
        raise ValueError("Se requiere b >= 0, e > 0 y n >= 2")
    resultado = 1
    base = b % n
    while e > 0:
        if e % 2 == 1:
            resultado = (resultado * base) % n
        base = (base * base) % n
        e //= 2
    return resultado


def bezout_matricial(a: int, b: int) -> tuple[int, int]:
    """Devuelve (x, y) con a*x + b*y = MCD(a, b)."""
    if a <= 0 or b <= 0:
        raise ValueError("bezout_matricial requiere enteros positivos")
    (x1, y1), (x2, y2) = (1, 0), (0, 1)
    while b != 0:
        q, r = a // b, a % b
        a, b = b, r
        (x1, y1), (x2, y2) = (x2, y2), (x1 - q * x2, y1 - q * y2)
    return (x1, y1)


def inverso_modular(a: int, m: int) -> int:
    if a <= 0 or m <= 1:
        raise ValueError("Parámetros inválidos para inverso modular")
    if mcd_euclides(a, m) != 1:
        raise ValueError("No existe inverso modular: MCD distinto de 1")
    x, _ = bezout_matricial(a, m)
    return x % m
