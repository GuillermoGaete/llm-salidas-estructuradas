"""Ejercicio 01 — Tokens.

Un modelo de lenguaje no lee letras ni palabras: lee TOKENS, pedacitos de
texto. Cada token tiene un número, y el modelo solo ve esos números.

Cómo correrlo:   uv run python tokens.py
Qué hacer:       cambiá TEXTO, guardá y corrélo de nuevo.
"""

from llama_cpp import Llama

# 1. Cargar el modelo.
#    verbose=False: que la librería no llene la pantalla con sus mensajes internos.
# Otros modelos:
#  Qwen3-1.7B-Q4_K_M.gguf
#  SmolLM2-135M-Instruct-Q4_K_M.gguf
modelo = Llama("../../modelos/SmolLM2-135M-Instruct-Q4_K_M.gguf", verbose=False)

# 2. Pedirle al usuario un texto, y repetir hasta que escriba "chau".
texto = input("Escribí un texto (si queres salir escribi 'chau'): ")
while texto != "chau":
    # 3. Tokenizar: de texto a números. (La librería pide el texto en bytes.)
    tokens = modelo.tokenize(texto.encode())

    print("Texto: ", texto)
    print("Tokens:", tokens)
    print("Son", len(tokens), "tokens. El vocabulario del modelo tiene", modelo.n_vocab())

    # 4. Ver qué pedacito de texto es cada número.
    #    errors="replace": algunos tokens son solo una parte de una letra o de un
    #    emoji. En ese caso se muestra en vez de dar un error.
    for token in tokens:
        pedacito = modelo.detokenize([token]).decode(errors="replace")
        print(token, repr(pedacito))

    # 5. El camino de vuelta: de números a texto.
    print("De vuelta:", modelo.detokenize(tokens).decode())

    texto = input("\nEscribí un texto (si queres salir escribi 'chau'): ")  
