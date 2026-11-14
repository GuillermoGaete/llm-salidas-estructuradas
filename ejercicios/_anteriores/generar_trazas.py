"""Guarda en JSON los puntajes reales del modelo para un texto.

Los ejercicios 03 y 04 usan estas «trazas» para trabajar sin cargar el modelo.

    uv run python herramientas/generar_trazas.py
"""

import json
from pathlib import Path

from taller import Modelo

RAIZ = Path(__file__).resolve().parent.parent


def traza(modelo: Modelo, texto: str, cuantos: int = 30) -> dict:
    """Los `cuantos` tokens con más puntaje después de leer `texto`."""
    modelo.empezar(texto)
    logits = modelo.logits()
    mejores = sorted(range(len(logits)), key=lambda i: -logits[i])[:cuantos]
    return {
        "texto": texto,
        "tokens": [modelo.pieza(i) for i in mejores],
        "logits": [round(logits[i], 3) for i in mejores],
    }


if __name__ == "__main__":
    modelo = Modelo()
    destino = RAIZ / "ejercicios" / "03-sampling" / "traza.json"
    datos = traza(modelo, "Mi comida favorita es la")
    destino.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Guardado {destino.relative_to(RAIZ)}: {datos['tokens'][:8]}...")
