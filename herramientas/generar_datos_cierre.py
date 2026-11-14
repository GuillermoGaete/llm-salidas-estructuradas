"""Genera clases/datos_cierre.js: los datos de la última diapositiva.

En esa diapositiva se le pide al modelo «Agradece al público presente», y el
modelo responde dos veces, de a una palabra por paso:

  1. Sin máscara. Es lo que salió en un sorteo real (ver SEMILLA_SIN_MASCARA).
  2. Con la máscara del ejercicio 04 (mascara_v2.py), con FORMATO = "Muchas gracias".

El modelo no elige palabras sino tokens. Para que la diapositiva se pueda leer
con palabras, cada token candidato se completa hasta terminar la palabra, igual
que en la primera diapositiva del LLM. La probabilidad que se muestra es la del
token real con el que empieza la palabra.

Cómo correrlo (desde la raíz del taller):   uv run python herramientas/generar_datos_cierre.py
"""

import json
import random
from pathlib import Path

import numpy as np
from llama_cpp import Llama
from scipy.special import softmax

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "clases" / "datos_cierre.js"

# Lo que se le pide al modelo.
ENTRADA = "Agradece al público presente"

# La respuesta sin máscara sale de un sorteo con temperatura 1.0. Con esta semilla el
# modelo responde «Obrigado(a)!». Se eligió entre 40 sorteos; otros empiezan con
# «Como modelo de lenguaje, no puedo…» (semilla 0) o «Claro que sí. Aquí tienes…» (semilla 11).
SEMILLA_SIN_MASCARA = 1
PALABRAS_SIN_MASCARA = 1  # cuántas palabras de esa respuesta se muestran

# Lo que tiene que salir con la máscara. No tiene ni «L» ni «D», así que en el
# formato del ejercicio 04 cada carácter es un símbolo exacto.
FORMATO = "Muchas gracias"

FILAS = 5   # cuántas palabras se muestran en cada paso, además de «el resto»
MIRAR = 12  # cuántos tokens candidatos se completan hasta formar una palabra

# logits_all=True: que la librería guarde los logits después de leer.
# verbose=False: que la librería no llene la pantalla con sus mensajes internos.
modelo = Llama(str(RAIZ / "modelos" / "Qwen3.5-2B-Q4_K_M.gguf"), logits_all=True, verbose=False)

# El texto que escribe cada token del vocabulario.
PIEZAS = [modelo.detokenize([token]).decode(errors="replace") for token in range(modelo.n_vocab())]

# La entrada, escrita como una conversación: es el mismo texto que arma la librería
# en el ejercicio 03. special=True: que las marcas se lean como tokens especiales.
BASE = modelo.tokenize(
    ("<|im_start|>user\n" + ENTRADA + "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n").encode(),
    special=True,
)


def leer(respuesta):
    """Borra lo anterior y hace que el modelo lea la entrada y lo que ya respondió."""
    modelo.reset()
    modelo.eval(BASE + respuesta)


def probabilidades():
    """Las probabilidades del próximo token, tal como las da el modelo."""
    return softmax(modelo.scores[modelo.n_tokens - 1])


def empieza_otra_palabra(token):
    """Verdadero si con este token empieza una palabra nueva, o si la respuesta terminó."""
    pieza = PIEZAS[token]
    return token == modelo.token_eos() or pieza == "" or pieza[0] in " \n"


def palabras_candidatas(respuesta):
    """Las palabras que el modelo prefiere para seguir, de la más probable a la menos probable.

    Cada token candidato se completa hasta terminar la palabra, siguiendo siempre
    con el token más probable. Si dos tokens llevan a la misma palabra, se suman.
    """
    leer(respuesta)
    p = probabilidades()
    suma = {}
    for token in np.argsort(p)[::-1][:MIRAR]:
        token = int(token)
        leer(respuesta + [token])
        piezas = [PIEZAS[token]]
        for _ in range(8):
            siguiente = int(np.argmax(modelo.scores[modelo.n_tokens - 1]))
            if empieza_otra_palabra(siguiente):
                break
            piezas.append(PIEZAS[siguiente])
            modelo.eval([siguiente])
        palabra = "".join(piezas).strip()
        if palabra != "":
            suma[palabra] = suma.get(palabra, 0) + float(p[token])
    return sorted(suma.items(), key=lambda par: -par[1])


def armar_filas(candidatas, palabra, p_palabra):
    """Las filas de un paso: las palabras favoritas del modelo, con la que salió incluida."""
    filas = dict(candidatas[:FILAS])
    if palabra not in filas:
        # La palabra que salió no está entre las favoritas: entra en lugar de la última.
        filas = dict(candidatas[: FILAS - 1])
        filas[palabra] = p_palabra
    ordenadas = sorted(filas.items(), key=lambda par: -par[1])
    return [{"palabra": nombre, "p": round(p, 4)} for nombre, p in ordenadas]


# ---------------------------------------------------------------- sin máscara
azar = random.Random(SEMILLA_SIN_MASCARA)
respuesta = []       # los tokens que ya salieron
pendiente = None     # el token con el que empieza la palabra siguiente, si ya se sorteó
pasos_sin_mascara = []
for numero in range(PALABRAS_SIN_MASCARA):
    candidatas = palabras_candidatas(respuesta)
    leer(respuesta)
    p = probabilidades()
    primero = pendiente if pendiente is not None else azar.choices(range(len(PIEZAS)), weights=p)[0]
    if primero == modelo.token_eos():
        break
    tokens = [primero]
    modelo.eval([primero])
    # Se sigue sorteando hasta que salga un token que empieza otra palabra.
    while True:
        siguiente = azar.choices(range(len(PIEZAS)), weights=probabilidades())[0]
        if empieza_otra_palabra(siguiente):
            pendiente = siguiente
            break
        tokens.append(siguiente)
        modelo.eval([siguiente])
    palabra = "".join(PIEZAS[token] for token in tokens).strip()
    pasos_sin_mascara.append(
        {
            "elegida": palabra,
            "tokens": [PIEZAS[token] for token in tokens],
            "filas": armar_filas(candidatas, palabra, float(p[primero])),
        }
    )
    respuesta = respuesta + tokens

# ---------------------------------------------------------------- con máscara
respuesta = []
escrito = ""
objetivo = ""
pasos_con_mascara = []
for palabra in FORMATO.split(" "):
    # Lo que tiene que quedar escrito cuando termine este paso.
    objetivo = palabra if objetivo == "" else objetivo + " " + palabra
    candidatas = palabras_candidatas(respuesta)
    leer(respuesta)
    tokens = []
    p_antes = None
    pasan = None
    # Se escribe la palabra token por token, con la máscara del ejercicio 04:
    # un token sirve si, agregado a lo escrito, sigue siendo el comienzo de lo que tiene que quedar.
    while escrito != objetivo:
        logits = modelo.scores[modelo.n_tokens - 1]
        mascara = np.array([pieza != "" and objetivo.startswith(escrito + pieza) for pieza in PIEZAS])
        sin_mascara = softmax(logits)
        con_mascara = softmax(np.where(mascara, logits, -np.inf))
        if p_antes is None:
            # Antes de la máscara: lo que suman los tokens con los que puede empezar esta palabra.
            p_antes = float(sin_mascara[mascara].sum())
            pasan = int(mascara.sum())
        elegido = int(np.argmax(con_mascara))  # sale el más probable de los que pasan
        tokens.append(elegido)
        escrito = escrito + PIEZAS[elegido]
        modelo.eval([elegido])
    filas = armar_filas(candidatas, palabra, p_antes)
    for fila in filas:
        fila["pasa"] = fila["palabra"] == palabra
    pasos_con_mascara.append(
        {
            "elegida": palabra,
            "tokens": [PIEZAS[token] for token in tokens],
            "pasan": pasan,
            "filas": filas,
        }
    )
    respuesta = respuesta + tokens

datos = {
    "modelo": "Qwen3.5-2B",
    "entrada": ENTRADA,
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
print("Entrada:", ENTRADA)
print("Sin máscara:", " ".join(paso["elegida"] for paso in pasos_sin_mascara))
for paso in pasos_sin_mascara:
    print("   ", repr(paso["elegida"]), paso["tokens"], "|", [(f["palabra"], f["p"]) for f in paso["filas"]])
print("Con máscara:", escrito)
for paso in pasos_con_mascara:
    print("   ", repr(paso["elegida"]), paso["tokens"], "| tokens que pasan:", paso["pasan"], "|", [(f["palabra"], f["p"], "pasa" if f["pasa"] else "tapada") for f in paso["filas"]])
