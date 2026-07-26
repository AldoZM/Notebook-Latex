# src/ctex/extraccion/escala.py
"""Paso 3: de la caja y los rangos tecleados a la transformacion.

Aritmetica pura. La escala no se lee de la imagen, se recibe (D34).
"""

from ctex.extraccion.tipos import Caja, Transformacion


class ErrorDeEscala(Exception):
    """Los rangos dados no sirven para construir una transformacion."""


def _validar(rango: tuple[float, float], nombre: str) -> None:
    minimo, maximo = rango
    if maximo <= minimo:
        raise ErrorDeEscala(
            f"El rango de {nombre} va de {minimo} a {maximo}: "
            f"el maximo tiene que ser mayor que el minimo"
        )


def fijar_escala(
    caja: Caja,
    rango_x: tuple[float, float],
    rango_y: tuple[float, float],
) -> Transformacion:
    """Construye la conversion de pixel a valor a partir de la caja."""
    _validar(rango_x, "x")
    _validar(rango_y, "y")

    xmin, xmax = rango_x
    ymin, ymax = rango_y

    return Transformacion(
        escala_x=(xmax - xmin) / caja.ancho,
        escala_y=(ymax - ymin) / caja.alto,
        izquierda=caja.izquierda,
        arriba=caja.arriba,
        xmin=xmin,
        ymax=ymax,
    )
