"""Ejercicio 03 — Un LLM adentro de un programa.

Un LLM NO ES DETERMINISTA: la misma pregunta puede dar respuestas distintas,
y cada tanto da una que no esperábamos. Por eso, un programa que usa un LLM
tiene que COMPROBAR lo que el modelo devolvió antes de usarlo.

El ejemplo: un comercio recibe mensajes de sus clientes. El programa le pide
al modelo que diga de qué tipo es cada mensaje (reclamo, consulta, pedido o
saludo) y, según la respuesta, hace una cosa distinta.

Cómo correrlo:   uv run python clasificar.py
Qué hacer:       escribí el mensaje de un cliente y mirá el resultado. Probá con varios; para salir, «chau».
"""

import random

from llama_cpp import Llama

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

# Lo que le pedimos al modelo.
INSTRUCCIONES = (
    "Sos el asistente de un comercio. Clasificá el mensaje del cliente en una de "
    "estas categorías: reclamo, consulta, pedido, saludo. Respondé solo con la categoría."
)

# 1. Cargar el modelo.
#    logits_all=True: que la librería guarde los logits de cada token que escribe.
#    Sin esto no puede devolver los logprobs (da un error al pedirlos).
#    seed: el número con el que arranca el sorteo. Acá va uno al azar. Si no se lo
#    pasamos, la librería arranca siempre con el mismo, y cada vez que se corre
#    el programa salen las mismas respuestas en el mismo orden.
#    verbose=False: que la librería no llene la pantalla con sus mensajes internos.
modelo = Llama("../../modelos/Qwen3.5-2B-Q4_K_M.gguf", logits_all=True, seed=random.randrange(2**32), verbose=False)

# Pedirle al usuario un mensaje, y repetir hasta que escriba "chau".
mensaje = input("Escribí el mensaje de un cliente (si queres salir escribi 'chau'): ")
while mensaje != "chau":
    no_esperadas = 0
    for intento in range(1, VECES + 1):
        # 2. Pedirle al modelo que clasifique el mensaje.
        #    La librería arma el texto con las instrucciones y el mensaje, y hace
        #    todo lo del ejercicio 02: logits, sorteo, agregar el token y repetir.
        #    temperature: por defecto esta función usa 0.2, que hace salir casi
        #    siempre el token más probable. Con 1.0 las probabilidades no se cambian.
        #    max_tokens=20: cortar la respuesta a los 20 tokens. Una categoría es una
        #    sola palabra; si el modelo se pone a escribir de más, no lo esperamos.
        #    logprobs=True: que la respuesta traiga, por cada token que escribió, su
        #    logprob. Un logprob es el logaritmo de la probabilidad que tenía ese token;
        #    para volver a la probabilidad se usa math.exp(logprob): -0.29 es 75%.
        #    top_logprobs=5: además, los 5 tokens más probables en cada paso.
        #    Hay que pasar los dos: con logprobs=True solo, la librería no devuelve nada.
        #    Los logprobs salen de los logits tal cual: no cambian con la temperatura.
        #    Quedan en respuesta["choices"][0]["logprobs"]["content"], una entrada por token.
        respuesta = modelo.create_chat_completion(
            messages=[
                {"role": "system", "content": INSTRUCCIONES},
                {"role": "user", "content": mensaje},
            ],
            temperature=TEMPERATURA,
            max_tokens=20,
            logprobs=True,
            top_logprobs=5,
        )

        # 3. Sacar el texto que escribió el modelo.
        #    La respuesta trae varios datos más; el texto está en este lugar.
        print(respuesta)
        exit()
        categoria = respuesta["choices"][0]["message"]["content"]

        # 4. Comprobar lo que devolvió el modelo ANTES de usarlo.
        #    Sin esta comprobación, ACCIONES[categoria] da un error (KeyError)
        #    cuando la respuesta no es una de las cuatro, y el programa se corta.
        if categoria in ACCIONES:
            print(f"{intento:>2}. {categoria!r:<12} ✅ {ACCIONES[categoria]}")
        else:
            no_esperadas += 1
            print(f"{intento:>2}. {categoria!r:<12} ❌ el programa no sabe qué hacer con esto")

    # 5. Contar cuántas respuestas el programa no pudo usar.
    print()
    print(f"Respuestas que el programa no esperaba: {no_esperadas} de {VECES}.")

    mensaje = input("\nEscribí el mensaje de un cliente (si queres salir escribi 'chau'): ")
