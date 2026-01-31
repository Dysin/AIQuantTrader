'''
@Desc:   
@Author: Dysin
@Date:   2026/1/27
'''
import pandas as pd
from datetime import datetime

class StockTradeCalculator:
    """
    股票单笔交易收益计算器

    用于计算在给定买入时间、卖出时间和股票数量的情况下，
    考虑买卖手续费、印花税、资金利息后的实际收益、收益率和年化收益。
    """
    def __init__(
        self,
        df: pd.DataFrame,
        fee_buy: float = 0.0003,
        fee_sell: float = 0.0003,
        stamp_tax: float = 0.001,
        min_fee: float = 5.0,
        annual_interest_rate: float = 0.03
    ):
        '''
        初始化交易计算器
        :param df: 股票历史数据，索引为 datetime，必须包含 'close' 列
        :param fee_buy: 买入手续费比例（如 0.03% → 0.0003）
        :param fee_sell: 卖出手续费比例（如 0.03% → 0.0003）
        :param stamp_tax: 卖出印花税比例（如 0.1% → 0.001）
        :param min_fee: 最小手续费金额（元）
        :param annual_interest_rate: 买入资金年化利率，用于计算持仓利息成本
        '''
        # 对历史数据按时间排序
        self.df = df.sort_index()
        self.fee_buy = fee_buy
        self.fee_sell = fee_sell
        self.stamp_tax = stamp_tax
        self.min_fee = min_fee
        self.annual_interest_rate = annual_interest_rate

    # ------------------------
    # 内部工具函数
    # ------------------------
    def _calc_fee(self, amount, rate):
        """
        计算手续费，考虑最小手续费限制

        :param amount: 成交金额
        :param rate: 手续费比例
        :return: 手续费金额
        """
        return max(amount * rate, self.min_fee)

    def _days_between(self, start, end):
        """
        计算两个日期之间的天数差

        :param start: 起始日期 datetime
        :param end: 结束日期 datetime
        :return: 天数整数
        """
        return (end - start).days

    # ------------------------
    # 核心计算函数
    # ------------------------
    def calculate_trade(
        self,
        buy_time: datetime,
        sell_time: datetime,
        shares: int
    ):
        """
        给定买入时间 & 卖出时间，计算完整交易结果

        :param buy_time: 买入时间
        :param sell_time: 卖出时间
        :param shares: 买入数量（股数）
        :return: dict, 包含买卖价格、手续费、印花税、利息、净收益、收益率、年化收益等
        """

        # 获取买入价格（收盘价）
        buy_price = self.df.loc[buy_time, "close"]
        # 获取卖出价格（收盘价）
        sell_price = self.df.loc[sell_time, "close"]

        # 买入总金额
        buy_amount = buy_price * shares
        # 卖出总金额
        sell_amount = sell_price * shares

        # 计算买入手续费
        buy_fee = self._calc_fee(buy_amount, self.fee_buy)
        # 计算卖出手续费
        sell_fee = self._calc_fee(sell_amount, self.fee_sell)

        # 卖出印花税（只在卖出时收取）
        stamp_tax = sell_amount * self.stamp_tax

        # 计算持仓天数
        holding_days = self._days_between(buy_time, sell_time)
        # 资金占用利息成本（按天计算）
        interest_cost = buy_amount * self.annual_interest_rate * holding_days / 365

        # 总成本 = 买入金额 + 买入手续费 + 利息成本
        total_cost = buy_amount + buy_fee + interest_cost
        # 卖出到账金额 = 卖出金额 - 卖出手续费 - 印花税
        net_income = sell_amount - sell_fee - stamp_tax

        # 实际利润
        profit = net_income - total_cost
        # 收益率
        return_rate = profit / total_cost

        # 年化收益率（考虑持仓天数）
        annualized_return = (
            (1 + return_rate) ** (365 / holding_days) - 1
            if holding_days > 0 else 0
        )

        # 返回详细交易信息
        return {
            "buy_price": buy_price,                # 买入价格
            "sell_price": sell_price,              # 卖出价格
            "shares": shares,                      # 股票数量
            "holding_days": holding_days,          # 持仓天数
            "buy_amount": buy_amount,              # 买入金额
            "sell_amount": sell_amount,            # 卖出金额
            "buy_fee": buy_fee,                    # 买入手续费
            "sell_fee": sell_fee,                  # 卖出手续费
            "stamp_tax": stamp_tax,                # 卖出印花税
            "interest_cost": interest_cost,        # 持仓利息成本
            "total_cost": total_cost,              # 总成本
            "net_income": net_income,              # 卖出到账金额
            "profit": profit,                      # 实际利润
            "return_rate": return_rate,            # 收益率
            "annualized_return": annualized_return # 年化收益率
        }
