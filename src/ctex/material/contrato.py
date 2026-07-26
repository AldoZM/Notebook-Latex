"""Conversion de una definicion de grafica sintetica a documento del contrato."""


def definicion_a_contrato(definicion: dict, nombre_archivo: str = "sintetico.png") -> dict:
    """Convierte una definicion de grafica en un documento del contrato valido (v1.0).

    Args:
        definicion: Diccionario producido por `generar_definicion`.
        nombre_archivo: Nombre del archivo de imagen de origen ficticio.

    Returns:
        Diccionario que representa un documento de contrato con un bloque 'grafica'.
    """
    contenido_grafica = {
        "tipo_grafica": definicion.get("tipo_grafica", "lineas"),
        "titulo": definicion.get("titulo", "Grafica sintetica"),
        "ejes": definicion["ejes"],
        "series": definicion["series"],
    }

    return {
        "version_contrato": "1.0",
        "origen": {
            "archivo": nombre_archivo,
            "pagina": 1,
        },
        "bloques": [
            {
                "id": "b1",
                "tipo": "grafica",
                "region": {
                    "x": 0,
                    "y": 0,
                    "ancho": 800,
                    "alto": 600,
                },
                "confianza": 1.0,
                "contenido": contenido_grafica,
            }
        ],
        "dudas": [],
    }
