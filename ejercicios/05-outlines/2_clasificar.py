"""Ejercicio 05, parte 2 — El programa del ejercicio 03, con una lista cerrada.

Es el mismo programa del comercio: clasifica el mensaje de un cliente muchas
veces y cuenta cuántas respuestas no esperaba.

Cambia una sola cosa. Al llamar al modelo se le pasa, además de los mensajes,
el FORMATO: la lista de las respuestas posibles. Outlines arma la máscara, y
el modelo no puede escribir nada que no esté en la lista.

Cómo correrlo:   uv run python 2_clasificar.py
Qué hacer:       escribí el mensaje de un cliente y mirá el resultado. Probá con varios; para salir, «chau».
"""

import random

import outlines
from llama_cpp import Llama
from outlines.inputs import Chat
from outlines.types import Choice

VECES = 20          # cuántas veces hacerle la misma pregunta al modelo
TEMPERATURA = 1.0   # 1.0: no cambia las probabilidades que da el modelo

# Lo que el programa sabe hacer con cada tipo de mensaje.
# Son las únicas cuatro respuestas que espera.
ACCIONES = {
    "reclamo": "se lo paso a una persona",
    "consulta": "le mando las preguntas frecuentes",
    "pedido": "lo anoto para la cocina",
    "saludo": "le devuelvo el saludo",
}

# El formato: la respuesta tiene que ser una de estas palabras, y ninguna otra.
FORMATO = Choice(["reclamo", "consulta", "pedido", "saludo"])

# Lo que le pedimos al modelo. Es lo mismo que en el ejercicio 03.
INSTRUCCIONES = (
    "Sos el asistente de un comercio. Clasificá el mensaje del cliente en una de "
    "estas categorías: reclamo, consulta, pedido, saludo. Respondé solo con la categoría."
)

# 1. Cargar el modelo y dárselo a Outlines.
#    seed: el número con el que arranca el sorteo. Acá va uno al azar. Si no se lo
#    pasamos, la librería arranca siempre con el mismo, y cada vez que se corre
#    el programa salen las mismas respuestas en el mismo orden.
#    verbose=False: que la librería no llene la pantalla con sus mensajes internos.
llama = Llama("../../modelos/Qwen3.5-2B-Q4_K_M.gguf", seed=random.randrange(2**32), verbose=False)
modelo = outlines.from_llamacpp(llama)

# Pedirle al usuario un mensaje, y repetir hasta que escriba "chau".
mensaje = input("Escribí el mensaje de un cliente (si queres salir escribi 'chau'): ")
while mensaje != "chau":
    no_esperadas = 0
    for intento in range(1, VECES + 1):
        # 2. Llamar al modelo con los mensajes y el formato.
        #    Chat([...]): los mismos dos mensajes del ejercicio 03, las
        #    instrucciones y el mensaje del cliente.
        #    FORMATO: lo nuevo. En el ejercicio 03 no se pasaba ningún formato.
        #    temperature: por defecto esta función usa 0.2.
        #    Outlines devuelve directamente el texto que escribió el modelo.
        categoria = modelo(
            Chat([
                {"role": "system", "content": INSTRUCCIONES},
                {"role": "user", "content": mensaje},
            ]),
            FORMATO,
            temperature=TEMPERATURA,
        )

        # 3. La misma comprobación del ejercicio 03.
        if categoria in ACCIONES:
            print(f"{intento:>2}. {categoria!r:<12} ✅ {ACCIONES[categoria]}")
        else:
            no_esperadas += 1
            print(f"{intento:>2}. {categoria!r:<12} ❌ el programa no sabe qué hacer con esto")

    # 4. Contar cuántas respuestas el programa no pudo usar.
    print()
    print(f"Respuestas que el programa no esperaba: {no_esperadas} de {VECES}.")

    mensaje = input("\nEscribí el mensaje de un cliente (si queres salir escribi 'chau'): ")
