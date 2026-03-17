## Cap. 2 — Fórmulas explicadas “en cristiano” (sin LaTeX)

La idea de este archivo es que puedas leer todas las fórmulas importantes **sin saber LaTeX**.
Voy en orden: caminata aleatoria simple → distribución → retorno → ruina → duración.

---

### 1) Definición de caminata aleatoria simple

- Tenemos pasos independientes, cada uno vale **+1** o **-1**.
- Probabilidad de +1 = p.
- Probabilidad de -1 = q = 1 - p.
- Empezamos en 0.

La posición después de n pasos es:

- X_0 = 0
- X_n = suma de los n pasos (xi_1 + xi_2 + ... + xi_n)

**Ejemplo numérico**

- p = 0.6 (60% de ir a la derecha).
- q = 0.4 (40% de ir a la izquierda).
- Una trayectoria posible en 5 pasos: +1, -1, +1, +1, -1 → X_5 = +1 -1 +1 +1 -1 = +1.

---

### 2) Esperanza y varianza de X_n

Resultado:

- Esperanza (promedio) de X_n:  
  E[X_n] = n * (p - q)
- Varianza de X_n:  
  Var[X_n] = 4 * n * p * q

Intuición:

- Si p > q (más probabilidad de +1 que de -1), el promedio se va hacia la derecha.
- Si p < q, se va hacia la izquierda.
- La varianza crece lineal con n → la incertidumbre crece con los pasos.

**Ejemplo numérico**

- p = 0.6, q = 0.4, n = 10
- E[X_10] = 10 * (0.6 - 0.4) = 10 * 0.2 = 2
- Var[X_10] = 4 * 10 * 0.6 * 0.4 = 40 * 0.24 = 9.6

---

### 3) Distribución exacta de X_n (probabilidad de estar en x)

Después de n pasos:

- Para llegar a una posición X_n = x,
- hace falta que el número de pasos a la derecha sea:
  - R = (n + x) / 2
- y a la izquierda: L = n - R = (n - x) / 2

Condiciones:

- |x| <= n
- n y x deben tener la misma “paridad” (ambos pares o ambos impares).

Fórmula de la probabilidad:

- P(X_n = x) = C(n, R) * p^R * q^(n - R)
- donde:
  - R = (n + x) / 2
  - C(n, R) = “n sobre R”, el coeficiente binomial = número de formas de elegir R posiciones entre n.

**Ejemplo numérico simple**

Pregunta: ¿Cuál es la probabilidad de que X_4 = 0 cuando p = 0.5?

- n = 4, x = 0 ⇒ R = (4 + 0) / 2 = 2.
- C(4, 2) = 6.
- p = 0.5, q = 0.5.
- P(X_4 = 0) = 6 * (0.5)^2 * (0.5)^(4 - 2) = 6 * 0.25 * 0.25 = 6 * 0.0625 = 0.375.

---

### 4) Ruina del jugador (probabilidad de terminar en 0)

Contexto:

- Dos jugadores A y B se apuestan 1 unidad cada vez.
- Capital total entre los dos: N unidades.
- Capital inicial de A: k (entonces B tiene N - k).
- A tiene probabilidad p de ganar cada apuesta y q = 1 - p de perderla.
- Si A llega a 0 → se arruina.
- Si A llega a N → gana todo.

Definimos:

- u_k = probabilidad de que A se arruine empezando con capital k.

Ecuación que cumple u_k (para k = 1, 2, ..., N-1):

- u_k = p * u_{k+1} + q * u_{k-1}
- Condiciones de frontera:
  - u_0 = 1 (si empiezas arruinado, ya estás arruinado)
  - u_N = 0 (si ya tienes todo el dinero, no te puedes arruinar).

**Solución final (la fórmula importante):**

Caso 1: juego justo, p = q = 0.5

- u_k = (N - k) / N

Caso 2: juego no justo, p distinto de 0.5

- Define r = q / p
- u_k = (r^k - r^N) / (1 - r^N)

**Ejemplos numéricos**

1) Juego justo, p = 0.5, N = 10, k = 3

- u_3 = (10 - 3) / 10 = 7 / 10 = 0.7
- Interpretación: con juego justo, si tú tienes 3 y el otro 7, tienes 70% de probabilidad de arruinarte.

2) Juego con ligera ventaja, p = 0.51, q = 0.49, N = 10, k = 3

- r = q / p = 0.49 / 0.51 ≈ 0.960784
- r^10 ≈ (0.960784)^10 ≈ 0.66 (aprox)
- r^3 ≈ (0.960784)^3 ≈ 0.885 (aprox)
- u_3 ≈ (0.885 - 0.66) / (1 - 0.66) ≈ 0.225 / 0.34 ≈ 0.66
- Comparando:
  - juego justo: 0.70,
  - con pequeña ventaja: ≈ 0.66 (un poco menos de probabilidad de ruina).

---

### 5) Número esperado de apuestas hasta que termina el juego (duración esperada)

Definimos:

- m_k = esperanza del número de apuestas hasta que el juego termine
- (es decir, hasta que A se arruine o gane todo),
- empezando con capital k.

Ecuación que cumple (otra vez análisis del primer paso):

- m_k = 1 + p * m_{k+1} + q * m_{k-1}, para k = 1, 2, ..., N-1
- Condiciones de frontera:
  - m_0 = 0 (si ya estás en 0, el juego ya terminó)
  - m_N = 0 (si ya ganaste todo, también terminó).

**Solución importante (caso juego justo p = 0.5):**

- m_k = k * (N - k)

Esta fórmula es muy fácil de recordar:

- máximo cuando k = N/2
- simétrica en k y N - k

**Ejemplo numérico**

Juego justo, p = 0.5, N = 10

- Si k = 1:
  - m_1 = 1 * 9 = 9 apuestas en promedio.
- Si k = 5:
  - m_5 = 5 * 5 = 25 apuestas en promedio (es la máxima duración).

**Idea cualitativa en el caso no justo p ≠ 0.5**

- Si tienes ventaja fuerte (p mucho mayor que 0.5), el juego acaba más rápido (porque tiende a empujar hacia N).
- Si estás en desventaja fuerte (p mucho menor que 0.5), también acaba rápido (pero empujando hacia 0).
- El juego más “largo” suele ser cerca de p = 0.5 y k ≈ N/2.

---

### 6) Cómo leer y estudiar sin ver LaTeX

Te propongo esta estrategia:

1. **Primero** lee este archivo (`08_formulas_cap2_en_cristiano.md`) hasta que entiendas las ideas con ejemplos.
2. **Después**, mira el mismo resultado en:
   - `docs/01_random_walks_rigor_finance.md` (teoría),
   - `docs/04_soluciones_cap2_rincon.md` (ejercicios),
   y trata de reconocer las mismas fórmulas, aunque estén con símbolos.
3. Si algo de LaTeX no se entiende, tráelo al chat y lo traducimos a palabras + números.

Además:

- Si abres los `.md` en GitHub, muchas veces el LaTeX se ve mejor (como fórmulas rendereadas).
- En tu editor (por ejemplo VSCode/Cursor), puedes usar la **vista previa de Markdown** para ver el texto formateado y que las fórmulas no se vean tan “crudas”.

