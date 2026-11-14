# 01 — Tokens

**Tiempo:** 10 minutos · **Necesita:** haber hecho el [ejercicio 00](../00-preparacion)

Un modelo de lenguaje no lee letras ni palabras. Lee **tokens**: pedacitos de texto, cada uno con su número. Acá usamos el tokenizador real del modelo del taller.

```
texto  →  tokens  →  números
«Hola, quiero…»   Hola | , | ·quiero   [68012, 11, 91720]
```

## Qué hacer

```
cd ejercicios/01-tokens
uv run python tokens.py
```

El programa tiene cuatro pasos: carga el modelo, convierte el texto en tokens (`tokenize`), muestra el pedacito de cada token (`detokenize`) y vuelve a armar el texto. El programa te pide un texto, muestra sus tokens y vuelve a preguntar; para salir, escribí `chau`. Probá con:

1. Tu nombre y tu apellido.
2. Una palabra muy larga: `electroencefalografista`.
3. La misma palabra con minúscula y con mayúscula: `hola`, `Hola`.
4. Un emoji, o una palabra con `ñ`. Si aparece `�`, ese token es solo una parte de un carácter.
5. Una frase en inglés y la misma frase en español. ¿Cuál usa menos tokens?

## Para pensar entre todos

- ¿Los tokens son palabras? ¿Son letras? ¿Son sílabas?
- ¿Qué palabras quedan enteras y cuáles se parten? ¿Por qué será?
- ¿Dónde queda el espacio que separa dos palabras?
- El vocabulario tiene 151.936 tokens. ¿Se puede escribir una palabra que el modelo nunca vio?

## La idea que nos llevamos

El modelo trabaja con **números de token**, no con texto. El vocabulario es fijo: cualquier texto se arma combinando esos pedacitos.
