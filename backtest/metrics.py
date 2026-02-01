'''
@Desc:   
@Author: Dysin
@Date:   2026/1/31
'''

# backtest/metrics.py

import numpy as np
import pandas as pd
from typing import Dict


class PerformanceMetrics:
    """
    回测绩效评估类
    - 输入资产净值曲线
    - 输出常用量化绩效指标
    """

    def __init__(self, equity_series: pd.Series):
        """
        初始化绩效评估对象

        :param equity_series: 资产净值时间序列（index=time, value=equity）
        :return: None
        """
        self.equity = equity_series.sort_index()
        self.returns = self.equity.pct_change().dropna()

    # -------------------------------------------------
    def total_return(self) -> float:
        """
        计算总收益率

        :param name: None
        :return: 总收益率
        """
        return self.equity.iloc[-1] / self.equity.iloc[0] - 1

    # -------------------------------------------------
    def annual_return(self, periods_per_year: int = 252) -> float:
        """
        计算年化收益率（复利）

        :param periods_per_year: 每年周期数（日线=252，分钟线需调整）
        :return: 年化收益率
        """
        total_ret = self.total_return()
        n_periods = len(self.equity)
        return (1 + total_ret) ** (periods_per_year / n_periods) - 1

    # -------------------------------------------------
    def annual_volatility(self, periods_per_year: int = 252) -> float:
        """
        计算年化波动率

        :param periods_per_year: 每年周期数
        :return: 年化波动率
        """
        return self.returns.std() * np.sqrt(periods_per_year)

    # -------------------------------------------------
    def sharpe_ratio(
        self,
        risk_free_rate: float = 0.0,
        periods_per_year: int = 252,
    ) -> float:
        """
        计算 Sharpe Ratio

        :param risk_free_rate: 无风险利率（年化）
        :param periods_per_year: 每年周期数
        :return: Sharpe 比率
        """
        rf_per_period = risk_free_rate / periods_per_year
        excess_return = self.returns - rf_per_period
        return np.sqrt(periods_per_year) * excess_return.mean() / excess_return.std()

    # -------------------------------------------------
    def max_drawdown(self) -> float:
        """
        计算最大回撤（MDD）

        :param name: None
        :return: 最大回撤（正值）
        """
        cumulative_max = self.equity.cummax()
        drawdown = (cumulative_max - self.equity) / cumulative_max
        return drawdown.max()

    # -------------------------------------------------
    def win_rate(self) -> float:
        """
        计算胜率（基于周期收益）

        :param name: None
        :return: 胜率
        """
        return (self.returns > 0).sum() / len(self.returns)

    # -------------------------------------------------
    def calmar_ratio(self) -> float:
        """
        计算 Calmar Ratio

        :param name: None
        :return: Calmar Ratio
        """
        mdd = self.max_drawdown()
        if mdd == 0:
            return np.nan
        return self.annual_return() / mdd

    # -------------------------------------------------
    def summary(self) -> Dict:
        """
        汇总所有绩效指标

        :param name: None
        :return: dict
        """
        return {
            "total_return": self.total_return(),
            "annual_return": self.annual_return(),
            "annual_volatility": self.annual_volatility(),
            "sharpe_ratio": self.sharpe_ratio(),
            "max_drawdown": self.max_drawdown(),
            "win_rate": self.win_rate(),
            "calmar_ratio": self.calmar_ratio(),
        }
