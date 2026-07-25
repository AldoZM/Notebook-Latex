"""Un compositor por tipo de bloque del contrato.

Cada funcion recibe el `contenido` del bloque y devuelve un fragmento de LaTeX.
Ninguna copia texto del contrato sin pasarlo por `escapar`.
"""

from ctex.composicion.escapado import comandos_no_permitidos, escapar

_NIVELES = ["section", "subsection", "subsubsection"]


def componer_titulo(contenido: dict) -> str:
    nivel = int(contenido.get("nivel", 1))
    indice = min(max(nivel, 1), len(_NIVELES)) - 1
    return f"\\{_NIVELES[indice]}{{{escapar(contenido['texto'])}}}"


def componer_parrafo(contenido: dict) -> str:
    return escapar(contenido["texto"])


def degradar(texto_original: str) -> str:
    """Inserta un fragmento como texto literal, marcado visiblemente (D18)."""
    return f"\\ctexdegradado{{{escapar(texto_original)}}}"


def componer_ecuacion(contenido: dict) -> str:
    latex = contenido["latex"]

    prohibidos = comandos_no_permitidos(latex)
    if prohibidos:
        # No se compone lo que no se entiende. El bloque se degrada y el resto
        # del documento sale bien.
        return degradar(latex)

    entorno = "equation" if contenido.get("numerada", True) else "equation*"
    return f"\\begin{{{entorno}}}\n{latex}\n\\end{{{entorno}}}"
