import os
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from src.backtest import BinLiquidityBacktester

def run_slippage_comparison():
    bin_step_bp = 15.0      
    capital = 2000.0        
    base_fee_rate = 0.0009  
    drift = 0.15            
    pool_bin_tvl = 100000.0 
    gas_fee_real = 0.3500  # Gas real en Avalanche C-Chain
    
    backtester = BinLiquidityBacktester()
    
    # 1. Cargar datasets de 1m reales
    csv_1w_path = os.path.join(os.path.dirname(__file__), "avax_usdc_1week_1m.csv")
    csv_1m_path = os.path.join(os.path.dirname(__file__), "avax_usdc_1month_1m.csv")
    
    if not os.path.exists(csv_1w_path) or not os.path.exists(csv_1m_path):
        print("[ERROR] No se encontraron los datasets de alta resolución de 1m.")
        return
        
    df_1w = pd.read_csv(csv_1w_path)
    df_1m = pd.read_csv(csv_1m_path)
    
    # 2. Definir las 3 Medidas de Deslizamiento (Slippage)
    slippage_configurations = [
        ("Medida 1: Rebalanceo Naive (Slippage 0.10%)", 0.0010),
        ("Medida 2: Rebalanceo Optimizado (Slippage 0.03%)", 0.0003),
        ("Medida 3: Aporte Asimétrico (Slippage 0.00%)", 0.0000)
    ]
    
    selected_strategies = ["static", "dynamic_1sig", "opt_constant", "opt_garch", "opt_heston"]
    mapping = {
        "static": "Estática Fija (12 bins)",
        "dynamic_1sig": "Dinámica 1-Sigma",
        "opt_constant": "Optimizada Constante",
        "opt_garch": "Optimizada GARCH(1,1)",
        "opt_heston": "Optimizada Heston"
    }
    
    # --- CAMPAÑA 1 SEMANA (10,080 minutos, velas 1m) ---
    p_init_1w = df_1w["price"].values[0]
    p_final_1w = df_1w["price"].values[-1]
    hodl_1w = capital * 0.5 + capital * 0.5 * (p_final_1w / p_init_1w)
    
    print("\n" + "=" * 120)
    print(f" CAMPAÑA 1 SEMANA (VELAS 1m): EVALUACIÓN DE LAS 3 MEDIDAS DE MITIGACIÓN DE SLIPPAGE ")
    print(f" Duración: 7.00 días | Precio: ${p_init_1w:.2f} -> ${p_final_1w:.2f} ({((p_final_1w/p_init_1w)-1)*100:+.2f}%)")
    print(f" VALOR DE SOLO HODL: ${hodl_1w:.2f} USD")
    print("=" * 120)
    print("  Estrategia / Estimador Vol.      | Conf. Slippage | Rebal. | Fees ($) | Gas ($) | Slippage ($) | Valor Final ($)")
    print("-" * 120)
    
    dt_step_1w = 1.0 / 525600.0
    expected_vol_min_1w = df_1w["volume_real"].mean()
    
    # Ejecutar backtest una sola vez por cada tasa de deslizamiento
    results_1w = {}
    for config_name, slip_rate in slippage_configurations:
        res = backtester.run_backtest(
            prices_real=df_1w["price"].values,
            vols_real=df_1w["volatility_true"].values,
            volume_real=df_1w["volume_real"].values,
            times_real=np.arange(len(df_1w)) * dt_step_1w,
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
            dt_step=dt_step_1w,
            slippage_rate=slip_rate
        )
        results_1w[slip_rate] = res["stats"]

    for k in selected_strategies:
        for config_name, slip_rate in slippage_configurations:
            stats = results_1w[slip_rate][k]
            print(
                f"  - {mapping[k]:30} | "
                f"{config_name.split(':')[0]:14} | "
                f"{stats['mean_rebalances']:5.0f} | "
                f"${stats['mean_fees_earned']:8.2f} | "
                f"${stats['mean_gas_spent']:7.2f} | "
                f"${stats['mean_slippage']:12.2f} | "
                f"${stats['absolute_portfolio_value']:15.2f}"
            )
        print("-" * 120)
        
    # --- CAMPAÑA 1 MES (43,200 minutos, velas 1m) ---
    p_init_1m = df_1m["price"].values[0]
    p_final_1m = df_1m["price"].values[-1]
    hodl_1m = capital * 0.5 + capital * 0.5 * (p_final_1m / p_init_1m)
    
    print("\n" + "=" * 120)
    print(f" CAMPAÑA 1 MES (VELAS 1m): EVALUACIÓN DE LAS 3 MEDIDAS DE MITIGACIÓN DE SLIPPAGE ")
    print(f" Duración: 30.00 días | Precio: ${p_init_1m:.2f} -> ${p_final_1m:.2f} ({((p_final_1m/p_init_1m)-1)*100:+.2f}%)")
    print(f" VALOR DE SOLO HODL: ${hodl_1m:.2f} USD")
    print("=" * 120)
    print("  Estrategia / Estimador Vol.      | Conf. Slippage | Rebal. | Fees ($) | Gas ($) | Slippage ($) | Valor Final ($)")
    print("-" * 120)
    
    dt_step_1m = 1.0 / 525600.0
    expected_vol_min_1m = df_1m["volume_real"].mean()
    
    # Ejecutar backtest una sola vez por cada tasa de deslizamiento
    results_1m = {}
    for config_name, slip_rate in slippage_configurations:
        res = backtester.run_backtest(
            prices_real=df_1m["price"].values,
            vols_real=df_1m["volatility_true"].values,
            volume_real=df_1m["volume_real"].values,
            times_real=np.arange(len(df_1m)) * dt_step_1m,
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
            dt_step=dt_step_1m,
            slippage_rate=slip_rate
        )
        results_1m[slip_rate] = res["stats"]

    for k in selected_strategies:
        for config_name, slip_rate in slippage_configurations:
            stats = results_1m[slip_rate][k]
            print(
                f"  - {mapping[k]:30} | "
                f"{config_name.split(':')[0]:14} | "
                f"{stats['mean_rebalances']:5.0f} | "
                f"${stats['mean_fees_earned']:8.2f} | "
                f"${stats['mean_gas_spent']:7.2f} | "
                f"${stats['mean_slippage']:12.2f} | "
                f"${stats['absolute_portfolio_value']:15.2f}"
            )
        print("-" * 120)

if __name__ == "__main__":
    run_slippage_comparison()
