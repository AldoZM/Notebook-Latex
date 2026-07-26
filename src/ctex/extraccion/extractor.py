# src/ctex/extraccion/extractor.py
"""La tuberia: de un recorte a un documento del contrato.

Devuelve tambien la traza con los intermedios (D43).
"""

from pathlib import Path

from ctex.extraccion.escala import fijar_escala
from ctex.extraccion.imagen import cargar
from ctex.extraccion.marco import detectar_caja
from ctex.extraccion.rastreo import barrer
from ctex.extraccion.remuestreo import remuestrear
from ctex.extraccion.tinta import aislar_curva
from ctex.extraccion.tipos import Traza

# Marcador de posicion declarado (D44). El aparato de confianza es la fase 2.
# Se elige 0.5 porque es el valor que menos informacion aparenta.
CONFIANZA_MARCADOR = 0.5


def extraer(
    ruta_imagen: Path,
    rango_x: tuple[float, float],
    rango_y: tuple[float, float],
    cuantos: int = 30,
) -> tuple[dict, Traza]:
    """De un recorte de grafica a un documento del contrato v1.0."""
    ruta_imagen = Path(ruta_imagen)
    imagen = cargar(ruta_imagen)

    traza = Traza()

    caja = detectar_caja(imagen)
    traza.caja = caja

    transformacion = fijar_escala(caja, rango_x, rango_y)
    traza.transformacion = transformacion

    mascara = aislar_curva(imagen, caja)

    centroides, validez = barrer(mascara)
    traza.centroides = centroides
    traza.validez = validez

    puntos = remuestrear(centroides, validez, transformacion, cuantos)
    traza.puntos = puntos

    alto, ancho = imagen.shape
    documento = {
        "version_contrato": "1.0",
        # `pagina: 1` es deuda anotada en D46: el recorte no viene de la
        # pagina de nada, pero el esquema lo exige.
        "origen": {"archivo": ruta_imagen.name, "pagina": 1},
        "bloques": [
            {
                "id": "b1",
                "tipo": "grafica",
                # La region es el recorte entero: por D37 la entrada ya es la
                # grafica y no hay nada que localizar.
                "region": {
                    "x": 0, "y": 0, "ancho": float(ancho), "alto": float(alto),
                },
                "confianza": CONFIANZA_MARCADOR,
                "contenido": {
                    "tipo_grafica": "lineas",
                    "titulo": "",
                    "ejes": {
                        "x": {
                            "min": rango_x[0], "max": rango_x[1],
                            "etiqueta": "", "escala": "lineal",
                        },
                        "y": {
                            "min": rango_y[0], "max": rango_y[1],
                            "etiqueta": "", "escala": "lineal",
                        },
                    },
                    "series": [{"etiqueta": "", "puntos": puntos}],
                },
            }
        ],
        "dudas": [],
    }

    return documento, traza
