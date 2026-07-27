"""De las partes clasificadas al documento del contrato v1.0."""

from pathlib import Path

from ctex.libro.estructura import Parte

# Mismo criterio que D44 en el extractor: aqui tampoco hay medicion de
# confianza, y un numero inventado que parezca significar algo es peor que uno
# que declare que no mide nada.
CONFIANZA_MARCADOR = 0.5


def a_contrato(partes: list[Parte], archivo: Path, pagina: int) -> dict:
    """Arma el documento del contrato a partir de las partes clasificadas."""
    bloques = []
    for indice, parte in enumerate(partes, start=1):
        if parte.tipo == "titulo":
            contenido = {"nivel": parte.nivel, "texto": parte.texto}
        elif parte.tipo == "tabla":
            # Sin encabezado: de la geometria no se puede saber si la primera
            # fila es titulo de columna o un dato mas, y marcarla de mas seria
            # inventar. Si el compositor no recibe encabezado, no dibuja regla
            # doble.
            contenido = {"filas": [list(fila) for fila in parte.filas]}
        else:
            contenido = {"texto": parte.texto}
        bloques.append(
            {
                "id": f"b{indice}",
                "tipo": parte.tipo,
                # La region es un marcador: el contrato la exige y aqui todavia
                # no se arrastra la caja real de cada bloque. Cuando haga falta
                # para senalar dudas sobre la pagina, saldra de Bloque.
                "region": {"x": 0, "y": indice * 10, "ancho": 1, "alto": 1},
                "confianza": CONFIANZA_MARCADOR,
                "contenido": contenido,
            }
        )

    return {
        "version_contrato": "1.0",
        "origen": {"archivo": Path(archivo).name, "pagina": pagina},
        "bloques": bloques,
        "dudas": [],
    }
