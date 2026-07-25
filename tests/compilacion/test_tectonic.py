import shutil

import pytest

from ctex.compilacion.tectonic import ErrorDeCompilacion, compilar

pytestmark = pytest.mark.skipif(
    shutil.which("tectonic") is None,
    reason="Tectonic no esta instalado",
)

TEX_MINIMO = r"""\documentclass{article}
\begin{document}
Hola.
\end{document}
"""

TEX_ROTO = r"""\documentclass{article}
\begin{document}
\begin{itemize}
\end{document}
"""


def test_un_documento_minimo_produce_un_pdf(tmp_path):
    pdf = compilar(TEX_MINIMO, tmp_path)
    assert pdf.exists()
    assert pdf.suffix == ".pdf"
    assert pdf.stat().st_size > 0


def test_el_pdf_empieza_con_la_firma_de_pdf(tmp_path):
    pdf = compilar(TEX_MINIMO, tmp_path)
    assert pdf.read_bytes()[:5] == b"%PDF-"


def test_el_tex_se_conserva_junto_al_pdf(tmp_path):
    # La salida es el PDF y el .tex: el .tex es del usuario.
    compilar(TEX_MINIMO, tmp_path)
    assert (tmp_path / "documento.tex").exists()


def test_un_documento_roto_levanta_con_el_registro(tmp_path):
    with pytest.raises(ErrorDeCompilacion) as excepcion:
        compilar(TEX_ROTO, tmp_path)
    assert excepcion.value.registro != ""
