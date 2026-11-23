# Casos demo

1. **Chat:** Alice envía `Hola` a Bob en «Funcionamiento real»; luego activar «Ser Alice» y «Ser Bob».
2. **Encriptar:** `M="RSA"`, `p=367`, `q=373`, `e=17` → `C="026054 123875"`, `L=3`, `(17, 136891)`.
3. **Desencriptar:** `C="026054 123875"`, `L=3`, 367/373/17 → `d=8009`, `M="RSA"`; con `L=4` → `"RSA "`.
4. **Espacios:** `M="  Hi  "` ida y vuelta exacta.
5. **Errores:** `C="26054 123875"` (bloque de 5 dígitos), `L=5`, `p=q=367`, `e=6`, `M="Canción"`.
