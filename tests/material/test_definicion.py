import pytest

from ctex.material.definicion import FAMILIAS, generar_definicion


def test_familias_disponibles():
    assert "lineal" in FAMILIAS
    assert "exponencial_decreciente" in FAMILIAS
    assert "senoidal" in FAMILIAS

    for familia in FAMILIAS:
        def_grafica = generar_definicion(familia=familia, semilla=42)
        assert def_grafica["familia"] == familia
        assert len(def_grafica["series"][0]["puntos"]) > 0


def test_puntos_caen_dentro_de_ejes():
    for familia in FAMILIAS:
        for semilla in range(10):
            def_grafica = generar_definicion(familia=familia, semilla=semilla)
            eje_x = def_grafica["ejes"]["x"]
            eje_y = def_grafica["ejes"]["y"]
            puntos = def_grafica["series"][0]["puntos"]

            for x, y in puntos:
                assert eje_x["min"] <= x <= eje_x["max"]
                assert eje_y["min"] <= y <= eje_y["max"]


def test_misma_semilla_da_misma_definicion():
    def1 = generar_definicion(familia="lineal", semilla=12345)
    def2 = generar_definicion(familia="lineal", semilla=12345)
    assert def1 == def2

    def3 = generar_definicion(familia="senoidal", semilla=999)
    def4 = generar_definicion(familia="senoidal", semilla=999)
    assert def3 == def4


def test_semilla_diferente_da_definicion_diferente():
    def1 = generar_definicion(familia="lineal", semilla=1)
    def2 = generar_definicion(familia="lineal", semilla=2)
    assert def1["series"][0]["puntos"] != def2["series"][0]["puntos"]
