"""Ejercicio 05, parte 3 — Varios datos juntos: un esquema.

Un programa casi nunca necesita una sola palabra. Necesita varios datos, cada
uno de un tipo: un texto, un número, un sí o un no.

El formato para eso es un ESQUEMA: la lista de los datos, con el nombre y el
tipo de cada uno. Outlines hace que el modelo escriba un JSON con esos datos,
con esos nombres y con esos tipos.

Cómo correrlo:   uv run python 3_esquema.py
Qué hacer:       escribí el pedido de un cliente y mirá el resultado. Probá con varios; para salir, «chau».
"""

import json
import random

import outlines
from llama_cpp import Llama
from outlines.inputs import Chat
from pydantic import BaseModel

TEMPERATURA = 1.0   # 1.0: no cambia las probabilidades que da el modelo


# El formato: un esquema. Cada renglón es un dato, con su nombre y su tipo.
class Pedido(BaseModel):
    producto: str       # un texto
    cantidad: int       # un número entero
    para_llevar: bool   # verdadero o falso


# Lo que le pedimos al modelo.
INSTRUCCIONES = "Sos el asistente de un comercio. Extraé el pedido del mensaje del cliente."

# 1. Cargar el modelo y dárselo a Outlines.
#    seed: el número con el que arranca el sorteo. Acá va uno al azar. Si no se lo
#    pasamos, la librería arranca siempre con el mismo, y cada vez que se corre
#    el programa salen las mismas respuestas en el mismo orden.
#    verbose=False: que la librería no llene la pantalla con sus mensajes internos.
llama = Llama("../../modelos/Qwen3.5-2B-Q4_K_M.gguf", seed=random.randrange(2**32), verbose=False)
modelo = outlines.from_llamacpp(llama)

# Pedirle al usuario un pedido, y repetir hasta que escriba "chau".
mensaje = input("Escribí el pedido de un cliente (si queres salir escribi 'chau'): ")
while mensaje != "chau":
    # 2. Llamar al modelo con los mensajes y el formato.
    #    Pedido: el esquema de arriba. Es lo que se le pasa como formato.
    #    temperature: por defecto esta función usa 0.2.
    respuesta = modelo(
        Chat([
            {"role": "system", "content": INSTRUCCIONES},
            {"role": "user", "content": mensaje},
        ]),
        Pedido,
        temperature=TEMPERATURA,
    )

    # 3. Lo que escribió el modelo es un texto con forma de JSON.
    print("El modelo escribió:", respuesta)

    # 4. Convertir ese texto en un diccionario de Python, y usar cada dato.
    #    Los tres datos están siempre, con el nombre y el tipo del esquema.
    pedido = json.loads(respuesta)
    print("Producto:   ", pedido["producto"])
    print("Cantidad:   ", pedido["cantidad"])
    print("Para llevar:", pedido["para_llevar"])

    mensaje = input("\nEscribí el pedido de un cliente (si queres salir escribi 'chau'): ")
