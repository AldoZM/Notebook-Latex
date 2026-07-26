# src/ctex/extraccion/tipos.py
"""Los tipos que cruzan las fronteras del extractor.

Ninguno depende de OpenCV: son datos, no imagenes.
"""

from dataclasses import dataclass, field, replace


@dataclass(frozen=True)
class Recta:
    """Una recta en la forma de Hough: distancia al origen y angulo normal."""

    rho: float
    theta: float


@dataclass(frozen=True)
class Caja:
    """Los cuatro bordes del area de la grafica, en pixeles.

    El borde izquierdo vale xmin y el derecho xmax; el inferior ymin y el
    superior ymax. Es lo que ancla la escala: dos rectas infinitas no bastan.
    """

    izquierda: float
    derecha: float
    arriba: float
    abajo: float

    def __post_init__(self) -> None:
        if self.derecha <= self.izquierda:
            raise ValueError(
                f"Caja invalida: derecha ({self.derecha}) no es mayor que "
                f"izquierda ({self.izquierda})"
            )
        if self.abajo <= self.arriba:
            raise ValueError(
                f"Caja invalida: abajo ({self.abajo}) no es mayor que "
                f"arriba ({self.arriba})"
            )

    @property
    def ancho(self) -> float:
        return self.derecha - self.izquierda

    @property
    def alto(self) -> float:
        return self.abajo - self.arriba


@dataclass(frozen=True)
class Transformacion:
    """Convierte coordenadas de pixel a valores de la grafica."""

    escala_x: float
    escala_y: float
    izquierda: float
    arriba: float
    xmin: float = 0.0
    ymax: float = 0.0

    def con_ymax(self, ymax: float) -> "Transformacion":
        return replace(self, ymax=ymax)

    def con_xmin(self, xmin: float) -> "Transformacion":
        return replace(self, xmin=xmin)

    def a_valor_x(self, columna: float) -> float:
        return self.xmin + (columna - self.izquierda) * self.escala_x

    def a_valor_y(self, fila: float) -> float:
        # Resta y no suma: la fila 0 esta arriba en la imagen, y arriba esta
        # ymax en la grafica. Invertir este signo produce una curva reflejada
        # que sigue pareciendo una curva, asi que no se nota.
        return self.ymax - (fila - self.arriba) * self.escala_y


@dataclass
class Traza:
    """Los intermedios de los siete pasos, para depurar y para medir (D43)."""

    caja: Caja | None = None
    transformacion: Transformacion | None = None
    centroides: object = None
    validez: object = None
    puntos: list = field(default_factory=list)
