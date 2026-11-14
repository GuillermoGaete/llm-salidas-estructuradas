"""Ejercicio 02, parte 3 — Una inferencia completa, paso a paso.

Escribir un texto es repetir muchas veces lo mismo:
  1. el modelo le pone un logit a cada token,
  2. se sortea uno (como en la parte 2),
  3. ese token se agrega al texto, y se vuelve a empezar.

Cómo correrlo:   uv run python 3_generar.py
Qué hacer:       escribí un texto y mirá el resultado. Probá con varios; para salir, «chau».
"""

import numpy as np
from llama_cpp import Llama
from scipy.special import softmax

PASOS = 12         # cuántos tokens escribir

# Cargar el modelo.
# logits_all=True: que la librería guarde los logits después de leer.
# Si no se lo pedimos, no los guarda (para ahorrar memoria).
# verbose=False: que la librería no llene la pantalla con sus mensajes internos.
modelo = Llama("../../modelos/Qwen3-0.6B-Q4_K_M.gguf", logits_all=True, verbose=False)
# Pedirle al usuario un texto, y repetir hasta que escriba "chau".
texto = input("Escribí un texto (si queres salir escribi 'chau'): ")
while texto != "chau":
    # modelo.reset() borra lo que el modelo leyó en la vuelta anterior.
    # Sin esto, cada texto nuevo se sumaría a los anteriores.
    modelo.reset()

    tokens = modelo.tokenize(texto.encode("utf-8"))
    modelo.eval(tokens)

    elegidos = []
    for paso in range(1, PASOS + 1):
        # 1. Los logits del próximo token, y sus probabilidades.
        logits = modelo.scores[modelo.n_tokens - 1]
        probabilidades = softmax(logits)

        # 2. El sorteo.
        #    Los cuatro valores apagan los ajustes que la librería trae prendidos, para que
        #    cada token salga exactamente con la probabilidad que le dio el modelo:
        #      temp=1.0   no cambia las probabilidades (por defecto es 0.8)
        #      top_k=0    no descarta ningún token (por defecto se queda con los 40 mejores)
        #      top_p=1.0  no descarta ningún token (por defecto es 0.95)
        #      min_p=0    no descarta ningún token (por defecto es 0.05)
        elegido = modelo.sample(temp=0.2, top_k=0, top_p=1.0, min_p=0)
        if elegido == modelo.token_eos():  # el modelo eligió el token «terminé»
            break

        # Mostrar los tres favoritos del modelo y cuál salió sorteado.
        # errors="replace": algunos tokens son solo una parte de una letra o de un
        # emoji. En ese caso se muestra � en vez de dar un error.
        print(f"Paso {paso}. Favoritos:", end=" ")
        # Ordenar los tokens del logit más alto al más bajo, y quedarse con los primeros.
        orden = np.argsort(logits)   # los números de token, del logit más bajo al más alto
        orden = orden[::-1]          # se da vuelta la lista: ahora va del más alto al más bajo
        mejores = orden[:3]           # se toman los primeros 3
        for token in mejores:
            pedacito = modelo.detokenize([token]).decode("utf-8", errors="replace")
            print(f"{pedacito!r} {probabilidades[token]:.0%}", end="  ")
        pedacito = modelo.detokenize([elegido]).decode("utf-8", errors="replace")
        print(f"→ salió {pedacito!r}")

        # 3. Agregar el token elegido: ahora el modelo también lo lee.
        elegidos.append(elegido)
        modelo.eval([elegido])

    print()
    print(texto + modelo.detokenize(elegidos).decode("utf-8", errors="replace"))

    texto = input("\nEscribí un texto (si queres salir escribi 'chau'): ")
