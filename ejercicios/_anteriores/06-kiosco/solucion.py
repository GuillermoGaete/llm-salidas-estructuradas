"""SOLUCIÓN del ejercicio 06 — Mini proyecto: el tomador de pedidos del kiosco.

Llega un mensaje de WhatsApp y el programa tiene que calcular cuánto cobrar.
El modelo convierte el mensaje en datos; la cuenta la hace Python.

Cómo correrlo:   uv run python ejercicio.py
"""

from typing import Literal

from pydantic import BaseModel

from taller import armar_prompt, cargar_modelo

modelo = cargar_modelo("mediano")

PRECIOS = {
    "empanada de carne": 1200,
    "empanada de pollo": 1200,
    "empanada de jamón y queso": 1300,
    "coca": 2500,
    "agua": 1500,
}

INSTRUCCIONES = (
    "Sos el asistente de un kiosco. Extraé el pedido del mensaje del cliente. "
    f"Menú: {', '.join(PRECIOS)}. Incluí solo lo que el cliente pidió."
)
EJEMPLOS = [
    (
        "tres de pollo y dos aguas",
        '{"items": [{"producto": "empanada de pollo", "cantidad": 3}, {"producto": "agua", "cantidad": 2}]}',
    ),
]


# ---------------------------------------------------------------------------
# PASO 1 — El esquema del pedido
#
# Un Item tiene:    producto  (solo puede ser uno de los 5 del menú → Literal)
#                   cantidad  (un número entero)
# Un Pedido tiene:  items     (una lista de Item → list[Item])
# ---------------------------------------------------------------------------
class Item(BaseModel):
    producto: Literal[
        "empanada de carne", "empanada de pollo", "empanada de jamón y queso", "coca", "agua"
    ]
    cantidad: int


class Pedido(BaseModel):
    items: list[Item]


# ---------------------------------------------------------------------------
# PASO 2 — Del mensaje al pedido
#
# 1. Armá el prompt con armar_prompt(INSTRUCCIONES, mensaje, EJEMPLOS)
# 2. Llamá al modelo con el prompt y Pedido como tipo de salida (max_tokens=200)
# 3. Convertí la respuesta con Pedido.model_validate_json(...) y devolvela
# ---------------------------------------------------------------------------
def tomar_pedido(mensaje):
    prompt = armar_prompt(INSTRUCCIONES, mensaje, EJEMPLOS)
    respuesta = modelo(prompt, Pedido, max_tokens=200)
    return Pedido.model_validate_json(respuesta)


# ---------------------------------------------------------------------------
# PASO 3 — La cuenta la hace Python, no el modelo
#
# Sumá precio × cantidad de cada item del pedido.
# El precio de un item está en PRECIOS[item.producto]
# ---------------------------------------------------------------------------
def total(pedido):
    return sum(PRECIOS[item.producto] * item.cantidad for item in pedido.items)


def atender(mensaje):
    pedido = tomar_pedido(mensaje)
    print(f"\nCliente: «{mensaje}»")
    for item in pedido.items:
        print(f"  {item.cantidad:>3} × {item.producto}")
    print(f"  Total: ${total(pedido)}")


if __name__ == "__main__":
    try:
        if set(Item.model_fields) != {"producto", "cantidad"} or set(Pedido.model_fields) != {"items"}:
            raise NotImplementedError("PASO 1: completá las clases Item y Pedido")
        prueba = Pedido(items=[Item(producto="coca", cantidad=2), Item(producto="agua", cantidad=1)])
        atender("Hola, mandame dos de carne y una coca")
        assert total(prueba) == 6500, f"2 cocas y 1 agua son $6500, no ${total(prueba)}"
        print("\n✅ Pasos 1, 2 y 3 correctos")
    except NotImplementedError as falta:
        raise SystemExit(f"⏳ Todavía falta → {falta}")

    atender("Buenas! quiero 3 de carne, 6 de pollo y dos cocas")
    atender("una de jamón y queso y un agua porfa")

    # PASO 4 — Tratá de romperlo (respuestas en el README):
    atender("quiero 400 empanadas de carne")
    atender("una docena de carne")
    atender("¿tienen empanadas de humita? dame dos")
    atender("hola, ¿cómo andan?")

    # PASO 5 — Atendé vos:
    while mensaje := input("\nEscribí un pedido (o Enter para salir): "):
        atender(mensaje)
