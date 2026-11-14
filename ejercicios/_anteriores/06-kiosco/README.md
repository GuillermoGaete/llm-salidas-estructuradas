# 06 — Mini proyecto: el tomador de pedidos

**Tiempo:** 20 minutos · **Necesita:** el entorno del taller (`uv sync`)

Juntamos todo. Llega un mensaje de WhatsApp y el programa calcula cuánto cobrar.

```
«mandame dos de carne y una coca»
        │  modelo + esquema (siempre devuelve un Pedido válido)
        ▼
{"items": [{"producto": "empanada de carne", "cantidad": 2}, {"producto": "coca", "cantidad": 1}]}
        │  Python (la cuenta no la hace el modelo)
        ▼
Total: $4900
```

Es el mismo problema del ejercicio 03, con una respuesta más grande: un pedido entero en vez de una sola palabra.

## Qué hacer

```
uv run python ejercicio.py
```

1. **`Item` y `Pedido`**: el esquema.
2. **`tomar_pedido`**: del mensaje al objeto `Pedido`.
3. **`total`**: precio × cantidad, sumado.
4. **Tratá de romperlo** con los mensajes del final.
5. **Atendé vos**: el programa queda esperando pedidos.

## Desafíos

- Rechazá en Python los pedidos con más de 50 unidades de un producto.
- Agregá al esquema `forma_de_pago: Literal["efectivo", "transferencia"]`.
- Cambiá `cargar_modelo("mediano")` por `cargar_modelo("chico")`. ¿El formato falla? ¿Y el contenido?
