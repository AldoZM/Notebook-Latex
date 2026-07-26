import json
import shutil
import pytest

from ctex.material.definicion import generar_definicion
from ctex.material.generador import generar_corpus

pytestmark = pytest.mark.skipif(
    shutil.which("tectonic") is None or shutil.which("pdftoppm") is None,
    reason="Tectonic o pdftoppm no estan instalados",
)


def test_generar_corpus_crea_cuatro_archivos_para_dos_graficas(tmp_path):
    salida = tmp_path / "corpus"
    pares = generar_corpus(cuantas=2, semilla=42, carpeta_salida=salida)

    assert len(pares) == 2

    # Deben existir 000.png, 000.verdad.json, 001.png, 001.verdad.json
    f000_png = salida / "000.png"
    f000_json = salida / "000.verdad.json"
    f001_png = salida / "001.png"
    f001_json = salida / "001.verdad.json"

    assert f000_png.exists()
    assert f000_json.exists()
    assert f001_png.exists()
    assert f001_json.exists()


def test_puntos_de_verdad_json_son_identicos_a_los_de_la_definicion(tmp_path):
    salida = tmp_path / "corpus_verdad"
    semilla = 100
    generar_corpus(cuantas=1, semilla=semilla, carpeta_salida=salida)

    f_json = salida / "000.verdad.json"
    data = json.loads(f_json.read_text(encoding="utf-8"))

    def_original = generar_definicion(familia=data["familia"], semilla=data["semilla"])

    assert data["puntos"] == def_original["series"][0]["puntos"]
    assert data["ejes"]["x"] == def_original["ejes"]["x"]
    assert data["ejes"]["y"] == def_original["ejes"]["y"]
    assert data["semilla"] == semilla


def test_png_generado_es_recorte_y_no_pagina_carta(tmp_path):
    import struct

    salida = tmp_path / "corpus_recorte"
    generar_corpus(cuantas=1, semilla=42, carpeta_salida=salida)

    png_path = salida / "000.png"
    bytes_png = png_path.read_bytes()

    assert bytes_png[:8] == b"\x89PNG\r\n\x1a\n"
    assert bytes_png[12:16] == b"IHDR"
    ancho, alto = struct.unpack(">II", bytes_png[16:24])

    # Una pagina carta a 200 ppp es de 1700 x 2200 = 3,740,000 pixeles.
    # El recorte standalone debe ser sustancialmente mas chico (< 1.5M pixeles)
    # y su relacion de aspecto ya no es la de una hoja carta (1700/2200 ~ 0.7727).
    total_pixeles = ancho * alto
    assert total_pixeles < 1_500_000
    assert (ancho / alto) != pytest.approx(1700 / 2200, rel=1e-2)
