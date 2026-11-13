"""Ejercicio 00 — Preparar la máquina.

Descarga los modelos del taller a la carpeta modelos/ y comprueba que funcionan.

Cómo correrlo:   uv run python preparar.py

Se puede correr todas las veces que haga falta: los modelos que ya están
descargados no se bajan de nuevo.
"""

import sys
from pathlib import Path

import llama_cpp
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

# Los modelos a descargar. Cada uno es: (repositorio en Hugging Face, archivo).
MODELOS = [
    # Los modelos del taller.
    ("unsloth/Qwen3-0.6B-GGUF", "Qwen3-0.6B-Q4_K_M.gguf"),  # 0,4 GB · multilingüe
    ("unsloth/Qwen3-1.7B-GGUF", "Qwen3-1.7B-Q4_K_M.gguf"),  # 1,1 GB · multilingüe

    # Lista tentativa de otros modelos, para probar y comparar.
    # Para bajar uno: sacale el # de adelante, guardá y corré de nuevo el programa.
    # ("bartowski/SmolLM2-135M-Instruct-GGUF", "SmolLM2-135M-Instruct-Q4_K_M.gguf"),      # 0,1 GB · solo inglés
    # ("LiquidAI/LFM2.5-350M-GGUF", "LFM2.5-350M-Q4_K_M.gguf"),                           # 0,2 GB · multilingüe
    # ("ibm-granite/granite-4.0-350m-GGUF", "granite-4.0-350m-Q4_K_M.gguf"),              # 0,2 GB · multilingüe
    # ("unsloth/gemma-3-270m-it-GGUF", "gemma-3-270m-it-Q4_K_M.gguf"),                    # 0,3 GB · multilingüe
    # ("bartowski/SmolLM2-360M-Instruct-GGUF", "SmolLM2-360M-Instruct-Q4_K_M.gguf"),      # 0,3 GB · solo inglés
    # ("unsloth/Qwen3.5-0.8B-GGUF", "Qwen3.5-0.8B-Q4_K_M.gguf"),                          # 0,5 GB · multilingüe
    # ("LiquidAI/LFM2.5-1.2B-Instruct-GGUF", "LFM2.5-1.2B-Instruct-Q4_K_M.gguf"),         # 0,7 GB · multilingüe
    # ("unsloth/gemma-3-1b-it-GGUF", "gemma-3-1b-it-Q4_K_M.gguf"),                        # 0,8 GB · multilingüe
    # ("bartowski/Llama-3.2-1B-Instruct-GGUF", "Llama-3.2-1B-Instruct-Q4_K_M.gguf"),      # 0,8 GB · multilingüe
    # ("HuggingFaceTB/SmolLM2-1.7B-Instruct-GGUF", "smollm2-1.7b-instruct-q4_k_m.gguf"),  # 1,1 GB · solo inglés
    # ("unsloth/Qwen3.5-2B-GGUF", "Qwen3.5-2B-Q4_K_M.gguf"),                              # 1,3 GB · multilingüe
]

# La carpeta modelos/ está en la raíz del taller, dos carpetas arriba de este archivo.
CARPETA = Path(__file__).resolve().parents[2] / "modelos"

print("Python", sys.version.split()[0], "· llama-cpp-python", llama_cpp.__version__)
print("Los modelos se guardan en", CARPETA)

for repositorio, archivo in MODELOS:
    # 1. Descargar el modelo desde Hugging Face.
    #    Si ya está descargado, no lo baja de nuevo.
    #    local_dir: en qué carpeta guardarlo. Si no se lo decimos, lo guarda en una
    #    carpeta escondida del usuario, y los ejercicios no lo encontrarían.
    ruta = hf_hub_download(repositorio, archivo, local_dir=CARPETA)

    # 2. Cargar el modelo en memoria.
    #    verbose=False: que la librería no llene la pantalla con sus mensajes internos.
    modelo = Llama(ruta, verbose=False)

    # 3. Probarlo: partir una frase en tokens.
    tokens = modelo.tokenize("Hola, ¿todo listo?".encode())
    print(f"✅ {archivo}: leyó la frase como {len(tokens)} tokens. Su vocabulario tiene {modelo.n_vocab()}.")

    # 4. Liberar la memoria antes de cargar el siguiente.
    modelo.close()

print("🎉 Todo listo. Podés seguir con el ejercicio 01.")
