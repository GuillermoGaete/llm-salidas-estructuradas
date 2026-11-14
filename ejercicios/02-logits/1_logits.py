"""Ejercicio 02, parte 1 — Logits y probabilidades.

El modelo lee un texto y le pone un puntaje a CADA token del vocabulario:
«¿qué tan bien queda este token como el próximo?». Esos puntajes son los
LOGITS. Las probabilidades son los mismos logits, pasados por la función
softmax para que sean todos positivos y sumen 1.

Cómo correrlo:   uv run python 1_logits.py
Qué hacer:       escribí un texto y mirá el resultado. Probá con varios; para salir, «chau».
"""

import numpy as np
from llama_cpp import Llama
from scipy.special import softmax

CUANTOS = 15  # cuántos tokens mostrar

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

    # 2. Tokenizar el texto y hacer que el modelo lo lea.
    tokens = modelo.tokenize(texto.encode())

    print("Texto: ", texto)
    print("Tokens:", tokens)

    #    eval es la línea que LLAMA AL MODELO: acá es donde se hace la inferencia.
    #    Los tokens entran a la red neuronal, que hace todas sus cuentas y deja
    #    calculados los logits del próximo token. Es la línea que más tarda.
    #    No devuelve nada: los logits quedan guardados en modelo.scores.
    modelo.eval(tokens)

    # 3. Los logits del PRÓXIMO token: un número por cada token del vocabulario.
    logits = modelo.scores[modelo.n_tokens - 1]
    print("Cantidad de logits:", len(logits))

    # 4. De logits a probabilidades.
    probabilidades = softmax(logits)
    print("Suma de las probabilidades:", probabilidades.sum())

    # 5. Mostrar los tokens con el logit más alto.
    #    errors="replace": algunos tokens son solo una parte de una letra o de un
    #    emoji. En ese caso se muestra � en vez de dar un error.
    # Ordenar los tokens del logit más alto al más bajo, y quedarse con los primeros.
    orden = np.argsort(logits)   # los números de token, del logit más bajo al más alto
    orden = orden[::-1]          # se da vuelta la lista: ahora va del más alto al más bajo
    mejores = orden[:CUANTOS]     # se toman los primeros CUANTOS
    print()
    print("token             logit  probabilidad")
    for token in mejores:
        pedacito = modelo.detokenize([token]).decode(errors="replace")
        barra = "█" * round(probabilidades[token] * 40)
        print(f"{pedacito!r:<14} {logits[token]:>8.2f} {probabilidades[token]:>8.2%}  {barra}")

    # 6. Y el token con el logit más bajo de todos.
    peor = np.argmin(logits)
    pedacito = modelo.detokenize([peor]).decode(errors="replace")
    print("...")
    print(f"{pedacito!r:<14} {logits[peor]:>8.2f} {probabilidades[peor]:>8.2%}")

    texto = input("\nEscribí un texto (si queres salir escribi 'chau'): ")

# ---------------------------------------------------------------------------
# ANEXO — Cómo se lee la línea que imprime cada fila de la tabla
#
#   print(f"{pedacito!r:<14} {logits[token]:>8.2f} {probabilidades[token]:>8.2%}  {barra}")
#
# La f antes de las comillas quiere decir «texto con huecos». Cada par de
# llaves { } es un hueco: Python pone ahí el valor de lo que está adentro.
# Lo que viene después de los dos puntos dice CÓMO mostrar ese valor.
#
#   {pedacito!r:<14}
#       pedacito   el texto del token
#       !r         mostrarlo entre comillas, para que se vean los espacios:
#                  ' pizza' en vez de  pizza
#       <14        ocupar 14 lugares, con el texto pegado a la izquierda
#
#   {logits[token]:>8.2f}
#       logits[token]   el logit de ese token
#       >8              ocupar 8 lugares, con el número pegado a la derecha
#       .2f             mostrarlo con 2 decimales:  15.18
#
#   {probabilidades[token]:>8.2%}
#       probabilidades[token]   la probabilidad de ese token (entre 0 y 1)
#       >8                      ocupar 8 lugares, pegado a la derecha
#       .2%                     mostrarlo como porcentaje con 2 decimales:
#                               0.278 se ve como 27.80%
#
#   {barra}
#       la barra de bloques █, tal cual, sin ningún formato
#
# Los anchos fijos (14, 8, 8) son los que hacen que las filas queden
# alineadas en columnas, una debajo de la otra.
# ---------------------------------------------------------------------------
