# 02 — Un LLM es un clasificador en loop

**Tiempo:** 15 minutos · **Necesita:** el entorno del taller (`uv sync`)

Abrimos un modelo real y lo miramos por adentro. No le «hacemos una pregunta»: le pedimos los puntajes, igual que al clasificador del ejercicio 01.

```
texto → tokens → puntajes (150.000) → probabilidades → próximo token
                      ↑                                      │
                      └──────── lo agrego y repito ──────────┘
```

## Qué hacer

```
uv run python ejercicio.py
```

1. **`softmax`**: copiá la del ejercicio 01. Es exactamente la misma.
2. **`mas_probable`**: la posición del puntaje más alto.
3. **`completar`**: el loop. Son 4 líneas.
4. **Experimentá** con otros textos.
