# Guía Matemática Visual: Valuación de Opciones de Barrera Discreta

Esta guía explica la matemática estocástica y la programación dinámica aplicadas a la valuación de opciones exóticas de barrera discreta sobre Avalanche.

---

## 1. El Árbol Binomial y su Flujo de Tiempo

Modelamos el precio del activo subyacente $S$ (por ejemplo, AVAX) como un proceso estocástico discreto en un árbol binomial de $N$ pasos. En cada paso de tiempo $\Delta t$, el precio puede subir por un factor $u$ o bajar por un factor $d$:

```text
                                                 [ S * u^2 ] (Paso 2)
                                                /
                                  [ S * u ] ---
                                 /              \
                   [ S_0 ] ------                [ S * u * d ]
                     (n=0)       \              /
                                  [ S * d ] ---
                                                \
                                                 [ S * d^2 ]
```

### Parámetros de Calibración (Modelo de Cox-Ross-Rubinstein)
Dada la volatilidad anualizada $\sigma$, la tasa libre de riesgo $r$ y el paso de tiempo $\Delta t = T/N$:

$$u = e^{\sigma \sqrt{\Delta t}}, \qquad d = e^{-\sigma \sqrt{\Delta t}} = \frac{1}{u}$$

La probabilidad bajo la **medida neutral al riesgo** (la probabilidad $p^*$ que hace que el precio descontado del activo sea una martingala) es:

$$p^* = \frac{e^{r \Delta t} - d}{u - d}, \qquad q^* = 1 - p^*$$

---

## 2. Programación Dinámica (Inducción Hacia Atrás)

El precio de una opción europea tradicional depende únicamente del valor final del subyacente en el vencimiento $T$. Las opciones de barrera son **dependientes de la trayectoria** (path-dependent). Para resolverlas de manera eficiente, utilizamos **programación dinámica** barriendo la rejilla de atrás hacia adelante (backward induction).

```text
Paso n (Calcular)                     Paso n+1 (Conocido)
                                        [ V_{n+1, j+1} ] (Nodo superior)
                                       / 
                    [ V_{n, j} ] <=== |  (Ponderado por p* y descontado por e^{-r dt})
                                       \
                                        [ V_{n+1, j-1} ] (Nodo inferior)
```

La ecuación local de valuación en cada nodo interno es:

$$V_{n, j} = e^{-r \Delta t} \left( p^* V_{n+1, j+1} + q^* V_{n+1, j-1} \right)$$

---

## 3. Barreras Discretas como Estados Absorbentes (Knock-out)

En una opción de tipo **Knock-out**, si el precio toca o supera una barrera superior $U$ o cae por debajo de una barrera inferior $L$ en cualquiera de los momentos de observación, la opción se extingue inmediatamente perdiendo todo su valor (se vuelve $0$).

En términos estocásticos, las barreras actúan como **estados de absorción con recompensa cero**.

### Representación de la Rejilla con Barreras

```text
  [ Barrera Superior U ] ======================================== (Payoff = 0)
                            /           /           /
                       [ Nodo ] --- [ Nodo ] --- [ Nodo ]
                      /       \     /       \     /       \
                 [ S_0 ]       \   /         \   /         [ Payoff final ]
                      \       /     \       /     \       /
                       [ Nodo ] --- [ Nodo ] --- [ Nodo ]
                            \           \           \
  [ Barrera Inferior L ] ======================================== (Payoff = 0)
```

### Algoritmo de Evaluación de Nodo
Para cada paso $n$ desde $N-1$ hasta $0$ y cada nodo $j$:

$$V_{n, j} = \begin{cases} 
0 & \text{si } S_{n, j} \ge U \quad \text{o} \quad S_{n, j} \le L \\
e^{-r \Delta t} \left( p^* V_{n+1, j+1} + q^* V_{n+1, j-1} \right) & \text{en otro caso}
\end{cases}$$

---

## 4. El Sesgo de Discretización y Corrección de Continuidad

Una opción de barrera continua observa el precio en cada instante de tiempo. Una opción de barrera discreta en cadena solo lo observa en intervalos específicos (por ejemplo, cada bloque o cada hora vía oráculo).
*   **Problema:** Una simulación continua siempre arrojará una probabilidad de tocar la barrera mayor o igual que la observación discreta, pues el precio podría tocar la barrera en medio de dos observaciones y regresar.
*   **Solución:** Broadie, Glasserman y Kou (1997) demostraron que podemos corregir la barrera discreta $H_{discreta}$ para aproximarla a la continua $H_{continua}$ desplazando la barrera una distancia equivalente a:

$$H_{discreta} = H_{continua} \cdot e^{\pm \beta \sigma \sqrt{\Delta t}}$$

Donde:
*   $\beta \approx 0.5826$ es una constante universal derivada de la función zeta de Riemann.
*   El signo es $+$ para una barrera inferior y $-$ para una barrera superior.

Esta corrección física permite valorar opciones discretas en cadena de forma extremadamente precisa sin sobrecargar la computación del oráculo.
