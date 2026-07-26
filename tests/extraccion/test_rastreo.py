# tests/extraccion/test_rastreo.py
import numpy as np
import pytest

from ctex.extraccion.rastreo import barrer


def test_una_horizontal_da_centroide_constante():
    mascara = np.zeros((20, 20), dtype=bool)
    mascara[7, :] = True
    centroides, validez = barrer(mascara)
    assert validez.all()
    assert centroides == pytest.approx(np.full(20, 7.0))


def test_una_diagonal_se_recupera_tal_cual():
    mascara = np.zeros((20, 20), dtype=bool)
    for i in range(20):
        mascara[i, i] = True
    centroides, validez = barrer(mascara)
    assert validez.all()
    assert centroides == pytest.approx(np.arange(20, dtype=float))


def test_un_trazo_grueso_promedia_al_centro():
    mascara = np.zeros((20, 20), dtype=bool)
    mascara[8:11, :] = True          # filas 8, 9 y 10
    centroides, _ = barrer(mascara)
    assert centroides == pytest.approx(np.full(20, 9.0))


def test_las_columnas_sin_tinta_salen_invalidas_no_cero():
    mascara = np.zeros((20, 20), dtype=bool)
    mascara[5, :] = True
    mascara[:, 12:14] = False        # se vacian dos columnas
    centroides, validez = barrer(mascara)
    assert not validez[12]
    assert not validez[13]
    assert np.isnan(centroides[12])
    assert validez[11] and validez[14]


def test_una_mascara_vacia_no_tiene_ninguna_columna_valida():
    centroides, validez = barrer(np.zeros((20, 20), dtype=bool))
    assert not validez.any()
    assert np.isnan(centroides).all()
