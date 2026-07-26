"""Generador de punta a punta del corpus sintético nivel -1 (Tarea 4)."""

import json
import tempfile
from pathlib import Path

from ctex.compilacion.tectonic import compilar
from ctex.composicion.bloques import componer_grafica
from ctex.contrato.validador import validar
from ctex.material.contrato import definicion_a_contrato
from ctex.material.definicion import FAMILIAS, generar_definicion
from ctex.material.plantilla import (
    envolver_standalone,
    extraer_tikzpicture,
    quitar_leyenda,
)
from ctex.material.rasterizador import rasterizar_pdf


def generar_corpus(
    cuantas: int, semilla: int, carpeta_salida: Path
) -> list[tuple[Path, Path]]:
    """Genera el corpus de pares (PNG, verdad.json) sinteticos.

    Args:
        cuantas: Numero de pares a generar.
        semilla: Semilla base para determinismo.
        carpeta_salida: Directorio donde se guardaran los archivos.

    Returns:
        Lista de tuplas (ruta_png, ruta_json).
    """
    carpeta_salida = Path(carpeta_salida)
    carpeta_salida.mkdir(parents=True, exist_ok=True)

    resultados: list[tuple[Path, Path]] = []

    for i in range(cuantas):
        prefijo = f"{i:03d}"
        familia = FAMILIAS[i % len(FAMILIAS)]
        sub_semilla = semilla + i

        definicion = generar_definicion(familia=familia, semilla=sub_semilla)
        doc_contrato = definicion_a_contrato(definicion, nombre_archivo=f"{prefijo}.png")
        validar(doc_contrato)

        bloque_grafica = doc_contrato["bloques"][0]["contenido"]
        fragmento = componer_grafica(bloque_grafica)
        tikz = quitar_leyenda(extraer_tikzpicture(fragmento))
        tex = envolver_standalone(tikz)

        with tempfile.TemporaryDirectory() as dir_temp:
            dir_temp_path = Path(dir_temp)
            pdf_path = compilar(tex, dir_temp_path)

            png_path = carpeta_salida / f"{prefijo}.png"
            rasterizar_pdf(pdf_path, ppp=200, ruta_salida=png_path)

        verdad = {
            "familia": definicion["familia"],
            "semilla": definicion["semilla"],
            "ejes": definicion["ejes"],
            "puntos": definicion["series"][0]["puntos"],
        }

        json_path = carpeta_salida / f"{prefijo}.verdad.json"
        json_path.write_text(
            json.dumps(verdad, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        resultados.append((png_path, json_path))

    return resultados
