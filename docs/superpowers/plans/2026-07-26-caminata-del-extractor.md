# Caminata esquelética del extractor — plan de implementación

> **Para trabajadores agénticos:** SUB-SKILL REQUERIDA: usar
> superpowers:subagent-driven-development (recomendada) o
> superpowers:executing-plans para implementar este plan tarea por tarea. Los
> pasos usan casillas (`- [ ]`) para el seguimiento.

**Objetivo:** que una imagen de gráfica entre por un extremo y salga un
documento del contrato válido por el otro, atravesando los siete pasos con la
versión más delgada posible de cada uno.

**Arquitectura:** un módulo por paso bajo `src/ctex/extraccion/`, encadenados por
`extractor.py` y expuestos por `ctex-extraer`. Cada paso es una función pura que
recibe y devuelve datos, sin estado. OpenCV queda confinado a `marco.py` y
`tinta.py`; el rastreo es solo NumPy.

**Pila:** Python 3.11+, NumPy, OpenCV, `jsonschema` (ya presente), pytest.

**Especificación:** [`2026-07-26-extractor-graficas-design.md`](../specs/2026-07-26-extractor-graficas-design.md)

## Restricciones globales

- **No se modifica** `src/ctex/contrato/`, `src/ctex/composicion/`,
  `src/ctex/compilacion/` ni `src/ctex/material/`. Se importan y se usan.
- **Las 107 pruebas existentes siguen pasando.** Sin excepción.
- **En Python nunca se recorre píxel por píxel** (D11). La operación se expresa
  sobre el arreglo completo.
- **Nada de OpenCV cruza hacia afuera** de `marco.py` y `tinta.py`.
- **El entorno virtual es `.venv`.** Usar `.venv\Scripts\python.exe`.
- Comentarios y nombres en español, como el resto del código.
- **Sin firma de IA ni `Co-Authored-By`** en los commits.

## Qué queda fuera de esta caminata

Se construye después, con su propio plan. No es olvido:

| Fuera | Por qué |
|---|---|
| `rectificacion.py` (D40) | Sobre material del nivel −1 es identidad: pgfplots dibuja los ejes perfectamente rectos. Entra cuando entre el nivel 0, que es el que trae inclinación |
| Cierre morfológico y rellenos (D45) | Requieren que el barrido exista primero |
| Detección de saltos (D47) | Igual |
| Umbrales de fallo (D47) | El 30% es una conjetura que se calibra **con** esta caminata corriendo |
| Caja en L, sin recuadro | El nivel −1 siempre trae recuadro completo. La versión estricta basta y falla ruidosamente |
| `ctex-medir` | Fase 2 |

## Estructura de archivos

```
src/ctex/extraccion/
    __init__.py        vacío
    tipos.py           Recta, Caja, Transformacion, Traza
    marco.py           imagen -> Caja
    escala.py          Caja + rangos -> Transformacion
    tinta.py           imagen + Caja -> máscara booleana
    rastreo.py         máscara -> centroides + validez
    remuestreo.py      centroides válidos -> N puntos
    extractor.py       la tubería + el documento del contrato
    cli.py             ctex-extraer

tests/extraccion/
    test_tipos.py  test_marco.py  test_escala.py  test_tinta.py
    test_rastreo.py  test_remuestreo.py  test_extractor.py  test_cli.py
```

---

### Tarea 1: Andamiaje y tipos

**Archivos:**
- Crear: `src/ctex/extraccion/__init__.py` (vacío)
- Crear: `src/ctex/extraccion/tipos.py`
- Crear: `tests/extraccion/test_tipos.py`
- Modificar: `pyproject.toml`

**Interfaces:**
- Consume: nada.
- Produce: `Recta(rho, theta)`, `Caja(izquierda, derecha, arriba, abajo)`,
  `Transformacion(escala_x, escala_y, izquierda, arriba)` con métodos
  `a_valor_x(columna) -> float` y `a_valor_y(fila) -> float`, y
  `Traza(caja, transformacion, centroides, validez, puntos)`.

- [ ] **Paso 1: Escribir la prueba que falla**

```python
# tests/extraccion/test_tipos.py
import pytest

from ctex.extraccion.tipos import Caja, Recta, Transformacion


def test_una_caja_conoce_su_ancho_y_su_alto():
    caja = Caja(izquierda=10.0, derecha=110.0, arriba=20.0, abajo=220.0)
    assert caja.ancho == 100.0
    assert caja.alto == 200.0


def test_una_caja_invertida_se_rechaza():
    with pytest.raises(ValueError):
        Caja(izquierda=110.0, derecha=10.0, arriba=20.0, abajo=220.0)


def test_la_transformacion_lleva_columna_a_valor():
    t = Transformacion(escala_x=0.1, escala_y=0.05, izquierda=10.0, arriba=20.0)
    assert t.a_valor_x(10.0) == pytest.approx(0.0)
    assert t.a_valor_x(110.0) == pytest.approx(10.0)


def test_el_eje_y_va_al_reves_que_las_filas():
    # ymax esta ARRIBA en la grafica, pero la fila 0 esta arriba en la imagen.
    t = Transformacion(escala_x=0.1, escala_y=0.05, izquierda=10.0, arriba=20.0)
    t = t.con_ymax(11.0)
    assert t.a_valor_y(20.0) == pytest.approx(11.0)   # fila de arriba -> ymax
    assert t.a_valor_y(220.0) == pytest.approx(1.0)   # 11 - 200*0.05


def test_una_recta_guarda_rho_y_theta():
    r = Recta(rho=42.0, theta=0.0)
    assert r.rho == 42.0
    assert r.theta == 0.0
```

- [ ] **Paso 2: Correr para verificar que falla**

Correr: `.venv\Scripts\python.exe -m pytest tests/extraccion/test_tipos.py -v`
Esperado: FALLA con `ModuleNotFoundError: No module named 'ctex.extraccion'`

- [ ] **Paso 3: Escribir la implementación mínima**

```python
# src/ctex/extraccion/tipos.py
"""Los tipos que cruzan las fronteras del extractor.

Ninguno depende de OpenCV: son datos, no imagenes.
"""

from dataclasses import dataclass, field, replace


@dataclass(frozen=True)
class Recta:
    """Una recta en la forma de Hough: distancia al origen y angulo normal."""

    rho: float
    theta: float


@dataclass(frozen=True)
class Caja:
    """Los cuatro bordes del area de la grafica, en pixeles.

    El borde izquierdo vale xmin y el derecho xmax; el inferior ymin y el
    superior ymax. Es lo que ancla la escala: dos rectas infinitas no bastan.
    """

    izquierda: float
    derecha: float
    arriba: float
    abajo: float

    def __post_init__(self) -> None:
        if self.derecha <= self.izquierda:
            raise ValueError(
                f"Caja invalida: derecha ({self.derecha}) no es mayor que "
                f"izquierda ({self.izquierda})"
            )
        if self.abajo <= self.arriba:
            raise ValueError(
                f"Caja invalida: abajo ({self.abajo}) no es mayor que "
                f"arriba ({self.arriba})"
            )

    @property
    def ancho(self) -> float:
        return self.derecha - self.izquierda

    @property
    def alto(self) -> float:
        return self.abajo - self.arriba


@dataclass(frozen=True)
class Transformacion:
    """Convierte coordenadas de pixel a valores de la grafica."""

    escala_x: float
    escala_y: float
    izquierda: float
    arriba: float
    xmin: float = 0.0
    ymax: float = 0.0

    def con_ymax(self, ymax: float) -> "Transformacion":
        return replace(self, ymax=ymax)

    def con_xmin(self, xmin: float) -> "Transformacion":
        return replace(self, xmin=xmin)

    def a_valor_x(self, columna: float) -> float:
        return self.xmin + (columna - self.izquierda) * self.escala_x

    def a_valor_y(self, fila: float) -> float:
        # Resta y no suma: la fila 0 esta arriba en la imagen, y arriba esta
        # ymax en la grafica. Invertir este signo produce una curva reflejada
        # que sigue pareciendo una curva, asi que no se nota.
        return self.ymax - (fila - self.arriba) * self.escala_y


@dataclass
class Traza:
    """Los intermedios de los siete pasos, para depurar y para medir (D43)."""

    caja: Caja | None = None
    transformacion: Transformacion | None = None
    centroides: object = None
    validez: object = None
    puntos: list = field(default_factory=list)
```

- [ ] **Paso 4: Correr para verificar que pasa**

Correr: `.venv\Scripts\python.exe -m pytest tests/extraccion/test_tipos.py -v`
Esperado: PASAN las 5

- [ ] **Paso 5: Agregar las dependencias**

En `pyproject.toml`, dejar la sección `dependencies` así:

```toml
dependencies = [
    "jsonschema>=4.20",
    "numpy>=1.26",
    "opencv-python-headless>=4.9",
]
```

Se usa `opencv-python-headless` y no `opencv-python`: no se necesita interfaz
gráfica, y la variante sin ella pesa mucho menos, lo que va a importar cuando se
arme la imagen de despliegue.

Luego reinstalar: `.venv\Scripts\python.exe -m pip install -e ".[dev]"`

- [ ] **Paso 6: Correr la suite completa**

Correr: `.venv\Scripts\python.exe -m pytest -q`
Esperado: 112 passed (107 previas + 5 nuevas)

- [ ] **Paso 7: Comprometer**

```bash
git add src/ctex/extraccion tests/extraccion pyproject.toml
git commit -m "Extraccion: tipos del extractor y dependencias de vision"
```

---

### Tarea 2: `marco.py` — la caja

**Archivos:**
- Crear: `src/ctex/extraccion/marco.py`
- Crear: `tests/extraccion/test_marco.py`

**Interfaces:**
- Consume: `Caja`, `Recta` de `tipos.py`.
- Produce: `detectar_caja(imagen: np.ndarray) -> Caja` y la excepción
  `ErrorDeMarco`.

- [ ] **Paso 1: Escribir la prueba que falla**

```python
# tests/extraccion/test_marco.py
import numpy as np
import pytest

from ctex.extraccion.marco import ErrorDeMarco, detectar_caja


def imagen_con_recuadro(ancho=200, alto=160, borde=20):
    """Papel blanco con un recuadro negro de un pixel de grosor."""
    imagen = np.full((alto, ancho), 255, dtype=np.uint8)
    imagen[borde, borde : ancho - borde] = 0          # arriba
    imagen[alto - borde, borde : ancho - borde] = 0   # abajo
    imagen[borde : alto - borde, borde] = 0           # izquierda
    imagen[borde : alto - borde, ancho - borde] = 0   # derecha
    return imagen


def test_encuentra_los_cuatro_bordes_de_un_recuadro():
    caja = detectar_caja(imagen_con_recuadro())
    assert caja.izquierda == pytest.approx(20, abs=2)
    assert caja.derecha == pytest.approx(180, abs=2)
    assert caja.arriba == pytest.approx(20, abs=2)
    assert caja.abajo == pytest.approx(140, abs=2)


def test_una_imagen_en_blanco_no_tiene_marco():
    blanca = np.full((160, 200), 255, dtype=np.uint8)
    with pytest.raises(ErrorDeMarco):
        detectar_caja(blanca)


def test_una_sola_raya_no_alcanza_para_una_caja():
    imagen = np.full((160, 200), 255, dtype=np.uint8)
    imagen[80, :] = 0
    with pytest.raises(ErrorDeMarco):
        detectar_caja(imagen)
```

- [ ] **Paso 2: Correr para verificar que falla**

Correr: `.venv\Scripts\python.exe -m pytest tests/extraccion/test_marco.py -v`
Esperado: FALLA con `ModuleNotFoundError: No module named 'ctex.extraccion.marco'`

- [ ] **Paso 3: Escribir la implementación mínima**

```python
# src/ctex/extraccion/marco.py
"""Paso 1: encontrar la caja del area de la grafica.

OpenCV se queda aqui dentro: hacia afuera solo salen Caja y Recta.
"""

import cv2
import numpy as np

from ctex.extraccion.tipos import Caja, Recta

# Cuanto puede desviarse una recta de la horizontal o la vertical para seguir
# contando como tal. 5 grados: mas que eso ya no es un eje de una grafica.
TOLERANCIA = np.deg2rad(5)


class ErrorDeMarco(Exception):
    """No se pudo formar la caja del area de la grafica."""


def binarizar(imagen: np.ndarray) -> np.ndarray:
    """Deja la tinta en blanco y el papel en negro, que es lo que Hough espera."""
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY) if imagen.ndim == 3 else imagen
    _, binaria = cv2.threshold(
        gris, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    return binaria


def _clasificar(lineas: np.ndarray) -> tuple[list[float], list[float]]:
    """Separa las rectas en posiciones de verticales y de horizontales.

    El punto de la recta mas cercano al origen es (rho*cos(theta),
    rho*sin(theta)). Para una casi vertical, esa x es su posicion; para una
    casi horizontal, esa y lo es.
    """
    equis: list[float] = []
    yes: list[float] = []
    for (rho, theta), in lineas:
        if theta < TOLERANCIA or theta > np.pi - TOLERANCIA:
            equis.append(abs(rho * np.cos(theta)))
        elif abs(theta - np.pi / 2) < TOLERANCIA:
            yes.append(abs(rho * np.sin(theta)))
    return equis, yes


def detectar_caja(imagen: np.ndarray) -> Caja:
    """Devuelve los cuatro bordes del area de la grafica."""
    binaria = binarizar(imagen)
    alto, ancho = binaria.shape

    # Un eje cruza buena parte de la imagen. Pedir la mitad del lado menor deja
    # fuera el ruido y las lineas cortas sin dejar fuera los ejes.
    umbral = max(int(min(alto, ancho) * 0.5), 10)
    lineas = cv2.HoughLines(binaria, 1, np.pi / 180, umbral)

    if lineas is None:
        raise ErrorDeMarco("Hough no encontro ninguna recta larga en la imagen")

    equis, yes = _clasificar(lineas)

    if len(equis) < 2 or len(yes) < 2:
        raise ErrorDeMarco(
            f"No hay dos verticales y dos horizontales: se encontraron "
            f"{len(equis)} verticales y {len(yes)} horizontales"
        )

    return Caja(
        izquierda=min(equis),
        derecha=max(equis),
        arriba=min(yes),
        abajo=max(yes),
    )
```

- [ ] **Paso 4: Correr para verificar que pasa**

Correr: `.venv\Scripts\python.exe -m pytest tests/extraccion/test_marco.py -v`
Esperado: PASAN las 3

- [ ] **Paso 5: Comprometer**

```bash
git add src/ctex/extraccion/marco.py tests/extraccion/test_marco.py
git commit -m "Extraccion: la caja del area de la grafica, con Hough"
```

---

### Tarea 3: `escala.py` — de la caja a la transformación

**Archivos:**
- Crear: `src/ctex/extraccion/escala.py`
- Crear: `tests/extraccion/test_escala.py`

**Interfaces:**
- Consume: `Caja`, `Transformacion` de `tipos.py`.
- Produce: `fijar_escala(caja: Caja, rango_x: tuple[float, float],
  rango_y: tuple[float, float]) -> Transformacion` y `ErrorDeEscala`.

- [ ] **Paso 1: Escribir la prueba que falla**

```python
# tests/extraccion/test_escala.py
import pytest

from ctex.extraccion.escala import ErrorDeEscala, fijar_escala
from ctex.extraccion.tipos import Caja


def caja_de_prueba():
    # 100 px de ancho, 200 px de alto
    return Caja(izquierda=10.0, derecha=110.0, arriba=20.0, abajo=220.0)


def test_los_bordes_de_la_caja_valen_los_extremos_del_rango():
    t = fijar_escala(caja_de_prueba(), (0.0, 10.0), (-1.0, 1.0))
    assert t.a_valor_x(10.0) == pytest.approx(0.0)
    assert t.a_valor_x(110.0) == pytest.approx(10.0)
    assert t.a_valor_y(20.0) == pytest.approx(1.0)    # arriba -> ymax
    assert t.a_valor_y(220.0) == pytest.approx(-1.0)  # abajo -> ymin


def test_el_centro_de_la_caja_es_el_centro_del_rango():
    t = fijar_escala(caja_de_prueba(), (0.0, 10.0), (-1.0, 1.0))
    assert t.a_valor_x(60.0) == pytest.approx(5.0)
    assert t.a_valor_y(120.0) == pytest.approx(0.0)


def test_un_rango_invertido_se_rechaza():
    with pytest.raises(ErrorDeEscala):
        fijar_escala(caja_de_prueba(), (10.0, 0.0), (-1.0, 1.0))


def test_un_rango_de_ancho_cero_se_rechaza():
    with pytest.raises(ErrorDeEscala):
        fijar_escala(caja_de_prueba(), (5.0, 5.0), (-1.0, 1.0))
```

- [ ] **Paso 2: Correr para verificar que falla**

Correr: `.venv\Scripts\python.exe -m pytest tests/extraccion/test_escala.py -v`
Esperado: FALLA con `ModuleNotFoundError`

- [ ] **Paso 3: Escribir la implementación mínima**

```python
# src/ctex/extraccion/escala.py
"""Paso 3: de la caja y los rangos tecleados a la transformacion.

Aritmetica pura. La escala no se lee de la imagen, se recibe (D34).
"""

from ctex.extraccion.tipos import Caja, Transformacion


class ErrorDeEscala(Exception):
    """Los rangos dados no sirven para construir una transformacion."""


def _validar(rango: tuple[float, float], nombre: str) -> None:
    minimo, maximo = rango
    if maximo <= minimo:
        raise ErrorDeEscala(
            f"El rango de {nombre} va de {minimo} a {maximo}: "
            f"el maximo tiene que ser mayor que el minimo"
        )


def fijar_escala(
    caja: Caja,
    rango_x: tuple[float, float],
    rango_y: tuple[float, float],
) -> Transformacion:
    """Construye la conversion de pixel a valor a partir de la caja."""
    _validar(rango_x, "x")
    _validar(rango_y, "y")

    xmin, xmax = rango_x
    ymin, ymax = rango_y

    return Transformacion(
        escala_x=(xmax - xmin) / caja.ancho,
        escala_y=(ymax - ymin) / caja.alto,
        izquierda=caja.izquierda,
        arriba=caja.arriba,
        xmin=xmin,
        ymax=ymax,
    )
```

- [ ] **Paso 4: Correr para verificar que pasa**

Correr: `.venv\Scripts\python.exe -m pytest tests/extraccion/test_escala.py -v`
Esperado: PASAN las 4

- [ ] **Paso 5: Comprometer**

```bash
git add src/ctex/extraccion/escala.py tests/extraccion/test_escala.py
git commit -m "Extraccion: la escala sale de la caja y de los rangos tecleados"
```

---

### Tarea 4: `tinta.py` — aislar la curva

**Archivos:**
- Crear: `src/ctex/extraccion/tinta.py`
- Crear: `tests/extraccion/test_tinta.py`

**Interfaces:**
- Consume: `Caja` de `tipos.py`.
- Produce: `aislar_curva(imagen: np.ndarray, caja: Caja) -> np.ndarray`, que
  devuelve una máscara booleana **del tamaño de la imagen completa**, y
  `ErrorDeTinta`.

La máscara conserva el tamaño de la imagen para que las columnas del barrido
sigan siendo columnas de la imagen, y así la transformación de `escala.py`
aplique sin corrimientos.

- [ ] **Paso 1: Escribir la prueba que falla**

```python
# tests/extraccion/test_tinta.py
import numpy as np
import pytest

from ctex.extraccion.tinta import ErrorDeTinta, aislar_curva
from ctex.extraccion.tipos import Caja


def imagen_con_recuadro_y_curva():
    """Recuadro negro, rejilla gris clara, y una diagonal negra dentro."""
    imagen = np.full((160, 200), 255, dtype=np.uint8)
    imagen[20, 20:180] = 0
    imagen[140, 20:180] = 0
    imagen[20:140, 20] = 0
    imagen[20:140, 180] = 0
    for x in range(40, 180, 20):        # rejilla clara
        imagen[21:140, x] = 200
    for i in range(100):                # la curva
        imagen[30 + i, 30 + i] = 0
    return imagen


CAJA = Caja(izquierda=20.0, derecha=180.0, arriba=20.0, abajo=140.0)


def test_la_curva_sobrevive():
    mascara = aislar_curva(imagen_con_recuadro_y_curva(), CAJA)
    assert mascara[80, 80]


def test_la_rejilla_clara_no_sobrevive():
    mascara = aislar_curva(imagen_con_recuadro_y_curva(), CAJA)
    assert not mascara[100, 60]


def test_los_bordes_de_la_caja_no_sobreviven():
    mascara = aislar_curva(imagen_con_recuadro_y_curva(), CAJA)
    assert not mascara[:, 20].any()
    assert not mascara[20, :].any()


def test_la_mascara_conserva_el_tamano_de_la_imagen():
    imagen = imagen_con_recuadro_y_curva()
    assert aislar_curva(imagen, CAJA).shape == imagen.shape


def test_sin_curva_dentro_de_la_caja_levanta():
    vacia = np.full((160, 200), 255, dtype=np.uint8)
    vacia[20, 20:180] = 0
    vacia[140, 20:180] = 0
    vacia[20:140, 20] = 0
    vacia[20:140, 180] = 0
    with pytest.raises(ErrorDeTinta):
        aislar_curva(vacia, CAJA)
```

- [ ] **Paso 2: Correr para verificar que falla**

Correr: `.venv\Scripts\python.exe -m pytest tests/extraccion/test_tinta.py -v`
Esperado: FALLA con `ModuleNotFoundError`

- [ ] **Paso 3: Escribir la implementación mínima**

```python
# src/ctex/extraccion/tinta.py
"""Paso 4: quitar el marco y la rejilla, dejar la curva.

Segunda y ultima casa de OpenCV en el extractor.
"""

import cv2
import numpy as np

from ctex.extraccion.tipos import Caja

# Cuantos pixeles a cada lado de un borde de la caja se borran. Un eje dibujado
# a mano tiene grosor; dos pixeles cubren el caso limpio y el mediano.
GROSOR_BORDE = 2

# Debajo de esto se considera tinta. La rejilla impresa vive alrededor de 200 y
# la curva alrededor de 0; 128 los separa con holgura. Es un numero por
# calibrar cuando entren las fotos del nivel 0.
UMBRAL_TINTA = 128


class ErrorDeTinta(Exception):
    """No quedo curva despues de quitar el marco y la rejilla."""


def aislar_curva(imagen: np.ndarray, caja: Caja) -> np.ndarray:
    """Devuelve una mascara booleana del tamano de la imagen con solo la curva."""
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY) if imagen.ndim == 3 else imagen

    mascara = gris < UMBRAL_TINTA

    # Fuera de la caja no hay grafica: etiquetas, titulo, lo que sea.
    fuera = np.ones_like(mascara)
    arriba = int(caja.arriba)
    abajo = int(caja.abajo)
    izquierda = int(caja.izquierda)
    derecha = int(caja.derecha)
    fuera[arriba:abajo, izquierda:derecha] = False
    mascara[fuera] = False

    # Los cuatro bordes de la caja, con su grosor.
    for fila in (arriba, abajo):
        mascara[
            max(fila - GROSOR_BORDE, 0) : fila + GROSOR_BORDE + 1, :
        ] = False
    for columna in (izquierda, derecha):
        mascara[
            :, max(columna - GROSOR_BORDE, 0) : columna + GROSOR_BORDE + 1
        ] = False

    if not mascara.any():
        raise ErrorDeTinta(
            "No quedo ningun pixel de curva dentro de la caja despues de "
            "quitar el marco y la rejilla"
        )

    return mascara
```

- [ ] **Paso 4: Correr para verificar que pasa**

Correr: `.venv\Scripts\python.exe -m pytest tests/extraccion/test_tinta.py -v`
Esperado: PASAN las 5

- [ ] **Paso 5: Comprometer**

```bash
git add src/ctex/extraccion/tinta.py tests/extraccion/test_tinta.py
git commit -m "Extraccion: aislar la curva quitando el marco y la rejilla"
```

---

### Tarea 5: `rastreo.py` — el barrido por columnas

**Archivos:**
- Crear: `src/ctex/extraccion/rastreo.py`
- Crear: `tests/extraccion/test_rastreo.py`

**Interfaces:**
- Consume: nada de los módulos anteriores. **Solo NumPy.**
- Produce: `barrer(mascara: np.ndarray) -> tuple[np.ndarray, np.ndarray]`, que
  devuelve `(centroides, validez)`, ambos de largo igual al ancho de la máscara.
  `centroides` lleva `nan` donde `validez` es `False`.

Este es el módulo de D38. **No lleva un solo bucle sobre píxeles**, y por eso
cae la excepción de C++ que D11 había reservado: sin un paso que dependa del
anterior, no hay nada que acelerar.

- [ ] **Paso 1: Escribir la prueba que falla**

```python
# tests/extraccion/test_rastreo.py
import numpy as np
import pytest

from ctex.extraccion.rastreo import barrer


def test_una_horizontal_da_centroide_constante():
    mascara = np.zeros((20, 20), dtype=bool)
    mascara[7, :] = True
    centroides, validez = barrer(mascara)
    assert validez.all()
    assert centroides == pytest.approx(np.full(20, 7.0))


def test_una_diagonal_se_recupera_tal_cual():
    mascara = np.zeros((20, 20), dtype=bool)
    for i in range(20):
        mascara[i, i] = True
    centroides, validez = barrer(mascara)
    assert validez.all()
    assert centroides == pytest.approx(np.arange(20, dtype=float))


def test_un_trazo_grueso_promedia_al_centro():
    mascara = np.zeros((20, 20), dtype=bool)
    mascara[8:11, :] = True          # filas 8, 9 y 10
    centroides, _ = barrer(mascara)
    assert centroides == pytest.approx(np.full(20, 9.0))


def test_las_columnas_sin_tinta_salen_invalidas_no_cero():
    mascara = np.zeros((20, 20), dtype=bool)
    mascara[5, :] = True
    mascara[:, 12:14] = False        # se vacian dos columnas
    centroides, validez = barrer(mascara)
    assert not validez[12]
    assert not validez[13]
    assert np.isnan(centroides[12])
    assert validez[11] and validez[14]


def test_una_mascara_vacia_no_tiene_ninguna_columna_valida():
    centroides, validez = barrer(np.zeros((20, 20), dtype=bool))
    assert not validez.any()
    assert np.isnan(centroides).all()
```

- [ ] **Paso 2: Correr para verificar que falla**

Correr: `.venv\Scripts\python.exe -m pytest tests/extraccion/test_rastreo.py -v`
Esperado: FALLA con `ModuleNotFoundError`

- [ ] **Paso 3: Escribir la implementación mínima**

```python
# src/ctex/extraccion/rastreo.py
"""Paso 5: el barrido por columnas con centroide de la tinta (D38).

Cuatro operaciones sobre el arreglo completo. Ningun bucle sobre pixeles: por
eso este modulo no necesita C++, y por eso D38 revoco la excepcion de D11.
"""

import numpy as np


def barrer(mascara: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Devuelve el centroide de tinta por columna y cuales columnas son validas.

    Las columnas sin un solo pixel de tinta salen como `nan` y marcadas
    invalidas. No se interpolan aqui: eso lo decide el remuestreo (D45).
    """
    tinta = mascara.astype(np.float64)
    alto, ancho = tinta.shape

    filas = np.arange(alto, dtype=np.float64).reshape(-1, 1)

    total = tinta.sum(axis=0)
    ponderada = (tinta * filas).sum(axis=0)

    validez = total > 0
    centroides = np.full(ancho, np.nan, dtype=np.float64)
    centroides[validez] = ponderada[validez] / total[validez]

    return centroides, validez
```

- [ ] **Paso 4: Correr para verificar que pasa**

Correr: `.venv\Scripts\python.exe -m pytest tests/extraccion/test_rastreo.py -v`
Esperado: PASAN las 5

- [ ] **Paso 5: Comprometer**

```bash
git add src/ctex/extraccion/rastreo.py tests/extraccion/test_rastreo.py
git commit -m "Extraccion: barrido por columnas con centroide, sin un solo bucle"
```

---

### Tarea 6: `remuestreo.py` — de columnas a puntos

**Archivos:**
- Crear: `src/ctex/extraccion/remuestreo.py`
- Crear: `tests/extraccion/test_remuestreo.py`

**Interfaces:**
- Consume: `Transformacion` de `tipos.py`.
- Produce: `remuestrear(centroides, validez, transformacion, cuantos=30) ->
  list[list[float]]`, una lista de pares `[x, y]` en valores de la gráfica, y
  `ErrorDeRemuestreo`.

**Sin rellenos todavía.** Las columnas inválidas simplemente no aportan punto;
los huecos, el cierre morfológico y las dudas de D45 entran en el plan siguiente.

- [ ] **Paso 1: Escribir la prueba que falla**

```python
# tests/extraccion/test_remuestreo.py
import numpy as np
import pytest

from ctex.extraccion.remuestreo import ErrorDeRemuestreo, remuestrear
from ctex.extraccion.tipos import Transformacion


def transformacion_identidad_en_x():
    # 100 px de ancho valen 0..10; 200 px de alto valen -1..1
    return Transformacion(
        escala_x=0.1, escala_y=0.01, izquierda=0.0, arriba=0.0,
        xmin=0.0, ymax=1.0,
    )


def test_devuelve_la_cantidad_pedida():
    centroides = np.full(100, 50.0)
    validez = np.ones(100, dtype=bool)
    puntos = remuestrear(centroides, validez, transformacion_identidad_en_x(), 10)
    assert len(puntos) == 10


def test_los_puntos_estan_en_valores_no_en_pixeles():
    centroides = np.full(100, 100.0)   # fila 100 -> y = 1 - 100*0.01 = 0
    validez = np.ones(100, dtype=bool)
    puntos = remuestrear(centroides, validez, transformacion_identidad_en_x(), 3)
    assert puntos[0][0] == pytest.approx(0.0)
    assert puntos[-1][0] == pytest.approx(9.9, abs=0.2)
    for _, y in puntos:
        assert y == pytest.approx(0.0)


def test_las_columnas_invalidas_no_aportan_punto():
    centroides = np.full(100, 50.0)
    validez = np.ones(100, dtype=bool)
    validez[:50] = False
    centroides[:50] = np.nan
    puntos = remuestrear(centroides, validez, transformacion_identidad_en_x(), 5)
    assert all(x >= 5.0 - 0.2 for x, _ in puntos)


def test_los_puntos_salen_ordenados_por_x():
    centroides = np.arange(100, dtype=float)
    validez = np.ones(100, dtype=bool)
    puntos = remuestrear(centroides, validez, transformacion_identidad_en_x(), 8)
    equis = [x for x, _ in puntos]
    assert equis == sorted(equis)


def test_con_menos_de_cinco_columnas_validas_levanta():
    centroides = np.full(100, np.nan)
    validez = np.zeros(100, dtype=bool)
    centroides[:3] = 10.0
    validez[:3] = True
    with pytest.raises(ErrorDeRemuestreo):
        remuestrear(centroides, validez, transformacion_identidad_en_x(), 10)
```

- [ ] **Paso 2: Correr para verificar que falla**

Correr: `.venv\Scripts\python.exe -m pytest tests/extraccion/test_remuestreo.py -v`
Esperado: FALLA con `ModuleNotFoundError`

- [ ] **Paso 3: Escribir la implementación mínima**

```python
# src/ctex/extraccion/remuestreo.py
"""Pasos 6 y 7: convertir a valores y quedarse con 20-50 puntos.

La conversion es una transformacion afin que no puede crear ni destruir un
hueco, asi que se aplica solo a las columnas validas y la marca de validez pasa
intacta.
"""

import numpy as np

from ctex.extraccion.tipos import Transformacion

MINIMO_DE_COLUMNAS = 5


class ErrorDeRemuestreo(Exception):
    """No hay columnas validas suficientes para formar una serie."""


def remuestrear(
    centroides: np.ndarray,
    validez: np.ndarray,
    transformacion: Transformacion,
    cuantos: int = 30,
) -> list[list[float]]:
    """Devuelve `cuantos` puntos [x, y] en valores de la grafica."""
    columnas_validas = np.flatnonzero(validez)

    if columnas_validas.size < MINIMO_DE_COLUMNAS:
        raise ErrorDeRemuestreo(
            f"Solo {columnas_validas.size} columnas con tinta: hacen falta al "
            f"menos {MINIMO_DE_COLUMNAS} para formar una serie"
        )

    cuantos = min(cuantos, columnas_validas.size)
    indices = np.linspace(0, columnas_validas.size - 1, cuantos).round().astype(int)
    elegidas = columnas_validas[indices]

    return [
        [
            round(float(transformacion.a_valor_x(columna)), 6),
            round(float(transformacion.a_valor_y(centroides[columna])), 6),
        ]
        for columna in elegidas
    ]
```

- [ ] **Paso 4: Correr para verificar que pasa**

Correr: `.venv\Scripts\python.exe -m pytest tests/extraccion/test_remuestreo.py -v`
Esperado: PASAN las 5

- [ ] **Paso 5: Comprometer**

```bash
git add src/ctex/extraccion/remuestreo.py tests/extraccion/test_remuestreo.py
git commit -m "Extraccion: remuestreo a puntos en valores de la grafica"
```

---

### Tarea 7: `extractor.py` — la tubería y el contrato

**Archivos:**
- Crear: `src/ctex/extraccion/extractor.py`
- Crear: `tests/extraccion/test_extractor.py`

**Interfaces:**
- Consume: todo lo anterior, más `ctex.contrato.validador.validar`.
- Produce: `extraer(ruta_imagen, rango_x, rango_y, cuantos=30) ->
  tuple[dict, Traza]`.

- [ ] **Paso 1: Escribir la prueba que falla**

```python
# tests/extraccion/test_extractor.py
import cv2
import numpy as np
import pytest

from ctex.contrato.validador import validar
from ctex.extraccion.extractor import extraer


@pytest.fixture
def recorte(tmp_path):
    """Recuadro con una diagonal dentro, escrito a disco."""
    imagen = np.full((160, 200), 255, dtype=np.uint8)
    imagen[20, 20:180] = 0
    imagen[140, 20:180] = 0
    imagen[20:140, 20] = 0
    imagen[20:140, 180] = 0
    for i in range(100):
        imagen[30 + i, 30 + i] = 0
    ruta = tmp_path / "recorte.png"
    cv2.imwrite(str(ruta), imagen)
    return ruta


def test_el_documento_cumple_el_contrato(recorte):
    documento, _ = extraer(recorte, (0.0, 10.0), (-1.0, 1.0))
    validar(documento)  # no lanza


def test_sale_un_solo_bloque_de_grafica(recorte):
    documento, _ = extraer(recorte, (0.0, 10.0), (-1.0, 1.0))
    assert len(documento["bloques"]) == 1
    assert documento["bloques"][0]["tipo"] == "grafica"


def test_los_rangos_salen_de_los_argumentos_no_de_la_imagen(recorte):
    documento, _ = extraer(recorte, (0.0, 10.0), (-1.0, 1.0))
    ejes = documento["bloques"][0]["contenido"]["ejes"]
    assert ejes["x"]["min"] == 0.0 and ejes["x"]["max"] == 10.0
    assert ejes["y"]["min"] == -1.0 and ejes["y"]["max"] == 1.0


def test_los_textos_van_vacios_porque_la_fase_1_no_lee_etiquetas(recorte):
    contenido = extraer(recorte, (0.0, 10.0), (-1.0, 1.0))[0]["bloques"][0]["contenido"]
    assert contenido["titulo"] == ""
    assert contenido["ejes"]["x"]["etiqueta"] == ""
    assert contenido["ejes"]["y"]["etiqueta"] == ""


def test_la_confianza_es_el_marcador_de_posicion(recorte):
    documento, _ = extraer(recorte, (0.0, 10.0), (-1.0, 1.0))
    assert documento["bloques"][0]["confianza"] == 0.5


def test_la_traza_trae_la_caja_y_la_transformacion(recorte):
    _, traza = extraer(recorte, (0.0, 10.0), (-1.0, 1.0))
    assert traza.caja is not None
    assert traza.transformacion is not None
    assert traza.centroides is not None


def test_una_imagen_que_no_existe_levanta(tmp_path):
    with pytest.raises(FileNotFoundError):
        extraer(tmp_path / "no_existe.png", (0.0, 10.0), (-1.0, 1.0))
```

- [ ] **Paso 2: Correr para verificar que falla**

Correr: `.venv\Scripts\python.exe -m pytest tests/extraccion/test_extractor.py -v`
Esperado: FALLA con `ModuleNotFoundError`

- [ ] **Paso 3: Escribir la implementación mínima**

```python
# src/ctex/extraccion/extractor.py
"""La tuberia: de un recorte a un documento del contrato.

Devuelve tambien la traza con los intermedios (D43).
"""

from pathlib import Path

import cv2

from ctex.extraccion.escala import fijar_escala
from ctex.extraccion.marco import detectar_caja
from ctex.extraccion.rastreo import barrer
from ctex.extraccion.remuestreo import remuestrear
from ctex.extraccion.tinta import aislar_curva
from ctex.extraccion.tipos import Traza

# Marcador de posicion declarado (D44). El aparato de confianza es la fase 2.
# Se elige 0.5 porque es el valor que menos informacion aparenta.
CONFIANZA_MARCADOR = 0.5


def extraer(
    ruta_imagen: Path,
    rango_x: tuple[float, float],
    rango_y: tuple[float, float],
    cuantos: int = 30,
) -> tuple[dict, Traza]:
    """De un recorte de grafica a un documento del contrato v1.0."""
    ruta_imagen = Path(ruta_imagen)
    if not ruta_imagen.exists():
        raise FileNotFoundError(f"No existe la imagen: {ruta_imagen}")

    imagen = cv2.imread(str(ruta_imagen), cv2.IMREAD_GRAYSCALE)
    if imagen is None:
        raise FileNotFoundError(f"No se pudo leer como imagen: {ruta_imagen}")

    traza = Traza()

    caja = detectar_caja(imagen)
    traza.caja = caja

    transformacion = fijar_escala(caja, rango_x, rango_y)
    traza.transformacion = transformacion

    mascara = aislar_curva(imagen, caja)

    centroides, validez = barrer(mascara)
    traza.centroides = centroides
    traza.validez = validez

    puntos = remuestrear(centroides, validez, transformacion, cuantos)
    traza.puntos = puntos

    alto, ancho = imagen.shape
    documento = {
        "version_contrato": "1.0",
        # `pagina: 1` es deuda anotada en D46: el recorte no viene de la
        # pagina de nada, pero el esquema lo exige.
        "origen": {"archivo": ruta_imagen.name, "pagina": 1},
        "bloques": [
            {
                "id": "b1",
                "tipo": "grafica",
                # La region es el recorte entero: por D37 la entrada ya es la
                # grafica y no hay nada que localizar.
                "region": {
                    "x": 0, "y": 0, "ancho": float(ancho), "alto": float(alto),
                },
                "confianza": CONFIANZA_MARCADOR,
                "contenido": {
                    "tipo_grafica": "lineas",
                    "titulo": "",
                    "ejes": {
                        "x": {
                            "min": rango_x[0], "max": rango_x[1],
                            "etiqueta": "", "escala": "lineal",
                        },
                        "y": {
                            "min": rango_y[0], "max": rango_y[1],
                            "etiqueta": "", "escala": "lineal",
                        },
                    },
                    "series": [{"etiqueta": "", "puntos": puntos}],
                },
            }
        ],
        "dudas": [],
    }

    return documento, traza
```

- [ ] **Paso 4: Correr para verificar que pasa**

Correr: `.venv\Scripts\python.exe -m pytest tests/extraccion/test_extractor.py -v`
Esperado: PASAN las 7

- [ ] **Paso 5: Comprometer**

```bash
git add src/ctex/extraccion/extractor.py tests/extraccion/test_extractor.py
git commit -m "Extraccion: la tuberia de recorte a documento del contrato"
```

---

### Tarea 8: `cli.py` — el comando `ctex-extraer`

**Archivos:**
- Crear: `src/ctex/extraccion/cli.py`
- Crear: `tests/extraccion/test_cli.py`
- Modificar: `pyproject.toml` (sección `[project.scripts]`)

**Interfaces:**
- Consume: `extraer` de `extractor.py`.
- Produce: `main(argv: list[str] | None = None) -> int`.

- [ ] **Paso 1: Escribir la prueba que falla**

```python
# tests/extraccion/test_cli.py
import json

import cv2
import numpy as np
import pytest

from ctex.extraccion.cli import main


@pytest.fixture
def recorte(tmp_path):
    imagen = np.full((160, 200), 255, dtype=np.uint8)
    imagen[20, 20:180] = 0
    imagen[140, 20:180] = 0
    imagen[20:140, 20] = 0
    imagen[20:140, 180] = 0
    for i in range(100):
        imagen[30 + i, 30 + i] = 0
    ruta = tmp_path / "recorte.png"
    cv2.imwrite(str(ruta), imagen)
    return ruta


def test_escribe_el_json_y_sale_con_cero(recorte, tmp_path):
    salida = tmp_path / "hoja.json"
    codigo = main([
        str(recorte), "--escala-x", "0,10", "--escala-y", "-1,1",
        "--salida", str(salida),
    ])
    assert codigo == 0
    assert salida.exists()
    documento = json.loads(salida.read_text(encoding="utf-8"))
    assert documento["version_contrato"] == "1.0"


def test_un_rango_invertido_sale_con_dos(recorte, tmp_path):
    codigo = main([
        str(recorte), "--escala-x", "10,0", "--escala-y", "-1,1",
        "--salida", str(tmp_path / "hoja.json"),
    ])
    assert codigo == 2


def test_una_imagen_sin_marco_sale_con_tres(tmp_path):
    blanca = tmp_path / "blanca.png"
    cv2.imwrite(str(blanca), np.full((160, 200), 255, dtype=np.uint8))
    codigo = main([
        str(blanca), "--escala-x", "0,10", "--escala-y", "-1,1",
        "--salida", str(tmp_path / "hoja.json"),
    ])
    assert codigo == 3


def test_la_traza_se_escribe_si_se_pide(recorte, tmp_path):
    traza = tmp_path / "traza.json"
    main([
        str(recorte), "--escala-x", "0,10", "--escala-y", "-1,1",
        "--salida", str(tmp_path / "hoja.json"), "--traza", str(traza),
    ])
    assert traza.exists()
    contenido = json.loads(traza.read_text(encoding="utf-8"))
    assert "caja" in contenido
```

- [ ] **Paso 2: Correr para verificar que falla**

Correr: `.venv\Scripts\python.exe -m pytest tests/extraccion/test_cli.py -v`
Esperado: FALLA con `ModuleNotFoundError`

- [ ] **Paso 3: Escribir la implementación mínima**

```python
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
```

- [ ] **Paso 4: Correr para verificar que pasa**

Correr: `.venv\Scripts\python.exe -m pytest tests/extraccion/test_cli.py -v`
Esperado: PASAN las 4

- [ ] **Paso 5: Registrar el comando**

En `pyproject.toml`, dejar `[project.scripts]` así:

```toml
[project.scripts]
ctex = "ctex.cli:main"
ctex-extraer = "ctex.extraccion.cli:main"
```

Reinstalar: `.venv\Scripts\python.exe -m pip install -e ".[dev]"`

- [ ] **Paso 6: Comprometer**

```bash
git add src/ctex/extraccion/cli.py tests/extraccion/test_cli.py pyproject.toml
git commit -m "Extraccion: el comando ctex-extraer, con sus codigos de salida"
```

---

### Tarea 9: La caminata completa contra el nivel −1

**Archivos:**
- Crear: `tests/extraccion/test_caminata.py`

**Interfaces:**
- Consume: `ctex.material.generador.generar_corpus` y `ctex.extraccion.extractor.extraer`.
- Produce: nada. Es la prueba que cierra la caminata.

Esta es la tarea que hace que todo lo anterior valga: **material con verdad
perfecta entra, y se compara el resultado contra esa verdad.** Se salta sola si
falta Tectonic o pdftoppm, igual que el resto de las pruebas que compilan.

- [ ] **Paso 1: Escribir la prueba que falla**

```python
# tests/extraccion/test_caminata.py
import json
import shutil

import numpy as np
import pytest

from ctex.contrato.validador import validar
from ctex.extraccion.extractor import extraer
from ctex.material.generador import generar_corpus

faltan_herramientas = shutil.which("tectonic") is None or shutil.which("pdftoppm") is None
saltar = pytest.mark.skipif(
    faltan_herramientas, reason="hacen falta tectonic y pdftoppm"
)


@pytest.fixture(scope="module")
def par(tmp_path_factory):
    """Genera una grafica del nivel -1 y devuelve (png, verdad)."""
    carpeta = tmp_path_factory.mktemp("nivel_menos_1")
    resultados = generar_corpus(cuantas=1, semilla=7, carpeta_salida=carpeta)
    png, ruta_verdad = resultados[0]
    verdad = json.loads(ruta_verdad.read_text(encoding="utf-8"))
    return png, verdad


@saltar
def test_del_nivel_menos_1_sale_un_contrato_valido(par):
    png, verdad = par
    rango_x = (verdad["ejes"]["x"]["min"], verdad["ejes"]["x"]["max"])
    rango_y = (verdad["ejes"]["y"]["min"], verdad["ejes"]["y"]["max"])
    documento, _ = extraer(png, rango_x, rango_y)
    validar(documento)


@saltar
def test_el_error_mediano_esta_por_debajo_del_dos_por_ciento(par):
    png, verdad = par
    rango_x = (verdad["ejes"]["x"]["min"], verdad["ejes"]["x"]["max"])
    rango_y = (verdad["ejes"]["y"]["min"], verdad["ejes"]["y"]["max"])

    documento, _ = extraer(png, rango_x, rango_y, cuantos=50)
    extraidos = np.array(documento["bloques"][0]["contenido"]["series"][0]["puntos"])
    ciertos = np.array(verdad["puntos"])

    # La curva extraida se evalua en las x de la verdad, que es como compara
    # ctex-medir: los puntos remuestreados no caen en las x de la verdad.
    estimados = np.interp(ciertos[:, 0], extraidos[:, 0], extraidos[:, 1])

    rango = rango_y[1] - rango_y[0]
    errores = np.abs(estimados - ciertos[:, 1]) / rango

    assert np.median(errores) < 0.02, (
        f"error mediano {np.median(errores):.4f}, peor {errores.max():.4f}"
    )
```

- [ ] **Paso 2: Correr para verificar que falla**

Correr: `.venv\Scripts\python.exe -m pytest tests/extraccion/test_caminata.py -v`
Esperado: FALLA. Puede fallar por dos motivos distintos y **hay que distinguirlos**:
si falla con `ModuleNotFoundError`, falta código de tareas anteriores; si falla en
la aserción del 2%, la caminata corre pero el extractor no da la precisión.

- [ ] **Paso 3: Ajustar hasta que pase**

No hay código nuevo que escribir: las nueve piezas ya existen. Si el error
mediano supera el 2%, los sospechosos, en orden:

1. **`UMBRAL_TINTA` en `tinta.py`.** La curva de pgfplots es azul, no negra: en
   gris queda alrededor de 100, no de 0. Si el umbral la deja fuera, no hay
   curva; si deja pasar la rejilla, el centroide se corre hacia ella.
2. **`GROSOR_BORDE` en `tinta.py`.** Si es muy chico, quedan restos del recuadro
   dentro de la máscara y jalan el centroide en las columnas de los bordes.
3. **Los marcadores de los puntos.** pgfplots dibuja un círculo relleno en cada
   punto; son más gruesos que la línea y desplazan el centroide de esa columna.
   Si esto resulta ser la causa dominante, **anotarlo**: significa que el
   material del nivel −1 debe generarse sin marcadores, y eso es un cambio en
   `ctex.material`, no en el extractor.

Cualquier ajuste va acompañado de una nota en el commit diciendo qué se movió y
por qué.

- [ ] **Paso 4: Correr la suite completa**

Correr: `.venv\Scripts\python.exe -m pytest -q`
Esperado: todas pasan, ninguna saltada (Tectonic y pdftoppm están instalados)

- [ ] **Paso 5: Correr el comando de verdad, de punta a punta**

```bash
.venv\Scripts\python.exe -m ctex.material.generar --cuantas 1 --semilla 7 --salida .\salida\caminata
.venv\Scripts\python.exe -m ctex.extraccion.cli .\salida\caminata\000.png --escala-x 0,5 --escala-y -1,11 --salida .\salida\caminata\hoja.json
.venv\Scripts\python.exe -m ctex.cli .\salida\caminata\hoja.json --salida .\salida\caminata
```

Ajustar los rangos a los que diga `000.verdad.json`. Al final tiene que haber un
PDF con una gráfica que se parezca a la de entrada. **Abrirlo y mirarlo.**

- [ ] **Paso 6: Comprometer**

```bash
git add tests/extraccion/test_caminata.py
git commit -m "Extraccion: la caminata completa, medida contra el nivel -1"
```

---

## Terminado cuando

- Las nueve tareas cumplen su criterio.
- `python -m pytest` pasa entero, sin saltadas.
- La cadena de tres comandos del paso 5 de la Tarea 9 produce un PDF, y al
  abrirlo se ve una gráfica parecida a la de entrada.
- El error mediano contra el nivel −1 está por debajo del 2% del rango.

**Y una advertencia que hay que repetir al reportar el resultado:** pasar el
nivel −1 **no dice que el extractor sirva.** Son gráficas generadas por nuestro
propio motor, sin ruido, sin papel y sin mano. Es la prueba de que no está roto.
Quien responde I1a es el nivel 1, que son las 24 gráficas de D41 dibujadas a
mano, y ese corpus todavía no existe.
