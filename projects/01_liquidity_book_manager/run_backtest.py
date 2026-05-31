import os
from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from src.backtest import BinLiquidityBacktester

def explain_avalanche_gas_fees(gas_used: int, gas_price_gwei: float, avax_usd_price: float) -> Tuple[float, str]:
    """
    Calcula matemáticamente el costo de gas en USD de una transacción real en Avalanche C-Chain.
    """
    avax_cost = gas_used * gas_price_gwei * 1e-9
    usd_cost = avax_cost * avax_usd_price
    
    breakdown = (
        f"  - Gas Consumido por el Contrato (Joe): {gas_used:,} unidades\n"
        f"  - Tarifa de Gas (Base Fee + Tip): {gas_price_gwei:.2f} nAVAX (gwei)\n"
        f"  - Precio de Mercado de AVAX: ${avax_usd_price:.2f} USD\n"
        f"  - Costo Total en AVAX: {avax_cost:.6f} AVAX\n"
        f"  - Costo Equivalente en USD: ${usd_cost:.4f} USD"
    )
    return usd_cost, breakdown

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

def print_multi_period_table(
    period_title: str,
    period_stats: str,
    results: Dict[str, Any],
    capital: float,
    fee_rate: float,
    gas_fee: float
):
    """
    Imprime una tabla de reporte ASCII de alta fidelidad que desglosa las 15 estrategias.
    """
    print("\n" + "=" * 125)
    print(f" {period_title:^123} ")
    print(f" {period_stats:^123} ")
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

def run_backtesting_campaign():
    # 1. Configuración de Parámetros Reales de Mercado y Red
    bin_step_bp = 15.0      
    capital = 2000.0        
    base_fee_rate = 0.0009  
    drift = 0.15            
    pool_bin_tvl = 100000.0 
    
    # Gas real de Avalanche C-Chain calibrado a $0.3500 USD
    gas_used_joe = 300000   
    gas_price_avax = 33.3333333  
    avax_price_usd = 35.0   
    
    gas_fee_real, gas_breakdown = explain_avalanche_gas_fees(gas_used_joe, gas_price_avax, avax_price_usd)

    print("=========================================================================")
    print("              CÁLCULO CIENTÍFICO DE GAS FEE EN AVALANCHE C-CHAIN         ")
    print("=========================================================================")
    print(gas_breakdown)
    print("=========================================================================\n")

    # 2. Cargar Dataset Histórico Empírico Real de GeckoTerminal (6,000 minutos)
    csv_path = os.path.join(os.path.dirname(__file__), "avax_usdc_historical.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró el archivo de precios históricos en: {csv_path}")
        
    df_hist = pd.read_csv(csv_path)
    print(f"Cargando dataset histórico empírico: {csv_path}")
    print(f"  - Registros cargados: {len(df_hist):,} minutos (aprox. {len(df_hist)/1440:.2f} días de trading real)\n")

    period_length = 2000
    
    # Segmentar en 3 Periodos
    df_p1 = df_hist.iloc[0:period_length].copy().reset_index(drop=True)
    df_p2 = df_hist.iloc[period_length:2*period_length].copy().reset_index(drop=True)
    df_p3 = df_hist.iloc[2*period_length:3*period_length].copy().reset_index(drop=True)
    
    backtester = BinLiquidityBacktester()
    dt_min = 1.0 / 525600.0

    periods = [
        ("PERIODO 1: TENDENCIA BAJISTA MODERADA Y ALTO VOLUMEN", df_p1),
        ("PERIODO 2: CAÍDA ACELERADA Y PÁNICO EXTREMO (CISNE NEGRO)", df_p2),
        ("PERIODO 3: ESTABILIZACIÓN Y CONSOLIDACIÓN (QUIETUD Y VOLUMEN MODERADO)", df_p3)
    ]

    for idx, (title, df_p) in enumerate(periods):
        prices = df_p["price"].values
        vols = df_p["volatility_true"].values
        volume = df_p["volume_real"].values
        n_steps = len(df_p) - 1
        
        times = np.arange(n_steps + 1) * dt_min
        expected_vol_min = volume.mean()
        
        price_change = ((prices[-1] / prices[0]) - 1.0) * 100
        total_vol = volume.sum()
        
        stats_str = (
            f"Duración: {n_steps/60:.1f} horas | Precio: ${prices[0]:.2f} -> ${prices[-1]:.2f} ({price_change:+.2f}%) | "
            f"Volumen Pool: ${total_vol:,.2f} USD (Avg: ${expected_vol_min:,.2f}/min)"
        )
        
        # Ejecutar el backtest bajo el modelo realista en cadena (LFJ)
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
            dt_step=dt_min
        )
        
        # Imprimir la tabla para este periodo
        print_multi_period_table(title, stats_str, results, capital, base_fee_rate, gas_fee_real)
        
        # Guardar gráfico de rendimiento para el Periodo 2 (Cisne Negro)
        if idx == 1:
            output_path = os.path.join(os.path.dirname(__file__), "visual_backtest_performance.png")
            save_performance_plot(
                times=times,
                results=results,
                output_path=output_path,
                title="Evolución de Rentabilidad sobre HODL - Periodo 2 (Caída y Pánico con Cortafuegos)"
            )
            print(f"¡Gráfico de rendimiento de las 15 estrategias guardado en: {output_path}!\n")

    # --- 3. RUN CONSOLIDATED CONTINUOUS BACKTEST OVER THE FULL 6,000 MINUTES ---
    prices_full = df_hist["price"].values
    vols_full = df_hist["volatility_true"].values
    volume_full = df_hist["volume_real"].values
    n_steps_full = len(df_hist) - 1
    times_full = np.arange(n_steps_full + 1) * dt_min
    expected_vol_min_full = volume_full.mean()
    
    price_change_full = ((prices_full[-1] / prices_full[0]) - 1.0) * 100
    total_vol_full = volume_full.sum()
    
    stats_str_full = (
        f"Duración Continua: {n_steps_full/1440:.2f} días ({n_steps_full/60:.1f} horas) | "
        f"Precio: ${prices_full[0]:.2f} -> ${prices_full[-1]:.2f} ({price_change_full:+.2f}%) | "
        f"Volumen Pool: ${total_vol_full:,.2f} USD (Avg: ${expected_vol_min_full:,.2f}/min)"
    )
    
    print("\n" + "=" * 125)
    print("                  EJECUTANDO BACKTEST COMPLETO CONSOLIDADO (CONTINUO DE 6,000 MINUTOS)                       ")
    print("=============================================================================================================")
    results_full = backtester.run_backtest(
        prices_real=prices_full,
        vols_real=vols_full,
        volume_real=volume_full,
        times_real=times_full,
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
        expected_volume_per_minute=expected_vol_min_full,
        fee_model="realistic",
        dt_step=dt_min
    )
    
    print_multi_period_table(
        "TABLA COMPLETA CONSOLIDADA (ACUMULADO TOTAL CONTÍNUO DE 6,000 MINUTOS)",
        stats_str_full,
        results_full,
        capital,
        base_fee_rate,
        gas_fee_real
    )

    # --- 4. EJECUTAR CAMPAÑA 1 SEMANA (VELAS DE 5 MINUTOS) ---
    csv_path_1w = os.path.join(os.path.dirname(__file__), "avax_usdc_1week.csv")
    if os.path.exists(csv_path_1w):
        df_1w = pd.read_csv(csv_path_1w)
        prices_1w = df_1w["price"].values
        vols_1w = df_1w["volatility_true"].values
        volume_1w = df_1w["volume_real"].values
        n_steps_1w = len(df_1w) - 1
        
        dt_step_1w = 5.0 / 525600.0  # Velas de 5 minutos
        times_1w = np.arange(n_steps_1w + 1) * dt_step_1w
        expected_vol_min_1w = volume_1w.mean() / 5.0
        
        price_change_1w = ((prices_1w[-1] / prices_1w[0]) - 1.0) * 100
        total_vol_1w = volume_1w.sum()
        
        stats_str_1w = (
            f"Duración: {n_steps_1w * 5 / 1440:.2f} días ({n_steps_1w * 5 / 60:.1f} horas) | "
            f"Precio: ${prices_1w[0]:.2f} -> ${prices_1w[-1]:.2f} ({price_change_1w:+.2f}%) | "
            f"Volumen Pool: ${total_vol_1w:,.2f} USD (Avg: ${expected_vol_min_1w:,.2f}/min)"
        )
        
        print("\n" + "=" * 125)
        print("                        EJECUTANDO CAMPAÑA DE BACKTEST COMPLETO: 1 SEMANA                                   ")
        print("=============================================================================================================")
        
        results_1w = backtester.run_backtest(
            prices_real=prices_1w,
            vols_real=vols_1w,
            volume_real=volume_1w,
            times_real=times_1w,
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
            expected_volume_per_minute=expected_vol_min_1w,
            fee_model="realistic",
            dt_step=dt_step_1w
        )
        
        print_multi_period_table(
            "CAMPAÑA COMPLETA: 1 SEMANA (PASOS DE 5 MINUTOS - EMPÍRICO REAL)",
            stats_str_1w,
            results_1w,
            capital,
            base_fee_rate,
            gas_fee_real
        )
        
        output_path_1w = os.path.join(os.path.dirname(__file__), "visual_backtest_performance_1week.png")
        save_performance_plot(
            times=times_1w,
            results=results_1w,
            output_path=output_path_1w,
            title="Evolución de Rentabilidad sobre HODL - Campaña 1 Semana (Velocidad de 5 minutos)"
        )
        print(f"¡Gráfico de rendimiento de la campaña de 1 semana guardado en: {output_path_1w}!\n")
    else:
        print(f"Advertencia: No se encontró el dataset de 1 semana en: {csv_path_1w}")

    # --- 5. EJECUTAR CAMPAÑA 1 MES (VELAS DE 15 MINUTOS) ---
    csv_path_1m = os.path.join(os.path.dirname(__file__), "avax_usdc_1month.csv")
    if os.path.exists(csv_path_1m):
        df_1m = pd.read_csv(csv_path_1m)
        prices_1m = df_1m["price"].values
        vols_1m = df_1m["volatility_true"].values
        volume_1m = df_1m["volume_real"].values
        n_steps_1m = len(df_1m) - 1
        
        dt_step_1m = 15.0 / 525600.0  # Velas de 15 minutos
        times_1m = np.arange(n_steps_1m + 1) * dt_step_1m
        expected_vol_min_1m = volume_1m.mean() / 15.0
        
        price_change_1m = ((prices_1m[-1] / prices_1m[0]) - 1.0) * 100
        total_vol_1m = volume_1m.sum()
        
        stats_str_1m = (
            f"Duración: {n_steps_1m * 15 / 1440:.2f} días ({n_steps_1m * 15 / 60:.1f} horas) | "
            f"Precio: ${prices_1m[0]:.2f} -> ${prices_1m[-1]:.2f} ({price_change_1m:+.2f}%) | "
            f"Volumen Pool: ${total_vol_1m:,.2f} USD (Avg: ${expected_vol_min_1m:,.2f}/min)"
        )
        
        print("\n" + "=" * 125)
        print("                        EJECUTANDO CAMPAÑA DE BACKTEST COMPLETO: 1 MES                                      ")
        print("=============================================================================================================")
        
        results_1m = backtester.run_backtest(
            prices_real=prices_1m,
            vols_real=vols_1m,
            volume_real=volume_1m,
            times_real=times_1m,
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
            expected_volume_per_minute=expected_vol_min_1m,
            fee_model="realistic",
            dt_step=dt_step_1m
        )
        
        print_multi_period_table(
            "CAMPAÑA COMPLETA: 1 MES (PASOS DE 15 MINUTOS - EMPÍRICO REAL)",
            stats_str_1m,
            results_1m,
            capital,
            base_fee_rate,
            gas_fee_real
        )
        
        output_path_1m = os.path.join(os.path.dirname(__file__), "visual_backtest_performance_1month.png")
        save_performance_plot(
            times=times_1m,
            results=results_1m,
            output_path=output_path_1m,
            title="Evolución de Rentabilidad sobre HODL - Campaña 1 Mes (Velocidad de 15 minutos)"
        )
        print(f"¡Gráfico de rendimiento de la campaña de 1 mes guardado en: {output_path_1m}!\n")
    else:
        print(f"Advertencia: No se encontró el dataset de 1 mes en: {csv_path_1m}")

if __name__ == "__main__":
    run_backtesting_campaign()
