from ctex.composicion.bloques import componer_parrafo, componer_titulo
from ctex.composicion.plantilla import envolver


def test_un_titulo_de_nivel_1_es_una_section():
    salida = componer_titulo({"nivel": 1, "texto": "Series de Fourier"})
    assert salida == r"\section{Series de Fourier}"


def test_un_titulo_de_nivel_2_es_una_subsection():
    salida = componer_titulo({"nivel": 2, "texto": "Convergencia"})
    assert salida == r"\subsection{Convergencia}"


def test_un_titulo_de_nivel_absurdo_cae_en_el_mas_profundo():
    salida = componer_titulo({"nivel": 99, "texto": "Hondo"})
    assert salida == r"\subsubsection{Hondo}"


def test_el_texto_del_titulo_va_escapado():
    salida = componer_titulo({"nivel": 1, "texto": "Costos & margenes 100%"})
    assert salida == r"\section{Costos \& margenes 100\%}"


def test_un_parrafo_es_texto_escapado():
    salida = componer_parrafo({"texto": "La suma converge."})
    assert salida == "La suma converge."


def test_el_texto_del_parrafo_va_escapado():
    salida = componer_parrafo({"texto": r"Ejecuta \write18{ls} ahora"})
    assert r"\write18" not in salida


def test_envolver_produce_un_documento_completo():
    salida = envolver(r"\section{Hola}")
    assert salida.startswith(r"\documentclass")
    assert r"\begin{document}" in salida
    assert r"\section{Hola}" in salida
    assert salida.rstrip().endswith(r"\end{document}")


def test_el_preambulo_carga_pgfplots():
    salida = envolver("")
    assert r"\usepackage{pgfplots}" in salida
