"""Textos en español de la interfaz (sin tkinter)."""

TITULO_VENTANA = "Sistema criptográfico RSA — Alice ↔ Bob"
BTN_ALICE = "Ser Alice"
BTN_REAL = "Funcionamiento Real"
BTN_BOB = "Ser Bob"

POPUP_ALICE = ("Modo «Ser Alice»: verás los datos internos de Alice (p, q, φ, d) y el cálculo "
               "paso a paso de lo que Alice envía o recibe. En un canal real esta información "
               "es secreta; aquí se muestra solo con fines didácticos.")
POPUP_BOB = ("Modo «Ser Bob»: verás los datos internos de Bob (p, q, φ, d) y el cálculo "
             "paso a paso de lo que Bob envía o recibe. En un canal real esta información "
             "es secreta; aquí se muestra solo con fines didácticos.")
POPUP_EXPLICACION = ("¿Por qué funciona y no es un error? RSA protege el canal público, no la "
                     "pantalla de quien lo usa: el dueño de una llave siempre conoce sus propios "
                     "p, q, φ y d. Quien envía solo usa la llave pública (e, n) del receptor y "
                     "únicamente el receptor puede deshacer el cifrado con su d privado.")

STATUS = {
    "listo": "Listo. Escriba un mensaje en el teléfono de Alice o de Bob.",
    "llave": "{origen} solicita la llave pública de {destino}…",
    "llave_ok": "Llave pública de {destino}: (e = {e}, n = {n})",
    "cifrando": "{origen} cifra el mensaje con la llave pública de {destino}…",
    "sobre": "Mensaje cifrado viajando por el canal público…",
    "descifrando": "{destino} descifra con su exponente privado d…",
    "entregado": "Mensaje entregado a {destino}.",
    "error": "Error: {mensaje}",
}

ETIQUETAS = {"M": "Mensaje M", "C": "Mensaje cifrado C", "L": "Longitud L",
             "p": "Primo p", "q": "Primo q", "e": "Exponente e"}
AYUDA_M = "ASCII imprimible 32-126 (sin tildes, ñ, tabs ni saltos de línea)"
AYUDA_C = "Bloques de 6 dígitos separados por UN espacio"
AYUDA_L = "Longitud original de M (incluye espacios)"
AVISO_REAL = ("Modo Funcionamiento real: proceso interno oculto. Active Modo Alice o Modo Bob "
              "para inspeccionar el cálculo paso a paso.")
