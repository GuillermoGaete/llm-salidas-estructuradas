# Recorrido del taller

> Estas secciones estaban en el `README.md` de la raíz. Se movieron acá porque el `README.md` publicado tiene, por ahora, solo la guía de instalación. Cuando se publiquen los ejercicios y las diapositivas, vuelven al `README.md`.

## Recorrido

### Primera parte: cómo infiere un LLM

Los programas ya están completos y son cortos: usan directo `llama-cpp-python` (`tokenize`, `eval`, `scores`, `sample`) y `softmax` de SciPy. El trabajo es **correrlos, cambiar los valores de arriba y observar**. Todo usa un modelo real.

| # | Carpeta | Min | Qué se hace |
|---|---|---|---|
| | Diapositiva | 10 | Un clasificador de imágenes: perro, persona, persona disfrazada de perro |
| 00 | [`00-preparacion`](../ejercicios/00-preparacion) | 10 | Instalar las librerías, bajar los modelos y probarlos |
| 01 | [`01-tokens`](../ejercicios/01-tokens) | 10 | El tokenizador real: cómo se parte un texto en tokens |
| 02 | [`02-logits`](../ejercicios/02-logits) | 25 | Logits y probabilidades; temperatura, top-k y top-p; una inferencia paso a paso |

Cada carpeta tiene un `README.md` con las instrucciones y las preguntas para conversar.

### Segunda parte: salida estructurada

Todos los ejercicios ya son los del recorrido nuevo. Los programas están completos, igual que los de la primera parte:

| # | Carpeta | Min | Qué se hace |
|---|---|---|---|
| 03 | [`03-clasificar`](../ejercicios/03-clasificar) | 10 | Un LLM adentro de un programa: clasificar el mensaje de un cliente y comprobar lo que el modelo devolvió |
| 04 | [`04-mascara`](../ejercicios/04-mascara) | 20 | La máscara, ya escrita, para una patente `AB 123 CD`: primero con un modelo ficticio de 38 tokens, después con el modelo real. En cada paso se ve qué tokens deja pasar |
| 05 | [`05-outlines`](../ejercicios/05-outlines) | 15 | Lo mismo con una librería: se le pasa el texto y el formato (expresión regular, lista cerrada, esquema) |
| 06 | [`06-kiosco`](../ejercicios/06-kiosco) | 20 | El tomador de pedidos: el modelo pasa el mensaje a datos con un esquema, y Python hace la cuenta |

La versión anterior de los ejercicios (gancho, clasificador, próximo token, sampling a mano, y la máscara, Outlines y el kiosco para completar) quedó en [`_anteriores`](../ejercicios/_anteriores).

Modelos que usa cada programa (al 2026-11-14):

| Modelo | Tamaño | Se usa en |
|---|---|---|
| SmolLM2-135M | 0,1 GB | 01 |
| Granite 4.0 350M | 0,2 GB | 02 (`2_muestreo.py`) |
| Qwen3-1.7B | 1,1 GB | 02 (`1_logits.py`) |
| Qwen3.5-2B | 1,3 GB | 02 (`3_generar.py`), 03, 04 (`mascara_v2.py`), 05, 06 |

## Diapositivas

Están en [`clases/index.html`](../clases/index.html), hechas con reveal.js. Se abren con doble clic, sin servidor y sin internet (reveal.js está copiado en `clases/vendor/`).

- Flechas o barra espaciadora: avanzar.
- `S`: vista del presentador, con las notas de cada diapositiva.
- `F`: pantalla completa. `Esc`: ver todas las diapositivas.

Las diapositivas de la primera parte son interactivas: se elige una imagen, una frase, o se mueven las perillas de temperatura, top-k y top-p con el mouse. Los tokens y los logits que muestran son reales: están guardados en `clases/datos.js` y se regeneran con:

```
uv run python herramientas/generar_datos_clase.py
```

Los porcentajes del clasificador de imágenes son ilustrativos.

## Otras carpetas

- `taller/`: código de apoyo para los scripts de `herramientas/`. Ningún ejercicio lo usa.
- `herramientas/`: scripts para descargar los modelos y regenerar los datos de las diapositivas.
- `docs/planificacion.md`: el diseño original del taller.
