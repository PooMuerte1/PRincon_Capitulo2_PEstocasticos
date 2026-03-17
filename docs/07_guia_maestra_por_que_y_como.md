## Guía maestra: por qué este método funciona y cómo ejecutarlo (principiante → avanzado)

Esta guía explica **por qué** creamos cada documento/proyecto, **qué riesgo evita**, y **cómo** usarlo para estudiar un capítulo a profundidad sin “huecos”.

---

### 1) El problema real al estudiar cuant

La mayoría de personas falla por una (o varias) de estas razones:

- **Ilusión de comprensión**: leer y “sentir que entendiste”, pero no puedes derivar ni resolver.
- **Rigor sin aplicación**: sabes teoremas, pero no sabes cuándo sirven en finanzas.
- **Código sin validación**: simulas y obtienes números, pero no sabes si están bien.
- **Papers como adorno**: citas sin entender supuestos/limitaciones.
- **Backtest engañoso**: resultados por sesgos (look-ahead, data-snooping, survivorship).

El método que estamos usando está diseñado para **atacar esos fallos**, en ese orden.

---

### 2) Por qué existen estos entregables (y qué te dan)

#### 2.1 `docs/00_roadmap.md` (mapa)

- **Por qué**: sin un mapa, estudias “en espiral” y repites temas o saltas prerequisitos.
- **Qué evita**: perderte, estudiar cosas bonitas pero irrelevantes, o entrar a Ito sin dominar hitting.
- **Cómo se usa**: antes de empezar el capítulo, verificas prerequisitos y el “orden lógico”.

#### 2.2 `docs/NN_<tema>_rigor_finance.md` (teoría con traducción)

- **Por qué**: la matemática sola es insuficiente; finanzas sola es frágil. Necesitas el puente.
- **Qué evita**: memorizar fórmulas sin saber supuestos; o “intuiciones” sin demostración.
- **Cómo se hace bien**:
  - Cada definición debe venir con al menos un ejemplo y una “no-ejemplo”.
  - Cada resultado debe decir: **hipótesis → conclusión → por qué importa**.
  - Cada resultado debe tener “checks”: casos límite, simetrías, unidades.

#### 2.3 `docs/NN_<tema>_soluciones_ejercicios.md` (soluciones formales)

- **Por qué**: los ejercicios son el lugar donde la teoría se vuelve habilidad.
- **Qué evita**: creer que sabes porque “entiendes la lectura”.
- **Cómo se hace bien**:
  - Escribes pasos justificando *cada* igualdad no trivial.
  - Dices qué técnica estás usando (primer paso, Markov, generatriz…).
  - Incluyes un check: ¿la respuesta tiene sentido? (monotonía, límites).

#### 2.4 `docs/NN_<tema>_ejercicios_industria.md` (banco industrial)

- **Por qué**: la industria paga por resolver *variantes* del problema, no por repetir el libro.
- **Qué evita**: quedarte “académico” sin poder convertirlo a pricing/riesgo/calibración.
- **Cómo se hace bien**:
  - Cada ejercicio dice: **habilidad** (pricing DP, hitting, calibración, MC…).
  - Cada ejercicio dice: **cómo se valida** (fórmula cerrada, bounds, tests, IC).

#### 2.5 `docs/NN_<tema>_papers.md` o bibliografía (evidencia)

- **Por qué**: los papers son tu filtro de calidad: definen *qué es estándar* y *qué está probado*.
- **Qué evita**: construir “castillos” sin sustento o aprender modelos obsoletos sin saberlo.
- **Cómo se hace bien**:
  - Por paper: supuestos, qué demuestra, limitaciones, cómo se usa en finanzas.
  - No necesitas 50 papers; necesitas **pocos, bien leídos**.

#### 2.6 `projects/<tema>-finance/` (código reproducible)

- **Por qué**: un quant profesional necesita convertir matemáticas en números confiables.
- **Qué evita**: errores silenciosos, resultados irreproducibles, conclusiones por azar.
- **Cómo se hace bien**:
  - Reproducible (seed, comando exacto).
  - Validado (contra verdad teórica o tests).
  - Con incertidumbre (IC/SE).
  - Con supuestos escritos en README.

---

### 3) Por qué “primer paso” + “ecuación en diferencias” es tan importante

En modelos discretos, muchas preguntas industriales tienen esta forma:

- “¿Cuál es la probabilidad de tocar un nivel antes que otro?”
- “¿Cuál es el tiempo esperado hasta que pase algo?”
- “¿Cuál es el valor esperado descontado de un payoff con barrera?”

La técnica del **primer paso** traduce estas preguntas a una ecuación local:

- probabilidad de hoy = combinación de probabilidades de mañana

Eso te da ecuaciones en diferencias / DP, que es exactamente el corazón de:

- árboles binomiales (pricing),
- cadenas absorbentes (default),
- hitting times (barreras).

---

### 4) Qué significa “bien hecho” en computación (y por qué)

#### 4.1 IC/SE no son opcionales

Monte Carlo produce números aleatorios: sin IC/SE no sabes si un error es real o solo ruido.
En práctica, esto evita:

- “optimizar” una estrategia por puro azar,
- creer que un modelo gana cuando no.

#### 4.2 Validar contra casos donde conoces la respuesta

Si existe una fórmula cerrada (como ruina), tu simulación debe recuperarla.
Esto evita el error más caro: **código incorrecto con confianza alta**.

#### 4.3 Backtesting es otra disciplina

Backtesting no es “correr una estrategia”. Es un protocolo anti-sesgo.
Por eso lo separamos: primero teoría + simulación controlada; luego datos reales con reglas estrictas.

---

### 5) Cómo pasar de principiante a avanzado con este método

- **Principiante**: puedes explicar definiciones y hacer simulaciones simples.
- **Intermedio**: puedes derivar ecuaciones en diferencias y resolverlas; validar con MC + IC.
- **Avanzado**: puedes:
  - proponer variantes tipo industria,
  - identificar fallas del modelo,
  - elegir upgrades (GARCH/jumps/SV),
  - diseñar validación empírica sin sesgos.

