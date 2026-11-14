"""Ejercicio 06 — El tomador de pedidos del kiosco.

Juntamos todo. Llega un mensaje de WhatsApp y el programa calcula cuánto cobrar.

    «mandame dos de carne y una coca»
            │  el modelo, con un esquema: escribe un JSON que el programa puede leer
            ▼
    {"items": [{"producto": "empanada de carne", "cantidad": 2}, {"producto": "coca", "cantidad": 1}]}
            │  Python: busca los precios y hace la cuenta
            ▼
    Total: $4900

El modelo hace una sola cosa: convertir el mensaje en datos. La cuenta la hace
Python.

Cómo correrlo:   uv run python kiosco.py
Qué hacer:       escribí el pedido de un cliente y mirá el resultado. Probá con varios; para salir, «chau».
"""

import json
import random
from typing import Literal

import outlines
from llama_cpp import Llama
from outlines.inputs import Chat
from pydantic import BaseModel

TEMPERATURA = 0.2   # baja: para sacar datos de un mensaje conviene que salga casi siempre lo más probable

# El menú del kiosco: cada producto con su precio.
PRECIOS = {
    "empanada de carne": 1200,
    "empanada de pollo": 1200,
    "empanada de jamón y queso": 1300,
    "coca": 2500,
    "agua": 1500,
}


# El formato: un esquema, como en la parte 3 del ejercicio 05.
# Un pedido es una lista de items. Cada item es un producto y una cantidad.
class Item(BaseModel):
    # Literal[...]: solo puede ser uno de estos textos, y ningún otro.
    # tuple(PRECIOS) son los nombres de los productos del menú.
    producto: Literal[tuple(PRECIOS)]
    cantidad: int   # un número entero


class Pedido(BaseModel):
    items: list[Item]   # una lista de items

# Lo que le pedimos al modelo. El menú se arma con los nombres de PRECIOS.
INSTRUCCIONES = (
    "Sos el asistente de un kiosco. Extraé el pedido del mensaje del cliente. "
    "Menú: " + ", ".join(PRECIOS) + ". Incluí solo lo que el cliente pidió."
)

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
    #    temperature: por defecto esta función usa 0.2. Se pasa igual, para poder
    #    cambiarla desde arriba.
    respuesta = modelo(
        Chat([
            {"role": "system", "content": INSTRUCCIONES},
            {"role": "user", "content": mensaje},
        ]),
        Pedido,
        temperature=TEMPERATURA,
    )

    # 3. Lo que escribió el modelo es un texto con forma de JSON.
    #    json.loads lo convierte en un diccionario de Python.
    print("El modelo escribió:", respuesta)
    pedido = json.loads(respuesta)

    # 4. La cuenta la hace Python, no el modelo.
    total = 0
    for item in pedido["items"]:
        producto = item["producto"]
        cantidad = item["cantidad"]

        # PRECIOS[producto] no puede dar error: la máscara solo deja escribir
        # productos del menú.
        subtotal = PRECIOS[producto] * cantidad
        print(f"  {cantidad:>3} × {producto:<26} ${subtotal}")
        total = total + subtotal

    print(f"  Total: ${total}")

    mensaje = input("\nEscribí el pedido de un cliente (si queres salir escribi 'chau'): ")
