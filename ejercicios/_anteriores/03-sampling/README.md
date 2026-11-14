# 03 — Sampling: el dado cargado

**Tiempo:** 20 minutos · **Necesita:** solo Python (la segunda parte usa el entorno del taller)

En el ejercicio 02 elegimos siempre el token más probable y el texto salió repetitivo y siempre igual. Ahora vamos a **tirar un dado cargado**: cada token tiene tantas caras como probabilidad.

`traza.json` tiene los puntajes reales que dio el modelo después de leer «Mi comida favorita es la».

## Qué hacer

```
python ejercicio.py
```

1. **`softmax`**: otra vez la misma.
2. **`con_temperatura`**: dividir cada puntaje por un número.
3. **`elegir`**: tirar el dado cargado.
4. **`top_k`**: quedarse con los `k` mejores.
5. **`top_p`** (desafío): quedarse con los mejores hasta juntar probabilidad `p`.

El programa te muestra las barras y los resultados de tirar el dado a medida que completás cada paso.

### Segunda parte: con el modelo real

Cuando termines los pasos 1 a 4:

```
uv run python con_modelo.py
```

Ese programa usa **tus funciones** para escribir texto. Abrilo y cambiá `TEMPERATURA` y `K`.
