## Soluciones (Cap. 2) — Rincón (2012): Caminatas aleatorias

Estas soluciones corresponden a los ejercicios **4–19** del Capítulo 2 (caminatas aleatorias y ruina del jugador).

Convención: \(X_n=X_0+\sum_{i=1}^n \xi_i\) con \(\xi_i\in\{+1,-1\}\), \(P(\xi_i=+1)=p\), \(q=1-p\).

---

### Ejercicio 4 — Propiedad de Markov

**Enunciado.** Probar que una caminata aleatoria simple \(X_n\) sobre \(\mathbb Z\) es Markov:
\[
P(X_{n+1}=x_{n+1}\mid X_0=x_0,\ldots,X_n=x_n)=P(X_{n+1}=x_{n+1}\mid X_n=x_n).
\]

**Solución (rigurosa).** Observa que
\[
X_{n+1}=X_n+\xi_{n+1}.
\]
Luego, para cualquier historia \(X_0=x_0,\ldots,X_n=x_n\),
\[
P(X_{n+1}=x_{n+1}\mid X_0=x_0,\ldots,X_n=x_n)
=P(\xi_{n+1}=x_{n+1}-x_n\mid X_0=x_0,\ldots,X_n=x_n).
\]
Como \(\xi_{n+1}\) es independiente de \(\sigma(\xi_1,\ldots,\xi_n)\), y \((X_0,\ldots,X_n)\) es función de \((\xi_1,\ldots,\xi_n)\), se tiene independencia de \(\xi_{n+1}\) respecto del pasado:
\[
P(\xi_{n+1}=a\mid X_0=x_0,\ldots,X_n=x_n)=P(\xi_{n+1}=a).
\]
Por tanto la probabilidad anterior depende solo de \(x_n\) (vía \(x_{n+1}-x_n\)) y coincide con
\[
P(X_{n+1}=x_{n+1}\mid X_n=x_n),
\]
lo cual prueba Markov.

---

### Ejercicio 5 — Identidad de transición (ecuación de Chapman discreta)

**Enunciado.** Probar que
\[
P(X_{n+1}=x)=p\,P(X_n=x-1)+q\,P(X_n=x+1).
\]

**Solución.** Usando la partición por el último paso:
\[
\{X_{n+1}=x\}=\{X_n=x-1,\xi_{n+1}=+1\}\,\dot\cup\,\{X_n=x+1,\xi_{n+1}=-1\}.
\]
Entonces por aditividad y la independencia de \(\xi_{n+1}\) del pasado:
\[
P(X_{n+1}=x)=P(X_n=x-1)P(\xi_{n+1}=+1)+P(X_n=x+1)P(\xi_{n+1}=-1),
\]
igual a \(pP(X_n=x-1)+qP(X_n=x+1)\).

---

### Ejercicio 6 — Regreso al origen en el paso 6 (simétrica)

**Enunciado.** Para \(p=q=1/2\), hallar \(P(X_6=0)\).

**Solución.** \(X_6=0\iff\) #derechas \(R_6=3\). Como \(R_6\sim\mathrm{Bin}(6,1/2)\),
\[
P(X_6=0)=\binom{6}{3}2^{-6}=\frac{20}{64}=\frac{5}{16}.
\]

---

### Ejercicio 7 — Primera vez en 0 en el paso 6 (simétrica)

**Enunciado.** Para \(p=q=1/2\), hallar \(P(\text{primer regreso a 0 en }6)\).

**Solución (clásica; camino de Dyck + reflexión).**
Un regreso al origen en tiempo \(2n\) por primera vez equivale a un camino que:
1) empieza en 0, 2) nunca toca 0 en tiempos intermedios, 3) termina en 0 en \(2n\).
Para caminata simétrica, la probabilidad es \(\#\text{caminos}/2^{2n}\).

El número de caminos con primer retorno a 0 en \(2n\) es
\[
\frac{1}{2n-1}\binom{2n}{n},
\]
por lo que para \(2n=6\Rightarrow n=3\),
\[
P(\tau_0=6)=\frac{1}{5}\binom{6}{3}\,2^{-6}=\frac{1}{5}\cdot 20\cdot \frac{1}{64}=\frac{1}{16}.
\]

---

### Ejercicio 8 — Función generadora de momentos (mgf) de \(X_n\)

**Enunciado.** Probar \(M(t)=E[e^{tX_n}]=(pe^t+qe^{-t})^n\) y recuperar \(E[X_n]\), \(\mathrm{Var}(X_n)\).

**Solución.** Por independencia:
\[
E[e^{tX_n}]=E\Big[\prod_{i=1}^n e^{t\xi_i}\Big]=\prod_{i=1}^n E[e^{t\xi_i}]
=[pe^t+qe^{-t}]^n.
\]
Luego \(\log M(t)=n\log(pe^t+qe^{-t})\).

Derivando:
\[
E[X_n]=M'(0)=n(p-q),
\]
porque \(E[\xi]=p-q\).
Además \(\mathrm{Var}(X_n)=n\,\mathrm{Var}(\xi)=n(E[\xi^2]-E[\xi]^2)=n(1-(p-q)^2)=4npq\).

---

### Ejercicio 9 — Derivar (2.1) usando \(L_n\)

**Idea.** \(L_n\) = #pasos a la izquierda. Entonces \(L_n=(n-X_n)/2\) y también es binomial \(\mathrm{Bin}(n,q)\).

**Solución.** Como \(\xi_i=-1\) con probabilidad \(q\), \(L_n=\sum_{i=1}^n 1_{\{\xi_i=-1\}}\sim\mathrm{Bin}(n,q)\).
Además \(X_n=(\#R)-(\#L)=n-2L_n\Rightarrow L_n=(n-X_n)/2\).
Así, para \(|x|\le n\) y paridad compatible:
\[
P(X_n=x)=P\Big(L_n=\frac{n-x}{2}\Big)=\binom{n}{(n-x)/2}q^{(n-x)/2}p^{(n+x)/2},
\]
que coincide con (2.1).

---

### Ejercicio 10 — Simetría en \(x\) ssi \(p=1/2\)

**Enunciado.** Probar que \(P(X_n=x)=P(X_n=-x)\) para todo \(x\) admisible ssi \(p=q\).

**Solución.** Usando la fórmula:
\[
P(X_n=x)=\binom{n}{(n+x)/2}p^{(n+x)/2}q^{(n-x)/2}.
\]
Y
\[
P(X_n=-x)=\binom{n}{(n-x)/2}p^{(n-x)/2}q^{(n+x)/2}.
\]
Como \(\binom{n}{(n+x)/2}=\binom{n}{(n-x)/2}\), la igualdad para algún \(x\neq 0\) implica
\[
p^{(n+x)/2}q^{(n-x)/2}=p^{(n-x)/2}q^{(n+x)/2}\iff \Big(\frac{p}{q}\Big)^{x}=1.
\]
Para \(x\neq 0\) esto equivale a \(p/q=1\Rightarrow p=q=1/2\).
Si \(p=q\), la simetría es inmediata.

---

### Ejercicio 11 — Primera visita al estado \(n\ge 1\)

Sea \(\tau_n=\min\{k\ge 0: X_k=n\}\). Se pide \(P(\tau_n<\infty)\).

**Solución por ecuación en diferencias (primer paso).**
Define \(h(i)=P_i(\tau_n<\infty)\) donde \(P_i\) es probabilidad con \(X_0=i\).
Entonces para \(i<n\),
\[
h(i)=p\,h(i+1)+q\,h(i-1),
\]
con condición \(h(n)=1\) y condición de “no explosión” al \(i\to-\infty\) (acotación \(0\le h\le 1\)).

La solución general (caso \(p\neq q\)) es \(h(i)=A+B(q/p)^i\).
Imponiendo \(h(n)=1\) y acotación al \(i\to-\infty\):
- Si \(p>q\Rightarrow q/p<1\), entonces \((q/p)^i\to\infty\) cuando \(i\to-\infty\), por lo que debe ser \(B=0\). Así \(h(i)\equiv 1\) y en particular \(h(0)=1\).
- Si \(p<q\Rightarrow q/p>1\), entonces \((q/p)^i\to 0\) cuando \(i\to-\infty\), y puede quedar \(B\neq 0\). Usando \(h(n)=1\) y que \(h(i)\to 0\) al \(i\to-\infty\) se obtiene \(A=0\) y \(B=(p/q)^n\). Por tanto \(h(0)=(p/q)^n\).

Resultado:
\[
P(\tau_n<\infty)=
\begin{cases}
(p/q)^n,& p<1/2,\\
1,& p\ge 1/2,
\end{cases}
\]
que equivale a (2.18) tal como aparece en el texto.

**Generalización desde \(X_0=m\).**
Si \(m<n\): reemplaza 0 por \(m\) en la solución y obtienes
\[
P_m(\tau_n<\infty)=
\begin{cases}
(p/q)^{n-m},& p<1/2,\\
1,& p\ge 1/2.
\end{cases}
\]
Si \(m>n\), por simetría (hitting hacia abajo) intercambias \(p\) y \(q\) o consideras \(X'_k=-X_k\).

---

### Ejercicio 12 — Algoritmo aleatorio de búsqueda (uniforme en {0,...,k-1})

Sea \(T_k\) el tiempo esperado para llegar a 0 iniciando en \(k\).

Para \(k=0\), \(T_0=0\). Para \(k\ge 1\), en un paso vas a un estado uniforme en \(\{0,1,\dots,k-1\}\), así:
\[
T_k=1+\frac{1}{k}\sum_{j=0}^{k-1}T_j.
\]
Define \(S_k=\sum_{j=0}^k T_j\). Entonces
\[
T_k=1+\frac{S_{k-1}}{k},\qquad S_k=S_{k-1}+T_k.
\]
Sustituyendo:
\[
S_k=S_{k-1}+1+\frac{S_{k-1}}{k} = 1+\Big(1+\frac{1}{k}\Big)S_{k-1}.
\]
Con \(S_0=0\). Se obtiene por inducción:
\[
S_k=(k+1)H_k-(k+1),
\]
donde \(H_k=\sum_{i=1}^k \frac{1}{i}\) es el k-ésimo número armónico.
Luego
\[
T_k=S_k-S_{k-1}=H_k.
\]
**Respuesta:** el número esperado de pasos es \(T_k=H_k\sim \log k + \gamma\).

---

### Ejercicio 13 — Recurrencia y retorno al origen (vía \(f_{ij}\))

Se define \(f_{ij}=P_i(\exists n\ge 1: X_n=j)\).

**(a)** \(f_{-1,-1}=f_{-1,0}f_{0,-1}=f_{0,1}^2\): por homogeneidad espacial y Markov,
desde \(-1\) para volver a \(-1\) debes pasar por 0 con prob \(f_{-1,0}\), y desde 0 volver a \(-1\) con prob \(f_{0,-1}\).
Además por simetría espacial (traslación) \(f_{-1,0}=f_{0,1}\) y \(f_{0,-1}=f_{0,1}\) (reflexión + intercambio p/q si aplica).

**(b)** Primer paso desde 0:
\[
f_{00}=p f_{10}+q f_{-1,0}.
\]

**(c)** Primer paso desde 0 para alcanzar +1:
\[
f_{01}=p\cdot 1 + q f_{-1,1}=p+q f_{01}^2,
\]
porque desde -1 para llegar a +1 debes cruzar 0 y luego llegar a +1, lo cual produce el cuadrado (descomposición estándar de hitting por regeneración en 0).

**(d)** Resolver \(f_{01}=p+q f_{01}^2\Rightarrow q f_{01}^2-f_{01}+p=0\).
Raíces:
\[
f_{01}=\frac{1\pm |p-q|}{2q}.
\]
Las soluciones en \([0,1]\) son \(1\) y \(p/q\) (cuando \(p<q\)).

**(e)** Análogo \(f_{10}\in\{1,q/p\}\).

**(f)** Entonces
\[
f_{00}=p f_{10}+q f_{-1,0}.
\]
Si \(p<q\): \(f_{10}=q/p>1\) no es válido, así \(f_{10}=1\) pero \(f_{-1,0}=p/q\). Da \(f_{00}=p\cdot 1+q(p/q)=2p\).
Si \(p>q\): \(f_{-1,0}=1\) y \(f_{10}=q/p\), da \(f_{00}=p(q/p)+q\cdot 1=2q\).
En conjunto:
\[
f_{00}=2\min(p,q)=1-|p-q|.
\]

---

## El problema de la ruina del jugador

### Ejercicio 14 — Derivar la ecuación en diferencias

Sea \(u_k=P(X_\tau=0\mid X_0=k)\) y \(\tau=\min\{n: X_n\in\{0,N\}\}\).

Condiciona por el primer paso:
- con probabilidad \(p\) vas a \(k+1\) y luego la probabilidad de ruina es \(u_{k+1}\),
- con probabilidad \(q\) vas a \(k-1\) y luego la probabilidad de ruina es \(u_{k-1}\).

Así:
\[
u_k = p u_{k+1} + q u_{k-1},\qquad k=1,\dots,N-1,
\]
con \(u_0=1\), \(u_N=0\).

---

### Ejercicio 15 — Resolver la ecuación por ecuación característica

**(a)-(b)** Propón \(u_k=a m^k\). Sustituyendo:
\[
a m^k = p a m^{k+1} + q a m^{k-1}\ \Rightarrow\ 1 = p m + q m^{-1}.
\]
Multiplicando por \(m\):
\[
p m^2 - m + q=0.
\]

**(c)-(d)** Si \(p\neq q\), raíces \(m_1=1\), \(m_2=q/p\). Solución general:
\[
u_k = A + B (q/p)^k.
\]
Con \(u_0=1\Rightarrow A+B=1\).
Con \(u_N=0\Rightarrow A+B(q/p)^N=0\).
Resolviendo:
\[
u_k=\frac{(q/p)^k-(q/p)^N}{1-(q/p)^N}.
\]

**(e)** Si \(p=q=1/2\), la ecuación se vuelve \(u_{k+1}-2u_k+u_{k-1}=0\), cuya solución general es lineal:
\[
u_k=A+Bk.
\]
Con \(u_0=1, u_N=0\Rightarrow u_k=1-k/N=(N-k)/N\).

---

### Ejercicio 16 — Ruina del jugador B y \(u_k+v_{N-k}=1\)

Visto desde B, su capital inicial es \(N-k\) y su probabilidad de “ganar” es \(q\).
Entonces su probabilidad de ruina \(v_{N-k}\) se obtiene sustituyendo \(k\mapsto N-k\) y \(p\mapsto q\) en la fórmula de \(u\).

Para verificar \(u_k+v_{N-k}=1\): el juego termina a.s. en absorción (N finito y estados absorbentes), y exactamente uno de los dos se arruina.

---

### Ejercicio 17 — Derivar ecuación para \(m_k=E[\tau\mid X_0=k]\)

Por análisis del primer paso:
tras una apuesta siempre pasa 1 unidad de tiempo y luego estás en \(k+1\) con prob \(p\) o en \(k-1\) con prob \(q\):
\[
m_k = 1 + p m_{k+1} + q m_{k-1},\qquad k=1,\dots,N-1,
\]
con \(m_0=m_N=0\).

---

### Ejercicio 18 — Permitir empates (stay-put) no cambia \(u_k\)

Ahora \(P(\Delta=+1)=p\), \(P(\Delta=-1)=q\), \(P(\Delta=0)=r\), con \(p+q+r=1\).
Sea \(u_k\) probabilidad de absorción en 0.
Por primer paso:
\[
u_k = p u_{k+1} + q u_{k-1} + r u_k.
\]
Reordenando:
\[
(1-r)u_k = p u_{k+1} + q u_{k-1}.
\]
Dividiendo por \(1-r\) y definiendo \(p'=\frac{p}{1-r}\), \(q'=\frac{q}{1-r}\) (con \(p'+q'=1\)):
queda exactamente la ecuación original:
\[
u_k = p' u_{k+1} + q' u_{k-1},
\]
con las mismas fronteras. Por unicidad de solución, \(u_k\) es la misma que en (2.14) pero reemplazando \(p',q'\) en la fórmula, lo cual simplifica a la misma forma funcional en términos de \(q/p\).

---

### Ejercicio 19 — Cota \(m_k\le N^2/2\)

**Caso simétrico.** \(m_k=k(N-k)\). El máximo ocurre en \(k=N/2\) y vale \(N^2/4\le N^2/2\).

**Caso asimétrico.** Se puede demostrar la cota por:
- usar la expresión cerrada de \(m_k\) y acotar términos geométricos, o
- construir una supermartingala adecuada y aplicar opcional stopping, o
- (más elemental) mostrar que \(m_k\) es cóncava en \(k\) y comparar con la solución simétrica que maximiza la duración.

Una ruta directa: la duración esperada es máxima cerca de juego justo; al alejarse \(p\) de \(1/2\), la deriva acelera la absorción, por lo que \(m_k\) disminuye y queda por debajo del máximo simétrico \(N^2/4\).

---

### Checks computacionales (recomendado)

En `projects/random-walks-finance/` puedes validar:

- Ej. 6: `python -m src.cli pmf --n 6 --x 0 --p 0.5`
- Ruina/duración: `python -m src.cli ruin ...` y `python -m src.cli duration ...`

