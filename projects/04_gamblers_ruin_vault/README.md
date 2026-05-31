# Proyecto 04: Bóveda de Apuestas Peer-to-Pool con Control de Ruina

Este proyecto implementa y simula una bóveda de liquidez descentralizada para juegos estocásticos en Avalanche. La bóveda actúa como la "casa", y utiliza las ecuaciones exactas de la ruina del jugador para autoajustar dinámicamente los límites de apuesta de los usuarios, garantizando matemáticamente que la piscina de liquidez nunca quiebre.

## Fundamentos Matemáticos

Un usuario interactúa con la bóveda participando en juegos de azar o apuestas. Desde la perspectiva de la bóveda (la casa):
*   El capital actual de la bóveda es $k$ (unidades de token).
*   La capacidad máxima deseada de la bóveda es $N$.
*   La bóveda tiene una probabilidad $q$ de ganar cada apuesta (su ventaja matemática o *edge* de la casa), y una probabilidad $p = 1 - q$ de perderla.
*   Para que el negocio sea viable a largo plazo para los proveedores de liquidez (LPs), el *edge* debe ser positivo para la casa ($q > p$).

### Control Dinámico del Límite de Apuesta

La probabilidad de que la bóveda quiebre (llegue a $0$ de capital antes de alcanzar el objetivo $N$) empezando con capital $k$ es:

$$u_k = \frac{(p/q)^k - (p/q)^N}{1 - (p/q)^N}$$

Si los usuarios pudieran apostar sumas arbitrariamente grandes en un solo juego, la varianza aumentaría drásticamente y invalidaría el modelo discreto de incrementos de una unidad (o escalados). 

Para mantener la probabilidad de ruina acotada estrictamente por debajo de un nivel de seguridad $\alpha$ (por ejemplo, $\alpha = 1\%$):
1.  Se define el capital de la bóveda en unidades de la apuesta máxima permitida: $u_{k'} \le \alpha$, donde $k' = k / \text{MaxBet}$.
2.  Despejando de la ecuación de ruina, el contrato inteligente calcula dinámicamente en cadena el límite de apuesta permitido en cada bloque basándose en su nivel de reserva actual $k$:

$$\text{MaxBet}(k) = f(k, N, q, p, \alpha)$$

## Objetivos del Proyecto

1.  **Motor de Gestión de Riesgo (Python):** Desarrollar la biblioteca matemática que resuelva la ecuación inversa de la ruina para determinar la apuesta máxima segura.
2.  **Contrato de Bóveda en Solidity:** Escribir la interfaz y lógica del contrato inteligente de la bóveda en Avalanche C-Chain, incorporando la función de ajuste de límite dinámico.
3.  **Simulador de Ataque de Ballenas:** Simular escenarios donde jugadores con capital masivo intentan quebrar el pool bajo diferentes configuraciones del algoritmo de límite.
