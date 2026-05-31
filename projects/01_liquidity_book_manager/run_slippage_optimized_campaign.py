import os
from typing import Dict, Any
import numpy as np
import pandas as pd
from src.backtest import BinLiquidityBacktester
from src.rebalancer_with_slippage import BinLiquidityRebalancerWithSlippage

class SlippageAwareBacktester(BinLiquidityBacktester):
    """
    Subclase del motor de backtesting que sobrescribe el optimizador de anchos
    para hacerlo sensible al deslizamiento de precios (Slippage-Aware).
    """
    def __init__(self, slippage_rate_opt: float = 0.0):
        super().__init__()
        self.rebalancer_with_slippage = BinLiquidityRebalancerWithSlippage()
        self.slippage_rate_opt = slippage_rate_opt

    def _precompute_optimal_widths(
        self,
        capital: float,
        base_fee_rate: float,
        gas_fee: float,
        drift: float,
        bin_step_bp: float,
        fee_model: str,
        expected_volume_per_minute: float,
        pool_bin_tvl: float
    ) -> Dict[int, int]:
        opt_cache = {}
        for vol_pct in range(10, 201):
            vol = vol_pct / 100.0
            s = bin_step_bp / 10000.0
            dt = (np.log(1.0 + s) / vol) ** 2
            drift_adjustment = (drift - 0.5 * (vol ** 2)) / vol
            p = 0.5 * (1.0 + drift_adjustment * np.sqrt(dt))
            
            # Optimizar ancho considerando el costo de gas y el deslizamiento (slippage_rate)
            opt = self.rebalancer_with_slippage.optimize_range(
                p=p,
                capital=capital,
                base_fee_rate=base_fee_rate,
                gas_fee=gas_fee,
                slippage_rate=self.slippage_rate_opt,
                min_width=2,
                max_width=120,  # Permitir mayor flexibilidad de anchos defensivos
                dt_years=dt,
                expected_volume_per_minute=expected_volume_per_minute,
                pool_bin_tvl=pool_bin_tvl,
                fee_model=fee_model
            )
            opt_cache[vol_pct] = opt["optimal_width"]
            
        return opt_cache

def run_slippage_optimized_comparison():
    bin_step_bp = 15.0
    capital = 2000.0
    base_fee_rate = 0.0009
    drift = 0.15
    pool_bin_tvl = 100000.0
    gas_fee_real = 0.3500
    
    # 1. Cargar dataset mensual de alta resolución
    csv_1m_path = os.path.join(os.path.dirname(__file__), "avax_usdc_1month_1m.csv")
    if not os.path.exists(csv_1m_path):
        print("[ERROR] No se encontró el dataset avax_usdc_1month_1m.csv.")
        return
        
    df_1m = pd.read_csv(csv_1m_path)
    dt_step_1m = 1.0 / 525600.0
    expected_vol_min_1m = df_1m["volume_real"].mean()
    
    # 2. Instanciar backtesters
    # A. Backtester Clásico (no ve el slippage de 1% al optimizar anchos, solo el gas)
    classic_backtester = BinLiquidityBacktester()
    
    # B. Backtester Sensible al Slippage (optimiza anchos considerando el 1% de slippage)
    slippage_rate_catastrophic = 0.0100  # 1.00%
    aware_backtester = SlippageAwareBacktester(slippage_rate_opt=slippage_rate_catastrophic)
    
    print("\n" + "=" * 125)
    print(" CAMPAÑA 1 MES (VELAS 1m): OPTIMIZACIÓN DE RANGOS SENSIBLE AL DESLIZAMIENTO CATASTRÓFICO DEL 1.00% ")
    print("=" * 125)
    
    # Evaluar las 3 estrategias optimizadas para ambos modelos
    strategies_to_test = ["opt_constant", "opt_garch", "opt_heston"]
    mapping = {
        "opt_constant": "Optimizada Constante",
        "opt_garch": "Optimizada GARCH(1,1)",
        "opt_heston": "Optimizada Heston"
    }
    
    print("  Modelo / Estrategia              | Rebal. | Fees ($) | Gas ($) | Slippage ($) | Pool Final ($) | Valor Final ($)")
    print("-" * 125)
    
    # A. Ejecutar Backtest Clásico con 1% de Deslizamiento
    classic_res = classic_backtester.run_backtest(
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
        slippage_rate=slippage_rate_catastrophic
    )
    
    for k in strategies_to_test:
        stats = classic_res["stats"][k]
        print(
            f"  - [CLÁSICO] {mapping[k]:21} | "
            f"{stats['mean_rebalances']:5.0f} | "
            f"${stats['mean_fees_earned']:8.2f} | "
            f"${stats['mean_gas_spent']:7.2f} | "
            f"${stats['mean_slippage']:12.2f} | "
            f"${stats['final_assets']:14.2f} | "
            f"${stats['absolute_portfolio_value']:15.2f}"
        )
    
    print("-" * 125)
    
    # B. Ejecutar Backtest Sensible al Slippage con 1% de Deslizamiento
    aware_res = aware_backtester.run_backtest(
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
        slippage_rate=slippage_rate_catastrophic
    )
    
    for k in strategies_to_test:
        stats = aware_res["stats"][k]
        print(
            f"  - [AWARE]   {mapping[k]:21} | "
            f"{stats['mean_rebalances']:5.0f} | "
            f"${stats['mean_fees_earned']:8.2f} | "
            f"${stats['mean_gas_spent']:7.2f} | "
            f"${stats['mean_slippage']:12.2f} | "
            f"${stats['final_assets']:14.2f} | "
            f"${stats['absolute_portfolio_value']:15.2f}"
        )
        
    print("=" * 125)
    
    # Mostrar la tabla de anchos de búsqueda óptimos del rebalancer clásico vs el sensible al slippage
    print("\n COMPARATIVA DE ANCHOS DE RANGO ÓPTIMOS (W*) PARA VOLATILIDADES DE MERCADO:")
    print("-" * 80)
    print("  Volatilidad (%) | Ancho Clásico (Solo Gas) | Ancho Sensible (Gas + 1.00% Slippage)")
    print("-" * 80)
    
    # Precalcular anchos directamente para mostrar la diferencia
    from src.rebalancer import BinLiquidityRebalancer
    rebalancer_classic = BinLiquidityRebalancer()
    rebalancer_aware = BinLiquidityRebalancerWithSlippage()
    
    vols_to_show = [0.20, 0.40, 0.60, 0.80, 1.00, 1.20, 1.50]
    for vol in vols_to_show:
        s = bin_step_bp / 10000.0
        dt = (np.log(1.0 + s) / vol) ** 2
        drift_adjustment = (drift - 0.5 * (vol ** 2)) / vol
        p = 0.5 * (1.0 + drift_adjustment * np.sqrt(dt))
        
        opt_c = rebalancer_classic.optimize_range(
            p=p, capital=capital, base_fee_rate=base_fee_rate, gas_fee=gas_fee_real,
            dt_years=dt, expected_volume_per_minute=expected_vol_min_1m,
            pool_bin_tvl=pool_bin_tvl, fee_model="realistic"
        )
        opt_a = rebalancer_aware.optimize_range(
            p=p, capital=capital, base_fee_rate=base_fee_rate, gas_fee=gas_fee_real,
            slippage_rate=slippage_rate_catastrophic,
            dt_years=dt, expected_volume_per_minute=expected_vol_min_1m,
            pool_bin_tvl=pool_bin_tvl, fee_model="realistic"
        )
        print(f"      {vol*100:5.0f}%     |          {opt_c['optimal_width']:3.0f} Bins        |                 {opt_a['optimal_width']:3.0f} Bins")
    print("-" * 80)

if __name__ == "__main__":
    run_slippage_optimized_comparison()
