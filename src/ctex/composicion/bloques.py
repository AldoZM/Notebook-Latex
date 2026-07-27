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


def componer_codigo(contenido: dict) -> str:
    """Un listado de codigo, con cada linea escapada.

    NO usa `verbatim` ni ningun entorno literal, a proposito. Un entorno
    literal delimita su fin con una cadena —`\\end{verbatim}`—, asi que un
    listado que la contenga se sale del entorno y lo que siga se interpreta
    como LaTeX. Eso seria un segundo canal por donde entra un comando, y D31
    dice que el unico es el campo `latex` de las ecuaciones.

    Escapando cada linea con `escapar`, el texto no puede formar un comando ni
    salirse de nada: la barra invertida se vuelve `\\textbackslash{}` antes de
    que el motor la lea. Se reusa la frontera de seguridad que ya existe en vez
    de abrir una nueva.
    """
    lineas = contenido.get("lineas", [])

    compuestas = []
    for linea in lineas:
        # La sangria se cuenta ANTES de escapar, porque despues los espacios
        # quedan mezclados con las secuencias de escape. Y se reintroduce con
        # `~` DESPUES, porque escapar() convierte cualquier `~` que viniera en
        # el texto original: el que se agregue aqui no puede confundirse con uno
        # del contenido.
        sangria = len(linea) - len(linea.lstrip(" "))
        compuestas.append("~" * sangria + escapar(linea.strip(" ")))

    cuerpo = " \\\\\n".join(compuestas)
    return f"\\begin{{ctexcodigo}}\n{cuerpo}\n\\end{{ctexcodigo}}"


def componer_tabla(contenido: dict) -> str:
    """Una tabla, con cada celda escapada.

    El escapado importa mas aqui que en un parrafo: `&` separa columnas y `\\\\`
    separa filas, asi que una celda con un `&` sin escapar cambiaria la forma de
    la tabla. `escapar` lo convierte en `\\&` y la celda se queda en su lugar.
    """
    encabezado = contenido.get("encabezado", [])
    filas = contenido.get("filas", [])

    columnas = len(encabezado) if encabezado else (len(filas[0]) if filas else 0)
    if columnas == 0:
        return degradar("tabla sin columnas")

    def fila_a_latex(celdas: list) -> str:
        # Las filas cortas se rellenan y las largas se recortan: una tabla con
        # filas de distinto largo no compila, y degradar el documento entero por
        # una celda de menos seria peor que perderla.
        ajustadas = (list(celdas) + [""] * columnas)[:columnas]
        return " & ".join(escapar(str(celda)) for celda in ajustadas) + " \\\\"

    partes = [f"\\begin{{tabular}}{{{'l' * columnas}}}", "\\hline"]
    if encabezado:
        partes.append(fila_a_latex(encabezado))
        partes.append("\\hline")
    partes.extend(fila_a_latex(fila) for fila in filas)
    partes.append("\\hline")
    partes.append("\\end{tabular}")

    return "\n".join(partes)


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
