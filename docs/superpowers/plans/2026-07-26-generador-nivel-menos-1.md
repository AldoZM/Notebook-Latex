# Plan — El generador del nivel −1

**Fase 0** de D30. Produce el material de prueba con verdad perfecta contra el
cual se medirá el extractor de gráficas.

- **Escrito:** 2026-07-26
- **Rama:** `fase-0-generador-nivel-menos-1`
- **Decisiones que lo gobiernan:** D35 (la escalera de cuatro niveles), D41 (el
  corpus), D10 (Python no dibuja gráficas), D2 (el contrato es la frontera)

---

## Qué es

El motor de salida se vuelve el generador de material del motor de entrada:

```
datos exactos elegidos por nosotros
      |
      v
  bloque `grafica` del contrato        (esquema v1.0, ya existe)
      |
      v
  componer()                           (ya existe, no se toca)
      |
      v
  Tectonic                             (ya existe, no se toca)
      |
      v
  PDF  --pdftoppm-->  PNG
      |
      v
  (NNN.png , NNN.verdad.json)
```

**La verdad es exacta por construcción**, no por medición: los puntos que salen
en `verdad.json` son literalmente los que se le dieron al contrato. No hay
intermediario que los degrade.

## Por qué esto y no el extractor

El material de prueba va antes que lo que se va a probar. Si el extractor se
construye primero, pasa un rato sin nada contra qué medirse — que es justo lo
que D39 quiso evitar al poner el contrato como frontera dura.

Y no depende de ninguna decisión pendiente: la arquitectura del extractor está
sin diseñar, pero esto no la toca.

## Restricciones

1. **No se modifica `contrato/`, `composicion/` ni `compilacion/`.** Se importan
   y se usan. Si algo de ahí estorba, se reporta — no se edita.
2. **Las 89 pruebas existentes siguen pasando.** Sin excepción.
3. **Nada de matplotlib ni de dibujar la gráfica en Python.** D10. La gráfica la
   dibuja pgfplots dentro del PDF, y el PNG es una rasterización de ese PDF.
4. **Determinista.** La misma semilla produce exactamente el mismo corpus.
5. **Si falta Tectonic o pdftoppm, las pruebas que compilan se saltan solas**,
   igual que las de `tests/compilacion/`. Un `skipped` no es un `passed`.

---

## Tarea 1 — El módulo y la definición de una gráfica

Crear `src/ctex/material/` con una función que describa una gráfica sintética:
qué puntos, qué rangos de eje, qué etiquetas.

**Terminada cuando:**

- existe `src/ctex/material/__init__.py` y `src/ctex/material/definicion.py`
- una función construye la definición de una gráfica a partir de una familia de
  curvas y una semilla
- hay al menos tres familias: lineal, exponencial decreciente y senoidal
- los puntos generados caen dentro de los rangos de eje declarados, siempre
- una prueba verifica que la misma semilla da la misma definición

## Tarea 2 — De la definición al documento del contrato

Convertir una definición en un documento del contrato válido, con un solo
bloque de tipo `grafica`.

**Terminada cuando:**

- una función recibe una definición y devuelve el diccionario del contrato
- el documento pasa `ctex.contrato.validador.validar()` sin lanzar
- el bloque lleva `tipo_grafica`, `ejes` con `min`/`max`/`etiqueta`/`escala`, y
  una sola serie con sus puntos — la forma exacta de `tests/datos/hoja_ejemplo.json`
- una prueba verifica que el documento generado es válido según el esquema

## Tarea 3 — El rasterizador

Convertir el PDF que produce `compilar()` en un PNG.

**Terminada cuando:**

- una función recibe la ruta de un PDF y devuelve la ruta de un PNG
- usa `pdftoppm` como subproceso, con resolución configurable (por omisión 200 ppp)
- si `pdftoppm` no está, levanta un error propio y claro, no un `FileNotFoundError`
  crudo
- una prueba compila un documento mínimo, lo rasteriza y verifica que el PNG
  existe y que su firma de archivo es la de un PNG
- esa prueba se salta sola si falta Tectonic o pdftoppm

## Tarea 4 — El generador de punta a punta

Encadenar todo y escribir los pares al disco.

**Terminada cuando:**

- una función recibe cuántas gráficas, una semilla y una carpeta de salida, y
  escribe los pares
- cada par son dos archivos con el mismo prefijo numerado: `000.png` y
  `000.verdad.json`
- `verdad.json` contiene, como mínimo: los puntos exactos, los rangos de los dos
  ejes, la familia de la curva y la semilla
- los puntos de `verdad.json` son idénticos a los que se le dieron al contrato —
  una prueba lo verifica comparando los dos, no confiando
- una prueba genera dos gráficas y verifica que salen cuatro archivos

## Tarea 5 — El comando

Exponerlo por línea de comandos, como el resto del motor.

**Terminada cuando:**

- `python -m ctex.material.generar --cuantas 5 --semilla 1 --salida ./corpus/nivel-menos-1`
  produce cinco pares
- el comando imprime la carpeta de salida y termina con código 0
- si algo falla, sale con código distinto de 0 y un mensaje a `stderr`
- una prueba invoca el comando con `--cuantas 1` y verifica el código de salida

---

## Terminado cuando

- las cinco tareas cumplen su criterio
- `python -m pytest` pasa entero, con las 89 anteriores incluidas
- correr el comando dos veces con la misma semilla produce archivos idénticos
- **existe al menos un PNG que se puede abrir y se ve una gráfica**

## Lo que NO entra

- El extractor. Esto genera material, no lo lee.
- Los niveles 0, 1 y 2. Requieren cámara o mano.
- Deformaciones sintéticas (ruido, textura de papel, inclinación). El nivel −1 es
  la verdad limpia; deformarla es otra tarea y otra decisión.
