# Proyecto 01: Gestor de Liquidez Activa en Trader Joe (Liquidity Book)

Este proyecto aplica la teoría de caminatas aleatorias discreta sobre contenedores de precio discretos (**bins**) en el DEX Trader Joe de Avalanche. El objetivo es optimizar la colocación de liquidez y estimar el tiempo de permanencia activa antes de requerir un rebalanceo.

## Fundamentos Matemáticos

El modelo de Liquidity Book fragmenta el precio en intervalos discretos de tamaño constante (medido en puntos básicos o *basis points*, denominados `binStep`). El movimiento del precio entre estos contenedores se modela como una caminata aleatoria simple sobre los enteros $\mathbb{Z}$:

$$X_n = X_0 + \sum_{i=1}^n \xi_i$$

Donde:
*   $\xi_i \in \{+1, -1\}$ representa el salto de precio hacia el bin superior o inferior.
*   $P(\xi = +1) = p$ representa la probabilidad de subida (drift positivo si $p > 0.5$).
*   $P(\xi = -1) = q = 1 - p$ representa la probabilidad de bajada.

### Hitting Times y Duración Activa

Si proveemos liquidez en un rango de bins $[L, U]$ con la posición inicial en el precio actual $k \in (L, U)$:
1.  **Probabilidad de Salida:** La probabilidad de tocar la barrera superior $U$ antes que la inferior $L$ se modela directamente con las ecuaciones de la ruina del jugador (Sección 6 de `docs/01_random_walks_rigor_finance.md`).
2.  **Tiempo Esperado de Absorción (Duración Activa):** El número de pasos esperados $m_k$ que el precio permanecerá dentro de los límites activos satisface la ecuación de diferencias local (Sección 7 de `docs/01_random_walks_rigor_finance.md`):

$$m_k = 1 + p \, m_{k+1} + q \, m_{k-1}$$

con condiciones de frontera $m_L = m_U = 0$.

## Objetivos del Proyecto

1.  **Simulador de Caminata en Bins:** Implementar un motor de simulación de Monte Carlo en Python que modele los saltos del precio entre bins de Trader Joe dada una volatilidad y drift anualizados.
2.  **Cálculo de Métricas de Riesgo:**
    *   Estimación del tiempo esperado de salida (absorción) del rango activo.
    *   Probabilidad de desbalanceo asimétrico (quedar con 100% de token A o token B).
3.  **Algoritmo de Rebalanceo Óptimo:** Comparar el costo de transacción (fees de gas en la C-Chain de Avalanche) de rebalancear la posición contra la pérdida de comisiones por inactividad, usando la duración esperada $m_k$.
