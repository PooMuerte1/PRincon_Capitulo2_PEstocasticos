## Banco de ejercicios “tipo industria” (Random Walks → Finanzas)

Estos ejercicios están diseñados para entrenar habilidades que aparecen en práctica cuantitativa:

- modelado discreto (binomial/random walk)
- análisis del primer paso y ecuaciones en diferencias
- simulación Monte Carlo con validación (IC, sesgo, convergencia)
- calibración simple (MLE / momentos)
- control de riesgo (ruina, drawdowns, barreras)

Cada bloque incluye **qué habilidad industrial entrena** y **referencias** (papers/libros) para validar el enfoque.

### A) Distribución exacta, calibración y testing

#### A1. Calibración de \(p\) por máxima verosimilitud (i.i.d. \(\pm1\))

Tienes datos de incrementos discretos \(\xi_1,\dots,\xi_n\in\{+1,-1\}\).

- **(a)** Deriva el MLE \(\hat p\).
- **(b)** Da un IC asintótico para \(p\).
- **(c)** Traduce a retornos \(R_i=\delta\xi_i\) y discute limitaciones empíricas (colas, heterocedasticidad).

**Habilidad**: calibración básica + inferencia.

**Referencias**

- Cox, Ross, Rubinstein (1979): binomial como base de pricing.
- Cont (2001): stylized facts (por qué \(\pm1\) i.i.d. falla empíricamente).

#### A2. Verificación numérica de \(P(X_n=x)\) y control de error MC

Para varios \(n\), estima por Monte Carlo \(P(X_n=x)\) y compárala con la fórmula cerrada. Reporta:

- error absoluto y relativo
- IC binomial para la estimación MC
- dependencia del error con #paths

**Habilidad**: validación y cuantificación de error.

**Referencias**

- Glasserman (2004): Monte Carlo Methods in Financial Engineering (capítulos de error/IC).

### B) Hitting times y opciones barrera (discreto)

#### B1. Probabilidad de tocar una barrera superior antes del tiempo \(T\)

Define \(Y_n = Y_0 + \delta X_n\). Sea \(H>Y_0\). Define
\[
\tau_H=\min\{n\ge 0: Y_n\ge H\}.
\]

- **(a)** Para \(p\neq 1/2\), estima por simulación \(P(\tau_H\le T)\) y discute monotonicidad en \(p,\delta,H\).
- **(b)** Para un intervalo \([L,U]\), estima \(P(\tau_U<\tau_L)\) y conéctalo con ruina del jugador (absorción).

**Habilidad**: barreras + probabilidad de paso primero.

**Referencias**

- Broadie, Glasserman, Kou (1997): corrección de continuidad en barreras.
- Cox, Ross, Rubinstein (1979): árbol binomial y programación dinámica.

#### B2. Pricing discreto de un knock-out (por DP en rejilla)

En un modelo binomial para \(S_n\), define una opción que paga \(g(S_T)\) si nunca tocó una barrera \(B\) (knock-out), y 0 si la toca.

- **(a)** Formula el precio por **programación dinámica** (backward induction).
- **(b)** Implementa y valida vs Monte Carlo con mismas discretizaciones.
- **(c)** Discute sesgo de discretización vs barrera continua (si \(T\to\) continuo).

**Habilidad**: pricing por DP + verificación.

**Referencias**

- Cox, Ross, Rubinstein (1979).
- Broadie, Glasserman, Kou (1997).

### C) Ruina, margin y sizing (riesgo operativo real)

#### C1. Probabilidad de margin call bajo edge pequeño

Modela PnL por trade como \(\pm1\) con probabilidad \(p\) y \(q\).
Capital en unidades \(X_n\in\{0,1,\dots,N\}\), \(X_0=k\).

- **(a)** Usa la fórmula cerrada de \(u_k\) para estudiar sensibilidad cuando \(p=0.5005\) vs \(0.4995\).
- **(b)** Diseña \(k,N\) para cumplir \(u_k\le 1\%\) y analiza trade-off con el objetivo \(N\) y duración esperada.
- **(c)** Verifica por simulación y reporta error/IC.

**Habilidad**: “risk-of-ruin” y sensibilidad a edge.

**Referencias**

- Gerber (1999): ruina (marco teórico).
- Asmussen & Albrecher (2010): ruina (avanzado).

#### C2. Duración esperada y costos (slippage/fees) hasta absorción

Toma \(m_k=E[\tau\mid X_0=k]\) y discute:

- cómo crece con \(N\) (orden \(N^2\) en el juego justo),
- implicación para costos por trade (fees) acumulados,
- por qué “ruina baja” no implica “estrategia viable” si la duración/fees matan el edge.

**Habilidad**: conectar hitting times con economía del trading.

**Referencias**

- Glasserman (2004): simulación/estimación.
- Cont (2001): stylized facts (costos + heterocedasticidad cambian el modelo).

### D) Del random walk al Browniano (puente indispensable)

#### D1. Escalamiento y Donsker (experimento computacional)

Define el proceso reescalado:
\[
W_n(t)=\frac{1}{\sqrt{n}}X_{\lfloor nt\rfloor},\quad t\in[0,1].
\]

- **(a)** Simula trayectorias para \(n\) grande y compara con Browniano (visualmente + momentos).
- **(b)** Discute por qué esto justifica usar Browniano en Black–Scholes como límite.

**Habilidad**: entender el “por qué” del continuo desde lo discreto.

**Referencias**

- Donsker (1951): invariance principle (fundacional).
- Revuz & Yor (1999) o Karatzas & Shreve (1991): Browniano/Ito (texto).

### E) “Reality check” empírico (por qué el RW i.i.d. falla)

#### E1. Test de independencia/heterocedasticidad en retornos reales

Toma retornos diarios (por ejemplo S&P500).

- **(a)** contrasta independencia (ACF) y colas (kurtosis),
- **(b)** estima volatilidad condicional (ARCH/GARCH) y discute por qué RW i.i.d. es insuficiente,
- **(c)** conecta con modelos con volatilidad estocástica y jumps (ruta futura).

**Habilidad**: conectar teoría con datos reales sin autoengaño.

**Referencias**

- Cont (2001): stylized facts.
- Engle (1982): ARCH.
- Bollerslev (1986): GARCH.

---

### Lista corta de fuentes citadas (para seguimiento)

- Cox, J. C., Ross, S. A., Rubinstein, M. (1979).
- Broadie, M., Glasserman, P., Kou, S. (1997).
- Glasserman, P. (2004).
- Cont, R. (2001).
- Donsker, M. D. (1951).
- Engle, R. F. (1982).
- Bollerslev, T. (1986).
- Gerber, H. U. (1999).
- Asmussen, S., Albrecher, H. (2010).

