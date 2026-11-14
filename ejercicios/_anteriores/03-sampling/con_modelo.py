"""Ejercicio 03, segunda parte — Tu sampling manejando un modelo real.

Usa TUS funciones de ejercicio.py para elegir cada token.
Cambiá los números de abajo y mirá cómo cambia lo que escribe el modelo.

Cómo correrlo:   uv run python con_modelo.py
"""

from ejercicio import con_temperatura, elegir, softmax, top_k

from taller import Modelo

TEXTO = "Mi comida favorita es la"
TEMPERATURA = 1.0  # probá 0.2, 1.0, 1.5, 3.0
K = 40             # probá 1, 5, 40, 1000
CANTIDAD = 25      # cuántos tokens escribir


def escribir(modelo):
    modelo.empezar(TEXTO)
    elegidos = []
    for _ in range(CANTIDAD):
        logits = con_temperatura(modelo.logits(), TEMPERATURA)
        token = elegir(top_k(softmax(logits), K))
        if token == modelo.fin:  # el modelo eligió «terminé»
            break
        elegidos.append(token)
        modelo.agregar(token)
    return modelo.texto(elegidos)


if __name__ == "__main__":
    modelo = Modelo("chico")
    print(f"Temperatura {TEMPERATURA}, top-k {K}\n")
    try:
        for intento in range(1, 4):
            print(f"{intento}. {TEXTO}▸{escribir(modelo)}\n")
    except NotImplementedError as falta:
        raise SystemExit(f"⏳ Primero terminá ejercicio.py → {falta}")
