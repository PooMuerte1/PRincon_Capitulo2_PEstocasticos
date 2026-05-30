import numpy as np
from typing import Tuple

class BinLiquiditySimulator:
    """
    Simulador cuantitativo de trayectorias de precio discretizadas sobre bins
    de Trader Joe (Liquidity Book) utilizando caminatas aleatorias.
    """
    def __init__(self):
        pass

    def calibrate_parameters(self, volatility: float, drift: float, bin_step_bp: float) -> Tuple[float, float, float]:
        """
        Calibra los parámetros de la caminata aleatoria discreta a partir de
        las variables anualizadas del mercado continuo.

        Args:
            volatility: Volatilidad anualizada (p. ej., 0.60 para 60%).
            drift: Tasa de deriva o retorno anualizado (p. ej., 0.10 para 10%).
            bin_step_bp: Tamaño del paso del bin en puntos básicos (basis points, p. ej., 15).

        Returns:
            p: Probabilidad discreta de subir un bin.
            q: Probabilidad discreta de bajar un bin.
            dt: Intervalo de tiempo por paso discreto (en años).
        """
        if volatility <= 0:
            raise ValueError("La volatilidad debe ser estrictamente positiva.")
        if bin_step_bp <= 0:
            raise ValueError("El binStep debe ser estrictamente positivo.")

        # Convertir basis points a decimales (p. ej., 15 bp -> 0.0015)
        s = bin_step_bp / 10000.0

        # Calcular dt: intervalo de tiempo para que un paso sea exactamente de tamaño ln(1 + s)
        dt = (np.log(1.0 + s) / volatility) ** 2

        # Calcular la probabilidad neutral al riesgo p de subir un paso
        # Ajustamos por el drift continuo descontando la varianza de Ito (mu - 0.5 * sigma^2)
        drift_adjustment = (drift - 0.5 * (volatility ** 2)) / volatility
        p = 0.5 * (1.0 + drift_adjustment * np.sqrt(dt))
        q = 1.0 - p

        # Validación física de probabilidades
        if p < 0.0 or p > 1.0:
            raise ValueError(
                f"Calibración fuera de límites físicos: p={p:.4f}. "
                "La volatilidad es demasiado baja o el binStep es extremadamente alto "
                "para la tasa de drift seleccionada."
            )

        return p, q, dt

    def simulate_paths(self, steps: int, paths: int, start_bin: int, p: float) -> np.ndarray:
        """
        Genera trayectorias vectorizadas de caminata aleatoria discreta sobre bins.

        Args:
            steps: Cantidad de pasos temporales a simular en cada camino.
            paths: Número de trayectorias (caminos independientes) a generar.
            start_bin: Índice del bin inicial (punto de partida k).
            p: Probabilidad de dar un paso hacia arriba (+1).

        Returns:
            Un array de dimensiones (paths, steps + 1) con los índices de los bins.
        """
        if steps <= 0 or paths <= 0:
            raise ValueError("Steps y Paths deben ser mayores que cero.")

        # Generar decisiones aleatorias vectorizadas: True (+1) con prob p, False (-1) con prob (1-p)
        rands = np.random.rand(paths, steps)
        steps_taken = np.where(rands < p, 1, -1)

        # Acumular los pasos a lo largo del tiempo
        paths_accum = np.cumsum(steps_taken, axis=1)

        # Concatenar el bin inicial al principio de cada trayectoria
        initial_column = np.full((paths, 1), start_bin, dtype=int)
        all_paths = np.hstack([initial_column, start_bin + paths_accum])

        return all_paths

    def simulate_paths_garch(
        self,
        steps: int,
        paths: int,
        start_bin: int,
        volatility_init: float,
        drift: float,
        bin_step_bp: float,
        alpha: float = 0.08,
        beta: float = 0.90
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Simula trayectorias de precios sobre bins usando un modelo GARCH(1,1) de volatilidad dinámica.
        Implementa un reloj de tiempo variable (Time-Changed Random Walk).

        Returns:
            bins: Array (paths, steps + 1) con los índices de los bins.
            vols: Array (paths, steps + 1) con las volatilidades anualizadas locales.
            times: Array (paths, steps + 1) con el tiempo acumulado en años.
        """
        s = bin_step_bp / 10000.0
        log_s = np.log(1.0 + s)
        sigma_unconditional = volatility_init
        
        bins = np.zeros((paths, steps + 1), dtype=int)
        vols = np.zeros((paths, steps + 1), dtype=float)
        times = np.zeros((paths, steps + 1), dtype=float)
        
        bins[:, 0] = start_bin
        vols[:, 0] = sigma_unconditional
        times[:, 0] = 0.0
        
        # Parámetro omega GARCH anualizado (garantiza la reversión a la volatilidad incondicional)
        omega_annual = (sigma_unconditional ** 2) * (1.0 - alpha - beta)
        
        for t in range(1, steps + 1):
            sigma_prev = vols[:, t-1]
            Z = np.random.normal(0, 1, paths)
            
            # Ecuación de actualización de varianza GARCH(1,1)
            variance_next = omega_annual + alpha * (sigma_prev ** 2) * (Z ** 2) + beta * (sigma_prev ** 2)
            variance_next = np.clip(variance_next, 1e-4, 9.0)  # Filtro de seguridad física
            sigma_next = np.sqrt(variance_next)
            
            vols[:, t] = sigma_next
            
            # Reloj de tiempo variable: dt es inversamente proporcional a la volatilidad al cuadrado
            dt_t = (log_s / sigma_next) ** 2
            times[:, t] = times[:, t-1] + dt_t
            
            # Probabilidad local de subir bin p_t
            drift_adjustment = (drift - 0.5 * variance_next) / sigma_next
            p_t = 0.5 * (1.0 + drift_adjustment * np.sqrt(dt_t))
            p_t = np.clip(p_t, 0.0, 1.0)
            
            rands = np.random.rand(paths)
            steps_taken = np.where(rands < p_t, 1, -1)
            
            bins[:, t] = bins[:, t-1] + steps_taken
            
        return bins, vols, times

    def simulate_paths_heston(
        self,
        steps: int,
        paths: int,
        start_bin: int,
        volatility_init: float,
        drift: float,
        bin_step_bp: float,
        theta: float = 2.0,      # Velocidad de reversión a la media
        eta: float = 0.25        # Volatilidad de la volatilidad (vol of vol)
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Simula trayectorias de precios sobre bins usando un modelo de Volatilidad Estocástica (Heston Discreto).
        Implementa un reloj de tiempo variable (Time-Changed Random Walk).

        Returns:
            bins: Array (paths, steps + 1) con los índices de los bins.
            vols: Array (paths, steps + 1) con las volatilidades anualizadas locales.
            times: Array (paths, steps + 1) con el tiempo acumulado en años.
        """
        s = bin_step_bp / 10000.0
        log_s = np.log(1.0 + s)
        omega_unconditional = volatility_init ** 2
        
        bins = np.zeros((paths, steps + 1), dtype=int)
        vols = np.zeros((paths, steps + 1), dtype=float)
        times = np.zeros((paths, steps + 1), dtype=float)
        
        bins[:, 0] = start_bin
        vols[:, 0] = volatility_init
        times[:, 0] = 0.0
        
        for t in range(1, steps + 1):
            sigma_prev = vols[:, t-1]
            var_prev = sigma_prev ** 2
            
            # Tiempo transcurrido en el paso anterior para calibrar la discretización
            dt_prev = (log_s / sigma_prev) ** 2
            
            # Shock estocástico normal e independiente para la volatilidad
            Z = np.random.normal(0, 1, paths)
            
            # Ecuación Heston discreta para varianza anualizada (reversión a la media + shock)
            variance_next = var_prev + theta * (omega_unconditional - var_prev) * dt_prev + eta * sigma_prev * np.sqrt(dt_prev) * Z
            variance_next = np.clip(variance_next, 1e-4, 9.0)  # Filtro de seguridad física
            sigma_next = np.sqrt(variance_next)
            
            vols[:, t] = sigma_next
            
            # Reloj de tiempo variable local
            dt_t = (log_s / sigma_next) ** 2
            times[:, t] = times[:, t-1] + dt_t
            
            # Probabilidad local de subir bin p_t
            drift_adjustment = (drift - 0.5 * variance_next) / sigma_next
            p_t = 0.5 * (1.0 + drift_adjustment * np.sqrt(dt_t))
            p_t = np.clip(p_t, 0.0, 1.0)
            
            rands = np.random.rand(paths)
            steps_taken = np.where(rands < p_t, 1, -1)
            
            bins[:, t] = bins[:, t-1] + steps_taken
            
        return bins, vols, times
