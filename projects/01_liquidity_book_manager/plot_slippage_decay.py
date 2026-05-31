import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from src.backtest import BinLiquidityBacktester

def generate_slippage_plots():
    bin_step_bp = 15.0
    capital = 2000.0
    base_fee_rate = 0.0009
    drift = 0.15
    pool_bin_tvl = 100000.0
    gas_fee_real = 0.3500
    
    backtester = BinLiquidityBacktester()
    
    # 1. Cargar datasets de alta resolución
    csv_1w_path = os.path.join(os.path.dirname(__file__), "avax_usdc_1week_1m.csv")
    csv_1m_path = os.path.join(os.path.dirname(__file__), "avax_usdc_1month_1m.csv")
    
    if not os.path.exists(csv_1w_path) or not os.path.exists(csv_1m_path):
        print("[ERROR] No se encontraron los datasets de alta resolución de 1m.")
        return
        
    df_1w = pd.read_csv(csv_1w_path)
    df_1m = pd.read_csv(csv_1m_path)
    
    # Configuraciones de deslizamiento
    slippage_configurations = [
        ("Asimétrico (Slippage 0.00%)", 0.0000, "#10b981", "-"),       # Verde esmeralda
        ("Optimizado (Slippage 0.03%)", 0.0003, "#3b82f6", "--"),      # Azul
        ("Naive (Slippage 0.10%)", 0.0010, "#f59e0b", "-."),           # Ámbar
        ("Bot Ineficiente (Slippage 1.00%)", 0.0100, "#ef4444", ":")   # Rojo
    ]
    
    # --- CAMPAÑA 1 SEMANA ---
    p_init_1w = df_1w["price"].values[0]
    p_final_1w = df_1w["price"].values[-1]
    hodl_1w = capital * 0.5 + capital * 0.5 * (p_final_1w / p_init_1w)
    dt_step_1w = 1.0 / 525600.0
    expected_vol_min_1w = df_1w["volume_real"].mean()
    
    plt.figure(figsize=(12, 6))
    
    # Graficar HODL
    plt.axhline(y=hodl_1w, color="#6b7280", linestyle=":", label=f"Solo HODL Puro (${hodl_1w:.2f} USD)", linewidth=2)
    
    for label, slip_rate, color, style in slippage_configurations:
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
        # El valor final minuto a minuto es capital + historial de retorno neto acumulado
        path = capital + res["history_path0"]["opt_constant"]
        minutes = np.arange(len(path))
        days = minutes / 1440.0
        plt.plot(days, path, label=f"{label} (Final: ${path[-1]:.2f})", color=color, linestyle=style, linewidth=2)
        
    plt.title("Campaña de 1 Semana: Desgaste de Cartera bajo Diferentes Deslizamientos (Slippage)\nEstrategia: Optimizada Constante (1m) | Capital Inicial: $2,000 USD", fontsize=12, fontweight="bold", pad=15)
    plt.xlabel("Tiempo de Simulación (Días)", fontsize=10)
    plt.ylabel("Valor Neto de la Cartera (USD)", fontsize=10)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(fontsize=10, loc="lower left")
    plt.tight_layout()
    
    plot_1w_path = os.path.join(os.path.dirname(__file__), "visual_slippage_comparison_1week.png")
    plt.savefig(plot_1w_path, dpi=150)
    plt.close()
    print(f"[OK] Gráfico semanal guardado en: {plot_1w_path}")
    
    # --- CAMPAÑA 1 MES ---
    p_init_1m = df_1m["price"].values[0]
    p_final_1m = df_1m["price"].values[-1]
    hodl_1m = capital * 0.5 + capital * 0.5 * (p_final_1m / p_init_1m)
    dt_step_1m = 1.0 / 525600.0
    expected_vol_min_1m = df_1m["volume_real"].mean()
    
    plt.figure(figsize=(12, 6))
    
    # Graficar HODL
    plt.axhline(y=hodl_1m, color="#6b7280", linestyle=":", label=f"Solo HODL Puro (${hodl_1m:.2f} USD)", linewidth=2)
    
    for label, slip_rate, color, style in slippage_configurations:
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
        path = capital + res["history_path0"]["opt_constant"]
        minutes = np.arange(len(path))
        days = minutes / 1440.0
        plt.plot(days, path, label=f"{label} (Final: ${path[-1]:.2f})", color=color, linestyle=style, linewidth=2)
        
    plt.title("Campaña de 1 Mes: Desgaste de Cartera bajo Diferentes Deslizamientos (Slippage)\nEstrategia: Optimizada Constante (1m) | Capital Inicial: $2,000 USD", fontsize=12, fontweight="bold", pad=15)
    plt.xlabel("Tiempo de Simulación (Días)", fontsize=10)
    plt.ylabel("Valor Neto de la Cartera (USD)", fontsize=10)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(fontsize=10, loc="upper left")
    plt.tight_layout()
    
    plot_1m_path = os.path.join(os.path.dirname(__file__), "visual_slippage_comparison_1month.png")
    plt.savefig(plot_1m_path, dpi=150)
    plt.close()
    print(f"[OK] Gráfico mensual guardado en: {plot_1m_path}")

if __name__ == "__main__":
    generate_slippage_plots()
