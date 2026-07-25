"""Documento estructurado -> LaTeX (etapa 6).

Construye el .tex a partir del contrato con plantillas propias. Nunca copia y
pega lo que venga en el contrato: cada tipo de bloque tiene su compositor, y lo
que no reconoce lo salta.
"""

from ctex.composicion.bloques import (
    componer_ecuacion,
    componer_grafica,
    componer_parrafo,
    componer_titulo,
)
from ctex.composicion.plantilla import envolver

_COMPOSITORES = {
    "titulo": componer_titulo,
    "parrafo": componer_parrafo,
    "ecuacion": componer_ecuacion,
    "grafica": componer_grafica,
}


def componer(documento: dict) -> tuple[str, list[str]]:
    """Devuelve el .tex completo y las advertencias que se generaron.

    Regla 1 del contrato: un bloque de tipo desconocido se salta con
    advertencia, no revienta.
    """
    fragmentos: list[str] = []
    advertencias: list[str] = []

    for bloque in documento["bloques"]:
        compositor = _COMPOSITORES.get(bloque["tipo"])
        if compositor is None:
            advertencias.append(
                f"Bloque '{bloque['id']}' de tipo desconocido "
                f"'{bloque['tipo']}': se omitio."
            )
            continue
        fragmentos.append(compositor(bloque["contenido"]))

    return envolver("\n\n".join(fragmentos)), advertencias
