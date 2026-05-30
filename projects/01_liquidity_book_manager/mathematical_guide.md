# Guía Matemática Visual: Caminatas Aleatorias en Bins de Trader Joe

Esta guía explica de manera visual e intuitiva la matemática que conecta las caminatas aleatorias y la teoría de la ruina con la provisión de liquidez activa en el modelo de **Liquidity Book** de Trader Joe en Avalanche.

---

## 1. El Mapa de Discretización: De Precio Real a Bins

En un Pool tradicional (como Uniswap V2), el precio es continuo. En el **Liquidity Book de Trader Joe**, el espacio de precios se fragmenta en contenedores discretos llamados **bins**. Cada bin tiene un ancho constante en términos de puntos básicos (basis points, bp), determinado por el parámetro `binStep` ($s$).

La relación matemática que mapea el precio real $S$ a un índice de bin entero $i \in \mathbb{Z}$ es:

$$S(i) = S_0 \cdot (1 + s)^i$$

Donde:
*   $S_0$ es un precio de referencia base.
*   $s$ es el tamaño del paso (por ejemplo, $s = 0.0015$ para 15 puntos básicos).

### Representación Visual de la Rejilla de Bins

```text
    ... <--- [ Bin i-1 ] <--- [ Bin i ] ---> [ Bin i+1 ] ---> ...
                 ^                ^              ^
                 |                |              |
           Precio: 99.70    Precio: 99.85   Precio: 100.00
                           (Precio Actual)
```

En cada intervalo de tiempo discreto $\Delta t$, el precio da un "salto" de un bin a otro. Esto convierte la trayectoria de precios en una **caminata aleatoria simple** sobre los enteros.

---

## 2. Movimiento y Probabilidad: La Caminata con Drift

Modelamos los cambios de bin como pasos discretos $\xi_i \in \{+1, -1\}$.
*   Si el precio sube al bin de la derecha ($i \to i+1$): ocurre con probabilidad $p$.
*   Si el precio baja al bin de la izquierda ($i \to i-1$): ocurre con probabilidad $q = 1 - p$.

```text
                     q (Baja un bin)         p (Sube un bin)
                  <------------------ [Bin i] ------------------>
                  |                                             |
                  v                                             v
              [Bin i-1]                                     [Bin i+1]
```

### Calibración desde variables continuas de mercado
Para conectar esto con una volatilidad anualizada $\sigma$ y una tasa de deriva (drift) anualizada $\mu$ del precio del activo (por ejemplo, AVAX), calibramos los parámetros discretos:

$$\Delta t = \left( \frac{\ln(1 + s)}{\sigma} \right)^2$$

$$p = \frac{1}{2} \left( 1 + \frac{\mu - \frac{1}{2}\sigma^2}{\sigma} \sqrt{\Delta t} \right)$$

Este sistema asegura que, en el límite cuando $\Delta t \to 0$, la caminata aleatoria discreta converge al Movimiento Browniano Geométrico del mercado continuo.

---

## 3. Barreras de Liquidez como Muros de Absorción

Cuando un proveedor de liquidez (LP) coloca sus activos en Trader Joe, selecciona un rango de bins definido entre un límite inferior $L$ y un límite superior $U$.
*   Mientras el precio se mantenga dentro del rango $(L, U)$, el LP acumula comisiones activas.
*   Si el precio sale del rango tocando $L$ o $U$, la posición queda 100% desbalanceada (solo contiene un token inactivo) y deja de ganar comisiones.

En teoría estocástica, $L$ y $U$ son **barreras absorbentes** (muros de absorción).

```text
  [Muro L]                                                   [Muro U]
 (Absorción)                                                (Absorción)
    ||                                                         ||
    || <=== [Bin L+1] <=== ... <=== [Bin k] ===> ... ===> [Bin U-1] ||
    ||                               (Actual)                  ||
```

---

## 4. El Análisis del Primer Paso: ¿Por qué funcionan las ecuaciones?

Queremos calcular el **Tiempo Esperado de Absorción** $m_k$, que es el número de pasos promedio que el precio tardará en salir del rango $[L, U]$ partiendo desde el bin actual $k$.

Para derivar la ecuación sin memorizarla, usamos el **Análisis del Primer Paso**:

1.  Estando en el bin $k$, tomamos exactamente **1 paso** de tiempo.
2.  Con probabilidad $p$, el precio sube al bin $k+1$. A partir de ahí, el tiempo esperado para salir será $m_{k+1}$.
3.  Con probabilidad $q$, el precio baja al bin $k-1$. A partir de ahí, el tiempo esperado para salir será $m_{k-1}$.

Sumando ambos caminos ponderados por sus probabilidades de ocurrencia, obtenemos la ecuación en diferencias local:

$$m_k = 1 + p \cdot m_{k+1} + q \cdot m_{k-1}$$

### Condiciones de Frontera (Los Muros)
Si ya estamos en las barreras $L$ o $U$, el tiempo para salir es cero porque ya hemos salido:
*   $m_L = 0$
*   $m_U = 0$

---

## 5. Soluciones Cerradas y Comportamiento Cualitativo

Resolver esta ecuación en diferencias proporciona fórmulas exactas para analizar el riesgo del pool sin necesidad de correr simulaciones lentas de Monte Carlo.

### Caso A: Mercado Justo o Sin Drift ($p = q = 0.5$)
Si el mercado no tiene una tendencia clara de subida o bajada, la solución es simétrica:

$$m_k = (k - L)(U - k)$$

**Representación de la Duración:**
La duración máxima ocurre exactamente en el centro del rango ($k = (L+U)/2$) y decrece de forma cuadrática a medida que el precio se acerca a cualquiera de las dos barreras.

```text
Tiempo Esperado (m_k)
      ^
      |             * * * (Máximo en el centro)
      |           *       *
      |         *           *
      |       *               *
      +------|-----------------|------> Bin (k)
             L                 U
```

### Caso B: Mercado con Tendencia ($p \neq q$)
Si el mercado tiene un drift definido (por ejemplo, AVAX subiendo de precio de manera constante, $p > 0.5$):

$$m_k = \frac{k - L}{p - q} - \frac{U - L}{p - q} \cdot \left( \frac{1 - (q/p)^{k-L}}{1 - (q/p)^{U-L}} \right)$$

**Comportamiento Físico:**
Bajo un fuerte drift, el tiempo esperado cae drásticamente. El precio es empujado rápidamente hacia una de las barreras (absorción rápida hacia la derecha si $p > 0.5$), reduciendo la ventana de tiempo en la cual el LP cobra comisiones.
