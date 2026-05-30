import os
import time
import requests
import pandas as pd
import numpy as np

def fetch_real_avax_data():
    print("=========================================================================")
    print("      DESCARGA DE DATOS REALES ON-CHAIN DE WAVAX/USDC DE TRADER JOE (LFJ)  ")
    print("=========================================================================")
    
    network = "avax"
    pool_address = "0xf01449c0ba930b6e2caca3def3ccbd7a3e589534"
    base_url = f"https://api.geckoterminal.com/api/v2/networks/{network}/pools/{pool_address}/ohlcv/minute"
    headers = {"Accept": "application/json;version=20230302"}
    
    # Queremos descargar 4,000 minutos de datos históricos reales (aprox. 2.7 días)
    total_minutes = 4000
    all_candles = []
    
    before_timestamp = None
    print(f"Descargando {total_minutes} minutos de precios y volumen del pool principal...")
    
    while len(all_candles) < total_minutes:
        params = {
            "aggregate": 1,
            "limit": 1000
        }
        if before_timestamp:
            params["before_timestamp"] = before_timestamp
            
        try:
            response = requests.get(base_url, headers=headers, params=params, timeout=12)
            if response.status_code != 200:
                print(f"Error en la API de GeckoTerminal (Status {response.status_code})")
                print(f"Detalle: {response.text}")
                break
                
            data = response.json()
            ohlcv_list = data.get("data", {}).get("attributes", {}).get("ohlcv_list", [])
            if not ohlcv_list:
                print("No se encontraron más velas.")
                break
                
            # Agregar las velas obtenidas
            all_candles.extend(ohlcv_list)
            
            # El filter before_timestamp es el timestamp del último elemento de la página (el más antiguo de ese bloque)
            before_timestamp = ohlcv_list[-1][0]
            
            print(f"  -> Descargadas {len(all_candles)} / {total_minutes} velas...")
            
            # Pausa de seguridad para evitar límites de tasa
            time.sleep(1.0)
            
        except Exception as e:
            print(f"Error de red: {e}")
            break
            
    # Recortar al tamaño deseado
    all_candles = all_candles[:total_minutes]
    
    # GeckoTerminal retorna en orden descendente (más nuevo primero). Invertimos el orden para tener secuencia cronológica.
    all_candles.reverse()
    
    # Formato de GeckoTerminal ohlcv:
    # [0: Timestamp, 1: Open, 2: High, 3: Low, 4: Close, 5: Volume]
    timestamps = [pd.to_datetime(x[0], unit='s') for x in all_candles]
    prices = [float(x[4]) for x in all_candles]
    volumes = [float(x[5]) for x in all_candles]
    
    # Calcular la Volatilidad Realizada Real para cada punto
    # Usaremos una ventana móvil de 30 minutos de log-retornos para estimar la volatilidad anualizada
    log_prices = np.log(prices)
    log_returns = np.diff(log_prices)
    
    # dt para 1 minuto en fracción de año
    dt = 1.0 / (365.0 * 24.0 * 60.0)
    
    vols = np.zeros(len(prices))
    vols[0] = 0.65  # Volatilidad base por defecto (65%)
    
    for t in range(1, len(prices)):
        window = max(0, t - 30)
        # Necesitamos al menos 5 retornos para una desviación estándar muestral representativa
        if t - window >= 5:
            std_ret = np.std(log_returns[window:t], ddof=1)
            vols[t] = np.clip(std_ret / np.sqrt(dt), 0.10, 2.50)
        else:
            vols[t] = 0.65
            
    # Crear DataFrame
    df = pd.DataFrame({
        "timestamp": timestamps,
        "price": prices,
        "volatility_true": vols,
        "volume_real": volumes
    })
    
    # Guardar en el directorio del proyecto
    output_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(output_dir, "avax_usdc_historical.csv")
    df.to_csv(output_path, index=False)
    
    # Calcular estadísticas del pool real
    max_price = df["price"].max()
    min_price = df["price"].min()
    price_change = ((prices[-1] / prices[0]) - 1.0) * 100
    realized_vol_ann = np.std(log_returns, ddof=1) / np.sqrt(dt)
    total_volume_usd = df["volume_real"].sum()
    avg_minute_volume = df["volume_real"].mean()
    
    print("\n=========================================================================")
    print("                ESTADÍSTICAS DEL MERCADO REAL TRADER JOE                 ")
    print("=========================================================================")
    print(f"  - Dirección del Pool: {pool_address}")
    print(f"  - Rango Temporal: {timestamps[0]} a {timestamps[-1]}")
    print(f"  - Registros Totales: {len(df):,} minutos")
    print(f"  - Precio Inicial AVAX: ${prices[0]:.4f} USD | Precio Final: ${prices[-1]:.4f} USD")
    print(f"  - Precio Máximo: ${max_price:.4f} USD | Precio Mínimo: ${min_price:.4f} USD")
    print(f"  - Retorno Neto Real: {price_change:.2f}%")
    print(f"  - Volatilidad Anualizada Realizada: {realized_vol_ann*100:.2f}%")
    print(f"  - Volumen Total de Trading: ${total_volume_usd:,.2f} USD")
    print(f"  - Volumen Promedio por Minuto: ${avg_minute_volume:,.2f} USD")
    print("=========================================================================\n")
    print(f"¡Precios y volúmenes históricos REALES guardados con éxito en: {output_path}!")

if __name__ == "__main__":
    fetch_real_avax_data()
