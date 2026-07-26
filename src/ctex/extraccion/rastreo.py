# src/ctex/extraccion/rastreo.py
"""Paso 5: el barrido por columnas con centroide de la tinta (D38).

Cuatro operaciones sobre el arreglo completo. Ningun bucle sobre pixeles: por
eso este modulo no necesita C++, y por eso D38 revoco la excepcion de D11.
"""

import numpy as np


def barrer(mascara: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Devuelve el centroide de tinta por columna y cuales columnas son validas.

    Las columnas sin un solo pixel de tinta salen como `nan` y marcadas
    invalidas. No se interpolan aqui: eso lo decide el remuestreo (D45).
    """
    tinta = mascara.astype(np.float64)
    alto, ancho = tinta.shape

    filas = np.arange(alto, dtype=np.float64).reshape(-1, 1)

    total = tinta.sum(axis=0)
    ponderada = (tinta * filas).sum(axis=0)

    validez = total > 0
    centroides = np.full(ancho, np.nan, dtype=np.float64)
    centroides[validez] = ponderada[validez] / total[validez]

    return centroides, validez
