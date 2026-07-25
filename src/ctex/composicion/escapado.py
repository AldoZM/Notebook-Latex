"""Escapado de texto y filtrado de comandos.

Esta es la frontera de seguridad de la composicion. Todo texto que venga del
contrato pasa por `escapar` antes de llegar al .tex, y todo campo `latex` pasa
por `comandos_no_permitidos` antes de insertarse tal cual.
"""

import re

# str.translate hace UNA sola pasada sobre la cadena, asi que las llaves que
# introduce \textbackslash{} no se vuelven a escapar. Un bucle de .replace()
# encadenados si tendria ese error.
_TABLA = str.maketrans({
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
})

COMANDOS_PERMITIDOS = frozenset({
    # estructura matematica
    "frac", "sqrt", "sum", "prod", "int", "lim", "infty", "partial",
    "left", "right", "cdot", "times", "div", "pm", "mp",
    "leq", "geq", "neq", "approx", "equiv", "propto",
    "quad", "qquad",
    # funciones
    "sin", "cos", "tan", "cot", "sec", "csc",
    "arcsin", "arccos", "arctan", "log", "ln", "exp", "max", "min",
    # letras griegas
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta",
    "eta", "theta", "vartheta", "iota", "kappa", "lambda", "mu", "nu",
    "xi", "pi", "rho", "sigma", "tau", "upsilon", "phi", "varphi",
    "chi", "psi", "omega",
    "Gamma", "Delta", "Theta", "Lambda", "Xi", "Pi", "Sigma",
    "Upsilon", "Phi", "Psi", "Omega",
    # conjuntos y logica
    "in", "notin", "subset", "subseteq", "cup", "cap", "emptyset",
    "forall", "exists", "to", "rightarrow", "leftarrow", "Rightarrow",
    # tipografia matematica
    "mathbb", "mathcal", "mathrm", "mathbf", "text",
})

_PATRON_COMANDO = re.compile(r"\\([a-zA-Z]+)")

# La notacion ^^ de TeX codifica un caracter por su valor: ^^77 es 'w'. La
# sustitucion ocurre en el lexer, ANTES de que exista el nombre del comando, asi
# que `\^^77rite18` es `\write18` para el motor y no es ningun comando para una
# busqueda de \[a-zA-Z]+. Es el hueco por donde se evade la lista blanca (D32).
#
# Dos acentos seguidos nunca aparecen en matematicas legitimas: `x^2` y `x^{n+1}`
# llevan uno solo. Por eso se puede prohibir el par sin estorbar a los
# superindices, que si son necesarios.
_PATRON_CARET = re.compile(r"\^\^")


def escapar(texto: str) -> str:
    """Convierte texto plano en texto seguro para insertar en un .tex."""
    return texto.translate(_TABLA)


def comandos_no_permitidos(latex: str) -> set[str]:
    """Devuelve los comandos del fragmento que no estan en la lista blanca.

    Solo mira comandos con nombre alfabetico. Lo que se escribe con notacion ^^
    no lo ve: de eso se encarga `notacion_peligrosa`.
    """
    encontrados = set(_PATRON_COMANDO.findall(latex))
    return encontrados - COMANDOS_PERMITIDOS


def notacion_peligrosa(latex: str) -> set[str]:
    """Detecta la notacion que construye comandos sin escribir su nombre.

    Devuelve `{"^^"}` o un conjunto vacio. Va aparte de la lista blanca porque
    no es un comando prohibido: es la forma de esconder cualquiera de ellos.
    """
    return {"^^"} if _PATRON_CARET.search(latex) else set()


def motivos_de_rechazo(latex: str) -> set[str]:
    """Todo lo que impide insertar el fragmento tal cual en el .tex.

    Esta es la compuerta del unico campo del contrato por donde entra LaTeX
    (D31). Un conjunto vacio significa que el fragmento puede pasar.
    """
    return comandos_no_permitidos(latex) | notacion_peligrosa(latex)
