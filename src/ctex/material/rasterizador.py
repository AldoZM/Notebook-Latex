"""Rasterizador de PDF a PNG usando pdftoppm (Tarea 3)."""

import shutil
import subprocess
from pathlib import Path


class ErrorDeRasterizacion(Exception):
    """Error al rasterizar el PDF a PNG."""


def rasterizar_pdf(
    pdf_path: Path, ppp: int = 200, ruta_salida: Path | None = None
) -> Path:
    """Rasteriza un archivo PDF a PNG usando pdftoppm.

    Args:
        pdf_path: Ruta al archivo PDF.
        ppp: Puntos por pulgada (resolucion, por defecto 200).
        ruta_salida: Ruta deseada del PNG resultante. Si es None, reemplaza la extension
            .pdf por .png.

    Returns:
        Path al archivo PNG generado.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise ErrorDeRasterizacion(f"El archivo PDF no existe: {pdf_path}")

    if shutil.which("pdftoppm") is None:
        raise ErrorDeRasterizacion(
            "pdftoppm no esta instalado o no se encuentra en el PATH del sistema."
        )

    if ruta_salida is None:
        ruta_salida = pdf_path.with_suffix(".png")
    else:
        ruta_salida = Path(ruta_salida)

    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    prefix = ruta_salida.with_suffix("")

    cmd = [
        "pdftoppm",
        "-png",
        "-r",
        str(ppp),
        "-singlefile",
        str(pdf_path),
        str(prefix),
    ]

    try:
        resultado = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as error:
        raise ErrorDeRasterizacion(
            "pdftoppm no esta instalado o no se encuentra en el PATH del sistema."
        ) from error

    png_path = prefix.with_suffix(".png")
    if resultado.returncode != 0 or not png_path.exists():
        raise ErrorDeRasterizacion(
            f"pdftoppm no pudo generar la imagen PNG (codigo {resultado.returncode}).\n"
            f"Stderr: {resultado.stderr}"
        )

    return png_path
