# src/ctex/extraccion/marco.py
"""Paso 1: encontrar la caja del area de la grafica.

OpenCV se queda aqui dentro: hacia afuera solo salen Caja y Recta.
"""

import cv2
import numpy as np

from ctex.extraccion.tipos import Caja, Recta

# Cuanto puede desviarse una recta de la horizontal o la vertical para seguir
# contando como tal. 5 grados: mas que eso ya no es un eje de una grafica.
TOLERANCIA = np.deg2rad(5)


class ErrorDeMarco(Exception):
    """No se pudo formar la caja del area de la grafica."""


def binarizar(imagen: np.ndarray) -> np.ndarray:
    """Deja la tinta en blanco y el papel en negro, que es lo que Hough espera."""
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY) if imagen.ndim == 3 else imagen
    _, binaria = cv2.threshold(
        gris, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    return binaria


def _clasificar(lineas: np.ndarray) -> tuple[list[float], list[float]]:
    """Separa las rectas en posiciones de verticales y de horizontales.

    El punto de la recta mas cercano al origen es (rho*cos(theta),
    rho*sin(theta)). Para una casi vertical, esa x es su posicion; para una
    casi horizontal, esa y lo es.
    """
    equis: list[float] = []
    yes: list[float] = []
    for (rho, theta), in lineas:
        if theta < TOLERANCIA or theta > np.pi - TOLERANCIA:
            equis.append(abs(rho * np.cos(theta)))
        elif abs(theta - np.pi / 2) < TOLERANCIA:
            yes.append(abs(rho * np.sin(theta)))
    return equis, yes


def detectar_caja(imagen: np.ndarray) -> Caja:
    """Devuelve los cuatro bordes del area de la grafica."""
    binaria = binarizar(imagen)
    alto, ancho = binaria.shape

    # Un eje cruza buena parte de la imagen. Pedir la mitad del lado menor deja
    # fuera el ruido y las lineas cortas sin dejar fuera los ejes.
    umbral = max(int(min(alto, ancho) * 0.5), 10)
    lineas = cv2.HoughLines(binaria, 1, np.pi / 180, umbral)

    if lineas is None:
        raise ErrorDeMarco("Hough no encontro ninguna recta larga en la imagen")

    equis, yes = _clasificar(lineas)

    if len(equis) < 2 or len(yes) < 2:
        raise ErrorDeMarco(
            f"No hay dos verticales y dos horizontales: se encontraron "
            f"{len(equis)} verticales y {len(yes)} horizontales"
        )

    return Caja(
        izquierda=min(equis),
        derecha=max(equis),
        arriba=min(yes),
        abajo=max(yes),
    )
