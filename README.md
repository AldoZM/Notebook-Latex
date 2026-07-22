# C-tex

Servicio que convierte documentos capturados —fotografía, papel escaneado— en
PDF profesional compuesto con LaTeX.

> **Estado: diseño del motor aprobado.** No hay código todavía. Sigue el plan de
> implementación.

## La idea

Un motor de conversión con dos productos encima:

- **Plan personal**, con límite preestablecido, para estudiantes, secretarias y
  trabajadores.
- **API**, para empresas que capturan datos de forma masiva.

Los dos usan el mismo motor. Lo que los separa es la cuota, la integración y el
precio.

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
| 2 | [Registro de decisiones](docs/planeacion/notas-plan.md) | **Por qué** el proyecto es así. Las 22 decisiones con su razonamiento, los riesgos y lo que quedó aparcado |
| 3 | [Antecedente](docs/planeacion/antecedente-m14.md) | De dónde salió la idea y qué objeción tuvo que superar para existir |

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

## Nombre

`C-tex` es el nombre del prototipo y está abierto a cambio.
