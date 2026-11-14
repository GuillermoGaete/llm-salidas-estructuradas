"""Descarga los modelos del taller a la carpeta modelos/ (1,5 GB en total).

Conviene correrlo en cada máquina antes de la clase:

    uv run python herramientas/descargar_modelos.py
"""

from taller.modelo import MODELOS, ruta_del_modelo

if __name__ == "__main__":
    for tamaño in MODELOS:
        print(f"{tamaño}: {ruta_del_modelo(tamaño)}")
