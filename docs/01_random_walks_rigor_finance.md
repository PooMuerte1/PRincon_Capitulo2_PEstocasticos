## Caminatas aleatorias (rigor) con traducción a finanzas

Base: `Rincón(2012) Procesos estocásticos`, Cap. 2 (Caminatas aleatorias).

### 1) Modelo: caminata aleatoria simple en \(\mathbb Z\)

Sea \((\xi_i)_{i\ge 1}\) i.i.d. con
\[
P(\xi=+1)=p,\qquad P(\xi=-1)=q=1-p.
\]
Definimos el proceso a tiempo discreto
\[
X_0=0,\qquad X_n=\sum_{i=1}^n \xi_i.
\]

**Propiedad de Markov (formal).** Para \(n\ge 0\) y enteros \(x_0,\dots,x_{n+1}\),
\[
P(X_{n+1}=x_{n+1}\mid X_0=x_0,\dots,X_n=x_n)=P(X_{n+1}=x_{n+1}\mid X_n=x_n).
\]
La razón estructural: los incrementos \(\xi_{n+1}\) son independientes del pasado dado el presente, y \(X_{n+1}=X_n+\xi_{n+1}\).

**Traducción a finanzas.**

- Si modelas *retornos discretos* como \(R_i=\delta\,\xi_i\), entonces el log-precio \(Y_n:=\log S_n\) puede representarse como
  \[
  Y_n=Y_0+\sum_{i=1}^n R_i = Y_0+\delta X_n.
  \]
  Esto es el prototipo de “random walk” discreto.
- En un mundo sin fricciones, la condición de “juego justo” típica (martingala bajo una medida adecuada) corresponde a que el proceso descontado sea martingala. En modelos binomiales, eso se logra con una **medida neutral al riesgo** (cambio de \(p\)).

### 2) Momentos: esperanza y varianza

\[
E[X_n]=n(p-q),\qquad \mathrm{Var}(X_n)=4npq.
\]

Interpretación:

- \(p\neq 1/2\) induce **deriva** en el promedio.
- La varianza crece linealmente en \(n\): incertidumbre acumulada.

**Traducción a finanzas.**

- \(p-q\) se relaciona con drift del retorno discreto.
- \(4pq\) controla la volatilidad por paso (en el escalamiento continuo aparece \(\sigma^2\)).

### 3) Distribución exacta de \(X_n\) (binomial + paridad)

Definamos \(R_n\) = #pasos a la derecha. Entonces
\[
X_n = R_n - (n-R_n)=2R_n-n \quad\Rightarrow\quad R_n=\frac{n+X_n}{2}.
\]
Por lo tanto, si \(|x|\le n\) y \(n\) y \(x\) tienen la misma paridad,
\[
P(X_n=x) = \binom{n}{(n+x)/2}\,p^{(n+x)/2}\,q^{(n-x)/2},
\]
en otro caso es 0.

**Traducción a finanzas.**

- Es la “densidad” exacta de un modelo binomial de retornos discretos.
- Permite construir precios por expectativas discretas **sin Monte Carlo** para productos que dependan sólo del valor final.

### 4) Probabilidades de primera visita / hitting

Los problemas de “primera visita” (hitting times) se resuelven típicamente por:

- **Análisis del primer paso**: condicionar sobre \(\xi_1\).
- **Ecuaciones en diferencias** con condiciones de frontera.
- **Funciones generadoras** cuando interesa sumar sobre tiempos.

**Aplicación financiera típica.**

- Probabilidad de tocar una barrera antes de un horizonte: base de **barrier options** (en discreto).
- “Ruin / margin call”: probabilidad de que el capital toque 0 antes de alcanzar un objetivo.

### 5) Retorno al origen: recurrencia vs transiencia (1D)

Para la caminata en \(\mathbb Z\):

- Si \(p=q=1/2\) (simétrica), el retorno eventual al origen ocurre con probabilidad 1 (recurrencia).
- Si \(p\neq 1/2\) (asimétrica), el retorno eventual ocurre con probabilidad \(<1\).

Además, en el caso simétrico el **tiempo esperado de retorno** es infinito (cola pesada del tiempo de retorno).

**Por qué importa en finanzas.**

- “Seguro que vuelva” no implica “vuelva rápido”: colas de hitting times impactan riesgo de liquidez, duración de estrategias con stop/target, y dimensionamiento de capital.
- Modelos con drift cambian cualitativamente la probabilidad de tocar niveles (riesgo asimétrico).

### 6) Ruina del jugador = caminata absorbente en \(\{0,1,\dots,N\}\)

Modelo: capital del jugador A es \(X_n\) con \(X_0=k\) y estados absorbentes 0 y \(N\).

Definimos el tiempo de absorción
\[
\tau = \min\{n\ge 0: X_n\in\{0,N\}\}.
\]
Probabilidad de ruina:
\[
u_k = P(X_\tau=0\mid X_0=k).
\]

**Ecuación en diferencias (primer paso).**

Para \(k=1,\dots,N-1\):
\[
u_k = p\,u_{k+1} + q\,u_{k-1},
\]
con condiciones \(u_0=1,\ u_N=0\).

**Solución cerrada.**

- Si \(p=q=1/2\): \(u_k=(N-k)/N\).
- Si \(p\neq q\):
  \[
  u_k = \frac{(q/p)^k-(q/p)^N}{1-(q/p)^N}.
  \]

**Traducción a finanzas (interpretación industrial).**

- \(X_n\) puede interpretarse como *equity* discreto en unidades: ganancias/pérdidas por trade.
- 0 = default/margin call; \(N\) = take-profit/target de capital.
- La fórmula muestra sensibilidad extrema cuando \(p\approx 1/2\): pequeñas ventajas cambian drásticamente el riesgo de ruina (relevante para “edge” pequeño).

### 7) Tiempo esperado hasta absorción

Definimos \(m_k = E[\tau\mid X_0=k]\).

Satisface la ecuación (para \(k=1,\dots,N-1\)):
\[
m_k = 1 + p\,m_{k+1} + q\,m_{k-1},
\]
con \(m_0=m_N=0\).

Solución:

- Si \(p=q=1/2\): \(m_k = k(N-k)\).
- Si \(p\neq q\): existe forma cerrada (ver capítulo), y su comportamiento cualitativo es:
  - maximiza cerca de \(k\approx N/2\),
  - cae cuando hay drift fuerte (absorción más rápida hacia un lado).

**Traducción a finanzas.**

- Duración esperada de una estrategia con stop/target discretos.
- Incluso con probabilidad de ruina “moderada”, la duración puede ser enorme (riesgo operacional y de costos).

### 8) Qué deberías saber demostrar sin mirar

Checklist de “dominio” (si esto sale fluido, estás sólido):

- Derivar la distribución de \(X_n\) usando \(R_n\sim\mathrm{Bin}(n,p)\) y la restricción de paridad.
- Montar una ecuación en diferencias por análisis del primer paso para:
  - probabilidad de hitting de un nivel,
  - probabilidad de absorción en 0 antes que en \(N\),
  - tiempo esperado de absorción.
- Saber cuándo una solución “lineal” es válida (caso simétrico) y cuándo aparece un término geométrico (caso asimétrico).

### 9) Referencias (finanzas + estocásticos) para validar/expandir

#### Random walk y mercados (empírico)

- Fama, E. (1965). *The Behavior of Stock-Market Prices*. Journal of Business.
- Malkiel, B. (1973/ediciones posteriores). *A Random Walk Down Wall Street* (libro; útil como perspectiva histórica, no es un texto técnico).

#### Barreras, hitting times y pricing (conexión a práctica)

- Cox, Ross, Rubinstein (1979). *Option Pricing: A Simplified Approach*. Journal of Financial Economics. (binomial ↔ random walk + pricing por expectativa/DP)
- Broadie, Glasserman, Kou (1997). *A Continuity Correction for Discrete Barrier Options*. Mathematical Finance. (clave: barreras discretas vs continuas)

#### Ruina / riesgo de quiebra (conexión directa)

- Gerber, H. U. (1999). *An Introduction to Mathematical Risk Theory*. (ruina clásica; es actuarial pero muy relevante)
- Asmussen, S., Albrecher, H. (2010). *Ruin Probabilities*. (más avanzado)

#### Texto base de cadenas de Markov / potencial

- Norris, J. R. (1997). *Markov Chains*. (hitting/absorción bien explicado)
- Lawler, G. F., Limic, V. (2010). *Random Walk: A Modern Introduction*. (random walk moderno; hitting y potencial)

> Nota: en `docs/03_bibliografia_papers.md` dejo una bibliografía más completa y “mapeada” a ejercicios industriales.

