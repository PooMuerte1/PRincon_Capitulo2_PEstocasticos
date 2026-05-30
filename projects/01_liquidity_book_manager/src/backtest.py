import numpy as np
from typing import Dict, Any, Tuple
from .rebalancer import BinLiquidityRebalancer

class BinLiquidityBacktester:
    """
    Motor de Backtesting cuantitativo empírico avanzado para provisión de liquidez en Trader Joe.
    Soporta:
      - Dos estructuras de comisiones: Idealista y Realista (Volume-Share).
      - Cuatro modelos de estimación de volatilidad en tiempo real:
        1. Constante (Constant)
        2. Desviación Estándar Móvil (Simple Rolling)
        3. GARCH(1,1) Recursivo
        4. Filtro de Heston
      - Pérdida Impermanente (IL) real de desbalanceo.
      - Costo de gas de Avalanche C-Chain por transacción.
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
        fee_model: str = "realistic"
    ) -> Dict[str, Any]:
        """
        Ejecuta el backtest comparativo real de 9 estrategias cuantitativas.
        
        Soporta los dos modelos de comisiones (idealistic y realistic) y los 4
        estimadores de volatilidad (constant, rolling, garch, heston).
        """
        n_steps = len(prices_real) - 1

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
        price_bins = np.round(np.log(prices_real / prices_real[0]) / log_s).astype(int)

        # 2. Inicializar las 9 estrategias
        keys = [
            "static", "dynamic_1sig", "dynamic_2sig", "dynamic_3sig",
            "opt_constant", "opt_rolling", "opt_garch", "opt_heston", "opt_garch_cb"
        ]
        
        state = {}
        
        # Volatilidad incondicional estimada (promedio de la serie para los modelos constantes)
        log_returns_full = np.diff(np.log(prices_real))
        dt_min = 1.0 / 525600.0
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

        # Inicialización de posiciones para cada estrategia
        # Cada estrategia guarda: L, U, w, fees, gas, rebal, il, entry_bin, active
        # 1. Static
        state["static"] = {"L": price_bins[0] - static_width//2, "U": price_bins[0] + static_width//2, "w": static_width, "fees": 0.0, "gas": 0.0, "rebal": 0, "il": 0.0, "entry": price_bins[0], "active": True}
        
        # 2-4. Sigmas (usan Simple Rolling Volatility inicial)
        vol_init = vols_real[0]
        w_1s = get_sigma_width(vol_init, 1.0)
        w_2s = get_sigma_width(vol_init, 2.0)
        w_3s = get_sigma_width(vol_init, 3.0)
        state["dynamic_1sig"] = {"L": price_bins[0] - w_1s//2, "U": price_bins[0] + w_1s//2, "w": w_1s, "fees": 0.0, "gas": 0.0, "rebal": 0, "il": 0.0, "entry": price_bins[0], "active": True}
        state["dynamic_2sig"] = {"L": price_bins[0] - w_2s//2, "U": price_bins[0] + w_2s//2, "w": w_2s, "fees": 0.0, "gas": 0.0, "rebal": 0, "il": 0.0, "entry": price_bins[0], "active": True}
        state["dynamic_3sig"] = {"L": price_bins[0] - w_3s//2, "U": price_bins[0] + w_3s//2, "w": w_3s, "fees": 0.0, "gas": 0.0, "rebal": 0, "il": 0.0, "entry": price_bins[0], "active": True}

        # 5. Opt Constant
        w_c = get_opt_width(vol_unconditional)
        state["opt_constant"] = {"L": price_bins[0] - w_c//2, "U": price_bins[0] + w_c//2, "w": w_c, "fees": 0.0, "gas": 0.0, "rebal": 0, "il": 0.0, "entry": price_bins[0], "active": True}

        # 6. Opt Rolling
        w_r = get_opt_width(vol_init)
        state["opt_rolling"] = {"L": price_bins[0] - w_r//2, "U": price_bins[0] + w_r//2, "w": w_r, "fees": 0.0, "gas": 0.0, "rebal": 0, "il": 0.0, "entry": price_bins[0], "active": True}

        # 7. Opt GARCH
        state["opt_garch"] = {"L": price_bins[0] - w_r//2, "U": price_bins[0] + w_r//2, "w": w_r, "fees": 0.0, "gas": 0.0, "rebal": 0, "il": 0.0, "entry": price_bins[0], "active": True}

        # 8. Opt Heston
        state["opt_heston"] = {"L": price_bins[0] - w_r//2, "U": price_bins[0] + w_r//2, "w": w_r, "fees": 0.0, "gas": 0.0, "rebal": 0, "il": 0.0, "entry": price_bins[0], "active": True}

        # 9. Opt GARCH con Circuit Breaker
        state["opt_garch_cb"] = {"L": price_bins[0] - w_r//2, "U": price_bins[0] + w_r//2, "w": w_r, "fees": 0.0, "gas": 0.0, "rebal": 0, "il": 0.0, "entry": price_bins[0], "active": True}

        # Historial de ganancias netas acumuladas paso a paso para graficar
        history_path0 = {k: np.zeros(n_steps + 1) for k in keys}
        
        # Historial de volatilidades estimadas paso a paso para depuración y visualización
        history_vols = {
            "rolling": np.zeros(n_steps + 1),
            "garch": np.zeros(n_steps + 1),
            "heston": np.zeros(n_steps + 1)
        }
        history_vols["rolling"][0] = vol_init
        history_vols["garch"][0] = vol_init
        history_vols["heston"][0] = vol_init

        # Volatilidades recursivas iniciales
        vol_garch = vol_init
        vol_heston = vol_init

        # Bucle de backtest minuto a minuto
        for t in range(1, n_steps + 1):
            price_bin = price_bins[t]
            r_t = log_returns_full[t-1]  # Retorno real de este minuto

            # --- 3. ACTUALIZACIÓN EN TIEMPO REAL DE LOS ESTIMADORES DE VOLATILIDAD ---
            # A. Simple Rolling Volatility (30 minutos)
            if t >= 5:
                window_start = max(0, t - 1 - vol_window)
                returns_w = log_returns_full[window_start:t]
                std_step = np.std(returns_w, ddof=1)
                vol_rolling = std_step / np.sqrt(dt_min)
                vol_rolling = np.clip(vol_rolling, 0.10, 2.0)
            else:
                vol_rolling = vol_init
            history_vols["rolling"][t] = vol_rolling

            # B. GARCH(1,1) Recursivo
            # omega = vol_unconditional^2 * (1 - alpha - beta)
            alpha_g = 0.08
            beta_g = 0.90
            omega_g = (vol_unconditional ** 2) * (1.0 - alpha_g - beta_g)
            # Actualización de varianza anualizada condicional
            var_garch_next = omega_g + alpha_g * (r_t ** 2 / dt_min) + beta_g * (vol_garch ** 2)
            vol_garch = np.sqrt(np.clip(var_garch_next, 1e-4, 9.0))
            vol_garch = np.clip(vol_garch, 0.10, 2.0)
            history_vols["garch"][t] = vol_garch

            # C. Filtro de Heston
            # dV_t = theta*(V_bar - V_t)*dt + eta * sqrt(V_t) * dW_t
            # Usamos el residuo absoluto del retorno real reciente como shock para actualizar la varianza
            theta_h = 2.0
            eta_h = 0.25
            var_heston_prev = vol_heston ** 2
            var_heston_next = var_heston_prev + theta_h * ((vol_unconditional ** 2) - var_heston_prev) * dt_min + eta_h * np.abs(r_t)
            vol_heston = np.sqrt(np.clip(var_heston_next, 1e-4, 9.0))
            vol_heston = np.clip(vol_heston, 0.10, 2.0)
            history_vols["heston"][t] = vol_heston

            # Mapeo de estimador de volatilidad a cada estrategia
            vol_estimator = {
                "static": vol_unconditional,
                "dynamic_1sig": vol_rolling,
                "dynamic_2sig": vol_rolling,
                "dynamic_3sig": vol_rolling,
                "opt_constant": vol_unconditional,
                "opt_rolling": vol_rolling,
                "opt_garch": vol_garch,
                "opt_heston": vol_heston,
                "opt_garch_cb": vol_garch
            }

            # --- 4. FUNCIÓN DE IMPERMANENT LOSS REAL ---
            def compute_il(entry_b, exit_b):
                ratio = (1.0 + s) ** (exit_b - entry_b)
                il_pct = 1.0 - (2.0 * np.sqrt(ratio)) / (1.0 + ratio)
                return float(il_pct * capital)

            # --- 5. EVALUACIÓN Y REBALANCEO DE LAS ESTRATEGIAS ---
            for k in keys:
                st = state[k]
                vol_est_local = vol_estimator[k]

                # Caso Especial: Cortafuegos de Volatilidad
                if k == "opt_garch_cb":
                    if st["active"]:
                        if vol_est_local > vol_threshold:
                            # Activa cortafuegos: retira liquidez a stablecoin
                            st["gas"] += gas_fee
                            st["rebal"] += 1
                            st["active"] = False
                    else:
                        if vol_est_local <= vol_threshold:
                            # Se calma la tormenta: re-deposita centrándose
                            st["gas"] += gas_fee
                            st["rebal"] += 1
                            w_new = get_opt_width(vol_est_local)
                            st["w"] = w_new
                            st["L"] = price_bin - w_new // 2
                            st["U"] = price_bin + w_new // 2
                            st["entry"] = price_bin
                            st["active"] = True

                # Lógica general para posiciones activas
                if st["active"]:
                    if st["L"] <= price_bin <= st["U"]:
                        # ACUMULACIÓN DE COMISIONES (FEES)
                        if fee_model == "realistic":
                            # Porción del volumen real del pool minuto a minuto
                            c_bin = capital / st["w"]
                            share = c_bin / (pool_bin_tvl + c_bin)
                            fee_earned = volume_real[t] * base_fee_rate * share
                            st["fees"] += fee_earned
                        else:
                            # Modelo idealista simplificado antiguo
                            vol_factor = 1.0 + 2.0 * max(0.0, (vol_est_local / 0.65) - 1.0)
                            effective_fee_rate = base_fee_rate * vol_factor
                            c_bin = capital / st["w"]
                            st["fees"] += c_bin * effective_fee_rate
                    else:
                        # SALIDA DE RANGO: Rebalanceo con IL, gas y redefinición de ancho
                        il_loss = compute_il(st["entry"], price_bin)
                        st["il"] += il_loss
                        st["gas"] += gas_fee
                        st["rebal"] += 1

                        # Determinar nuevo ancho
                        if k == "static":
                            w_new = static_width
                        elif k == "dynamic_1sig":
                            w_new = get_sigma_width(vol_est_local, 1.0)
                        elif k == "dynamic_2sig":
                            w_new = get_sigma_width(vol_est_local, 2.0)
                        elif k == "dynamic_3sig":
                            w_new = get_sigma_width(vol_est_local, 3.0)
                        else:
                            # Para las optimizadas: consultar la tabla de búsqueda
                            w_new = get_opt_width(vol_est_local)

                        st["w"] = w_new
                        st["L"] = price_bin - w_new // 2
                        st["U"] = price_bin + w_new // 2
                        st["entry"] = price_bin

                # Guardar el valor neto neto acumulado en cada paso temporal
                history_path0[k][t] = st["fees"] - st["gas"] - st["il"]

        # 6. Compilar las estadísticas agregadas finales
        stats = {}
        for k in keys:
            st = state[k]
            net_ret = st["fees"] - st["gas"] - st["il"]
            stats[k] = {
                "mean_net_return": float(net_ret),
                "mean_rebalances": float(st["rebal"]),
                "mean_gas_spent": float(st["gas"]),
                "mean_il_loss": float(st["il"]),
                "mean_fees_earned": float(st["fees"])
            }

        return {
            "stats": stats,
            "history_path0": history_path0,
            "history_vols": history_vols
        }
