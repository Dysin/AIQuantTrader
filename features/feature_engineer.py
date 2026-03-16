'''
@Desc:   特征工程
@Author: Dysin
@Date:   2026/3/13
'''
import os.path

import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
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

    def __init__(self, df: pd.DataFrame):
        """
        初始化特征工程模块
        :param df: 原始行情数据
        """
        super().__init__()
        self.df = df.copy()

    # ===============================
    # 主入口
    # ===============================
    def generate_features(self):
        """
        生成完整特征集合

        :return: 包含特征的新 DataFrame
        """
        # 基础特征
        self._add_returns()
        # 趋势特征
        self._add_ma()
        # self._add_ema()
        self._add_sar()
        # 波动率特征
        self._add_volatility()
        self._add_bollinger(20)
        self._add_atr()
        # 动量特征
        self._add_momentum()
        # 成交量指标
        self._add_vwap()
        self._add_obv()
        # 震荡指标
        self._add_kdj()
        self._add_cci()
        # 技术指标
        self._add_rsi()
        self._add_macd()
        # 统计特征
        self._add_rolling_features()
        # 清理缺失值
        self.df.dropna()

    def plot_features(self, name: str=None, period: int=90):
        self.plot_trend_indicators(name, period)
        self.plot_bollinger_indicators(name, period)
        self.plot_momentum_indicators(name, period)
        self.plot_volatility_indicators(name, period)
        self.plot_oscillator_indicators(name, period)
        self.plot_volume_indicators(name, period)

    def plot_style(
            self,
            df,
            name,
            addplot,
            panel_ratios,
            bool_volume=True
    ):
        # 1. 样式与颜色配置
        mc = mpf.make_marketcolors(
            up='red',
            down='green',
            edge='inherit',
            wick='inherit',
            volume='inherit'
        )
        style = mpf.make_mpf_style(
            facecolor='white',
            gridstyle='--',
            gridcolor='gray',
            marketcolors=mc
        )
        # 3. 绘图 (注意：这里去掉了 title 参数，后面手动加)
        fig, axlist = mpf.plot(
            df,
            type="candle",
            volume=bool_volume,
            addplot=addplot,
            style=style,
            figsize=(18, sum(list(panel_ratios))),
            datetime_format='%Y-%m-%d',
            panel_ratios=panel_ratios,
            scale_padding=0,
            tight_layout=True,
            returnfig=True
        )

        # (1) 设置 X 轴左右顶格
        for ax in axlist:
            ax.grid(False)
            ax.xaxis.grid(True, linestyle='--', color='gray', alpha=0.5)  # 只绘制竖向网格线
            ax.set_xlim(-0.5, len(df) - 0.5)

        # (2) 在整个画布最上方添加标题
        fig.suptitle(f"{name} Stock Analysis", fontsize=20, y=0.98)

        # 设置Legend
        # 自动抓取所有 line 和 scatter 并显示 legend
        for ax in axlist:
            lines = ax.get_lines()
            labels = [
                line.get_label() for line in lines if line.get_label() != '_nolegend_'
            ]
            if labels:
                ax.legend(lines, labels, loc='upper left', frameon=False, fontsize=10)

        # for i, ax in enumerate(axlist):
        #     handles, labels = ax.get_legend_handles_labels()
        #     # 去重：防止同一个指标（如均线）出现多次
        #     unique_labels = dict(zip(labels, handles))
        #     # 正确过滤：只提取有效的 label 和对应的 handle
        #     final_data = [
        #         (l, h) for l, h in unique_labels.items() if l and not l.startswith("_")
        #     ]
        #
        #     if final_data:
        #         curr_labels, curr_handles = zip(*final_data)  # 解压回两个列表
        #         ax.legend(
        #             handles=curr_handles,
        #             labels=curr_labels,
        #             loc="upper left",
        #             # 方案 A：如果子图太扁，尝试放在图外右侧
        #             # bbox_to_anchor=(1.01, 1),
        #             # 方案 B：如果子图够宽，增加列数减少垂直占用
        #             ncol=min(len(curr_labels), 3),
        #             frameon=False,
        #             fontsize=8,  # 缩小字号
        #             labelspacing=0.2,  # 紧凑行间距
        #             handletextpad=0.5  # 图标与文字间距
        #         )
        return fig, axlist

    def plot_trend_indicators(self, name: str=None, period: int=90):
        """
        趋势指标
        :param name: 股票名
        :param period: 观察周期
        :return:
        """
        path_img = os.path.join(
            self.pm.images,
            "stock",
            f"technical_indicators_trend_{name}_{period}days.png"
        )
        df_plot = self.df.tail(period).copy()
        # 2. 配置 Addplots (确保 secondary_y=False)
        apds = [
            # Panel 0:
            # 均线MA
            mpf.make_addplot(df_plot['ma5'], panel=0, color='red', width=1.2),
            mpf.make_addplot(df_plot['ma10'], panel=0, color='blue', width=1.2),
            mpf.make_addplot(df_plot['ma20'], panel=0, color='orange', width=1.2),

            # SAR（scatter）
            mpf.make_addplot(
                df_plot['sar'],
                panel=0,
                type='scatter',
                marker='.',
                markersize=20,
                color='black'
            ),
        ]

        fig, axlist = self.plot_style(
            df=df_plot,
            name=name,
            addplot=apds,
            panel_ratios=(6, 2),
        )

        # K线层 (Panel 0)
        lines_main = axlist[0].get_lines()
        # MA
        line_ma5 = lines_main[0]  # 假设是 MA5
        line_ma10 = lines_main[1]
        line_ma20 = lines_main[2]

        # SAR scatter 手动创建 legend
        sar_handle = mlines.Line2D(
            [],
            [],
            color='black',
            marker='.',
            linestyle='None',
            markersize=6
        )
        axlist[0].legend(
            [line_ma5, line_ma10, line_ma20, sar_handle],  # MA + SAR
            ['MA5', 'MA10', 'MA20', 'SAR'],
            loc='upper left',
            frameon=False,
            fontsize=10,
            ncol=1
        )

        # 成交量层 (Panel 1)
        # axlist[1].legend(['Volume'], loc='upper left', frameon=False, fontsize=10)

        # 6. 保存并释放
        fig.savefig(path_img, dpi=300, bbox_inches="tight")
        plt.close(fig)

    def plot_bollinger_indicators(self, name: str=None, period: int=90):
        """
        趋势指标
        :param name: 股票名
        :param period: 观察周期
        :return:
        """
        path_img = os.path.join(
            self.pm.images,
            "stock",
            f"technical_indicators_bollinger_{name}_{period}days.png"
        )
        df_plot = self.df.tail(period).copy()
        # 2. 配置 Addplots (确保 secondary_y=False)
        apds = [
            # Panel 0:
            mpf.make_addplot(
                df_plot['bb_middle'],
                panel=0,
                color='black',
                width=1.2,
                label="BB Middle"
            ),
            mpf.make_addplot(
                df_plot['bb_upper'],
                panel=0,
                color='red',
                linestyle='dashed',
                width=0.8,
                label="BB Upper"
            ),
            mpf.make_addplot(
                df_plot['bb_lower'],
                panel=0,
                color='green',
                linestyle='dashed',
                width=0.8,
                label="BB Lower"
            ),
        ]

        fig, axlist = self.plot_style(
            df=df_plot,
            name=name,
            addplot=apds,
            panel_ratios=(6, 2),
        )

        # # K线层 (Panel 0)
        # lines_main = axlist[0].get_lines()
        # # MA
        # line_ma5 = lines_main[0]  # 假设是 MA5
        # line_ma10 = lines_main[1]
        # line_ma20 = lines_main[2]
        #
        # # SAR scatter 手动创建 legend
        # sar_handle = mlines.Line2D(
        #     [],
        #     [],
        #     color='black',
        #     marker='.',
        #     linestyle='None',
        #     markersize=6
        # )
        # axlist[0].legend(
        #     [line_ma5, line_ma10, line_ma20, sar_handle],  # MA + SAR
        #     ['MA5', 'MA10', 'MA20', 'SAR'],
        #     loc='upper left',
        #     frameon=False,
        #     fontsize=10,
        #     ncol=1
        # )

        # 成交量层 (Panel 1)
        # axlist[1].legend(['Volume'], loc='upper left', frameon=False, fontsize=10)

        # 6. 保存并释放
        fig.savefig(path_img, dpi=300, bbox_inches="tight")
        plt.close(fig)

    def plot_volatility_indicators(self, name: str=None, period: int=90):
        """
        波动率指标
        判断市场波动大小
        :param name:
        :param period:
        :return:
        """
        path_img = os.path.join(
            self.pm.images,
            "stock",
            f"technical_indicators_volatility_{name}_{period}days.png"
        )
        df_plot = self.df.tail(period).copy()
        # 2. 配置 Addplots (确保 secondary_y=False)
        apds = [
            # ATR
            mpf.make_addplot(
                df_plot['atr'],
                panel=1,
                color='black',
                width=1.2,
                label="ATR"
            ),
        ]

        fig, axlist = self.plot_style(
            df=df_plot,
            name=name,
            addplot=apds,
            panel_ratios=(6, 2),
            bool_volume=False
        )

        # 6. 保存并释放
        fig.savefig(path_img, dpi=300, bbox_inches="tight")
        plt.close(fig)

    def plot_momentum_indicators(self, name: str=None, period: int=90):
        """
        动量指标，判断上涨/下跌的速度和强度
        :param name: 股票名
        :param period: 观察周期
        :return:
        """
        path_img = os.path.join(
            self.pm.images,
            "stock",
            f"technical_indicators_momentum_{name}_{period}days.png"
        )
        df_plot = self.df.tail(period).copy()
        # MACD 柱状图颜色逻辑
        macd_colors = ['red' if v >= 0 else 'green' for v in df_plot['macd_hist']]
        # 2. 配置 Addplots (确保 secondary_y=False)
        apds = [
            # Panel 1: RSI 主线
            mpf.make_addplot(
                df_plot["rsi"],
                panel=1,
                color="purple",
                width=1.2,
                secondary_y=False,
                label="RSI"
            ),
            # 上阈值
            mpf.make_addplot(
                [70] * len(df_plot),
                panel=1,
                color="red",
                linestyle="dashed",
                width=0.8,
                secondary_y=False,
                label="Overbought(70)"
            ),
            # 下阈值
            mpf.make_addplot(
                [30] * len(df_plot),
                panel=1,
                color="green",
                linestyle="dashed",
                width=0.8,
                secondary_y=False,
                label="Oversold(30)"
            ),
            # Panel 2: MACD
            mpf.make_addplot(
                df_plot['macd'],
                panel=2,
                color='blue',
                width=1.2,
                secondary_y=False,
                label="MACD"
            ),
            mpf.make_addplot(
                df_plot['macd_signal'],
                panel=2,
                color='orange',
                width=1.2,
                secondary_y=False,
                label="Signal"
            ),
            mpf.make_addplot(
                df_plot['macd_hist'],
                type='bar',
                panel=2,
                color=macd_colors,
                alpha=0.6,
                secondary_y=False
            ),
        ]

        fig, axlist = self.plot_style(
            df=df_plot,
            name=name,
            addplot=apds,
            panel_ratios=(6, 2, 3),
            bool_volume=False
        )

        # 6. 保存并释放
        fig.savefig(path_img, dpi=300, bbox_inches="tight")
        plt.close(fig)

    def plot_oscillator_indicators(self, name: str = None, period: int = 90):
        """
        震荡指标，判断市场拐点
        :param name: 股票名
        :param period: 观察周期
        :return:
        """
        path_img = os.path.join(
            self.pm.images,
            "stock",
            f"technical_indicators_oscillator_{name}_{period}days.png"
        )
        df_plot = self.df.tail(period).copy()
        # MACD 柱状图颜色逻辑
        macd_colors = ['red' if v >= 0 else 'green' for v in df_plot['macd_hist']]
        # 2. 配置 Addplots (确保 secondary_y=False)
        apds = [
            # Panel 4: KDJ
            mpf.make_addplot(
                df_plot['k'],
                panel=1,
                color='blue',
                width=1.0,
                label="K"
            ),
            mpf.make_addplot(
                df_plot['d'],
                panel=1,
                color='orange',
                width=1.0,
                label="D"
            ),
            mpf.make_addplot(
                df_plot['j'],
                panel=1,
                color='green',
                width=1.0,
                label="J"
            ),
            # Panel 5: CCI
            mpf.make_addplot(
                df_plot['cci'],
                panel=2,
                color='black',
                width=1.2,
                label="CCI"
            ),
            mpf.make_addplot(
                [100] * len(df_plot),
                panel=2,
                color='red',
                linestyle='dashed',
                width=0.8,
                label="Overbought"
            ),
            mpf.make_addplot(
                [-100] * len(df_plot),
                panel=2,
                color='green',
                linestyle='dashed',
                width=0.8,
                label="Overbought"
            ),
        ]

        fig, axlist = self.plot_style(
            df=df_plot,
            name=name,
            addplot=apds,
            panel_ratios=(6, 3, 2),
            bool_volume=False
        )

        # 6. 保存并释放
        fig.savefig(path_img, dpi=300, bbox_inches="tight")
        plt.close(fig)

    def plot_volume_indicators(self, name: str=None, period: int=90):
        """
        成交量指标
        :param name:
        :param period:
        :return:
        """
        path_img = os.path.join(
            self.pm.images,
            "stock",
            f"technical_indicators_volume_{name}_{period}days.png"
        )
        df_plot = self.df.tail(period).copy()
        # 2. 配置 Addplots (确保 secondary_y=False)
        apds = [
            # VWAP
            mpf.make_addplot(
                df_plot['vwap'],
                panel=0,
                color='orange',
                width=1.2,
                label="VWAP"
            ),
            mpf.make_addplot(
                df_plot['vwap_20'],
                panel=0,
                color='blue',
                width=1.2,
                label="VWAP 20"
            ),
            # Panel 7: OBV
            mpf.make_addplot(
                df_plot['obv'],
                panel=1,
                color='black',
                width=1.2,
                label="OBV"
            ),
        ]

        fig, axlist = self.plot_style(
            df=df_plot,
            name=name,
            addplot=apds,
            panel_ratios=(6, 2),
            bool_volume=False
        )

        # 6. 保存并释放
        fig.savefig(path_img, dpi=300, bbox_inches="tight")
        plt.close(fig)

    def plot_features2(self, name: str = None):
        path_img = os.path.join(self.pm.images, "stock", f"kline_macd_{name}.png")
        df_plot = self.df.tail(150).copy()

        # MACD 柱状图颜色逻辑
        macd_colors = ['red' if v >= 0 else 'green' for v in df_plot['macd_hist']]

        # 2. 配置 Addplots (确保 secondary_y=False)
        apds = [
            # Panel 0:
            # 均线MA
            mpf.make_addplot(df_plot['ma5'], panel=0, color='red', width=1.2),
            mpf.make_addplot(df_plot['ma10'], panel=0, color='blue', width=1.2),
            mpf.make_addplot(df_plot['ma20'], panel=0, color='orange', width=1.2),

            # Bollinger Bands
            mpf.make_addplot(df_plot['bb_upper'], panel=0, color='gray', linestyle='dashed', width=1),
            mpf.make_addplot(df_plot['bb_middle'], panel=0, color='black', width=1),
            mpf.make_addplot(df_plot['bb_lower'], panel=0, color='gray', linestyle='dashed', width=1),

            # VWAP
            mpf.make_addplot(df_plot['vwap'], panel=0, color='gold', width=1.2),

            # SAR（scatter）
            mpf.make_addplot(
                df_plot['sar'],
                panel=0,
                type='scatter',
                marker='.',
                markersize=20,
                color='black'
            ),

            # Panel 2: MACD
            mpf.make_addplot(
                df_plot['macd'],
                panel=2,
                color='blue',
                width=1.2,
                secondary_y=False
            ),
            mpf.make_addplot(
                df_plot['macd_signal'],
                panel=2,
                color='orange',
                width=1.2,
                secondary_y=False
            ),
            mpf.make_addplot(
                df_plot['macd_hist'],
                type='bar',
                panel=2,
                color=macd_colors,
                alpha=0.6,
                secondary_y=False
            ),

            # Panel 3: RSI
            mpf.make_addplot(
                df_plot["rsi"],
                panel=3,
                color="purple",
                width=1.2,
                secondary_y=False
            ),
            mpf.make_addplot(
                [70] * len(df_plot),
                panel=3,
                color="red",
                linestyle="dashed",
                width=0.8
            ),

            mpf.make_addplot(
                [30] * len(df_plot),
                panel=3,
                color="green",
                linestyle="dashed",
                width=0.8
            ),

            # Panel 4: KDJ
            mpf.make_addplot(df_plot['k'], panel=4, color='blue', width=1.0),
            mpf.make_addplot(df_plot['d'], panel=4, color='orange', width=1.0),
            mpf.make_addplot(df_plot['j'], panel=4, color='green', width=1.0),

            # Panel 5: CCI
            mpf.make_addplot(df_plot['cci'], panel=5, color='purple', width=1.2),
            mpf.make_addplot([100] * len(df_plot), panel=5, color='red', linestyle='dashed', width=0.8),
            mpf.make_addplot([-100] * len(df_plot), panel=5, color='green', linestyle='dashed', width=0.8),

            # Panel 6: ATR
            mpf.make_addplot(df_plot['atr'], panel=6, color='brown', width=1.2),

            # Panel 7: OBV
            mpf.make_addplot(df_plot['obv'], panel=7, color='black', width=1.2),

        ]

        fig, axlist = self.plot_style(
            df=df_plot,
            name="AAPL",
            addplot=apds,
            panel_ratios=(6, 2, 3, 2, 2, 2, 2, 2),
        )

        # (3) 增加子图之间的物理间距，防止 Legend 重叠
        # hspace=0.6 提供足够的空间放置 MACD 的图例
        # plt.subplots_adjust(hspace=0.6, top=0.93)

        # 5. 【精准图例绘制】

        # K线层 (Panel 0)
        lines_main = axlist[0].get_lines()
        axlist[0].legend(
            lines_main[-7:],  # MA + Bollinger + VWAP
            [
                'MA5', 'MA10', 'MA20',
                'BB Upper', 'BB Mid', 'BB Lower',
                'VWAP'
            ],
            loc='upper left',
            frameon=False,
            fontsize=9,
            ncol=2
        )

        # 成交量层 (Panel 1)
        # axlist[2].legend(['Volume'], loc='upper left', frameon=False, fontsize=10)

        # MACD 层 (Panel 2)
        lines_macd = axlist[4].get_lines()
        axlist[4].legend(
            lines_macd[-2:],
            ['MACD', 'Signal'],
            loc='upper left',
            bbox_to_anchor=(0, 1.02),
            ncol=2,
            frameon=False,
            fontsize=10
        )

        # RSI
        lines_rsi = axlist[6].get_lines()
        axlist[6].legend(
            lines_rsi[:1],
            ["RSI"],
            loc="upper left",
            frameon=False,
            fontsize=10
        )

        # 6. 保存并释放
        fig.savefig(path_img, dpi=300, bbox_inches="tight")
        plt.close(fig)

    # ===============================
    # 1. 收益率特征
    # ===============================
    def _add_returns(self):
        """
        添加收益率特征
        financial meaning:
        收益率是金融时间序列中最基础的特征
        """
        # 单期收益率
        self.df["return_1"] = self.df["close"].pct_change()
        # 多期收益率
        self.df["return_5"] = self.df["close"].pct_change(5)
        self.df["return_10"] = self.df["close"].pct_change(10)
        # 对数收益率
        self.df["log_return"] = np.log(self.df["close"] / self.df["close"].shift(1))

    # ===============================
    # 2. 趋势类指标
    # ===============================
    def _add_ma(self):
        """
        添加移动平均特征Moving Average
        用于捕捉趋势
        """
        self.df["ma5"] = self.df["close"].rolling(5).mean()
        self.df["ma10"] = self.df["close"].rolling(10).mean()
        self.df["ma20"] = self.df["close"].rolling(20).mean()
        # 均线差
        self.df["ma_diff"] = self.df["ma5"] - self.df["ma20"]

    def _add_ema(self):
        """
        计算 EMA 指标
        指数移动平均
        """
        self.df["ema12"] = self.df["close"].ewm(span=12, adjust=False).mean()
        self.df["ema26"] = self.df["close"].ewm(span=26, adjust=False).mean()

    def _add_bollinger(self, window: int = 20):
        """
        计算 Bollinger Bands
        布林带（Bollinger Bands）是一种非常常用的技术分析指标，
        由技术分析师John Bollinger在 1980 年代提出，用于衡量 价格趋势 + 波动率。
        价格通常会在“统计波动范围”内上下波动
        """
        self.df["bb_middle"] = self.df["close"].rolling(window).mean()
        std = self.df["close"].rolling(window).std()
        self.df["bb_upper"] = self.df["bb_middle"] + 2 * std
        self.df["bb_lower"] = self.df["bb_middle"] - 2 * std

    def _add_sar(self, step: float = 0.02, max_step: float = 0.2):
        """
        计算 Parabolic SAR
        """
        high = self.df["high"].values
        low = self.df["low"].values
        length = len(self.df)
        sar = [low[0]]
        trend_up = True
        ep = high[0]
        af = step

        for i in range(1, length):
            prev_sar = sar[-1]
            if trend_up:
                new_sar = prev_sar + af * (ep - prev_sar)
                if low[i] < new_sar:
                    trend_up = False
                    new_sar = ep
                    ep = low[i]
                    af = step
                else:
                    if high[i] > ep:
                        ep = high[i]
                        af = min(af + step, max_step)
            else:
                new_sar = prev_sar + af * (ep - prev_sar)

                if high[i] > new_sar:
                    trend_up = True
                    new_sar = ep
                    ep = high[i]
                    af = step
                else:
                    if low[i] < ep:
                        ep = low[i]
                        af = min(af + step, max_step)
            sar.append(new_sar)
        self.df["sar"] = sar

    def _add_vwap(self):
        """
        计算 VWAP
        成交量加权平均价格（Volume Weighted Average Price，VWAP）是金融市场中非常重要的技术指标之一，
        广泛用于 机构交易、量化交易和算法交易。
        在计算平均价格时，成交量大的价格影响更大。
        """
        typical_price = (self.df["high"] + self.df["low"] + self.df["close"]) / 3
        tp_vol = typical_price * self.df["volume"]
        self.df["vwap"] = (
                tp_vol.groupby(self.df.index.date).cumsum() /
                self.df["volume"].groupby(self.df.index.date).cumsum()
        )
        self.df["vwap_20"] = (
             (typical_price * self.df["volume"]).rolling(20).sum() /
             self.df["volume"].rolling(20).sum()
        )
        #
        # typical_price = (self.df["high"] + self.df["low"] + self.df["close"]) / 3
        # tp_vol = typical_price * self.df["volume"]
        # cum_tp_vol = tp_vol.cumsum()
        # cum_vol = self.df["volume"].cumsum()
        # self.df["vwap"] = cum_tp_vol / cum_vol.replace(0, np.nan)


    # ===============================
    # 3. 波动率特征
    # ===============================
    def _add_volatility(self):
        """
        计算波动率

        金融含义：
        波动率代表风险水平
        """

        self.df["volatility_5"] = self.df["return_1"].rolling(5).std()
        self.df["volatility_10"] = self.df["return_1"].rolling(10).std()

    def _add_kdj(self, period: int = 9, k_period: int = 3, d_period: int = 3):
        """
        计算 KDJ 指标
        新增列：
            k, d, j
        """
        low_min = self.df['low'].rolling(period).min()
        high_max = self.df['high'].rolling(period).max()
        rsv = (self.df['close'] - low_min) / (high_max - low_min) * 100

        self.df['k'] = rsv.ewm(alpha=1 / k_period).mean()
        self.df['d'] = self.df['k'].ewm(alpha=1 / d_period).mean()
        self.df['j'] = 3 * self.df['k'] - 2 * self.df['d']

    def _add_cci(self, period: int = 20):
        """
        计算 CCI 指标
        新增列：
            cci
        """
        tp = (self.df['high'] + self.df['low'] + self.df['close']) / 3
        ma = tp.rolling(period).mean()
        md = tp.rolling(period).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
        self.df['cci'] = (tp - ma) / (0.015 * md)

    def _add_atr(self, period: int = 14):
        """
        计算 ATR 指标
        新增列：
            atr
        """
        high_low = self.df['high'] - self.df['low']
        high_close = np.abs(self.df['high'] - self.df['close'].shift(1))
        low_close = np.abs(self.df['low'] - self.df['close'].shift(1))
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        self.df['atr'] = tr.rolling(period).mean()

    def _add_obv(self):
        """
        计算 OBV 指标
        """
        direction = np.sign(self.df["close"].diff()).fillna(0)
        self.df["obv"] = (direction * self.df["volume"]).cumsum()

    # ===============================
    # 4. 动量特征
    # ===============================
    def _add_momentum(self):
        """
        计算动量指标
        """

        self.df["momentum_5"] = self.df["close"] - self.df["close"].shift(5)
        self.df["momentum_10"] = self.df["close"] - self.df["close"].shift(10)

        

    # ===============================
    # 5. RSI 指标
    # ===============================
    def _add_rsi(self, period=14):
        """
        RSI (Relative Strength Index)

        衡量超买 / 超卖
        """

        delta = self.df["close"].diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()

        rs = avg_gain / avg_loss

        self.df["rsi"] = 100 - (100 / (1 + rs))

        

    # ===============================
    # 6. MACD
    # ===============================
    def _add_macd(self):
        """
        MACD 指标
        """
        ema12 = self.df["close"].ewm(span=12).mean()
        ema26 = self.df["close"].ewm(span=26).mean()

        self.df["macd"] = ema12 - ema26
        self.df["macd_signal"] = self.df["macd"].ewm(span=9).mean()
        self.df["macd_hist"] = self.df["macd"] - self.df["macd_signal"]
        

    # ===============================
    # 7. Rolling统计特征
    # ===============================
    def _add_rolling_features(self):
        """
        滚动统计特征
        """

        self.df["rolling_max_10"] = self.df["close"].rolling(10).max()
        self.df["rolling_min_10"] = self.df["close"].rolling(10).min()

        self.df["price_position"] = (
            (self.df["close"] - self.df["rolling_min_10"]) /
            (self.df["rolling_max_10"] - self.df["rolling_min_10"])
        )

        