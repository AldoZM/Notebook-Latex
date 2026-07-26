# src/ctex/extraccion/remuestreo.py
"""Pasos 6 y 7: convertir a valores y quedarse con 20-50 puntos.

La conversion es una transformacion afin que no puede crear ni destruir un
hueco, asi que se aplica solo a las columnas validas y la marca de validez pasa
intacta.
"""

import numpy as np

from ctex.extraccion.tipos import Transformacion

MINIMO_DE_COLUMNAS = 5


class ErrorDeRemuestreo(Exception):
    """No hay columnas validas suficientes para formar una serie."""


def remuestrear(
    centroides: np.ndarray,
    validez: np.ndarray,
    transformacion: Transformacion,
    cuantos: int = 30,
) -> list[list[float]]:
    """Devuelve `cuantos` puntos [x, y] en valores de la grafica."""
    columnas_validas = np.flatnonzero(validez)

    if columnas_validas.size < MINIMO_DE_COLUMNAS:
        raise ErrorDeRemuestreo(
            f"Solo {columnas_validas.size} columnas con tinta: hacen falta al "
            f"menos {MINIMO_DE_COLUMNAS} para formar una serie"
        )

    cuantos = min(cuantos, columnas_validas.size)
    indices = np.linspace(0, columnas_validas.size - 1, cuantos).round().astype(int)
    elegidas = columnas_validas[indices]

    return [
        [
            round(float(transformacion.a_valor_x(columna)), 6),
            round(float(transformacion.a_valor_y(centroides[columna])), 6),
        ]
        for columna in elegidas
    ]
