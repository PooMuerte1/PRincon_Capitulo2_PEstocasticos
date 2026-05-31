import os
import time
import requests
import pandas as pd
import numpy as np

def fetch_period_data(name: str, aggregate: int, total_candles: int, filename: str):
    print("\n" + "=" * 80)
    print(f" DESCARGANDO DATASET: {name} (Velas de {aggregate} minutos) ")
    print("=" * 80)
    
    network = "avax"
    pool_address = "0xf01449c0ba930b6e2caca3def3ccbd7a3e589534"
    base_url = f"https://api.geckoterminal.com/api/v2/networks/{network}/pools/{pool_address}/ohlcv/minute"
    headers = {"Accept": "application/json;version=20230302"}
    
    all_candles = []
    before_timestamp = None
    
    while len(all_candles) < total_candles:
        params = {
            "aggregate": aggregate,
            "limit": 1000
        }
        if before_timestamp:
            params["before_timestamp"] = before_timestamp
            
        try:
            response = requests.get(base_url, headers=headers, params=params, timeout=12)
            if response.status_code != 200:
                print(f"Error en la API de GeckoTerminal (Status {response.status_code})")
                break
                
            data = response.json()
            ohlcv_list = data.get("data", {}).get("attributes", {}).get("ohlcv_list", [])
            if not ohlcv_list:
                print("No se encontraron más velas.")
                break
                
            all_candles.extend(ohlcv_list)
            before_timestamp = ohlcv_list[-1][0]
            
            print(f"  -> Descargadas {len(all_candles)} / {total_candles} velas...")
            time.sleep(1.0)
            
        except Exception as e:
            print(f"Error de red: {e}")
            break
            
    all_candles = all_candles[:total_candles]
    all_candles.reverse()
    
    timestamps = [pd.to_datetime(x[0], unit='s') for x in all_candles]
    prices = [float(x[4]) for x in all_candles]
    volumes = [float(x[5]) for x in all_candles]
    
    # Calcular la Volatilidad Realizada Móvil
    log_prices = np.log(prices)
    log_returns = np.diff(log_prices)
    
    # dt en fracción de año para este paso específico (5m o 15m)
    dt_step = (aggregate) / 525600.0
    
    vols = np.zeros(len(prices))
    vols[0] = 0.65
    
    # Ventana móvil de 30 velas
    for t in range(1, len(prices)):
        window = max(0, t - 30)
        if t - window >= 5:
            std_ret = np.std(log_returns[window:t], ddof=1)
            vols[t] = np.clip(std_ret / np.sqrt(dt_step), 0.10, 2.50)
        else:
            vols[t] = 0.65
            
    df = pd.DataFrame({
        "timestamp": timestamps,
        "price": prices,
        "volatility_true": vols,
        "volume_real": volumes
    })
    
    output_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(output_dir, filename)
    df.to_csv(output_path, index=False)
    
    max_price = df["price"].max()
    min_price = df["price"].min()
    price_change = ((prices[-1] / prices[0]) - 1.0) * 100
    realized_vol_ann = np.std(log_returns, ddof=1) / np.sqrt(dt_step)
    total_volume_usd = df["volume_real"].sum()
    avg_step_volume = df["volume_real"].mean()
    
    print("-" * 80)
    print(f"  - Rango Temporal: {timestamps[0]} a {timestamps[-1]}")
    print(f"  - Registros Guardados: {len(df):,} velas")
    print(f"  - Precio Inicial: ${prices[0]:.2f} USD | Precio Final: ${prices[-1]:.2f} USD")
    print(f"  - Retorno Neto Real: {price_change:+.2f}%")
    print(f"  - Volatilidad Anualizada Realizada: {realized_vol_ann*100:.2f}%")
    print(f"  - Volumen Total de Trading: ${total_volume_usd:,.2f} USD")
    print(f"  - Volumen Promedio por Vela: ${avg_step_volume:,.2f} USD")
    print(f"¡Dataset guardado en: {output_path}!\n")

def main():
    # 1. Dataset de 1 semana: 7 días = 10,080 minutos. Velas de 5 minutos = 2,016 velas
    fetch_period_data("1 SEMANA (5-min aggregate)", 5, 2016, "avax_usdc_1week.csv")
    
    # 2. Dataset de 1 mes: 30 días = 43,200 minutos. Velas de 15 minutos = 2,880 velas
    fetch_period_data("1 MES (15-min aggregate)", 15, 2880, "avax_usdc_1month.csv")

if __name__ == "__main__":
    main()
