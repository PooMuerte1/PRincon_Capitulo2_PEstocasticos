## Bibliografía y papers (mapa por temas) — Random Walks en finanzas

### 1) Árbol binomial / random walk para pricing (fundacional)

- Cox, J. C., Ross, S. A., Rubinstein, M. (1979). *Option Pricing: A Simplified Approach*. Journal of Financial Economics.
  - **Por qué importa**: formaliza pricing por expectativa neutral al riesgo y DP discreta (árbol binomial).

### 2) Barreras y monitoreo discreto vs continuo

- Broadie, M., Glasserman, P., Kou, S. (1997). *A Continuity Correction for Discrete Barrier Options*. Mathematical Finance.
  - **Por qué importa**: cuantifica el gap entre barreras discretas y continuas; esencial para implementación real.

### 3) Monte Carlo en finanzas (validación, error, varianza)

- Glasserman, P. (2004). *Monte Carlo Methods in Financial Engineering*. Springer.
  - **Por qué importa**: estándar industrial para simulación, reducción de varianza, CI, y buenas prácticas.

### 4) Estilizados empíricos (por qué el RW i.i.d. es insuficiente)

- Cont, R. (2001). *Empirical properties of asset returns: stylized facts and statistical issues*. Quantitative Finance.
  - **Por qué importa**: base para entender colas, clustering de volatilidad y límites del random walk simple.

### 5) ARCH/GARCH (volatilidad condicional)

- Engle, R. (1982). *Autoregressive Conditional Heteroscedasticity with Estimates of the Variance of United Kingdom Inflation*. Econometrica.
- Bollerslev, T. (1986). *Generalized Autoregressive Conditional Heteroskedasticity*. Journal of Econometrics.
  - **Por qué importa**: primer “upgrade” realista al RW i.i.d. para retornos.

### 6) Principio de invariancia (puente al Browniano)

- Donsker, M. D. (1951). *An Invariance Principle for Certain Probability Limit Theorems*. Memoirs of the AMS.
  - **Por qué importa**: justifica Browniano como límite de caminatas reescaladas.

### 7) Random walk moderno (hitting times/potencial)

- Lawler, G. F., Limic, V. (2010). *Random Walk: A Modern Introduction*. Cambridge.
  - **Por qué importa**: hitting times, potencial, herramientas modernas (más allá del nivel “intro”).

### 8) Cadenas de Markov (absorción, hitting, potencial)

- Norris, J. R. (1997). *Markov Chains*. Cambridge.
  - **Por qué importa**: teoría limpia para absorber/hitting; útil en credit migration y modelos discretos.

### 9) Ruina (riesgo de quiebra) — puente directo a margin/default

- Gerber, H. U. (1999). *An Introduction to Mathematical Risk Theory*. (libro).
- Asmussen, S., Albrecher, H. (2010). *Ruin Probabilities*. World Scientific.
  - **Por qué importa**: marco general de ruina; random walk es el caso base.

### 10) Random walk e hipótesis de eficiencia (histórico)

- Fama, E. (1965). *The Behavior of Stock-Market Prices*. Journal of Business.
  - **Por qué importa**: origen histórico del “random walk” en finanzas (no es un manual de implementación).

---

### Cómo usar este mapa

- Si tu foco es **pricing**: comienza con Cox–Ross–Rubinstein y Broadie–Glasserman–Kou, y usa Glasserman para implementación.
- Si tu foco es **riesgo/ruina/margin**: Gerber → Asmussen/Albrecher.
- Si tu foco es **fundamentos/probabilidad**: Norris + Lawler/Limic + Donsker (para puente al continuo).

