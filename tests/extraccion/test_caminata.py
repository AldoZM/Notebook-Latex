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


def _errores(par):
    """Error de cada punto de verdad, como fraccion del rango del eje Y."""
    png, verdad = par
    rango_x = (verdad["ejes"]["x"]["min"], verdad["ejes"]["x"]["max"])
    rango_y = (verdad["ejes"]["y"]["min"], verdad["ejes"]["y"]["max"])

    documento, _ = extraer(png, rango_x, rango_y, cuantos=50)
    extraidos = np.array(documento["bloques"][0]["contenido"]["series"][0]["puntos"])
    ciertos = np.array(verdad["puntos"])

    # La curva extraida se evalua en las x de la verdad, que es como compara
    # ctex-medir: los puntos remuestreados no caen en las x de la verdad.
    estimados = np.interp(ciertos[:, 0], extraidos[:, 0], extraidos[:, 1])

    return np.abs(estimados - ciertos[:, 1]) / (rango_y[1] - rango_y[0])


# El criterio de exito de I1 (Seccion 11) tiene DOS partes y las dos se
# comprueban. Con solo la mediana, la suite pasaba en verde mientras 3 de 11
# puntos fallaban con casi 20%: la mediana no ve los valores extremos, que es
# justo lo que el segundo criterio existe para atrapar.


@saltar
def test_el_error_mediano_esta_por_debajo_del_dos_por_ciento(par):
    errores = _errores(par)
    assert np.median(errores) < 0.02, (
        f"error mediano {np.median(errores) * 100:.2f}%, "
        f"peor {errores.max() * 100:.2f}%"
    )


@saltar
def test_ningun_punto_pasa_del_cinco_por_ciento(par):
    errores = _errores(par)
    peores = np.flatnonzero(errores > 0.05)
    assert peores.size == 0, (
        f"{peores.size} de {errores.size} puntos por encima del 5%; "
        f"el peor con {errores.max() * 100:.2f}%"
    )
