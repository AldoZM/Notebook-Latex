"""Validacion de documentos contra el esquema del contrato."""

import json
from functools import lru_cache
from pathlib import Path

import jsonschema

VERSION_SOPORTADA = "1.0"

_RUTA_ESQUEMA = Path(__file__).parent / "esquema.json"


class ErrorDeContrato(Exception):
    """El documento no cumple el esquema del contrato."""


@lru_cache(maxsize=1)
def _esquema() -> dict:
    with open(_RUTA_ESQUEMA, encoding="utf-8") as f:
        return json.load(f)


def validar(documento: dict) -> None:
    """Valida un documento. Lanza ErrorDeContrato si no cumple.

    No modifica el documento y no devuelve nada: o pasa, o levanta.
    """
    try:
        jsonschema.validate(instance=documento, schema=_esquema())
    except jsonschema.ValidationError as error:
        ruta = "/".join(str(parte) for parte in error.absolute_path)
        ubicacion = f" en '{ruta}'" if ruta else ""
        raise ErrorDeContrato(f"Documento invalido{ubicacion}: {error.message}") from error
