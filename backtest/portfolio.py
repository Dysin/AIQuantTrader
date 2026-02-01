'''
@Desc:  账户 & 持仓 & 资产曲线 & 交易统计
            1.账户状态（现金 / 市值）
            2.持仓管理
            3.资产净值时间序列
@Author: Dysin
@Date:   2026/1/29
'''

from typing import Dict, List
import pandas as pd


class Portfolio:
    '''
    资产组合管理类
    - 管理账户资金
    - 记录资产净值变化
    - 提供回测统计所需数据
    '''

    def __init__(self, init_cash: float = 1_000_000):
        '''
        初始化投资组合
        :param init_cash: 初始资金
        :return: None
        '''
        self.init_cash = init_cash

        # 当前账户状态
        self.cash = init_cash
        self.position = 0.0          # 持仓数量
        self.position_price = 0.0    # 持仓均价

        # 资产曲线
        self.equity_curve: List[float] = []

        # 时间索引
        self.time_index: List = []

        # 交易记录
        self.trades: List[Dict] = []

    # -------------------------------------------------
    def update_position(
        self,
        time,
        direction: int,
        price: float,
        volume: float,
        fee: float,
    ):
        '''
        更新持仓状态（买入 / 卖出后调用）
        :param time: 交易时间
        :param direction: 交易方向（1=买入, -1=卖出）
        :param price: 成交价格
        :param volume: 成交数量
        :param fee: 手续费
        :return: None
        '''

        # ===== 买入 =====
        if direction == 1:
            cost = price * volume + fee
            self.cash -= cost
            self.position += volume
            self.position_price = price

        # ===== 卖出 =====
        elif direction == -1:
            revenue = price * self.position - fee
            self.cash += revenue
            self.position = 0.0
            self.position_price = 0.0

        # ===== 记录交易 =====
        self.trades.append(
            {
                'time': time,
                'direction': direction,
                'price': price,
                'volume': volume,
                'fee': fee,
                'cash_after': self.cash,
            }
        )

    # -------------------------------------------------
    def update_equity(self, time, market_price: float):
        '''
        更新当前时刻的资产净值
        :param time: 当前时间
        :param market_price: 当前市场价格
        :return: None
        '''
        equity = self.cash + self.position * market_price
        self.equity_curve.append(equity)
        self.time_index.append(time)

    # -------------------------------------------------
    def current_equity(self, market_price: float) -> float:
        '''
        获取当前总资产
        :param market_price: 当前市场价格
        :return: 当前资产净值
        '''
        return self.cash + self.position * market_price

    # -------------------------------------------------
    def get_equity_series(self) -> pd.Series:
        '''
        获取资产净值时间序列（用于绩效分析）
        :param name: None
        :return: pandas.Series
        '''
        return pd.Series(
            self.equity_curve,
            index=self.time_index,
            name='equity',
        )

    # -------------------------------------------------
    def get_trade_dataframe(self) -> pd.DataFrame:
        '''
        获取交易记录 DataFrame
        :param name: None
        :return: pandas.DataFrame
        '''
        return pd.DataFrame(self.trades)

    # -------------------------------------------------
    def summary(self) -> Dict:
        '''
        获取投资组合总结信息
        :param name: None
        :return: dict
        '''
        final_equity = self.equity_curve[-1] if self.equity_curve else self.init_cash
        total_return = final_equity / self.init_cash - 1

        return {
            'init_cash': self.init_cash,
            'final_equity': final_equity,
            'total_return': total_return,
            'trade_count': len(self.trades),
        }
