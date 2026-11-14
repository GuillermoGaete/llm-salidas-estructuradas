"""Playground — Un servidor chico para probar prompts.

Abre una página con tres pestañas:
  1. Comparar modelos: el mismo prompt a dos modelos locales y a uno de OpenAI,
     con la probabilidad de cada token.
  2. Salida estructurada: un prompt y un modelo de Pydantic. La respuesta sale
     con ese formato.
  3. Sesgos: una pregunta con opciones, repetida muchas veces, y la cuenta de
     qué eligió el modelo.

Cómo correrlo:
    uv run python servidor.py
    y abrir http://localhost:8000 en el navegador.

Para usar los modelos de OpenAI hace falta una clave, que se pasa así:
    OPENAI_API_KEY="sk-..." uv run python servidor.py
"""

import copy
import json
import os
import random
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np
import outlines
from llama_cpp import Llama, LogitsProcessorList
from outlines.types import Choice
from pydantic import BaseModel, ValidationError
from scipy.special import log_softmax

from casos import ESTRUCTURADOS, SESGOS

PUERTO = 8000
ALTERNATIVAS = 5  # cuántas opciones mostrar para cada token

CARPETA = Path(__file__).resolve().parent  # la carpeta de este archivo
MODELOS = CARPETA.parents[1] / "modelos"   # la carpeta modelos/, en la raíz del taller

# La clave de OpenAI se lee de la terminal: no se escribe en ningún archivo.
CLAVE_DE_OPENAI = os.environ.get("OPENAI_API_KEY", "")
URL_DE_OPENAI = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

cargados = {}               # los modelos locales ya cargados: nombre del archivo → modelo
candado = threading.Lock()  # los modelos locales atienden un solo pedido por vez


# ---------------------------------------------------------------------------
# Los modelos
# ---------------------------------------------------------------------------
def modelos_locales():
    """Los archivos de modelo que hay en la carpeta modelos/."""
    return sorted(archivo.name for archivo in MODELOS.glob("*.gguf"))


def modelos_de_openai():
    """Los modelos de texto que la clave puede usar. Sin clave, ninguno."""
    if not CLAVE_DE_OPENAI:
        return []
    respuesta = llamar_a_openai("/models")
    nombres = [modelo["id"] for modelo in respuesta["data"]]
    # De toda la lista quedan los «gpt», sin los de audio, imagen o búsqueda.
    descartar = ("audio", "realtime", "tts", "transcribe", "search", "image", "instruct")
    return sorted(n for n in nombres if n.startswith("gpt-") and not any(d in n for d in descartar))


def modelo_local(archivo):
    """Devuelve un modelo local ya cargado; si no lo está, lo carga.

    Devuelve dos cosas: el modelo de llama-cpp y el mismo modelo envuelto por
    Outlines, que es el que acepta un formato. Hay que llamarla con el candado tomado.
    """
    if archivo not in modelos_locales():
        raise ValueError("No existe el modelo " + archivo)
    if archivo not in cargados:
        # Se guardan dos modelos como máximo: si hay que cargar un tercero, se saca el más viejo.
        if len(cargados) >= 2:
            cargados.pop(next(iter(cargados)))["llama"].close()
        # logits_all=True: que la librería guarde los logits. Hace falta para pedir logprobs.
        # seed: el número con el que arranca el sorteo. Acá va uno al azar; si no se lo
        #   pasamos, cada vez que se arranca el servidor salen las mismas respuestas.
        # verbose=False: que la librería no llene la pantalla con sus mensajes internos.
        llama = Llama(str(MODELOS / archivo), logits_all=True, seed=random.randrange(2**32), verbose=False)
        cargados[archivo] = {"llama": llama, "outlines": outlines.from_llamacpp(llama)}
    return cargados[archivo]["llama"], cargados[archivo]["outlines"]


def llamar_a_openai(ruta, datos=None):
    """Hace un pedido a la API de OpenAI y devuelve la respuesta, ya convertida de JSON."""
    pedido = urllib.request.Request(
        URL_DE_OPENAI + ruta,
        # Con datos el pedido es un POST; sin datos, un GET.
        data=json.dumps(datos).encode() if datos else None,
        headers={"Authorization": "Bearer " + CLAVE_DE_OPENAI, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(pedido) as respuesta:
        return json.load(respuesta)


def conversar_con_openai(pedido):
    """Le pide una respuesta a un modelo de OpenAI. `pedido` es lo que va en el cuerpo del pedido."""
    if not CLAVE_DE_OPENAI:
        raise ValueError("Falta la clave: arrancá el servidor con OPENAI_API_KEY.")
    # Razonamiento apagado: algunos modelos «piensan» antes de responder, y mientras
    # lo hacen no devuelven logprobs completos ni dejan cambiar la temperatura.
    pedido = dict(pedido, reasoning_effort="none")
    try:
        return llamar_a_openai("/chat/completions", pedido)
    except urllib.error.HTTPError as error:
        # Los modelos que no razonan no conocen ese ajuste y rechazan el pedido (error 400).
        # En ese caso se manda de nuevo, igual pero sin él.
        if error.code != 400:
            raise
        del pedido["reasoning_effort"]
        return llamar_a_openai("/chat/completions", pedido)


# ---------------------------------------------------------------------------
# Pestaña 1 — Comparar modelos
# ---------------------------------------------------------------------------
def responder_local(archivo, prompt, maximo, temperatura):
    """Le manda el prompt a un modelo local."""
    with candado:
        llama, _ = modelo_local(archivo)
        # temperature: la que se eligió en la página. Con 1.0 el sorteo usa las probabilidades
        #   tal como las da el modelo; más baja, sale casi siempre el token más probable;
        #   más alta, salen más seguido los menos probables.
        # logprobs y top_logprobs: que devuelva la probabilidad de cada token y de sus alternativas.
        respuesta = llama.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=temperatura,
            max_tokens=maximo,
            logprobs=True,
            top_logprobs=ALTERNATIVAS,
        )
    return resumir(respuesta)


def responder_openai(modelo, prompt, maximo, temperatura):
    """Le manda el mismo prompt a un modelo de OpenAI. El pedido tiene la misma forma que el local."""
    respuesta = conversar_con_openai(
        {
            "model": modelo,
            "messages": [{"role": "user", "content": prompt}],
            "max_completion_tokens": maximo,
            "temperature": temperatura,
            "logprobs": True,
            "top_logprobs": ALTERNATIVAS,
        }
    )
    return resumir(respuesta)


def resumir(respuesta):
    """De todo lo que trae la respuesta, lo que muestra la página: el texto y,
    por cada token, su logprob y los de las otras opciones que había."""
    opcion = respuesta["choices"][0]
    logprobs = opcion.get("logprobs") or {}
    tokens = []
    for dato in logprobs.get("content") or []:
        tokens.append(
            {
                "token": dato["token"],
                "logprob": float(dato["logprob"]),
                "opciones": [{"token": o["token"], "logprob": float(o["logprob"])} for o in dato["top_logprobs"]],
            }
        )
    return {"texto": opcion["message"]["content"], "tokens": tokens}


# ---------------------------------------------------------------------------
# Pestañas 2 y 3 — Una respuesta local, anotando las probabilidades de cada token
# ---------------------------------------------------------------------------
class Registro:
    """Anota, en cada paso de una respuesta, las probabilidades de los tokens.

    La librería lo llama una vez por paso, justo antes del sorteo, con los logits
    que dio el modelo. Si hay una máscara, también la aplica acá: a los tokens que
    no respetan el formato les deja el logit en menos infinito.
    """

    def __init__(self, mascara):
        self.mascara = mascara  # la máscara que armó Outlines, o None si la respuesta es libre
        self.pasos = []         # lo anotado: un elemento por cada token de la respuesta
        self.pendiente = None   # el paso que se está sorteando: todavía no se sabe qué token salió

    def __call__(self, leidos, logits):
        # `leidos` son los tokens que el modelo leyó hasta ahora. El último es el que salió
        # sorteado en el paso anterior: recién acá nos enteramos de cuál fue.
        if self.pendiente is not None:
            self.anotar(int(leidos[-1]))

        # log_softmax: de logits a logprobs. El logprob es el logaritmo de la probabilidad.
        sin_mascara = log_softmax(logits)
        con_mascara = None
        if self.mascara is not None:
            logits = self.mascara(leidos, logits)
            con_mascara = log_softmax(logits)
        self.pendiente = (sin_mascara, con_mascara)
        return logits  # la librería sortea con estos logits

    def anotar(self, elegido):
        """Guarda el paso pendiente, ahora que se sabe qué token salió."""
        sin_mascara, con_mascara = self.pendiente
        self.pendiente = None

        # Los tokens para mostrar: los más probables sin la máscara, los más probables
        # con la máscara, y el que salió (que puede no estar entre los más probables).
        # np.argsort ordena del menos probable al más probable: [::-1] da vuelta la lista.
        mostrar = list(np.argsort(sin_mascara)[::-1][:ALTERNATIVAS])
        if con_mascara is not None:
            for token in np.argsort(con_mascara)[::-1][:ALTERNATIVAS]:
                # Si la máscara deja pasar pocos tokens, entre «los más probables» aparecen
                # tokens tapados (logprob de menos infinito): esos no se agregan.
                if not np.isneginf(con_mascara[token]):
                    mostrar.append(token)
        mostrar.append(elegido)

        opciones = []
        for token in dict.fromkeys(int(token) for token in mostrar):  # dict.fromkeys saca los repetidos
            opcion = {"numero": token, "logprob": float(sin_mascara[token]), "salio": token == elegido}
            if con_mascara is not None:
                # Un token tapado por la máscara se anota con None.
                tapado = np.isneginf(con_mascara[token])
                opcion["logprob_con_mascara"] = None if tapado else float(con_mascara[token])
            opciones.append(opcion)
        self.pasos.append(opciones)


def generar(llama, mensajes, mascara, temperatura, maximo):
    """Le pide una respuesta a un modelo local y anota las probabilidades de cada token.

    `mascara` es la máscara que armó Outlines, o None si la respuesta es libre.
    Devuelve el texto y la lista de tokens, con la misma forma que usa la pestaña 1.
    Hay que llamarla con el candado tomado.
    """
    registro = Registro(mascara)
    respuesta = llama.create_chat_completion(
        messages=mensajes,
        # temperature: la que se eligió en la página (por defecto esta función usa 0.2).
        temperature=temperatura,
        # max_tokens: se pide un token de más. El registro se entera de qué token salió
        #   recién en el paso siguiente; con uno de más, el último que nos interesa
        #   también queda anotado. El token de más se descarta más abajo.
        max_tokens=maximo + 1,
        # Los tres valores que siguen apagan los recortes que la librería trae prendidos,
        # igual que en el ejercicio 02. Así el sorteo usa las probabilidades que se muestran.
        top_k=0,    # no descarta ningún token (por defecto se queda con los 40 mejores)
        top_p=1.0,  # no descarta ningún token (por defecto es 0.95)
        min_p=0.0,  # no descarta ningún token (por defecto es 0.05)
        # logits_processor: lo que la librería llama en cada paso, antes del sorteo.
        logits_processor=LogitsProcessorList([registro]),
    )
    # Borrar lo que el modelo leyó, como hace Outlines después de cada respuesta.
    llama.reset()

    texto = respuesta["choices"][0]["message"]["content"]
    pasos = registro.pasos
    if respuesta["usage"]["completion_tokens"] > maximo:
        # La respuesta llegó al máximo: se saca el token de más y se arma el texto con los que quedan.
        pasos = pasos[:maximo]
        elegidos = [opcion["numero"] for paso in pasos for opcion in paso if opcion["salio"]]
        texto = llama.detokenize(elegidos).decode("utf-8", errors="replace")

    # Pasar cada paso a la forma que espera la página: el número de token se cambia por su texto.
    tokens = []
    for paso in pasos:
        opciones = []
        for opcion in paso:
            # special=True: que las marcas especiales (como la de «terminé») se vean con su
            #   nombre. Si no, se convierten en un texto vacío.
            # errors="replace": algunos tokens son solo una parte de una letra o de un
            #   emoji. En ese caso se muestra � en vez de dar un error.
            pieza = llama.detokenize([opcion.pop("numero")], special=True).decode("utf-8", errors="replace")
            # La librería devuelve un texto vacío para los tokens de más de 32 bytes (por
            # ejemplo, 40 espacios seguidos). Esos no se muestran, salvo que sea el que salió.
            if pieza == "" and not opcion["salio"]:
                continue
            opciones.append({"token": pieza, **opcion})
        salio = next(opcion for opcion in opciones if opcion["salio"])
        token = {"token": salio["token"], "logprob": salio["logprob"], "opciones": opciones}
        if mascara is not None:
            token["logprob_con_mascara"] = salio["logprob_con_mascara"]
        tokens.append(token)
    return texto, tokens


def conversar_con_logprobs(pedido):
    """Como conversar_con_openai, pidiendo además los logprobs.
    Si el modelo no los da, repite el pedido sin pedirlos."""
    try:
        return conversar_con_openai(dict(pedido, logprobs=True, top_logprobs=ALTERNATIVAS))
    except urllib.error.HTTPError as error:
        if error.code != 400:
            raise
        return conversar_con_openai(pedido)


# ---------------------------------------------------------------------------
# Pestaña 2 — Salida estructurada
# ---------------------------------------------------------------------------
def modelo_de_pydantic(codigo):
    """Convierte el texto que se escribió en la página en un modelo de Pydantic.

    Ejecuta ese código y devuelve la última clase que hereda de BaseModel. Si hay
    varias (un modelo que usa a otros), la principal tiene que ser la última.
    """
    # Lo que el código puede usar sin importarlo.
    espacio = {}
    exec("from enum import Enum\nfrom typing import *\nfrom pydantic import BaseModel, Field\n", espacio)
    exec(codigo, espacio)
    clases = [
        valor
        for valor in espacio.values()
        if isinstance(valor, type) and issubclass(valor, BaseModel) and valor is not BaseModel
    ]
    if not clases:
        raise ValueError("El código no define ningún modelo: tiene que haber una clase que herede de BaseModel.")
    return clases[-1]


def esquema_estricto(esquema):
    """Adapta un esquema a lo que pide OpenAI: en cada objeto todos los datos son
    obligatorios, y no puede haber ninguno de más."""
    esquema = copy.deepcopy(esquema)

    def adaptar(parte):
        if isinstance(parte, dict):
            if "properties" in parte:
                parte["required"] = list(parte["properties"])
                parte["additionalProperties"] = False
            parte.pop("default", None)
            for valor in parte.values():
                adaptar(valor)
        elif isinstance(parte, list):
            for valor in parte:
                adaptar(valor)

    adaptar(esquema)
    return esquema


def responder_con_formato(origen, nombre, prompt, codigo, maximo, temperatura, forzar):
    """Le manda el prompt a un modelo. Si `forzar` es verdadero, la respuesta tiene que
    cumplir el modelo de Pydantic; si no, el modelo responde lo que quiere.
    En los dos casos se comprueba si la respuesta cumple."""
    Formato = modelo_de_pydantic(codigo)
    esquema = Formato.model_json_schema()  # el mismo formato, escrito como JSON Schema
    mensajes = [{"role": "user", "content": prompt}]

    if origen == "local":
        with candado:
            llama, con_outlines = modelo_local(nombre)
            mascara = None
            if forzar:
                # Outlines recibe el formato y arma la máscara, como en el ejercicio 05.
                # En el ejercicio también hace la llamada al modelo; acá la hacemos nosotros
                # (en `generar`), para poder anotar las probabilidades de cada token.
                mascara = outlines.Generator(con_outlines, Formato).logits_processor
            texto, tokens = generar(llama, mensajes, mascara, temperatura, maximo)
    else:
        pedido = {"model": nombre, "messages": mensajes, "max_completion_tokens": maximo, "temperature": temperatura}
        if forzar:
            # A OpenAI el formato se le pasa como JSON Schema. Con strict=True la respuesta
            # lo cumple siempre: del otro lado también hay una máscara.
            pedido["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": Formato.__name__, "strict": True, "schema": esquema_estricto(esquema)},
            }
        respuesta = conversar_con_logprobs(pedido)
        texto = respuesta["choices"][0]["message"]["content"] or ""
        tokens = resumir(respuesta)["tokens"]

    # Comprobar la respuesta contra el modelo de Pydantic.
    try:
        Formato.model_validate_json(texto)
        problema = ""
    except ValidationError as error:
        # error.errors() trae un problema por cada dato que está mal: dónde está y qué le pasa.
        renglones = []
        for uno in error.errors():
            if uno["type"] == "json_invalid":
                # Pasa cuando el modelo responde con texto libre, o cuando el JSON quedó cortado.
                renglones.append("La respuesta no es un JSON válido.")
            else:
                lugar = ".".join(str(parte) for parte in uno["loc"])  # por ejemplo: items.0.cantidad
                renglones.append(lugar + ": " + uno["msg"])
        problema = "\n".join(renglones)
    return {"texto": texto, "cumple": not problema, "problema": problema, "esquema": esquema, "tokens": tokens}


# ---------------------------------------------------------------------------
# Pestaña 3 — Sesgos
# ---------------------------------------------------------------------------
def elegir(origen, nombre, prompt, opciones, temperatura):
    """Le hace una pregunta a un modelo y lo obliga a responder con una de las opciones."""
    mensajes = [{"role": "user", "content": prompt}]
    if origen == "local":
        with candado:
            llama, con_outlines = modelo_local(nombre)
            # Choice: una lista cerrada. La máscara solo deja escribir una de las opciones.
            mascara = outlines.Generator(con_outlines, Choice(opciones)).logits_processor
            # 40: un tope de tokens, por si una opción es muy larga.
            texto, tokens = generar(llama, mensajes, mascara, temperatura, 40)
        return {"respuesta": texto, "tokens": tokens}
    # En OpenAI, la lista cerrada es un JSON con un solo dato, que solo puede valer una de las opciones.
    esquema = {
        "type": "object",
        "properties": {"respuesta": {"type": "string", "enum": opciones}},
        "required": ["respuesta"],
        "additionalProperties": False,
    }
    respuesta = conversar_con_logprobs(
        {
            "model": nombre,
            "messages": mensajes,
            "max_completion_tokens": 60,
            "temperature": temperatura,
            "response_format": {"type": "json_schema", "json_schema": {"name": "eleccion", "strict": True, "schema": esquema}},
        }
    )
    elegida = json.loads(respuesta["choices"][0]["message"]["content"])["respuesta"]
    return {"respuesta": elegida, "tokens": resumir(respuesta)["tokens"]}


# ---------------------------------------------------------------------------
# El servidor
# ---------------------------------------------------------------------------
def explicar(error):
    """El mensaje de un error, para mostrarlo en la página."""
    if isinstance(error, urllib.error.HTTPError):
        # OpenAI explica el problema en el cuerpo de la respuesta.
        try:
            return json.load(error)["error"]["message"]
        except Exception:
            return "OpenAI respondió con el error " + str(error.code)
    # Si el modelo de Pydantic está mal escrito, se muestra también qué tipo de error es.
    return f"{type(error).__name__}: {error}"


class Pedidos(BaseHTTPRequestHandler):
    """Atiende lo que pide la página."""

    def do_GET(self):
        if self.path == "/":
            self.enviar("text/html; charset=utf-8", (CARPETA / "pagina.html").read_bytes())
        elif self.path == "/modelos":
            try:
                openai = modelos_de_openai()
            except Exception:
                openai = []
            self.enviar_json({"locales": modelos_locales(), "openai": openai, "hay_clave": bool(CLAVE_DE_OPENAI)})
        elif self.path == "/casos":
            self.enviar_json({"estructurados": ESTRUCTURADOS, "sesgos": SESGOS})
        else:
            self.send_error(404)

    def do_POST(self):
        # Solo se atienden los pedidos que hace la propia página. Este servidor ejecuta el
        # código del modelo de Pydantic que recibe; sin este control, cualquier otra página
        # abierta en el navegador podría mandarle código para ejecutar.
        propios = (f"localhost:{PUERTO}", f"127.0.0.1:{PUERTO}")
        origen = self.headers.get("Origin")
        if self.headers.get("Host") not in propios or (origen and origen.removeprefix("http://") not in propios):
            return self.send_error(403)

        largo = int(self.headers["Content-Length"])
        p = json.loads(self.rfile.read(largo))
        temperatura = p.get("temperatura", 1.0)  # si la página no la manda, 1.0
        try:
            if self.path == "/local":
                resultado = responder_local(p["modelo"], p["prompt"], p["maximo"], temperatura)
            elif self.path == "/openai":
                resultado = responder_openai(p["modelo"], p["prompt"], p["maximo"], temperatura)
            elif self.path == "/estructurada":
                resultado = responder_con_formato(p["origen"], p["modelo"], p["prompt"], p["codigo"], p["maximo"], temperatura, p["forzar"])
            elif self.path == "/elegir":
                resultado = elegir(p["origen"], p["modelo"], p["prompt"], p["opciones"], temperatura)
            else:
                resultado = {"error": "No existe " + self.path}
        except Exception as error:
            resultado = {"error": explicar(error)}
        self.enviar_json(resultado)

    def enviar_json(self, datos):
        self.enviar("application/json; charset=utf-8", json.dumps(datos, ensure_ascii=False).encode())

    def enviar(self, tipo, contenido):
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(contenido)))
        self.end_headers()
        self.wfile.write(contenido)


if __name__ == "__main__":
    # "127.0.0.1": el servidor solo atiende a esta computadora. Así nadie más
    # en la red puede usar la página (ni la clave de OpenAI).
    servidor = ThreadingHTTPServer(("127.0.0.1", PUERTO), Pedidos)
    print(f"Playground listo en http://localhost:{PUERTO}  (para cerrarlo: Ctrl + C)")
    print("Clave de OpenAI:", "sí" if CLAVE_DE_OPENAI else "no (los modelos de OpenAI quedan apagados)")
    servidor.serve_forever()
