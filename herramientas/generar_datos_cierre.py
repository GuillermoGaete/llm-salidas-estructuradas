"""Genera clases/datos_cierre.js: los datos de la última diapositiva.

En esa diapositiva el modelo continúa un texto de despedida dos veces:

  1. Sin máscara. Es lo que salió en un sorteo real, guardado en SIN_MASCARA.
  2. Con la máscara del ejercicio 04 (mascara_v2.py), con FORMATO = "Muchas gracias".

En cada paso se guardan las probabilidades reales del modelo, para que la
diapositiva las muestre sin tener que cargar el modelo.

Cómo correrlo (desde la raíz del taller):   uv run python herramientas/generar_datos_cierre.py
"""

import json
from pathlib import Path

import numpy as np
from llama_cpp import Llama
from scipy.special import softmax

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "clases" / "datos_cierre.js"

# Lo que lee el modelo antes de escribir. Se le agrega un espacio, como en el ejercicio 04.
TEXTO = "Llegamos al final del taller. Solo me queda decirles:"

# Lo que escribió el modelo al sortear sin máscara, token por token (temperatura 1.0).
# Se eligió entre 40 sorteos, y se guarda acá para que la diapositiva muestre siempre lo mismo.
SIN_MASCARA = ["9", "2", "0", "0", " euros"]

# Lo que tiene que salir con la máscara. No tiene ni «L» ni «D», así que en el
# formato del ejercicio 04 cada carácter es un símbolo exacto.
FORMATO = "Muchas gracias"

FILAS = 5  # cuántos tokens se muestran en cada paso, además de «el resto»

# verbose=False: que la librería no llene la pantalla con sus mensajes internos.
# logits_all=True: que la librería guarde los logits después de leer.
modelo = Llama(str(RAIZ / "modelos" / "Qwen3.5-2B-Q4_K_M.gguf"), logits_all=True, verbose=False)

# El texto que escribe cada token del vocabulario.
PIEZAS = [modelo.detokenize([token]).decode(errors="replace") for token in range(modelo.n_vocab())]


def leer_texto():
    """Borra lo anterior y hace que el modelo lea el texto de despedida."""
    modelo.reset()
    modelo.eval(modelo.tokenize((TEXTO + " ").encode()))


def mas_probables(probabilidades, cuantos):
    """Los números de los tokens más probables, del más probable al menos probable."""
    return [int(token) for token in np.argsort(probabilidades)[::-1][:cuantos]]


# ---------------------------------------------------------------- sin máscara
leer_texto()
pasos_sin_mascara = []
for pieza in SIN_MASCARA:
    probabilidades = softmax(modelo.scores[modelo.n_tokens - 1])
    elegido = PIEZAS.index(pieza)
    pasos_sin_mascara.append(
        {
            "elegido": pieza,
            "p_elegido": round(float(probabilidades[elegido]), 4),
            "filas": [
                {"pieza": PIEZAS[token], "p": round(float(probabilidades[token]), 4)}
                for token in mas_probables(probabilidades, FILAS)
            ],
        }
    )
    modelo.eval([elegido])

# ---------------------------------------------------------------- con máscara
leer_texto()
pasos_con_mascara = []
escrito = ""
while len(escrito) < len(FORMATO):
    logits = modelo.scores[modelo.n_tokens - 1]

    # La máscara: un token sirve si, agregado a lo escrito, sigue siendo el comienzo del formato.
    mascara = [pieza != "" and FORMATO.startswith(escrito + pieza) for pieza in PIEZAS]
    sin_mascara = softmax(logits)
    con_mascara = softmax(np.where(mascara, logits, -np.inf))

    # Sale el token más probable de los que deja pasar la máscara.
    elegido = int(np.argmax(con_mascara))

    # Las filas que se muestran: los tres favoritos del modelo y los dos mejores
    # de los que pasan la máscara. Si se repiten, se completa con más favoritos.
    filas = []
    candidatos = mas_probables(sin_mascara, 3) + mas_probables(con_mascara, 2) + mas_probables(sin_mascara, FILAS + 2)
    for token in candidatos:
        if token not in filas and len(filas) < FILAS:
            # Un token que la máscara tapó no entra como «uno de los que pasan».
            filas.append(token)
    # Se ordenan como las ve el modelo: de la más probable a la menos probable, sin máscara.
    filas.sort(key=lambda token: -sin_mascara[token])

    pasos_con_mascara.append(
        {
            "elegido": PIEZAS[elegido],
            "pasan": int(sum(mascara)),
            "filas": [
                {
                    "pieza": PIEZAS[token],
                    "p": round(float(sin_mascara[token]), 4),
                    "pasa": bool(mascara[token]),
                    "con": round(float(con_mascara[token]), 4),
                }
                for token in filas
            ],
        }
    )
    escrito = escrito + PIEZAS[elegido]
    modelo.eval([elegido])

datos = {
    "modelo": "Qwen3.5-2B",
    "texto": TEXTO + " ",
    "vocabulario": modelo.n_vocab(),
    "formato": FORMATO,
    "sin_mascara": pasos_sin_mascara,
    "con_mascara": pasos_con_mascara,
}
DESTINO.write_text(
    "// Generado por herramientas/generar_datos_cierre.py. No editar a mano.\n"
    f"window.DATOS_CIERRE = {json.dumps(datos, ensure_ascii=False, indent=1)};\n",
    encoding="utf-8",
)

print(f"Guardado {DESTINO.relative_to(RAIZ)}")
print("Sin máscara:", TEXTO, "".join(paso["elegido"] for paso in pasos_sin_mascara))
for paso in pasos_sin_mascara:
    print("   ", repr(paso["elegido"]), paso["p_elegido"], "| favoritos:", [(f["pieza"], f["p"]) for f in paso["filas"]])
print("Con máscara:", TEXTO, escrito)
for paso in pasos_con_mascara:
    print("   ", repr(paso["elegido"]), "| pasan", paso["pasan"], "|", [(f["pieza"], f["p"], f["con"] if f["pasa"] else "tapado") for f in paso["filas"]])
