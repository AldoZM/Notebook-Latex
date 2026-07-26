"""Definicion de graficas sinteticas para el material de prueba nivel -1."""

import math
import random

FAMILIAS = ["lineal", "exponencial_decreciente", "senoidal"]


def generar_definicion(familia: str | None = None, semilla: int = 42) -> dict:
    """Genera la definicion deterministica de una grafica sintetica.

    Args:
        familia: Nombre de la familia de curvas ("lineal", "exponencial_decreciente",
            "senoidal"). Si es None, se elige una segun la semilla.
        semilla: Semilla entera para reproducibilidad exacta.

    Returns:
        Diccionario con la definicion de la grafica, incluyendo ejes, titulo,
        familia, semilla y puntos.
    """
    rnd = random.Random(semilla)

    if familia is None:
        familia = rnd.choice(FAMILIAS)
    elif familia not in FAMILIAS:
        raise ValueError(
            f"Familia desconocida: '{familia}'. Opciones validas: {FAMILIAS}"
        )

    if familia == "lineal":
        m = rnd.uniform(0.5, 3.0)
        b = rnd.uniform(-5.0, 5.0)
        xmin, xmax = 0.0, 10.0
        n_puntos = 11
        xs = [xmin + (xmax - xmin) * i / (n_puntos - 1) for i in range(n_puntos)]
        ys = [m * x + b for x in xs]

    elif familia == "exponencial_decreciente":
        A = rnd.uniform(2.0, 10.0)
        k = rnd.uniform(0.2, 0.8)
        C = rnd.uniform(0.0, 5.0)
        xmin, xmax = 0.0, 5.0
        n_puntos = 11
        xs = [xmin + (xmax - xmin) * i / (n_puntos - 1) for i in range(n_puntos)]
        ys = [A * math.exp(-k * x) + C for x in xs]

    elif familia == "senoidal":
        A = rnd.uniform(1.0, 5.0)
        w = rnd.uniform(0.5, 2.0)
        phi = rnd.uniform(0.0, math.pi)
        C = rnd.uniform(-2.0, 2.0)
        xmin, xmax = 0.0, 10.0
        n_puntos = 21
        xs = [xmin + (xmax - xmin) * i / (n_puntos - 1) for i in range(n_puntos)]
        ys = [A * math.sin(w * x + phi) + C for x in xs]

    puntos = [[round(x, 4), round(y, 4)] for x, y in zip(xs, ys)]

    min_y = min(ys)
    max_y = max(ys)
    ymin = math.floor(min_y) - 1.0
    ymax = math.ceil(max_y) + 1.0

    return {
        "familia": familia,
        "semilla": semilla,
        "tipo_grafica": "lineas",
        "titulo": f"Grafica sintetica ({familia})",
        "ejes": {
            "x": {
                "min": round(xmin, 4),
                "max": round(xmax, 4),
                "etiqueta": "x",
                "escala": "lineal",
            },
            "y": {
                "min": round(ymin, 4),
                "max": round(ymax, 4),
                "etiqueta": "y",
                "escala": "lineal",
            },
        },
        "series": [
            {
                "etiqueta": f"curva_{familia}",
                "puntos": puntos,
            }
        ],
    }
