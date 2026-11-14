# 04 — La máscara

**Tiempo:** 20 minutos · **Necesita:** haber hecho el [ejercicio 00](../00-preparacion)

Queremos que un modelo escriba una patente con este formato: `AB 123 CD`. Pedirlo con palabras no alcanza: en el ejercicio 03 el modelo respondió, cada tanto, algo que el programa no esperaba.

Con una **máscara** el modelo no puede escribir otra cosa. En cada paso, **antes del sorteo**, a los tokens que no respetan el formato se les cambia el logit por menos infinito. Con logit menos infinito la probabilidad es cero: ese token no puede salir.

```
logits  →  MÁSCARA: los tokens que no sirven pasan a −∞  →  probabilidades  →  sorteo
```

El formato se escribe carácter por carácter: `L` es una letra, `D` es un dígito, y cualquier otro símbolo es ese símbolo exacto.

```
FORMATO = "LL DDD LL"
```

Son dos programas. En los dos la máscara ya está escrita, y ninguno pide nada por teclado: los valores para cambiar están arriba, en el archivo. Después de cada cambio, guardá y corrélo de nuevo.

```
cd ejercicios/04-mascara
```

## Versión 1 — Con un modelo ficticio

```
uv run python mascara_v1.py
```

El modelo es de juguete. Su vocabulario tiene 38 tokens (las 27 letras, los 10 dígitos y el espacio) y no sabe nada: a cada token le pone un logit al azar. Como son pocos tokens, en cada paso se ve la máscara entera: los tokens tapados aparecen como un punto.

1. Mirá la primera línea: es lo que escribe el modelo solo, sin máscara.
2. Seguí los pasos. Si ya está escrito `AB`, ahora tiene que venir un espacio: es el único token que pasa.
3. Corrélo dos o tres veces. Cada vez sale otra patente, con el mismo formato.
4. Cambiá `FORMATO` por `"LLL DDD"`, y después por `"DD DDD DDD"`.

En esta versión el formato solo puede tener letras, dígitos y espacios: el vocabulario del modelo ficticio no tiene otros tokens.

## Versión 2 — Con el modelo real

```
uv run python mascara_v2.py
```

Es la misma máscara sobre el modelo real. Cambian dos cosas: el vocabulario tiene 248.320 tokens, y un token puede tener varios caracteres. Por eso la función `armar_mascara` es más larga que la de la versión 1: revisa cada carácter de cada token. Está comentada parte por parte.

El modelo lee el texto «La patente de mi auto es» y lo continúa. En cada paso el programa muestra:

- **El modelo quiere**: los tokens más probables, sin la máscara.
- **Con la máscara**: los tokens más probables entre los que respetan el formato.
- Cuántos tokens dejó pasar la máscara, de todos los del vocabulario, y cuál salió en el sorteo.

1. Corrélo dos o tres veces. Cada vez sale otra patente, con el mismo formato.
2. Cambiá `TEXTO` por uno que no tenga nada que ver con una patente: `"Hola, ¿cómo estás?"`.
3. Cambiá `TEMPERATURA` a `2.0`.
4. Cambiá `FORMATO` por una fecha, `"DD/DD/DDDD"`, y `TEXTO` por `"Mi cumpleaños es el"`.
5. Cambiá `FORMATO` por un DNI: `"DD.DDD.DDD"`.
