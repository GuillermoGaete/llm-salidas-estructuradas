"""Ejercicio 04, segunda parte — Tu máscara sobre un modelo real.

Usa TUS funciones de ejercicio.py. Lo único que cambia es el vocabulario:
en vez de 37 tokens de juguete, los ~150.000 del modelo.

Cómo correrlo:   uv run python con_modelo.py
"""

import ejercicio
from ejercicio import elegir, enmascarar, probar_token, softmax

from taller import Modelo

TEXTO = "La patente de mi auto es: "
ejercicio.FORMATO = "LL DDD LL"  # probá "DD/DD/DDDD" con TEXTO = "Mi cumpleaños es el "


def escribir(modelo, vocabulario):
    modelo.empezar(TEXTO)
    escrito = ""
    estado = 0
    while estado < len(ejercicio.FORMATO):
        permitido = [probar_token(estado, pieza) is not None for pieza in vocabulario]
        logits = enmascarar(modelo.logits(), permitido)
        token = elegir(softmax(logits))
        print(f"  quedan {sum(permitido):>5} tokens vivos de {len(vocabulario)} → sale {vocabulario[token]!r}")
        escrito += vocabulario[token]
        estado = probar_token(estado, vocabulario[token])
        modelo.agregar(token)
    return escrito


if __name__ == "__main__":
    modelo = Modelo("chico")
    vocabulario = modelo.vocabulario()
    try:
        for _ in range(3):
            print(f"{TEXTO}▸{escribir(modelo, vocabulario)}\n")
    except NotImplementedError as falta:
        raise SystemExit(f"⏳ Primero terminá ejercicio.py → {falta}")
