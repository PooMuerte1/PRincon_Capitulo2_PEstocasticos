# Guía Matemática Visual: Riesgo de Insolvencia en Protocolos de Préstamo

Esta guía explica el modelado estocástico del riesgo de liquidación e insolvencia en protocolos de préstamo descentralizados (lending) utilizando la teoría de la ruina del jugador y caminatas aleatorias discreta.

---

## 1. La Posición de Deuda como una Caminata Aleatoria

En un protocolo de préstamo (como Benqi o Aave en Avalanche), un usuario deposita un colateral $C$ y toma prestado una deuda $D$. La seguridad de la posición se mide a través de la distancia entre el colateral y la deuda.

Modelamos la salud de la deuda en unidades discretas de valor. Sea $X_n$ la holgura de capital (colateral excedente sobre la deuda) en el bloque $n$:

$$X_n = \text{Valor del Colateral}_n - \text{Deuda}_n$$

```text
   Incremento del precio del colateral (Probabilidad p)
              +------------------> [ Holgura X_n ] ------------------> [ Sube Salud ]
              |
              v (Probabilidad q = 1 - p)
   [ Cae Salud ] (Tendencia bajista del mercado)
```

Si el precio del colateral cae, $X_n$ retrocede. Si el precio sube, $X_n$ avanza. En un mercado bajista extremo o de alta volatilidad, la probabilidad de caída $q$ es mayor que la de subida ($q > p$).

---

## 2. La Ruina del Protocolo: Insolvencia Activa

Definimos los estados de nuestra caminata sobre la holgura de capital $X_n \in [0, N]$:
*   **$X_n = 0$ (Insolvencia):** El valor del colateral es igual o menor a la deuda. El protocolo incurre en pérdida neta (deuda incobrable o *bad debt*). Este es el **muro de ruina**.
*   **$X_n = N$ (Salud Segura):** La holgura es lo suficientemente amplia como para considerar la posición totalmente segura.
*   **$X_0 = k$ (Posición Inicial):** El punto de partida de la holgura, determinado por el parámetro **LTV** (Loan-to-Value) del protocolo. Un LTV más alto significa un capital inicial $k$ más cercano a 0 (mayor riesgo).

```text
    [Muro de Insolvencia]                                     [Muro de Salud]
         (Ruina 0)                                               (Meta N)
            ||                                                      ||
            || <=== [Bin 1] <=== ... <=== [Bin k] ===> ... ===> [Bin N] ||
            ||                         (Salud LTV)                  ||
```

### La Probabilidad Asimétrica de Ruina
Bajo una tendencia de mercado dada por la tasa de cambio $r = q/p$:

$$u_k = \frac{r^k - r^N}{1 - r^N}$$

Si $q > p$ (mercado cayendo), la base $r > 1$ crece de manera geométrica. Esto muestra por qué la probabilidad de insolvencia se dispara exponencialmente ante pequeñas variaciones en el LTV (que disminuyen $k$).

---

## 3. El Impacto de la Latencia de Liquidación (Slippage)

En el mundo real, la liquidación de una posición no ocurre instantáneamente al tocar el umbral de liquidación. Existe un retraso discreto compuesto por:
1.  Tiempo de actualización del oráculo en Avalanche.
2.  Tiempo de minado de bloques y ejecución de la transacción del liquidador ($\tau_{delay}$ bloques).

Durante esta ventana de tiempo de retraso, la caminata aleatoria del precio del colateral **continúa moviéndose**.

### Representación Visual de la "Zona de Caída Libre"

```text
                        Umbral de Liquidación (L)
                                  |
                                  v
                                  | [Zona de Caída Libre] 
  ... ===> [Bin L+2] ===> [Bin L+1] ===> [Bin L] ================> [ Insolvencia ] (X_n = 0)
                                  |       |
                                  |       +--- Latencia del Oráculo y Gas ---> (Transcurren \tau_delay bloques)
                                  v
                             [Liquidación exitosa si el precio
                              no toca 0 durante la latencia]
```

Si durante los $\tau_{delay}$ bloques de retraso el precio cae con velocidad $q$ y toca el valor de la deuda, el protocolo sufre insolvencia activa antes de que el liquidador pueda cerrar la posición.

La probabilidad de insolvencia considerando la latencia se modela calculando la probabilidad de que la caminata aleatoria toque la barrera absorbente $0$ dentro de los próximos $\tau_{delay}$ pasos, dado que se inició el proceso de liquidación en el bin $L$:

$$P(\text{Insolvencia} \mid \text{Inicio liquidación en L}) = P(\tau_0 \le \tau_{delay} \mid X_0 = L)$$

---

## 4. Calibración Óptima del LTV

El objetivo del proyecto es resolver el problema inverso: dado un nivel máximo de insolvencia tolerado por el protocolo $\alpha$ (por ejemplo, $\alpha = 0.05\%$), y conociendo el tiempo de latencia de red $\tau_{delay}$ y la volatilidad del activo:

1.  Calcular el umbral de liquidación óptimo $L$ para resistir la latencia.
2.  Calcular la holgura inicial $k$ requerida, lo que define el **LTV Máximo Seguro** bajo el cual el protocolo puede operar garantizando la solidez matemática de sus fondos.
