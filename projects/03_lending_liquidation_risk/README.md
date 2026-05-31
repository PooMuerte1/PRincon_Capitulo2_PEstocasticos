# Proyecto 03: Optimizador de Riesgo de Insolvencia en Protocolos de Préstamo

Este proyecto aplica la teoría de caminatas aleatorias y la ruina del jugador para evaluar y mitigar el riesgo de insolvencia activa en protocolos de préstamo (como Benqi o Aave) en la red Avalanche C-Chain, optimizando los parámetros de relación Préstamo-Valor (LTV) y umbral de liquidación bajo latencia de red.

## Fundamentos Matemáticos

Consideramos una posición de deuda respaldada por colateral. El factor de salud financiera de la posición en cada paso $n$ se puede modelar como un proceso estocástico discreto. 

### Modelado de Insolvencia como Ruina del Jugador

Si representamos el capital excedente (Colateral - Deuda - Margen de Liquidación) en unidades discretas $X_n \in [0, N]$:
*   $X_n = 0$ representa la insolvencia (el valor del colateral es menor que la deuda, generando pérdidas para el protocolo).
*   $X_n = N$ representa el retorno a una salud financiera holgada.
*   $X_0 = k$ es la salud inicial de la posición determinada por el LTV calibrado.

La probabilidad de ruina del protocolo $u_k$ ante una tendencia del precio bajista (con desventaja para el colateral, $p < 0.5$) se deriva de las ecuaciones de diferencias de la ruina asimétrica (Sección 6 de `docs/01_random_walks_rigor_finance.md`):

$$u_k = \frac{(q/p)^k - (q/p)^N}{1 - (q/p)^N}$$

Donde:
*   $p$ es la probabilidad de que el precio del colateral suba en un intervalo discreto.
*   $q = 1 - p$ es la probabilidad de caída.

### Incorporación de Latencia y Deslizamiento (Slippage)

En la práctica, cuando la posición cruza el umbral de liquidación, los liquidadores requieren un tiempo de ejecución (latencia de bloques de Avalanche y procesamiento de oráculos) para liquidar la posición. Esto se modela como una caminata que continúa su curso de caída en un número discreto de pasos de retraso, incrementando la gravedad de la ruina si el precio sigue cayendo.

## Objetivos del Proyecto

1.  **Analizador de Ruina de Deuda:** Desarrollar un modelo analítico que determine la probabilidad de que una posición de préstamo se vuelva insolvente antes de ser liquidada con éxito.
2.  **Calibrador de Parámetros de Riesgo (LTV):** Diseñar un optimizador que, dada una volatilidad histórica de un token de Avalanche, determine el LTV óptimo y el umbral de liquidación necesarios para mantener la probabilidad de insolvencia de la bóveda inferior al 0.1%.
3.  **Simulador de Latencia de Red:** Modelar el impacto de la congestión y latencia de bloque de Avalanche en el margen de liquidación seguro.
