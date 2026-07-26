# tests/extraccion/test_escala.py
import pytest

from ctex.extraccion.escala import ErrorDeEscala, fijar_escala
from ctex.extraccion.tipos import Caja


def caja_de_prueba():
    # 100 px de ancho, 200 px de alto
    return Caja(izquierda=10.0, derecha=110.0, arriba=20.0, abajo=220.0)


def test_los_bordes_de_la_caja_valen_los_extremos_del_rango():
    t = fijar_escala(caja_de_prueba(), (0.0, 10.0), (-1.0, 1.0))
    assert t.a_valor_x(10.0) == pytest.approx(0.0)
    assert t.a_valor_x(110.0) == pytest.approx(10.0)
    assert t.a_valor_y(20.0) == pytest.approx(1.0)    # arriba -> ymax
    assert t.a_valor_y(220.0) == pytest.approx(-1.0)  # abajo -> ymin


def test_el_centro_de_la_caja_es_el_centro_del_rango():
    t = fijar_escala(caja_de_prueba(), (0.0, 10.0), (-1.0, 1.0))
    assert t.a_valor_x(60.0) == pytest.approx(5.0)
    assert t.a_valor_y(120.0) == pytest.approx(0.0)


def test_un_rango_invertido_se_rechaza():
    with pytest.raises(ErrorDeEscala):
        fijar_escala(caja_de_prueba(), (10.0, 0.0), (-1.0, 1.0))


def test_un_rango_de_ancho_cero_se_rechaza():
    with pytest.raises(ErrorDeEscala):
        fijar_escala(caja_de_prueba(), (5.0, 5.0), (-1.0, 1.0))
