# tests/extraccion/test_extractor.py
import cv2
import numpy as np
import pytest

from ctex.contrato.validador import validar
from ctex.extraccion.extractor import extraer


@pytest.fixture
def recorte(tmp_path):
    """Recuadro con una diagonal dentro, escrito a disco."""
    imagen = np.full((160, 200), 255, dtype=np.uint8)
    imagen[20, 20:180] = 0
    imagen[140, 20:180] = 0
    imagen[20:140, 20] = 0
    imagen[20:140, 180] = 0
    for i in range(100):
        imagen[30 + i, 30 + i] = 0
    ruta = tmp_path / "recorte.png"
    cv2.imwrite(str(ruta), imagen)
    return ruta


def test_el_documento_cumple_el_contrato(recorte):
    documento, _ = extraer(recorte, (0.0, 10.0), (-1.0, 1.0))
    validar(documento)  # no lanza


def test_sale_un_solo_bloque_de_grafica(recorte):
    documento, _ = extraer(recorte, (0.0, 10.0), (-1.0, 1.0))
    assert len(documento["bloques"]) == 1
    assert documento["bloques"][0]["tipo"] == "grafica"


def test_los_rangos_salen_de_los_argumentos_no_de_la_imagen(recorte):
    documento, _ = extraer(recorte, (0.0, 10.0), (-1.0, 1.0))
    ejes = documento["bloques"][0]["contenido"]["ejes"]
    assert ejes["x"]["min"] == 0.0 and ejes["x"]["max"] == 10.0
    assert ejes["y"]["min"] == -1.0 and ejes["y"]["max"] == 1.0


def test_los_textos_van_vacios_porque_la_fase_1_no_lee_etiquetas(recorte):
    contenido = extraer(recorte, (0.0, 10.0), (-1.0, 1.0))[0]["bloques"][0]["contenido"]
    assert contenido["titulo"] == ""
    assert contenido["ejes"]["x"]["etiqueta"] == ""
    assert contenido["ejes"]["y"]["etiqueta"] == ""


def test_la_confianza_es_el_marcador_de_posicion(recorte):
    documento, _ = extraer(recorte, (0.0, 10.0), (-1.0, 1.0))
    assert documento["bloques"][0]["confianza"] == 0.5


def test_la_traza_trae_la_caja_y_la_transformacion(recorte):
    _, traza = extraer(recorte, (0.0, 10.0), (-1.0, 1.0))
    assert traza.caja is not None
    assert traza.transformacion is not None
    assert traza.centroides is not None


def test_una_imagen_que_no_existe_levanta(tmp_path):
    with pytest.raises(FileNotFoundError):
        extraer(tmp_path / "no_existe.png", (0.0, 10.0), (-1.0, 1.0))
