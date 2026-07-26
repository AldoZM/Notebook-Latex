"""Cargar una imagen del disco.

Existe para que `extractor.py` no tenga que importar OpenCV. La restriccion del
diseno es que la biblioteca de vision viva solo en los modulos que hacen vision
—`marco.py`, `tinta.py` y este—, de modo que cambiarla algun dia se detenga ahi
y no se propague por la tuberia.
"""

from pathlib import Path

import cv2
import numpy as np


def cargar(ruta: Path) -> np.ndarray:
    """Devuelve la imagen en escala de grises como arreglo de NumPy.

    Levanta FileNotFoundError si el archivo no existe o si existe pero no se
    puede leer como imagen, que para quien llama es el mismo problema: no hay
    imagen con que trabajar.
    """
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"No existe la imagen: {ruta}")

    imagen = cv2.imread(str(ruta), cv2.IMREAD_GRAYSCALE)
    if imagen is None:
        raise FileNotFoundError(f"No se pudo leer como imagen: {ruta}")

    return imagen
