"""Ejercicio 04, versión 1 — La máscara, con un modelo ficticio.

Queremos que un modelo escriba una patente con este formato: AB 123 CD.
Dos letras, un espacio, tres dígitos, un espacio y dos letras.

Pedirlo con palabras no alcanza: el modelo sortea, y cada tanto escribe otra
cosa (ejercicio 03). Con una MÁSCARA no puede escribir otra cosa.

La máscara se aplica en cada paso, ANTES del sorteo: a los tokens que no
sirven se les cambia el logit por menos infinito. Con logit menos infinito,
la probabilidad es cero: ese token no puede salir.

Para ver la máscara entera usamos un modelo de juguete. Su vocabulario tiene
38 tokens: las 27 letras, los 10 dígitos y el espacio. Cada token es un solo
carácter. Y no sabe nada: a cada token le pone un logit al azar.

Cómo correrlo:   uv run python mascara_v1.py
Qué hacer:       corrélo varias veces. Después cambiá FORMATO, guardá y corrélo de nuevo.
"""

import random

import numpy as np
from scipy.special import softmax

# El formato, carácter por carácter:
#   L = una letra      D = un dígito
#   cualquier otro símbolo = ese símbolo exacto (acá, el espacio)
FORMATO = "LL DDD LL"

# El vocabulario del modelo ficticio: 38 tokens, cada uno de un solo carácter.
LETRAS = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
DIGITOS = "0123456789"
VOCABULARIO = list(LETRAS + DIGITOS + " ")


def modelo_ficticio():
    """El modelo de juguete: devuelve un logit por cada token del vocabulario.

    Un modelo real calcula los logits después de leer el texto. Este no lee
    nada y no sabe nada: los logits son números al azar.
    """
    logits = []
    for token in VOCABULARIO:
        logits.append(random.uniform(-2, 2))
    return logits


def armar_mascara(escrito):
    """La máscara: una lista con un True o un False por cada token del vocabulario.

    True quiere decir que el token sirve: es lo que el formato pide en el
    lugar donde quedó la escritura.
    """
    pide = FORMATO[len(escrito)]   # "L", "D" u otro símbolo
    mascara = []
    for token in VOCABULARIO:
        if pide == "L":
            sirve = token in LETRAS
        elif pide == "D":
            sirve = token in DIGITOS
        else:
            sirve = token == pide
        mascara.append(sirve)
    return mascara


def mostrar_mascara(mascara):
    """Muestra el vocabulario y, abajo, lo que la máscara deja pasar.

    Los tokens tapados se ven como un punto. El espacio se dibuja como ␣.
    """
    arriba = ""
    abajo = ""
    for token, sirve in zip(VOCABULARIO, mascara):   # recorre las dos listas a la vez
        visible = token.replace(" ", "␣")
        arriba = arriba + visible + " "
        if sirve:
            abajo = abajo + visible + " "
        else:
            abajo = abajo + "· "
    print("  Vocabulario:", arriba)
    print("  Con máscara:", abajo)


# 1. El modelo solo, sin máscara. Escribe cualquier cosa.
escrito = ""
while len(escrito) < len(FORMATO):
    logits = modelo_ficticio()
    probabilidades = softmax(logits)
    elegido = random.choices(VOCABULARIO, weights=probabilidades)[0]
    escrito = escrito + elegido

print("Sin máscara, el modelo escribe:", repr(escrito))

# 2. El mismo modelo, con la máscara.
escrito = ""
paso = 0
while len(escrito) < len(FORMATO):
    paso = paso + 1

    # El modelo da un logit por cada token.
    logits = modelo_ficticio()

    # La máscara dice qué tokens sirven en este lugar del formato.
    mascara = armar_mascara(escrito)

    # A los tokens que no sirven se les cambia el logit por menos infinito.
    logits_con_mascara = np.where(mascara, logits, -np.inf)

    # De logits a probabilidades, y el sorteo.
    # random.choices devuelve una lista de un solo elemento; con [0] se saca ese elemento.
    probabilidades = softmax(logits_con_mascara)
    elegido = random.choices(VOCABULARIO, weights=probabilidades)[0]

    print()
    print(f"Paso {paso}. Ya está escrito {escrito!r}. El formato pide {FORMATO[len(escrito)]!r}.")
    mostrar_mascara(mascara)
    print(f"  Tokens que pasan: {sum(mascara)} de {len(mascara)}. Salió {elegido!r}.")

    # Agregar el token que salió.
    escrito = escrito + elegido

print()
print("Con máscara, el modelo escribe:", repr(escrito))
