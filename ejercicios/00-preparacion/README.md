# 00 — Preparar la máquina

**Tiempo:** 10 minutos (la descarga depende de internet) · **Se hace una sola vez**

Vamos a trabajar con modelos de lenguaje **reales**, que corren en tu computadora, sin internet y sin placa de video. Antes de usarlos hay que instalar las herramientas y bajar los modelos.

La guía completa, con la instalación de `uv` en Linux y en Windows, está en el [`README.md` principal](../../README.md). Este es el resumen.

## Qué hacer

Parado en la carpeta del taller (la que tiene el archivo `pyproject.toml`):

```
uv sync
cd ejercicios/00-preparacion
uv run python preparar.py
```

- `uv sync` instala Python 3.12 y `llama-cpp-python`, la librería que corre los modelos.
- `preparar.py` descarga los modelos del taller (2,1 GB) a la carpeta `modelos/`, carga cada uno y le hace partir una frase en tokens.

Si todo salió bien, termina así:

```
✅ Qwen3-0.6B-Q4_K_M.gguf: leyó la frase como 7 tokens. Su vocabulario tiene 151936.
✅ Qwen3-1.7B-Q4_K_M.gguf: leyó la frase como 7 tokens. Su vocabulario tiene 151936.
🎉 Todo listo. Podés seguir con el ejercicio 01.
```

Puede aparecer un aviso sobre `HF_TOKEN`: no es un error.

## ¿Qué bajamos?

| Modelo | Archivo | Tamaño | Se usa en |
|---|---|---|---|
| **Qwen3-0.6B**: 600 millones de parámetros | `Qwen3-0.6B-Q4_K_M.gguf` | 0,4 GB | Ejercicio 02 |
| **Qwen3-1.7B**: 1.700 millones de parámetros | `Qwen3-1.7B-Q4_K_M.gguf` | 1,1 GB | Segunda parte |
| **SmolLM2-135M**: 135 millones de parámetros | `SmolLM2-135M-Instruct-Q4_K_M.gguf` | 0,1 GB | Ejercicio 01 |
| **LFM2.5-350M**: 350 millones de parámetros | `LFM2.5-350M-Q4_K_M.gguf` | 0,2 GB | Para comparar |
| **Granite 4.0 350M**: 350 millones de parámetros | `granite-4.0-350m-Q4_K_M.gguf` | 0,2 GB | Ejercicio 02 |

Se descargan de [Hugging Face](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF).

Un modelo es **un archivo de números**. `GGUF` es el formato del archivo y `Q4` quiere decir que cada número se guardó comprimido, en 4 bits, para que ocupe menos.

## Probar otros modelos

Al comienzo de `preparar.py` hay una lista tentativa de otros modelos, para comparar. Sus líneas están comentadas (empiezan con `#`). Para bajar uno, borrale el `#`, guardá y corré de nuevo el programa: descarga solo lo que falta.

La tabla con los idiomas, el tamaño y la licencia de cada uno está en el [`README.md` principal](../../README.md#los-modelos).

## Si algo falla

Los problemas más comunes y su solución están en el [`README.md` principal](../../README.md#si-algo-falla).
