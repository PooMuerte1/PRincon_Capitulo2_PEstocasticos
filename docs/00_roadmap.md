## Roadmap: de caminatas aleatorias a “quant” (rigor + práctica)

### Objetivo

Construir una base **matemáticamente rigurosa** en procesos estocásticos discretos (caminatas aleatorias / cadenas de Markov) y traducirla a tareas típicas en finanzas cuantitativas: **probabilidades de tocar barreras**, **tiempos de primera visita**, **ruina/margin**, **pricing discreto**, **validación por simulación**, y **conexión al límite continuo** (Browniano / Ito / Black–Scholes).

### Prerrequisitos (mínimos, pero bien)

- **Probabilidad**: variables aleatorias, independencia, esperanza/varianza, condicional, ley de la probabilidad total.
- **Cadenas de Markov a tiempo discreto**: matriz de transición, estados absorbentes, tiempos de hitting.
- **Cálculo/álgebra**: series, funciones generadoras, ecuaciones en diferencias.

### Unidad 1 (este PDF): Caminatas aleatorias (Cap. 2)

**Bloques conceptuales (en orden)**

- **Definición formal**: \(X_n=\sum_{i=1}^n \xi_i\), \(\xi_i\in\{+1,-1\}\), \(P(\xi=+1)=p\).
- **Distribución exacta de \(X_n\)**: binomial + restricción de paridad.
- **Hitting/retorno**: probabilidad de volver al origen; recurrencia vs transiencia.
- **Ruina del jugador**: absorción en \(\{0,N\}\), ecuación en diferencias, solución cerrada.
- **Tiempo esperado a absorción**: otra ecuación en diferencias (no homogénea).

**Traducción a finanzas**

- **Barreras discretas**: probabilidad de tocar un nivel (knock-in/knock-out en rejilla).
- **Riesgo de default / margin call**: ruina del capital con límite inferior absorbente.
- **Valuación por programación dinámica**: ecuaciones en diferencias ≈ versión discreta de PDE.
- **Puente al continuo**: escalamiento (CLT / Donsker) sugiere Browniano y modelos continuos.

### Qué “entregables” debes producir por unidad

- **Notas (Markdown)**: definiciones, teoremas, pruebas, y “por qué importa en finanzas”.
- **Implementación (Python)**:
  - simulación vectorizada
  - estimación por Monte Carlo con IC
  - verificación de fórmulas cerradas (ruina/tiempo esperado)
  - experimentos reproducibles (seed, parámetros, gráficos)
- **Lecturas**: una lista corta de papers/fuentes por tema (fundacional + aplicado).

### Próximas unidades (después de este capítulo)

- **Cadenas de Markov generales**: absorción, tiempos de retorno, cadenas irreducibles.
- **Procesos de conteo (Poisson) y renovaciones**: jumps, crédito, eventos.
- **Límite continuo**: Browniano, Ito, Girsanov, Black–Scholes.

