"""Invocacion de Tectonic (etapa 7).

Compilar es ejecutar, asi que esto corre con las defensas de la Seccion 9:
shell-escape desactivado via --untrusted, y un limite de tiempo que mata el
proceso. El limite de memoria y la ausencia de red los pone el contenedor, no
este modulo.
"""

import subprocess
from pathlib import Path

LIMITE_SEGUNDOS = 60

NOMBRE_FUENTE = "documento.tex"
NOMBRE_PDF = "documento.pdf"


class ErrorDeCompilacion(Exception):
    """Tectonic no produjo un PDF."""

    def __init__(self, mensaje: str, registro: str = "") -> None:
        super().__init__(mensaje)
        self.registro = registro


def compilar(tex: str, carpeta_salida: Path) -> Path:
    """Compila el .tex y devuelve la ruta del PDF.

    El .tex se conserva junto al PDF: es del usuario y puede llevarselo.
    """
    carpeta_salida = Path(carpeta_salida)
    carpeta_salida.mkdir(parents=True, exist_ok=True)

    fuente = carpeta_salida / NOMBRE_FUENTE
    fuente.write_text(tex, encoding="utf-8")

    try:
        resultado = subprocess.run(
            [
                "tectonic",
                "--untrusted",      # sin shell-escape, sin rutas absolutas
                "--outdir", str(carpeta_salida),
                str(fuente),
            ],
            capture_output=True,
            text=True,
            timeout=LIMITE_SEGUNDOS,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise ErrorDeCompilacion(
            f"La compilacion excedio {LIMITE_SEGUNDOS} s y se mato el proceso."
        ) from error

    pdf = carpeta_salida / NOMBRE_PDF
    if resultado.returncode != 0 or not pdf.exists():
        raise ErrorDeCompilacion(
            "Tectonic no produjo un PDF.",
            registro=resultado.stderr or resultado.stdout,
        )

    return pdf
