"""La unica plantilla de la v1: un articulo limpio (D16)."""

PREAMBULO = r"""\documentclass[11pt]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[spanish]{babel}
\usepackage[margin=2.5cm]{geometry}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepackage{xcolor}

% Entorno de los listados de codigo. No es verbatim ni lo parece: recibe texto
% ya escapado por `escapar`, solo le pone tipografia de ancho fijo. Un verbatim
% de verdad seria un segundo canal de inyeccion, porque su fin se delimita con
% una cadena que el contenido puede contener.
\newenvironment{ctexcodigo}
  {\par\medskip\noindent\ttfamily\small\raggedright}
  {\par\medskip}

% Marca visible para los bloques degradados (D18).
\newcommand{\ctexdegradado}[1]{%
  \par\noindent\fcolorbox{red}{red!5}{%
    \parbox{\dimexpr\linewidth-2\fboxsep-2\fboxrule}{%
      \textcolor{red}{\textbf{[no se pudo componer]}}\\ \texttt{#1}%
    }%
  }\par
}
"""


def envolver(cuerpo: str) -> str:
    """Mete el cuerpo compuesto dentro del documento completo."""
    return f"{PREAMBULO}\n\\begin{{document}}\n\n{cuerpo}\n\n\\end{{document}}\n"
