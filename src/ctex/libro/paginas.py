"""Leer un PDF conservando la posicion y el tamano de cada linea.

`pdftotext` a secas devuelve texto plano y tira la geometria, y con ella se va
la unica senal que distingue un encabezado corrido de un parrafo: que el
encabezado esta en el margen y su tipografia es mas alta. Con `-bbox-layout`
esa geometria se conserva.
"""

import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

# pdftotext emite XHTML, asi que todo viene con este espacio de nombres.
XHTML = "{http://www.w3.org/1999/xhtml}"


class ErrorDeLectura(Exception):
    """No se pudo leer el PDF o no trae capa de texto."""


@dataclass(frozen=True)
class Linea:
    """Una linea de texto con su caja."""

    texto: str
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def alto(self) -> float:
        """Alto de la caja, que sirve de medida del tamano de la letra."""
        return self.y1 - self.y0


@dataclass
class Bloque:
    """Un grupo de lineas que pdftotext considero una unidad de maquetado.

    Se conserva su agrupacion en vez de rehacerla: pdftotext ya hizo ese
    analisis y sus bloques corresponden casi siempre a un parrafo.
    """

    lineas: list[Linea] = field(default_factory=list)

    @property
    def y0(self) -> float:
        return min(linea.y0 for linea in self.lineas)

    @property
    def y1(self) -> float:
        return max(linea.y1 for linea in self.lineas)

    @property
    def x0(self) -> float:
        return min(linea.x0 for linea in self.lineas)


@dataclass
class Pagina:
    numero: int
    ancho: float
    alto: float
    bloques: list[Bloque] = field(default_factory=list)

    @property
    def lineas(self) -> list[Linea]:
        return [linea for bloque in self.bloques for linea in bloque.lineas]


def _xml_de(pdf: Path, primera: int, ultima: int) -> str:
    try:
        resultado = subprocess.run(
            [
                "pdftotext", "-bbox-layout",
                "-f", str(primera), "-l", str(ultima),
                str(pdf), "-",
            ],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except FileNotFoundError as error:
        raise ErrorDeLectura(
            "pdftotext no esta instalado o no se encuentra en el PATH"
        ) from error

    if resultado.returncode != 0 or not resultado.stdout.strip():
        raise ErrorDeLectura(
            f"pdftotext no devolvio nada para {pdf} (codigo {resultado.returncode}). "
            f"Puede que el PDF no tenga capa de texto."
        )
    return resultado.stdout


def leer(pdf: Path, primera: int, ultima: int) -> list[Pagina]:
    """Devuelve las paginas del rango, con sus bloques y lineas ubicadas."""
    pdf = Path(pdf)
    if not pdf.exists():
        raise ErrorDeLectura(f"No existe el PDF: {pdf}")

    raiz = ET.fromstring(_xml_de(pdf, primera, ultima))

    paginas: list[Pagina] = []
    for indice, nodo_pagina in enumerate(raiz.iter(f"{XHTML}page")):
        pagina = Pagina(
            numero=primera + indice,
            ancho=float(nodo_pagina.get("width", 0)),
            alto=float(nodo_pagina.get("height", 0)),
        )

        for nodo_bloque in nodo_pagina.iter(f"{XHTML}block"):
            bloque = Bloque()
            for nodo_linea in nodo_bloque.iter(f"{XHTML}line"):
                palabras = [
                    (nodo.text or "").strip()
                    for nodo in nodo_linea.iter(f"{XHTML}word")
                ]
                texto = " ".join(p for p in palabras if p)
                if not texto:
                    continue
                bloque.lineas.append(
                    Linea(
                        texto=texto,
                        x0=float(nodo_linea.get("xMin", 0)),
                        y0=float(nodo_linea.get("yMin", 0)),
                        x1=float(nodo_linea.get("xMax", 0)),
                        y1=float(nodo_linea.get("yMax", 0)),
                    )
                )
            if bloque.lineas:
                pagina.bloques.append(bloque)

        paginas.append(pagina)

    if not paginas:
        raise ErrorDeLectura(f"No se encontro ninguna pagina en {pdf}")

    return paginas
