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


def escapar(texto: str) -> str:
    """Convierte texto plano en texto seguro para insertar en un .tex."""
    return texto.translate(_TABLA)


def comandos_no_permitidos(latex: str) -> set[str]:
    """Devuelve los comandos del fragmento que no estan en la lista blanca.

    Un conjunto vacio significa que el fragmento se puede insertar tal cual.
    """
    encontrados = set(_PATRON_COMANDO.findall(latex))
    return encontrados - COMANDOS_PERMITIDOS
