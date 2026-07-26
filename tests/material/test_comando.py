import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    shutil.which("tectonic") is None or shutil.which("pdftoppm") is None,
    reason="Tectonic o pdftoppm no estan instalados",
)


def test_invocacion_comando_cuantas_uno(tmp_path):
    salida = tmp_path / "corpus_cmd"
    python_bin = sys.executable

    cmd = [
        python_bin,
        "-m",
        "ctex.material.generar",
        "--cuantas",
        "1",
        "--semilla",
        "42",
        "--salida",
        str(salida),
    ]

    resultado = subprocess.run(cmd, capture_output=True, text=True, check=False)

    assert resultado.returncode == 0
    assert str(salida.resolve()) in resultado.stdout
    assert (salida / "000.png").exists()
    assert (salida / "000.verdad.json").exists()


def test_comando_falla_con_argumentos_invalidos():
    python_bin = sys.executable

    cmd = [
        python_bin,
        "-m",
        "ctex.material.generar",
        "--cuantas",
        "0",
    ]

    resultado = subprocess.run(cmd, capture_output=True, text=True, check=False)

    assert resultado.returncode != 0
    assert resultado.stderr != ""


def test_reproducibilidad_misma_semilla_produce_archivos_identicos(tmp_path):
    salida1 = tmp_path / "run1"
    salida2 = tmp_path / "run2"
    python_bin = sys.executable

    cmd1 = [
        python_bin,
        "-m",
        "ctex.material.generar",
        "--cuantas",
        "2",
        "--semilla",
        "123",
        "--salida",
        str(salida1),
    ]
    cmd2 = [
        python_bin,
        "-m",
        "ctex.material.generar",
        "--cuantas",
        "2",
        "--semilla",
        "123",
        "--salida",
        str(salida2),
    ]

    subprocess.run(cmd1, check=True)
    subprocess.run(cmd2, check=True)

    json1 = (salida1 / "000.verdad.json").read_bytes()
    json2 = (salida2 / "000.verdad.json").read_bytes()
    assert json1 == json2

    png1 = hashlib.sha256((salida1 / "000.png").read_bytes()).hexdigest()
    png2 = hashlib.sha256((salida2 / "000.png").read_bytes()).hexdigest()
    assert png1 == png2
