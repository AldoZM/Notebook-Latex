# tests/extraccion/test_cli.py
import json

import cv2
import numpy as np
import pytest

from ctex.extraccion.cli import main


@pytest.fixture
def recorte(tmp_path):
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


def test_escribe_el_json_y_sale_con_cero(recorte, tmp_path):
    salida = tmp_path / "hoja.json"
    codigo = main([
        str(recorte), "--escala-x", "0,10", "--escala-y", "-1,1",
        "--salida", str(salida),
    ])
    assert codigo == 0
    assert salida.exists()
    documento = json.loads(salida.read_text(encoding="utf-8"))
    assert documento["version_contrato"] == "1.0"


def test_un_rango_invertido_sale_con_dos(recorte, tmp_path):
    codigo = main([
        str(recorte), "--escala-x", "10,0", "--escala-y", "-1,1",
        "--salida", str(tmp_path / "hoja.json"),
    ])
    assert codigo == 2


def test_una_imagen_sin_marco_sale_con_tres(tmp_path):
    blanca = tmp_path / "blanca.png"
    cv2.imwrite(str(blanca), np.full((160, 200), 255, dtype=np.uint8))
    codigo = main([
        str(blanca), "--escala-x", "0,10", "--escala-y", "-1,1",
        "--salida", str(tmp_path / "hoja.json"),
    ])
    assert codigo == 3


def test_la_traza_se_escribe_si_se_pide(recorte, tmp_path):
    traza = tmp_path / "traza.json"
    main([
        str(recorte), "--escala-x", "0,10", "--escala-y", "-1,1",
        "--salida", str(tmp_path / "hoja.json"), "--traza", str(traza),
    ])
    assert traza.exists()
    contenido = json.loads(traza.read_text(encoding="utf-8"))
    assert "caja" in contenido
