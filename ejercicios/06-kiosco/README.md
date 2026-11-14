# 06 — El tomador de pedidos del kiosco

**Tiempo:** 20 minutos · **Necesita:** haber hecho el [ejercicio 00](../00-preparacion)

Juntamos todo. Llega un mensaje de WhatsApp y el programa calcula cuánto cobrar.

```
«mandame dos de carne y una coca»
        │  el modelo, con un esquema: escribe un JSON que el programa puede leer
        ▼
{"items": [{"producto": "empanada de carne", "cantidad": 2}, {"producto": "coca", "cantidad": 1}]}
        │  Python: busca los precios y hace la cuenta
        ▼
Total: $4900
```

El modelo hace una sola cosa: convertir el mensaje en datos. El formato es un esquema, como en la parte 3 del ejercicio 05: un pedido es una lista de items, y cada item tiene un producto del menú y una cantidad. La cuenta la hace Python.

## Qué hacer

```
cd ejercicios/06-kiosco
uv run python kiosco.py
```

El programa te pide el pedido de un cliente. Muestra lo que escribió el modelo, cada item con su subtotal y el total. Para salir, escribí `chau`. Probá con:

1. `Hola, mandame dos de carne y una coca`
2. `Buenas! quiero 3 de carne, 6 de pollo y dos cocas`
3. `una docena de carne`
4. `quiero 400 empanadas de carne`
5. Un producto que no está en el menú: `¿tienen empanadas de humita? dame dos`
6. Un mensaje que no es un pedido: `hola, ¿cómo andan?`
7. Abrí `kiosco.py` y agregá un producto al menú, con una línea más en `PRECIOS`. Después pedilo.
8. Cambiá `TEMPERATURA` a `1.0` y repetí los mensajes.
