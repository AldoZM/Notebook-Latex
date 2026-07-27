import pytest

from ctex.libro.estructura import (
    _unir,
    altura_del_cuerpo,
    clasificar,
    es_corrido,
    es_titulo,
    margen_del_cuerpo,
)
from ctex.libro.paginas import Bloque, Linea, Pagina

# Las medidas son las reales de CtCI, para que las pruebas fallen si alguien
# cambia un umbral sin mirar de donde salio: cuerpo 12.06, titulo 10.82,
# margen izquierdo 109, pagina de 710 puntos de alto.
CUERPO = 12.06
TITULO = 10.82
MARGEN = 109.2


def linea(texto, y0, alto=CUERPO, x0=MARGEN):
    return Linea(texto=texto, x0=x0, y0=y0, x1=x0 + 400, y1=y0 + alto)


def pagina_de(*bloques):
    return Pagina(numero=1, ancho=607.2, alto=709.92, bloques=list(bloques))


def test_lo_que_esta_arriba_del_todo_es_corrido():
    encabezado = Bloque([linea("IV I Before the Interview", 12.4, alto=15.9)])
    assert es_corrido(encabezado, pagina_de(encabezado))


def test_lo_que_esta_abajo_del_todo_es_corrido():
    pie = Bloque([linea("CrackingTheCodingInterview.com", 690.0)])
    assert es_corrido(pie, pagina_de(pie))


def test_el_cuerpo_no_es_corrido():
    cuerpo = Bloque([linea("Additionally, for US positions", 46.4)])
    assert not es_corrido(cuerpo, pagina_de(cuerpo))


def test_el_encabezado_no_llega_al_documento():
    encabezado = Bloque([linea("IV I Before the Interview", 12.4, alto=15.9)])
    cuerpo = Bloque([linea("Additionally, for US positions", 46.4)])
    partes = clasificar([pagina_de(encabezado, cuerpo)])
    assert len(partes) == 1
    assert "Before the Interview" not in partes[0].texto


def test_un_titulo_en_otra_tipografia_se_reconoce_aunque_sea_mas_bajo():
    # El caso real que rompio la primera version: el titulo mide MENOS que el
    # cuerpo porque va en una sans en negrita.
    cuerpo1 = Bloque([linea("Additionally, for US positions", 46.4)])
    titulo = Bloque([linea("Beware of (Potential) Stigma", 80.0, alto=TITULO)])
    cuerpo2 = Bloque([linea("Certain languages have stigmas", 100.0)])

    partes = clasificar([pagina_de(cuerpo1, titulo, cuerpo2)])
    tipos = [p.tipo for p in partes]
    assert tipos == ["parrafo", "titulo", "parrafo"]


def test_una_linea_suelta_en_la_letra_del_cuerpo_no_es_titulo():
    cuerpo1 = Bloque([linea("Additionally, for US positions", 46.4)])
    suelta = Bloque([linea("A few stigmas you should be aware of:", 80.0)])
    cuerpo2 = Bloque([linea("Certain languages have stigmas", 100.0)])

    partes = clasificar([pagina_de(cuerpo1, suelta, cuerpo2)])
    assert [p.tipo for p in partes] == ["parrafo", "parrafo", "parrafo"]


def test_lo_que_flota_lejos_del_margen_no_es_titulo():
    # Una etiqueta suelta en medio de un diagrama de flujo.
    cuerpo = Bloque([linea("Additionally, for US positions", 46.4)])
    flotante = Bloque([linea("Expand Network.", 300.0, alto=11.31, x0=398.6)])

    partes = clasificar([pagina_de(cuerpo, flotante)])
    assert [p.tipo for p in partes] == ["parrafo", "parrafo"]


# Las tres condiciones de es_titulo se prueban sobre el predicado y no sobre
# clasificar(), porque clasificar() calcula la mediana a partir de los bloques
# que se le den: en un montaje de tres bloques, la mediana la puede ganar el
# bloque de prueba y la clasificacion se invierte. Eso es correcto en la
# tubería y ruido en una prueba de una sola propiedad.


def test_un_bloque_de_varias_lineas_nunca_es_titulo():
    largo = Bloque([
        linea("Certain languages have stigmas", 80.0, alto=TITULO),
        linea("associated with them.", 95.0, alto=TITULO),
    ])
    assert not es_titulo(largo, "Certain languages have stigmas associated",
                         CUERPO, MARGEN)


def test_una_linea_en_otra_tipografia_y_en_el_margen_si_es_titulo():
    corto = Bloque([linea("Beware of (Potential) Stigma", 80.0, alto=TITULO)])
    assert es_titulo(corto, "Beware of (Potential) Stigma", CUERPO, MARGEN)


def test_un_texto_largo_no_es_titulo_aunque_cambie_de_letra():
    largo = "Beware of the potential stigma that certain programming languages carry with them"
    bloque = Bloque([linea(largo, 80.0, alto=TITULO)])
    assert not es_titulo(bloque, largo, CUERPO, MARGEN)


def test_la_division_silabica_del_pdf_se_deshace():
    bloque = Bloque([
        linea("This sort of personal informa-", 46.4),
        linea("tion is not appreciated", 60.0),
    ])
    assert _unir(bloque) == "This sort of personal information is not appreciated"


def test_las_lineas_de_un_parrafo_se_unen_con_espacio():
    bloque = Bloque([
        linea("Certain languages have", 46.4),
        linea("stigmas associated", 60.0),
    ])
    assert _unir(bloque) == "Certain languages have stigmas associated"


def test_la_altura_del_cuerpo_ignora_los_encabezados():
    # Si el encabezado contara, su letra grande subiria la mediana y el titulo
    # dejaria de destacar contra ella.
    encabezado = Bloque([linea("IV I Before the Interview", 12.4, alto=40.0)])
    cuerpo = Bloque([linea("Additionally, for US positions", 46.4)])
    assert altura_del_cuerpo([pagina_de(encabezado, cuerpo)]) == pytest.approx(CUERPO)


def test_el_margen_sale_del_cuerpo():
    cuerpo = Bloque([linea("Additionally, for US positions", 46.4)])
    assert margen_del_cuerpo([pagina_de(cuerpo)]) == pytest.approx(MARGEN)


def test_una_pagina_de_diagrama_no_arrastra_el_margen_de_otra():
    # El fallo que se descubrio al procesar cinco paginas en vez de una: las
    # paginas 41 y 42 de CtCI son diagramas de flujo con cajas repartidas por
    # todo el ancho, margenes de 250 y 277. Con la mediana global, el titulo de
    # la pagina 40 quedaba a 42 puntos de "su" margen y se perdia.
    #
    # Sintoma peligroso: procesar MAS paginas empeoraba el resultado.
    texto = pagina_de(
        Bloque([linea("Additionally, for US positions", 46.4)]),
        Bloque([linea("Beware of (Potential) Stigma", 80.0, alto=TITULO)]),
        Bloque([linea("Certain languages have stigmas", 100.0)]),
    )
    diagrama = pagina_de(
        Bloque([linea("Expand Network.", 300.0, x0=398.6)]),
        Bloque([linea("Build projects.", 320.0, x0=250.9)]),
        Bloque([linea("Learn Big O.", 340.0, x0=277.3)]),
    )

    solo = [p.tipo for p in clasificar([texto])]
    con_diagrama = [p.tipo for p in clasificar([texto, diagrama])]

    assert solo[:3] == ["parrafo", "titulo", "parrafo"]
    assert con_diagrama[:3] == solo[:3], (
        "agregar una pagina de diagrama no debe cambiar como se clasifica otra"
    )


def test_una_pagina_sin_cuerpo_no_revienta():
    solo_encabezado = Bloque([linea("IV I Before the Interview", 12.4)])
    assert clasificar([pagina_de(solo_encabezado)]) == []
