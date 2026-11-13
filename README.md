# Taller: de clasificadores a LLMs con salida estructurada

Taller práctico de 2 horas. Se trabaja con modelos de lenguaje **reales**, que corren en la computadora de cada estudiante: sin placa de video, y sin internet durante la clase.

> **Un LLM es un clasificador que se usa en loop. La salida estructurada es tapar opciones antes de elegir.**

Por ahora este repositorio tiene solo **la preparación de las máquinas**: esta guía y el programa que descarga los modelos. Los ejercicios y las diapositivas se publican más adelante.

## Versiones

| Programa | Versión | Cómo se instala |
|---|---|---|
| [uv](https://docs.astral.sh/uv/) | 0.8.6 o más nueva | Con un comando (está en la guía de cada sistema). Es lo único que se instala a mano. |
| Python | 3.12 | No se instala a mano. `uv` usa el Python 3.12 del sistema si está, y si no lo descarga. |

`uv` es el programa que instala Python y las librerías del taller. Instala siempre las mismas versiones, las que están anotadas en el archivo `uv.lock`.

La guía de Linux está probada de punta a punta en Ubuntu. La de Windows todavía no se probó en una máquina real.

## Instalación en Linux (Ubuntu)

Todo se instala dentro de tu carpeta personal. Abrí una terminal con `Ctrl` + `Alt` + `T`.

### Paso 1 — Instalar `uv`

```
wget -qO- https://astral.sh/uv/install.sh | sh
```

**Cerrá la terminal y abrila de nuevo.** Después comprobá que quedó instalado:

```
uv --version
```

Tiene que responder `uv 0.8.6` o un número más alto. Si ya tenías `uv` y es más viejo, actualizalo con `uv self update`.

### Paso 2 — Bajar el taller

```
wget -qO- https://github.com/GuillermoGaete/llm-salidas-estructuradas/archive/refs/heads/main.tar.gz | tar xz
cd llm-salidas-estructuradas-main
```

Si tenés `git`, también sirve `git clone https://github.com/GuillermoGaete/llm-salidas-estructuradas.git`. En ese caso la carpeta se llama `llm-salidas-estructuradas`, sin `-main`.

### Paso 3 — Instalar Python y las librerías

Parado en la carpeta del taller:

```
uv sync
```

Crea la carpeta `.venv` con Python 3.12 y las librerías. Con buena conexión tarda menos de un minuto.

### Paso 4 — Bajar los modelos y probarlos

```
cd ejercicios/00-preparacion
uv run python preparar.py
```

Descarga los dos modelos del taller (1,5 GB) a la carpeta `modelos/` y comprueba que cada uno funciona. Si todo salió bien, termina así:

```
Python 3.12.3 · llama-cpp-python 0.3.36
Los modelos se guardan en /home/alumno/llm-salidas-estructuradas-main/modelos
✅ Qwen3-0.6B-Q4_K_M.gguf: leyó la frase como 7 tokens. Su vocabulario tiene 151936.
✅ Qwen3-1.7B-Q4_K_M.gguf: leyó la frase como 7 tokens. Su vocabulario tiene 151936.
🎉 Todo listo. Podés seguir con el ejercicio 01.
```

El programa se puede correr todas las veces que haga falta: lo que ya está descargado no se baja de nuevo.

## Instalación en Windows

Los comandos se escriben en **PowerShell** (botón derecho sobre el menú Inicio → «Terminal» o «Windows PowerShell»).

### Paso 1 — Instalar Visual C++ Redistributable

La librería que corre los modelos necesita este paquete de Microsoft. Muchas máquinas ya lo tienen, y volver a instalarlo no rompe nada.

Descargá y ejecutá [`vc_redist.x64.exe`](https://aka.ms/vs/17/release/vc_redist.x64.exe). Pide permisos de administrador.

### Paso 2 — Instalar `uv`

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Cerrá PowerShell y abrilo de nuevo.** Después comprobá que quedó instalado:

```
uv --version
```

Tiene que responder `uv 0.8.6` o un número más alto.

### Paso 3 — Bajar el taller

```
Invoke-WebRequest https://github.com/GuillermoGaete/llm-salidas-estructuradas/archive/refs/heads/main.zip -OutFile taller.zip
Expand-Archive taller.zip -DestinationPath .
cd llm-salidas-estructuradas-main
```

También se puede bajar desde la página del repositorio, con el botón verde «Code» → «Download ZIP», y descomprimirlo.

### Paso 4 — Instalar Python y las librerías

```
uv sync
```

### Paso 5 — Bajar los modelos y probarlos

```
cd ejercicios\00-preparacion
uv run python preparar.py
```

Tiene que terminar con `🎉 Todo listo`, igual que en Linux.

## Instalación en macOS

Son los mismos cuatro pasos que en Linux. Cambian los comandos de los dos primeros, y hay que instalar antes las herramientas de compilación:

```
xcode-select --install
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Cerrá la terminal, abrila de nuevo y bajá el taller:

```
curl -L https://github.com/GuillermoGaete/llm-salidas-estructuradas/archive/refs/heads/main.tar.gz | tar xz
cd llm-salidas-estructuradas-main
```

Los pasos 3 y 4 son iguales. En macOS, `uv sync` compila la librería que corre los modelos, y por eso tarda unos minutos.

## Preparar muchas máquinas

- Los pasos 1 a 3 se hacen en cada máquina, con el usuario que va a usar el taller.
- Los modelos se pueden descargar una sola vez. Copiá la carpeta `modelos/` de una máquina ya preparada a la carpeta del taller de las otras, y corré el paso 4 para comprobar. No vuelve a descargar nada.
- Con todo instalado, el taller funciona sin internet.

## Los modelos

Un modelo es **un archivo de números**. Los que usamos están en formato `GGUF` y comprimidos a 4 bits por número (`Q4`), para que ocupen menos. Se descargan de [Hugging Face](https://huggingface.co), sin cuenta ni permiso.

La lista está al comienzo de [`preparar.py`](ejercicios/00-preparacion/preparar.py). Los dos primeros modelos son los del taller. El resto es una **lista tentativa** para probar y comparar: esas líneas están comentadas (empiezan con `#`) y no se descargan.

Para bajar uno de los otros modelos:

1. Abrí `preparar.py`.
2. Borrá el `#` del comienzo de la línea de ese modelo.
3. Guardá y corré de nuevo `uv run python preparar.py`.

| Modelo | Se descarga | Idiomas | Parámetros | Tamaño | Vocabulario | Licencia |
|---|---|---|---|---|---|---|
| [Qwen3-0.6B](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF) | **Sí** | Multilingüe | 596 M | 0,4 GB | 151.936 | Apache 2.0 |
| [Qwen3-1.7B](https://huggingface.co/unsloth/Qwen3-1.7B-GGUF) | **Sí** | Multilingüe | 1.721 M | 1,1 GB | 151.936 | Apache 2.0 |
| [SmolLM2-135M](https://huggingface.co/bartowski/SmolLM2-135M-Instruct-GGUF) | Comentado | Solo inglés | 135 M | 0,1 GB | 49.152 | Apache 2.0 |
| [LFM2.5-350M](https://huggingface.co/LiquidAI/LFM2.5-350M-GGUF) | Comentado | Multilingüe (9 idiomas, con español) | 354 M | 0,2 GB | 65.536 | LFM Open License 1.0 |
| [Granite 4.0 350M](https://huggingface.co/ibm-granite/granite-4.0-350m-GGUF) | Comentado | Multilingüe (12 idiomas, con español) | 352 M | 0,2 GB | 100.352 | Apache 2.0 |
| [Gemma 3 270M](https://huggingface.co/unsloth/gemma-3-270m-it-GGUF) | Comentado | Multilingüe | 268 M | 0,3 GB | 262.144 | Gemma |
| [SmolLM2-360M](https://huggingface.co/bartowski/SmolLM2-360M-Instruct-GGUF) | Comentado | Solo inglés | 362 M | 0,3 GB | 49.152 | Apache 2.0 |
| [Qwen3.5-0.8B](https://huggingface.co/unsloth/Qwen3.5-0.8B-GGUF) | Comentado | Multilingüe | 752 M | 0,5 GB | 248.320 | Apache 2.0 |
| [LFM2.5-1.2B](https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-GGUF) | Comentado | Multilingüe (8 idiomas, con español) | 1.170 M | 0,7 GB | 65.536 | LFM Open License 1.0 |
| [Gemma 3 1B](https://huggingface.co/unsloth/gemma-3-1b-it-GGUF) | Comentado | Multilingüe | 1.000 M | 0,8 GB | 262.144 | Gemma |
| [Llama 3.2 1B](https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF) | Comentado | Multilingüe (8 idiomas, con español) | 1.236 M | 0,8 GB | 128.256 | Llama 3.2 |
| [SmolLM2-1.7B](https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct-GGUF) | Comentado | Solo inglés | 1.711 M | 1,1 GB | 49.152 | Apache 2.0 |
| [Qwen3.5-2B](https://huggingface.co/unsloth/Qwen3.5-2B-GGUF) | Comentado | Multilingüe | 1.882 M | 1,3 GB | 248.320 | Apache 2.0 |

- **Idiomas**: lo que declara la ficha de cada modelo en Hugging Face. «Multilingüe» sin más detalle quiere decir que la ficha no da la lista de idiomas.
- **Vocabulario**: cuántos tokens distintos conoce el modelo.
- **Licencia**: las de Gemma, Llama 3.2 y LFM permiten usar los modelos, con condiciones. No son licencias de código abierto como Apache 2.0.
- Los once modelos comentados suman 6,3 GB.

De la lista tentativa solo comprobamos que cada archivo existe, que se descarga sin cuenta y que la librería reconoce el tipo de modelo. Falta probarlos con los ejercicios.

## Si algo falla

**`uv: command not found`** (Linux) o **«El término 'uv' no se reconoce…»** (Windows)
Cerrá la terminal y abrila de nuevo después de instalar `uv`.

**`warning: Failed to parse pyproject.toml` … `unknown field extra-build-variables`**
Tu `uv` es anterior a la versión 0.8.6. Actualizalo con `uv self update`.

**`Failed to load shared library` … `llama.dll`** (Windows)
Falta el paso 1: instalar Visual C++ Redistributable.

**`Illegal instruction`** (Linux), o el programa se cierra de golpe, sin mensaje de error (Windows)
El procesador no tiene instrucciones AVX2. En Linux se comprueba con `grep -c avx2 /proc/cpuinfo`: si responde `0`, no las tiene, y la librería ya compilada no sirve en esa máquina.

**`Failed to load model from file`**
La librería no pudo abrir ese modelo. Borrá el archivo de la carpeta `modelos/` y corré de nuevo `preparar.py`. Si es un modelo de la lista tentativa y vuelve a fallar, dejá su línea comentada.

**La descarga se corta**
Corré de nuevo `preparar.py`. Sigue desde donde quedó.

**Avisos que no son errores**

- `Warning: You are sending unauthenticated requests to the HF Hub`: aparece siempre. La descarga funciona igual.
- `Couldn't access the Hub to check for update but local file already exists`: aparece cuando no hay internet y los modelos ya están descargados.
