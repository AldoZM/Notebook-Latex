# R4 — Licencias de datos y pesos para los tres reconocedores

**Fecha de la investigación:** 25 de julio de 2026
**Alcance:** verificación de licencias en fuente primaria para conjuntos de datos y pesos abiertos aplicables a un servicio comercial de pago.
**Advertencia:** este documento es investigación técnica, no asesoría legal. Antes de comprometer presupuesto de entrenamiento conviene una revisión legal de los tres o cuatro conjuntos que se elijan.

---

## 1. Veredicto en tres líneas

1. **Dígitos y signos (13 clases): SÍ, camino limpio.** Hay al menos tres rutas independientes sin restricción comercial — datos sintéticos con tipografías SIL OFL, NIST Special Database 19 (obra del gobierno de Estados Unidos), y el conjunto optdigits de UCI bajo CC BY 4.0. No hay razón para tocar MNIST ni EMNIST.
2. **Ecuaciones manuscritas a LaTeX: SÍ, pero por un solo camino y estrecho.** Todos los conjuntos famosos del área (CROHME, MathWriting, HME100K) prohíben el uso comercial. El único conjunto de expresiones manuscritas con licencia comercial verificada es **Aida Calculus (CDLA-Sharing-1.0)**, y está limitado a un dominio (límites de cálculo). Se complementa con IM2LATEX-100K (CC0, pero impreso, no manuscrito) y con generación sintética propia.
3. **Prosa manuscrita: CON CONDICIONES, y es el caso más pobre.** IAM, RIMES e Imgur5K —los tres estándares— son todos no comerciales. Queda **GNHK bajo CC BY 4.0** y NIST SD19, más generación sintética. Es suficiente para arrancar pero no para igualar el estado del arte.

**Consecuencia de negocio inmediata:** R4 no bloquea la fase 1 (dígitos). Sí condiciona fuertemente la fase 2 (ecuaciones), donde el plan realista es **partir de pesos abiertos permisivos y afinar con datos propios y sintéticos**, no entrenar desde cero con datos públicos.

---

## 2. Tabla por conjunto de datos

| Conjunto | Para qué sirve | Licencia exacta | ¿Uso comercial? | Tamaño aproximado | Fuente donde se verificó |
|---|---|---|---|---|---|
| **NIST Special Database 19** | Dígitos, prosa (letra de molde) | Sin licencia explícita en la ficha; aplica la política general de NIST: obras de empleados de NIST no tienen protección de copyright en Estados Unidos, con derecho concedido a preparar obras derivadas y distribuir, exigiendo atribución | **Sí** (con atribución) | 810,000 imágenes de caracteres, 3,600 escritores | [nist.gov/open/license](https://www.nist.gov/open/license) · [ficha SD19](https://www.nist.gov/srd/nist-special-database-19) · [registro PDR](https://data.nist.gov/od/id/ark:/88434/mds00tf5pn) |
| **UCI Optical Recognition of Handwritten Digits (optdigits)** | Dígitos | Creative Commons Attribution 4.0 International (CC BY 4.0) | **Sí** (con atribución) | 5,620 instancias, rasgos 8×8 enteros 0–16 | [archive.ics.uci.edu/dataset/80](https://archive.ics.uci.edu/dataset/80/optical+recognition+of+handwritten+digits) |
| **MNIST** | Dígitos | **Conflictiva.** La página oficial de LeCun no fue accesible durante la investigación. Un espejo académico afirma CC BY-SA 3.0; la ficha de Hugging Face del propio autor afirma MIT; el registro de UCI dice "consultar el conjunto original". | **No verificado** | 70,000 imágenes 28×28 | [pymvpa.org/datadb/mnist.html](https://www.pymvpa.org/datadb/mnist.html) · [huggingface.co/datasets/ylecun/mnist](https://huggingface.co/datasets/ylecun/mnist) · [UCI 683](https://archive.ics.uci.edu/dataset/683/mnist+database+of+handwritten+digits) |
| **EMNIST** | Dígitos, letras | **CC BY-ND 4.0** (Attribution-NoDerivatives), titular Western Sydney University. Las páginas de NIST y el readme oficial **no declaran licencia alguna**. | **Condicionado y riesgoso** — CC BY-ND permite uso comercial de la obra *sin modificar*, pero prohíbe distribuir material adaptado | ~814,000 caracteres, hasta 62 clases | [researchdata.edu.au/…/2368050](https://researchdata.edu.au/extended-mnist-emnist-dataset/2368050) · [researchers.westernsydney.edu.au](https://researchers.westernsydney.edu.au/en/datasets/extended-mnist-emnist-dataset/) · [readme NIST](https://biometrics.nist.gov/cs_links/EMNIST/Readme.txt) |
| **Detexify (datos de muestra)** | Símbolos matemáticos sueltos, dígitos | Open Database License (ODbL) | **Sí**, con copyleft sobre la base de datos | No declarado en el repositorio (los datos viven en Google Drive) | [github.com/kirel/detexify-data](https://github.com/kirel/detexify-data) |
| **HWRT database of handwritten symbols** | Símbolos matemáticos, alfanuméricos, griegos, flechas | ODC Open Database License v1.0 | **Sí**, con copyleft sobre la base de datos | Conteo de clases no declarado en la ficha | [zenodo.org/records/50022](https://zenodo.org/records/50022) |
| **Aida Calculus Math Handwriting Recognition Dataset** | **Ecuaciones** | **CDLA-Sharing-1.0** (Community Data License Agreement – Sharing v1.0). Propietario: Aida by Pearson. | **Sí** — y la cláusula 3.5 exime explícitamente a los "Results" (modelos entrenados) del copyleft | 100,000 imágenes sintéticas, ~13.8 GB, con LaTeX, cajas delimitadoras y máscaras por carácter | [API de Kaggle, campo licenseName](https://www.kaggle.com/api/v1/datasets/view/aidapearson/ocr-data) · [espejo en HF](https://huggingface.co/datasets/deepcopy/Aida-Calculus-Math-Handwriting) · [texto CDLA](https://cdla.dev/sharing-1-0/) |
| **IM2LATEX-100K** | Ecuaciones (**impresas**, no manuscritas) | Creative Commons Zero v1.0 Universal (CC0) | **Sí**, sin condiciones | ~100,000 fórmulas, 306.8 MB | [zenodo.org/records/56198](https://zenodo.org/records/56198) |
| **CROHME** (ICFHR/ICDAR, todas las ediciones) | Ecuaciones | CC BY-NC-SA (3.0 Unported en la sede histórica, 4.0 en el depósito de Curtin). Texto literal de la sede oficial: *"All data and tools provided here are freely available only for research purpose without any commercial use."* | **No** | CROHME23: 164,000 trazos, 102,000 etiquetas distintas, 105 tokens | [isical.ac.in/~crohme/CROHME_data.html](https://www.isical.ac.in/~crohme/CROHME_data.html) · [researchdata.edu.au/…/639782](https://researchdata.edu.au/crohme-competition-recognition-expressions-png/639782) |
| **MathWriting (Google)** | Ecuaciones | Texto literal: *"The data is licensed by Google LLC under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International license."* | **No** | 650,000 muestras (230,000 humanas + 400,000 sintéticas), 2.9 GB | [github.com/google-research/…/mathwriting/README.md](https://github.com/google-research/google-research/blob/master/mathwriting/README.md) · [arxiv 2404.10690](https://arxiv.org/html/2404.10690v1) |
| **HME100K (TAL / 好未来)** | Ecuaciones | **Sin licencia abierta declarada.** El sitio solo enlaza un "acuerdo de servicio" y un "acuerdo de privacidad", y el pie de página declara propiedad intelectual de TAL Education. | **No** (sin licencia = todos los derechos reservados) | 99,109 imágenes (74,502 entrenamiento / 24,607 prueba), 245 clases, 728.8 MB | [ai.100tal.com/dataset](https://ai.100tal.com/dataset) |
| **UniMER-1M / UniMER-Test** | Ecuaciones | Declarada **Apache 2.0** en la ficha de Hugging Face, pero el conjunto se construye a partir de CROHME y HME100K | **No** — relicenciamiento aguas abajo que no sanea la restricción de origen | >1,000,000 pares LaTeX–imagen; prueba de 23,757 muestras; 2.13 GB | [huggingface.co/datasets/wanderkid/UniMER_Dataset](https://huggingface.co/datasets/wanderkid/UniMER_Dataset) · [github.com/opendatalab/UniMERNet](https://github.com/opendatalab/UniMERNet) |
| **GNHK (GoodNotes Handwriting Kollection)** | **Prosa** | Texto literal: *"The GNHK dataset is free to download under a CC-BY-4.0 License."* | **Sí** (con atribución) | No declarado en el readme | [github.com/GoodNotes/GNHK-dataset](https://github.com/GoodNotes/GNHK-dataset/blob/main/README.md) |
| **IAM Handwriting Database** | Prosa | Sin licencia formal. Texto literal: *"The IAM Handwriting Database is publicly accessible and freely available for non-commercial research purposes."* Pide registro. | **No** | Inglés manuscrito sin restricciones, escaneado a 300 ppp | [fki.tic.heia-fr.ch/…/download-the-iam-handwriting-database](https://fki.tic.heia-fr.ch/databases/download-the-iam-handwriting-database) |
| **RIMES** | Prosa (francés) | Creative Commons Attribution Non Commercial 4.0 International. Titular actual: Mitek Systems, Inc. (por adquisición de A2iA en 2018). | **No** — pese a que la difusión de 2024 se anunció como "licencia permisiva" | 5,605 cartas manuscritas, 12,610 imágenes | [zenodo.org/records/10812725](https://zenodo.org/records/10812725) |
| **Imgur5K** | Prosa (en entorno natural) | Creative Commons Attribution-NonCommercial 4.0 International | **No** — y además las imágenes pertenecen a usuarios de Imgur, no a Meta | 8,177 imágenes de página, 230,573 imágenes de palabra | [github.com/facebookresearch/IMGUR5K-Handwriting-Dataset](https://github.com/facebookresearch/IMGUR5K-Handwriting-Dataset/blob/main/README.md) · [incidencia 6, sin respuesta](https://github.com/facebookresearch/IMGUR5K-Handwriting-Dataset/issues/6) |
| **Tipografías de Google Fonts (datos sintéticos)** | Dígitos, prosa | SIL Open Font License | **Sí** — la única restricción es no vender la tipografía como producto independiente | Cientos de familias, decenas con estilo manuscrito | [SIL Open Font License](https://en.wikipedia.org/wiki/SIL_Open_Font_License) *(ver sección 7: no verificado en fuente primaria)* |

---

## 3. Los conjuntos utilizables y qué hay que cumplir

### Para el reconocedor 1 — dígitos y signos

**NIST Special Database 19** — la mejor base real.
- Obligación: acreditar explícitamente al National Institute of Standards and Technology como fuente de los datos, en la documentación del producto o en un aviso de terceros.
- Ventaja estratégica decisiva: SD19 es el **origen** tanto de MNIST como de EMNIST. Reconstruir el preprocesamiento propio (normalización a 28×28 o al tamaño que convenga) a partir de SD19 produce un conjunto equivalente a EMNIST **sin heredar la cláusula ND** que Western Sydney University impuso sobre EMNIST. Esto elimina el problema de raíz en lugar de esquivarlo.
- Limitación: SD19 tiene dígitos y letras, pero **no** signo menos ni punto decimal. Esas dos clases hay que cubrirlas por otra vía.

**UCI optdigits** — CC BY 4.0.
- Obligación: atribución.
- Limitación: 8×8 y solo 5,620 instancias. Sirve como conjunto de validación cruzada independiente, no como conjunto de entrenamiento principal.

**Detexify y HWRT** — ODbL / ODC-ODbL.
- Obligación: atribución y, si se **publica** una base de datos derivada, publicarla bajo ODbL. El copyleft de ODbL recae sobre la base de datos, no sobre los modelos entrenados con ella; aun así, la interpretación de ODbL sobre "produced work" es menos clara que la de CDLA. Recomendación: usarlos solo si hace falta, y nunca redistribuir los datos.
- Ventaja: **sí contienen signos matemáticos**, incluido el menos, que es justo lo que le falta a SD19.

**Datos sintéticos propios** — sin obligación de licencia sobre los datos.
- Ver sección 6 para la evaluación de viabilidad.

### Para el reconocedor 2 — ecuaciones

**Aida Calculus (CDLA-Sharing-1.0)** — el hallazgo central de esta investigación.
- Obligaciones: conservar la atribución al proveedor de datos; si se **publica** el conjunto o una versión modificada de él, hacerlo bajo la misma CDLA-Sharing-1.0 sin modificar.
- Punto clave verificado: la cláusula 3.5 del CDLA-Sharing-1.0 dice literalmente *"This Agreement imposes no obligations or restrictions on Your Use or Publication of Results"*, y define "Results" como los resultados de uso computacional de los datos que no incorporen más que una porción mínima de los datos. **Un modelo entrenado es un Result.** Por lo tanto el copyleft no se contagia a los pesos ni al servicio.
- Ventaja adicional: es **sintético**, con máscaras a nivel de píxel y cajas por carácter. Eso significa cero riesgo de datos personales y anotación perfecta.
- Limitación seria: el dominio es "límites de cálculo". No cubre matrices, integrales complejas, notación de física, ni el rango de una libreta general.

**IM2LATEX-100K (CC0)**.
- Obligación: ninguna. CC0 es renuncia a derechos.
- Uso correcto: es LaTeX **renderizado**, no manuscrito. Sirve para preentrenar el **decodificador** —la parte que aprende la gramática de LaTeX y la estructura de fórmulas— antes de afinar con imágenes manuscritas. Esta es una técnica estándar y aquí es además la única legalmente cómoda.
- Salvedad honesta: las fórmulas provienen de fuentes LaTeX de artículos de arXiv. La renuncia CC0 la hizo el depositante del conjunto, no los autores de cada artículo. Como se trata de fragmentos cortos de notación matemática (poco o nada protegibles por copyright de forma individual), el riesgo práctico es bajo, pero no es un cero absoluto.

### Para el reconocedor 3 — prosa

**GNHK (CC BY 4.0)**.
- Obligación: atribución.
- Nota: los autores ofrecen retirar documentos si alguien encuentra información personal suya. Conviene registrar la versión y fecha descargada.

**NIST SD19** también sirve aquí: contiene formularios manuscritos completos, aunque en letra de molde y no cursiva.

---

## 4. Los conjuntos que hay que descartar, y por qué exactamente

| Conjunto | Motivo exacto del descarte |
|---|---|
| **CROHME** (todas las ediciones) | CC BY-NC-SA. La sede oficial lo dice dos veces y sin ambigüedad: *"freely available only for research purpose without any commercial use"*. No hay lectura alternativa. |
| **MathWriting** | CC BY-NC-SA 4.0 declarada por Google LLC en su propio repositorio. La cláusula NC lo excluye por completo. Duele porque es el conjunto más grande y mejor del área. |
| **HME100K** | Peor caso: **no declara licencia abierta**. Ausencia de licencia significa todos los derechos reservados, no permiso tácito. Además el pie del sitio reclama propiedad intelectual de TAL Education. Usarlo sería infracción directa. |
| **UniMER-1M / UniMER-Test** | Declara Apache 2.0, pero está construido sobre CROHME y HME100K. Nadie puede otorgar más derechos de los que tiene: la etiqueta Apache aguas abajo **no sanea** la cláusula NC de CROHME ni la ausencia de licencia de HME100K. Es exactamente la trampa que R4 anticipa — un conjunto que se ve limpio y no lo es. Descartar. |
| **IAM Handwriting Database** | "Non-commercial research purposes only", más registro nominal. Excluido. Consecuencia derivada: cualquier modelo afinado sobre IAM arrastra el problema (ver sección 5, TrOCR). |
| **RIMES** | CC BY-NC 4.0. Las notas de difusión de 2024 de Mitek hablan de "licencia permisiva", pero el campo de licencia del registro de Zenodo dice Non Commercial. **El campo de licencia manda sobre la nota de prensa.** Excluido. |
| **Imgur5K** | Doble problema. Uno, CC BY-NC 4.0. Dos, el conjunto solo distribuye enlaces a imágenes cuya titularidad es de Imgur o de los usuarios que las subieron; Meta nunca tuvo los derechos para sublicenciar el contenido. En la incidencia 6 del repositorio se preguntó por licencia comercial y **nadie contestó**; el repositorio se archivó en febrero de 2025. Excluido. |
| **EMNIST** | CC BY-ND 4.0. La cláusula ND prohíbe distribuir material adaptado. Aunque se puede argumentar que entrenar sin redistribuir el conjunto no viola ND, es un argumento que no conviene tener que sostener ante un cliente empresarial o en una revisión de diligencia debida. Como existe la ruta limpia por SD19, **no hay razón para asumir este riesgo**. Descartar por prudencia, no por imposibilidad. |
| **MNIST** | No se descarta por prohibición sino por **incertidumbre**: tres fuentes dan tres respuestas distintas (CC BY-SA 3.0, MIT, "consultar el original"). Además solo tiene 10 de las 13 clases necesarias. Con SD19 disponible, no aporta nada que justifique documentar una ambigüedad. |

---

## 5. Pesos abiertos (plan de contingencia)

| Modelo | Para qué | Licencia del **código** | Licencia de los **pesos** | ¿Uso comercial? | Fuente verificada |
|---|---|---|---|---|---|
| **Donut base** (naver-clova-ix) | Base visión-a-texto | MIT | **MIT** | **Sí**, limpio | [huggingface.co/naver-clova-ix/donut-base](https://huggingface.co/naver-clova-ix/donut-base) |
| **texify** (VikParuchuri) | Imagen de matemáticas → LaTeX y Markdown | — | **CC BY-SA 4.0** | **Sí, condicionado.** Construido sobre Donut (MIT) y entrenado con im2latex y datos web. El copyleft SA obliga a compartir bajo la misma licencia si se **distribuyen** pesos derivados. Servir el modelo por API no es distribución bajo CC BY-SA. | [github.com/VikParuchuri/texify](https://github.com/VikParuchuri/texify/blob/master/README.md) |
| **Pix2Text MFR** (breezedeus/pix2text-mfr) | Reconocimiento de fórmulas | MIT | **MIT** (versión libre en Hugging Face) | **Sí**, pero verificar cuál artefacto se descarga: el autor comercializa aparte modelos de pago y existió una versión de "uso personal únicamente" | [huggingface.co/breezedeus/pix2text-mfr](https://huggingface.co/breezedeus/pix2text-mfr) · [LICENSE del repositorio](https://github.com/breezedeus/Pix2Text/blob/main/LICENSE) |
| **TrOCR** (microsoft) | OCR manuscrito e impreso | MIT (proyecto unilm) | **MIT** | **Sí en licencia, con reserva en procedencia.** `trocr-base-handwritten` y `trocr-large-handwritten` están afinados sobre **IAM**, que es no comercial. La licencia MIT del peso no cura la restricción del dato de origen. Preferir las variantes `stage1` (preentrenadas con texto sintético) y afinarlas con datos propios. | [microsoft/trocr-base-handwritten](https://huggingface.co/microsoft/trocr-base-handwritten) |
| **GOT-OCR2.0** (stepfun-ai) | OCR general, incluye fórmulas | Apache 2.0 | **apache-2.0** declarada en la ficha de Hugging Face | **Sí**, con reserva: el repositorio de origen muestra una insignia de datos CC BY-NC 4.0, lo que sugiere que el corpus de entrenamiento era no comercial | [huggingface.co/stepfun-ai/GOT-OCR2_0](https://huggingface.co/stepfun-ai/GOT-OCR2_0) · [github.com/Ucas-HaoranWei/GOT-OCR2.0](https://github.com/Ucas-HaoranWei/GOT-OCR2.0) |
| **olmOCR** (allenai) | OCR de documentos con modelo visión-lenguaje | Apache 2.0 | **apache-2.0** | **Sí.** La ficha añade que está "intended for research and educational use" y remite a las guías de uso responsable de Ai2, pero Apache 2.0 permite uso comercial y esa frase no es una cláusula restrictiva del contrato de licencia. | [huggingface.co/allenai/olmOCR-7B-0725](https://huggingface.co/allenai/olmOCR-7B-0725) |
| **Nougat** (Meta) | Documentos académicos → Markdown y LaTeX | MIT | **CC-BY-NC** | **No.** Texto literal del repositorio: *"Nougat codebase is licensed under MIT. Nougat model weights are licensed under CC-BY-NC."* Caso de manual de licencia de código distinta de licencia de pesos. | [github.com/facebookresearch/nougat](https://github.com/facebookresearch/nougat) |
| **Chandra OCR 2** (datalab-to) | OCR de documentos | — | OpenRAIL-M modificada | **No para C-tex a mediano plazo**: gratuita solo para empresas por debajo de cierto umbral de financiamiento o ingresos | *(ver sección 7: no verificado en fuente primaria)* |

**Lectura de conjunto:** el plan de contingencia es sólido. **Donut (MIT) + texify (CC BY-SA 4.0) + Pix2Text MFR (MIT)** dan tres puntos de partida comercialmente viables para el reconocedor de ecuaciones, y `texify` en particular ya resuelve la tarea exacta que se busca. La combinación más limpia jurídicamente es **partir de Donut base (MIT) y afinar con Aida + IM2LATEX + datos sintéticos propios**, porque no arrastra ninguna cláusula heredada.

---

## 6. Recomendación, con orden de acción

### Reconocedor 1 — dígitos y signos (13 clases). Prioridad inmediata.

**Ruta recomendada: sintética primero, real como validación.**

1. **Generar el conjunto sintético propio.** Es la opción más viable de las tres y quita el problema de licencia por completo. Evaluación de viabilidad: **alta, casi trivial para este caso**. Las razones concretas:
   - Son 13 clases de un solo carácter (`0`–`9`, `-`, `.`, y conviene añadir `,` para notación en español). No es una tarea de vocabulario abierto.
   - Google Fonts publica bajo SIL Open Font License, que permite uso comercial; hay decenas de familias con estilo manuscrito (Caveat, Kalam, Indie Flower y similares). Renderizar 13 glifos por cada una de 40 o 60 tipografías, con aumentación (rotación leve, grosor de trazo, ruido, desenfoque, deformación elástica, fondo de papel real) produce con facilidad cientos de miles de muestras.
   - El dominio objetivo ayuda: son etiquetas de ejes de gráfica, escritas pequeñas y con cuidado, no caligrafía libre. La brecha entre lo sintético y lo real es mucho menor aquí que en prosa.
   - Coste: días de trabajo de un desarrollador, no meses. Y el conjunto queda como activo propio de la empresa.
2. **Añadir NIST SD19** reprocesado por cuenta propia, para los dígitos `0`–`9`. Aporta variación de escritores reales (3,600 personas) que lo sintético no captura. Acreditar a NIST.
3. **Cubrir `-`, `.` y `,`** con lo sintético y, si hace falta más variedad real, con Detexify o HWRT bajo ODbL, sin redistribuir.
4. **Reservar optdigits (CC BY 4.0) como conjunto de prueba independiente**, nunca de entrenamiento. Sirve para detectar sobreajuste al generador sintético.
5. **No tocar MNIST ni EMNIST.** No aportan nada que las opciones anteriores no cubran, y ambas traen ambigüedad o cláusula ND.

### Reconocedor 2 — ecuaciones manuscritas a LaTeX. Prioridad media, es el caso caro.

**Ruta recomendada: partir de pesos abiertos permisivos. No entrenar desde cero.**

1. **Base:** Donut base (MIT) o, si se acepta el copyleft de CC BY-SA sobre pesos distribuidos, texify directamente. Como C-tex servirá el modelo, no distribuirá los pesos, texify es utilizable en la práctica; aun así Donut es la opción sin condicionantes.
2. **Preentrenar el decodificador con IM2LATEX-100K (CC0).** Enseña la gramática de LaTeX sin ninguna restricción.
3. **Afinar con Aida Calculus (CDLA-Sharing-1.0).** Es el único corpus de expresiones manuscritas con permiso comercial verificado, con la cláusula 3.5 protegiendo explícitamente al modelo resultante.
4. **Construir un generador sintético de expresiones manuscritas propio**, reutilizando la infraestructura del punto 1 del reconocedor de dígitos pero componiendo expresiones completas con estructura de árbol. Esto es lo que compensa que Aida solo cubra límites de cálculo.
5. **Presupuestar la recolección de datos propios etiquetados.** Dado que los tres grandes conjuntos del área están cerrados al uso comercial, un corpus propio de expresiones manuscritas es un activo defensivo y probablemente una ventaja competitiva. Conviene empezar a recolectarlo pronto, con consentimiento explícito y cesión de derechos por escrito de quienes escriben.
6. **Nunca usar UniMER**, por más cómodo que resulte su empaquetado en Hugging Face.

### Reconocedor 3 — prosa manuscrita. Prioridad baja.

1. **GNHK (CC BY 4.0)** como base real. Atribución obligatoria.
2. **NIST SD19** para letra de molde.
3. **Generación sintética** con tipografías OFL sobre corpus de texto de dominio público en español (Wikisource, Proyecto Gutenberg, textos oficiales). Aquí la brecha entre sintético y real es mayor que en dígitos, así que esperar rendimiento moderado.
4. **Pesos abiertos:** TrOCR variantes `stage1` (MIT, preentrenadas con texto sintético impreso), afinadas con lo anterior. **Evitar las variantes `-handwritten` publicadas por Microsoft**, porque están afinadas sobre IAM.
5. Si la calidad no alcanza el umbral de producto, la salida realista es **licenciar un corpus comercial** o recolectar datos propios. No hay un IAM libre esperando.

### Acción transversal, sugerida para esta semana

Crear un archivo de procedencia de datos en el repositorio (por ejemplo `docs/DATA_PROVENANCE.md`) que registre, por cada conjunto que entre a un entrenamiento: nombre, versión, fecha de descarga, URL, texto de la licencia guardado en copia local, y el aviso de atribución exigido. Cuando llegue el primer cliente empresarial con diligencia debida, ese archivo es la diferencia entre una respuesta de un día y una auditoría de un mes.

---

## 7. Lo que no pude verificar

Listado sin adornos. Ninguno de estos puntos debe darse por cierto sin comprobación adicional.

1. **La licencia oficial de MNIST.** La página de Yann LeCun (`yann.lecun.com/exdb/mnist/`) rechazó la conexión durante toda la investigación, y no pude acceder a Internet Archive desde este entorno. Tengo tres afirmaciones de terceros que se contradicen: CC BY-SA 3.0 (espejo PyMVPA), MIT (ficha de Hugging Face bajo el usuario `ylecun`), y "consultar el original" (UCI). **No sé cuál es la licencia real de MNIST.**
2. **Los términos exactos de NIST Special Database 19 en su propia ficha.** Verifiqué la política general de licenciamiento de NIST, que es clara y favorable. Pero ni la página del producto, ni el registro del repositorio de datos de NIST, ni el catálogo de data.gov (dos URLs devolvieron 404) mostraron un campo de licencia específico para SD19. Además, la propia página de NIST distingue entre "Standard Reference Data", sobre la cual NIST **sí** asegura protección de copyright a nombre del Secretario de Comercio, y el resto de datos y software, que son de dominio público. **SD19 se distribuye bajo el programa SRD, lo cual podría colocarlo en la categoría con copyright asegurado.** Este punto es importante y debe resolverse: la recomendación de usar SD19 depende de él. La vía práctica es leer el Users' Guide de la segunda edición (`https://s3.amazonaws.com/nist-srd/SD19/sd19_users_guide_edition_2.pdf`) y, si sigue sin ser concluyente, escribir a NIST.
3. **La licencia de las tipografías de Google Fonts en fuente primaria.** No abrí la ficha de licencia de `fonts.google.com` ni el texto de la SIL OFL en `scripts.sil.org`. La afirmación de que Google Fonts se publica bajo OFL y permite uso comercial proviene de fuentes secundarias. Además, **no verifiqué si la OFL dice algo específico sobre generar y distribuir imágenes de glifos como conjunto de datos de entrenamiento** — es un uso que la licencia no contempló al redactarse. Antes de construir el generador sintético conviene leer el texto de la OFL, y verificar familia por familia, porque no todas las tipografías de Google Fonts están bajo OFL (algunas están bajo Apache 2.0).
4. **El tamaño del conjunto GNHK.** El readme declara la licencia CC BY 4.0 con claridad pero no da conteo de imágenes ni de palabras. No sé si son cientos o miles de muestras, y eso cambia su utilidad real.
5. **El número de clases y el volumen de HWRT y de Detexify.** Ninguna de las dos fichas lo declara. Los datos de Detexify además no están en el repositorio sino en una carpeta de Google Drive que no consulté.
6. **La licencia de Chandra OCR 2** (OpenRAIL-M modificada con umbral de ingresos). La conozco solo por un resultado de búsqueda secundario; no abrí la ficha del modelo. La incluí en la tabla marcada, pero no la tomes como verificada.
7. **La licencia de los pesos `trocr-*-stage1`.** La ficha de Hugging Face de `microsoft/trocr-base-stage1` no declara licencia ni datos de entrenamiento; fue escrita por el equipo de Hugging Face, no por Microsoft. Infiero MIT por el proyecto unilm, pero **la ficha específica no lo dice**.
8. **Los términos oficiales de CROHME en la sede del IAPR TC11.** El sitio `iapr-tc11.org` falló con un error de SSL y `crohme2023.ltu-ai.dev` devolvió 403. La conclusión de no comercial está bien respaldada por otras dos fuentes (la sede de datos del ISI y el depósito de Curtin University), así que el veredicto es firme, pero no leí la página histórica del TC11.
9. **Si CROHME 2023 cambió de licencia respecto de ediciones anteriores.** Vi CC BY-NC-SA 3.0 Unported atribuida a la sede histórica y CC BY-NC-SA 4.0 en el depósito de Curtin. Ambas son NC, así que la conclusión no cambia, pero no confirmé la versión exacta por edición.
10. **Si Meta u otros ofrecen licencia comercial negociada** para Nougat, Imgur5K o MathWriting. No investigué vías de licenciamiento pagado. Si alguno de esos conjuntos resulta crítico para el producto, preguntar directamente es una opción que no exploré.
11. **La interpretación jurídica de fondo**, en dos puntos que no son verificables por búsqueda web sino que requieren opinión legal: (a) si entrenar un modelo constituye o no la creación de una "obra adaptada" en el sentido de CC BY-ND y CC BY-SA, cuestión sobre la que no hay consenso ni jurisprudencia asentada; y (b) si la renuncia CC0 del depositante de IM2LATEX-100K es oponible respecto del contenido derivado de artículos de arXiv de terceros.
