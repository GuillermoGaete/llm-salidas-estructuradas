"""SOLUCIÓN del ejercicio 05 — Lo mismo, con una librería: Outlines.

En el ejercicio 04 escribiste la máscara a mano. Outlines hace eso mismo,
rápido y para formatos mucho más complicados. Se usa así:

    respuesta = modelo(prompt, tipo_de_salida)

Cómo correrlo:   uv run python ejercicio.py
(La primera respuesta tarda unos 20 segundos: Outlines prepara el autómata.)
"""

from typing import Literal

from outlines.types import Regex
from pydantic import BaseModel

from taller import armar_prompt, cargar_modelo

modelo = cargar_modelo("mediano")

INSTRUCCIONES = (
    "Sos el asistente de un kiosco. Clasificá el mensaje del cliente como "
    "pedido (quiere comprar), consulta (pregunta algo) o reclamo (se queja)."
)
EJEMPLOS = [
    ("Quiero tres empanadas de pollo", "pedido"),
    ("¿Tienen empanadas de verdura?", "consulta"),
    ("El pedido llegó incompleto", "reclamo"),
]


# ---------------------------------------------------------------------------
# PASO 1 — Lista cerrada: el LLM vuelve a ser un clasificador
#
# El tipo Literal["a", "b"] significa «solo puede salir a o b».
# Llamá al modelo con el prompt y un Literal con las tres clases,
# y devolvé la respuesta.
# ---------------------------------------------------------------------------
def clasificar(mensaje):
    prompt = armar_prompt(INSTRUCCIONES, mensaje, EJEMPLOS)
    return modelo(prompt, Literal["pedido", "consulta", "reclamo"])


# ---------------------------------------------------------------------------
# PASO 2 — Expresión regular: el formato «LL DDD LL» escrito como regex
#
#   [A-Z]   una letra mayúscula        [0-9]   un dígito
#   {2}     «repetido 2 veces»         un espacio es un espacio
#
# Completá la regex de la patente y devolvé lo que responde el modelo.
# Se usa así: modelo(prompt, Regex(r"..."), max_tokens=20)
# ---------------------------------------------------------------------------
def inventar_patente():
    prompt = armar_prompt("Respondé solo con lo que te piden.", "Inventá una patente argentina.")
    return modelo(prompt, Regex(r"[A-Z]{2} [0-9]{3} [A-Z]{2}"), max_tokens=20)


# ---------------------------------------------------------------------------
# PASO 3 — Un esquema: varios datos juntos, cada uno con su tipo
#
# Completá la clase Producto con tres campos:
#     nombre: str
#     precio: int
#     categoria: Literal["comida", "bebida", "golosina"]
# ---------------------------------------------------------------------------
class Producto(BaseModel):
    nombre: str
    precio: int
    categoria: Literal["comida", "bebida", "golosina"]


def inventar_producto(pista):
    prompt = armar_prompt("Inventá un producto para vender en un kiosco argentino.", pista)
    respuesta = modelo(prompt, Producto, max_tokens=100)  # un texto con forma de JSON
    return Producto.model_validate_json(respuesta)        # un objeto de Python


if __name__ == "__main__":
    try:
        for mensaje in [
            "Hola, mandame dos de carne y una coca",
            "¿Hasta qué hora abren?",
            "Las empanadas llegaron frías y tarde",
            "che, me vino todo helado",
            "hola",
        ]:
            clase = clasificar(mensaje)
            assert clase in ("pedido", "consulta", "reclamo"), f"salió {clase!r}"
            print(f"  {clase:<9} ← «{mensaje}»")
        print("✅ Paso 1 correcto\n")

        for _ in range(3):
            patente = inventar_patente()
            assert len(patente) == 9 and patente[2] == " " and patente[3:6].isdigit(), f"salió {patente!r}"
            print(f"  {patente}")
        print("✅ Paso 2 correcto\n")

        if set(Producto.model_fields) != {"nombre", "precio", "categoria"}:
            raise NotImplementedError("PASO 3: completá la clase Producto")
        for pista in ["algo dulce", "algo para tomar", "algo salado"]:
            producto = inventar_producto(pista)
            print(f"  {pista}: {producto.nombre} (${producto.precio}, {producto.categoria})")
        print("✅ Paso 3 correcto")
    except NotImplementedError as falta:
        raise SystemExit(f"⏳ Todavía falta → {falta}")
