'''
@Desc:   回测引擎核心模块
            该模块负责在历史数据上模拟真实交易过程：
            - 账户资金变化
            - 持仓变化
            - 交易执行（含滑点、手续费）
            - 资产净值曲线

            设计目标：
            1. 尽量贴近真实交易
            2. 与策略、模型完全解耦
            3. 可平滑升级到实盘
@Author: Dysin
@Date:   2026/1/29
'''

from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Trade:
    '''
    单笔交易记录结构体（用于复盘、统计、分析）

    time: 交易发生时间（K线时间）
    price: 成交价格（已包含滑点）
    volume: 成交数量（股 / 币）
    direction: 交易方向
                1  -> 买入
               -1  -> 卖出
    fee: 手续费
    '''
    time: Any
    price: float
    volume: float
    direction: int
    fee: float

class BacktestEngine:
    '''
    回测引擎（Backtest Engine）

    核心职责：
    1. 管理账户（现金 / 持仓）
    2. 执行交易信号
    3. 计算手续费与滑点
    4. 维护资产净值曲线
    5. 输出回测结果
    '''

    def __init__(
        self,
        init_cash: float = 10000,
        fee_rate: float = 0.001,
        slippage: float = 0.0005,
    ):
        '''
        :param init_cash: 初始资金
        :param fee_rate: 手续费率（单边）
        :param slippage: 滑点比例（成交价偏移）
        '''
        # 账户状态（Account State）
        self.init_cash = init_cash  # 初始资金（用于计算收益率）
        self.cash = init_cash  # 当前可用现金
        self.position = 0.0  # 当前持仓数量
        self.position_price = 0.0  # 当前持仓均价

        # 交易参数（Market Friction）
        self.fee_rate = fee_rate  # 手续费
        self.slippage = slippage  # 滑点

        # 回测记录
        self.trades: List[Trade] = []  # 所有交易记录
        self.equity_curve: List[float] = []  # 资产净值曲线

    def _apply_slippage(self, price: float, direction: int) -> float:
        '''
        根据交易方向施加滑点

        买入（direction=1）：
            实际成交价 > 市场价

        卖出（direction=-1）：
            实际成交价 < 市场价
        '''
        if direction == 1:
            return price * (1 + self.slippage)
        else:
            return price * (1 - self.slippage)

    def _calc_fee(self, turnover: float) -> float:
        '''
        根据成交金额计算手续费
        :param turnover : 成交额 = 成交价 × 成交量
        '''
        return turnover * self.fee_rate

    def execute_trade(self, time, price: float, signal: int):
        '''
        执行交易信号（全仓模式）
        :param time:
        :param price:
        :param signal:
                1  -> 全仓买入
               -1  -> 全仓卖出
                0  -> 不操作
        :return:
        '''
        # 买入
        if signal == 1 and self.cash > 0:
            # 应用滑点后的成交价
            exec_price = self._apply_slippage(price, 1)
            # 可买数量 = 现金 / 成交价
            volume = self.cash / exec_price
            # 成交额
            turnover = volume * exec_price
            # 手续费
            fee = self._calc_fee(turnover)

            # 更新账户状态
            self.cash -= (turnover + fee)
            self.position += volume
            self.position_price = exec_price

            # 记录交易
            self.trades.append(
                Trade(time, exec_price, volume, 1, fee)
            )

        # 卖出
        elif signal == -1 and self.position > 0:
            exec_price = self._apply_slippage(price, -1)

            turnover = self.position * exec_price
            fee = self._calc_fee(turnover)

            self.cash += (turnover - fee)
            self.position = 0
            self.position_price = 0

            self.trades.append(
                Trade(time, exec_price, 0, -1, fee)
            )

    def update_equity(self, price: float):
        '''
        计算当前总资产
            总资产 = 现金 + 持仓市值
        :param price:
        :return:
        '''
        equity = self.cash + self.position * price
        self.equity_curve.append(equity)

    def run(self, data, strategy):
        '''
        回测主入口
        :param data: DataFrame (index=time, 包含 Close)
        :param strategy: 策略对象，必须实现 generate_signal 方法
        :return:
        '''
        for time, row in data.iterrows():
            price = row['close']

            # 1.策略生成信号（只用当前及过去数据）
            signal = strategy.generate_signal(row)

            # 2.执行交易
            self.execute_trade(time, price, signal)

            # 3.更新资产
            self.update_equity(price)

        return self._summary()

    def _summary(self) -> Dict:
        '''
        汇总回测结果
        :return:
        '''
        total_return = self.equity_curve[-1] / self.init_cash - 1

        return {
            'init_cash': self.init_cash,
            'final_equity': self.equity_curve[-1],
            'total_return': total_return,
            'trade_count': len(self.trades),
            'equity_curve': self.equity_curve,
            'trades': self.trades,
        }