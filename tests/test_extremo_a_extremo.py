import json
import shutil
from pathlib import Path

import pytest

from ctex.cli import main

DATOS = Path(__file__).parent / "datos"

pytestmark = pytest.mark.skipif(
    shutil.which("tectonic") is None,
    reason="Tectonic no esta instalado",
)


def test_del_json_de_ejemplo_sale_un_pdf(tmp_path):
    codigo = main([str(DATOS / "hoja_ejemplo.json"), "--salida", str(tmp_path)])

    assert codigo == 0
    assert (tmp_path / "documento.pdf").exists()
    assert (tmp_path / "documento.tex").exists()


def test_un_json_invalido_sale_con_codigo_2(tmp_path, capsys):
    invalido = tmp_path / "malo.json"
    invalido.write_text(json.dumps({"version_contrato": "9.9"}), encoding="utf-8")

    codigo = main([str(invalido), "--salida", str(tmp_path / "salida")])

    assert codigo == 2
    assert "invalido" in capsys.readouterr().err.lower()


def test_las_advertencias_se_reportan(tmp_path, capsys):
    with open(DATOS / "hoja_ejemplo.json", encoding="utf-8") as f:
        documento = json.load(f)
    documento["bloques"].append({
        "id": "b9",
        "tipo": "inventado",
        "region": {"x": 0, "y": 0, "ancho": 10, "alto": 10},
        "confianza": 0.5,
        "contenido": {},
    })
    entrada = tmp_path / "con_desconocido.json"
    entrada.write_text(json.dumps(documento), encoding="utf-8")

    codigo = main([str(entrada), "--salida", str(tmp_path / "salida")])

    assert codigo == 0
    assert "inventado" in capsys.readouterr().err
