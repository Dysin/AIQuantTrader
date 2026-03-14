'''
@Desc:   
@Author: Dysin
@Date:   2026/1/31
'''

# backtest/metrics.py

import numpy as np
import pandas as pd
from typing import Dict
from utils.logger import get_logger
logger = get_logger(__name__)

class PerformanceMetrics:
    """
    回测绩效评估类 (Performance Metrics)

    功能：
    输入：
        资产净值时间序列（equity curve）

    输出：
        常用量化策略评价指标，例如：
        - 总收益率
        - 年化收益率
        - 年化波动率
        - Sharpe Ratio
        - 最大回撤
        - 胜率
        - Calmar Ratio

    作用：
        在量化交易系统中，用于对回测结果进行绩效评估。
    """
    def __init__(self, equity_series: pd.Series):
        """
        初始化绩效评估对象

        :param equity_series : pd.Series
            资产净值时间序列
            index : 时间 (datetime)
            value : 账户净值 (equity)

        例：
            2024-01-01    100000
            2024-01-02    101200
            2024-01-03    100800

        :param risk_free_rate: (float) 年化无风险利率
            例如：美国国债 ≈ 0.03
        """

        # 按时间排序（防止时间乱序）
        self.equity = equity_series.sort_index()

        # 计算每个周期收益率
        # pct_change() = (today - yesterday) / yesterday
        # dropna() 去掉第一行 NaN
        self.returns = self.equity.pct_change().dropna()
        
        # 无风险利率
        self.risk_free_rate = 0.02

    # -------------------------------------------------
    def total_return(self) -> float:
        """
        计算总收益率

        公式：
            Total Return = Final Equity / Initial Equity - 1

        示例：
            初始资金 = 100000
            最终资金 = 150000

            total_return = 150000 / 100000 - 1
                         = 0.5
                         = 50%

        :return: 总收益率
        """
        # iloc[0]  = 第一个净值
        # iloc[-1] = 最后一个净值
        return self.equity.iloc[-1] / self.equity.iloc[0] - 1

    # -------------------------------------------------
    def annual_return(self, periods_per_year: int = 252) -> float:
        """
        计算年化收益率（复利）
            为什么要年化？
            不同回测周期必须统一比较
        公式：
            Annual Return = (1 + Total Return)^(年周期数 / 回测周期数) - 1
        例如：
            回测 100 天收益 20%
            年化收益 = (1.2)^(252 / 100) - 1

        :param periods_per_year: int
            每年交易周期数

            常见：
            日线   = 252
            小时线 = 252 * 6.5
            分钟线 = 252 * 6.5 * 60

        :return : float
            年化收益率
        """

        # 总收益率
        total_ret = self.total_return()

        # 回测周期数量
        n_periods = len(self.equity)

        # 复利年化公式
        return (1 + total_ret) ** (periods_per_year / n_periods) - 1

    # -------------------------------------------------
    def annual_volatility(self, periods_per_year: int = 252) -> float:
        """
        计算年化波动率
        波动率 = 收益率标准差
        年化公式：
            Annual Volatility = std(returns) * sqrt(periods_per_year)
        含义：
            衡量策略风险大小
        举例：
            日收益标准差 = 1%
            年化波动率 = 1% * sqrt(252) ≈ 15.87%

        :param periods_per_year: (int) 每年周期数
        :return: (float) 年化波动率
        """
        # returns.std() = 收益率标准差
        # sqrt(periods_per_year) = 年化调整
        return self.returns.std() * np.sqrt(periods_per_year)

    # -------------------------------------------------
    def sharpe_ratio(
        self,
        periods_per_year: int = 252,
    ) -> float:
        """
        计算 Sharpe Ratio（夏普比率）
        Sharpe Ratio 定义：
            Sharpe = (策略收益 - 无风险收益) / 收益波动率
        年化公式：
            Sharpe = sqrt(252) * mean(excess_return) / std(excess_return)
        含义：
            每承担 1 单位风险，可以获得多少超额收益。
        Sharpe ratio评价标准：
            Sharpe <= 0     很差
            Sharpe (0, 1]   一般
            Sharpe (1, 2]   好
            Sharpe (2, 3]   优秀
            Sharpe > 3      顶级策略

        :param periods_per_year: (int) 每年周期数
        :return: (float) Sharpe Ratio
        """
        # 将年化无风险利率转换为每周期利率
        rf_per_period = self.risk_free_rate / periods_per_year
        # 超额收益
        excess_return = self.returns - rf_per_period
        # 年化 Sharpe
        return np.sqrt(periods_per_year) * excess_return.mean() / excess_return.std()

    # -------------------------------------------------
    def sortino_ratio(
            self,
            periods_per_year: int = 252,
    ) -> float:
        """
        计算 Sortino Ratio（索提诺比率）
        Sortino Ratio 与 Sharpe Ratio 类似，
        但只考虑下行波动（亏损风险）。
        公式：
            Sortino =
            sqrt(periods_per_year) *
            mean(excess_return) /
            downside_std

        :param periods_per_year: 每年周期数，日线=252
        :return: (float) Sortino Ratio
        """
        # 每周期无风险利率
        rf_per_period = self.risk_free_rate / periods_per_year
        # 超额收益
        excess_return = self.returns - rf_per_period
        # 只保留负收益（下行风险）
        downside_returns = excess_return[excess_return < 0]
        # 如果没有下行波动
        if len(downside_returns) == 0: return np.nan
        # 下行标准差
        downside_std = downside_returns.std()
        # 年化 Sortino
        return np.sqrt(periods_per_year) * excess_return.mean() / downside_std

    # -------------------------------------------------
    def max_drawdown(self) -> float:
        """
        计算最大回撤（Maximum Drawdown, MDD）
        定义：
            从历史最高点到最低点的最大跌幅
        公式：
            Drawdown = (Peak - Equity) / Peak
        举例：
            100k -> 150k -> 90k
            回撤 = (150k - 90k) / 150k = 40%

        :return: (float) 最大回撤
        """
        # 历史最高净值曲线
        cumulative_max = self.equity.cummax()
        # 当前回撤
        drawdown = (cumulative_max - self.equity) / cumulative_max
        # 最大回撤
        return drawdown.max()

    # -------------------------------------------------
    def win_rate(self) -> float:
        """
        计算胜率
        定义：
            盈利周期数量 / 总周期数量
        例如：
            交易 100 天
            盈利 55 天
            win_rate = 55%
        注意：
            这里只是周期胜率，不一定等同于交易胜率

        :return: (float) 胜率
        """
        # returns > 0 表示盈利周期
        return (self.returns > 0).sum() / len(self.returns)

    # -------------------------------------------------
    def calmar_ratio(self) -> float:
        """
        计算 Calmar Ratio
        定义：
            Calmar = Annual Return / Max Drawdown
        含义：
            每承担1单位最大回撤风险，可以获得多少年化收益。
            它主要用于评估策略在承担回撤风险情况下获得收益的能力
        举例：
            年化收益 30%，最大回撤 10%，Calmar = 3
        一般经验值：
            Calmar Ratio <= 0.5     很差
            Calmar Ratio (0.5, 1]   一般
            Calmar Ratio (1, 2]     较好
            Calmar Ratio (2, 3]     优秀
            Calmar Ratio > 3        顶级策略

        :return: (float) Calmar Ratio
        """
        # 最大回撤
        mdd = self.max_drawdown()
        # 避免除0
        if mdd == 0:
            return np.nan
        # Calmar
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
            "sortino_ratio": self.sortino_ratio(),
            "max_drawdown": self.max_drawdown(),
            "win_rate": self.win_rate(),
            "calmar_ratio": self.calmar_ratio(),
        }
