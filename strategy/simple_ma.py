'''
@Desc:   5 日均线上穿 → 买入，下穿 → 卖出
@Author: Dysin
@Date:   2026/1/31
'''

# strategy/simple_ma_strategy.py

class SimpleMAStrategy:
    def __init__(self, window=3):
        self.window = window
        self.prices = []

    def generate_signal(self, row):
        """
        生成交易信号
        return:
            1  -> 买入
           -1  -> 卖出
            0  -> 不操作
        """
        self.prices.append(row["close"])

        # 数据不够，不交易
        if len(self.prices) < self.window:
            return 0

        ma = sum(self.prices[-self.window:]) / self.window

        if row["close"] > ma:
            return 1
        elif row["close"] < ma:
            return -1
        return 0
