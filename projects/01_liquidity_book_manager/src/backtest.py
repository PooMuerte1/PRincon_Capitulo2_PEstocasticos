import numpy as np
from typing import Dict, Any, Tuple
from .rebalancer import BinLiquidityRebalancer

class BinLiquidityBacktester:
    """
    Motor de Backtesting cuantitativo empírico avanzado para provisión de liquidez en Trader Joe.
    Soporta:
      - Dos estructuras de comisiones: Idealista y Realista (Volume-Share).
      - Cuatro modelos de estimación de volatilidad en tiempo real (Constant, Rolling, GARCH, Heston).
      - 15 estrategias cuantitativas en paralelo (con y sin Cortafuegos Estocástico).
      - Pérdida Impermanente (IL) real de desbalanceo.
      - Costo de gas de Avalanche C-Chain por transacción.
      - Seguimiento exacto del VALOR ABSOLUTO DE LA CARTERA EN USD (Riesgo de Inventario).
    """
    def __init__(self):
        self.rebalancer = BinLiquidityRebalancer()

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
        """
        Precalcula y cachea el ancho de rango óptimo (W*) para un rango discreto de
        volatilidades (de 10% a 200% en incrementos de 1%), optimizando el rendimiento.
        """
        opt_cache = {}
        for vol_pct in range(10, 201):
            vol = vol_pct / 100.0
            s = bin_step_bp / 10000.0
            dt = (np.log(1.0 + s) / vol) ** 2
            drift_adjustment = (drift - 0.5 * (vol ** 2)) / vol
            p = 0.5 * (1.0 + drift_adjustment * np.sqrt(dt))
            
            opt = self.rebalancer.optimize_range(
                p=p,
                capital=capital,
                base_fee_rate=base_fee_rate,
                gas_fee=gas_fee,
                min_width=2,
                max_width=60,
                dt_years=dt,
                expected_volume_per_minute=expected_volume_per_minute,
                pool_bin_tvl=pool_bin_tvl,
                fee_model=fee_model
            )
            opt_cache[vol_pct] = opt["optimal_width"]
            
        return opt_cache

    def run_backtest(
        self,
        prices_real: np.ndarray,
        vols_real: np.ndarray,
        volume_real: np.ndarray,
        times_real: np.ndarray,
        capital: float,
        base_fee_rate: float,
        gas_fee: float,
        drift: float,
        bin_step_bp: float,
        static_width: int = 12,
        horizon_hours: float = 4.0,
        vol_threshold: float = 1.20,
        vol_window: int = 30,
        pool_bin_tvl: float = 100000.0,
        expected_volume_per_minute: float = 5000.0,
        fee_model: str = "realistic",
        dt_step: float = 1.0 / 525600.0
    ) -> Dict[str, Any]:
        """
        Ejecuta el backtest comparativo real de 15 estrategias cuantitativas.
        
        Soporta los dos modelos de comisiones (idealistic y realistic) y los 4
        estimadores de volatilidad (constant, rolling, garch, heston), evaluando
        cada estrategia con y sin cortafuegos.
        """
        n_steps = len(prices_real) - 1
        start_price = prices_real[0]

        # 1. Precalcular tabla de búsqueda óptima para la estrategia optimizada
        width_lookup = self._precompute_optimal_widths(
            capital=capital,
            base_fee_rate=base_fee_rate,
            gas_fee=gas_fee,
            drift=drift,
            bin_step_bp=bin_step_bp,
            fee_model=fee_model,
            expected_volume_per_minute=expected_volume_per_minute,
            pool_bin_tvl=pool_bin_tvl
        )

        tau = horizon_hours / 8760.0
        s = bin_step_bp / 10000.0
        log_s = np.log(1.0 + s)

        # Convertir precios a índices de bins discretos
        price_bins = np.round(np.log(prices_real / start_price) / log_s).astype(int)

        # 2. Definir las 15 estrategias a evaluar
        keys = [
            "static", 
            "dynamic_1sig", "dynamic_1sig_cb",
            "dynamic_2sig", "dynamic_2sig_cb",
            "dynamic_3sig", "dynamic_3sig_cb",
            "opt_constant", "opt_constant_cb",
            "opt_rolling", "opt_rolling_cb",
            "opt_garch", "opt_garch_cb",
            "opt_heston", "opt_heston_cb"
        ]
        
        state = {}
        
        # Volatilidad incondicional estimada (promedio de la serie para los modelos constantes)
        log_returns_full = np.diff(np.log(prices_real))
        dt_min = dt_step
        vol_unconditional = np.std(log_returns_full, ddof=1) / np.sqrt(dt_min)
        vol_unconditional = np.clip(vol_unconditional, 0.10, 2.0)
        
        # Función para determinar el ancho óptimo dada una volatilidad
        def get_opt_width(vol_est):
            vol_pct = int(np.clip(round(vol_est * 100), 10, 200))
            return width_lookup.get(vol_pct, 12)

        # Helpers para sigmas
        def get_sigma_width(vol_est, k_sigma):
            std_bins = (vol_est * np.sqrt(tau)) / log_s
            w = 2 * max(1, int(np.round(k_sigma * std_bins)))
            return w

        # Inicialización de posiciones para todas las 15 estrategias
        for k in keys:
            # Encontrar el ancho inicial correspondiente
            if k == "static":
                w = static_width
            elif "1sig" in k:
                w = get_sigma_width(vols_real[0], 1.0)
            elif "2sig" in k:
                w = get_sigma_width(vols_real[0], 2.0)
            elif "3sig" in k:
                w = get_sigma_width(vols_real[0], 3.0)
            elif "opt_constant" in k:
                w = get_opt_width(vol_unconditional)
            else:
                # Rolling, GARCH y Heston usan vols_real[0] al inicio
                w = get_opt_width(vols_real[0])
                
            state[k] = {
                "L": price_bins[0] - w//2,
                "U": price_bins[0] + w//2,
                "w": w,
                "fees": 0.0,
                "gas": 0.0,
                "rebal": 0,
                "il": 0.0,
                "entry": price_bins[0],
                "active": True,
                "capital_assets": capital
            }

        # Historial de ganancias netas acumuladas paso a paso para graficar
        history_path0 = {k: np.zeros(n_steps + 1) for k in keys}
        
        # Historial de volatilidades estimadas
        history_vols = {
            "rolling": np.zeros(n_steps + 1),
            "garch": np.zeros(n_steps + 1),
            "heston": np.zeros(n_steps + 1)
        }
        history_vols["rolling"][0] = vols_real[0]
        history_vols["garch"][0] = vols_real[0]
        history_vols["heston"][0] = vols_real[0]

        vol_garch = vols_real[0]
        vol_heston = vols_real[0]

        # Bucle de backtest minuto a minuto
        for t in range(1, n_steps + 1):
            price_bin = price_bins[t]
            r_t = log_returns_full[t-1]  # Retorno real de este minuto
            price_usd = prices_real[t]

            # --- 3. ACTUALIZACIÓN EN TIEMPO REAL DE LOS ESTIMADORES DE VOLATILIDAD ---
            if t >= 5:
                window_start = max(0, t - 1 - vol_window)
                returns_w = log_returns_full[window_start:t]
                std_step = np.std(returns_w, ddof=1)
                vol_rolling = std_step / np.sqrt(dt_min)
                vol_rolling = np.clip(vol_rolling, 0.10, 2.0)
            else:
                vol_rolling = vols_real[0]
            history_vols["rolling"][t] = vol_rolling

            # GARCH(1,1)
            alpha_g = 0.08
            beta_g = 0.90
            omega_g = (vol_unconditional ** 2) * (1.0 - alpha_g - beta_g)
            var_garch_next = omega_g + alpha_g * (r_t ** 2 / dt_min) + beta_g * (vol_garch ** 2)
            vol_garch = np.sqrt(np.clip(var_garch_next, 1e-4, 9.0))
            vol_garch = np.clip(vol_garch, 0.10, 2.0)
            history_vols["garch"][t] = vol_garch

            # Heston Filter
            theta_h = 2.0
            eta_h = 0.25
            var_heston_prev = vol_heston ** 2
            var_heston_next = var_heston_prev + theta_h * ((vol_unconditional ** 2) - var_heston_prev) * dt_min + eta_h * np.abs(r_t)
            vol_heston = np.sqrt(np.clip(var_heston_next, 1e-4, 9.0))
            vol_heston = np.clip(vol_heston, 0.10, 2.0)
            history_vols["heston"][t] = vol_heston

            # Asignar estimadores
            vol_estimator = {}
            for k in keys:
                if "constant" in k:
                    vol_estimator[k] = vol_unconditional
                elif "garch" in k:
                    vol_estimator[k] = vol_garch
                elif "heston" in k:
                    vol_estimator[k] = vol_heston
                elif "rolling" in k or "sig" in k:
                    vol_estimator[k] = vol_rolling
                else:
                    vol_estimator[k] = vol_unconditional

            # --- 4. FUNCIÓN DE IMPERMANENT LOSS REAL ---
            def compute_il(entry_b, exit_b):
                ratio = (1.0 + s) ** (exit_b - entry_b)
                il_pct = 1.0 - (2.0 * np.sqrt(ratio)) / (1.0 + ratio)
                return float(il_pct * capital)

            # --- 5. EVALUACIÓN Y REBALANCEO DE LAS 15 ESTRATEGIAS ---
            for k in keys:
                st = state[k]
                vol_est_local = vol_estimator[k]

                # A. Aplicar Lógica de Cortafuegos si corresponde
                if k.endswith("_cb"):
                    if st["active"]:
                        if vol_est_local > vol_threshold:
                            # Activa cortafuegos: retira liquidez a stablecoin
                            entry_usd_local = start_price * (1.0 + s) ** st["entry"]
                            L_usd_local = start_price * (1.0 + s) ** st["L"]
                            U_usd_local = start_price * (1.0 + s) ** st["U"]
                            
                            # Valuación antes de salir
                            if price_usd <= L_usd_local:
                                il_L = compute_il(st["entry"], st["L"])
                                current_assets = st["capital_assets"] * (0.5 + 0.5 * (L_usd_local / entry_usd_local)) * (1.0 - il_L / capital) * (price_usd / L_usd_local)
                            elif price_usd >= U_usd_local:
                                il_U = compute_il(st["entry"], st["U"])
                                current_assets = st["capital_assets"] * (0.5 + 0.5 * (U_usd_local / entry_usd_local)) * (1.0 - il_U / capital)
                            else:
                                il_t = compute_il(st["entry"], price_bin)
                                current_assets = st["capital_assets"] * (0.5 + 0.5 * (price_usd / entry_usd_local)) * (1.0 - il_t / capital)
                            
                            st["capital_assets"] = current_assets - gas_fee
                            st["gas"] += gas_fee
                            st["rebal"] += 1
                            st["active"] = False
                    else:
                        if vol_est_local <= vol_threshold:
                            # Se calma: re-deposita centrándose
                            st["gas"] += gas_fee
                            st["rebal"] += 1
                            st["capital_assets"] -= gas_fee
                            
                            if "1sig" in k:
                                w_new = get_sigma_width(vol_est_local, 1.0)
                            elif "2sig" in k:
                                w_new = get_sigma_width(vol_est_local, 2.0)
                            elif "3sig" in k:
                                w_new = get_sigma_width(vol_est_local, 3.0)
                            elif "constant" in k:
                                w_new = get_opt_width(vol_unconditional)
                            else:
                                w_new = get_opt_width(vol_est_local)
                                
                            st["w"] = w_new
                            st["L"] = price_bin - w_new // 2
                            st["U"] = price_bin + w_new // 2
                            st["entry"] = price_bin
                            st["active"] = True

                # B. Lógica de Provisiones Activas
                if st["active"]:
                    entry_usd_local = start_price * (1.0 + s) ** st["entry"]
                    L_usd_local = start_price * (1.0 + s) ** st["L"]
                    U_usd_local = start_price * (1.0 + s) ** st["U"]
                    
                    # Calcular valuación actual de activos
                    if price_usd <= L_usd_local:
                        il_L = compute_il(st["entry"], st["L"])
                        current_assets = st["capital_assets"] * (0.5 + 0.5 * (L_usd_local / entry_usd_local)) * (1.0 - il_L / capital) * (price_usd / L_usd_local)
                    elif price_usd >= U_usd_local:
                        il_U = compute_il(st["entry"], st["U"])
                        current_assets = st["capital_assets"] * (0.5 + 0.5 * (U_usd_local / entry_usd_local)) * (1.0 - il_U / capital)
                    else:
                        il_t = compute_il(st["entry"], price_bin)
                        current_assets = st["capital_assets"] * (0.5 + 0.5 * (price_usd / entry_usd_local)) * (1.0 - il_t / capital)

                    if st["L"] <= price_bin <= st["U"]:
                        # COMISIONES
                        if fee_model == "realistic":
                            c_bin = capital / st["w"]
                            share = c_bin / (pool_bin_tvl + c_bin)
                            fee_earned = volume_real[t] * base_fee_rate * share
                            st["fees"] += fee_earned
                        else:
                            vol_factor = 1.0 + 2.0 * max(0.0, (vol_est_local / 0.65) - 1.0)
                            effective_fee_rate = base_fee_rate * vol_factor
                            c_bin = capital / st["w"]
                            st["fees"] += c_bin * effective_fee_rate
                    else:
                        # REBALANCEO
                        il_loss = compute_il(st["entry"], price_bin)
                        st["il"] += il_loss
                        st["gas"] += gas_fee
                        st["rebal"] += 1

                        st["capital_assets"] = current_assets - gas_fee

                        # Determinar nuevo ancho
                        if k == "static":
                            w_new = static_width
                        elif "1sig" in k:
                            w_new = get_sigma_width(vol_est_local, 1.0)
                        elif "2sig" in k:
                            w_new = get_sigma_width(vol_est_local, 2.0)
                        elif "3sig" in k:
                            w_new = get_sigma_width(vol_est_local, 3.0)
                        elif "constant" in k:
                            w_new = get_opt_width(vol_unconditional)
                        else:
                            w_new = get_opt_width(vol_est_local)

                        st["w"] = w_new
                        st["L"] = price_bin - w_new // 2
                        st["U"] = price_bin + w_new // 2
                        st["entry"] = price_bin
                else:
                    current_assets = st["capital_assets"]

                # Guardar en historial
                history_path0[k][t] = st["fees"] - st["gas"] - st["il"]

        # 6. Compilar las estadísticas finales
        stats = {}
        for k in keys:
            st = state[k]
            net_ret = st["fees"] - st["gas"] - st["il"]
            
            final_assets = st["capital_assets"]
            absolute_portfolio_value = final_assets + st["fees"]
            absolute_net_profit = absolute_portfolio_value - capital
            inventory_devaluation = final_assets - capital + st["gas"]

            stats[k] = {
                "mean_net_return": float(net_ret),
                "mean_rebalances": float(st["rebal"]),
                "mean_gas_spent": float(st["gas"]),
                "mean_il_loss": float(st["il"]),
                "mean_fees_earned": float(st["fees"]),
                "final_assets": float(final_assets),
                "absolute_portfolio_value": float(absolute_portfolio_value),
                "absolute_net_profit": float(absolute_net_profit),
                "inventory_devaluation": float(inventory_devaluation)
            }

        return {
            "stats": stats,
            "history_path0": history_path0,
            "history_vols": history_vols
        }
