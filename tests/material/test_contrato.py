import pytest

from ctex.contrato.validador import validar
from ctex.material.contrato import definicion_a_contrato
from ctex.material.definicion import FAMILIAS, generar_definicion


def test_definicion_a_contrato_valida_con_esquema():
    for familia in FAMILIAS:
        definicion = generar_definicion(familia=familia, semilla=42)
        doc = definicion_a_contrato(definicion)
        # validar no debe lanzar ErrorDeContrato
        validar(doc)


def test_estructura_del_documento_generado():
    definicion = generar_definicion(familia="lineal", semilla=7)
    doc = definicion_a_contrato(definicion, nombre_archivo="test_000.png")

    assert doc["version_contrato"] == "1.0"
    assert doc["origen"]["archivo"] == "test_000.png"
    assert len(doc["bloques"]) == 1

    bloque = doc["bloques"][0]
    assert bloque["tipo"] == "grafica"
    assert bloque["id"] == "b1"
    assert "region" in bloque
    assert "confianza" in bloque

    contenido = bloque["contenido"]
    assert contenido["tipo_grafica"] == "lineas"
    assert "titulo" in contenido
    assert "x" in contenido["ejes"]
    assert "y" in contenido["ejes"]

    for eje_nombre in ("x", "y"):
        eje = contenido["ejes"][eje_nombre]
        assert "min" in eje
        assert "max" in eje
        assert "etiqueta" in eje
        assert "escala" in eje

    assert len(contenido["series"]) == 1
    assert contenido["series"][0]["puntos"] == definicion["series"][0]["puntos"]
