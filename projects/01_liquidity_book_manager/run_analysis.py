import os
import numpy as np
import matplotlib.pyplot as plt
from src.simulation import BinLiquiditySimulator
from src.metrics import BinLiquidityMetrics
from src.rebalancer import BinLiquidityRebalancer

def print_ascii_diagram(L: int, k: int, U: int, p: float):
    """
    Imprime un diagrama de consola representativo de la rejilla de bins y las barreras.
    """
    q = 1.0 - p
    print("\n=========================================================================")
    print("                     DIAGRAMA VISUAL DEL SISTEMA DE BINS                  ")
    print("=========================================================================")
    print(f" Barrera L (Muro Absorbente)                               Barrera U")
    print(f"       [{L:^3}] <===================== [{k:^3}] =====================> [{U:^3}]")
    print(f"        ||                            (Inicio)                          ||")
    print(f"        ||                                                              ||")
    print(f"        ||                   <--- q = {q:.4f}  |  p = {p:.4f} --->       ||")
    print(f"        v                                                               v")
    print("  [ REBALANCEO ]                                                  [ REBALANCEO ]")
    print("=========================================================================\n")

def evaluate_variable_time_mc(paths_array, times_array, L, U):
    """
    Evalúa métricas de Monte Carlo empíricas para simulaciones con reloj de tiempo variable.
    """
    n_paths = len(paths_array)
    is_out = (paths_array <= L) | (paths_array >= U)
    has_out = np.any(is_out, axis=1)
    first_out_idx = np.argmax(is_out, axis=1)
    
    # Probabilidad de Ruina (tocar L antes que U)
    ruined = np.where(has_out, paths_array[np.arange(n_paths), first_out_idx] <= L, False)
    empirical_ruin = np.mean(ruined)
    empirical_ruin_se = np.std(ruined, ddof=1) / np.sqrt(n_paths)
    
    # Tiempo de salida en días reales
    exit_years = np.where(has_out, times_array[np.arange(n_paths), first_out_idx], times_array[:, -1])
    exit_days = exit_years * 365.0
    empirical_duration_days = np.mean(exit_days)
    empirical_duration_se_days = np.std(exit_days, ddof=1) / np.sqrt(n_paths)
    
    return {
        "ruin_prob": empirical_ruin,
        "ruin_se": empirical_ruin_se,
        "duration_days": empirical_duration_days,
        "duration_se_days": empirical_duration_se_days,
        "unabsorbed": np.mean(~has_out)
    }

def run_main_analysis():
    # Fijar semilla de reproducibilidad
    np.random.seed(42)

    # 1. Configuración de parámetros de mercado continuos (AVAX/USDC en Avalanche)
    volatility = 0.65       # 65% anualizada
    drift = 0.15            # 15% de retorno anual
    bin_step_bp = 15.0      # 15 basis points por bin (s = 0.0015)

    print("=== CONFIGURACIÓN CONTINUA DE MERCADO ===")
    print(f"Activo: AVAX")
    print(f"Volatilidad Anual (sigma): {volatility * 100:.2f}%")
    print(f"Retorno Anual (mu): {drift * 100:.2f}%")
    print(f"Ancho del Bin (binStep): {bin_step_bp} puntos básicos (0.15%)\n")

    # 2. Inicializar componentes
    simulator = BinLiquiditySimulator()
    metrics_calc = BinLiquidityMetrics()
    rebalancer = BinLiquidityRebalancer()

    # 3. Calibrar parámetros discretos base
    p, q, dt = simulator.calibrate_parameters(volatility, drift, bin_step_bp)
    
    dt_days = dt * 365.0
    dt_hours = dt_days * 24.0
    print("=== CALIBRACIÓN DISCRETA (PUENTE CONTINUO-DISCRETO) ===")
    print(f"Intervalo de tiempo por paso (dt): {dt:.8f} años")
    print(f"  -> Equivalente a: {dt_days:.4f} días ({dt_hours:.2f} horas)")
    print(f"Probabilidad de subir bin (p): {p:.6f}")
    print(f"Probabilidad de bajar bin (q): {q:.6f}\n")

    # 4. Configurar el escenario de evaluación
    L = -10
    U = 10
    k = 0
    
    print_ascii_diagram(L, k, U, p)

    # Calcular valores teóricos exactos clásicos (Volatilidad Constante)
    theoretical_ruin = metrics_calc.calculate_theoretical_ruin(k, L, U, p)
    theoretical_duration = metrics_calc.calculate_theoretical_duration(k, L, U, p)

    print("=== CÁLCULO DE VALORES TEÓRICOS EXACTOS CLÁSICOS ===")
    print(f"Probabilidad exacta de tocar barrera L antes que U (Ruin): {theoretical_ruin * 100:.4f}%")
    print(f"Tiempo esperado de permanencia activa (m_k): {theoretical_duration:.2f} pasos discretos")
    print(f"  -> Equivalente en tiempo real: {theoretical_duration * dt_days:.2f} días\n")

    # 5. Ejecutar Simulaciones de Monte Carlo para los 3 Modelos
    n_paths = 15000
    n_steps = 1000 # Pasos de la simulación

    # A. Modelo de Volatilidad Constante (Base)
    print(f"A. Simulando {n_paths} caminos con VOLATILIDAD CONSTANTE...")
    paths_const = simulator.simulate_paths(n_steps, n_paths, k, p)
    times_const = np.tile(np.arange(n_steps + 1) * dt, (n_paths, 1)) # dt constante para cada paso
    mc_const = evaluate_variable_time_mc(paths_const, times_const, L, U)

    # B. Modelo GARCH(1,1) de Volatilidad Dinámica
    alpha_garch = 0.08
    beta_garch = 0.90
    print(f"B. Simulando {n_paths} caminos con VOLATILIDAD DINÁMICA GARCH(1,1)...")
    paths_garch, vols_garch, times_garch = simulator.simulate_paths_garch(
        n_steps, n_paths, k, volatility, drift, bin_step_bp, alpha=alpha_garch, beta=beta_garch
    )
    mc_garch = evaluate_variable_time_mc(paths_garch, times_garch, L, U)

    # C. Modelo de Volatilidad Estocástica (Heston Discreto)
    theta_heston = 2.0
    eta_heston = 0.25 # vol of vol
    print(f"C. Simulando {n_paths} caminos con VOLATILIDAD ESTOCÁSTICA HESTON...")
    paths_heston, vols_heston, times_heston = simulator.simulate_paths_heston(
        n_steps, n_paths, k, volatility, drift, bin_step_bp, theta=theta_heston, eta=eta_heston
    )
    mc_heston = evaluate_variable_time_mc(paths_heston, times_heston, L, U)

    # 6. Tabla Comparativa de Resultados
    print("\n=========================================================================")
    print("                      TABLA COMPARATIVA DE MODELOS                       ")
    print("=========================================================================")
    print("  Modelo             | Prob. Ruina (L primero) | Duración Activa Promedio")
    print("-------------------------------------------------------------------------")
    print(f"  Vol. Constante     |      {mc_const['ruin_prob']*100:6.2f} %           |      {mc_const['duration_days']:7.4f} días")
    print(f"  GARCH(1,1)         |      {mc_garch['ruin_prob']*100:6.2f} %           |      {mc_garch['duration_days']:7.4f} días")
    print(f"  Heston Discreto    |      {mc_heston['ruin_prob']*100:6.2f} %           |      {mc_heston['duration_days']:7.4f} días")
    print("=========================================================================\n")

    # 7. Graficar Comparativa de Volatilidad y Caminos de Precios
    print("Generando panel visual comparativo...")
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))

    # Subplot 1: Caminos de precio bajo Heston
    # Graficar las primeras 10 trayectorias
    for i in range(10):
        ax1.plot(paths_heston[i, :200], alpha=0.6)
    ax1.axhline(y=U, color='g', linestyle='--', linewidth=2, label=f"Barrera U ({U})")
    ax1.axhline(y=L, color='r', linestyle='--', linewidth=2, label=f"Barrera L ({L})")
    ax1.axhline(y=k, color='black', linestyle=':', label="Bin inicial")
    ax1.set_title("Trayectorias de Precios (Volatilidad Heston)", fontsize=11)
    ax1.set_xlabel("Pasos Discretos", fontsize=9)
    ax1.set_ylabel("Índice de Bin", fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper left", fontsize=8)

    # Subplot 2: GARCH Volatility Evolution para el primer camino
    sample_path_idx = 0
    ax2.plot(paths_garch[sample_path_idx, :300], color='blue', label="Precio (Bin)")
    ax2_vol = ax2.twinx()
    ax2_vol.plot(vols_garch[sample_path_idx, :300] * 100, color='orange', linestyle='--', label="Vol. GARCH (%)")
    ax2.set_title("Camino GARCH: Precio vs. Vol. Dinámica", fontsize=11)
    ax2.set_xlabel("Pasos Discretos", fontsize=9)
    ax2.set_ylabel("Índice de Bin (Precio)", color='blue', fontsize=9)
    ax2_vol.set_ylabel("Volatilidad Anualizada GARCH (%)", color='orange', fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # Combinar leyendas
    lines, labels = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_vol.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc="upper left", fontsize=8)

    # Subplot 3: Heston Volatility Evolution para el primer camino
    ax3.plot(paths_heston[sample_path_idx, :300], color='purple', label="Precio (Bin)")
    ax3_vol = ax3.twinx()
    ax3_vol.plot(vols_heston[sample_path_idx, :300] * 100, color='red', linestyle='--', label="Vol. Heston (%)")
    ax3.set_title("Camino Heston: Precio vs. Vol. Estocástica", fontsize=11)
    ax3.set_xlabel("Pasos Discretos", fontsize=9)
    ax3.set_ylabel("Índice de Bin (Precio)", color='purple', fontsize=9)
    ax3_vol.set_ylabel("Volatilidad Anualizada Heston (%)", color='red', fontsize=9)
    ax3.grid(True, alpha=0.3)
    
    # Combinar leyendas
    lines_h, labels_h = ax3.get_legend_handles_labels()
    lines_h2, labels_h2 = ax3_vol.get_legend_handles_labels()
    ax3.legend(lines_h + lines_h2, labels_h + labels_h2, loc="upper left", fontsize=8)

    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(__file__), "visual_comparison_volatility.png")
    plt.savefig(output_path, dpi=150)
    print(f"¡Gráficos comparativos de volatilidad guardados en: {output_path}!\n")

if __name__ == "__main__":
    run_main_analysis()
