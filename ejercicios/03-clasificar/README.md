# 03 — Un LLM adentro de un programa

**Tiempo:** 10 minutos · **Necesita:** haber hecho el [ejercicio 00](../00-preparacion)

Un LLM **no es determinista**: la misma pregunta puede dar respuestas distintas, y cada tanto da una que no esperábamos. Por eso, un programa que usa un LLM tiene que **comprobar lo que el modelo devolvió** antes de usarlo.

El ejemplo: un comercio recibe mensajes de sus clientes. El programa le pide al modelo que diga de qué tipo es cada mensaje y, según la respuesta, hace una cosa distinta.

```
mensaje del cliente  →  LLM  →  «reclamo»   →  se lo paso a una persona
                                «consulta»  →  le mando las preguntas frecuentes
                                «pedido»    →  lo anoto para la cocina
                                «saludo»    →  le devuelvo el saludo
                                otra cosa   →  ???
```

Cuando la respuesta no es una de las cuatro, el programa no sabe qué hacer. Tiene tres salidas: cortar con un error, volver a preguntarle al modelo, o tratar esa respuesta como un caso especial.

## Qué hacer

```
cd ejercicios/03-clasificar
uv run python clasificar.py
```

El programa te pide el mensaje de un cliente y le hace la misma pregunta al modelo 20 veces. Cada respuesta se comprueba: ✅ si es una de las cuatro categorías, ❌ si es otra cosa. Al final cuenta cuántas no pudo usar. Para salir, escribí `chau`. Probá con:

1. Un reclamo: `Las empanadas llegaron frías y tarde`.
2. Un saludo: `Hola, buenas tardes`.
3. Un mensaje que es dos cosas a la vez: `Hola, ¿tienen coca? Quiero dos`.
4. Un mensaje que no es ninguna de las cuatro: `jajaja`.
5. El mismo mensaje otra vez. ¿Sale la misma cantidad de ❌?
6. Abrí `clasificar.py`, cambiá `TEMPERATURA` a `0.2` y repetí el primer mensaje.
