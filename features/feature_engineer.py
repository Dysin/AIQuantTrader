'''
@Desc:   特征工程
@Author: Dysin
@Date:   2026/3/13
'''
import os.path

import pandas as pd
import numpy as np
import mplfinance as mpf
from data.data_utils import DataUtils

class FeatureEngineer(DataUtils):
    """
    特征工程模块（Feature Engineering）
    作用：
    1. 从原始行情数据生成特征
    2. 计算技术指标
    3. 生成机器学习输入变量
    4. 清洗缺失值

    输入数据要求：
        DataFrame index = datetime
        必须包含列：
            open
            high
            low
            close
            volume
    """

    def __init__(self, config=None):
        """
        初始化特征工程模块
        :param config: 特征配置（可选）
        """
        super().__init__()
        self.config = config

    # ===============================
    # 主入口
    # ===============================
    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        生成完整特征集合
        :param df: 原始行情数据
        :return: 包含特征的新 DataFrame
        """
        df = df.copy()
        # 基础特征
        df = self._add_returns(df)
        # 趋势特征
        df = self._add_moving_averages(df)
        # 波动率特征
        df = self._add_volatility(df)
        # 动量特征
        df = self._add_momentum(df)
        # 技术指标
        df = self._add_rsi(df)
        df = self._add_macd(df)
        # 统计特征
        df = self._add_rolling_features(df)
        # 清理缺失值
        df = df.dropna()
        return df

    def polt_features(
            self,
            df: pd.DataFrame,
            name: str=None
    ):
        path_img = os.path.join(
            self.pm.images,
            "stock",
            f"kline_{name}.png"
        )
        mc = mpf.make_marketcolors(
            up='red',  # 上涨K线
            down='green',  # 下跌K线
            edge='inherit',
            wick='inherit',
            volume='inherit'
        )
        style = mpf.make_mpf_style(
            facecolor='white',  # 图表背景
            figcolor='white',  # 整个画布背景
            gridstyle = '--',
            gridcolor = 'gray',
            marketcolors=mc
        )
        df_kilne = df.tail(100)
        mpf.plot(
            df_kilne,
            type="candle",
            volume=True,
            mav=(5, 10, 20),
            mavcolors=['red', 'blue', 'orange'],
            style=style,
            figsize=(16, 9),
            title=f"{name} K-Line",
            tight_layout=True,  # 自动调整布局
            scale_padding={'top': 5},  # 增加顶部填充，给标题留空间
            ylabel="Price",
            ylabel_lower="Volume",
            savefig=dict(
                fname=path_img,
                dpi=600,
                bbox_inches="tight"
            )
        )

        path_img = os.path.join(
            self.pm.images,
            "stock",
            f"macd_{name}.png"
        )
        colors = ['red' if v >= 0 else 'green' for v in df_kilne['macd_hist']]
        apds = [
            mpf.make_addplot(df_kilne['macd'], panel=1, color='blue'),
            mpf.make_addplot(df_kilne['macd_signal'], panel=1, color='orange'),
            mpf.make_addplot(
                df_kilne['macd_hist'],
                type='bar',
                panel=1,
                color=colors
            )
        ]
        mpf.plot(
            df_kilne,
            type='candle',
            volume=False,
            addplot=apds,
            style=style,
            figsize=(16, 9),
            title=f"{name} MACD",
            tight_layout=True,  # 自动调整布局
            scale_padding={'top': 5},  # 增加顶部填充，给标题留空间
            ylabel="Price",
            ylabel_lower="Volume",
            savefig=dict(
                fname=path_img,
                dpi=600,
                bbox_inches="tight"
            )
        )

    # ===============================
    # 1. 收益率特征
    # ===============================
    def _add_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        添加收益率特征
        financial meaning:
        收益率是金融时间序列中最基础的特征
        """
        # 单期收益率
        df["return_1"] = df["close"].pct_change()
        # 多期收益率
        df["return_5"] = df["close"].pct_change(5)
        df["return_10"] = df["close"].pct_change(10)
        # 对数收益率
        df["log_return"] = np.log(df["close"] / df["close"].shift(1))
        return df

    # ===============================
    # 2. 移动平均
    # ===============================
    def _add_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        添加移动平均特征
        用于捕捉趋势
        """
        df["ma5"] = df["close"].rolling(5).mean()
        df["ma10"] = df["close"].rolling(10).mean()
        df["ma20"] = df["close"].rolling(20).mean()
        # 均线差
        df["ma_diff"] = df["ma5"] - df["ma20"]
        return df

    # ===============================
    # 3. 波动率特征
    # ===============================
    def _add_volatility(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算波动率

        金融含义：
        波动率代表风险水平
        """

        df["volatility_5"] = df["return_1"].rolling(5).std()
        df["volatility_10"] = df["return_1"].rolling(10).std()

        return df

    # ===============================
    # 4. 动量特征
    # ===============================
    def _add_momentum(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算动量指标
        """

        df["momentum_5"] = df["close"] - df["close"].shift(5)
        df["momentum_10"] = df["close"] - df["close"].shift(10)

        return df

    # ===============================
    # 5. RSI 指标
    # ===============================
    def _add_rsi(self, df: pd.DataFrame, period=14) -> pd.DataFrame:
        """
        RSI (Relative Strength Index)

        衡量超买 / 超卖
        """

        delta = df["close"].diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()

        rs = avg_gain / avg_loss

        df["rsi"] = 100 - (100 / (1 + rs))

        return df

    # ===============================
    # 6. MACD
    # ===============================
    def _add_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        MACD 指标
        """
        ema12 = df["close"].ewm(span=12).mean()
        ema26 = df["close"].ewm(span=26).mean()

        df["macd"] = ema12 - ema26
        df["macd_signal"] = df["macd"].ewm(span=9).mean()
        df["macd_hist"] = df["macd"] - df["macd_signal"]
        return df

    # ===============================
    # 7. Rolling统计特征
    # ===============================
    def _add_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        滚动统计特征
        """

        df["rolling_max_10"] = df["close"].rolling(10).max()
        df["rolling_min_10"] = df["close"].rolling(10).min()

        df["price_position"] = (
            (df["close"] - df["rolling_min_10"]) /
            (df["rolling_max_10"] - df["rolling_min_10"])
        )

        return df