import numpy as np
from typing import Dict, Any, Tuple
from .metrics import BinLiquidityMetrics

class BinLiquidityRebalancerWithSlippage:
    """
    Optimizador cuantitativo de rangos de liquidez con sensibilidad al deslizamiento (Slippage-Aware).
    Resuelve la frontera óptima de Trade-off incorporando el costo friccional de gas y 
    la pérdida directa por deslizamiento en cada rebalanceo de red.
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
        slippage_rate: float = 0.0,
        dt_years: float = 0.0,
        expected_volume_per_minute: float = 0.0,
        pool_bin_tvl: float = 100000.0,
        fee_model: str = "realistic"
    ) -> Tuple[float, float, float, float]:
        """
        Calcula la tasa de retorno neta esperada incorporando el deslizamiento por rebalanceo.
        """
        if width <= 1:
            return -999999.0, 0.0, 0.0, 0.0

        L = 0
        U = width
        k = width // 2

        # 1. Calcular la duración teórica esperada en pasos (m_k)
        expected_duration = self.metrics_calculator.calculate_theoretical_duration(k, L, U, p)

        if expected_duration <= 0:
            return -999999.0, 0.0, 0.0, 0.0

        # 2. Calcular las comisiones brutas esperadas antes de salir
        if fee_model == "realistic":
            dt_minutes = dt_years * 525600.0
            expected_volume_per_step = expected_volume_per_minute * dt_minutes
            pool_fees_per_step = expected_volume_per_step * base_fee_rate
            
            c_bin = capital / width
            share = c_bin / (pool_bin_tvl + c_bin)
            gross_fee_per_step = pool_fees_per_step * share
        else:
            liquidity_per_bin = capital / width
            gross_fee_per_step = liquidity_per_bin * base_fee_rate

        gross_fees = expected_duration * gross_fee_per_step

        # 3. Incorporar el costo friccional del swap de rebalanceo
        # El deslizamiento ocurre sobre el capital total rebalanceado
        slippage_loss = capital * slippage_rate

        # Retorno Neto Esperado (Fees ganados - Gas - Pérdida por Deslizamiento)
        net_return = gross_fees - gas_fee - slippage_loss

        # Tasa de retorno neta por paso discreto
        net_return_rate = net_return / expected_duration

        return net_return_rate, expected_duration, gross_fees, slippage_loss

    def optimize_range(
        self,
        p: float,
        capital: float,
        base_fee_rate: float,
        gas_fee: float,
        slippage_rate: float = 0.0,
        min_width: int = 2,
        max_width: int = 120,
        dt_years: float = 0.0,
        expected_volume_per_minute: float = 0.0,
        pool_bin_tvl: float = 100000.0,
        fee_model: str = "realistic"
    ) -> Dict[str, Any]:
        """
        Encuentra el ancho óptimo de rango (U - L) que maximiza la tasa de retorno neta,
        teniendo en cuenta la fricción del deslizamiento.
        """
        best_width = None
        best_rate = -float("inf")
        best_duration = 0.0
        best_gross = 0.0
        best_slippage_loss = 0.0

        widths = []
        all_rates = []

        for w in range(min_width, max_width + 1):
            if w % 2 != 0:
                continue

            try:
                rate, dur, gross, slip_loss = self.calculate_net_return_rate(
                    width=w,
                    p=p,
                    capital=capital,
                    base_fee_rate=base_fee_rate,
                    gas_fee=gas_fee,
                    slippage_rate=slippage_rate,
                    dt_years=dt_years,
                    expected_volume_per_minute=expected_volume_per_minute,
                    pool_bin_tvl=pool_bin_tvl,
                    fee_model=fee_model
                )
                widths.append(w)
                all_rates.append(rate)

                if rate > best_rate:
                    best_rate = rate
                    best_width = w
                    best_duration = dur
                    best_gross = gross
                    best_slippage_loss = slip_loss
            except ValueError:
                continue

        return {
            "optimal_width": best_width,
            "optimal_net_return_rate": best_rate,
            "expected_duration_steps": best_duration,
            "expected_gross_fees": best_gross,
            "expected_slippage_loss": best_slippage_loss,
            "all_widths": widths,
            "all_rates": all_rates
        }
