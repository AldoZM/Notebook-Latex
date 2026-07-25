import copy
import json
from pathlib import Path

import pytest

from ctex.contrato.validador import ErrorDeContrato, validar

DATOS = Path(__file__).parent.parent / "datos"


def cargar_ejemplo() -> dict:
    with open(DATOS / "hoja_ejemplo.json", encoding="utf-8") as f:
        return json.load(f)


def test_el_ejemplo_de_la_especificacion_es_valido():
    validar(cargar_ejemplo())


def test_una_version_distinta_se_rechaza():
    doc = cargar_ejemplo()
    doc["version_contrato"] = "2.0"
    with pytest.raises(ErrorDeContrato):
        validar(doc)


def test_un_bloque_sin_confianza_se_rechaza():
    # Regla 2 del contrato: la confianza siempre se propaga.
    doc = cargar_ejemplo()
    del doc["bloques"][0]["confianza"]
    with pytest.raises(ErrorDeContrato):
        validar(doc)


def test_una_confianza_fuera_de_rango_se_rechaza():
    doc = cargar_ejemplo()
    doc["bloques"][0]["confianza"] = 1.5
    with pytest.raises(ErrorDeContrato):
        validar(doc)


def test_un_bloque_de_tipo_desconocido_es_valido():
    # Regla 1: el esquema admite tipos nuevos. Quien decide saltarlos es la
    # composicion, no el validador.
    doc = cargar_ejemplo()
    doc["bloques"].append({
        "id": "b9",
        "tipo": "inventado",
        "region": {"x": 0, "y": 0, "ancho": 10, "alto": 10},
        "confianza": 0.5,
        "contenido": {"lo_que_sea": True},
    })
    validar(doc)


def test_una_duda_apunta_a_un_bloque_y_lleva_alternativas():
    doc = cargar_ejemplo()
    doc["dudas"].append({
        "id": "d1",
        "bloque_id": "b2",
        "tipo": "simbolo_ambiguo",
        "region": {"x": 512, "y": 350, "ancho": 40, "alto": 44},
        "descripcion": "El limite superior de la suma",
        "alternativas": [
            {"valor": "6", "probabilidad": 0.55},
            {"valor": "b", "probabilidad": 0.41},
        ],
    })
    validar(doc)


def test_el_documento_no_se_modifica_al_validarlo():
    doc = cargar_ejemplo()
    antes = copy.deepcopy(doc)
    validar(doc)
    assert doc == antes
