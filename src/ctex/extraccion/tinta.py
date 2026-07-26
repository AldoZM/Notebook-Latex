# src/ctex/extraccion/tinta.py
"""Paso 4: quitar el marco y la rejilla, dejar la curva.

Segunda y ultima casa de OpenCV en el extractor.
"""

import cv2
import numpy as np

from ctex.extraccion.tipos import Caja

# Cuantos pixeles a cada lado de un borde de la caja se borran. Un eje dibujado
# a mano tiene grosor; dos pixeles cubren el caso limpio y el mediano.
GROSOR_BORDE = 2

# Debajo de esto se considera tinta. La rejilla impresa vive alrededor de 200 y
# la curva alrededor de 0; 128 los separa con holgura. Es un numero por
# calibrar cuando entren las fotos del nivel 0.
UMBRAL_TINTA = 128


class ErrorDeTinta(Exception):
    """No quedo curva despues de quitar el marco y la rejilla."""


def aislar_curva(imagen: np.ndarray, caja: Caja) -> np.ndarray:
    """Devuelve una mascara booleana del tamano de la imagen con solo la curva."""
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY) if imagen.ndim == 3 else imagen

    mascara = gris < UMBRAL_TINTA

    # Fuera de la caja no hay grafica: etiquetas, titulo, lo que sea.
    fuera = np.ones_like(mascara)
    arriba = int(caja.arriba)
    abajo = int(caja.abajo)
    izquierda = int(caja.izquierda)
    derecha = int(caja.derecha)
    fuera[arriba:abajo, izquierda:derecha] = False
    mascara[fuera] = False

    # Los cuatro bordes de la caja, con su grosor.
    for fila in (arriba, abajo):
        mascara[
            max(fila - GROSOR_BORDE, 0) : fila + GROSOR_BORDE + 1, :
        ] = False
    for columna in (izquierda, derecha):
        mascara[
            :, max(columna - GROSOR_BORDE, 0) : columna + GROSOR_BORDE + 1
        ] = False

    if not mascara.any():
        raise ErrorDeTinta(
            "No quedo ningun pixel de curva dentro de la caja despues de "
            "quitar el marco y la rejilla"
        )

    return mascara
