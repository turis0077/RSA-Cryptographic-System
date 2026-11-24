"""Arma la carpeta _site/ que se publica en GitHub Pages.

La raíz del sitio es una página de bienvenida que muestra el README con un botón
para abrir el programa, que queda en app/. Copia la página (web/), los módulos Python
que Pyodide cargará en el navegador (rsa_core/, ui/adaptadores.py, ui/textos.py y
web/app_web.py) y las imágenes.
Uso:  python build_web.py
"""
import json
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SITIO = RAIZ / "_site"
APP = SITIO / "app"
PY = APP / "py"

if SITIO.exists():
    shutil.rmtree(SITIO)
PY.mkdir(parents=True)

# Página
for nombre in ("index.html", "style.css", "app.js"):
    shutil.copy(RAIZ / "web" / nombre, APP / nombre)
shutil.copytree(RAIZ / "ui" / "public", APP / "public")
shutil.copy(RAIZ / "web" / "landing.html", SITIO / "index.html")
shutil.copy(RAIZ / "README.md", SITIO / "README.md")
(SITIO / ".nojekyll").write_text("", encoding="utf-8")

# Módulos Python que se ejecutan en el navegador (sin tkinter)
archivos = [Path("rsa_core") / p.name for p in sorted((RAIZ / "rsa_core").glob("*.py"))]
archivos += [Path("ui") / "__init__.py", Path("ui") / "adaptadores.py", Path("ui") / "textos.py"]
archivos += [Path("app_web.py")]
manifiesto = []
for rel in archivos:
    origen = RAIZ / "web" / rel if rel.name == "app_web.py" else RAIZ / rel
    destino = PY / rel
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(origen, destino)
    manifiesto.append(rel.as_posix())
(PY / "manifest.json").write_text(json.dumps(manifiesto, indent=2), encoding="utf-8")
print(f"Sitio generado en {SITIO} ({len(manifiesto)} módulos Python)")
