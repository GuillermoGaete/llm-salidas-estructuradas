"""Ayudas para cargar los modelos del taller y mirarlos «por adentro».

La idea es que los ejercicios no dependan de los detalles de las librerías:
solo necesitamos tokens, logits y la posibilidad de agregar un token.
"""

import random
from pathlib import Path
from typing import NamedTuple

# Los dos modelos son Qwen3 (licencia Apache 2.0), comprimidos a 4 bits.
MODELOS = {
    "chico": ("unsloth/Qwen3-0.6B-GGUF", "Qwen3-0.6B-Q4_K_M.gguf"),    # ~400 MB
    "mediano": ("unsloth/Qwen3-1.7B-GGUF", "Qwen3-1.7B-Q4_K_M.gguf"),  # ~1,1 GB
}
CARPETA = Path(__file__).resolve().parent.parent / "modelos"


def ruta_del_modelo(tamaño: str = "chico") -> str:
    """Devuelve la ruta al archivo del modelo. Lo descarga la primera vez."""
    repo, archivo = MODELOS[tamaño]
    destino = CARPETA / archivo
    if not destino.exists():
        from huggingface_hub import hf_hub_download

        print(f"Descargando {archivo} (solo la primera vez)...")
        hf_hub_download(repo, archivo, local_dir=CARPETA)
    return str(destino)


def _llama(tamaño: str):
    from llama_cpp import Llama

    # n_batch chico: la librería reserva (n_batch × vocabulario) números al cargar.
    return Llama(ruta_del_modelo(tamaño), n_ctx=2048, n_batch=128, verbose=False)


class Candidato(NamedTuple):
    """Un token que puede salir sorteado como próximo token."""

    token: int           # el número de token
    logit: float         # el puntaje que le dio el modelo (sin tocar)
    probabilidad: float  # entre 0 y 1, después de aplicar temperatura, top-k y top-p


class Modelo:
    """El modelo visto como un clasificador: entra texto, salen puntajes por token."""

    def __init__(self, tamaño: str = "chico"):
        self.llm = _llama(tamaño)
        self.fin = self.llm.token_eos()
        self._vocabulario: list[str] | None = None

    # --- tokens -----------------------------------------------------------

    def tokenizar(self, texto: str) -> list[int]:
        """Texto → lista de números de token."""
        return self.llm.tokenize(texto.encode("utf-8"), add_bos=False, special=True)

    def pieza(self, token: int) -> str:
        """Número de token → el pedacito de texto que representa."""
        return self.llm.detokenize([token]).decode("utf-8", errors="replace")

    def bytes_de(self, token: int) -> bytes:
        """Número de token → los bytes que representa (un emoji ocupa varios tokens)."""
        return self.llm.detokenize([token])

    def texto(self, tokens: list[int]) -> str:
        """Lista de números de token → texto."""
        return self.llm.detokenize(tokens).decode("utf-8", errors="replace")

    def vocabulario(self) -> list[str]:
        """Todas las piezas que conoce el modelo, en orden (posición = número de token)."""
        if self._vocabulario is None:
            self._vocabulario = [self.pieza(i) for i in range(self.llm.n_vocab())]
        return self._vocabulario

    # --- el loop ----------------------------------------------------------

    def empezar(self, texto: str) -> None:
        """Borra lo anterior y le hace leer `texto` al modelo."""
        self.llm.reset()
        self.llm.eval(self.tokenizar(texto))

    def logits(self) -> list[float]:
        """Un puntaje por cada token del vocabulario, para la PRÓXIMA posición."""
        import llama_cpp
        import numpy as np

        puntero = llama_cpp.llama_get_logits_ith(self.llm.ctx, -1)
        return np.ctypeslib.as_array(puntero, shape=(self.llm.n_vocab(),)).tolist()

    def candidatos(self, temperatura: float = 1.0, top_k: int = 0, top_p: float = 1.0):
        """Los tokens que pueden salir como PRÓXIMO token, y cuál salió sorteado.

        Devuelve dos cosas:
          - la lista de `Candidato`, del más probable al menos probable;
          - el número del token que salió en el sorteo.

        Las cuentas no las hacemos nosotros: se las pedimos a llama.cpp, la
        librería que corre el modelo. Aplica, en este orden:
          1. top-k: se queda con los `top_k` tokens de mayor logit (0 = todos);
          2. top-p: se queda con los más probables hasta juntar `top_p` (1.0 = todos);
          3. temperatura: divide los logits (menos de 1 afila, más de 1 achata);
          4. softmax + sorteo: pasa los logits a probabilidades y tira el dado.
        """
        import llama_cpp
        import numpy as np
        from llama_cpp._internals import LlamaSampler, LlamaTokenDataArray

        cantidad = self.llm.n_vocab()
        puntero = llama_cpp.llama_get_logits_ith(self.llm.ctx, -1)
        originales = np.ctypeslib.as_array(puntero, shape=(cantidad,))

        # La «cadena» de pasos de llama.cpp, igual a la que usa cuando genera texto.
        cadena = LlamaSampler()
        cadena.add_top_k(top_k)
        cadena.add_top_p(top_p, 1)
        cadena.add_temp(temperatura)
        cadena.add_dist(random.getrandbits(32))  # semilla distinta en cada sorteo

        datos = LlamaTokenDataArray(n_vocab=cantidad)
        datos.copy_logits(originales)
        llama_cpp.llama_sampler_apply(cadena.sampler, datos.candidates)

        # Lo que quedó después de los recortes, con su probabilidad final.
        vivos = datos.candidates_data[: datos.candidates.size]
        elegido = int(vivos.id[datos.candidates.selected])
        orden = np.argsort(-vivos.p, kind="stable")
        tokens = vivos.id[orden].tolist()
        probabilidades = vivos.p[orden].tolist()
        lista = [
            Candidato(token, float(originales[token]), probabilidad)
            for token, probabilidad in zip(tokens, probabilidades)
        ]
        cadena.close()
        return lista, elegido

    def agregar(self, token: int) -> None:
        """Agrega un token al final del texto (un paso del loop)."""
        self.llm.eval([token])


def cargar_modelo(tamaño: str = "mediano"):
    """Carga el modelo listo para usar con Outlines:  modelo(prompt, tipo_de_salida)."""
    import outlines

    # chat_mode=False: el prompt va tal cual lo arma `armar_prompt`.
    return outlines.from_llamacpp(_llama(tamaño), chat_mode=False)


def armar_prompt(instrucciones: str, mensaje: str, ejemplos=()) -> str:
    """Arma la conversación en el formato que Qwen3 vio al entrenarse.

    `ejemplos` es una lista de pares (mensaje, respuesta correcta). Con dos o
    tres ejemplos, un modelo chico acierta mucho más.
    El bloque <think> vacío le dice al modelo que responda directo, sin razonar
    en voz alta.
    """
    directo = "<think>\n\n</think>\n\n"
    prompt = f"<|im_start|>system\n{instrucciones}<|im_end|>\n"
    for pregunta, respuesta in ejemplos:
        prompt += f"<|im_start|>user\n{pregunta}<|im_end|>\n"
        prompt += f"<|im_start|>assistant\n{directo}{respuesta}<|im_end|>\n"
    prompt += f"<|im_start|>user\n{mensaje}<|im_end|>\n<|im_start|>assistant\n{directo}"
    return prompt
