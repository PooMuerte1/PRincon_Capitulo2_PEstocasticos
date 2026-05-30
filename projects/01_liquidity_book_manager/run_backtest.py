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
    # 1 gwei (nAVAX) = 1e-9 AVAX
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

def print_campaign_table(campaign_title: str, results: Dict[str, Any], capital: float, fee_rate: float, gas_fee: float):
    """
    Imprime una tabla de reporte ASCII de alta fidelidad para una campaña específica.
    """
    print("\n" + "=" * 110)
    print(f" {campaign_title:^108} ")
    print(f"      CAPITAL INICIAL: ${capital:.2f} USD | TASA SWAP POOL: {fee_rate*100:.3f}% | COSTO GAS REBAL: ${gas_fee:.2f} USD")
    print("=" * 110)
    print("  Estrategia / Estimador Volatilidad | Retorno Neto ($) | Swap Fees ($) | Gas Pagado ($) | Perdida IL ($) | Rebalances")
    print("-" * 110)
    
    mapping = {
        "static": "Estática (Manual Fijo 12 bins) ",
        "dynamic_1sig": "Dinámica 1-Sigma (Rolling Vol) ",
        "dynamic_2sig": "Dinámica 2-Sigma (Rolling Vol) ",
        "dynamic_3sig": "Dinámica 3-Sigma (Rolling Vol) ",
        "opt_constant": "Optimizada (Vol. Constante 44%)",
        "opt_rolling": "Optimizada (Rolling Vol 30m)  ",
        "opt_garch": "Optimizada (GARCH 1,1 condic)  ",
        "opt_heston": "Optimizada (Filtro Heston stoch)",
        "opt_garch_cb": "Optimizada (GARCH + Cortafuegos) "
    }

    for k in [
        "static", "dynamic_1sig", "dynamic_2sig", "dynamic_3sig",
        "opt_constant", "opt_rolling", "opt_garch", "opt_heston", "opt_garch_cb"
    ]:
        stats = results["stats"][k]
        
        net_ret = stats["mean_net_return"]
        gas_spent = stats["mean_gas_spent"]
        il_loss = stats["mean_il_loss"]
        fees_earned = stats["mean_fees_earned"]
        rebal_count = stats["mean_rebalances"]
        
        print(
            f"  - {mapping[k]:32} | "
            f"${net_ret:15.2f} | "
            f"${fees_earned:13.2f} | "
            f"${gas_spent:14.2f} | "
            f"${il_loss:14.2f} | "
            f"{rebal_count:10.0f}"
        )
    print("=" * 110 + "\n")

def run_backtesting_campaign():
    # 1. Configuración de Parámetros Reales de Mercado y Red
    bin_step_bp = 15.0      # 15 basis points por bin de Trader Joe (s = 0.0015)
    capital = 2000.0        # Bóveda del LP de $2000 USD
    base_fee_rate = 0.0009  # Comisión real del pool principal WAVAX/USDC (0.09% swap fee tier)
    drift = 0.15            # 15% retorno anual esperado
    pool_bin_tvl = 100000.0 # Competencia estimada: $100k USD por bin activo en el pool
    
    # Gas real de Avalanche C-Chain calibrado a $0.3500 USD
    gas_used_joe = 300000   
    gas_price_avax = 33.3333333  # gwei
    avax_price_usd = 35.0   # USD
    
    gas_fee_real, gas_breakdown = explain_avalanche_gas_fees(gas_used_joe, gas_price_avax, avax_price_usd)

    print("=========================================================================")
    print("              CÁLCULO CIENTÍFICO DE GAS FEE EN AVALANCHE C-CHAIN         ")
    print("=========================================================================")
    print(gas_breakdown)
    print("=========================================================================\n")

    # 2. Cargar Dataset Histórico Empírico Real (Fase A)
    csv_path = os.path.join(os.path.dirname(__file__), "avax_usdc_historical.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró el archivo de precios históricos en: {csv_path}")
        
    df_hist = pd.read_csv(csv_path)
    prices_real = df_hist["price"].values
    vols_real = df_hist["volatility_true"].values
    volume_real = df_hist["volume_real"].values
    
    n_steps = len(df_hist) - 1
    
    # Calcular volumen esperado por minuto
    expected_vol_min = volume_real.mean()
    
    print(f"Cargando dataset histórico empírico on-chain (GeckoTerminal): {csv_path}")
    print(f"  - Registros cargados: {len(df_hist):,} minutos (aprox. {n_steps/60:.2f} horas de trading real)")
    print(f"  - Precio Inicial AVAX: ${prices_real[0]:.4f} USD")
    print(f"  - Precio Final AVAX: ${prices_real[-1]:.4f} USD")
    print(f"  - Variación de Precio: {((prices_real[-1] / prices_real[0]) - 1.0) * 100:.2f}% (Tendencia bajista del -3.03%)\n")
    print(f"  - Volumen Promedio de Trading del Pool: ${expected_vol_min:,.2f} USD/minuto")
    print(f"  - Liquidez de Competencia por Bin ($L_bin$): ${pool_bin_tvl:,.2f} USD")

    # 3. Inicializar Backtester Cuantitativo
    backtester = BinLiquidityBacktester()

    # Tiempo en fracción de año para cada paso
    dt_min = 1.0 / 525600.0
    times_real = np.arange(n_steps + 1) * dt_min

    # --- CAMPAÑA A: MODELO DE COMISIONES IDEALISTA (FALSO) ---
    print("\nEjecutando Campaña A: Modelo de Comisiones Idealista (Antiguo)...")
    results_ideal = backtester.run_backtest(
        prices_real=prices_real,
        vols_real=vols_real,
        volume_real=volume_real,
        times_real=times_real,
        capital=capital,
        base_fee_rate=0.0035, # Usamos el fee rate de simulación antiguo
        gas_fee=gas_fee_real,
        drift=drift,
        bin_step_bp=bin_step_bp,
        static_width=12,
        horizon_hours=4.0,
        vol_threshold=1.20,
        vol_window=30,
        pool_bin_tvl=pool_bin_tvl,
        expected_volume_per_minute=expected_vol_min,
        fee_model="idealistic"
    )

    # --- CAMPAÑA B: MODELO DE COMISIONES REALISTA (VOLUME-SHARE) ---
    print("Ejecutando Campaña B: Modelo de Comisiones Realista en Cadena (LFJ)...")
    results_real = backtester.run_backtest(
        prices_real=prices_real,
        vols_real=vols_real,
        volume_real=volume_real,
        times_real=times_real,
        capital=capital,
        base_fee_rate=base_fee_rate, # 0.09% real
        gas_fee=gas_fee_real,
        drift=drift,
        bin_step_bp=bin_step_bp,
        static_width=12,
        horizon_hours=4.0,
        vol_threshold=1.20,
        vol_window=30,
        pool_bin_tvl=pool_bin_tvl,
        expected_volume_per_minute=expected_vol_min,
        fee_model="realistic"
    )

    # 4. Imprimir Reportes Cuantitativos
    print_campaign_table("CAMPAÑA A: REPORTE DE BACKTEST BAJO MODELO DE COMISIONES IDEALISTA (VOL. CONSTANTE/FAKE)", results_ideal, capital, 0.0035, gas_fee_real)
    print_campaign_table("CAMPAÑA B: REPORTE DE BACKTEST BAJO MODELO DE COMISIONES REALISTA (VOLUME-SHARE DE POOL LFJ)", results_real, capital, base_fee_rate, gas_fee_real)

    # 5. Graficar los Resultados de Tiempo vs. Rentabilidad Real Acumulada
    print("Generando visualizaciones de rentabilidad temporal empírica bajo el modelo realista...")
    plt.figure(figsize=(12, 7))
    
    # Tiempo transcurrido en horas
    hours_elapsed = times_real * 365.0 * 24.0

    colors = {
        "static": "red",
        "dynamic_1sig": "orange",
        "dynamic_2sig": "darkorange",
        "dynamic_3sig": "gold",
        "opt_constant": "gray",
        "opt_rolling": "cyan",
        "opt_garch": "green",
        "opt_heston": "purple",
        "opt_garch_cb": "blue"
    }
    
    labels = {
        "static": "Estática (Fijo 12 bins)",
        "dynamic_1sig": "Dinámica 1-Sigma",
        "dynamic_2sig": "Dinámica 2-Sigma",
        "dynamic_3sig": "Dinámica 3-Sigma",
        "opt_constant": "Optimizada (Vol. Constante)",
        "opt_rolling": "Optimizada (Rolling Vol 30m)",
        "opt_garch": "Optimizada (GARCH Vol condic)",
        "opt_heston": "Optimizada (Heston Filter)",
        "opt_garch_cb": "Optimizada (GARCH + CB)"
    }

    # Graficar en el modelo realista
    for k in colors:
        linewidth = 2.5 if k in ["opt_garch", "opt_garch_cb", "opt_heston"] else 1.2
        linestyle = "--" if k == "opt_garch_cb" else "-"
        plt.plot(hours_elapsed, results_real["history_path0"][k], color=colors[k], linewidth=linewidth, linestyle=linestyle, label=labels[k])
        
    plt.axhline(y=0, color='black', linestyle=':', label="Punto de Empate ($0 USD)")
    plt.title("Evolución de Rentabilidad Neta REALISTA en WAVAX/USDC (Datos On-Chain GeckoTerminal)", fontsize=12)
    plt.xlabel("Tiempo Transcurrido (Horas)", fontsize=10)
    plt.ylabel("Rentabilidad Neta Acumulada (USD) [Fees - Gas - IL]", fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=9, loc="upper left")

    output_path = os.path.join(os.path.dirname(__file__), "visual_backtest_performance.png")
    plt.savefig(output_path, dpi=150)
    print(f"¡Gráfico de rendimiento de Backtesting Empírico guardado en: {output_path}!\n")

    # Graficar los estimadores de volatilidad para visualizar su lag y picos
    plt.figure(figsize=(12, 5))
    plt.plot(hours_elapsed, vols_real * 100, color='gray', alpha=0.5, label="Vol. Realizada (Binance ref)")
    plt.plot(hours_elapsed, results_real["history_vols"]["rolling"] * 100, color='cyan', label="Simple Rolling Vol 30m")
    plt.plot(hours_elapsed, results_real["history_vols"]["garch"] * 100, color='green', label="Condicional GARCH(1,1)")
    plt.plot(hours_elapsed, results_real["history_vols"]["heston"] * 100, color='purple', label="Stochastic Heston Filter")
    plt.title("Evolución de los Estimadores de Volatilidad en el Entorno Real", fontsize=12)
    plt.xlabel("Tiempo Transcurrido (Horas)", fontsize=10)
    plt.ylabel("Volatilidad Anualizada Estimada (%)", fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=9, loc="upper right")
    
    output_vol_path = os.path.join(os.path.dirname(__file__), "visual_comparison_volatility.png")
    plt.savefig(output_vol_path, dpi=150)
    print(f"¡Gráfico de evolución de volatilidad guardado en: {output_vol_path}!\n")

if __name__ == "__main__":
    run_backtesting_campaign()
