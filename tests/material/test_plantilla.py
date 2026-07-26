import pytest

from ctex.composicion.bloques import componer_grafica
from ctex.material.contrato import definicion_a_contrato
from ctex.material.definicion import generar_definicion
from ctex.material.plantilla import (
    ErrorDeExtraccionTikz,
    envolver_standalone,
    extraer_tikzpicture,
)


def test_extraer_tikzpicture_exito():
    fragmento = (
        "\\begin{figure}[htbp]\n"
        "  \\centering\n"
        "  \\begin{tikzpicture}\n"
        "    \\begin{axis}\n"
        "    \\addplot coordinates {(0,1) (1,2)};\n"
        "    \\end{axis}\n"
        "  \\end{tikzpicture}\n"
        "  \\caption{Mi Grafica}\n"
        "\\end{figure}"
    )
    tikz = extraer_tikzpicture(fragmento)
    assert tikz.startswith("\\begin{tikzpicture}")
    assert tikz.endswith("\\end{tikzpicture}")
    assert "\\addplot coordinates" in tikz
    assert "\\caption" not in tikz


def test_extraer_tikzpicture_error_si_falta():
    with pytest.raises(ErrorDeExtraccionTikz) as exc_info:
        extraer_tikzpicture("texto sin tikz")

    assert "No se encontro" in str(exc_info.value)


def test_envolver_standalone():
    tikz = "\\begin{tikzpicture}\\end{tikzpicture}"
    doc = envolver_standalone(tikz)

    assert r"\documentclass[border=2mm]{standalone}" in doc
    assert r"\usepackage{pgfplots}" in doc
    assert r"\begin{document}" in doc
    assert tikz in doc
    assert r"\end{document}" in doc


def test_tikzpicture_extraido_contiene_los_mismos_puntos_que_definicion():
    definicion = generar_definicion(familia="lineal", semilla=42)
    doc_contrato = definicion_a_contrato(definicion)
    bloque = doc_contrato["bloques"][0]["contenido"]

    fragmento = componer_grafica(bloque)
    tikz = extraer_tikzpicture(fragmento)

    puntos = definicion["series"][0]["puntos"]
    for x, y in puntos:
        # Los puntos en tikz se formatean como (x,y)
        # por ejemplo (0,0) o (1.5,2.3)
        str_x = str(int(x)) if isinstance(x, int) or float(x).is_integer() else f"{x:g}"
        str_y = str(int(y)) if isinstance(y, int) or float(y).is_integer() else f"{y:g}"
        coord = f"({str_x},{str_y})"
        assert coord in tikz
