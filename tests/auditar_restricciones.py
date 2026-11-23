"""Auditoría estática de restricciones (ast). Código de salida 0 = limpio, 1 = hallazgos."""
import ast
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PROHIBIDOS = {"math", "fractions", "sympy", "Crypto", "cryptography", "rsa", "gmpy2", "numpy", "PIL"}
LLAMADAS_PROHIBIDAS = {"gcd", "lcm", "isqrt"}
METODOS_RECORTE = {"strip", "rstrip", "lstrip", "replace"}
ARCHIVOS_DATOS = {"codificacion.py", "decodificacion.py", "encriptacion.py",
                  "desencriptacion.py", "validacion.py", "validacion_cifrado.py"}


def _nombre_llamada(nodo: ast.Call):
    f = nodo.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def _modulos_importados(nodo):
    if isinstance(nodo, ast.Import):
        return [a.name for a in nodo.names]
    if isinstance(nodo, ast.ImportFrom):
        base = nodo.module or ""
        return [base] if nodo.level == 0 else []
    return []


def auditar_archivo(ruta: Path, carpeta: str) -> list[str]:
    hallazgos = []
    arbol = ast.parse(ruta.read_text(encoding="utf-8"), filename=str(ruta))
    rel = ruta.relative_to(RAIZ)
    for nodo in ast.walk(arbol):
        for mod in _modulos_importados(nodo):
            raiz = mod.split(".")[0]
            if raiz in PROHIBIDOS:
                hallazgos.append(f"{rel}:{nodo.lineno}: import prohibido '{mod}'")
            if carpeta == "rsa_core" and raiz == "tkinter":
                hallazgos.append(f"{rel}:{nodo.lineno}: rsa_core no puede importar tkinter")
            if carpeta == "ui" and raiz == "rsa_core" and ruta.name != "servicio.py":
                hallazgos.append(f"{rel}:{nodo.lineno}: solo ui/servicio.py puede importar rsa_core")
        if isinstance(nodo, ast.Call):
            nombre = _nombre_llamada(nodo)
            if nombre == "pow" and isinstance(nodo.func, ast.Name):
                neg = False
                if len(nodo.args) >= 2:
                    seg = nodo.args[1]
                    neg = (isinstance(seg, ast.UnaryOp) and isinstance(seg.op, ast.USub)) or \
                          (isinstance(seg, ast.Constant) and isinstance(seg.value, (int, float)) and seg.value < 0)
                if len(nodo.args) == 3 or neg:
                    hallazgos.append(f"{rel}:{nodo.lineno}: pow modular / exponente negativo prohibido")
            if nombre in LLAMADAS_PROHIBIDAS:
                hallazgos.append(f"{rel}:{nodo.lineno}: llamada prohibida '{nombre}'")
            if carpeta == "rsa_core" and ruta.name in ARCHIVOS_DATOS and \
                    isinstance(nodo.func, ast.Attribute) and nombre in METODOS_RECORTE:
                hallazgos.append(f"{rel}:{nodo.lineno}: '.{nombre}()' prohibido sobre datos")
        if isinstance(nodo, ast.BinOp) and isinstance(nodo.op, ast.Mod) and \
                isinstance(nodo.left, ast.BinOp) and isinstance(nodo.left.op, ast.Pow):
            hallazgos.append(f"{rel}:{nodo.lineno}: patrón 'a ** b % n' prohibido")
    return hallazgos


def main() -> int:
    hallazgos = []
    for carpeta in ("rsa_core", "ui", "web"):
        for ruta in sorted((RAIZ / carpeta).glob("*.py")):
            hallazgos += auditar_archivo(ruta, carpeta)
    if hallazgos:
        print("HALLAZGOS:")
        for h in hallazgos:
            print(" -", h)
        return 1
    print("Auditoría limpia: sin imports, llamadas ni patrones prohibidos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
