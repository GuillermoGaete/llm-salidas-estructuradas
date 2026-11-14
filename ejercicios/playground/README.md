# Playground

Una página para mandar el mismo prompt a tres modelos y comparar lo que responden: dos modelos locales, de los que están en la carpeta `modelos/`, y uno de OpenAI.

De cada respuesta se ve el texto y una tabla con una fila por token y su probabilidad. Al tocar un token se abre una ventana con todas las opciones que había en ese lugar, cada una con su probabilidad y su logprob completos.

## Cómo usarlo

```
cd ejercicios/playground
uv run python servidor.py
```

Después abrí http://localhost:8000 en el navegador. Para cerrarlo, `Ctrl` + `C` en la terminal.

Escribí el prompt, elegí un modelo en cada columna y apretá «Enviar».

Cada columna tiene su propia **temperatura**:

- `1`: el sorteo usa las probabilidades tal como las da el modelo.
- Más baja (hasta `0`): sale casi siempre el token más probable, y las respuestas se repiten.
- Más alta (hasta `2`): salen más seguido los tokens menos probables, y las respuestas se vuelven más raras.

La temperatura cambia qué token sale en el sorteo, no la tabla: las probabilidades que se muestran son las que dio el modelo, antes de aplicar la temperatura. Esto está comprobado en los modelos locales.

Algunos modelos de OpenAI no aceptan cambiar la temperatura. Si elegís uno de esos, la columna muestra el error que da OpenAI.

## La columna de OpenAI

Hace falta una clave de OpenAI. Se pasa al arrancar el servidor:

```
OPENAI_API_KEY="sk-..." uv run python servidor.py
```

- Sin clave, las dos columnas locales funcionan igual y la de OpenAI queda apagada.
- La clave no se guarda en ningún archivo ni llega a la página: la usa solo el servidor.
- El servidor atiende solo a tu computadora, así que nadie más en la red puede usar la página.
- Cada prompt enviado a OpenAI se cobra en esa cuenta.
- Algunos modelos de OpenAI no devuelven logprobs. Si elegís uno de esos, la columna muestra el error que da OpenAI.
- El pedido va con el razonamiento apagado (`reasoning_effort: "none"`), porque los modelos que «piensan» antes de responder no devuelven los logprobs completos. Si el modelo no conoce ese ajuste, el servidor repite el pedido sin él.
- Aun así, algunos devuelven solo el logprob del token que salió, sin las alternativas. En ese caso la ventana de detalle lo avisa. Pasa con algunos de la familia GPT-5; los `gpt-4.1` devuelven las alternativas.

## Qué son los logprobs

Un logprob es el logaritmo de una probabilidad. La ventana de detalle lo muestra junto a la probabilidad ya calculada, con todos sus decimales: un logprob de `0` es 100%, `-0.69` es 50% y `-2.3` es 10%. Cuanto más negativo, menos probable era ese token.

## Límites

- El prompt y la respuesta juntos no pueden pasar de 512 tokens en los modelos locales.
- Los Qwen3 (0.6B y 1.7B) escriben primero su razonamiento entre `<think>` y `</think>`. Los Qwen3.5 responden directo.
- Quedan cargados dos modelos locales a la vez. Al elegir un tercero, el servidor descarga el más viejo; la primera respuesta de un modelo recién elegido tarda un poco más.

## Los archivos

- `servidor.py`: el servidor. Usa `llama-cpp-python` para los modelos locales y un pedido HTTP para OpenAI; los dos devuelven los logprobs con la misma forma.
- `pagina.html`: la página.
