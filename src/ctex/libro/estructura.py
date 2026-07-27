"""Decidir que es cada bloque: encabezado corrido, titulo o parrafo.

Todo se decide con dos senales medibles —donde esta y que tan alta es su
letra—, nunca adivinando por el contenido del texto. Un "if empieza con
mayuscula" acierta a veces y falla en silencio; la geometria no.
"""

import re
import statistics
from dataclasses import dataclass

from ctex.libro.paginas import Bloque, Pagina
from ctex.libro.tablas import (
    a_filas_de_texto,
    detectar_tablas,
    es_adorno,
    lineas_de,
)

# Fraccion de la pagina, arriba y abajo, donde vive lo corrido: encabezado,
# pie y folio.
#
# Medido en CtCI: el centro del encabezado cae al 2.9% y el cuerpo empieza al
# 6.5%, asi que el umbral tiene que ir entre esos dos. Estuvo en 8% y era un
# error latente: con el PDF real funcionaba de casualidad, porque el primer
# bloque del cuerpo tiene varias lineas y su centro queda por debajo del 8%.
# Un parrafo de UNA linea al principio de la pagina se habria borrado sin que
# nadie lo notara. Lo cazo una prueba, no el ojo.
MARGEN = 0.05

# Cuanto se tiene que apartar la altura de linea de la del cuerpo para que el
# bloque cuente como escrito en OTRA tipografia.
#
# La primera version buscaba letra MAS ALTA, y estaba mal. Medido en CtCI, el
# titulo "Beware of (Potential) Stigma" mide 10.82 y el cuerpo 12.06: el titulo
# es mas BAJO, porque va en una sans en negrita cuya caja de glifos es mas
# corta. Lo que distingue a un titulo no es el tamano, es ser de otra
# tipografia. Por eso la comparacion es en valor absoluto.
#
# El cuerpo es 12.06 en todos los parrafos, asi que la separacion real es
# limpia: 10.3% para el titulo contra 2.5% para la variacion normal del cuerpo.
DESVIACION_TITULO = 0.05

# Un titulo es corto. Por encima de esto es un parrafo aunque cambie de letra.
MAXIMO_DE_UN_TITULO = 80

# Cuanto puede alejarse un titulo del margen izquierdo del cuerpo, en puntos.
# Un titulo empieza donde empieza el texto; lo que flota en medio de la pagina
# es una etiqueta de figura o de diagrama, no un titulo.
TOLERANCIA_MARGEN = 20.0


@dataclass(frozen=True)
class Parte:
    """Un trozo del documento, ya clasificado."""

    tipo: str  # "titulo", "parrafo" o "tabla"
    texto: str = ""
    nivel: int = 2
    # Solo para las tablas. Tupla y no lista para que Parte siga siendo
    # inmutable y comparable, que es lo que hace faciles las pruebas.
    filas: tuple[tuple[str, ...], ...] = ()


def _unir(bloque: Bloque) -> str:
    """Junta las lineas del bloque en un solo texto, deshaciendo la division.

    El PDF corta palabras al final del renglon con guion o con guion suave.
    Unir sin deshacerlo deja "informa- tion" en medio de la frase.
    """
    partes: list[str] = []
    for linea in bloque.lineas:
        texto = linea.texto
        if texto.endswith(("-", "­")):
            partes.append(texto[:-1])
        else:
            partes.append(texto + " ")
    return re.sub(r"\s+", " ", "".join(partes)).strip()


def es_corrido(bloque: Bloque, pagina: Pagina) -> bool:
    """Encabezado, pie o folio: lo que se repite en todas las paginas."""
    limite_arriba = pagina.alto * MARGEN
    limite_abajo = pagina.alto * (1 - MARGEN)
    centro = (bloque.y0 + bloque.y1) / 2
    return centro < limite_arriba or centro > limite_abajo


def altura_del_cuerpo(paginas: list[Pagina]) -> float:
    """Altura tipica de la letra del cuerpo, en puntos.

    Se mide sobre TODAS las paginas y no sobre una: una pagina que empiece con
    un titulo grande subiria su propia mediana y el titulo dejaria de destacar
    contra ella.
    """
    alturas = [
        linea.alto
        for pagina in paginas
        for bloque in pagina.bloques
        if not es_corrido(bloque, pagina)
        for linea in bloque.lineas
        if linea.alto > 0
    ]
    if not alturas:
        return 0.0
    return statistics.median(alturas)


def margen_del_cuerpo(paginas: list[Pagina]) -> float:
    """Donde empieza el texto corrido, en puntos desde el borde izquierdo.

    OJO: esto se mide POR PAGINA, al reves que `altura_del_cuerpo`. No es una
    inconsistencia, es que las dos cosas viven en escalas distintas:

        la tipografia es del LIBRO      -> se mide sobre todas las paginas
        el margen es de la PAGINA       -> se mide sobre una

    Medido en CtCI: la pagina 40 es texto corrido y su margen es 110.9; las
    paginas 41 y 42 son diagramas de flujo con cajas repartidas por todo el
    ancho, y sus margenes son 250.3 y 277.3. Juntando las cinco, la mediana se
    va a 150.2 y el titulo real de la pagina 40 —que empieza en 108.2— queda a
    42 puntos de un margen que no es el suyo.

    El sintoma era el peor posible: procesar MAS paginas empeoraba el
    resultado. Con la pagina 40 sola el titulo se detectaba; con las cinco, se
    perdia.
    """
    margenes = [
        bloque.x0
        for pagina in paginas
        for bloque in pagina.bloques
        if not es_corrido(bloque, pagina)
    ]
    if not margenes:
        return 0.0
    return statistics.median(margenes)


def es_titulo(bloque: Bloque, texto: str, cuerpo: float, margen: float) -> bool:
    """Tres condiciones geometricas, ninguna sobre el contenido del texto.

    1. Una sola linea. Un titulo que ocupa dos renglones existe, pero en un
       libro es raro y confundirlo con un parrafo cuesta menos que lo contrario.
    2. Otra tipografia que el cuerpo, medida por la altura de linea.
    3. Empieza donde empieza el texto. Lo que flota en medio de la pagina es
       una etiqueta de figura, no un titulo.
    """
    if cuerpo <= 0 or len(bloque.lineas) != 1:
        return False
    if len(texto) > MAXIMO_DE_UN_TITULO:
        return False

    alto = bloque.lineas[0].alto
    otra_letra = abs(alto - cuerpo) / cuerpo > DESVIACION_TITULO
    en_el_margen = abs(bloque.x0 - margen) <= TOLERANCIA_MARGEN

    return otra_letra and en_el_margen


def clasificar(paginas: list[Pagina]) -> list[Parte]:
    """Convierte las paginas en una lista de titulos, parrafos y tablas."""
    # La tipografia es del libro y se mide sobre todo el rango; el margen es de
    # cada pagina y se mide dentro del bucle. Ver `margen_del_cuerpo`.
    cuerpo = altura_del_cuerpo(paginas)
    partes: list[Parte] = []

    for pagina in paginas:
        margen = margen_del_cuerpo([pagina])
        # Las tablas se buscan a nivel de LINEA y no de bloque, porque
        # pdftotext mete las filas alineadas dentro del bloque del parrafo
        # anterior. Confiar en su agrupacion aqui perderia la tabla entera.
        #
        # Y se les pasan solo las lineas del cuerpo. Filtrar despues no sirve:
        # una racha que empieza en el encabezado y baja al cuerpo ya mezclo las
        # dos cosas y no hay como separarlas mirando el resultado.
        # Los adornos se quitan aqui y no solo en la deteccion de tablas: una
        # raya del margen que el OCR leyo como "I" forma su propio bloque de una
        # linea, y como su caja no mide como la del cuerpo, se clasificaba como
        # titulo. Salian secciones fantasma llamadas "I".
        del_cuerpo = [
            linea
            for bloque in pagina.bloques
            if not es_corrido(bloque, pagina)
            for linea in bloque.lineas
            if not es_adorno(linea)
        ]
        tablas = detectar_tablas(pagina, del_cuerpo)
        consumidas = lineas_de(tablas)

        # Se acumula con la `y` de cada parte para devolverlas en el orden en
        # que aparecen en la pagina: las tablas se detectan aparte de los
        # bloques y sin esto saldrian todas juntas al final.
        ubicadas: list[tuple[float, Parte]] = []

        for tabla in tablas:
            ubicadas.append((
                tabla[0][0].y0,
                Parte(
                    tipo="tabla",
                    filas=tuple(tuple(fila) for fila in a_filas_de_texto(tabla)),
                ),
            ))

        for bloque in pagina.bloques:
            if es_corrido(bloque, pagina):
                # Encabezado, pie o numero de pagina: no son del documento,
                # son del libro impreso. Se descartan.
                continue

            # Lo que ya se llevo una tabla no vuelve a salir como parrafo, y
            # los adornos no salen nunca.
            restantes = [
                l for l in bloque.lineas
                if l not in consumidas and not es_adorno(l)
            ]
            if not restantes:
                continue
            limpio = Bloque(restantes)

            texto = _unir(limpio)
            if not texto:
                continue

            ubicadas.append((
                limpio.y0,
                Parte(tipo="titulo", texto=texto, nivel=2)
                if es_titulo(limpio, texto, cuerpo, margen)
                else Parte(tipo="parrafo", texto=texto),
            ))

        partes.extend(parte for _, parte in sorted(ubicadas, key=lambda par: par[0]))

    return partes
