"""Un compositor por tipo de bloque del contrato.

Cada funcion recibe el `contenido` del bloque y devuelve un fragmento de LaTeX.
Ninguna copia texto del contrato sin pasarlo por `escapar`.
"""

from ctex.composicion.escapado import escapar

_NIVELES = ["section", "subsection", "subsubsection"]


def componer_titulo(contenido: dict) -> str:
    nivel = int(contenido.get("nivel", 1))
    indice = min(max(nivel, 1), len(_NIVELES)) - 1
    return f"\\{_NIVELES[indice]}{{{escapar(contenido['texto'])}}}"


def componer_parrafo(contenido: dict) -> str:
    return escapar(contenido["texto"])
