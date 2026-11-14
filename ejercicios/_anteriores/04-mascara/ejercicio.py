"""Ejercicio 04 — La máscara: tapar opciones antes de elegir.

Este es el corazón del taller. Vamos a obligar a un modelo a escribir una
patente argentina (AB 123 CD) aunque el modelo no tenga ni idea de patentes.

El truco: antes de tirar el dado, TAPAMOS los tokens que romperían el formato.

Cómo correrlo:   python ejercicio.py
Solo necesita Python (ninguna librería).
"""

import math
import random

# El formato, carácter por carácter:
#   L = una letra mayúscula      D = un dígito
#   cualquier otro símbolo = ese símbolo exacto (acá, el espacio)
FORMATO = "LL DDD LL"

# Un vocabulario de juguete. Ojo: los tokens NO son letras sueltas.
# Hay tokens de varios caracteres, igual que en un modelo real.
VOCABULARIO = [
    "A", "B", "C", "K", "M", "Z", "AB", "GH", "XY",
    "0", "1", "2", "5", "7", "9", "12", "45", "123", "907",
    " ", " 3", " 86", "7 ", "9 P", " QR",
    "hola", "la", "a", "b", ".", ",", "!", "-", "\n", "ñ", "Ab", "1a",
]


def modelo_desordenado(texto):
    """Un «modelo» que no sabe nada: devuelve puntajes al azar para cada token."""
    return [random.uniform(-2, 2) for _ in VOCABULARIO]


def softmax(puntajes):
    exponentes = [math.exp(p) for p in puntajes]
    total = sum(exponentes)
    return [e / total for e in exponentes]


def elegir(probabilidades):
    return random.choices(range(len(probabilidades)), weights=probabilidades)[0]


# ---------------------------------------------------------------------------
# PASO 1 — La máscara
#
# `permitido` es una lista de True/False, una por token.
# Devolvé una lista nueva de logits donde los NO permitidos valen -math.inf.
#
# ¿Por qué menos infinito? Porque math.exp(-math.inf) da 0:
# después del softmax esos tokens tienen probabilidad CERO. No pueden salir.
# ---------------------------------------------------------------------------
def enmascarar(logits, permitido):
    raise NotImplementedError("PASO 1: escribí enmascarar")


# ---------------------------------------------------------------------------
# PASO 2 — El autómata, de a un carácter
#
# El «estado» es cuántos caracteres del formato ya escribimos (empieza en 0).
# Si `caracter` es lo que el formato pide en esa posición, devolvé estado + 1.
# Si no sirve (o el formato ya se completó), devolvé None.
#
# Pistas: FORMATO[estado] te dice qué se espera ('L', 'D' u otro símbolo).
#         "A" <= caracter <= "Z" pregunta si es una letra mayúscula.
#         "0" <= caracter <= "9" pregunta si es un dígito.
# ---------------------------------------------------------------------------
def avanzar(estado, caracter):
    raise NotImplementedError("PASO 2: escribí avanzar")


# ---------------------------------------------------------------------------
# PASO 3 — El autómata, de a un token
#
# Un token puede tener varios caracteres ("AB", " 86"). Hacé avanzar el
# autómata con cada carácter. Si alguno no sirve, el token no sirve: None.
# Si todos sirven, devolvé el estado final.
# Un token vacío ("") nunca sirve: devolvé None.
# ---------------------------------------------------------------------------
def probar_token(estado, token):
    raise NotImplementedError("PASO 3: escribí probar_token")


# ---------------------------------------------------------------------------
# Ya está hecho: el loop de generación. Leelo, es corto.
# ---------------------------------------------------------------------------
def generar(con_mascara=True, mostrar_pasos=False):
    texto = ""
    estado = 0
    while estado < len(FORMATO):
        logits = modelo_desordenado(texto)
        if con_mascara:
            permitido = [probar_token(estado, token) is not None for token in VOCABULARIO]
            if not any(permitido):
                raise SystemExit(
                    f"💥 Trabado después de escribir {texto!r}: el formato pide "
                    f"{FORMATO[estado]!r} y ningún token del vocabulario sirve."
                )
            logits = enmascarar(logits, permitido)
        token = VOCABULARIO[elegir(softmax(logits))]
        if con_mascara and mostrar_pasos:
            vivos = [t for t, ok in zip(VOCABULARIO, permitido) if ok]
            print(f"  estado {estado}: quedan {len(vivos):>2} tokens vivos {vivos} → sale {token!r}")
        texto += token
        estado = probar_token(estado, token) if con_mascara else estado + 1
    return texto


def comprobar():
    global FORMATO
    elegido, FORMATO = FORMATO, "LL DDD LL"  # las pruebas usan siempre la patente
    assert enmascarar([1.0, 2.0, 3.0], [True, False, True]) == [1.0, -math.inf, 3.0]
    print("✅ Paso 1 correcto")
    assert avanzar(0, "A") == 1 and avanzar(0, "7") is None and avanzar(0, "a") is None
    assert avanzar(2, " ") == 3 and avanzar(2, "A") is None
    assert avanzar(3, "7") == 4 and avanzar(3, "A") is None
    assert avanzar(len(FORMATO), "A") is None, "si el formato ya terminó, nada sirve"
    print("✅ Paso 2 correcto")
    assert probar_token(0, "AB") == 2 and probar_token(0, "Ab") is None
    assert probar_token(2, " 86") == 5 and probar_token(5, "7 ") == 7
    assert probar_token(0, "") is None and probar_token(7, "XYZ") is None
    print("✅ Paso 3 correcto")
    FORMATO = elegido


if __name__ == "__main__":
    try:
        comprobar()
    except NotImplementedError as falta:
        raise SystemExit(f"⏳ Todavía falta → {falta}")

    print("\nSin máscara, el modelo desordenado escribe:")
    for _ in range(3):
        print(f"  {generar(con_mascara=False)!r}")

    print("\nCon máscara, paso a paso:")
    print(f"  → {generar(mostrar_pasos=True)!r}")

    print("\nCon máscara, 10 veces:")
    print("  " + "   ".join(generar() for _ in range(10)))

    # PASO 4 — Cambiá FORMATO (arriba de todo) y volvé a correr:
    #   una fecha:  "DD/DD/DDDD"   → ¿qué pasa? ¿por qué? (mirá el VOCABULARIO)
    #   un DNI:     "DD.DDD.DDD"
