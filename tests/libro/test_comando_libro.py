import argparse
import shutil

import pytest

from ctex.libro.cli import _rango, main

sin_pdftotext = pytest.mark.skipif(
    shutil.which("pdftotext") is None, reason="hace falta pdftotext"
)


def test_una_pagina_sola_es_un_rango_de_una():
    assert _rango("40") == (40, 40)


def test_un_rango_se_lee_con_guion():
    assert _rango("40-44") == (40, 44)


def test_un_rango_invertido_se_rechaza():
    with pytest.raises(argparse.ArgumentTypeError):
        _rango("44-40")


def test_un_rango_que_no_es_numero_se_rechaza():
    with pytest.raises(argparse.ArgumentTypeError):
        _rango("cuarenta")


@sin_pdftotext
def test_un_pdf_que_no_existe_sale_con_dos(tmp_path):
    codigo = main([
        str(tmp_path / "no_existe.pdf"),
        "--paginas", "1",
        "--salida", str(tmp_path / "hoja.json"),
    ])
    assert codigo == 2


@sin_pdftotext
def test_un_archivo_que_no_es_pdf_sale_con_tres(tmp_path):
    falso = tmp_path / "falso.pdf"
    falso.write_text("esto no es un PDF", encoding="utf-8")
    codigo = main([
        str(falso),
        "--paginas", "1",
        "--salida", str(tmp_path / "hoja.json"),
    ])
    assert codigo == 3
