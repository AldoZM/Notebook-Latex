# C-tex

Servicio que convierte documentos capturados —fotografía, papel escaneado— en
PDF profesional compuesto con LaTeX.

> **Estado: planificación.** No hay código todavía. El diseño se está puliendo
> en `docs/planeacion/notas-plan.txt`.

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

- [`docs/planeacion/notas-plan.txt`](docs/planeacion/notas-plan.txt) — decisiones
  tomadas, riesgos marcados y lo que falta por decidir. Archivo vivo.
- [`docs/planeacion/antecedente-m14.txt`](docs/planeacion/antecedente-m14.txt) —
  de dónde salió la idea y qué objeción tuvo que superar.
- `docs/superpowers/specs/` — las especificaciones, cuando el diseño se apruebe.

## Nombre

`C-tex` es el nombre del prototipo y está abierto a cambio.
