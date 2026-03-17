## random-walks-finance

Proyecto Python para:

- simular caminatas aleatorias (incrementos \(\pm 1\))
- validar distribución exacta de \(X_n\)
- resolver y verificar ruina del jugador (\(u_k\)) y tiempo esperado (\(m_k\))
- estimar hitting/barreras por Monte Carlo

### Instalación

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m src.cli --help
```

### Ejemplos

```bash
# Validar P(X_n=x) vs Monte Carlo
python -m src.cli pmf --n 100 --x 6 --p 0.55 --paths 200000

# Ruina: u_k cerrada vs simulación
python -m src.cli ruin --N 100 --k 40 --p 0.505 --paths 200000

# Tiempo esperado a absorción: m_k cerrada vs simulación
python -m src.cli duration --N 100 --k 40 --p 0.5 --paths 200000

# Probabilidad de tocar barrera superior antes de T
python -m src.cli hit --p 0.5 --delta 0.01 --y0 0 --H 0.1 --T 200 --paths 200000
```

