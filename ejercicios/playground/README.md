# Playground

Una página con tres pestañas para probar modelos: los locales, que están en la carpeta `modelos/`, y los de OpenAI.

1. **Comparar modelos**: el mismo prompt a tres modelos, con la probabilidad de cada token.
2. **Salida estructurada**: un prompt y un modelo de Pydantic. La respuesta sale con ese formato.
3. **Sesgos**: una pregunta con opciones, repetida muchas veces, y la cuenta de qué eligió el modelo.

## Cómo usarlo

```
cd ejercicios/playground
uv run python servidor.py
```

Después abrí http://localhost:8000 en el navegador. Para cerrarlo, `Ctrl` + `C` en la terminal.

Si cambiás `servidor.py` o `casos.py`, cerrá el servidor y arrancalo de nuevo. Si cambiás `pagina.html`, alcanza con recargar la página.

## Pestaña 1: Comparar modelos

Manda el mismo prompt a dos modelos locales y a uno de OpenAI. Escribí el prompt, elegí un modelo en cada columna y apretá «Enviar».

De cada respuesta se ve el texto y una tabla con una fila por token y su probabilidad. Al tocar un token se abre una ventana con todas las opciones que había en ese lugar, cada una con su probabilidad y su logprob completos.

Cada columna tiene su propia **temperatura**:

- `1`: el sorteo usa las probabilidades tal como las da el modelo.
- Más baja (hasta `0`): sale casi siempre el token más probable, y las respuestas se repiten.
- Más alta (hasta `2`): salen más seguido los tokens menos probables, y las respuestas se vuelven más raras.

La temperatura cambia qué token sale en el sorteo, no la tabla: las probabilidades que se muestran son las que dio el modelo, antes de aplicar la temperatura. Esto está comprobado en los modelos locales.

Un logprob es el logaritmo de una probabilidad. La ventana de detalle lo muestra junto a la probabilidad ya calculada, con todos sus decimales: un logprob de `0` es 100%, `-0.69` es 50% y `-2.3` es 10%. Cuanto más negativo, menos probable era ese token.

## Pestaña 2: Salida estructurada

Tiene dos cuadros: el prompt y un modelo de Pydantic, que es el formato que tiene que cumplir la respuesta. Elegí un caso de la lista, o escribí el tuyo, elegí un modelo y apretá «Enviar».

En el modelo de Pydantic ya están importados `BaseModel`, `Field`, `Literal`, `Optional`, `List` y `Enum`. Si hay varias clases, la principal va al final.

La tilde **«Forzar el formato»** decide qué recibe el modelo:

- Con la tilde, recibe el prompt y el formato. En los modelos locales, Outlines arma la máscara, como en el ejercicio 05. A OpenAI el formato se le pasa como JSON Schema.
- Sin la tilde, recibe solo el prompt y responde lo que quiere.

En los dos casos el servidor comprueba la respuesta contra el modelo de Pydantic. La página muestra ✓ si cumple y ✗ si no cumple, con el motivo. Debajo de la respuesta se puede abrir el JSON Schema que se armó a partir del modelo de Pydantic.

### La respuesta, token por token

Debajo de la respuesta hay una tabla con una fila por token y su probabilidad. Al tocar un token se abre una ventana con las otras opciones que había en ese lugar, cada una con su probabilidad y su logprob.

En los modelos locales con el formato forzado, cada token tiene dos probabilidades:

- **Sin la máscara**: la que le dio el modelo.
- **Con la máscara**: la que le quedó después de tapar los tokens que no respetan el formato. En la ventana, los tokens tapados dicen «tapado».

Un ejemplo, con Qwen3.5-2B y el caso «Datos de una persona». Para el primer token, el modelo le dio 56% a `Bas`, el comienzo de una respuesta en texto libre, y 0,0006% a `{`. La máscara tapó `Bas` y todos los tokens que no pueden empezar un JSON, y `{` quedó con 92%.

En estas dos pestañas (2 y 3), el sorteo de los modelos locales no descarta ningún token, igual que en el ejercicio 02. Con temperatura `1`, cada token sale con la probabilidad que muestra la tabla.

Para tener en cuenta:

- El formato forzado garantiza la forma de la respuesta, no que los datos sean ciertos. En el caso «Algo que el texto no dice», el texto no tiene ni nombre ni edad ni ciudad, y el modelo igual los completa.
- Si la respuesta llega al máximo de tokens antes de terminar, el JSON queda cortado y no cumple.
- OpenAI exige que todos los datos sean obligatorios y no admite todo lo que admite Pydantic. El servidor adapta el esquema; si aun así OpenAI lo rechaza, la página muestra el error que da OpenAI.

## Pestaña 3: Sesgos

Trae preguntas que no tienen una respuesta correcta: a quién contratar si solo se sabe la nacionalidad, quién es el sospechoso si no hay pruebas, cuál es el mejor país. El modelo no tiene con qué decidir. La página le hace la misma pregunta muchas veces y cuenta qué elige.

Elegí un caso, un modelo y cuántas veces preguntar, y apretá «Correr». Las barras se van actualizando con cada respuesta; «Detener» corta la corrida. La pregunta y las opciones se pueden cambiar en los cuadros: en la pregunta, donde dice `{opciones}` se escribe la lista de opciones.

- **La respuesta está forzada.** Una máscara solo deja escribir una de las opciones, así que el modelo no puede negarse ni explicar: siempre elige.
- **«Mezclar el orden de las opciones cada vez»** (viene prendida): en cada pregunta las opciones se escriben en otro orden. Sin esto, una opción puede ganar solo por estar primera.
- **«Agregar la opción «prefiero no elegir»»** (viene apagada): suma esa opción, siempre al final. Sirve para comparar qué hace el modelo cuando tiene esa salida y cuando no la tiene.
- **Temperatura**: en los modelos locales, con `0` no hay sorteo y sale siempre la opción más probable. Si aun así la respuesta cambia de una vez a otra, es por el orden de las opciones.

Debajo de las barras está **«La última respuesta, token por token»**, con las mismas dos columnas que en la pestaña 2. Ahí se ve qué probabilidad le daba el modelo a cada opción, y qué otras respuestas tenía en cuenta antes de la máscara. Para mirar una sola respuesta, poné `1` en «Veces».

El resultado vale para ese modelo, con esa pregunta escrita de esa manera y con esa temperatura. Con pocas repeticiones, una diferencia de dos o tres respuestas entre opciones puede ser azar: para comparar, conviene repetir la corrida o subir las veces.

## Los modelos de OpenAI

Hace falta una clave de OpenAI. Se pasa al arrancar el servidor:

```
OPENAI_API_KEY="sk-..." uv run python servidor.py
```

- Sin clave, los modelos locales funcionan igual. La columna de OpenAI queda apagada, y en las otras dos pestañas la lista muestra solo los modelos locales.
- La clave no se guarda en ningún archivo ni llega a la página: la usa solo el servidor.
- Cada pedido a OpenAI se cobra en esa cuenta. En la pestaña «Sesgos», cada repetición es un pedido: 20 veces son 20 pedidos.
- Algunos modelos de OpenAI no aceptan cambiar la temperatura, y algunos no devuelven logprobs. En la pestaña 1, si elegís uno de esos, la columna muestra el error que da OpenAI.
- En las pestañas 2 y 3 el servidor también pide los logprobs. Si el modelo rechaza ese pedido, el servidor lo repite sin pedirlos: la respuesta sale igual, y la tabla avisa que el modelo no informó las probabilidades.
- Con OpenAI la tabla tiene una sola columna, con las probabilidades que informa OpenAI. La máscara la aplican ellos, y no informan qué tokens tapó.
- El pedido va con el razonamiento apagado (`reasoning_effort: "none"`), porque los modelos que «piensan» antes de responder no devuelven los logprobs completos. Si el modelo no conoce ese ajuste, el servidor repite el pedido sin él.
- Aun así, algunos devuelven solo el logprob del token que salió, sin las alternativas. En ese caso la ventana de detalle lo avisa. Pasa con algunos de la familia GPT-5; los `gpt-4.1` devuelven las alternativas.

## El servidor atiende solo a tu computadora

El servidor ejecuta el código que se escribe en el cuadro «Modelo de Pydantic». Por eso:

- Escucha solo en `127.0.0.1`: nadie más en la red puede usar la página, ni la clave de OpenAI.
- Rechaza los pedidos que no vienen de su propia página.

No lo cambies para que atienda a otras computadoras: cualquiera que llegue a la página podría ejecutar código en la tuya.

## Límites

- El prompt y la respuesta juntos no pueden pasar de 512 tokens en los modelos locales.
- Los Qwen3 (0.6B y 1.7B) escriben primero su razonamiento entre `<think>` y `</think>`. Los Qwen3.5 responden directo.
- La pestaña 1 sortea como lo trae la librería, que antes del sorteo descarta los tokens menos probables (`top_k=40`, `top_p=0.95`, `min_p=0.05`). Las pestañas 2 y 3 no descartan ninguno.
- En la ventana de detalle no aparecen los tokens de más de 32 bytes (por ejemplo, 40 espacios seguidos): la librería no los puede convertir a texto.
- Quedan cargados dos modelos locales a la vez. Al elegir un tercero, el servidor descarga el más viejo; la primera respuesta de un modelo recién elegido tarda un poco más.

## Los archivos

- `servidor.py`: el servidor. Usa `llama-cpp-python` y Outlines para los modelos locales, y pedidos HTTP para OpenAI.
- `pagina.html`: la página, con las tres pestañas.
- `casos.py`: los casos que vienen cargados en las pestañas 2 y 3. Para sumar uno, copiá un bloque, cambiale los datos y arrancá de nuevo el servidor.
