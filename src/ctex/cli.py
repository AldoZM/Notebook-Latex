"""El motor por linea de comandos (D9).

    ctex hoja.json --salida ./salida
"""

import argparse
import json
import sys
from pathlib import Path

from ctex.compilacion.tectonic import ErrorDeCompilacion, compilar
from ctex.composicion.compositor import componer
from ctex.contrato.validador import ErrorDeContrato, validar


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(
        prog="ctex",
        description="Convierte un documento del contrato en un PDF compuesto con LaTeX.",
    )
    analizador.add_argument("entrada", type=Path, help="Archivo JSON del contrato")
    analizador.add_argument(
        "--salida", type=Path, default=Path("salida"),
        help="Carpeta donde se escriben el PDF y el .tex",
    )
    argumentos = analizador.parse_args(argv)

    with open(argumentos.entrada, encoding="utf-8") as archivo:
        documento = json.load(archivo)

    try:
        validar(documento)
    except ErrorDeContrato as error:
        print(f"Documento invalido: {error}", file=sys.stderr)
        return 2

    tex, advertencias = componer(documento)
    for advertencia in advertencias:
        print(f"Advertencia: {advertencia}", file=sys.stderr)

    try:
        pdf = compilar(tex, argumentos.salida)
    except ErrorDeCompilacion as error:
        print(f"No compilo: {error}", file=sys.stderr)
        if error.registro:
            print(error.registro, file=sys.stderr)
        return 3

    print(pdf)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
