import os
import numpy as np
import pandas as pd

def generate_realistic_historical_data():
    # Fijar semilla de reproducibilidad
    np.random.seed(42)
    
    n_steps = 5000
    start_price = 35.0  # AVAX price in USD
    base_vol = 0.65     # 65% unconditional volatility
    drift = 0.15        # 15% drift
    
    # Parámetros GARCH(1,1) para simular la realidad del mercado
    alpha = 0.08
    beta = 0.90
    omega = (base_vol ** 2) * (1.0 - alpha - beta)
    
    prices = np.zeros(n_steps + 1)
    vols = np.zeros(n_steps + 1)
    
    prices[0] = start_price
    vols[0] = base_vol
    
    # Delta t para un paso de 1 minuto (en fracción de año)
    dt = 1.0 / (365.0 * 24.0 * 60.0) 
    
    variance = base_vol ** 2
    
    for t in range(1, n_steps + 1):
        # Shock normal estándar
        Z = np.random.normal(0, 1)
        
        # Ocasionales choques de cisne negro extremos (black swans)
        # 0.2% de chance de un salto extremo (pánico)
        if np.random.rand() < 0.002:
            Z = np.random.normal(-5.0, 1.5)  # Caída masiva de 5 sigmas
            
        # Actualización GARCH de varianza
        variance = omega + alpha * (variance * (Z ** 2)) + beta * variance
        variance = np.clip(variance, 0.01, 4.0)  # Limitar varianza entre 10% y 200% vol
        vol_t = np.sqrt(variance)
        vols[t] = vol_t
        
        # Movimiento Browniano Geométrico con la volatilidad GARCH del bloque
        return_t = (drift - 0.5 * variance) * dt + vol_t * np.sqrt(dt) * Z
        prices[t] = prices[t-1] * np.exp(return_t)
    
    # Crear DataFrame
    timestamps = pd.date_range(start="2026-05-30 00:00:00", periods=n_steps+1, freq="min")
    df = pd.DataFrame({
        "timestamp": timestamps,
        "price": prices,
        "volatility_true": vols
    })
    
    # Guardar en CSV
    output_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(output_dir, "avax_usdc_historical.csv")
    df.to_csv(output_path, index=False)
    print(f"¡Dataset histórico generado con éxito en: {output_path}!")
    print(f"  - Registros: {len(df):,}")
    print(f"  - Precio Inicial: ${prices[0]:.2f} | Precio Final: ${prices[-1]:.2f}")
    print(f"  - Retorno Acumulado: {((prices[-1] / prices[0]) - 1.0) * 100:.2f}%")

if __name__ == "__main__":
    generate_realistic_historical_data()
