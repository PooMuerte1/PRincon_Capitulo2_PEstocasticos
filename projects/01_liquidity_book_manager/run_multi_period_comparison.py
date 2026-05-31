import os
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from src.backtest import BinLiquidityBacktester

def explain_avalanche_gas_fees(gas_used: int, gas_price_gwei: float, avax_usd_price: float) -> Tuple[float, str]:
    """
    Calcula el costo de gas en USD para Avalanche C-Chain.
    """
    avax_cost = gas_used * gas_price_gwei * 1e-9
    usd_cost = avax_cost * avax_usd_price
    return usd_cost, f"Gas en USD: ${usd_cost:.4f}"

def downsample_dataframe(df: pd.DataFrame, k: int) -> pd.DataFrame:
    """
    Agrupa cada k registros de alta frecuencia (1m) en una sola vela de resolución más baja (k minutos).
    """
    records = []
    n = len(df)
    for i in range(0, n, k):
        chunk = df.iloc[i : min(i + k, n)]
        if len(chunk) == 0:
            continue
        
        price_close = chunk["price"].values[-1]
        vol_mean = chunk["volatility_true"].mean()
        vol_sum = chunk["volume_real"].sum()
        timestamp = chunk["timestamp"].values[0]
        
        records.append({
            "timestamp": timestamp,
            "price": price_close,
            "volatility_true": vol_mean,
            "volume_real": vol_sum
        })
        
    return pd.DataFrame(records)

def print_multi_period_table(
    period_title: str,
    period_stats: str,
    results: Dict[str, Any],
    capital: float,
    hodl_value: float
):
    """
    Imprime una tabla de reporte ASCII de alta fidelidad que desglosa las 15 estrategias.
    """
    print("\n" + "=" * 125)
    print(f" {period_title:^123} ")
    print(f" {period_stats:^123} ")
    print(f" VALOR DE SOLO HODL (50/50 AVAX/USDC): ${hodl_value:.2f} USD | Capital Inicial: ${capital:.2f} USD ")
    print("-" * 125)
    print("  Estrategia / Estimador Vol.      | Ret. HODL ($) | Fees ($) | Gas ($) | Deval. Inventario ($) | Valor Final ($) | Rebal.")
    print("-" * 125)
    
    mapping = {
        "static": "Estática (Manual Fijo 12 bins) ",
        "dynamic_1sig": "Dinámica 1-Sigma (Rolling Vol) ",
        "dynamic_1sig_cb": "Dinámica 1-Sigma + Cortafuegos ",
        "dynamic_2sig": "Dinámica 2-Sigma (Rolling Vol) ",
        "dynamic_2sig_cb": "Dinámica 2-Sigma + Cortafuegos ",
        "dynamic_3sig": "Dinámica 3-Sigma (Rolling Vol) ",
        "dynamic_3sig_cb": "Dinámica 3-Sigma + Cortafuegos ",
        "opt_constant": "Optimizada (Vol. Constante)    ",
        "opt_constant_cb": "Optimizada Constante + Cortafue",
        "opt_rolling": "Optimizada (Rolling Vol 30m)  ",
        "opt_rolling_cb": "Optimizada Rolling + Cortafuego",
        "opt_garch": "Optimizada (GARCH 1,1 condic)  ",
        "opt_garch_cb": "Optimizada GARCH + Cortafuegos ",
        "opt_heston": "Optimizada (Filtro Heston stoch)",
        "opt_heston_cb": "Optimizada Heston + Cortafuegos"
    }

    for k in [
        "static", 
        "dynamic_1sig", "dynamic_1sig_cb",
        "dynamic_2sig", "dynamic_2sig_cb",
        "dynamic_3sig", "dynamic_3sig_cb",
        "opt_constant", "opt_constant_cb",
        "opt_rolling", "opt_rolling_cb",
        "opt_garch", "opt_garch_cb",
        "opt_heston", "opt_heston_cb"
    ]:
        stats = results["stats"][k]
        
        net_ret = stats["mean_net_return"] 
        gas_spent = stats["mean_gas_spent"]
        fees_earned = stats["mean_fees_earned"]
        rebal_count = stats["mean_rebalances"]
        
        final_val = stats["absolute_portfolio_value"] 
        deval = stats["inventory_devaluation"] 
        
        print(
            f"  - {mapping[k]:32} | "
            f"${net_ret:12.2f} | "
            f"${fees_earned:8.2f} | "
            f"${gas_spent:7.2f} | "
            f"${deval:21.2f} | "
            f"${final_val:15.2f} | "
            f"{rebal_count:5.0f}"
        )
    print("=" * 125 + "\n")

def save_performance_plot(times: np.ndarray, results: Dict[str, Any], output_path: str, title: str):
    """
    Grafica la evolución de rentabilidad sobre HODL para las 15 estrategias en paralelo.
    """
    plt.figure(figsize=(14, 8))
    
    total_days = (times[-1] - times[0]) * 365.0
    if total_days <= 8.0:
        time_axis = times * 365.0 * 24.0
        time_label = "Tiempo Transcurrido (Horas)"
    else:
        time_axis = times * 365.0
        time_label = "Tiempo Transcurrido (Días)"
        
    colors = {
        "static": "red",
        "dynamic_1sig": "orange",
        "dynamic_1sig_cb": "orange",
        "dynamic_2sig": "darkorange",
        "dynamic_2sig_cb": "darkorange",
        "dynamic_3sig": "gold",
        "dynamic_3sig_cb": "gold",
        "opt_constant": "gray",
        "opt_constant_cb": "gray",
        "opt_rolling": "cyan",
        "opt_rolling_cb": "cyan",
        "opt_garch": "green",
        "opt_garch_cb": "green",
        "opt_heston": "purple",
        "opt_heston_cb": "purple"
    }
    
    labels = {
        "static": "Estática (Manual Fijo)",
        "dynamic_1sig": "Dinámica 1-Sigma",
        "dynamic_1sig_cb": "Dinámica 1-Sigma + CB",
        "dynamic_2sig": "Dinámica 2-Sigma",
        "dynamic_2sig_cb": "Dinámica 2-Sigma + CB",
        "dynamic_3sig": "Dinámica 3-Sigma",
        "dynamic_3sig_cb": "Dinámica 3-Sigma + CB",
        "opt_constant": "Optimizada (Vol. Constante)",
        "opt_constant_cb": "Optimizada Constante + CB",
        "opt_rolling": "Optimizada (Rolling Vol)",
        "opt_rolling_cb": "Optimizada Rolling + CB",
        "opt_garch": "Optimizada (GARCH Vol)",
        "opt_garch_cb": "Optimizada GARCH + CB",
        "opt_heston": "Optimizada (Heston Filter)",
        "opt_heston_cb": "Optimizada Heston + CB"
    }
    
    for k in colors:
        linewidth = 2.2 if "opt_" in k else 1.0
        linestyle = "--" if k.endswith("_cb") else "-"
        alpha_val = 1.0 if k.endswith("_cb") or k == "static" else 0.5
        plt.plot(time_axis, results["history_path0"][k], color=colors[k], linewidth=linewidth, linestyle=linestyle, alpha=alpha_val, label=labels[k])
        
    plt.axhline(y=0, color='black', linestyle=':', label="Punto de Empate ($0 USD)")
    plt.title(title, fontsize=12)
    plt.xlabel(time_label, fontsize=10)
    plt.ylabel("Rentabilidad sobre HODL (USD)", fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=8, loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

def run_campaign_on_dataset(csv_filename: str, label: str):
    csv_path = os.path.join(os.path.dirname(__file__), csv_filename)
    if not os.path.exists(csv_path):
        print(f"\n[WARN] No se encontró el dataset en: {csv_path}. Omitiendo campaña.")
        return
        
    print(f"\n=========================================================================")
    print(f"   EJECUTANDO CAMPAÑA MULTI-VELAS PARA PERIODO: {label.upper()}   ")
    print(f"=========================================================================")
    
    df_base = pd.read_csv(csv_path)
    
    bin_step_bp = 15.0      
    capital = 2000.0        
    base_fee_rate = 0.0009  
    drift = 0.15            
    pool_bin_tvl = 100000.0 
    
    # Gas real de Avalanche C-Chain calibrado a $0.3500 USD
    gas_fee_real = 0.3500
    backtester = BinLiquidityBacktester()
    
    # Calcular HODL
    p_initial = df_base["price"].values[0]
    p_final = df_base["price"].values[-1]
    hodl_value = capital * 0.5 + capital * 0.5 * (p_final / p_initial)
    
    resolutions = [
        ("Velas de 1 Minuto", 1, 1.0 / 525600.0),
        ("Velas de 5 Minutos", 5, 5.0 / 525600.0),
        ("Velas de 15 Minutos", 15, 15.0 / 525600.0)
    ]
    
    for title, k, dt_step in resolutions:
        if k == 1:
            df_res = df_base.copy()
        else:
            df_res = downsample_dataframe(df_base, k)
            
        prices = df_res["price"].values
        vols = df_res["volatility_true"].values
        volume = df_res["volume_real"].values
        n_steps = len(df_res) - 1
        
        times = np.arange(n_steps + 1) * dt_step
        expected_vol_min = volume.mean() / k
        
        price_change = ((prices[-1] / prices[0]) - 1.0) * 100
        total_vol = volume.sum()
        
        stats_str = (
            f"Resolución: {title} | Velas reales: {len(df_res):,} | "
            f"Precio: ${prices[0]:.2f} -> ${prices[-1]:.2f} ({price_change:+.2f}%) | "
            f"Volumen Pool: ${total_vol:,.2f} USD"
        )
        
        results = backtester.run_backtest(
            prices_real=prices,
            vols_real=vols,
            volume_real=volume,
            times_real=times,
            capital=capital,
            base_fee_rate=base_fee_rate,
            gas_fee=gas_fee_real,
            drift=drift,
            bin_step_bp=bin_step_bp,
            static_width=12,
            horizon_hours=4.0,
            vol_threshold=1.20,
            vol_window=30,
            pool_bin_tvl=pool_bin_tvl,
            expected_volume_per_minute=expected_vol_min,
            fee_model="realistic",
            dt_step=dt_step
        )
        
        print_multi_period_table(
            f"CAMPAÑA {label.upper()} ({title.upper()})",
            stats_str,
            results,
            capital,
            hodl_value
        )
        
        output_filename = f"visual_comparison_{label.lower()}_{k}m.png"
        output_path = os.path.join(os.path.dirname(__file__), output_filename)
        save_performance_plot(
            times=times,
            results=results,
            output_path=output_path,
            title=f"Rendimiento de las Estrategias ({label}) - Velas de {k} Minutos"
        )
        print(f"¡Gráfico guardado en: {output_path}!\n")

def main():
    # A. Ejecutar Campaña de 1 Semana
    run_campaign_on_dataset("avax_usdc_1week_1m.csv", "1_semana")
    
    # B. Ejecutar Campaña de 1 Mes
    run_campaign_on_dataset("avax_usdc_1month_1m.csv", "1_mes")

if __name__ == "__main__":
    main()
