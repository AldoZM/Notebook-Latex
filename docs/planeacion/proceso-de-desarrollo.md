# Cómo se construye este proyecto

Este documento no dice **qué** se construye —eso está en la
[especificación](../superpowers/specs/2026-07-21-motor-conversion-latex-design.md)—
ni **por qué** —eso está en el [registro de decisiones](notas-plan.md)—.

Dice **cómo se pasa de un diseño aprobado a un producto terminado**: qué etapas
hay, qué produce cada una, y cómo se sabe que una etapa acabó y empieza la
siguiente.

- **Escrito:** 2026-07-22
- **Para releerse:** cada vez que no esté claro qué toca hacer ahora

---

## Dónde estamos

Conviene decirlo con precisión, porque es fácil subestimarlo: **la planificación
ya terminó.** Lo hecho hasta ahora tiene nombre propio y son etapas completas.

| Lo hecho | Cómo se llama |
|---|---|
| Banco de ideas, filtro de sustitución por IA, "soy mi propio usuario" | Validación de la idea |
| Las 30 decisiones con su razonamiento | Registro de decisiones de arquitectura |
| Las siete etapas, el contrato, seguridad, criterios de éxito | Diseño técnico |
| I1, I2, R1–R6 | Análisis de riesgos |

Lo que falta es el **plan de implementación**, y luego construir.

---

## El ciclo real, no el de los libros

La versión de libro de texto —planificación, diseño, implementación, pruebas,
despliegue, mantenimiento— describe cómo se **documenta** un proyecto terminado,
no cómo se hace uno. En la práctica:

```
        ┌─────────────────────────────────────┐
        ▼                                     │
    diseñar → construir → medir → aprender ───┘
        ▲                            │
        └──── y a veces, revocar ────┘
```

Este proyecto ya dio una vuelta completa a ese ciclo **antes de escribir una
línea de código**: se diseñó, se aprendió algo (que el motor debía ser propio) y
se revocaron cinco decisiones. Eso no fue un fallo de planificación, fue el ciclo
funcionando.

> **La diferencia entre un proyecto sano y uno enfermo no es cuántas veces cambia
> de opinión, es cuánto cuesta cada cambio.**

El contrato de la Sección 5 existe para que cambiar la etapa 3 cueste una etapa y
no el sistema entero. **Esa propiedad es la que hay que proteger durante toda la
construcción.** Cada vez que algo tenga la tentación de saltarse el contrato,
recordar que es lo que hace baratos los errores.

---

## Las ocho etapas

| # | Etapa | Produce | Terminada cuando |
|---|---|---|---|
| 1 | Validación | ¿Vale la pena y soy yo el usuario? | Hay una objeción identificada y respondida |
| 2 | Diseño | Especificación + decisiones | Un lector nuevo puede discutir el proyecto sin preguntarte nada |
| 3 | **Plan de implementación** | Tareas ordenadas, con dependencias y criterio de terminado | Se puede empezar a trabajar sin volver a decidir nada |
| 4 | Andamiaje | Repositorio, estructura, pruebas corriendo | Un comando ejecuta las pruebas y pasan, aunque sean triviales |
| 5 | Caminata esquelética | El camino más delgado de punta a punta | Sale un PDF real desde una entrada de mentiras |
| 6 | Construcción por fases | Las fases 0–4 de D30 | Cada fase, por su criterio propio |
| 7 | Medición | Los números de I1 e I2 | Un comando devuelve las métricas y el diagrama de fiabilidad |
| 8 | Producto | Plataforma, cobro, API | Fuera del alcance del motor |

Las etapas 1 y 2 están hechas. Lo que sigue se detalla abajo.

---

## Etapa 3 — El plan de implementación

**No es un calendario ni una lista de deseos.** Es la especificación partida en
pedazos que se pueden terminar y verificar de uno en uno.

### Anatomía de una tarea

Una tarea sirve si cumple tres cosas:

1. **Cabe en una sesión de trabajo.** Si toma dos semanas, no es una tarea: es
   una fase mal partida. Lo que tarda mucho sin producir nada verificable es
   donde se pierde el hilo, sobre todo trabajando solo.
2. **Dice de qué depende.** Para saber qué se puede hacer hoy y qué está
   bloqueado.
3. **Tiene criterio de terminado.** No "hacer el compositor de ecuaciones", sino
   qué tiene que ser cierto para poder tacharla.

Así se ve una tarea de verdad:

```
T-12 · Compositor: bloque `ecuacion` → LaTeX
Depende de: T-08 (esquema del contrato, validable)

Terminada cuando:
  - un JSON con un bloque `ecuacion` produce \begin{equation}…\end{equation}
  - los caracteres & % _ # en el contenido salen escapados
  - un bloque de tipo inventado se salta con advertencia, no revienta
  - existe una prueba automática que verifica lo anterior y pasa
```

> Ese criterio de terminado no se inventó: sale de las tres reglas del contrato
> (Sección 5) y de las pruebas rápidas (Sección 11).
>
> **Un buen plan de implementación no agrega requisitos nuevos: traduce a algo
> tachable los que ya están escritos.** Si al planear aparece un requisito que no
> estaba en la especificación, es señal de que falta una decisión, no de que
> falte una tarea.

---

## Etapa 4 — El andamiaje

Antes de construir nada del motor: el repositorio con su estructura, el gestor de
dependencias, el ejecutor de pruebas, y **una prueba trivial que pase**.

Parece tiempo perdido y no lo es. Es lo que hace que a partir de ahí cada tarea
termine con "y la prueba pasa" en vez de "y creo que funciona".

---

## Etapa 5 — La caminata esquelética

**El primer código no es el extractor.** El instinto dice empezar por la fase 1,
las gráficas. Se empieza antes por las **etapas 6 y 7 — composición y
compilación**:

```
JSON a mano  →  validador  →  compositor  →  Tectonic  →  PDF
```

Sin imágenes, sin reconocimiento, sin gráficas. Cuatro razones:

| | |
|---|---|
| **Se prueba sin una sola imagen** | La Sección 11 ya lo pide: *"JSON escrito a mano → composición → compila"*. El JSON de ejemplo de la Sección 5 sirve tal cual |
| **Convierte el contrato en código** | Hoy el contrato es un documento. Con un validador de esquema y un compositor que lo consuma, se vuelve ejecutable — y los huecos que ningún documento revela aparecen en veinte minutos |
| **Le da a la fase 1 dónde entregar** | Cuando el extractor empiece a producir números, ya existe la tubería que los convierte en PDF. Si no, produce JSON al vacío |
| **Hay un PDF visible la primera semana** | No es cosmético. D9 aceptó el costo de que *"durante un buen rato no habrá nada que enseñarle a nadie"*. Esto lo acorta a días, y un proyecto largo que no enseña nada se abandona |

Se llama caminata esquelética: **el camino más delgado que atraviesa el sistema
completo y funciona de verdad, aunque casi todo sea de mentiras.** Después se le
cambia el primer eslabón por el extractor real.

---

## Etapa 6 — La construcción por fases

Las fases son las de D30. Lo que aplica a todas:

- **Rebanadas verticales, no horizontales.** No construir toda la etapa 1, luego
  toda la 2, luego toda la 3. Construir un camino delgado que atraviese todas y
  engordarlo. Lo horizontal deja seis etapas al 80% y nada que funcione.
- **La prueba primero, en lo determinista.** En composición, compilación,
  escalado y remuestreo la respuesta correcta se conoce de antemano: la prueba se
  escribe antes que el código. En el reconocedor no aplica igual — ahí no se
  prueba exactitud, se miden métricas contra un conjunto de validación.
- **Ramas y commits chicos.** Una rama por tarea, commits legibles después. Es lo
  que permite retroceder cuando una decisión resulte equivocada, y alguna lo
  será.
- **Cuando el código contradiga al diseño, gana el código — pero se anota.** El
  mecanismo ya está montado: una decisión nueva que revoca la vieja, con su
  motivo. **No se edita el pasado.**

---

## Etapa 7 — La medición

Tiene una regla que la Sección 11 ya dejó escrita y que conviene repetir aquí
porque es la que más fácil se incumple:

> **Si medir es trabajoso, no se mide.**

I1, I2 y el cronómetro de las diez páginas tienen que salir de **ejecutar un
comando**, no de un procedimiento manual. La suite de medición es parte del
producto de la fase 2, no un extra.

---

## Cómo se sabe que terminó

"Terminar" significa tres cosas distintas según de qué se hable. Vale la pena no
confundirlas.

### El motor termina cuando cumple los tres criterios de la Sección 11

1. **I1** — error mediano por punto menor al 2% del rango, ningún punto por
   encima del 5%, escala correcta en más del 95% de las gráficas.
2. **I2** — de lo marcado con confianza mayor a 0.90, al menos el 97% correcto;
   error de calibración esperado por debajo de 0.10; al menos el 90% de los
   errores debieron haber generado duda.
3. **La promesa del producto** — diez páginas reales toman **menos de la mitad**
   del tiempo que tipografiarlas a mano.

El tercero es el que de verdad importa, porque es el único que mide lo que el
usuario compra. Un motor con métricas excelentes que deja al usuario contestando
cuarenta dudas por página es un motor que nadie va a pagar.

**Si los tres se cumplen, el motor está terminado y empieza el subsistema 2.**
Si alguno no se cumple, el proyecto cambia de forma — y para eso se construyó en
este orden.

### La v1 termina cuando el motor funciona por línea de comandos

Sin web, sin cuentas, sin cobro (D9). Es un hito interno, no algo que se lance.

### El producto no termina: se lanza

Después vienen los subsistemas 2, 3 y 4 —plataforma, cobro, API—, cada uno con su
propia especificación y su propia vuelta a este mismo ciclo. Un servicio vivo no
tiene estado "terminado", tiene estado "estable".

---

## Qué NO es este documento

- **No es un calendario.** No hay fechas y no debería haberlas hasta que la fase 1
  dé una idea real de cuánto cuesta una tarea de este proyecto. Estimar antes de
  haber construido nada es inventar.
- **No es un contrato.** Si al construir resulta que una etapa sobra o que hacen
  falta dos, se cambia este documento — con su nota de qué cambió y por qué, igual
  que el registro de decisiones.
