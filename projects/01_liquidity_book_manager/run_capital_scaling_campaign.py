import os
import numpy as np
import pandas as pd
from src.backtest import BinLiquidityBacktester

def run_capital_scaling_analysis():
    bin_step_bp = 15.0
    base_fee_rate = 0.0009
    drift = 0.15
    pool_bin_tvl = 100000.0
    gas_fee_real = 0.3500
    
    backtester = BinLiquidityBacktester()
    
    # 1. Cargar dataset mensual
    csv_1m_path = os.path.join(os.path.dirname(__file__), "avax_usdc_1month_1m.csv")
    if not os.path.exists(csv_1m_path):
        print("[ERROR] No se encontró el dataset avax_usdc_1month_1m.csv.")
        return
        
    df_1m = pd.read_csv(csv_1m_path)
    dt_step_1m = 1.0 / 525600.0
    expected_vol_min_1m = df_1m["volume_real"].mean()
    
    capital_sizes = [50.0, 100.0, 200.0, 1000.0, 2000.0]
    
    # Medidas a evaluar:
    # - Medida 2: Rebalanceo Optimizado (Slippage 0.03%)
    # - Medida 3: Aporte Asimétrico (Slippage 0.00%)
    mitigation_measures = [
        ("Medida 2: Rebalanceo Optimizado (Slippage 0.03%)", 0.0003),
        ("Medida 3: Aporte Asimétrico (Slippage 0.00%)", 0.0000)
    ]
    
    print("\n" + "=" * 142)
    print(" CAMPAÑA 1 MES (VELAS 1m): ANÁLISIS DE ESCALABILIDAD DE CAPITAL INICIAL Y ROI NETO ")
    print("=" * 142)
    print("  Cap. Inicial ($) | Medida Slippage | Rebal. | Fees ($) | Gas ($) | Slippage ($) | Pool Final ($) | Val. Final ($) | Net ROI (%)")
    print("-" * 142)
    
    for cap in capital_sizes:
        for label, slip_rate in mitigation_measures:
            res = backtester.run_backtest(
                prices_real=df_1m["price"].values,
                vols_real=df_1m["volatility_true"].values,
                volume_real=df_1m["volume_real"].values,
                times_real=np.arange(len(df_1m)) * dt_step_1m,
                capital=cap,
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
            
            stats = res["stats"]["opt_constant"]
            net_profit = stats["absolute_portfolio_value"] - cap
            roi = (net_profit / cap) * 100.0
            
            print(
                f"  - ${cap:13.2f} | "
                f"{label.split(':')[0]:15} | "
                f"{stats['mean_rebalances']:5.0f} | "
                f"${stats['mean_fees_earned']:8.2f} | "
                f"${stats['mean_gas_spent']:7.2f} | "
                f"${stats['mean_slippage']:12.2f} | "
                f"${stats['final_assets']:14.2f} | "
                f"${stats['absolute_portfolio_value']:14.2f} | "
                f"{roi:+10.2f}%"
            )
        print("-" * 142)
        
    print("\n Nota: Un ROI de -100.00% indica que el colateral del pool fue absorbido en su totalidad por el gas fijo de $0.35.")

if __name__ == "__main__":
    run_capital_scaling_analysis()
