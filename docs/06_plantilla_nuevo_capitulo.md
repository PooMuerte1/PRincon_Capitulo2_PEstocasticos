## Plantilla para estudiar otro capítulo (mismo método: rigor + finanzas + práctica + papers)

Esta plantilla sirve para repetir exactamente el flujo que hicimos con **Cap. 2 (caminatas aleatorias)**, pero ahora con **cualquier capítulo** del libro.

> Si quieres entender el “por qué” del método (por qué funciona y qué errores evita), lee primero `docs/07_guia_maestra_por_que_y_como.md`.

---

### 0) Resultado esperado (deliverables)

Al terminar el capítulo debes tener:

- **Notas rigurosas** del capítulo en `.md`
- **Soluciones formales** de los ejercicios del capítulo en `.md`
- **Banco de ejercicios tipo industria** derivados del tema (y su “mapeo” a tareas reales)
- **Proyecto Python reproducible** con:
  - simulación/estimación (si aplica),
  - verificación contra resultados teóricos (cuando exista fórmula cerrada),
  - gráficos/experimentos,
  - CLI o notebook reproducible
- **Bibliografía y papers**: 5–15 referencias (fundacionales + aplicadas) y “qué valida cada una”

---

### 0.1) Por qué estos deliverables (y por qué esto se considera “bien hecho”)

**Idea central**: en cuant, “entender” significa poder hacer 3 cosas con el mismo concepto:

- **Intuición**: explicarlo sin fórmulas.
- **Rigor**: derivarlo/probarlo y saber exactamente qué supuestos usa.
- **Implementación**: producir números reproducibles y validados.

Estos deliverables están diseñados para evitar los fallos típicos:

- leer sin poder resolver (ilusión de comprensión),
- programar sin validar (bugs silenciosos),
- aplicar a finanzas sin supuestos (model risk),
- citar papers sin entender límites (argumentos vacíos).

Si completas los deliverables, es muy difícil que te “queden huecos” sin darte cuenta.

---

### 1) Carpeta y nombres de archivo (convención)

En `docs/` crea:

- `NN_<tema>_rigor_finance.md`  
  (teoría + pruebas + “traducción a finanzas”)
- `NN_<tema>_soluciones_ejercicios.md`  
  (soluciones 100% formales)
- `NN_<tema>_ejercicios_industria.md`  
  (ejercicios tipo industria + referencias)
- `NN_<tema>_papers.md`  
  (lista de papers con notas)

En `projects/` crea:

- `projects/<tema>-finance/` con `src/`, `requirements.txt`, `README.md`

> Mantén NN como número incremental para que tu curso sea navegable.

---

### 1.1) Por qué conviene una convención de nombres

- **Por qué**: cuando tengas 20–50 capítulos/unidades, una estructura estándar te ahorra tiempo mental.
- **Qué evita**: tener notas dispersas, código sin relación con teoría, y bibliografía imposible de rastrear.
- **Señal de calidad**: si alguien externo abre tu repo, entiende dónde está: teoría, ejercicios, práctica, fuentes.

---

### 2) Lectura “activa”: extraer el esqueleto matemático del capítulo

Haz una tabla (en el `.md`) con:

- **Definiciones** (objetos): procesos, variables, filtraciones si aparecen
- **Supuestos** (los que hacen que todo funcione): i.i.d., Markov, estacionariedad, etc.
- **Resultados**: proposiciones/teoremas (qué afirman y bajo qué condiciones)
- **Técnicas**: “primer paso”, ecuaciones en diferencias, generatrices, martingalas, etc.

Regla de oro:

- Si un resultado es usado en ejercicios posteriores, lo debes poder **re-demostrar** sin mirar.

---

### 2.1) Por qué “lectura activa” y no lectura pasiva

- **Lectura pasiva**: “me suena” → alta probabilidad de olvidar o confundir supuestos.
- **Lectura activa**: extraes objetos/supuestos/técnicas → puedes reconstruir el capítulo.

Esto es crucial en finanzas porque pequeños cambios en supuestos cambian el resultado (por ejemplo: i.i.d. vs dependencia; barrera discreta vs continua).

---

### 3) Traducción a finanzas (sin humo)

Por cada concepto importante del capítulo, escribe:

- **Qué modela** en finanzas (ej.: hitting ↔ barreras; absorción ↔ default/margin)
- **Qué NO modela** (limitaciones: colas, clustering, microestructura, fricciones)
- **Qué métrica/práctica industrial conecta** (pricing, riesgo, calibración, simulación)

Plantilla por concepto:

- **Concepto**: …
- **Matemática**: (definición + resultado)
- **Finanzas**: (interpretación concreta)
- **Falla típica**: (qué rompe el supuesto)
- **Cómo lo arregla la industria**: (modelo siguiente: GARCH, jumps, SV, etc.)
- **Papers**: 2–3

---

### 3.1) Por qué “sin humo” (reglas para no engañarte)

En finanzas, casi cualquier modelo “suena razonable” si no lo presionas.
Por eso, por cada concepto debes escribir también:

- **Qué no modela** (limitación concreta),
- **Qué observable** se rompe en datos reales (colas, volatilidad en clusters, microestructura),
- **Qué upgrade** se usa en práctica (y cuándo vale la pena).

Si no haces esto, terminas con modelos bonitos pero inútiles.

---

### 4) Ejercicios del libro: cómo resolverlos (ritual)

Para cada ejercicio:

- **(i) Qué herramienta usa** (primer paso, Markov, generatriz, etc.)
- **(ii) Solución formal** (pasos + justificación)
- **(iii) Check rápido** (caso borde, simetría, unidades, comparación con simulación)
- **(iv) Versión “finanzas”**: cambia el lenguaje para que sea un problema real

---

### 4.1) Por qué resolver ejercicios del libro (y no saltarlos)

- **Por qué**: los ejercicios entrenan las “palancas” (primer paso, DP, generatrices, martingalas).
- **Qué evita**: ser bueno leyendo pero malo produciendo soluciones.
- **Señal de dominio**: puedes resolver sin mirar y explicar por qué cada paso es válido.

---

### 5) Ejercicios tipo industria (derivados del capítulo)

Tu banco debe cubrir 4 categorías:

- **Exacto/analítico**: cuando hay fórmulas cerradas
- **Numérico**: programación dinámica, recursiones, PDE discretas
- **Monte Carlo**: estimación + IC + reducción de varianza (si aplica)
- **Datos reales**: test de supuestos / calibración / backtesting (si aplica)

Regla de oro:

- Cada ejercicio tipo industria debe decir: **qué habilidad entrena** y **cómo se valida**.

---

### 5.1) Por qué agregar ejercicios industriales

Porque en un trabajo cuant raramente te piden “repite el ejercicio 7”.
Te piden:

- variar el modelo,
- agregar fricciones,
- calibrar con datos,
- cuantificar error,
- explicar limitaciones.

El banco industrial hace esa transición y te obliga a conectar teoría con decisiones reales.

---

### 6) Práctica computacional: estándar mínimo “bien hecho”

Antes de confiar en un resultado computacional, exige:

- **Supuestos explícitos** en el README (qué simulamos exactamente)
- **Reproducibilidad** (seed, versiones, comando exacto)
- **Validación** contra “verdad” (si existe): fórmula cerrada, casos límites, tests
- **Incertidumbre**: IC para probabilidades; SE/IC para medias
- **Sesgos**:
  - discretización (barreras discretas vs continuas),
  - look-ahead (si hay datos),
  - survivorship (si hay universo),
  - data-snooping/overfitting (si optimizas parámetros)

---

### 6.1) Qué significa “bien hecho” (criterios concretos)

Un resultado computacional es “confiable” si cumple:

- **Correctitud**: se valida contra resultados exactos o tests diseñados.
- **Incertidumbre**: reporta IC/SE; no solo un número.
- **Reproducibilidad**: otro puede replicarlo con los mismos comandos.
- **Trazabilidad**: queda claro qué supuestos se usaron.

Esto es lo mínimo para evitar “conclusiones por azar” (especialmente peligroso en trading).

---

### 7) Papers: cómo elegir y “validar”

Por tema, intenta incluir:

- **1 fundacional** (define el marco)
- **1 metodológico** (cómo se implementa/estima)
- **1 aplicado** (caso financiero real)

Y para cada paper:

- **Qué asume**
- **Qué prueba/demuestra**
- **Qué limita**
- **Cómo lo usarías tú** (pricing/riesgo/estrategia)

---

### 7.1) Por qué papers y no solo libros

- El libro te da base; el paper te muestra:
  - qué es **estándar** hoy,
  - qué está **probado** y bajo qué supuestos,
  - qué limitaciones se conocen,
  - qué técnicas se usan en práctica.

Pero los papers solo ayudan si los lees con el mismo protocolo: supuestos → aporte → límites → uso.

---

### 8) Checklist final del capítulo

Marca como “dominado” si puedes:

- explicar el capítulo en 3 niveles: intuición, formal, implementación
- resolver 80% de ejercicios sin mirar
- reproducir por código al menos 2 resultados (con IC)
- explicar 2 fallas del modelo y 2 “upgrades” usados en industria
- citar 5+ fuentes y decir qué valida cada una

---

### 9) Errores típicos (y cómo detectarlos temprano)

- **Error**: “mi simulación da un número” sin IC/SE.  
  **Detección**: no sabes si dos métodos difieren de verdad.
- **Error**: “calibré \(p\)” y luego evalué en los mismos datos.  
  **Detección**: performance “demasiado buena” y se cae fuera de muestra.
- **Error**: usar un modelo discreto para una barrera continua sin corrección.  
  **Detección**: sensibilidad rara a \(\Delta t\) o a la frecuencia de muestreo.
- **Error**: creer que random walk i.i.d. describe retornos reales sin revisar stylized facts.  
  **Detección**: clustering de volatilidad, colas y autocorrelación en \(|r_t|\).


