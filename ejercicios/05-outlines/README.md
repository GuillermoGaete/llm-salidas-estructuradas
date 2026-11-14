# 05 — Lo mismo, con una librería

**Tiempo:** 15 minutos · **Necesita:** haber hecho el [ejercicio 00](../00-preparacion)

En el ejercicio 04 la máscara está escrita a mano. **Outlines** es una librería que hace ese trabajo: recibe el formato, arma la máscara y la aplica en cada paso, antes del sorteo.

A la librería se le pasan dos cosas, el texto y el formato:

```python
respuesta = modelo(texto, formato)
```

Son tres programas cortos. En cada uno cambia lo que se le pasa como formato:

| Programa | Qué se le pasa como formato | Qué puede salir |
|---|---|---|
| `1_patente.py` | Una expresión regular: `Regex("[A-Z]{2} [0-9]{3} [A-Z]{2}")` | Un texto con esa forma |
| `2_clasificar.py` | Una lista cerrada: `Choice(["reclamo", "consulta", "pedido", "saludo"])` | Una de esas palabras |
| `3_esquema.py` | Un esquema: la clase `Pedido`, con tres datos | Un JSON con esos datos y esos tipos |

```
cd ejercicios/05-outlines
```

## Parte 1 — La patente

```
uv run python 1_patente.py
```

Es la patente del ejercicio 04. El formato `LL DDD LL` ahora se escribe como una expresión regular: `[A-Z]` es una letra mayúscula, `[0-9]` es un dígito y `{2}` quiere decir «repetido 2 veces». El programa muestra el texto, el formato y cinco patentes.

- Compará con `mascara_v2.py`, del ejercicio 04: acá no hay ninguna máscara escrita. La arma la librería.
- Cambiá `FORMATO` por una fecha, `"[0-9]{2}/[0-9]{2}/[0-9]{4}"`, y `TEXTO` por `"Mi cumpleaños es el"`.

## Parte 2 — El clasificador del ejercicio 03

```
uv run python 2_clasificar.py
```

Es el programa del ejercicio 03 con una cosa más: al llamar al modelo se le pasa el formato, que es la lista de las cuatro respuestas posibles.

- Escribí los mismos mensajes que en el ejercicio 03: `Las empanadas llegaron frías y tarde`, `Hola, buenas tardes`.
- Mirá la cuenta del final y comparala con la del ejercicio 03.
- Escribí un mensaje que no es ninguna de las cuatro: `jajaja`.

## Parte 3 — Un esquema

```
uv run python 3_esquema.py
```

El formato es un esquema: la lista de los datos que necesita el programa, con el nombre y el tipo de cada uno. El modelo escribe un JSON con esos datos, y el programa los usa.

- `Hola, quiero tres empanadas de carne para llevar`
- `dame una coca, la tomo acá`
- `me das media docena de medialunas?`
- Agregá un renglón al esquema, por ejemplo `con_envio: bool`, y corrélo de nuevo.
