# 04 — La máscara: tapar opciones antes de elegir

**Tiempo:** 25 minutos · **Necesita:** solo Python (la segunda parte usa el entorno del taller)

**Este es el ejercicio central del taller.** En el ejercicio 03 el modelo respondió, cada tanto, algo que el programa no esperaba. Acá vemos cómo se evita.

La idea: **antes del sorteo, a los tokens que no sirven se les pone probabilidad cero.** Eso es la máscara.

Vamos a obligar a un modelo a escribir una patente (`AB 123 CD`). Para que quede claro que el truco no depende de que el modelo sea bueno, usamos un «modelo» que da puntajes **al azar**.

```
puntajes → [MÁSCARA: los que rompen el formato pasan a −∞] → softmax → dado
```

## Qué hacer

```
python ejercicio.py
```

1. **`enmascarar`**: los tokens no permitidos pasan a valer menos infinito.
2. **`avanzar`**: dado un estado y un carácter, ¿sirve? ¿A qué estado paso?
3. **`probar_token`**: lo mismo, pero para un token de varios caracteres.
4. **Cambiá `FORMATO`** por una fecha (`"DD/DD/DDDD"`) y por un DNI (`"DD.DDD.DDD"`).

### Segunda parte: con el modelo real

```
uv run python con_modelo.py
```

Usa **tus funciones** sobre los 150.000 tokens del modelo de verdad.
