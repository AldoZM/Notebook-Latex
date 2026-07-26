# src/ctex/extraccion/cli.py
"""El comando `ctex-extraer` (D39).

    ctex-extraer recorte.png --escala-x 0,10 --escala-y -1,1 --salida hoja.json

Codigos de salida (D47): 0 salio; 2 argumentos malos; 3 no hubo marco;
4 hubo marco pero no curva.
"""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from ctex.extraccion.escala import ErrorDeEscala
from ctex.extraccion.extractor import extraer
from ctex.extraccion.marco import ErrorDeMarco
from ctex.extraccion.remuestreo import ErrorDeRemuestreo
from ctex.extraccion.tinta import ErrorDeTinta


def _rango(texto: str) -> tuple[float, float]:
    partes = texto.split(",")
    if len(partes) != 2:
        raise argparse.ArgumentTypeError(
            f"Un rango se escribe como 'min,max'; se recibio '{texto}'"
        )
    try:
        return float(partes[0]), float(partes[1])
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Los dos extremos del rango tienen que ser numeros: '{texto}'"
        ) from None


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(
        prog="ctex-extraer",
        description="Convierte un recorte de grafica en un documento del contrato.",
    )
    analizador.add_argument("entrada", type=Path, help="Recorte de la grafica")
    analizador.add_argument("--escala-x", type=_rango, required=True,
                            help="Rango del eje X como min,max")
    analizador.add_argument("--escala-y", type=_rango, required=True,
                            help="Rango del eje Y como min,max")
    analizador.add_argument("--salida", type=Path, default=Path("hoja.json"))
    analizador.add_argument("--traza", type=Path, default=None,
                            help="Si se da, escribe ahi los intermedios")
    analizador.add_argument("--puntos", type=int, default=30,
                            help="Cuantos puntos tiene la serie de salida")
    argumentos = analizador.parse_args(argv)

    try:
        documento, traza = extraer(
            argumentos.entrada,
            argumentos.escala_x,
            argumentos.escala_y,
            argumentos.puntos,
        )
    except (ErrorDeEscala, FileNotFoundError) as error:
        print(f"Argumentos invalidos: {error}", file=sys.stderr)
        return 2
    except ErrorDeMarco as error:
        print(f"No se encontro el marco de la grafica: {error}", file=sys.stderr)
        return 3
    except (ErrorDeTinta, ErrorDeRemuestreo) as error:
        print(f"Se encontro el marco pero no la curva: {error}", file=sys.stderr)
        return 4

    argumentos.salida.parent.mkdir(parents=True, exist_ok=True)
    argumentos.salida.write_text(
        json.dumps(documento, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    if argumentos.traza is not None:
        resumen = {
            "caja": asdict(traza.caja),
            "transformacion": asdict(traza.transformacion),
            "columnas_validas": int(traza.validez.sum()),
            "columnas_totales": int(traza.validez.size),
            "puntos": traza.puntos,
        }
        argumentos.traza.write_text(
            json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    print(argumentos.salida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
