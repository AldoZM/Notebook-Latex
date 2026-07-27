from pathlib import Path

from ctex.contrato.validador import validar
from ctex.libro.contrato import a_contrato
from ctex.libro.estructura import Parte


def partes_de_ejemplo():
    return [
        Parte(tipo="parrafo", texto="Additionally, for US positions."),
        Parte(tipo="titulo", texto="Beware of (Potential) Stigma", nivel=2),
        Parte(tipo="parrafo", texto="Certain languages have stigmas."),
    ]


def test_el_documento_cumple_el_contrato():
    documento = a_contrato(partes_de_ejemplo(), Path("libro.pdf"), 40)
    validar(documento)  # no lanza


def test_los_bloques_conservan_el_orden_y_el_tipo():
    documento = a_contrato(partes_de_ejemplo(), Path("libro.pdf"), 40)
    assert [b["tipo"] for b in documento["bloques"]] == [
        "parrafo", "titulo", "parrafo",
    ]


def test_el_titulo_lleva_nivel_y_el_parrafo_no():
    documento = a_contrato(partes_de_ejemplo(), Path("libro.pdf"), 40)
    titulo, parrafo = documento["bloques"][1], documento["bloques"][0]
    assert titulo["contenido"]["nivel"] == 2
    assert "nivel" not in parrafo["contenido"]


def test_el_origen_guarda_el_archivo_y_la_pagina():
    documento = a_contrato(partes_de_ejemplo(), Path(r"D:\algo\libro.pdf"), 40)
    assert documento["origen"] == {"archivo": "libro.pdf", "pagina": 40}


def test_la_confianza_es_el_marcador_de_posicion():
    documento = a_contrato(partes_de_ejemplo(), Path("libro.pdf"), 40)
    assert all(b["confianza"] == 0.5 for b in documento["bloques"])


def test_un_documento_sin_partes_sigue_siendo_valido():
    validar(a_contrato([], Path("libro.pdf"), 1))
