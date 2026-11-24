# Sistema criptográfico RSA — Parcial 3

**Curso:** MM2015 Matemática Discreta 1 · **Grupo 3**

| Integrante | Carné |
| :-- | :-- |
| Axel Arturo Cruz Lima | 24656 |
| Enya Ayleen Gálvez Hernández | 24693 |

Aplicación en Python con interfaz gráfica (Tkinter) y una **versión web publicada en GitHub Pages** (sin instalar nada) que encripta y desencripta mensajes de texto con RSA, muestra el proceso paso a paso y recupera **exactamente** el mensaje original (incluidos espacios iniciales, finales y consecutivos).

## Versión de Python y dependencias

- Python **3.12.x** recomendado (mínimo 3.10; también probado con 3.13). Tkinter con Tcl/Tk 8.6.
- **Solo se usa la biblioteca estándar.** No hay paquetes externos que instalar; `requirements.txt` solo lo indica con un comentario.
- Recursos de la interfaz: `ui/public/Alice.png` y `ui/public/Bob.png` (imágenes de los usuarios en el canal). Deben permanecer en esa carpeta.

## Versión web (sin instalar nada)

**Enlace público:** https://turis0077.github.io/RSA-Cryptographic-System/

La página principal muestra esta documentación con el botón **Abrir el programa**. También se puede entrar directo al programa en `/app/` (https://turis0077.github.io/RSA-Cryptographic-System/app/).

Abra el enlace y use el chat (escriba en el teléfono de Alice o de Bob y pulse `>`) o las pestañas **Encriptar** y **Desencriptar**. No requiere usuario ni clave. La primera carga tarda unos segundos porque el navegador descarga el intérprete de Python.

La versión web ejecuta **el mismo código Python** (`rsa_core/`) dentro del navegador con [Pyodide](https://pyodide.org); la página (`web/`) solo dibuja los resultados. Por eso es el mismo comportamiento que la aplicación de escritorio: mismas validaciones, mismos modos Ser Alice / Funcionamiento Real / Ser Bob y mismo panel de detalle.

Para generarla localmente:

```bash
python build_web.py                          # crea la carpeta _site/
python -m http.server 8000 --directory _site # abrir http://localhost:8000 (programa en /app/)
```

Publicación: cada `push` a `main` ejecuta `.github/workflows/pages.yml`, que corre las pruebas, arma `_site/` y lo despliega en GitHub Pages (en el repositorio: Settings → Pages → Source: **GitHub Actions**).

## Instalación y ejecución (aplicación de escritorio)

No requiere instalación. Desde la carpeta del proyecto:

```bash
python --version
python -m tkinter                          # comprueba que Tkinter funciona
python main.py                             # inicia la aplicación
python -m unittest discover -s tests -v    # pruebas automáticas
python tests/auditar_restricciones.py      # auditoría de restricciones (código 0 = limpio)
```

## Estructura

```text
main.py            Arranque de la aplicación
rsa_core/          Lógica RSA pura (no importa tkinter)
ui/                Interfaz Tkinter (solo accede al núcleo mediante ui/servicio.py)
ui/public/         Imágenes de Alice y Bob
web/               Versión web: index.html, style.css, app.js y app_web.py (puente Python)
build_web.py       Arma la carpeta _site/ que se publica en GitHub Pages
.github/workflows/ Despliegue automático en GitHub Pages
tests/             Pruebas, auditoría estática y guion de casos (casos_demo.md)
```

## Uso

### Chat Alice ↔ Bob
1. Escriba un mensaje en el teléfono de Alice o de Bob y pulse `>` o Enter.
2. El emisor cifra con la **llave pública (e, n) del receptor**; el canal público muestra la llave y el sobre cifrado viajando; el receptor descifra con su exponente privado `d`.
3. La barra superior tiene **Ser Alice**, **Funcionamiento Real** y **Ser Bob** (Alice y Bob pueden activarse a la vez). En «Funcionamiento Real» solo se ven los datos públicos (`n`, `e`, `C`, `L`); al activar un modo se revela el proceso paso a paso y, si corresponde, los datos privados del dueño (`p`, `q`, `φ`, `d`). La primera vez que se activa un modo aparece una ventana explicativa.

### Encriptación manual (pestaña «Encriptar»)
1. Ingrese `M`, `p`, `q` y `e` (campos siempre legibles).
2. Pulse **Encriptar**.
3. Salidas: `C`, `L` y la llave pública `(e, n)`. El panel «Detalle de encriptación» muestra `n` y `φ`, `L` y si hubo relleno, cada pareja con sus códigos ASCII de 3 dígitos, el bloque `m` (antes del cifrado) y el bloque `c` (después), el registro de pasos y las validaciones.

### Desencriptación manual (pestaña «Desencriptar»)
1. Ingrese `C`, `L`, `p`, `q` y `e`.
2. Pulse **Desencriptar**.
3. Salidas: `d` y `M` (también `M` entre comillas, para ver los espacios). El panel «Detalle de desencriptación» muestra `n`, `φ`, la identidad de Bézout, `d`, cada bloque `c` y el `m` recuperado, los códigos y su validación 32–126, los caracteres y el retiro del relleno.

### Pestaña «Llaves (chat)»
Permite cambiar `p`, `q` y `e` de Alice o de Bob; si los datos son inválidos se marca el campo con error y no se modifica nada.

### Dónde se muestran C y L y cómo ingresarlos
- **Se muestran** en la pestaña «Encriptar» (salidas `C` y `L`), en el panel de detalle y, en el chat, el sobre del canal muestra `C`.
- **Para desencriptar**, `C` se escribe como bloques de **exactamente 6 dígitos separados por un solo espacio** (ej. `026054 123875`, sin espacios al inicio ni al final) y `L` es la longitud original del mensaje, incluidos sus espacios. Cada mensaje enviado por el chat rellena `C` y `L` automáticamente en la pestaña «Desencriptar» (siguen editables para probar errores; `p`, `q` y `e` se escriben a mano).

## Ejemplo completo

`M = "RSA"`, `p = 367`, `q = 373`, `e = 17`

| Paso | Resultado |
| :-- | :-- |
| Parámetros | `n = 136891`, `φ = 136152`, `MCD(17, 136152) = 1` |
| Inverso | Bézout: `17·8009 + 136152·(−1) = 1` → `d = 8009` |
| Longitud y relleno | `L = 3` (impar) → mensaje con relleno `"RSA "` |
| Códigos ASCII | `R=082 S=083`, `A=065 ␣=032` |
| Bloques `m` | `082083`, `065032` |
| Bloques `c` | `82083^17 mod 136891 = 26054` → `026054`; `65032^17 mod 136891 = 123875` |
| Salidas | `C = "026054 123875"`, `L = 3`, `(e, n) = (17, 136891)` |
| Desencriptar | `m = c^d mod n` → `082083`, `065032` → `"RSA "` → con `L = 3` se retira el relleno → `"RSA"` |
| Misma `C` con `L = 4` | `"RSA "` (no se retira nada) |

## Lógica del sistema RSA en esta aplicación

### 1. Variables

| Variable | Significado | Regla |
| :-- | :-- | :-- |
| `M` | Mensaje original | No vacío; solo ASCII 32–126 |
| `L` | Longitud original de `M` (con todos sus espacios, antes del relleno) | `L = 2k` (par) o `L = 2k−1` (impar) |
| `p`, `q` | Primos secretos | Enteros, primos y distintos |
| `n` | Módulo público, `n = p·q` | `126126 < n < 1000000` |
| `φ` | `φ = (p−1)(q−1)` (secreto) | — |
| `e` | Exponente público | `e > 1` y `MCD(e, φ) = 1` (puede ser mayor que `φ`) |
| `d` | Exponente privado | `e·d ≡ 1 (mod φ)`, `1 ≤ d < φ` |
| `m` | Bloque numérico de 2 caracteres (6 dígitos) | `032032 ≤ m ≤ 126126 < n` |
| `c` | Bloque cifrado | `0 ≤ c < n`, siempre de 6 dígitos |
| `C` | Mensaje cifrado | `k` bloques `c` separados por un espacio |

Llave pública: `(e, n)`. Llave privada: `(d, n)`.

### 2. Validación de parámetros (`rsa_core/validacion.py`)
Orden fijo para responder siempre al instante:
1. `p`, `q`, `e` deben ser enteros (se rechazan vacío, decimales, `1_0`, espacios, booleanos).
2. `p ≥ 2`, `q ≥ 2` y `p ≠ q`.
3. Se calcula `n = p·q` y se comprueba el rango **antes** de probar primalidad (evita bloqueos con números enormes).
4. `p` y `q` son primos (se informa el divisor encontrado si no lo son).
5. Se calcula `φ`.
6. `e > 1` y `MCD(e, φ) = 1` con el algoritmo de Euclides propio.

### 3. Primalidad
`es_primo` busca el menor divisor de `n` entre 2 y `√n` (si `n` es compuesto tiene un divisor en ese rango). `menor_divisor` devuelve ese divisor para explicar el error.

### 4. Máximo común divisor
`mcd_euclides(a, b)` repite `a, b = b, a % b` hasta que `b = 0`. Se usa únicamente para validar que `e` y `φ` sean primos relativos.

### 5. Inverso modular y exponente privado
`bezout_matricial(e, φ)` aplica el algoritmo de Euclides extendido en forma matricial y devuelve `(x, y)` con `e·x + φ·y = 1`. `inverso_modular` toma `d = x mod φ`, de modo que `d` queda positivo (`1 ≤ d < φ`) aunque `x` sea negativo. Se comprueba `(e·d) mod φ = 1`.

### 6. Exponenciación modular
`exponenciacion_modular(b, e, n)` usa cuadrados repetidos: recorre el exponente en binario, multiplica el resultado cuando el bit es 1 y eleva la base al cuadrado, **reduciendo módulo `n` en cada paso**. Nunca calcula la potencia completa. Acepta `b = 0` (bloque `000000` válido).

### 7. Codificación del mensaje (`codificacion.py`)
1. Se valida `M` y se mide `L`.
2. Si `L` es impar se agrega un espacio (código 032).
3. El texto se separa en parejas de caracteres.
4. Cada carácter se convierte con `ord` a 3 dígitos (con ceros a la izquierda) y los dos códigos se concatenan: `"RS"` → `082083`.

### 8. Encriptación (`encriptacion.py`)
Para cada bloque: `c = m^e mod n`, formateado a 6 dígitos con ceros a la izquierda. `C` une los bloques con un solo espacio. Salidas: `C`, `L` y `(e, n)`, más la traza completa de pasos.

### 9. Validación de `C` y `L` (`validacion_cifrado.py`)
- `C` se separa con un solo espacio; cada bloque debe tener exactamente 6 dígitos 0–9 y cumplir `0 ≤ c < n`.
- Con `k` bloques, `L` debe ser entero y valer `2k` (sin relleno) o `2k−1` (con relleno).

### 10. Desencriptación (`desencriptacion.py`)
1. Se validan `p`, `q`, `e`, `C` y `L`.
2. Se calcula `d` (sección 5).
3. Para cada bloque: `m = c^d mod n`, escrito con 6 dígitos.
4. `m` se divide en dos códigos de 3 dígitos (`m // 1000` y `m % 1000`); ambos deben estar entre 32 y 126, y se convierten con `chr`.
5. Si `L` es impar se comprueba que el último carácter recuperado sea un espacio y se retira exactamente ese; si es par no se retira nada.

### 11. Por qué se recupera el mensaje
Como `e·d ≡ 1 (mod φ)` y `MCD(m, n) = 1` o `m` es múltiplo de `p` o `q`, se cumple `(m^e)^d ≡ m (mod n)`. Por eso `c^d mod n` devuelve exactamente el bloque `m` original. Esto vale para todo `m < n`, y todo bloque posible (`≤ 126126`) es menor que `n`.

### 12. Roles Alice y Bob (`usuario.py`)
- Quien envía cifra con la llave pública `(e, n)` del **receptor**; el receptor descifra con su propio `d`.
- `UsuarioRSA` guarda `p`, `q`, `φ`, `d` como atributos privados (`__p`, `__q`, `__phi`, `__d`) y expone solo `e` y `n`.
- Usuarios por defecto: Bob `(p=367, q=373, e=17)` → `n=136891`, `φ=136152`, `d=8009`; Alice `(p=389, q=397, e=7)` → `n=154433`, `φ=153648`, `d=87799`.

### 13. Modos de visualización
- **Funcionamiento Real:** solo se ven los datos públicos del canal (`e`, `n`, `C`, `L`).
- **Ser Alice / Ser Bob** (pueden activarse a la vez): muestran el proceso paso a paso y los datos privados (`p`, `q`, `φ`, `d`) del usuario que se activa. El emisor ve el detalle de encriptación si su modo está activo; el receptor ve el de desencriptación y sus secretos si el suyo lo está.

### 14. Manejo de errores
Toda validación fallida lanza `ErrorRSA` con el campo afectado, un mensaje en español y los pasos acumulados. La interfaz resalta el campo, limpia las salidas anteriores y no cierra el programa.

## Mecanismo de relleno y conservación de espacios

`L` se mide **antes** de rellenar y cuenta todos los espacios del mensaje. Si `L` es impar se agrega **un** espacio (código `032`) al final. Al desencriptar, `L` indica si hubo relleno: si es impar se comprueba que el último carácter recuperado sea un espacio y se retira exactamente ese carácter; si es par no se retira nada. Nunca se usa `strip`, `rstrip`, `lstrip` ni `replace` sobre mensajes o bloques, por lo que los espacios originales (iniciales, finales y consecutivos) se conservan. `C` debe contener `k` bloques y `L` debe ser `2k` o `2k−1`.

## Archivos y funciones de los algoritmos propios

| Algoritmo | Archivo | Función |
| :-- | :-- | :-- |
| Primalidad (divisor ≤ √n) | `rsa_core/algoritmos.py` | `es_primo`, `menor_divisor` |
| Máximo común divisor (Euclides), usado para validar `e` | `rsa_core/algoritmos.py` | `mcd_euclides` (usada en `validar_parametros`, `rsa_core/validacion.py`) |
| Inverso modular (Euclides extendido / Bézout matricial), usado para `d` | `rsa_core/algoritmos.py` | `bezout_matricial`, `inverso_modular` |
| Exponenciación modular (cuadrados repetidos, reduciendo módulo `n` en cada paso) | `rsa_core/algoritmos.py` | `exponenciacion_modular` |

Otros módulos: `codificacion.py`/`decodificacion.py` (ASCII ↔ bloques de 6 dígitos y relleno), `validacion.py`/`validacion_cifrado.py` (validación de `M`, `p`, `q`, `e`, `C`, `L`), `encriptacion.py`/`desencriptacion.py` (`encriptar(M, p, q, e)`, `desencriptar(C, L, p, q, e)`) y `usuario.py` (`UsuarioRSA`).

Como solicitado, no se utilizó `math`, `fractions` ni `pow` con módulo ni con exponente negativo, ni la forma `a ** b % n`, ni ninguna librería criptográfica. `tests/auditar_restricciones.py` lo verifica automáticamente.

## Nota sobre `UsuarioRSA` (decisión D-4)

`UsuarioRSA` encapsula `__p`, `__q`, `__phi` y `__d` (atributos privados) y expone solo `e` y `n`. El emisor cifra con la llave pública del receptor; `cifrar_con_su_llave_publica(M)` delega en `encriptar(M, self.__p, self.__q, self.e)` únicamente para reutilizar la firma exigida por el enunciado. La interfaz nunca muestra `p`, `q`, `φ` ni `d` en «Funcionamiento Real».

## Validaciones

Un dato inválido muestra un mensaje en español, resalta el campo y nunca cierra el programa ni deja una salida anterior como si fuera correcta.

| Dato | Se rechaza |
| :-- | :-- |
| `p`, `q`, `e` | no enteros (`abc`, `17.5`, vacío, `1_0`, espacios), `p = q`, no primos, `n` fuera de `126126 < n < 1000000`, `e ≤ 1`, `MCD(e, φ) ≠ 1` |
| `M` | vacío o con caracteres fuera de 32–126 (tildes, `ñ`, tabulaciones, saltos de línea) |
| `C` | bloques que no tengan exactamente 6 dígitos 0–9, separación distinta de un espacio, `c ≥ n` |
| `L` | no entero, ≤ 0, distinto de `2k` y `2k−1` |
| Texto recuperado | códigos fuera de 32–126 (llave o `C` incorrectos), `L` impar sin espacio final |

## Comprobaciones realizadas

- **Pruebas automáticas** (`python -m unittest discover -s tests -v`): 29 pruebas.
  - Ida y vuelta exacta de 10 mensajes: longitud par e impar, mayúsculas y minúsculas, números y signos, espacios consecutivos, espacios al inicio y al final, el bloque máximo `~~`, y la llave de Alice.
  - Ceros iniciales en bloques cifrados (por ejemplo `"Hola"` → `028621`, `"Hola Bob"` con la llave de Alice → `007472`, `"~~"` → `051700`).
  - Ida y vuelta exhaustiva de las 95 × 95 parejas ASCII imprimibles.
  - Algoritmos comparados con oráculos independientes (MCD ingenuo, `d` verificado con `(e·d) mod φ = 1` en 1000 pares coprimos).
  - Rechazo de parámetros inválidos (incluido `p = 10^30` sin bloqueo), caracteres no admitidos, bloques mal formados, `c ≥ n`, longitudes inconsistentes y relleno no válido.
  - Encapsulación de `UsuarioRSA` y flujo Alice ↔ Bob.
- **Auditoría estática** (`python tests/auditar_restricciones.py`): sin imports, llamadas ni patrones prohibidos, y sin que el núcleo importe `tkinter`.
- **Pruebas manuales de la interfaz:** chat, modos, formularios y errores, guiadas por `tests/casos_demo.md`.

## Video demostrativo
[Enlace Al video](https://drive.google.com/drive/folders/1pER3JzLFQ-zxI0gja3vUSrJW59eO3isC?usp=sharing)
