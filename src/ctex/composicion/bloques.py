"""Un compositor por tipo de bloque del contrato.

Cada funcion recibe el `contenido` del bloque y devuelve un fragmento de LaTeX.
Ninguna copia texto del contrato sin pasarlo por `escapar`.
"""

from ctex.composicion.escapado import escapar, motivos_de_rechazo

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

    prohibidos = motivos_de_rechazo(latex)
    if prohibidos:
        # No se compone lo que no se entiende. El bloque se degrada y el resto
        # del documento sale bien.
        return degradar(latex)

    entorno = "equation" if contenido.get("numerada", True) else "equation*"
    return f"\\begin{{{entorno}}}\n{latex}\n\\end{{{entorno}}}"


def _formatear(valor: float) -> str:
    """Numero sin ceros de relleno: 0.9 y no 0.900000."""
    if isinstance(valor, int) or float(valor).is_integer():
        return str(int(valor))
    return f"{valor:g}"


def _opciones_de_eje(eje: dict, nombre: str) -> list[str]:
    opciones = [
        f"{nombre}min={_formatear(eje['min'])}",
        f"{nombre}max={_formatear(eje['max'])}",
        f"{nombre}label={{{escapar(eje.get('etiqueta', ''))}}}",
    ]
    if eje.get("escala") == "log":
        opciones.append(f"{nombre}mode=log")
    return opciones


def componer_grafica(contenido: dict) -> str:
    ejes = contenido["ejes"]
    opciones = _opciones_de_eje(ejes["x"], "x") + _opciones_de_eje(ejes["y"], "y")
    opciones.append("grid=both")
    opciones.append("legend pos=north east")

    trazos = []
    for serie in contenido["series"]:
        puntos = " ".join(
            f"({_formatear(x)},{_formatear(y)})" for x, y in serie["puntos"]
        )
        trazos.append(f"    \\addplot coordinates {{{puntos}}};")
        trazos.append(f"    \\addlegendentry{{{escapar(serie.get('etiqueta', ''))}}}")

    cuerpo = "\n".join(trazos)
    opciones_texto = ",\n      ".join(opciones)
    titulo = escapar(contenido.get("titulo", ""))

    return (
        "\\begin{figure}[htbp]\n"
        "  \\centering\n"
        "  \\begin{tikzpicture}\n"
        "    \\begin{axis}[\n"
        f"      {opciones_texto},\n"
        "    ]\n"
        f"{cuerpo}\n"
        "    \\end{axis}\n"
        "  \\end{tikzpicture}\n"
        f"  \\caption{{{titulo}}}\n"
        "\\end{figure}"
    )
