"""Gancho — Le pedimos JSON a un modelo 10 veces. ¿Cuántas veces cumple?

No hay nada para completar: se corre y se mira.

Cómo correrlo:   uv run python gancho.py
"""

import json

from taller import armar_prompt, cargar_modelo

INSTRUCCIONES = (
    "Sos el asistente de un kiosco. Extraé el pedido del mensaje del cliente. "
    "Menú: empanada de carne, empanada de pollo, coca, agua. "
    'Respondé SOLO con JSON, con esta forma: {"items": [{"producto": "...", "cantidad": 1}]}'
)
MENSAJE = "Hola, mandame dos de carne y una coca"

if __name__ == "__main__":
    modelo = cargar_modelo("chico")
    prompt = armar_prompt(INSTRUCCIONES, MENSAJE)

    print(f"Cliente: «{MENSAJE}»\n")
    funcionaron = 0
    for intento in range(1, 11):
        # Sin tipo de salida: el modelo escribe lo que quiere.
        respuesta = modelo(prompt, max_tokens=300, temperature=1.0, seed=intento)
        try:
            pedido = json.loads(respuesta)  # lo que haría el programa del kiosco
            funcionaron += 1
            print(f"{intento:>2}. ✅ {pedido}")
        except json.JSONDecodeError as error:
            print(f"{intento:>2}. 💥 el programa se rompió: {error}")
            print(f"      el modelo escribió: {respuesta!r}")

    print(f"\nFuncionó {funcionaron} de 10 veces.")
    print("¿Cómo hacemos para que algo que tira dados cumpla SIEMPRE?")
