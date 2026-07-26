# tests/extraccion/test_remuestreo.py
import numpy as np
import pytest

from ctex.extraccion.remuestreo import ErrorDeRemuestreo, remuestrear
from ctex.extraccion.tipos import Transformacion


def transformacion_identidad_en_x():
    # 100 px de ancho valen 0..10; 200 px de alto valen -1..1
    return Transformacion(
        escala_x=0.1, escala_y=0.01, izquierda=0.0, arriba=0.0,
        xmin=0.0, ymax=1.0,
    )


def test_devuelve_la_cantidad_pedida():
    centroides = np.full(100, 50.0)
    validez = np.ones(100, dtype=bool)
    puntos = remuestrear(centroides, validez, transformacion_identidad_en_x(), 10)
    assert len(puntos) == 10


def test_los_puntos_estan_en_valores_no_en_pixeles():
    centroides = np.full(100, 100.0)   # fila 100 -> y = 1 - 100*0.01 = 0
    validez = np.ones(100, dtype=bool)
    puntos = remuestrear(centroides, validez, transformacion_identidad_en_x(), 3)
    assert puntos[0][0] == pytest.approx(0.0)
    assert puntos[-1][0] == pytest.approx(9.9, abs=0.2)
    for _, y in puntos:
        assert y == pytest.approx(0.0)


def test_las_columnas_invalidas_no_aportan_punto():
    centroides = np.full(100, 50.0)
    validez = np.ones(100, dtype=bool)
    validez[:50] = False
    centroides[:50] = np.nan
    puntos = remuestrear(centroides, validez, transformacion_identidad_en_x(), 5)
    assert all(x >= 5.0 - 0.2 for x, _ in puntos)


def test_los_puntos_salen_ordenados_por_x():
    centroides = np.arange(100, dtype=float)
    validez = np.ones(100, dtype=bool)
    puntos = remuestrear(centroides, validez, transformacion_identidad_en_x(), 8)
    equis = [x for x, _ in puntos]
    assert equis == sorted(equis)


def test_con_menos_de_cinco_columnas_validas_levanta():
    centroides = np.full(100, np.nan)
    validez = np.zeros(100, dtype=bool)
    centroides[:3] = 10.0
    validez[:3] = True
    with pytest.raises(ErrorDeRemuestreo):
        remuestrear(centroides, validez, transformacion_identidad_en_x(), 10)
