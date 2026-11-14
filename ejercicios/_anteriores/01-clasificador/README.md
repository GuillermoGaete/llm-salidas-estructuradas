# 01 — Un clasificador desde cero

**Tiempo:** 15 minutos · **Necesita:** solo Python

Al kiosco le llegan mensajes por WhatsApp. Vamos a construir un programa que decide si cada mensaje es un **pedido**, una **consulta** o un **reclamo**.

```
mensaje → puntajes → probabilidades → etiqueta
```

## Qué hacer

Abrí `ejercicio.py` y corrélo:

```
python ejercicio.py
```

Te va a decir qué paso falta. Completalos en orden:

1. **`softmax`**: convierte los 3 puntajes en 3 probabilidades que suman 1.
2. **`etiqueta`**: devuelve la clase con más probabilidad.
3. **Experimentá** con los tres mensajes del final.
