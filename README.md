# C-tex

Servicio que convierte documentos capturados —fotografía, papel escaneado— en
PDF profesional compuesto con LaTeX.

> **Estado al 2026-07-26: el motor va de imagen a PDF, de punta a punta.** Una
> foto de una gráfica entra, sale un PDF con la curva redibujada por pgfplots.
> 205 pruebas, 50 decisiones registradas.
>
> **Pero la pregunta que decide el proyecto sigue sin respuesta.** El extractor
> mide 0.35% de error mediano contra material sintético — generado por nuestro
> propio motor, sin ruido, sin papel y sin mano. Eso prueba que **no está roto**,
> no que sirva. Quien responde I1 son 24 gráficas dibujadas a mano que todavía no
> existen.
>
> **El motor es propio (D28).** El reconocimiento corre en nuestro servidor, con
> nuestro código y nuestros pesos. No llama a la API de nadie.

## Probarlo

```bash
python -m venv .venv
.venv\Scripts\activate          # en Git Bash: source .venv/Scripts/activate
pip install -e ".[dev]"

python -m pytest                 # 205 pruebas
```

**El motor de salida**, de un JSON del contrato a un PDF:

```bash
ctex tests/datos/hoja_ejemplo.json --salida ./salida
```

Sale `salida/documento.pdf` con el título, la ecuación numerada y la gráfica.
Junto a él queda `documento.tex`, que es del usuario.

**El material de prueba**, que el propio motor genera con verdad exacta:

```bash
python -m ctex.material.generar --cuantas 3 --semilla 1 --salida ./salida/corpus
```

**El extractor**, de un recorte de gráfica al contrato:

```bash
ctex-extraer ./salida/corpus/000.png --escala-x 0,10 --escala-y -1,11 \
             --salida hoja.json
ctex hoja.json --salida ./salida
```

Requiere [Tectonic](https://tectonic-typesetting.github.io/) y `pdftoppm` en el
PATH. Sin ellos, **las pruebas que compilan se saltan solas** — y un `skipped` no
es un `passed`.

## La idea

Un motor de conversión con dos productos encima:

- **Plan personal**, con límite preestablecido, para estudiantes, secretarias y
  trabajadores.
- **API**, para empresas que capturan datos de forma masiva.

Los dos usan el mismo motor. Lo que los separa es la cuota, la integración y el
precio.

## El motor se construye, no se contrata

El reconocimiento es **nuestro**: nuestro código, nuestros pesos, corriendo en
nuestro servidor. El motor no llama a la API de nadie.

No es una postura ideológica, es lo que hace que el proyecto tenga sentido. Un
servicio que se limita a reenviar la foto a la API de otro no tiene nada propio
que defender: el proveedor cambia de precio, de modelo o de política, y el
producto cambia con él. Aquí el motor **es** el producto.

De las siete etapas del motor, seis eran ya código determinista propio. Con esta
decisión la séptima también lo es.

| Ganancia | |
|---|---|
| **Costo** | No hay costo por token. La página cuesta segundos de cómputo propio |
| **Confianza** | Las probabilidades del reconocedor se leen y se **calibran**, en vez de inferirse |
| **Seguridad** | Ningún contenedor necesita salida a internet |
| **Independencia** | No hay proveedor de por medio |

El costo aceptado, dicho sin adornos: reconocer matemáticas manuscritas propias
va a ser peor que un modelo de frontera, al menos al principio. **No afecta a las
gráficas**, que son el diferenciador y la incógnita principal.

## Por qué LaTeX y no un OCR más

La diferencia está en las gráficas. El extractor no devuelve un dibujo: devuelve
**los valores** —rango de ejes, escala, puntos de cada serie, etiquetas— y
pgfplots la dibuja. Eso hace que la gráfica quede:

- **editable**, porque el usuario corrige un dato mal leído, no un trazo;
- **consistente** con el resto del documento, con la misma tipografía, colores y
  rejilla que las demás gráficas;
- **verificable**, porque el dato extraído se puede contrastar contra la imagen
  original. Contra un vector opaco eso no se puede hacer.

Los dibujos, las ilustraciones y las firmas sí se vectorizan, porque ahí no hay
datos que extraer, solo geometría.

## Arquitectura, en dos etapas

| Etapa | Entrada | Salida | Cómo se prueba |
|---|---|---|---|
| **Extracción** | Imagen | Contenido estructurado: texto, ecuaciones, datos de gráficas, vectores | Se le mete una imagen y se verifica la salida |
| **Composición** | Contenido estructurado | LaTeX y PDF | Se le mete contenido y se verifica que compile |

La estructura, la jerarquía, los flotantes y la tipografía los decide LaTeX.

## Subsistemas

1. **Motor de conversión** — imagen a contenido estructurado a LaTeX a PDF.
2. **Plataforma web** — subir, revisar y corregir, descargar.
3. **Cobro y membresías.**
4. **API pública** — llaves, cuotas, trabajos asíncronos, facturación por uso.

El motor es la dependencia de los otros tres. El orden de construcción está por
decidir.

## Documentación

Si llegas nuevo al proyecto, léelas en este orden:

| # | Documento | Qué contiene |
|---|---|---|
| 1 | [**Diseño del motor**](docs/superpowers/specs/2026-07-21-motor-conversion-latex-design.md) | La especificación: **qué** se va a construir. Arquitectura, contrato entre etapas, seguridad y criterios de éxito |
| 2 | [Registro de decisiones](docs/planeacion/notas-plan.md) | **Por qué** el proyecto es así. Las 50 decisiones con su razonamiento, los riesgos y lo que quedó aparcado |
| 3 | [Diseño del extractor](docs/superpowers/specs/2026-07-26-extractor-graficas-design.md) | La fase 1 en detalle: los siete pasos, el contrato de salida, y **los números que están por calibrar**, listados aparte para que nadie los confunda con resultados |
| 4 | [Mapa del proceso](MAPA-DEL-PROCESO.txt) | **Cómo se trabaja**, con diagramas: el lazo de una decisión, el embudo de pregunta a código, y qué documento contesta qué pregunta |
| 5 | [Proceso de desarrollo](docs/planeacion/proceso-de-desarrollo.md) | Cómo se pasa del diseño al producto. Las ocho etapas y cómo se sabe que terminó |
| 6 | [Licencias de datos (R4)](docs/planeacion/r4-licencias-datos.md) | Qué conjuntos de entrenamiento existen y **cuáles permiten uso comercial**, con la URL donde se verificó cada licencia |
| 7 | [Antecedente](docs/planeacion/antecedente-m14.md) | De dónde salió la idea y qué objeción tuvo que superar para existir |

Con leer el documento 1 tienes el contexto suficiente para hablar del proyecto.
El 2 es para cuando quieras discutir una decisión: ahí está el argumento
completo, incluidas las alternativas que se descartaron y por qué.

**Y si vas a retomar el trabajo**, empieza por
[`SIGUIENTE-SESION.txt`](SIGUIENTE-SESION.txt), que dice dónde se quedó todo.

## Las dos incógnitas

El proyecto se construye en el orden que resuelve primero lo que puede matarlo.
Todo lo demás depende de estas dos preguntas, que hoy no tienen respuesta:

- **I1** — ¿se pueden extraer los valores de una gráfica dibujada a mano con
  precisión suficiente para que valga la pena?
- **I2** — ¿la confianza que reporta el sistema es fiable, o dice "seguro"
  cuando se equivoca?

Si alguna resulta que no, el proyecto cambia de forma. Por eso se construye
primero el motor solo, por línea de comandos, sin plataforma ni cobro.

**Y dentro del motor, primero las gráficas.** De los siete pasos que hacen falta
para leer una gráfica, solo uno reconoce algo, y lo que reconoce son dígitos:
`0`, `5`, `10`. Los otros seis son visión clásica y aritmética. Eso significa que
**las dos incógnitas se pueden responder sin entrenar nada más que un
clasificador de dígitos** — antes de emprender el reconocedor de ecuaciones, que
es la parte larga.

| Fase | Qué | Qué responde | Estado |
|---|---|---|---|
| 0 | Licencias de datos, y generar el material de prueba | Un riesgo bloqueante | licencias **hechas** (D33); falta dibujar el corpus |
| 1 | Extractor de gráficas | **I1** | **el camino existe y mide**; falta el material real |
| 2 | Aparato de confianza y su calibración | **I2** | — |
| 3 | Reconocedor de ecuaciones | — | — |
| 4 | Reconocedor de prosa | — | — |

De la fase 0 salió que **no hay conjunto de matemáticas manuscritas de uso
comercial** salvo uno, así que el clasificador de dígitos se entrena con datos
sintéticos propios y el de ecuaciones parte de pesos abiertos. El detalle, con
las licencias verificadas una por una, está en el documento 6.

### Lo que bloquea hoy

Las 24 gráficas del nivel 1: papel cuadriculado, seis condiciones por cuatro, con
los puntos ya elegidos y escritos en
[`corpus/nivel-1/`](corpus/nivel-1/COMO-DIBUJARLAS.txt). **Es el único trabajo del
proyecto que no puede hacer una máquina**, y sin él I1 no tiene respuesta.

No hacen falta las 24 para empezar: con las cuatro de la condición C1 ya se mide
el caso fácil, y si ahí falla no hay que dibujar las otras veinte.

## Un segundo frente: libro impreso

Además del cuaderno manuscrito existe `ctex-libro`, que convierte páginas de un
PDF **con capa de texto** al mismo contrato. No reconoce nada — el texto ya
viene—, así que comparte toda la mitad de atrás del motor y nada de la de
adelante.

```bash
ctex-libro libro.pdf --paginas 40-44 --salida hoja.json
ctex hoja.json --salida ./salida
```

Quita encabezados y pies, separa párrafos y detecta títulos y tablas, todo por
**geometría** y nunca por el contenido del texto.

> **Su techo está medido y escrito en D50.** Se sostiene sobre ocho constantes
> ajustadas a mano sobre seis páginas de un libro, y comparado contra un modelo
> de maquetado pierde en listas, figuras y código. Para ir en serio hay que
> cambiar de método, no agregar un noveno umbral.

## Nombre

`C-tex` es el nombre del prototipo y **está descartado**: se lee como el lenguaje
C. Finalistas: **Scan2PDF** y **SnapTeX**. Sin veredicto.
