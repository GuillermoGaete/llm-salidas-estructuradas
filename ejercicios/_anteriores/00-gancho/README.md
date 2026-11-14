# 00 — Gancho: ¿cumple siempre?

**Tiempo:** 5 minutos · **Necesita:** el entorno del taller (`uv sync`) · **Lo corre el docente, proyectado**

Le pedimos a un modelo chico que convierta un pedido de WhatsApp en JSON, 10 veces seguidas. El prompt dice bien claro «respondé SOLO con JSON».

```
uv run python gancho.py
```

## Qué mirar

- ¿Cuántas de las 10 veces el programa pudo leer la respuesta?
- Cuando falla, ¿la respuesta «está mal»? Una persona la entiende sin problema. ¿Por qué el programa no?
- ¿Las 10 respuestas son iguales? ¿Por qué no?

## La pregunta que abre el taller

> ¿Cómo hago para que algo que tira dados cumpla **siempre**?

Para contestarla necesitamos entender cómo elige el modelo cada palabra. Eso son los ejercicios 01 a 03. La respuesta llega en el 04.
