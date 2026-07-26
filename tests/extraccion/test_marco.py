# tests/extraccion/test_marco.py
import numpy as np
import pytest

from ctex.extraccion.marco import ErrorDeMarco, detectar_caja


def imagen_con_recuadro(ancho=200, alto=160, borde=20):
    """Papel blanco con un recuadro negro de un pixel de grosor."""
    imagen = np.full((alto, ancho), 255, dtype=np.uint8)
    imagen[borde, borde : ancho - borde] = 0          # arriba
    imagen[alto - borde, borde : ancho - borde] = 0   # abajo
    imagen[borde : alto - borde, borde] = 0           # izquierda
    imagen[borde : alto - borde, ancho - borde] = 0   # derecha
    return imagen


def test_encuentra_los_cuatro_bordes_de_un_recuadro():
    caja = detectar_caja(imagen_con_recuadro())
    assert caja.izquierda == pytest.approx(20, abs=2)
    assert caja.derecha == pytest.approx(180, abs=2)
    assert caja.arriba == pytest.approx(20, abs=2)
    assert caja.abajo == pytest.approx(140, abs=2)


def test_una_imagen_en_blanco_no_tiene_marco():
    blanca = np.full((160, 200), 255, dtype=np.uint8)
    with pytest.raises(ErrorDeMarco):
        detectar_caja(blanca)


def test_una_sola_raya_no_alcanza_para_una_caja():
    imagen = np.full((160, 200), 255, dtype=np.uint8)
    imagen[80, :] = 0
    with pytest.raises(ErrorDeMarco):
        detectar_caja(imagen)
