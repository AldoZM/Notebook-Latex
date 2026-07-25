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


from ctex.composicion.bloques import componer_grafica

GRAFICA_EJEMPLO = {
    "tipo_grafica": "lineas",
    "titulo": "Convergencia",
    "ejes": {
        "x": {"min": 0, "max": 10, "etiqueta": "n", "escala": "lineal"},
        "y": {"min": -1, "max": 1, "etiqueta": "error", "escala": "lineal"},
    },
    "series": [
        {"etiqueta": "parcial", "puntos": [[0, 0.9], [2, 0.42], [4, 0.21], [6, 0.1]]}
    ],
}


def test_una_grafica_produce_un_entorno_axis():
    salida = componer_grafica(GRAFICA_EJEMPLO)
    assert r"\begin{tikzpicture}" in salida
    assert r"\begin{axis}" in salida
    assert r"\end{tikzpicture}" in salida


def test_los_limites_de_los_ejes_salen_del_contrato():
    salida = componer_grafica(GRAFICA_EJEMPLO)
    assert "xmin=0" in salida
    assert "xmax=10" in salida
    assert "ymin=-1" in salida
    assert "ymax=1" in salida


def test_los_puntos_salen_como_coordenadas():
    salida = componer_grafica(GRAFICA_EJEMPLO)
    assert "(0,0.9)" in salida
    assert "(6,0.1)" in salida


def test_la_grafica_no_contiene_ninguna_imagen_incrustada():
    # D10: matplotlib no aparece en la ruta de salida. Lo que sale son numeros.
    salida = componer_grafica(GRAFICA_EJEMPLO)
    assert r"\includegraphics" not in salida


def test_una_escala_logaritmica_se_traduce():
    contenido = {
        **GRAFICA_EJEMPLO,
        "ejes": {
            "x": {"min": 1, "max": 100, "etiqueta": "n", "escala": "log"},
            "y": {"min": -1, "max": 1, "etiqueta": "error", "escala": "lineal"},
        },
    }
    salida = componer_grafica(contenido)
    assert "xmode=log" in salida


def test_las_etiquetas_van_escapadas():
    contenido = {
        **GRAFICA_EJEMPLO,
        "titulo": "Costos & margenes",
        "ejes": {
            "x": {"min": 0, "max": 10, "etiqueta": "100%", "escala": "lineal"},
            "y": {"min": -1, "max": 1, "etiqueta": "error", "escala": "lineal"},
        },
    }
    salida = componer_grafica(contenido)
    assert r"Costos \& margenes" in salida
    assert r"100\%" in salida


def test_varias_series_producen_varios_addplot():
    contenido = {
        **GRAFICA_EJEMPLO,
        "series": [
            {"etiqueta": "a", "puntos": [[0, 1], [1, 2]]},
            {"etiqueta": "b", "puntos": [[0, 3], [1, 4]]},
        ],
    }
    salida = componer_grafica(contenido)
    assert salida.count(r"\addplot") == 2
