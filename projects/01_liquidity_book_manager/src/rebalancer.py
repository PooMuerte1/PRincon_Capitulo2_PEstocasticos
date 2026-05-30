import numpy as np
from typing import Dict, Any, Tuple
from .metrics import BinLiquidityMetrics

class BinLiquidityRebalancer:
    """
    Optimizador cuantitativo de rangos de liquidez.
    Resuelve la frontera óptima de Trade-off entre densidad de liquidez
    (comisiones por paso) y costos operativos de rebalanceo (fees de gas de Avalanche).
    Soporta tanto el modelo de comisiones Idealista como el Realista (Volume-Share).
    """
    def __init__(self):
        self.metrics_calculator = BinLiquidityMetrics()

    def calculate_net_return_rate(
        self,
        width: int,
        p: float,
        capital: float,
        base_fee_rate: float,
        gas_fee: float,
        dt_years: float = 0.0,
        expected_volume_per_minute: float = 0.0,
        pool_bin_tvl: float = 100000.0,
        fee_model: str = "realistic"
    ) -> Tuple[float, float, float]:
        """
        Calcula la tasa de retorno neta esperada por paso para un ancho de rango dado.

        Args:
            width: Ancho total del rango de bins (U - L). Debe ser par.
            p: Probabilidad de subir un bin.
            capital: Capital total provisto (en USD).
            base_fee_rate: Tasa de comisión base por unidad de liquidez.
            gas_fee: Costo de transacción de gas para rebalanceo.
            dt_years: Paso de tiempo local en fracción de año.
            expected_volume_per_minute: Volumen de trading esperado del pool por minuto en USD.
            pool_bin_tvl: Liquidez de competencia promedio en el bin activo en USD.
            fee_model: "idealistic" (comisiones fijas artificiales) o "realistic" (volume-share).

        Returns:
            net_return_rate: Tasa de retorno neta por paso.
            expected_duration: Pasos esperados hasta salir del rango (m_k).
            gross_fees: Comisiones totales brutas esperadas acumuladas antes de salir.
        """
        if width <= 1:
            return -999999.0, 0.0, 0.0

        # Asumimos que colocamos el precio en el centro exacto del rango
        L = 0
        U = width
        k = width // 2

        # Calcular duración esperada m_k
        expected_duration = self.metrics_calculator.calculate_theoretical_duration(k, L, U, p)

        if expected_duration <= 0:
            return -999999.0, 0.0, 0.0

        if fee_model == "realistic":
            # Paso de tiempo en minutos: dt_years * (365 * 24 * 60)
            dt_minutes = dt_years * 525600.0
            
            # Volumen esperado por paso = volumen por minuto * minutos por paso
            expected_volume_per_step = expected_volume_per_minute * dt_minutes
            
            # Comisiones totales generadas por el pool en este paso discreto
            pool_fees_per_step = expected_volume_per_step * base_fee_rate
            
            # Nuestra liquidez depositada en el bin activo: capital / width
            c_bin = capital / width
            
            # Nuestra fracción de participación del bin
            share = c_bin / (pool_bin_tvl + c_bin)
            
            # Comisiones brutas que ganamos en este paso
            gross_fee_per_step = pool_fees_per_step * share
        else:
            # Modelo idealista antiguo (fake)
            liquidity_per_bin = capital / width
            gross_fee_per_step = liquidity_per_bin * base_fee_rate

        # Comisiones totales esperadas antes de salir
        gross_fees = expected_duration * gross_fee_per_step

        # Retorno Neto Esperado (fees ganados - gas del rebalanceo final)
        net_return = gross_fees - gas_fee

        # Tasa de retorno neta por paso (net_return / expected_duration)
        net_return_rate = net_return / expected_duration

        return net_return_rate, expected_duration, gross_fees

    def optimize_range(
        self,
        p: float,
        capital: float,
        base_fee_rate: float,
        gas_fee: float,
        min_width: int = 2,
        max_width: int = 100,
        dt_years: float = 0.0,
        expected_volume_per_minute: float = 0.0,
        pool_bin_tvl: float = 100000.0,
        fee_model: str = "realistic"
    ) -> Dict[str, Any]:
        """
        Encuentra el ancho óptimo de rango (U - L) que maximiza la tasa de retorno neta.
        """
        best_width = None
        best_rate = -float("inf")
        best_duration = 0.0
        best_gross = 0.0

        widths = []
        rates = []
        durations = []

        # Recorremos anchos pares para asegurar posicionamiento centrado perfecto (k = width // 2)
        for w in range(min_width, max_width + 1):
            if w % 2 != 0:
                continue

            try:
                rate, dur, gross = self.calculate_net_return_rate(
                    width=w,
                    p=p,
                    capital=capital,
                    base_fee_rate=base_fee_rate,
                    gas_fee=gas_fee,
                    dt_years=dt_years,
                    expected_volume_per_minute=expected_volume_per_minute,
                    pool_bin_tvl=pool_bin_tvl,
                    fee_model=fee_model
                )
                widths.append(w)
                rates.append(rate)
                durations.append(dur)

                if rate > best_rate:
                    best_rate = rate
                    best_width = w
                    best_duration = dur
                    best_gross = gross
            except ValueError:
                continue

        return {
            "optimal_width": best_width,
            "optimal_net_return_rate": best_rate,
            "expected_duration_steps": best_duration,
            "expected_gross_fees": best_gross,
            "all_widths": widths,
            "all_rates": rates,
            "all_durations": durations
        }
