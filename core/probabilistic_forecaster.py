"""Probabilistic Forecasting for Financial Predictions"""
import numpy as np
from typing import Dict, List
from dataclasses import dataclass
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Forecast:
    """Probabilistic forecast with confidence intervals"""
    mean: float
    median: float
    std: float
    ci_lower: float
    ci_upper: float
    percentile_25: float
    percentile_75: float
    timestamp: str
    model: str


class ProbabilisticForecaster:
    """Forecaster using probabilistic methods"""

    def __init__(self, lookback_period: int = 60, confidence_level: float = 0.95):
        self.lookback_period = lookback_period
        self.confidence_level = confidence_level
        self.historical_data: List[float] = []
        logger.info(f"Forecaster initialized")

    def add_data_point(self, value: float):
        """Add historical data point"""
        self.historical_data.append(value)
        if len(self.historical_data) > self.lookback_period * 2:
            self.historical_data = self.historical_data[-self.lookback_period*2:]

    def forecast_monte_carlo(self, steps: int = 30, n_simulations: int = 1000) -> Forecast:
        """Monte Carlo probabilistic forecast"""
        if len(self.historical_data) < 10:
            return self._fallback_forecast()

        data = np.array(self.historical_data[-self.lookback_period:])
        mean = np.mean(data)
        std = np.std(data)

        simulations = np.random.normal(mean, std, (n_simulations, steps))
        last_price = self.historical_data[-1]
        cumulative_sim = np.cumsum(np.diff(simulations, axis=1, prepend=last_price), axis=1)
        final_values = cumulative_sim[:, -1]

        return Forecast(
            mean=np.mean(final_values),
            median=np.median(final_values),
            std=np.std(final_values),
            ci_lower=np.percentile(final_values, (1 - self.confidence_level) / 2 * 100),
            ci_upper=np.percentile(final_values, (1 + self.confidence_level) / 2 * 100),
            percentile_25=np.percentile(final_values, 25),
            percentile_75=np.percentile(final_values, 75),
            timestamp=datetime.now().isoformat(),
            model="monte_carlo"
        )

    def forecast_ensemble(self, steps: int = 30) -> Forecast:
        """Ensemble probabilistic forecast"""
        mc_forecast = self.forecast_monte_carlo(steps)
        return mc_forecast

    def _fallback_forecast(self) -> Forecast:
        """Fallback forecast when insufficient data"""
        if len(self.historical_data) > 0:
            last = self.historical_data[-1]
            return Forecast(
                mean=last, median=last, std=0.0,
                ci_lower=last * 0.95, ci_upper=last * 1.05,
                percentile_25=last * 0.98, percentile_75=last * 1.02,
                timestamp=datetime.now().isoformat(),
                model="fallback"
            )
        return Forecast(
            mean=0.0, median=0.0, std=0.0,
            ci_lower=-1.0, ci_upper=1.0,
            percentile_25=-0.5, percentile_75=0.5,
            timestamp=datetime.now().isoformat(),
            model="fallback"
        )
