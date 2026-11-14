"""Ejercicio 04, versión 2 — La máscara, con el modelo real.

Es la máscara de la versión 1, ahora sobre un modelo de verdad. La idea es la
misma: en cada paso, ANTES del sorteo, a los tokens que no sirven se les
cambia el logit por menos infinito, y así no pueden salir.

Cambian dos cosas:

  - El vocabulario no tiene 38 tokens: tiene 248.320.
  - Un token puede tener varios caracteres («AB», « A»). Por eso la máscara
    revisa cada carácter del token: sirve si todos respetan el formato desde
    el lugar donde quedó la escritura.

Si ya está escrito «AB», ahora tiene que venir un espacio: sirven los tokens
que empiezan con un espacio, y ningún otro.

Cómo correrlo:   uv run python mascara_v2.py
Qué hacer:       corrélo varias veces. Después cambiá FORMATO, TEXTO o TEMPERATURA, guardá y corrélo de nuevo.
"""

import random

import numpy as np
from llama_cpp import Llama
from scipy.special import softmax

# El formato, carácter por carácter:
#   L = una letra mayúscula      D = un dígito
#   cualquier otro símbolo = ese símbolo exacto (acá, el espacio)
FORMATO = "LL DDD LL"

TEXTO = "La patente de mi auto es"   # lo que lee el modelo antes de escribir
TEMPERATURA = 1.0                    # 1.0: no cambia las probabilidades que da el modelo
CUANTOS = 5                          # cuántos tokens mostrar en cada paso

# Cargar el modelo.
# logits_all=True: que la librería guarde los logits después de leer.
# Si no se lo pedimos, no los guarda (para ahorrar memoria).
# verbose=False: que la librería no llene la pantalla con sus mensajes internos.
modelo = Llama("../../modelos/Qwen3.5-2B-Q4_K_M.gguf", logits_all=True, verbose=False)

# Anotar qué pedacito de texto escribe cada token del vocabulario.
# PIEZAS[número de token] es el texto de ese token.
# errors="replace": algunos tokens son solo una parte de una letra o de un
# emoji. En ese caso se anota � en vez de dar un error.
PIEZAS = []
for token in range(modelo.n_vocab()):
    PIEZAS.append(modelo.detokenize([token]).decode(errors="replace"))


def armar_mascara(escrito):
    """Arma la máscara para el próximo paso.

    Recibe lo que ya está escrito (por ejemplo "AB") y devuelve una lista con
    un True o un False por cada token del vocabulario: True si el token sirve,
    False si no sirve.

    Un token sirve si CADA UNO de sus caracteres es lo que el formato pide en
    el lugar que le toca. Con el formato "LL DDD LL" y "AB 123" ya escrito,
    lo que falta es un espacio (lugar 6) y dos letras (lugares 7 y 8):

        " "      sirve:     en el lugar 6 el formato pide un espacio.
        " C"     sirve:     el espacio va en el lugar 6 y la C en el lugar 7,
                            donde el formato pide una letra.
        "C"      no sirve:  en el lugar 6 el formato pide un espacio, no una letra.
        " c"     no sirve:  el espacio está bien, pero la c es minúscula.
        " CDE"   no sirve:  la E iría en el lugar 9, y el formato termina en el 8.
    """
    mascara = []

    # Se revisan todos los tokens del vocabulario, de a uno.
    # «pieza» es el texto que escribe el token.
    for pieza in PIEZAS:
        # Se empieza suponiendo que el token sirve. Si después aparece un
        # carácter que no respeta el formato, pasa a False.
        sirve = True

        # El lugar del formato que le toca al primer carácter del token.
        # Los lugares se cuentan desde 0. Si ya hay 2 caracteres escritos
        # ("AB"), el próximo carácter va en el lugar 2.
        lugar = len(escrito)

        # Se revisa el token carácter por carácter.
        # El token " 12" tiene tres caracteres: el espacio, el 1 y el 2.
        for caracter in pieza:
            if lugar >= len(FORMATO):
                # El formato ya se terminó y al token le quedan caracteres:
                # se pasa del final. No sirve.
                sirve = False
            elif FORMATO[lugar] == "L":
                # El formato pide una letra mayúscula.
                # "A" <= caracter <= "Z" pregunta si el carácter está entre la A y la Z.
                if not "A" <= caracter <= "Z":
                    sirve = False
            elif FORMATO[lugar] == "D":
                # El formato pide un dígito.
                # "0" <= caracter <= "9" pregunta si el carácter está entre el 0 y el 9.
                if not "0" <= caracter <= "9":
                    sirve = False
            else:
                # El formato pide un símbolo exacto (en la patente, el espacio).
                # El carácter tiene que ser ese mismo símbolo.
                if caracter != FORMATO[lugar]:
                    sirve = False

            # El carácter siguiente del token va en el lugar siguiente del formato.
            lugar = lugar + 1

        # Un caso aparte: hay tokens que no escriben nada. Son marcas especiales,
        # como la que usa el modelo para decir «terminé». No tienen ningún
        # carácter para revisar, así que hasta acá quedaron en True. Pero con
        # ellos la escritura no avanza: no sirven.
        if pieza == "":
            sirve = False

        # Se anota el resultado de este token y se sigue con el próximo.
        mascara.append(sirve)

    # La lista tiene el mismo largo que el vocabulario: una respuesta por token.
    return mascara


def mostrar_mas_probables(probabilidades):
    """Muestra en un renglón los tokens más probables, cada uno con su probabilidad."""
    # np.argsort da los números de token ordenados del menos probable al más probable.
    orden = np.argsort(probabilidades)
    # Con [::-1] se da vuelta la lista: ahora va del más probable al menos probable.
    orden = orden[::-1]
    # Se toman los primeros CUANTOS.
    mejores = orden[:CUANTOS]
    for token in mejores:
        # Un token con probabilidad cero es uno que la máscara tapó: no se muestra.
        if probabilidades[token] > 0:
            print(f"{PIEZAS[token]!r} {probabilidades[token]:.1%}", end="   ")
    print()


# 1. Hacer que el modelo lea el texto.
#    Se le agrega un espacio al final, para que lo que escriba no quede pegado.
texto = TEXTO + " "
modelo.eval(modelo.tokenize(texto.encode()))

# 2. Escribir token por token, hasta completar el formato.
escrito = ""
paso = 0
while len(escrito) < len(FORMATO):
    paso = paso + 1

    # El modelo da un logit por cada token, igual que en el ejercicio 02.
    logits = modelo.scores[modelo.n_tokens - 1]

    # La máscara dice qué tokens sirven en este lugar del formato.
    mascara = armar_mascara(escrito)

    # A los tokens que no sirven se les cambia el logit por menos infinito.
    logits_con_mascara = np.where(mascara, logits, -np.inf)

    # De logits a probabilidades, sin la máscara y con la máscara.
    sin_mascara = softmax(logits / TEMPERATURA)
    con_mascara = softmax(logits_con_mascara / TEMPERATURA)

    # El sorteo, con las probabilidades de después de la máscara.
    # random.choices sortea un número de token: weights dice cuánto pesa cada uno.
    # Devuelve una lista de un solo elemento, y con [0] se saca ese elemento.
    elegido = random.choices(range(len(PIEZAS)), weights=con_mascara)[0]

    print()
    print(f"Paso {paso}. Ya está escrito {escrito!r}")
    print("  El modelo quiere: ", end="")
    mostrar_mas_probables(sin_mascara)
    print("  Con la máscara:   ", end="")
    mostrar_mas_probables(con_mascara)
    print(f"  Tokens que pasan: {sum(mascara)} de {len(mascara)}. Salió {PIEZAS[elegido]!r}.")

    # Agregar el token que salió: ahora el modelo también lo lee.
    escrito = escrito + PIEZAS[elegido]
    modelo.eval([elegido])

# 3. El texto completo: lo que leyó el modelo y lo que escribió.
print()
print(texto + escrito)
