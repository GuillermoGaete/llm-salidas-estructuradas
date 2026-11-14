"""Ejercicio 02, parte 2 — El sorteo.

El modelo no elige siempre el token más probable: SORTEA. Es un dado
cargado, donde cada token tiene su probabilidad de salir.

Cómo correrlo:   uv run python 2_muestreo.py
Qué hacer:       escribí un texto y mirá el resultado. Probá con varios; para salir, «chau».
"""

from collections import Counter

import numpy as np
from llama_cpp import Llama
from scipy.special import softmax

TIRADAS = 200  # cuántas veces tirar el dado

# 1. Cargar el modelo.
#    logits_all=True: que la librería guarde los logits después de leer.
#    Si no se lo pedimos, no los guarda (para ahorrar memoria).
#    verbose=False: que la librería no llene la pantalla con sus mensajes internos.
modelo = Llama("../../modelos/granite-4.0-350m-Q4_K_M.gguf", logits_all=True, verbose=False)
# Pedirle al usuario un texto, y repetir hasta que escriba "chau".
texto = input("Escribí un texto (si queres salir escribi 'chau'): ")
while texto != "chau":
    # modelo.reset() borra lo que el modelo leyó en la vuelta anterior.
    # Sin esto, cada texto nuevo se sumaría a los anteriores.
    modelo.reset()

    tokens = modelo.tokenize(texto.encode())
    modelo.eval(tokens)

    # 2. Los logits del próximo token, y sus probabilidades.
    logits = modelo.scores[modelo.n_tokens - 1]
    probabilidades = softmax(logits)

    # 3. Mostrar los 10 tokens más probables.
    #    errors="replace": algunos tokens son solo una parte de una letra o de un
    #    emoji. En ese caso se muestra � en vez de dar un error.
    print("token          probabilidad")
    # Ordenar los tokens del logit más alto al más bajo, y quedarse con los primeros.
    orden = np.argsort(logits)   # los números de token, del logit más bajo al más alto
    orden = orden[::-1]          # se da vuelta la lista: ahora va del más alto al más bajo
    mejores = orden[:10]          # se toman los primeros 10
    for token in mejores:
        pedacito = modelo.detokenize([token]).decode(errors="replace")
        barra = "█" * round(probabilidades[token] * 40)
        print(f"{pedacito!r:<14} {probabilidades[token]:>7.1%}  {barra}")

    # 4. Tirar el dado varias veces. El sorteo lo hace la librería.
    #    Los cuatro valores apagan los ajustes que la librería trae prendidos, para que
    #    cada token salga exactamente con la probabilidad que le dio el modelo:
    #      temp=1.0   no cambia las probabilidades (por defecto es 0.8)
    #      top_k=0    no descarta ningún token (por defecto se queda con los 40 mejores)
    #      top_p=1.0  no descarta ningún token (por defecto es 0.95)
    #      min_p=0    no descarta ningún token (por defecto es 0.05)
    salieron = Counter()
    for _ in range(TIRADAS):
        token = modelo.sample(temp=1.0, top_k=0, top_p=1.0, min_p=0)
        salieron[token] += 1

    # 5. Contar qué salió. Lo esperable: cada token sale más o menos tantas veces
    #    como dice su probabilidad.
    print()
    print(f"{TIRADAS} tiradas. Salió:")
    for token, veces in salieron.most_common():
        pedacito = modelo.detokenize([token]).decode(errors="replace")
        print(f"{pedacito!r:<14} {veces / TIRADAS:>7.1%}  {'●' * round(veces / TIRADAS * 40)} {veces}")

    texto = input("\nEscribí un texto (si queres salir escribi 'chau'): ")
