# Guía Matemática Visual: Bóveda de Apuestas con Control de Ruina

Esta guía explica la matemática de control de riesgo estocástico para diseñar una bóveda de liquidez en Avalanche que actúe como contraparte en apuestas y autoajuste dinámicamente sus límites para impedir su propia ruina.

---

## 1. La Bóveda como la Casa frente a Caminatas Aleatorias

En un protocolo de juegos o apuestas descentralizadas, los usuarios apuestan contra una piscina de liquidez central (la Bóveda). 
*   **Capital de la Bóveda ($X_n$):** El saldo de fondos disponibles en la bóveda.
*   **Edge de la Casa:** Cada juego está diseñado para dar a la casa una pequeña ventaja matemática.
    *   La bóveda gana una apuesta (recibe capital del jugador) con probabilidad $q$.
    *   La bóveda pierde una apuesta (paga capital al jugador) con probabilidad $p = 1 - q$.
    *   Para la viabilidad del pool, el drift debe ser estrictamente positivo para la casa: $q > p$.

```text
               Bóveda Gana (Probabilidad q > p)
              +------------------> [ Capital X_n ] ------------------> [ Drift Positivo ]
              |
              v (Probabilidad p)
    Bóveda Pierde (Paga al jugador)
```

A largo plazo, la ley de los grandes números asegura que el capital de la bóveda tenderá a crecer. Sin embargo, en el corto plazo, rachas de victorias de los jugadores representan una caminata aleatoria que puede empujar el capital de la bóveda hacia $0$.

---

## 2. La Ruina de la Bóveda

Definimos los estados del capital de la bóveda $X_n \in [0, N]$:
*   **$X_n = 0$ (Quiebra):** La bóveda se queda sin fondos para pagar a los ganadores. Es el estado absorbente de **ruina**.
*   **$X_n = N$ (Objetivo de Reserva):** La bóveda alcanza su capacidad óptima y distribuye los excesos de ganancias a los proveedores de liquidez (LPs).
*   **$X_0 = k$ (Capital Actual):** El saldo actual de la bóveda en tokens.

### Probabilidad de Ruina de la Bóveda
Puesto que la casa tiene la ventaja ($q > p$, por lo que $p/q < 1$), la fórmula exacta de la ruina empezando con capital $k$ es:

$$u_k = \frac{(p/q)^k - (p/q)^N}{1 - (p/q)^N}$$

Esta probabilidad decrece exponencialmente a medida que el capital $k$ es más grande.

---

## 3. El Peligro de las Apuestas Masivas y la Discretización Dinámica

Si los jugadores pueden realizar apuestas de tamaño ilimitado, un solo jugador afortunado podría vaciar la bóveda en un solo paso, rompiendo la hipótesis de incrementos unitarios de la caminata aleatoria. Para evitar esto, la bóveda debe restringir la **Apuesta Máxima** ($B$).

Definimos el capital de la bóveda en unidades de la apuesta máxima permitida:

$$k' = \frac{k}{B}, \qquad N' = \frac{N}{B}$$

Ahora, cada apuesta representa un paso de tamaño $\pm 1$ en una caminata escalada $X'_n \in [0, N']$. La probabilidad de ruina del pool de la bóveda se convierte en:

$$u_{k'} = \frac{(p/q)^{k/B} - (p/q)^{N/B}}{1 - (p/q)^{N/B}}$$

### Control de Ruina en Cadena: Ajuste Dinámico de Apuesta Máxima

Fijamos un nivel de riesgo máximo tolerable para los LPs de la bóveda: $\alpha = 1\%$ ($0.01$). Queremos que la probabilidad de ruina sea siempre menor o igual a $\alpha$.

```text
              Si el Capital k de la Bóveda Cae:
              
    [ k = Alto ]   =======>  El Contrato permite una apuesta máxima  ===> B = Grande
    [ k = Bajo ]   =======>  El Contrato reduce la apuesta máxima    ===> B = Pequeño
                                      |
                                      +----> Garantiza que la distancia al muro 0
                                             medida en unidades de paso (k/B)
                                             sea siempre lo bastante grande para u_{k'} <= \alpha
```

Al despejar analíticamente el límite de apuesta $B$ de la ecuación de ruina para que $u_{k'} = \alpha$:

$$B(k) \approx \frac{k \cdot \ln(p/q)}{\ln(\alpha)}$$

*(asumiendo $N$ muy grande donde $(p/q)^{N/B} \to 0$)*.

### Regla del Contrato Inteligente
En cada bloque $n$, el contrato lee su saldo actual $k$ de la EVM y calcula la apuesta máxima permitida:

$$\text{MaxBet}(k) = \min \left( \frac{k \cdot \ln(p/q)}{\ln(\alpha)}, \text{Límite Operativo} \right)$$

Esto garantiza de forma matemática que la bóveda auto-regula su nivel de riesgo de quiebra, protegiendo los fondos de los proveedores de liquidez sin intervención manual.
