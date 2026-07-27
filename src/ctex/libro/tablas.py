"""Detectar filas alineadas en una pagina, o sea tablas.

La senal es geometrica y no depende de la tipografia, que es justo lo que este
PDF no tiene: su capa de texto es OCR sobre un escaneo, asi que no hay fuentes
que comparar, solo cajas reconstruidas.

Lo que si sobrevive: cuando una fila tiene columnas separadas por un hueco
ancho, pdftotext la parte en varias `line` que comparten banda vertical. El
texto corrido siempre da una sola. Eso distingue una tabla sin adivinar nada
sobre el contenido.
"""

from ctex.libro.paginas import Linea, Pagina

# Cuanto se tienen que solapar verticalmente dos lineas para contar como la
# misma fila, en fraccion de la altura de la mas baja. Con 0.5 basta para
# tolerar el desajuste del OCR sin juntar renglones vecinos.
SOLAPE_MINIMO = 0.5

# Cuantas filas de varias columnas seguidas hacen una tabla.
#
# Con una sola no alcanza: un parrafo cualquiera puede partirse en dos por un
# hueco ancho —una sangria francesa, una formula centrada— y llamarlo tabla
# seria inventar estructura. Dos filas seguidas y alineadas ya no son
# casualidad.
MINIMO_DE_FILAS = 2

# Cuanto puede desviarse el margen izquierdo de una fila para seguir siendo de
# la misma tabla, en puntos.
#
# Existe porque una fila de tabla NO SIEMPRE se parte en varias columnas: si
# sus celdas quedan cerca, pdftotext la deja como una sola linea. Medido en la
# pagina 84, la tabla "Brute Force / Optimal Algorithm / BCR" tiene sus tres
# filas empezando en x=127, pero la de en medio no se partio. Cortar la racha
# ahi perdia la tabla entera.
#
# Lo que distingue a esa fila de un parrafo es que esta alineada con la tabla
# —127 contra los 109 del cuerpo—, no que tenga columnas.
TOLERANCIA_ALINEACION = 5.0


def _se_solapan(a: Linea, b: Linea) -> bool:
    """Si dos lineas comparten banda vertical, son la misma fila visual."""
    inicio = max(a.y0, b.y0)
    fin = min(a.y1, b.y1)
    solape = fin - inicio
    if solape <= 0:
        return False
    return solape >= min(a.alto, b.alto) * SOLAPE_MINIMO


def agrupar_en_filas(lineas: list[Linea]) -> list[list[Linea]]:
    """Junta las lineas que comparten banda vertical, de arriba abajo."""
    filas: list[list[Linea]] = []

    for linea in sorted(lineas, key=lambda l: (l.y0, l.x0)):
        if filas and any(_se_solapan(otra, linea) for otra in filas[-1]):
            filas[-1].append(linea)
        else:
            filas.append([linea])

    for fila in filas:
        fila.sort(key=lambda l: l.x0)

    return filas


# Ancho maximo, en puntos, de una linea de un solo caracter para considerarla
# decoracion y no contenido.
#
# Este libro pone una barra vertical al margen de los recuadros de nota, y el
# OCR la lee como "I". Esa "I" convierte cualquier parrafo de nota en una fila
# de dos columnas, y dos notas seguidas se volvian una tabla. No es una celda:
# es un adorno impreso.
ANCHO_DE_ADORNO = 6.0


def es_adorno(linea: Linea) -> bool:
    """Una raya del margen que el OCR leyo como letra."""
    return len(linea.texto.strip()) <= 1 and (linea.x1 - linea.x0) <= ANCHO_DE_ADORNO


def detectar_tablas(pagina: Pagina, lineas: list[Linea] | None = None) -> list[list[list[Linea]]]:
    """Devuelve las tablas de la pagina, cada una como lista de filas.

    Una tabla es una racha de filas seguidas que traen varias columnas, mas las
    filas alineadas con ellas que no llegaron partidas.

    `lineas` permite pasar solo las del cuerpo. Importa que se filtre ANTES y
    no despues: una racha que empieza en el encabezado y baja al cuerpo no se
    puede descartar mirando el resultado, porque ya mezclo las dos cosas.
    """
    candidatas = pagina.lineas if lineas is None else lineas
    candidatas = [linea for linea in candidatas if not es_adorno(linea)]
    tablas: list[list[list[Linea]]] = []
    racha: list[list[Linea]] = []

    def cerrar() -> None:
        # Solo cuenta como tabla si de verdad vio columnas en algun momento.
        # Sin esto, tres lineas cortas y alineadas —una lista con vinetas, una
        # formula centrada— se volverian una tabla de una columna.
        con_columnas = sum(1 for fila in racha if len(fila) >= 2)
        if len(racha) >= MINIMO_DE_FILAS and con_columnas >= MINIMO_DE_FILAS:
            tablas.append(list(racha))

    for fila in agrupar_en_filas(candidatas):
        if len(fila) >= 2:
            racha.append(fila)
            continue

        # Una fila de una sola columna continua la tabla si esta alineada con
        # ella: es una fila cuyas celdas quedaron demasiado juntas para que
        # pdftotext las separara.
        if racha and abs(fila[0].x0 - racha[0][0].x0) <= TOLERANCIA_ALINEACION:
            racha.append(fila)
            continue

        cerrar()
        racha = []

    cerrar()
    return tablas


def a_filas_de_texto(tabla: list[list[Linea]]) -> list[list[str]]:
    """Convierte una tabla de lineas en filas de celdas de texto.

    Todas las filas se dejan del mismo largo: la composicion rellena o recorta
    de todas formas (D49), pero igualarlas aqui deja el contrato mas honesto
    sobre lo que se vio.
    """
    columnas = max(len(fila) for fila in tabla)
    return [
        [linea.texto for linea in fila] + [""] * (columnas - len(fila))
        for fila in tabla
    ]


def lineas_de(tablas: list[list[list[Linea]]]) -> set[Linea]:
    """Todas las lineas que ya consumio una tabla, para no repetirlas."""
    return {
        linea
        for tabla in tablas
        for fila in tabla
        for linea in fila
    }
