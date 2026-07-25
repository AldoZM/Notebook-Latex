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


from ctex.composicion.bloques import componer_ecuacion


def test_una_ecuacion_numerada_usa_el_entorno_equation():
    salida = componer_ecuacion({
        "latex": r"f(x)=\sum_{n=1}^{6} a_n \cos(nx)",
        "numerada": True,
    })
    assert salida == (
        "\\begin{equation}\n"
        r"f(x)=\sum_{n=1}^{6} a_n \cos(nx)"
        "\n\\end{equation}"
    )


def test_una_ecuacion_no_numerada_usa_equation_estrella():
    salida = componer_ecuacion({"latex": "a+b=c", "numerada": False})
    assert salida.startswith(r"\begin{equation*}")
    assert salida.endswith(r"\end{equation*}")


def test_una_ecuacion_sin_el_campo_numerada_se_numera():
    salida = componer_ecuacion({"latex": "a+b=c"})
    assert r"\begin{equation}" in salida


def test_una_ecuacion_con_comando_prohibido_se_degrada():
    # D18: el motor siempre entrega un PDF. Un bloque que no se puede componer
    # se inserta como texto literal, marcado visiblemente.
    salida = componer_ecuacion({"latex": r"\write18{rm -rf /}", "numerada": True})
    assert r"\ctexdegradado" in salida
    assert r"\begin{equation}" not in salida


def test_una_ecuacion_degradada_no_deja_pasar_el_comando():
    salida = componer_ecuacion({"latex": r"\write18{ls}", "numerada": True})
    assert r"\write18" not in salida


def test_una_ecuacion_con_input_se_degrada():
    salida = componer_ecuacion({"latex": r"\input{/etc/passwd}"})
    assert r"\ctexdegradado" in salida
