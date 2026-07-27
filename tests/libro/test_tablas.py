"""Deteccion de filas alineadas.

Las medidas son las reales de la pagina 84 de CtCI, donde se descubrio cada
caso: cuerpo en x=109 con alto 12.06, tabla en x=127, adorno de nota en x=108
con ancho de 2 puntos.
"""

from ctex.libro.paginas import Bloque, Linea, Pagina
from ctex.libro.tablas import (
    a_filas_de_texto,
    agrupar_en_filas,
    detectar_tablas,
    es_adorno,
    lineas_de,
)

CUERPO = 12.06
X_CUERPO = 109.0
X_TABLA = 127.4


def linea(texto, y0, x0=X_TABLA, ancho=55.0):
    return Linea(texto=texto, x0=x0, y0=y0, x1=x0 + ancho, y1=y0 + CUERPO)


def pagina_con(*lineas):
    return Pagina(numero=1, ancho=607.2, alto=709.92, bloques=[Bloque(list(lineas))])


# ------------------------------------------------------- agrupar en filas


def test_dos_lineas_a_la_misma_altura_son_una_fila():
    filas = agrupar_en_filas([
        linea("Brute Force:", 357.07),
        linea("O(N2)", 357.05, x0=219.6),
    ])
    assert len(filas) == 1
    assert len(filas[0]) == 2


def test_las_columnas_salen_ordenadas_de_izquierda_a_derecha():
    filas = agrupar_en_filas([
        linea("O(N2)", 357.05, x0=219.6),
        linea("Brute Force:", 357.07),
    ])
    assert [l.texto for l in filas[0]] == ["Brute Force:", "O(N2)"]


def test_dos_renglones_distintos_no_se_juntan():
    filas = agrupar_en_filas([
        linea("Brute Force:", 357.07),
        linea("BCR:", 378.29),
    ])
    assert len(filas) == 2


# ------------------------------------------------------------ las tablas


def test_dos_filas_de_dos_columnas_son_una_tabla():
    pagina = pagina_con(
        linea("Brute Force:", 357.07), linea("O(N2)", 357.05, x0=219.6),
        linea("BCR:", 378.29), linea("O(N)", 378.29, x0=219.6),
    )
    tablas = detectar_tablas(pagina)
    assert len(tablas) == 1
    assert len(tablas[0]) == 2


def test_una_sola_fila_de_dos_columnas_no_es_una_tabla():
    # Un parrafo puede partirse en dos por un hueco ancho. Una vez es
    # casualidad; dos seguidas ya no.
    pagina = pagina_con(
        linea("algo", 357.07), linea("otra cosa", 357.05, x0=219.6),
        linea("texto corrido normal", 378.29, x0=X_CUERPO, ancho=400),
    )
    assert detectar_tablas(pagina) == []


def test_una_fila_de_una_columna_alineada_continua_la_tabla():
    # El caso real de la pagina 84: "Optimal Algorithm: ?" no se partio porque
    # sus dos celdas quedaron cerca, y cortaba la tabla en dos.
    pagina = pagina_con(
        linea("Brute Force:", 357.07), linea("O(N2)", 357.05, x0=219.6),
        linea("Optimal Algorithm: ?", 367.84),
        linea("BCR:", 378.29), linea("O(N)", 378.29, x0=219.6),
    )
    tablas = detectar_tablas(pagina)
    assert len(tablas) == 1
    assert len(tablas[0]) == 3


def test_una_fila_de_una_columna_desalineada_corta_la_tabla():
    pagina = pagina_con(
        linea("Brute Force:", 357.07), linea("O(N2)", 357.05, x0=219.6),
        linea("BCR:", 367.84), linea("O(N)", 367.84, x0=219.6),
        linea("Un parrafo del cuerpo", 378.29, x0=X_CUERPO, ancho=400),
        linea("Otro parrafo", 390.0, x0=X_CUERPO, ancho=400),
    )
    tablas = detectar_tablas(pagina)
    assert len(tablas) == 1
    assert len(tablas[0]) == 2


def test_varias_lineas_alineadas_sin_columnas_no_son_tabla():
    # Una lista con vinetas o una formula centrada: alineadas, pero sin
    # columnas. No hay estructura que recuperar.
    pagina = pagina_con(
        linea("primera", 357.07),
        linea("segunda", 367.84),
        linea("tercera", 378.29),
    )
    assert detectar_tablas(pagina) == []


def test_las_filas_se_igualan_a_lo_ancho():
    tabla = [
        [linea("Brute Force:", 357.07), linea("O(N2)", 357.05, x0=219.6)],
        [linea("Optimal Algorithm: ?", 367.84)],
    ]
    assert a_filas_de_texto(tabla) == [
        ["Brute Force:", "O(N2)"],
        ["Optimal Algorithm: ?", ""],
    ]


def test_lineas_de_devuelve_todas_las_consumidas():
    pagina = pagina_con(
        linea("Brute Force:", 357.07), linea("O(N2)", 357.05, x0=219.6),
        linea("BCR:", 378.29), linea("O(N)", 378.29, x0=219.6),
    )
    assert len(lineas_de(detectar_tablas(pagina))) == 4


# ------------------------------------------------------------ el adorno


def test_una_raya_del_margen_es_adorno():
    # Este libro pone una barra vertical al lado de los recuadros de nota y el
    # OCR la lee como "I". Sin filtrarla, dos notas seguidas parecen una tabla
    # y cada raya suelta parece un titulo.
    assert es_adorno(Linea(texto="I", x0=108.0, y0=40.0, x1=110.0, y1=52.0))


def test_una_celda_corta_de_verdad_no_es_adorno():
    assert not es_adorno(Linea(texto="?", x0=127.0, y0=40.0, x1=140.0, y1=52.0))


def test_el_adorno_no_forma_columnas():
    pagina = pagina_con(
        Linea(texto="I", x0=108.0, y0=40.0, x1=110.0, y1=52.0),
        linea("Un parrafo de nota", 40.0, x0=136.0, ancho=380),
        Linea(texto="I", x0=108.0, y0=60.0, x1=110.0, y1=72.0),
        linea("Otro parrafo de nota", 60.0, x0=136.0, ancho=380),
    )
    assert detectar_tablas(pagina) == []
