"""Ejercicio 03 — Sampling: el dado cargado.

El modelo ya leyó el texto y nos dio un puntaje (logit) para cada token.
Ahora hay que ELEGIR uno. ¿Siempre el más probable? ¿Al azar? ¿Cuán al azar?

Trabajamos con los puntajes reales que dio el modelo, guardados en traza.json
(solo los 30 tokens con más puntaje, para que entren en la pantalla).

Cómo correrlo:   python ejercicio.py
Solo necesita Python (ninguna librería).
"""

import json
import math
import random
from pathlib import Path

TRAZA = json.loads((Path(__file__).parent / "traza.json").read_text(encoding="utf-8"))
TEXTO = TRAZA["texto"]    # lo que leyó el modelo
TOKENS = TRAZA["tokens"]  # los 30 candidatos a próximo token
LOGITS = TRAZA["logits"]  # el puntaje de cada candidato


# ---------------------------------------------------------------------------
# PASO 1 — softmax (copiá la tuya del ejercicio 01)
# ---------------------------------------------------------------------------
def softmax(puntajes):
    raise NotImplementedError("PASO 1: copiá tu softmax del ejercicio 01")


# ---------------------------------------------------------------------------
# PASO 2 — Temperatura
#
# Dividí cada logit por la temperatura y devolvé la lista nueva.
#   temperatura chica (0.2) → las diferencias se agrandan → torta «afilada»
#   temperatura grande (2)  → las diferencias se achican  → torta «achatada»
# ---------------------------------------------------------------------------
def con_temperatura(logits, temperatura):
    raise NotImplementedError("PASO 2: escribí con_temperatura")


# ---------------------------------------------------------------------------
# PASO 3 — Tirar el dado cargado
#
# Devolvé la POSICIÓN de un token elegido al azar, respetando las
# probabilidades (el que tiene 0.5 tiene que salir la mitad de las veces).
# Pista: random.choices(opciones, weights=pesos)[0]
#        y las opciones son las posiciones: range(len(probabilidades))
# ---------------------------------------------------------------------------
def elegir(probabilidades):
    raise NotImplementedError("PASO 3: escribí elegir")


# ---------------------------------------------------------------------------
# PASO 4 — top-k: recortar la torta
#
# Quedate con las k probabilidades más altas, poné las demás en 0
# y volvé a repartir para que sumen 1 (dividí cada una por la suma).
# Pista: sorted(probabilidades, reverse=True)[k - 1] es la k-ésima más alta.
# ---------------------------------------------------------------------------
def top_k(probabilidades, k):
    raise NotImplementedError("PASO 4: escribí top_k")


# ---------------------------------------------------------------------------
# PASO 5 (desafío) — top-p
#
# En vez de una cantidad fija, quedate con los tokens más probables hasta
# juntar una probabilidad acumulada de p (por ejemplo 0.9). El resto va a 0
# y se vuelve a repartir.
# ---------------------------------------------------------------------------
def top_p(probabilidades, p):
    raise NotImplementedError("PASO 5: escribí top_p")


# ---------------------------------------------------------------------------
# Ya está hecho: dibujos y experimentos.
# ---------------------------------------------------------------------------
def mostrar(titulo, probabilidades, cuantos=10):
    print(f"\n{titulo}")
    orden = sorted(range(len(TOKENS)), key=lambda i: -probabilidades[i])
    for i in orden[:cuantos]:
        p = probabilidades[i]
        print(f"  {TOKENS[i]!r:<14} {'█' * round(p * 40):<40} {p:.1%}")


def tirar(probabilidades, veces=20):
    """Tira el dado varias veces y cuenta cuántas veces salió cada token."""
    conteo = {}
    for _ in range(veces):
        token = TOKENS[elegir(probabilidades)]
        conteo[token] = conteo.get(token, 0) + 1
    return dict(sorted(conteo.items(), key=lambda par: -par[1]))


def comprobar(hasta):
    if hasta >= 1:
        assert [round(x, 2) for x in softmax([2.0, 1.0, 0.0])] == [0.67, 0.24, 0.09]
    if hasta >= 2:
        assert con_temperatura([2.0, 4.0], 2) == [1.0, 2.0]
    if hasta >= 3:
        assert elegir([0.0, 1.0, 0.0]) == 1, "con [0, 1, 0] siempre tiene que salir la posición 1"
        salidas = [elegir([0.5, 0.5]) for _ in range(200)]
        assert 0 in salidas and 1 in salidas, "con [0.5, 0.5] tienen que salir las dos"
    if hasta >= 4:
        r = top_k([0.1, 0.5, 0.1, 0.3], 2)
        assert [round(x, 3) for x in r] == [0.0, 0.625, 0.0, 0.375], f"top_k dio {r}"
    if hasta >= 5:
        r = top_p([0.1, 0.5, 0.1, 0.3], 0.7)
        assert [round(x, 3) for x in r] == [0.0, 0.625, 0.0, 0.375], f"top_p dio {r}"
        r = top_p([0.1, 0.5, 0.1, 0.3], 0.4)
        assert [round(x, 3) for x in r] == [0.0, 1.0, 0.0, 0.0], f"top_p dio {r}"


if __name__ == "__main__":
    print(f"El modelo leyó: «{TEXTO}»")
    try:
        comprobar(1)
        mostrar("Probabilidades del próximo token:", softmax(LOGITS))

        comprobar(2)
        print("\n✅ Pasos 1 y 2 correctos")
        for t in [0.2, 1.0, 2.0]:
            mostrar(f"Temperatura {t}:", softmax(con_temperatura(LOGITS, t)), cuantos=6)

        comprobar(3)
        print("\n✅ Paso 3 correcto. Tiramos el dado 20 veces con cada temperatura:")
        for t in [0.2, 1.0, 2.0]:
            print(f"  T={t}: {tirar(softmax(con_temperatura(LOGITS, t)))}")

        comprobar(4)
        print("\n✅ Paso 4 correcto. Temperatura 2.0, pero recortando con top-k = 3:")
        print(f"  {tirar(top_k(softmax(con_temperatura(LOGITS, 2.0)), 3))}")

        comprobar(5)
        print("\n✅ Paso 5 correcto. Temperatura 2.0 con top-p = 0.5:")
        print(f"  {tirar(top_p(softmax(con_temperatura(LOGITS, 2.0)), 0.5))}")
    except NotImplementedError as falta:
        raise SystemExit(f"\n⏳ Todavía falta → {falta}")
