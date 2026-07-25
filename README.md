# C-tex

Servicio que convierte documentos capturados —fotografía, papel escaneado— en
PDF profesional compuesto con LaTeX.

> **Estado al 2026-07-25: la mitad de atrás del motor existe y compila.** Un JSON
> del contrato produce un PDF de verdad, con la gráfica dibujada por pgfplots. 89
> pruebas. Lo que falta es la mitad de adelante: de la imagen al contrato.
>
> **El motor es propio (D28).** El reconocimiento corre en nuestro servidor, con
> nuestro código y nuestros pesos. No llama a la API de nadie.

## Probarlo

```bash
python -m venv .venv
.venv\Scripts\activate          # en Git Bash: source .venv/Scripts/activate
pip install -e ".[dev]"

python -m pytest                 # 89 pruebas
ctex tests/datos/hoja_ejemplo.json --salida ./salida
```

Sale `salida/documento.pdf` con el título, la ecuación numerada y la gráfica.
Junto a él queda `documento.tex`, que es del usuario.

Requiere [Tectonic](https://tectonic-typesetting.github.io/) en el PATH. Sin él,
las pruebas que compilan se saltan solas y el comando no funciona.

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
| 2 | [Registro de decisiones](docs/planeacion/notas-plan.md) | **Por qué** el proyecto es así. Las 33 decisiones con su razonamiento, los riesgos y lo que quedó aparcado |
| 3 | [Proceso de desarrollo](docs/planeacion/proceso-de-desarrollo.md) | **Cómo** se pasa del diseño al producto. Las ocho etapas, qué produce cada una y cómo se sabe que terminó |
| 4 | [Licencias de datos (R4)](docs/planeacion/r4-licencias-datos.md) | Qué conjuntos de entrenamiento existen y **cuáles permiten uso comercial**, con la URL donde se verificó cada licencia |
| 5 | [Antecedente](docs/planeacion/antecedente-m14.md) | De dónde salió la idea y qué objeción tuvo que superar para existir |

Con leer el documento 1 tienes el contexto suficiente para hablar del proyecto.
El 2 es para cuando quieras discutir una decisión: ahí está el argumento
completo, incluidas las alternativas que se descartaron y por qué.

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
| 0 | Verificar qué datos de entrenamiento existen y **bajo qué licencia** | Un riesgo bloqueante | **hecha** (D33) |
| 1 | Extractor de gráficas completo | **I1** | siguiente |
| 2 | Aparato de confianza y su calibración | **I2** | — |
| 3 | Reconocedor de ecuaciones | — | — |
| 4 | Reconocedor de prosa | — | — |

De la fase 0 salió que **no hay conjunto de matemáticas manuscritas de uso
comercial** salvo uno, así que el clasificador de dígitos se entrena con datos
sintéticos propios y el de ecuaciones parte de pesos abiertos. El detalle, con
las licencias verificadas una por una, está en el documento 4.

## Nombre

`C-tex` es el nombre del prototipo y está abierto a cambio.
