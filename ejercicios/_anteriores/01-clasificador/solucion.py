"""SOLUCIÓN del ejercicio 01 — Un clasificador desde cero.

Al kiosco le llegan mensajes por WhatsApp. Queremos saber si cada uno es un
PEDIDO, una CONSULTA o un RECLAMO.

Cómo correrlo:   python ejercicio.py
Solo necesita Python (ninguna librería).
"""

import math

CLASES = ["pedido", "consulta", "reclamo"]

# Cada palabra le suma puntos a cada clase: [pedido, consulta, reclamo]
PESOS = {
    "quiero":    [2.0, 0.0, 0.0],
    "mandame":   [2.5, 0.0, 0.0],
    "dame":      [2.0, 0.0, 0.0],
    "docena":    [1.5, 0.5, 0.0],
    "empanadas": [1.0, 0.5, 0.3],
    "coca":      [1.0, 0.3, 0.0],
    "cuánto":    [0.0, 2.5, 0.0],
    "sale":      [0.0, 1.5, 0.0],
    "tienen":    [0.0, 2.0, 0.0],
    "abren":     [0.0, 2.0, 0.0],
    "hora":      [0.0, 1.5, 0.5],
    "frías":     [0.0, 0.0, 2.5],
    "tarde":     [0.0, 0.3, 2.0],
    "nunca":     [0.0, 0.0, 2.0],
    "llegó":     [0.3, 0.0, 1.5],
    "faltó":     [0.0, 0.0, 2.5],
}


def palabras(mensaje):
    """'¿Cuánto sale?' → ['cuánto', 'sale']"""
    for signo in "¿?¡!.,;:":
        mensaje = mensaje.replace(signo, " ")
    return mensaje.lower().split()


def puntajes(mensaje):
    """Suma los puntos de cada palabra conocida. Devuelve 3 números, uno por clase."""
    total = [0.0, 0.0, 0.0]
    for palabra in palabras(mensaje):
        if palabra in PESOS:
            for i in range(len(CLASES)):
                total[i] += PESOS[palabra][i]
    return total


# ---------------------------------------------------------------------------
# PASO 1 — De puntajes a probabilidades (softmax)
#
# Los puntajes pueden ser cualquier número. Queremos «porciones de torta»:
# números entre 0 y 1 que sumen 1.
#
#   1. A cada puntaje p lo convertimos en math.exp(p)   (siempre da positivo)
#   2. Dividimos cada uno por la suma de todos           (así suman 1)
# ---------------------------------------------------------------------------
def softmax(puntajes):
    exponentes = [math.exp(p) for p in puntajes]
    total = sum(exponentes)
    return [e / total for e in exponentes]


# ---------------------------------------------------------------------------
# PASO 2 — De probabilidades a etiqueta
#
# Devolvé el nombre de la clase con la probabilidad más alta.
# Pista: max(probabilidades) te da el valor más alto y
#        lista.index(valor) te dice en qué posición está.
# ---------------------------------------------------------------------------
def etiqueta(probabilidades):
    return CLASES[probabilidades.index(max(probabilidades))]


# ---------------------------------------------------------------------------
# Ya está hecho: muestra el resultado con barras.
# ---------------------------------------------------------------------------
def mostrar(mensaje):
    probabilidades = softmax(puntajes(mensaje))
    print(f"\n«{mensaje}»")
    for clase, p in zip(CLASES, probabilidades):
        print(f"  {clase:<9} {'█' * round(p * 30):<30} {p:.0%}")
    print(f"  → {etiqueta(probabilidades)}")


def comprobar():
    p = softmax([2.0, 1.0, 0.0])
    assert abs(sum(p) - 1) < 1e-9, "las probabilidades tienen que sumar 1"
    assert [round(x, 2) for x in p] == [0.67, 0.24, 0.09], f"softmax([2, 1, 0]) dio {p}"
    assert etiqueta([0.1, 0.7, 0.2]) == "consulta"
    assert etiqueta(softmax(puntajes("mandame una docena"))) == "pedido"
    print("✅ Pasos 1 y 2 correctos\n")


if __name__ == "__main__":
    try:
        comprobar()
    except NotImplementedError as falta:
        raise SystemExit(f"⏳ Todavía falta → {falta}")

    mostrar("Hola, quiero una docena de empanadas")
    mostrar("¿Hasta qué hora abren?")
    mostrar("Las empanadas llegaron frías y tarde")

    # PASO 3 — Experimentá (respuestas en el README):
    mostrar("hola")
    mostrar("che, me vino todo helado")
    mostrar("¿Tienen coca? Quiero dos")
