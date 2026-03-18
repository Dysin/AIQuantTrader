'''
@Desc:   选股工具
@Author: Dysin
@Date:   2026/3/18
'''

import pandas as pd

class StockSelection:
    """
    股票选择模块（Stock Selector）

    功能：
    1. 输入多股票行情数据
    2. 基于不同周期（短/中/长）进行选股
    3. 输出候选股票列表（按评分排序）

    使用场景：
    - 多标的策略
    - 量化选股
    - AI选股输入
    """
    def __init__(self, data: dict):
        """
        初始化选股器

        :param data:
            dict[str, pd.DataFrame]
            key = 股票代码
            value = K线数据（必须包含 close）
        """
        self.data = data

    def select_short_term(self, top_n=5) -> pd.DataFrame:
        """
        Desc
        短期选股（偏动量 + 超跌反弹）

        核心逻辑：
        1. 计算短期收益率（5日）
        2. 计算 RSI（判断是否超卖）
        3. 综合评分 = 动量 + 反转信号

        :param top_n: 选出前 N 个股票
        :return: DataFrame（排序结果）
        """

        results = []

        for symbol, df in self.data.items():

            if len(df) < 20:
                continue

            df = df.copy()

            # ===== 短期收益率（动量）=====
            df["ret_5"] = df["close"].pct_change(5)

            # ===== RSI =====
            delta = df["close"].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)

            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()

            rs = avg_gain / avg_loss
            df["rsi"] = 100 - (100 / (1 + rs))

            latest = df.iloc[-1]

            # ===== 评分逻辑 =====
            score = (
                    latest["ret_5"] * 0.7 +  # 动量
                    (30 - latest["rsi"]) * 0.3  # 超卖（越低越好）
            )

            results.append({
                "symbol": symbol,
                "score": score,
                "ret_5": latest["ret_5"],
                "rsi": latest["rsi"]
            })

        result_df = pd.DataFrame(results).sort_values(
            by="score",
            ascending=False
        )

        return result_df.head(top_n)

    def select_mid_term(self, top_n=5) -> pd.DataFrame:
        """
        Desc
        中期选股（趋势跟踪）

        核心逻辑：
        1. 均线系统（MA20 / MA60）
        2. 趋势强度（价格位置）
        3. 波动率过滤

        :param top_n: 返回前 N 个股票
        :return: DataFrame
        """

        results = []

        for symbol, df in self.data.items():

            if len(df) < 60:
                continue

            df = df.copy()

            # ===== 均线 =====
            df["ma20"] = df["close"].rolling(20).mean()
            df["ma60"] = df["close"].rolling(60).mean()

            # ===== 趋势强度 =====
            df["trend"] = df["ma20"] - df["ma60"]

            # ===== 波动率 =====
            df["volatility"] = df["close"].pct_change().rolling(20).std()

            latest = df.iloc[-1]

            # ===== 筛选条件 =====
            if latest["ma20"] < latest["ma60"]:
                continue  # 非上升趋势

            # ===== 评分 =====
            score = (
                    latest["trend"] * 0.6 +
                    (1 / latest["volatility"]) * 0.4
            )

            results.append({
                "symbol": symbol,
                "score": score,
                "trend": latest["trend"],
                "volatility": latest["volatility"]
            })

        result_df = pd.DataFrame(results).sort_values(
            by="score",
            ascending=False
        )

        return result_df.head(top_n)

    def select_long_term(self, top_n=5) -> pd.DataFrame:
        """
        Desc
        长期选股（趋势 + 稳定性）

        核心逻辑：
        1. 长期收益率（60日 / 120日）
        2. 最大回撤（风险控制）
        3. 稳定性（波动率）

        :param top_n: 返回前 N 个股票
        :return: DataFrame
        """

        results = []

        for symbol, df in self.data.items():

            if len(df) < 120:
                continue

            df = df.copy()

            # ===== 长期收益 =====
            df["ret_60"] = df["close"].pct_change(60)
            df["ret_120"] = df["close"].pct_change(120)

            # ===== 最大回撤 =====
            rolling_max = df["close"].cummax()
            drawdown = (df["close"] - rolling_max) / rolling_max
            max_dd = drawdown.min()

            # ===== 波动率 =====
            volatility = df["close"].pct_change().std()

            latest = df.iloc[-1]

            # ===== 评分 =====
            score = (
                    latest["ret_120"] * 0.5 +
                    latest["ret_60"] * 0.3 -
                    abs(max_dd) * 0.2
            )

            results.append({
                "symbol": symbol,
                "score": score,
                "ret_120": latest["ret_120"],
                "ret_60": latest["ret_60"],
                "max_dd": max_dd
            })

        result_df = pd.DataFrame(results).sort_values(
            by="score",
            ascending=False
        )

        return result_df.head(top_n)