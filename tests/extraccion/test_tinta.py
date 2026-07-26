# tests/extraccion/test_tinta.py
import numpy as np
import pytest

from ctex.extraccion.tinta import ErrorDeTinta, aislar_curva
from ctex.extraccion.tipos import Caja


def imagen_con_recuadro_y_curva():
    """Recuadro negro, rejilla gris clara, y una diagonal negra dentro."""
    imagen = np.full((160, 200), 255, dtype=np.uint8)
    imagen[20, 20:180] = 0
    imagen[140, 20:180] = 0
    imagen[20:140, 20] = 0
    imagen[20:140, 180] = 0
    for x in range(40, 180, 20):        # rejilla clara
        imagen[21:140, x] = 200
    for i in range(100):                # la curva
        imagen[30 + i, 30 + i] = 0
    return imagen


CAJA = Caja(izquierda=20.0, derecha=180.0, arriba=20.0, abajo=140.0)


def test_la_curva_sobrevive():
    mascara = aislar_curva(imagen_con_recuadro_y_curva(), CAJA)
    assert mascara[80, 80]


def test_la_rejilla_clara_no_sobrevive():
    mascara = aislar_curva(imagen_con_recuadro_y_curva(), CAJA)
    assert not mascara[100, 60]


def test_los_bordes_de_la_caja_no_sobreviven():
    mascara = aislar_curva(imagen_con_recuadro_y_curva(), CAJA)
    assert not mascara[:, 20].any()
    assert not mascara[20, :].any()


def test_la_mascara_conserva_el_tamano_de_la_imagen():
    imagen = imagen_con_recuadro_y_curva()
    assert aislar_curva(imagen, CAJA).shape == imagen.shape


def test_sin_curva_dentro_de_la_caja_levanta():
    vacia = np.full((160, 200), 255, dtype=np.uint8)
    vacia[20, 20:180] = 0
    vacia[140, 20:180] = 0
    vacia[20:140, 20] = 0
    vacia[20:140, 180] = 0
    with pytest.raises(ErrorDeTinta):
        aislar_curva(vacia, CAJA)
