"""El comando `ctex-libro`.

    ctex-libro "libro.pdf" --paginas 40-44 --salida hoja.json

Codigos de salida, con la convencion del resto del motor:
    0  salio el contrato
    2  argumentos malos, o el PDF no existe
    3  el PDF no tiene capa de texto
    4  no quedo ningun bloque despues de quitar encabezados y pies
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from ctex.libro.contrato import a_contrato
from ctex.libro.estructura import clasificar
from ctex.libro.paginas import ErrorDeLectura, leer


def _rango(texto: str) -> tuple[int, int]:
    partes = texto.split("-")
    try:
        if len(partes) == 1:
            unica = int(partes[0])
            return unica, unica
        if len(partes) == 2:
            primera, ultima = int(partes[0]), int(partes[1])
            if ultima < primera:
                raise ValueError
            return primera, ultima
    except ValueError:
        pass
    raise argparse.ArgumentTypeError(
        f"Las paginas se escriben como '40' o '40-44'; se recibio '{texto}'"
    )


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(
        prog="ctex-libro",
        description="Convierte paginas de un PDF con capa de texto en un documento del contrato.",
    )
    analizador.add_argument("entrada", type=Path, help="PDF del libro")
    analizador.add_argument("--paginas", type=_rango, required=True,
                            help="Una pagina (40) o un rango (40-44)")
    analizador.add_argument("--salida", type=Path, default=Path("hoja.json"))
    argumentos = analizador.parse_args(argv)

    primera, ultima = argumentos.paginas

    try:
        paginas = leer(argumentos.entrada, primera, ultima)
    except ErrorDeLectura as error:
        # Un PDF que no existe y uno sin capa de texto son fallas distintas y
        # se arreglan con cosas distintas, asi que salen con codigos distintos.
        if not argumentos.entrada.exists():
            print(f"Argumentos invalidos: {error}", file=sys.stderr)
            return 2
        print(f"No se pudo leer el texto del PDF: {error}", file=sys.stderr)
        return 3

    partes = clasificar(paginas)
    if not partes:
        print(
            "No quedo ningun bloque despues de quitar encabezados y pies",
            file=sys.stderr,
        )
        return 4

    documento = a_contrato(partes, argumentos.entrada, primera)

    argumentos.salida.parent.mkdir(parents=True, exist_ok=True)
    argumentos.salida.write_text(
        json.dumps(documento, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    cuenta = Counter(parte.tipo for parte in partes)
    detalle = ", ".join(f"{cuantos} {tipo}" for tipo, cuantos in sorted(cuenta.items()))
    print(f"{argumentos.salida}  ({len(partes)} bloques: {detalle})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
