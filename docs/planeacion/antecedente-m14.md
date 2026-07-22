# Antecedente — de dónde salió esta idea

> Escrito el 2026-07-21, antes del pivote a servicio. Se conserva sin cambios de
> fondo porque explica la objeción que el proyecto tuvo que superar para
> existir, y esa objeción sigue siendo la razón de varias decisiones del diseño.

La idea nació como **M14** dentro de un banco de ~60 ideas de proyecto
(`D:\Codigo Abierto\Ideas-tintero`), descrita en una línea:

> *Foto del cuaderno con ecuaciones y sale código LaTeX compilable.*

## La objeción que hubo que resolver

**Eso ya lo hace un modelo de visión hoy.**

Si el proyecto fuera eso y nada más, sería una envoltura: el modelo está dentro
del ciclo, mejora solo sin que nadie haga nada, y no queda aporte propio que no
se pueda reemplazar con una llamada a una API.

Cae exactamente en el primer filtro que Aldo aplica al evaluar un proyecto:

> **Sustitución por IA.** No basta con que el código sea difícil. Si el valor
> está en razonar una vez sobre algo, un modelo lo hace mejor y más barato.
> Sobreviven los proyectos donde el modelo no puede estar presente mientras el
> programa corre: tiempo real, hardware físico, sin internet, determinismo.

En cambio, la idea **sí** pasaba el filtro de validación sin discusión: Aldo es
su propio usuario, tiene cuadernos reales que fotografiar y tres corpus LaTeX
propios ya escritos —Japonés N5-N4, Estructuras de Datos, Amazon en C++—.

Así que la pregunta nunca fue *"¿sirve la idea?"*. Fue:

> **¿Qué construye Aldo, y qué deja que haga el modelo?**

## Las cuatro respuestas que se plantearon

Contexto que sostiene las cuatro: cuando un modelo devuelve LaTeX de una foto
pasan tres cosas que el modelo **no** resuelve. Sale con macros genéricas que no
son las tuyas. No siempre compila. Y verificar que transcribió bien la ecuación
toma casi tanto tiempo como haberla escrito a mano.

### 1. El ciclo de corrección

El modelo transcribe, pero el trabajo propio es la interfaz que vuelve trivial
verificar y corregir: foto y LaTeX renderizado lado a lado, tocar un símbolo
dudoso y arreglarlo al instante. El valor está en que revisar 40 ecuaciones tome
dos minutos y no veinte. Ingeniería de interfaz, no de modelo.

### 2. El compilador en el ciclo

Lo que sale del modelo se compila de verdad. Si no compila, se repara
automáticamente y se reintenta hasta que sí. Determinista y verificable.
Sobrevive el filtro porque quien está en el ciclo de ejecución es el compilador,
no el modelo.

### 3. Las convenciones propias

El sistema conoce el preámbulo y las macros de cada corpus, y emite LaTeX que
encaja en **ese** documento, en el capítulo correcto. Un modelo genérico no sabe
qué macros usa Aldo.

### 4. Sin internet, en el dispositivo

Reconocimiento corriendo local, sin llamadas a ninguna API. Contra: la calidad
del reconocimiento de matemáticas manuscritas en el dispositivo hoy es
notablemente peor.

## Qué pasó con cada una

| | Respuesta | Destino |
|---|---|---|
| 1 | El ciclo de corrección | **Viva**, transformada en revisión dirigida por confianza (D8) |
| 2 | El compilador en el ciclo | **Viva**, es la etapa 7 del motor (D17) |
| 3 | Las convenciones propias | **Viva**, pero se convirtió en *perfiles de documento* de la plataforma, no del motor (D16) |
| 4 | Sin internet, en el dispositivo | **Descartada** por el pivote a servicio: un servicio de paga no corre el modelo en la máquina del cliente |

Y apareció una quinta respuesta que no estaba en la lista original, que terminó
siendo la principal: **extraer las gráficas como datos y dejar que pgfplots las
dibuje** (D3). Es la que responde el filtro de sustitución por IA de forma más
limpia, porque ahí LaTeX no es intercambiable por una llamada a un modelo.

## Ideas hermanas que quedaron en el banco

Comparten corpus con esta y podrían acabar siendo el mismo producto:

- **Idea 20** — buscador semántico de apuntes propios. Indexa los PDF con
  incrustaciones locales y responde citando página.
- **Idea 36** — convertir los apuntes en un sitio interactivo.
- **Idea 21** — registro de práctica de escritura de kanji, con comparación de
  trazos.
- **Idea 4** — aplicación de repaso de japonés con repetición espaciada, que ya
  aprovecha los apuntes N5-N4.
