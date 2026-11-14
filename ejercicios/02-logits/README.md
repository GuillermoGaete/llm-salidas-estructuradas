# 02 — Logits, sorteo y generación

**Tiempo:** 20 minutos · **Necesita:** haber hecho el [ejercicio 00](../00-preparacion)

El modelo lee un texto y le pone un puntaje a **cada** token del vocabulario. Ese puntaje se llama **logit**. Los logits se pasan a probabilidades, se elige un token por sorteo, se agrega al texto y todo vuelve a empezar.

```
texto → logits → probabilidades → sorteo → próximo token
          ↑                                      │
          └──────── lo agrego y repito ──────────┘
```

Son tres programas cortos, que usan directo la librería `llama-cpp-python`. Cada uno te pide un texto, muestra el resultado y vuelve a preguntar; para salir, escribí `chau`.

| Qué hace | Cómo se escribe |
|---|---|
| El modelo lee los tokens | `modelo.eval(tokens)` |
| Los logits del próximo token | `modelo.scores[modelo.n_tokens - 1]` |
| De logits a probabilidades | `softmax(logits)` |
| Sortear un token | `modelo.sample(...)` |

```
cd ejercicios/02-logits
```

## Parte 1 — Logits y probabilidades

```
uv run python 1_logits.py
```

Muestra los tokens con el logit más alto, y su probabilidad.

- Mirá las dos columnas. El logit y la probabilidad dicen lo mismo en dos escalas: el orden es igual.
- Mirá el último token, el de logit más bajo. ¿Qué probabilidad tiene?
- Probá con otro texto. ¿El modelo está más seguro o menos seguro que antes?

## Parte 2 — El sorteo

```
uv run python 2_muestreo.py
```

Muestra las probabilidades de los 10 tokens más probables y después tira el dado muchas veces.

- Compará las dos tablas. ¿Lo que salió se parece a las probabilidades?
- ¿Salió algún token que no estaba entre los 10 más probables?
- Escribí el mismo texto otra vez. ¿Sale lo mismo?

## Parte 3 — Una inferencia completa

```
uv run python 3_generar.py
```

Escribe un texto token por token. En cada paso muestra los tres favoritos del modelo y cuál salió sorteado.

- Escribí tres veces el mismo comienzo. ¿Sale el mismo texto?
- ¿El token que sale es siempre el favorito?

## Para pensar entre todos

- ¿Por qué la misma pregunta a un chat da respuestas distintas cada vez?
- Un token con probabilidad muy baja, ¿puede salir? ¿Y uno con probabilidad cero?

## La idea que nos llevamos

El modelo no «escribe»: puntúa todos los tokens, **sortea** uno y repite. Lo que tiene probabilidad baja puede salir igual; lo que tiene probabilidad cero, nunca.
