# 05 — Lo mismo, con una librería

**Tiempo:** 15 minutos · **Necesita:** el entorno del taller (`uv sync`)

La máscara del ejercicio 04 está escrita a mano, en unas 20 líneas. **Outlines** es una librería que hace lo mismo, pero rápido y para formatos mucho más complejos. Ahora que sabés qué pasa adentro, no es magia.

```python
respuesta = modelo(prompt, tipo_de_salida)
```

| Tipo de salida | Qué deja salir |
|---|---|
| `Literal["sí", "no"]` | Solo una de esas opciones |
| `Regex(r"[0-9]{2}")` | Texto que cumple la expresión regular |
| Una clase de Pydantic | Un JSON con esos campos y esos tipos |

## Qué hacer

```
uv run python ejercicio.py
```

La primera respuesta tarda unos 20 segundos.

1. **`clasificar`**: con `Literal`, el LLM vuelve a ser el clasificador del ejercicio 01.
2. **`inventar_patente`**: el formato `LL DDD LL`, ahora escrito como expresión regular.
3. **`Producto`**: un esquema con tres campos.
