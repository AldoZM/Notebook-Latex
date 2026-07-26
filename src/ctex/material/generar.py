"""CLI del generador de material de prueba nivel -1 (Tarea 5)."""

import argparse
import sys
from pathlib import Path

from ctex.material.generador import generar_corpus


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generador de material sintético de prueba (nivel -1)."
    )
    parser.add_argument(
        "--cuantas",
        type=int,
        default=5,
        help="Número de pares (PNG, verdad.json) a generar.",
    )
    parser.add_argument(
        "--semilla",
        type=int,
        default=1,
        help="Semilla entera para determinismo.",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=Path("./corpus/nivel-menos-1"),
        help="Carpeta de salida para el corpus.",
    )

    args = parser.parse_args(argv)

    if args.cuantas <= 0:
        sys.stderr.write("Error: --cuantas debe ser un entero mayor que 0.\n")
        return 1

    try:
        salida = Path(args.salida)
        generar_corpus(
            cuantas=args.cuantas,
            semilla=args.semilla,
            carpeta_salida=salida,
        )
        print(str(salida.resolve()))
        return 0
    except Exception as error:
        sys.stderr.write(f"Error al generar material: {error}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
