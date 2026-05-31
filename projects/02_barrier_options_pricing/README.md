# Proyecto 02: Opciones de Barrera Discreta en Cadena (DeFi Structured Products)

Este proyecto desarrolla un motor de valuación y un contrato inteligente para opciones exóticas de barrera discreta (knock-out/knock-in) sobre activos de Avalanche (como AVAX o liquid staking tokens como sAVAX), utilizando programación dinámica y verificación por simulación.

## Fundamentos Matemáticos

A diferencia de las opciones tradicionales en continuo, las opciones de barrera discreta asumen observaciones del precio en momentos discretos del tiempo (por ejemplo, diariamente o cada 4 horas vía oráculo).

### Pricing por Programación Dinámica (Inducción Hacia Atrás)

En un árbol binomial de $N$ pasos que simula los caminos del precio de un activo $S_n$:
*   En cada nodo $(n, j)$, el precio de la opción $V_{n, j}$ se calcula descontando la esperanza bajo la medida neutral al riesgo $p^*$:

$$V_{n, j} = e^{-r \Delta t} \left( p^* V_{n+1, j+1} + (1 - p^*) V_{n+1, j-1} \right)$$

*   **Condición de Barrera Absorbente (Knock-out):** Si el nodo $(n, j)$ toca o cruza la barrera superior $U$ o inferior $L$, el valor de la opción es inmediatamente anulado:

$$V_{n, j} = 0 \quad \text{si } S_{n, j} \le L \quad \text{o} \quad S_{n, j} \ge U$$

*   **Condición Terminal:** En el paso final $T$, el payoff para una opción de compra (Call) estándar es:

$$V_{T, j} = \max(S_{T, j} - K, 0)$$

## Objetivos del Proyecto

1.  **Motor de Pricing (Python):** Desarrollar un modelo de valuación en rejilla binomial para opciones discreta knock-out y knock-in.
2.  **Verificador Monte Carlo:** Validar los precios de la rejilla mediante simulaciones de Monte Carlo con corrección de continuidad de Broadie-Glasserman-Kou.
3.  **Boceto de Contrato Inteligente (Solidity):** Diseñar las interfaces y lógica de liquidación en EVM de una opción de barrera discreta alimentada por un oráculo periódico.
