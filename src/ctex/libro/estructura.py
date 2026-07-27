"""Decidir que es cada bloque: encabezado corrido, titulo o parrafo.

Todo se decide con dos senales medibles —donde esta y que tan alta es su
letra—, nunca adivinando por el contenido del texto. Un "if empieza con
mayuscula" acierta a veces y falla en silencio; la geometria no.
"""

import re
import statistics
from dataclasses import dataclass

from ctex.libro.paginas import Bloque, Pagina

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

    tipo: str  # "titulo" o "parrafo"
    texto: str
    nivel: int = 2


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
    """Donde empieza el texto corrido, en puntos desde el borde izquierdo."""
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
    """Convierte las paginas en una lista de titulos y parrafos."""
    cuerpo = altura_del_cuerpo(paginas)
    margen = margen_del_cuerpo(paginas)
    partes: list[Parte] = []

    for pagina in paginas:
        for bloque in pagina.bloques:
            if es_corrido(bloque, pagina):
                # Encabezado, pie o numero de pagina: no son del documento,
                # son del libro impreso. Se descartan.
                continue

            texto = _unir(bloque)
            if not texto:
                continue

            partes.append(
                Parte(tipo="titulo", texto=texto, nivel=2)
                if es_titulo(bloque, texto, cuerpo, margen)
                else Parte(tipo="parrafo", texto=texto)
            )

    return partes
