# El extractor de gráficas — diseño

De un recorte de imagen a un documento del contrato. Es la **fase 1** de D30 y lo
que responde **I1a**: *¿se pueden extraer los valores de una gráfica dibujada a
mano con precisión suficiente?*

Este documento dice **qué** se construye. El **por qué** está en el
[registro de decisiones](../../planeacion/notas-plan.md), decisiones **D34 a
D47**. El **cómo se trabaja** está en
[`MAPA-DEL-PROCESO.txt`](../../../MAPA-DEL-PROCESO.txt).

- **Escrito:** 2026-07-26
- **Precede a:** el plan de implementación, que sale de aquí
- **Depende de:** el motor de salida, que ya existe y compila (107 pruebas)

---

## 1. Qué responde, y qué no

I1 se parte en dos preguntas de peso muy distinto (D34):

| | Pregunta | Si falla |
|---|---|---|
| **I1a** | ¿el rastreo es preciso? | **no hay proyecto** |
| **I1b** | ¿se lee la escala sola? | el usuario teclea. Es fricción, no muerte |

**Esta fase responde I1a solamente.** La escala se recibe por argumento; el
clasificador de dígitos no entra. Los criterios 1 y 2 de la Sección 11 de la
especificación del motor —error mediano bajo 2% del rango, ningún punto sobre
5%— se miden con la escala dada. El criterio 3 es I1b y espera.

## 2. Alcance

**Entra:** una sola curva, ejes rectos, con o sin rejilla (D36). La entrada es un
recorte que ya es la gráfica (D37).

**No entra:** varias curvas, dispersión, barras; localizar la gráfica dentro de
una hoja con texto —eso es la etapa 2, segmentación, y tendrá su propia fase—; y
leer las etiquetas de los ejes.

Dos curvas que se cruzan es un problema distinto —separación de curvas— y
contaminaría la medición de I1a con una dificultad que no es la que se mide.

## 3. Arquitectura

Los siete pasos de la Sección 6 del motor, con el paso 2 ausente por D34 y un
paso 1b nuevo por D40:

```
   recorte.png   +   --escala-x 0,10   --escala-y -1,1
        |
        v
   1   marco            las dos rectas largas de los ejes      OpenCV / Hough
        |
   1b  rectificación    endereza usando esas dos rectas        D40
        |
  [2]  leer etiquetas   -- NO ESTÁ. La escala se teclea        D34
        |
   3   escala           rectas + rangos dados → píxel a valor  determinista
        |
   4   tinta            quita rejilla y ejes, deja la curva    OpenCV
        |
   5   rastreo          barrido por columnas + centroide       D38
        |
   6   conversión       aplica la transformación del paso 3    determinista
        |
   7   remuestreo       20–50 puntos representativos           determinista
        |
        v
   hoja.json    contrato v1.0, un bloque `grafica`
```

**Seis de los siete pasos son deterministas y uno es visión clásica. No hay
ningún modelo en la ruta.** Es lo que D30 predijo al adelantar las gráficas: la
fase que decide si el proyecto vive no entrena nada.

### Mapa de módulos

Un módulo por paso, más el que los encadena. Cada uno se prueba por separado.

| Módulo | Recibe | Devuelve | Depende de |
|---|---|---|---|
| `marco.py` | imagen | **caja** (4 bordes) + rectas | OpenCV |
| `rectificacion.py` | imagen + rectas | imagen enderezada + caja nueva | OpenCV |
| `escala.py` | **caja** + los dos rangos | transformación píxel→valor | nada |
| `tinta.py` | imagen + rectas | máscara booleana de la curva | OpenCV, NumPy |
| `rastreo.py` | máscara | pares (columna, fila) **+ máscara de validez** | **solo NumPy** |
| `remuestreo.py` | puntos en valores + validez | 20–50 puntos + dudas | NumPy |
| `extractor.py` | ruta + rangos | documento del contrato + traza | los de arriba |
| `cli.py` | argumentos | `hoja.json` | `extractor` |

`rastreo.py` no depende de OpenCV, y eso no es casualidad: es D38 hecho
estructura. Si el barrido fuera secuencial habría un bucle por píxel, y ahí es
donde D11 reservaba C++. Sin bucle no hay nada que acelerar.

**Nada de OpenCV cruza hacia afuera de `marco`, `rectificacion` y `tinta`.** Si
algún día se cambia de biblioteca de visión, el cambio se detiene en esos tres
archivos.

### Tipos que cruzan las fronteras

```
Recta            rho, theta                       forma de Hough, no dos puntos
Caja             izquierda, derecha, arriba, abajo   en pixeles
Transformacion   escala_x, escala_y, izquierda, arriba
Traza            caja, transformacion, barrido_crudo, validez, puntos_finales
```

`Recta` en forma de Hough porque es lo que devuelve OpenCV y porque el ángulo
—que es lo que necesita `rectificacion`— se lee directo, sin arcotangentes.

**`Caja` es la pieza que hace posible la escala, y merece decirse aparte.** Dos
rectas infinitas dicen *dónde están los ejes*, pero no dicen qué píxel es `xmin`
ni cuál es `xmax`, así que por sí solas no determinan ninguna transformación. Lo
que ancla la escala son los **cuatro bordes del área de la gráfica**: el borde
izquierdo vale `xmin`, el derecho `xmax`, el inferior `ymin` y el superior
`ymax`. Esa es también la convención que se le pide al usuario cuando teclea la
escala (D34): los rangos son los de la caja dibujada, no los de la curva.

Imágenes como arreglos de NumPy; puntos como listas de pares; el contrato como
diccionario.

### Dependencias nuevas

Hoy el proyecto tiene una sola dependencia, `jsonschema`. Esta fase agrega
**NumPy y OpenCV**. Es el primer peso real y va a importar al armar la imagen de
despliegue, pero la pila de la especificación del motor ya las nombraba.

## 4. Los componentes

### `marco.py` — encontrar la caja

Binarizar y aplicar **transformada de Hough**. De las rectas que salgan, separar
las cercanas a la horizontal de las cercanas a la vertical, y quedarse con las
**cuatro extremas**: la vertical de más a la izquierda y la de más a la derecha,
la horizontal de más arriba y la de más abajo. Esas cuatro son la caja.

Hough devuelve las rectas ordenadas por votos, y los votos son proporcionales a
la longitud del trazo, así que "la más votada" equivale a "la más larga" sin
tener que medirla.

Con solo dos ejes en forma de L —sin recuadro completo— los otros dos bordes se
toman de la extensión de la tinta. La caja sigue quedando definida.

**Riesgo conocido:** con rejilla densa (condición C2 de D41) las líneas de
rejilla pueden ser tan largas como los ejes. Las desempata el grosor. Si eso no
basta, el respaldo es quedarse con las dos rectas **extremas** —la de más abajo y
la de más a la izquierda—, que es donde están los ejes por definición.

Si no se puede formar la caja, para (D47, código 3). Es el modo de fallo bueno:
ruidoso.

### `escala.py` — de la caja a la transformación

Aritmética, sin visión:

```
escala_x = (xmax - xmin) / (derecha - izquierda)
escala_y = (ymax - ymin) / (abajo - arriba)

valor_x = xmin + (columna - izquierda) * escala_x
valor_y = ymax - (fila    - arriba)    * escala_y
```

El eje Y va restando porque en una imagen la fila 0 está **arriba**, mientras que
en la gráfica el valor mayor está arriba. Invertir ese signo es el error más
fácil de cometer aquí y el más difícil de ver: produce una curva reflejada que
sigue pareciendo una curva.

### `rectificacion.py` — enderezar con los propios ejes

El barrido por columnas presupone que el eje X está horizontal en la imagen: una
columna de la imagen es una columna del sensor, no del eje. Con dos grados de
inclinación cada columna cruza la curva en un lugar distinto del que debería
(D40).

La corrección sale de las dos rectas del paso 1, que en el papel son
perpendiculares. **La gráfica trae su propio patrón de calibración dibujado
encima**, así que no hay que detectar los bordes de la hoja.

Si el ángulo resulta absurdo, para (D47, código 3).

### `tinta.py` — quitar todo menos la curva

Tres restas, en orden:

1. **Los ejes**, que ya se conocen por `marco`: se borran sus dos bandas.
2. **La rejilla**, por color o intensidad. Un umbral **por canal** separa mejor
   que uno por gris: la rejilla suele ser azul o verde y la tinta oscura.
3. **Lo suelto**: componentes conexas pequeñas fuera —motas, restos de
   etiquetas, marcas de doblez.

Después, **cierre morfológico** —dilatar y erosionar— para sellar los cortes de
uno o dos píxeles que el borrado de rejilla deja donde la curva la cruza (D45).
Sella sin mover la geometría del trazo, porque las dos operaciones se cancelan en
todo lo demás.

Si no queda nada, para (D47, código 4).

### `rastreo.py` — el barrido

Cuatro operaciones sobre arreglos completos, sin un solo bucle:

```
   mascara                arreglo booleano, alto x ancho
      |
      |  filas = arange(alto)
      v
   total[col]      = suma de tinta por columna
   ponderada[col]  = suma de (fila * tinta) por columna
      |
      v
   centroide[col]  = ponderada[col] / total[col]
```

**Las columnas sin tinta salen como división entre cero y se marcan inválidas.**
No se interpolan aquí: se dejan huecas y decide `remuestreo`.

Esa marca de validez es un arreglo booleano paralelo al de centroides, y **viaja
junto a los puntos a través del paso 6**. La conversión de píxel a valor es una
transformación afín que no puede crear ni destruir un hueco, así que se aplica
solo a las columnas válidas y la marca pasa intacta. Sin ese arreglo,
`remuestreo` no tendría cómo distinguir un valor medido de uno ausente y las
reglas de D45 no se podrían aplicar.

**Detección de saltos:** una columna con mucha más tinta que sus vecinas indica
un tramo casi vertical, donde el centroide cae en medio del salto y entrega un
valor creíble y falso. Se detecta y se emite `punto_incierto` (D47). No para el
proceso; lo anuncia.

### `remuestreo.py` — los huecos y los 20–50 puntos

Reglas de D45:

| Hueco | Qué se hace |
|---|---|
| En un extremo | **Nunca se toca.** Ahí no hay curva; rellenar sería extrapolar |
| Interior, angosto | Interpolación **lineal** + una `duda` de tipo `punto_incierto` |
| Interior, ancho | Se deja hueco |

Lineal y no spline: sobre huecos angostos difieren en menos de un píxel, y la
spline puede sobrepasar e inventar curvatura que no existía.

Si quedan menos de 5 puntos, para (D47, código 4).

## 5. El contrato de salida

Un documento v1.0 con **un solo bloque de tipo `grafica`** (D46):

```json
{
  "version_contrato": "1.0",
  "origen": { "archivo": "recorte.png", "pagina": 1 },
  "bloques": [
    {
      "id": "b1",
      "tipo": "grafica",
      "region": { "x": 0, "y": 0, "ancho": 678, "alto": 549 },
      "confianza": 0.5,
      "contenido": {
        "tipo_grafica": "lineas",
        "titulo": "",
        "ejes": {
          "x": { "min": 0, "max": 10, "etiqueta": "", "escala": "lineal" },
          "y": { "min": -1, "max": 1, "etiqueta": "", "escala": "lineal" }
        },
        "series": [ { "etiqueta": "", "puntos": [[0.0, 0.91]] } ]
      }
    }
  ],
  "dudas": []
}
```

- **`region` es el recorte entero.** Por D37 la entrada ya es la gráfica; no hay
  nada que localizar. El día que ese campo diga otra cosa, será porque entró la
  segmentación.
- **`confianza` vale 0.5**, marcador de posición declarado (D44). El aparato de
  confianza es la fase 2. Se elige 0.5 porque es el valor que menos información
  aparenta: un 0.9 afirmaría seguridad y sería mentira.
- **`titulo` y las dos `etiqueta` van vacíos** (D34, D46). Vacío es honesto;
  inventarlo sería peor.
- **`min` y `max` salen de los argumentos, no de la imagen** (D34).
- **`dudas`** lleva una entrada por cada hueco relleno y por cada salto
  detectado.

**Deuda registrada:** `origen.pagina` se escribe como `1` fijo. El recorte no
viene de la página de nada. Es válido para el esquema y es un dato falso; se
resuelve cuando llegue la segmentación, que sí sabe de qué página salió cada
recorte (D46).

## 6. El comando

```
ctex-extraer recorte.png --escala-x 0,10 --escala-y -1,1 --salida hoja.json
             [--traza traza.json] [--ppp 200] [--relleno-max 0.01]
```

Encadena con el motor que ya existe (D39):

```
ctex-extraer recorte.png --escala-x 0,10 --escala-y -1,1 --salida hoja.json
ctex hoja.json --salida ./salida
```

El contrato como frontera dura le da al extractor un blanco contra el cual
entregar, con validador y pruebas ya escritas.

`extraer()` devuelve **contrato y traza** (D43). La traza lleva los datos baratos
siempre —rectas, transformación, barrido crudo, puntos finales— y las imágenes
intermedias solo si se piden, porque una máscara de 4000×3000 pesa lo mismo que
la entrada.

## 7. Manejo de errores

**El extractor no degrada.** Es una excepción deliberada a D18, que hace que el
motor siempre entregue un PDF: D18 funciona porque la degradación es visible —el
recuadro rojo—, y en el extractor no hay dónde ponerlo. Una serie mal rastreada
produce una gráfica plausible con datos equivocados, que es el error catastrófico
de la Sección 6.

> **Prefiere no entregar nada antes que entregar algo plausible y falso** (D47).

| Paso | Si falla | Código |
|---|---|---|
| 1 marco | no aparecen dos rectas | 3 |
| 1b rectificación | ángulo absurdo | 3 |
| 3 escala | rango invertido o cero | 2 |
| 4 tinta | no queda nada | 4 |
| 5 rastreo | pocas columnas con valor | 4 |
| 7 remuestreo | menos de 5 puntos | 4 |

Que 3 y 4 sean distintos importa: son fallas de pasos distintos, se arreglan con
cosas distintas, y un solo código obligaría a abrir la imagen para saber cuál
fue.

**Lo único que degrada** son los huecos rellenos y los saltos marcados, y no es
una excepción: un relleno marcado deja su región para ir a mirarla, mientras que
una curva mal rastreada no deja rastro de su error.

## 8. Pruebas

### Rápidas, en cada cambio — sin una sola imagen real

Máscaras de NumPy escritas a mano, de 20×20, en milisegundos:

| Máscara | Verifica |
|---|---|
| una diagonal perfecta | el barrido devuelve la diagonal |
| una recta horizontal | centroide constante |
| dos columnas vaciadas | salen como hueco, no como cero |
| una columna con mucha tinta | se detecta como salto → duda |
| un hueco de 2 px | se cierra con la morfología |
| un hueco ancho | **no** se rellena |
| un hueco en el extremo | no se extrapola nunca |

Cubren D38, D45 y buena parte de D47 sin tocar una foto. Para `escala.py` la
prueba es aritmética pura: dos rectas y dos rangos conocidos dan una
transformación calculable a mano.

### El nivel −1 como prueba de regresión

El generador de material del nivel −1 ya existe y tiene verdad perfecta, así que
sirve de prueba automática de punta a punta:

```
generar N gráficas → extraer → comparar contra su verdad → error mediano < 2%
```

Falla si alguien rompe el rastreo. Es regresión sobre la métrica, no sobre el
código.

**Con un matiz:** pasar el nivel −1 **no dice que el extractor sirva.** Son
gráficas generadas por nuestro propio motor, sin ruido, sin papel y sin mano. Es
la prueba de que no está roto, no de que funciona.

### Lentas, bajo demanda — `ctex-medir`

```
ctex-medir corpus/nivel-1/ --informe medicion.md
```

Reporta el **error por condición** y no solo el global, con C4 fuera del
veredicto (D41), y el **error de los puntos medidos separado del de los
rellenos** (D45).

> **Las pruebas rápidas verifican que el código hace lo que dijimos.
> `ctex-medir` verifica que lo que dijimos sirve.** Un extractor puede tener las
> primeras en verde y reprobar I1a. No son la misma pregunta.

## 9. Los números que están por calibrar

Todos estos son conjeturas. Se listan juntos para que nadie los confunda con
resultados.

| Número | Dónde | Cómo se calibra |
|---|---|---|
| 30% de columnas con valor | umbral de fallo del rastreo | con el nivel −1: cuánto barre una gráfica limpia |
| 15° | ángulo máximo de rectificación | con el nivel 0, que aísla la cámara |
| 1% del ancho | hueco máximo que se rellena | `ctex-medir`, comparando el error de rellenos contra medidos |
| 0.5 | confianza marcador | no se calibra: se reemplaza en la fase 2 |
| 20–50 | puntos del remuestreo | heredado de la Sección 6 del motor |

## 10. Lo que no entra en esta fase

- El clasificador de dígitos y la lectura de escala (I1b).
- La segmentación: localizar la gráfica dentro de una hoja.
- La normalización de página completa, que se va con la segmentación (D40).
- El aparato de confianza y su calibración: es la fase 2.
- C++ en el rastreador. D38 revocó esa excepción de D11.
