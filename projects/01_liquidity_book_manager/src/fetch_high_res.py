import os
import time
import requests
import pandas as pd
import numpy as np

def fetch_high_res_data(name: str, aggregate: int, total_candles: int, filename: str, sleep_time: float = 2.1):
    print("\n" + "=" * 80)
    print(f" DESCARGANDO DATASET DE ALTA RESOLUCIÓN: {name} ")
    print(f" Velas de {aggregate} min | Total a descargar: {total_candles:,} velas")
    print("=" * 80)
    
    network = "avax"
    pool_address = "0xf01449c0ba930b6e2caca3def3ccbd7a3e589534"
    base_url = f"https://api.geckoterminal.com/api/v2/networks/{network}/pools/{pool_address}/ohlcv/minute"
    headers = {"Accept": "application/json;version=20230302"}
    
    all_candles = []
    before_timestamp = None
    
    request_count = 0
    while len(all_candles) < total_candles:
        params = {
            "aggregate": aggregate,
            "limit": 1000
        }
        if before_timestamp:
            params["before_timestamp"] = before_timestamp
            
        try:
            request_count += 1
            print(f"  [Petición {request_count}] Enviando solicitud a GeckoTerminal...")
            response = requests.get(base_url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 429:
                print("  [WARN] Rate limit (429) alcanzado. Esperando 30 segundos...")
                time.sleep(30.0)
                continue
                
            if response.status_code != 200:
                print(f"  [ERROR] Status {response.status_code} de la API.")
                break
                
            data = response.json()
            ohlcv_list = data.get("data", {}).get("attributes", {}).get("ohlcv_list", [])
            if not ohlcv_list:
                print("  [INFO] No se encontraron más velas.")
                break
                
            all_candles.extend(ohlcv_list)
            before_timestamp = ohlcv_list[-1][0]
            
            print(f"  -> Descargadas {len(all_candles):,} / {total_candles:,} velas...")
            
            # Espaciado regular para respetar el límite de 30 peticiones por minuto (2 segundos por petición es ideal)
            time.sleep(sleep_time)
            
        except Exception as e:
            print(f"  [ERROR] De red o parsing: {e}")
            print("  Esperando 10 segundos antes de reintentar...")
            time.sleep(10.0)
            
    all_candles = all_candles[:total_candles]
    all_candles.reverse()
    
    if not all_candles:
        print("  [ERROR] No se descargaron datos.")
        return
        
    timestamps = [pd.to_datetime(x[0], unit='s') for x in all_candles]
    prices = [float(x[4]) for x in all_candles]
    volumes = [float(x[5]) for x in all_candles]
    
    # Calcular la Volatilidad Realizada Móvil
    log_prices = np.log(prices)
    log_returns = np.diff(log_prices)
    
    dt_step = aggregate / 525600.0
    vols = np.zeros(len(prices))
    vols[0] = 0.65
    
    # Ventana móvil de 30 velas para inicializar
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
    
    price_change = ((prices[-1] / prices[0]) - 1.0) * 100
    total_volume_usd = df["volume_real"].sum()
    
    print("-" * 80)
    print(f"  - Rango Temporal: {timestamps[0]} a {timestamps[-1]}")
    print(f"  - Registros Guardados: {len(df):,} velas de {aggregate}m")
    print(f"  - Retorno Neto Real: {price_change:+.2f}%")
    print(f"  - Volumen Total de Trading: ${total_volume_usd:,.2f} USD")
    print(f"¡Dataset guardado en: {output_path}!\n")

def main():
    # 1. Dataset de 1 semana a 1 minuto: 7 días = 10,080 velas.
    fetch_high_res_data("1 SEMANA (1-min aggregate)", 1, 10080, "avax_usdc_1week_1m.csv", sleep_time=2.1)
    
    # 2. Dataset de 1 mes a 1 minuto: 30 días = 43,200 velas.
    # Usamos sleep_time=2.1 para garantizar no violar el límite de 30 requests/min (43 peticiones en total)
    fetch_high_res_data("1 MES (1-min aggregate)", 1, 43200, "avax_usdc_1month_1m.csv", sleep_time=2.2)

if __name__ == "__main__":
    main()
