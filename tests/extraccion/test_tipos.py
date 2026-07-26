# tests/extraccion/test_tipos.py
import pytest

from ctex.extraccion.tipos import Caja, Recta, Transformacion


def test_una_caja_conoce_su_ancho_y_su_alto():
    caja = Caja(izquierda=10.0, derecha=110.0, arriba=20.0, abajo=220.0)
    assert caja.ancho == 100.0
    assert caja.alto == 200.0


def test_una_caja_invertida_se_rechaza():
    with pytest.raises(ValueError):
        Caja(izquierda=110.0, derecha=10.0, arriba=20.0, abajo=220.0)


def test_la_transformacion_lleva_columna_a_valor():
    t = Transformacion(escala_x=0.1, escala_y=0.05, izquierda=10.0, arriba=20.0)
    assert t.a_valor_x(10.0) == pytest.approx(0.0)
    assert t.a_valor_x(110.0) == pytest.approx(10.0)


def test_el_eje_y_va_al_reves_que_las_filas():
    # ymax esta ARRIBA en la grafica, pero la fila 0 esta arriba en la imagen.
    t = Transformacion(escala_x=0.1, escala_y=0.05, izquierda=10.0, arriba=20.0)
    t = t.con_ymax(11.0)
    assert t.a_valor_y(20.0) == pytest.approx(11.0)   # fila de arriba -> ymax
    assert t.a_valor_y(220.0) == pytest.approx(1.0)   # 11 - 200*0.05


def test_una_recta_guarda_rho_y_theta():
    r = Recta(rho=42.0, theta=0.0)
    assert r.rho == 42.0
    assert r.theta == 0.0
