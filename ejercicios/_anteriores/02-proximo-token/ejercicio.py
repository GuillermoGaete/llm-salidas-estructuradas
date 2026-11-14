"""Ejercicio 02 — Un LLM es un clasificador que se usa en loop.

Abrimos un modelo real (Qwen3, 600 millones de parámetros) y miramos:
  1. cómo parte el texto en tokens,
  2. que «adivinar la próxima palabra» es clasificar entre ~150.000 clases,
  3. que escribir un texto es repetir eso muchas veces.

Cómo correrlo:   uv run python ejercicio.py
"""

import math

from taller import Modelo


# ---------------------------------------------------------------------------
# PASO 1 — softmax (copiá la tuya del ejercicio 01)
# ---------------------------------------------------------------------------
def softmax(puntajes):
    raise NotImplementedError("PASO 1: copiá tu softmax del ejercicio 01")


# ---------------------------------------------------------------------------
# PASO 2 — La «etiqueta» ganadora
#
# Devolvé la POSICIÓN del puntaje más alto (no el puntaje).
# Es lo mismo que `etiqueta` del ejercicio 01, pero devolviendo el número.
# ---------------------------------------------------------------------------
def mas_probable(puntajes):
    raise NotImplementedError("PASO 2: escribí mas_probable")


# ---------------------------------------------------------------------------
# PASO 3 — El loop
#
# Repetí `cantidad` veces:
#   a. pedile los puntajes al modelo:        modelo.logits()
#   b. elegí el token más probable:          mas_probable(...)
#   c. guardalo en la lista `elegidos`
#   d. agregalo al texto que lee el modelo:  modelo.agregar(token)
# ---------------------------------------------------------------------------
def completar(modelo, texto, cantidad=15):
    modelo.empezar(texto)  # el modelo lee el texto inicial
    elegidos = []
    raise NotImplementedError("PASO 3: escribí el loop de completar")
    return modelo.texto(elegidos)


def mostrar_tokens(modelo, texto):
    print(f"\n«{texto}» se parte en:")
    for token in modelo.tokenizar(texto):
        print(f"  {token:>7}  {modelo.pieza(token)!r}")


def mostrar_proximo(modelo, texto, cuantos=10):
    modelo.empezar(texto)
    logits = modelo.logits()
    probabilidades = softmax(logits)
    print(f"\nEl modelo leyó «{texto}» y puntuó {len(logits)} clases. Las mejores:")
    orden = sorted(range(len(logits)), key=lambda i: -probabilidades[i])
    for i in orden[:cuantos]:
        p = probabilidades[i]
        print(f"  {modelo.pieza(i)!r:<14} {'█' * round(p * 40):<40} {p:.1%}")


if __name__ == "__main__":
    modelo = Modelo("chico")
    try:
        mostrar_tokens(modelo, "Hola, quiero dos empanadas de carne")

        assert [round(x, 2) for x in softmax([2.0, 1.0, 0.0])] == [0.67, 0.24, 0.09]
        mostrar_proximo(modelo, "Mi comida favorita es la")

        assert mas_probable([0.1, 0.7, 0.2]) == 1, "mas_probable devuelve la posición"
        print("\n✅ Pasos 1 y 2 correctos")

        for texto in ["Mi comida favorita es la", "Había una vez un"]:
            print(f"\n{texto}▸{completar(modelo, texto)}")
        print("\n✅ Paso 3 correcto: escribiste un generador de texto")
    except NotImplementedError as falta:
        raise SystemExit(f"\n⏳ Todavía falta → {falta}")

    # PASO 4 — Experimentá:
    #   - Corré el programa otra vez. ¿Cambia el texto? ¿Por qué?
    #   - Cambiá los textos iniciales. Probá con tu nombre en mostrar_tokens.
