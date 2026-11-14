"""Ejercicio 05, parte 1 — La patente, con una librería.

En el ejercicio 04 la máscara está escrita a mano. OUTLINES es una librería
que hace ese trabajo: recibe el formato, arma la máscara y la aplica en cada
paso, antes del sorteo.

A la librería se le pasan dos cosas, el texto y el formato:

    respuesta = modelo(texto, formato)

Acá el formato se escribe como una EXPRESIÓN REGULAR, que es la manera usual
de describir la forma de un texto:

    [A-Z]   una letra mayúscula
    [0-9]   un dígito
    {2}     lo anterior, repetido 2 veces
    el espacio es un espacio

Cómo correrlo:   uv run python 1_patente.py
Qué hacer:       corrélo. Después cambiá FORMATO, TEXTO o TEMPERATURA, guardá y corrélo de nuevo.
"""

import random

import outlines
from llama_cpp import Llama
from outlines.types import Regex

FORMATO = "[A-Z]{2} [0-9]{3} [A-Z]{2}"   # es el «LL DDD LL» del ejercicio 04
TEXTO = "La patente de mi auto es"       # lo que lee el modelo antes de escribir
TEMPERATURA = 1.0                        # 1.0: no cambia las probabilidades que da el modelo
VECES = 5                                # cuántas patentes pedir

# 1. Cargar el modelo, igual que en los ejercicios anteriores.
#    seed: el número con el que arranca el sorteo. Acá va uno al azar. Si no se lo
#    pasamos, la librería arranca siempre con el mismo, y cada vez que se corre
#    el programa salen las mismas respuestas en el mismo orden.
#    verbose=False: que la librería no llene la pantalla con sus mensajes internos.
llama = Llama("../../modelos/Qwen3.5-2B-Q4_K_M.gguf", seed=random.randrange(2**32), verbose=False)

# 2. Darle el modelo a Outlines. Devuelve el mismo modelo, con una manera nueva
#    de llamarlo: modelo(texto, formato).
#    chat_mode=False: que el modelo lea el texto tal cual. Si no se lo pedimos,
#    Outlines lo convierte en el mensaje de una conversación (eso es la parte 2).
modelo = outlines.from_llamacpp(llama, chat_mode=False)

# 3. Mostrar lo que se le pasa a la librería.
print("Texto:  ", TEXTO)
print("Formato:", FORMATO)

for intento in range(VECES):
    # 4. Llamar al modelo con el texto y el formato.
    #    Al texto se le agrega un espacio, para que lo que escriba no quede pegado.
    #    Regex(FORMATO): le avisa a Outlines que el formato es una expresión regular.
    #    temperature: por defecto esta función usa 0.8.
    #    max_tokens=40: por defecto la respuesta se corta a los 16 tokens, y un
    #    formato más largo quedaría por la mitad.
    respuesta = modelo(TEXTO + " ", Regex(FORMATO), temperature=TEMPERATURA, max_tokens=40)
    print("Salió:  ", respuesta)
