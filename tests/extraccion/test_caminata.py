# tests/extraccion/test_caminata.py
import json
import shutil

import numpy as np
import pytest

from ctex.contrato.validador import validar
from ctex.extraccion.extractor import extraer
from ctex.material.generador import generar_corpus

faltan_herramientas = shutil.which("tectonic") is None or shutil.which("pdftoppm") is None
saltar = pytest.mark.skipif(
    faltan_herramientas, reason="hacen falta tectonic y pdftoppm"
)


@pytest.fixture(scope="module")
def par(tmp_path_factory):
    """Genera una grafica del nivel -1 y devuelve (png, verdad)."""
    carpeta = tmp_path_factory.mktemp("nivel_menos_1")
    resultados = generar_corpus(cuantas=1, semilla=7, carpeta_salida=carpeta)
    png, ruta_verdad = resultados[0]
    verdad = json.loads(ruta_verdad.read_text(encoding="utf-8"))
    return png, verdad


@saltar
def test_del_nivel_menos_1_sale_un_contrato_valido(par):
    png, verdad = par
    rango_x = (verdad["ejes"]["x"]["min"], verdad["ejes"]["x"]["max"])
    rango_y = (verdad["ejes"]["y"]["min"], verdad["ejes"]["y"]["max"])
    documento, _ = extraer(png, rango_x, rango_y)
    validar(documento)


@saltar
def test_el_error_mediano_esta_por_debajo_del_dos_por_ciento(par):
    png, verdad = par
    rango_x = (verdad["ejes"]["x"]["min"], verdad["ejes"]["x"]["max"])
    rango_y = (verdad["ejes"]["y"]["min"], verdad["ejes"]["y"]["max"])

    documento, _ = extraer(png, rango_x, rango_y, cuantos=50)
    extraidos = np.array(documento["bloques"][0]["contenido"]["series"][0]["puntos"])
    ciertos = np.array(verdad["puntos"])

    # La curva extraida se evalua en las x de la verdad, que es como compara
    # ctex-medir: los puntos remuestreados no caen en las x de la verdad.
    estimados = np.interp(ciertos[:, 0], extraidos[:, 0], extraidos[:, 1])

    rango = rango_y[1] - rango_y[0]
    errores = np.abs(estimados - ciertos[:, 1]) / rango

    assert np.median(errores) < 0.02, (
        f"error mediano {np.median(errores):.4f}, peor {errores.max():.4f}"
    )
