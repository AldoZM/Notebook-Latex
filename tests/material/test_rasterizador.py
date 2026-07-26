import shutil
import pytest

from ctex.compilacion.tectonic import compilar
from ctex.material.rasterizador import ErrorDeRasterizacion, rasterizar_pdf

pytestmark = pytest.mark.skipif(
    shutil.which("tectonic") is None or shutil.which("pdftoppm") is None,
    reason="Tectonic o pdftoppm no estan instalados",
)

TEX_MINIMO = r"""\documentclass{article}
\begin{document}
Hola generador.
\end{document}
"""


def test_rasterizar_pdf_produce_png_valido(tmp_path):
    pdf_path = compilar(TEX_MINIMO, tmp_path)
    png_path = rasterizar_pdf(pdf_path, ppp=200)

    assert png_path.exists()
    assert png_path.suffix == ".png"
    contenido = png_path.read_bytes()
    # Firma oficial de un PNG: \x89PNG\r\n\x1a\n
    assert contenido[:8] == b"\x89PNG\r\n\x1a\n"


def test_error_claro_cuando_falta_pdftoppm(tmp_path, monkeypatch):
    pdf_path = compilar(TEX_MINIMO, tmp_path)

    def mock_which(cmd):
        if cmd == "pdftoppm":
            return None
        return shutil.which(cmd)

    monkeypatch.setattr(shutil, "which", mock_which)

    with pytest.raises(ErrorDeRasterizacion) as exc_info:
        rasterizar_pdf(pdf_path)

    assert "pdftoppm" in str(exc_info.value)
