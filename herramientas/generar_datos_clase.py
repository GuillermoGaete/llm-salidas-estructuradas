"""Guarda en clases/datos.js los datos reales que usan las diapositivas interactivas.

Las diapositivas se abren con doble clic, sin servidor y sin modelo. Por eso
los números del modelo (tokens, logits) se calculan acá y quedan guardados.

    uv run python herramientas/generar_datos_clase.py
"""

import json
import re
from collections import Counter
from pathlib import Path

from taller import Modelo

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "clases" / "datos.js"

FRASES = [
    "Hola, quiero dos empanadas de carne",
    "Mi comida favorita es la pizza",
    "El ñandú corre rapidísimo",
    "Te mando un abrazo 🤗",
    "2 + 2 = 4, ¿no?",
]
TEXTO = "Mi comida favorita es la"
# Textos de la diapositiva «Un LLM también clasifica»: uno donde el modelo está
# muy seguro, uno donde duda entre varias opciones y el que se usa en el resto de la clase.
EJEMPLOS = ["Uno, dos, tres, cuatro,", "Hola, ¿cómo", TEXTO]
EXACTOS = 40   # tokens que se guardan con su logit exacto
ANCHO = 0.25   # el resto se guarda agrupado en cajones de este ancho de logit


def pieza_visible(modelo: Modelo, token: int) -> str:
    """El pedacito de texto, o sus bytes si es solo una parte de un carácter."""
    pieza = modelo.pieza(token)
    if "�" in pieza:
        return "<" + modelo.bytes_de(token).hex(" ") + ">"
    return pieza


def tokenizaciones(modelo: Modelo) -> list[dict]:
    """Cómo parte el modelo cada frase de ejemplo."""
    return [
        {
            "texto": frase,
            "tokens": [
                {"numero": token, "pieza": pieza_visible(modelo, token)}
                for token in modelo.tokenizar(frase)
            ],
        }
        for frase in FRASES
    ]


def proximo_token(modelo: Modelo) -> dict:
    """Los logits del próximo token: los mejores exactos y el resto agrupado."""
    modelo.empezar(TEXTO)
    candidatos, _ = modelo.candidatos()
    cajones = Counter(round(c.logit / ANCHO) for c in candidatos[EXACTOS:])
    return {
        "texto": TEXTO,
        "vocabulario": len(candidatos),
        "mejores": [
            {"pieza": pieza_visible(modelo, c.token), "logit": round(c.logit, 3)}
            for c in candidatos[:EXACTOS]
        ],
        # Cada cajón: [logit del centro, cuántos tokens tiene], del más alto al más bajo.
        "resto": [[round(k * ANCHO, 2), n] for k, n in sorted(cajones.items(), reverse=True)],
    }


LETRA = r"[a-záéíóúüñA-ZÁÉÍÓÚÜÑ]"


def ejemplos(modelo: Modelo, mirar: int = 15, cuantas: int = 5) -> list[dict]:
    """Para cada texto de ejemplo: las palabras más probables y cuánto junta el resto.

    El modelo no elige palabras sino tokens, que a veces son solo el comienzo de
    una palabra (« ens»). Para que la primera diapositiva del LLM se pueda leer
    con palabras, cada token candidato se completa hasta terminar la palabra
    (« ens» → «ensalada»). La probabilidad es la del token real. Los candidatos
    que no son palabras (signos) quedan dentro de «el resto».
    """
    lista = []
    for texto in EJEMPLOS:
        base = modelo.tokenizar(texto)
        modelo.empezar(texto)
        candidatos, _ = modelo.candidatos()
        suma: dict[str, float] = {}
        for candidato in candidatos[:mirar]:
            # El modelo lee el texto más este token, y sigue con el más probable
            # mientras lo que venga sea la continuación de la misma palabra.
            modelo.llm.reset()
            modelo.llm.eval(base + [candidato.token])
            piezas = [modelo.pieza(candidato.token)]
            for _ in range(6):
                siguientes, _ = modelo.candidatos()
                pieza = modelo.pieza(siguientes[0].token)
                if not re.match(LETRA, pieza):  # empieza con espacio o con un signo: la palabra terminó
                    break
                piezas.append(pieza)
                modelo.agregar(siguientes[0].token)
            palabra = "".join(piezas).strip()
            if re.fullmatch(LETRA + "+", palabra):
                suma[palabra] = suma.get(palabra, 0) + candidato.probabilidad
        mejores = sorted(suma.items(), key=lambda par: -par[1])[:cuantas]
        lista.append(
            {
                "texto": texto,
                "mejores": [{"palabra": palabra, "p": round(p, 4)} for palabra, p in mejores],
                "resto": round(1 - sum(p for _, p in mejores), 4),
            }
        )
    return lista


def ejemplos_con_tokens(modelo: Modelo, cuantos: int = 5) -> list[dict]:
    """Los mismos textos de ejemplo, pero tal como los ve el modelo: con tokens.

    Para cada texto: en qué tokens se parte, los tokens más probables para seguir
    y cuánto junta el resto.
    """
    lista = []
    for texto in EJEMPLOS:
        modelo.empezar(texto)
        candidatos, _ = modelo.candidatos()
        mejores = candidatos[:cuantos]
        lista.append(
            {
                "texto": texto,
                "piezas": [pieza_visible(modelo, token) for token in modelo.tokenizar(texto)],
                "mejores": [
                    {
                        "pieza": pieza_visible(modelo, c.token),
                        "p": round(c.probabilidad, 4),
                        "logit": round(c.logit, 2),
                    }
                    for c in mejores
                ],
                "resto": round(1 - sum(c.probabilidad for c in mejores), 4),
            }
        )
    return lista


# El ejemplo de la diapositiva del loop. La continuación la escribió el modelo
# mediano al sortear; se guarda acá para que la diapositiva muestre siempre la misma.
TEXTO_DEL_LOOP = "Mi comida favorita es la"
CONTINUACION_DEL_LOOP = " pizza, porque es deliciosa y es fácil de preparar."


def generacion() -> dict:
    """La generación de ejemplo, paso a paso: en cada paso, los favoritos del modelo y cuál salió."""
    modelo = Modelo("mediano")
    inicio = modelo.tokenizar(TEXTO_DEL_LOOP)
    completo = modelo.tokenizar(TEXTO_DEL_LOOP + CONTINUACION_DEL_LOOP)
    assert completo[: len(inicio)] == inicio, "la continuación cambia cómo se parte el texto inicial"
    modelo.empezar(TEXTO_DEL_LOOP)
    pasos = []
    for elegido in completo[len(inicio) :]:
        candidatos, _ = modelo.candidatos()  # las probabilidades tal como salen del modelo
        pasos.append(
            {
                "elegido": pieza_visible(modelo, elegido),
                "favoritos": [
                    {"pieza": pieza_visible(modelo, c.token), "p": round(c.probabilidad, 4)}
                    for c in candidatos[:5]
                ],
            }
        )
        modelo.agregar(elegido)
    return {"texto": TEXTO_DEL_LOOP, "modelo": "Qwen3-1.7B", "pasos": pasos}


def guardar(datos: dict) -> None:
    """Escribe los datos en clases/datos.js, como una variable que leen las diapositivas."""
    contenido = json.dumps(datos, ensure_ascii=False, indent=1)
    DESTINO.write_text(
        "// Generado por herramientas/generar_datos_clase.py. No editar a mano.\n"
        f"window.DATOS = {contenido};\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    modelo = Modelo("chico")
    datos = {
        "modelo": "Qwen3-0.6B",
        "tokens": tokenizaciones(modelo),
        "ejemplos": ejemplos(modelo),
        "ejemplos_con_tokens": ejemplos_con_tokens(modelo),
        "proximo": proximo_token(modelo),
        "generacion": generacion(),
    }
    guardar(datos)
    escrito = "".join(paso["elegido"] for paso in datos["generacion"]["pasos"])
    print(f"Guardado {DESTINO.relative_to(RAIZ)}")
    print(f"Generación de ejemplo: {TEXTO}▸{escrito}")
