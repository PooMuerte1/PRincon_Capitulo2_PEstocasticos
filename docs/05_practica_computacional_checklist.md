## Checklist: práctica computacional “bien hecha” (simulación / estimación / backtesting)

Este checklist es para evitar los errores más comunes en cuant:

- **supuestos implícitos** (model risk)
- **sesgos de estimación** (MC error, discretización, look-ahead)
- **validación incompleta** (sin tests, sin IC, sin stress)

---

### 1) Simulación (Monte Carlo)

- **Reproducibilidad**: usar seed y reportarlo.
- **Vectorización y performance**: evitar bucles Python si se puede; cuidado con memoria (paths×T).
- **Verificación contra “verdad”**:
  - si existe fórmula cerrada (pmf, ruina), comparar MC vs exacto.
  - reportar error y cómo escala con #paths.
- **Cuantificación de incertidumbre**:
  - reportar **intervalo de confianza** (IC) para probabilidades y errores estándar para medias.
  - evitar IC normal cuando \(p\) está cerca de 0/1 o \(n\) es pequeño (preferir Wilson/Clopper-Pearson).

### 2) Estimación (calibración)

- **Separar**: estimación de parámetros vs evaluación.
- **IC y robustez**:
  - IC asintótico es ok con n grande, pero reportar también robustez (bootstrap) si hace falta.
- **Model checking**:
  - contrastar supuestos i.i.d. y homocedasticidad (en datos financieros suelen fallar).

### 3) Backtesting (cuando ya uses datos reales)

Reglas mínimas (industria):

- **No look-ahead**: usar únicamente información disponible en el tiempo.
- **No survivorship bias**: usar universos históricos correctos.
- **Costos y fricciones**:
  - comisiones, spreads, slippage, market impact (aunque sea con un proxy).
- **Overfitting control**:
  - train/validation/test, walk-forward, y control de data-snooping.
- **Métricas correctas**:
  - no sólo Sharpe; también drawdowns, tail risk, turnover, capacity, stability.

### 4) “Semáforo” para este repo (estado actual)

Lo que YA está bien en `projects/random-walks-finance/`:

- **Reproducibilidad**: seed en CLI.
- **Validación**: se compara simulación vs fórmula cerrada en `pmf`, `ruin`, `duration`.
- **Reporte de error**: se imprime error absoluto.

Lo que MEJORO/DEBO MEJORAR para nivel industria:

- **IC para proporciones**: preferir Wilson/Clopper-Pearson en lugar de aproximación normal simple.
- **Casos borde**: \(p=0\) o \(p=1\) en fórmulas cerradas deben tratarse limpio.
- **Backtesting**: aún no hay pipeline con datos reales (esto es intencional: primero teoría + simulación).

