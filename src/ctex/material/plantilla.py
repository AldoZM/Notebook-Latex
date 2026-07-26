"""Plantilla standalone para el material sintético del nivel -1 (Tarea 6)."""

PREAMBULO_STANDALONE = r"""\documentclass[border=2mm]{standalone}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
"""


class ErrorDeExtraccionTikz(ValueError):
    """Error al intentar extraer un bloque tikzpicture de un fragmento LaTeX."""

    pass


def extraer_tikzpicture(fragmento: str) -> str:
    """Extrae el bloque \\begin{tikzpicture} ... \\end{tikzpicture} de un fragmento.

    Args:
        fragmento: Texto LaTeX devuelto por componer_grafica().

    Returns:
        Cadena con el bloque tikzpicture completo.

    Raises:
        ErrorDeExtraccionTikz: Si no se encuentra el delimitador de inicio o fin.
    """
    tag_inicio = r"\begin{tikzpicture}"
    tag_fin = r"\end{tikzpicture}"

    inicio = fragmento.find(tag_inicio)
    fin = fragmento.find(tag_fin)

    if inicio == -1 or fin == -1 or fin < inicio:
        raise ErrorDeExtraccionTikz(
            "No se encontro el bloque tikzpicture en el fragmento proporcionado"
        )

    fin += len(tag_fin)
    return fragmento[inicio:fin]


def envolver_standalone(cuerpo_tikz: str) -> str:
    """Envuelve un fragmento tikzpicture dentro del documento standalone.

    Args:
        cuerpo_tikz: Fragmento que contiene el entorno tikzpicture.

    Returns:
        Documento LaTeX completo de tipo standalone.
    """
    return f"{PREAMBULO_STANDALONE}\n\\begin{{document}}\n{cuerpo_tikz}\n\\end{{document}}\n"
