import json
from pathlib import Path

from ctex.composicion.compositor import componer

DATOS = Path(__file__).parent.parent / "datos"


def cargar_ejemplo() -> dict:
    with open(DATOS / "hoja_ejemplo.json", encoding="utf-8") as f:
        return json.load(f)


def test_el_ejemplo_produce_un_documento_completo():
    tex, advertencias = componer(cargar_ejemplo())
    assert tex.startswith(r"\documentclass")
    assert tex.rstrip().endswith(r"\end{document}")
    assert advertencias == []


def test_los_bloques_salen_en_el_orden_del_contrato():
    tex, _ = componer(cargar_ejemplo())
    posicion_titulo = tex.index(r"\section{Series de Fourier}")
    posicion_ecuacion = tex.index(r"\begin{equation}")
    posicion_grafica = tex.index(r"\begin{tikzpicture}")
    assert posicion_titulo < posicion_ecuacion < posicion_grafica


def test_un_bloque_de_tipo_desconocido_se_salta_con_advertencia():
    # Regla 1 del contrato. Se prueba desde la v1 metiendo un tipo inventado.
    documento = cargar_ejemplo()
    documento["bloques"].append({
        "id": "b9",
        "tipo": "inventado",
        "region": {"x": 0, "y": 0, "ancho": 10, "alto": 10},
        "confianza": 0.5,
        "contenido": {"lo_que_sea": True},
    })

    tex, advertencias = componer(documento)

    assert len(advertencias) == 1
    assert "inventado" in advertencias[0]
    assert "b9" in advertencias[0]
    assert tex.startswith(r"\documentclass")


def test_un_bloque_desconocido_no_impide_componer_los_demas():
    documento = cargar_ejemplo()
    documento["bloques"].insert(0, {
        "id": "b0",
        "tipo": "tabla",
        "region": {"x": 0, "y": 0, "ancho": 10, "alto": 10},
        "confianza": 0.9,
        "contenido": {},
    })

    tex, _ = componer(documento)

    assert r"\section{Series de Fourier}" in tex
    assert r"\begin{tikzpicture}" in tex


def test_un_documento_sin_bloques_produce_un_pdf_vacio_valido():
    documento = cargar_ejemplo()
    documento["bloques"] = []
    tex, advertencias = componer(documento)
    assert r"\begin{document}" in tex
    assert advertencias == []
