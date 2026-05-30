import numpy as np
from typing import Dict, Any, Tuple

class BinLiquidityMetrics:
    """
    Biblioteca cuantitativa para el cálculo analítico y la validación empírica
    de las probabilidades de ruina (salida por barrera) y duración de liquidez.
    """
    def __init__(self):
        pass

    def calculate_theoretical_ruin(self, k: int, L: int, U: int, p: float) -> float:
        """
        Calcula la probabilidad teórica exacta de tocar el límite inferior L antes
        que el límite superior U, partiendo del bin inicial k.

        Args:
            k: Bin inicial.
            L: Límite inferior (barrera absorbente inferior).
            U: Límite superior (barrera absorbente superior).
            p: Probabilidad de subir un bin.

        Returns:
            u_k: Probabilidad de ruina (tocar L antes que U).
        """
        if not (L < k < U):
            raise ValueError("El bin inicial k debe estar estrictamente dentro del rango (L, U).")

        q = 1.0 - p

        # Caso simétrico (Juego justo)
        if np.isclose(p, 0.5):
            return (U - k) / (U - L)

        # Caso asimétrico (Con drift)
        r = q / p
        numerator = (r ** (k - L)) - (r ** (U - L))
        denominator = 1.0 - (r ** (U - L))
        return numerator / denominator

    def calculate_theoretical_duration(self, k: int, L: int, U: int, p: float) -> float:
        """
        Calcula la duración esperada exacta (en número de pasos discretos)
        antes de tocar cualquiera de las barreras L o U, partiendo del bin inicial k.

        Args:
            k: Bin inicial.
            L: Límite inferior.
            U: Límite superior.
            p: Probabilidad de subir un bin.

        Returns:
            m_k: Cantidad esperada de pasos discretos hasta absorción.
        """
        if not (L < k < U):
            raise ValueError("El bin inicial k debe estar estrictamente dentro del rango (L, U).")

        q = 1.0 - p

        # Caso simétrico (Juego justo)
        if np.isclose(p, 0.5):
            return float((k - L) * (U - k))

        # Caso asimétrico (Con drift)
        r = q / p
        diff = q - p
        term1 = (k - L) / diff
        term2 = ((U - L) / diff) * ((1.0 - (r ** (k - L))) / (1.0 - (r ** (U - L))))
        return term1 - term2

    def evaluate_monte_carlo(self, paths_array: np.ndarray, L: int, U: int) -> Dict[str, Any]:
        """
        Extrae y evalúa las métricas empíricas de absorción a partir de las
        trayectorias simuladas de Monte Carlo. Calcula errores estándar e IC 95%.

        Args:
            paths_array: Array de NumPy con dimensiones (paths, steps + 1).
            L: Límite inferior.
            U: Límite superior.

        Returns:
            Un diccionario con las métricas empíricas, desviaciones y CIs.
        """
        n_paths, n_steps = paths_array.shape
        n_steps -= 1  # No contamos el paso cero inicial

        # Encontrar los momentos de salida
        # is_out es True si el precio toca o supera L o U
        is_out = (paths_array <= L) | (paths_array >= U)
        has_out = np.any(is_out, axis=1)

        # Para los caminos que salieron, tomamos el primer índice
        first_out_idx = np.argmax(is_out, axis=1)

        # Tiempos de absorción: si no salió, imputamos el máximo de pasos de la simulación
        absorption_times = np.where(has_out, first_out_idx, n_steps)

        # Advertencia de sesgo si muchos caminos no se absorbieron
        unabsorbed_ratio = np.mean(~has_out)

        # Calcular estadísticas de duración
        empirical_duration = float(np.mean(absorption_times))
        empirical_duration_std = float(np.std(absorption_times, ddof=1)) if n_paths > 1 else 0.0
        empirical_duration_se = empirical_duration_std / np.sqrt(n_paths)
        ci_duration = (
            empirical_duration - 1.96 * empirical_duration_se,
            empirical_duration + 1.96 * empirical_duration_se
        )

        # Calcular estadísticas de ruina (tocar L antes que U)
        # Solo tiene sentido si fue absorbido y tocó L
        ruined = np.where(
            has_out,
            paths_array[np.arange(n_paths), first_out_idx] <= L,
            False
        )
        empirical_ruin = float(np.mean(ruined))
        empirical_ruin_std = float(np.std(ruined, ddof=1)) if n_paths > 1 else 0.0
        empirical_ruin_se = empirical_ruin_std / np.sqrt(n_paths)
        ci_ruin = (
            empirical_ruin - 1.96 * empirical_ruin_se,
            empirical_ruin + 1.96 * empirical_ruin_se
        )

        return {
            "empirical_duration": empirical_duration,
            "empirical_duration_se": empirical_duration_se,
            "duration_ci_95": ci_duration,
            "empirical_ruin": empirical_ruin,
            "empirical_ruin_se": empirical_ruin_se,
            "ruin_ci_95": ci_ruin,
            "unabsorbed_ratio": unabsorbed_ratio,
            "total_paths": n_paths,
            "total_steps_simulated": n_steps
        }
