'''
@Desc:   股票量化流程
@Author: Dysin
@Date:   2026/3/11
'''


import os.path
import shutil
import pandas as pd
from utils.paths import PathManager
from utils.logger import get_logger
from backtest.stock_trade_calculator import StockTradeCalculator
from backtest.engine import BacktestEngine
from backtest.portfolio import Portfolio
from backtest.metrics import PerformanceMetrics
from strategy.simple_ma import SimpleMAStrategy
from utils.images import ImageUtils
from report.latex_quant import LatexQuant
from datetime import datetime
from analysis.data_processing import DataProcessing
from features.feature_engineer import FeatureEngineer

logger = get_logger(__name__)

class WorkflowStock:
    def __init__(self):
        self.pm = PathManager()
        self.path_backtest = os.path.join(
            self.pm.results,
            'backtest'
        )
        self.data_processing = DataProcessing(self.path_backtest)

    def test(self, name):
        csv_stock = os.path.join(
            self.pm.data_archived,
            "stock",
            f'us_stock_daily_{name}.csv'
        )
        df = pd.read_csv(csv_stock, parse_dates=["date"], index_col="date")
        df_slice = df.loc["2016-03-01":"2025-10-30"]

        data = pd.DataFrame({
            "Close": [100, 101, 102, 101, 103, 104, 102]
        }, index=pd.date_range("2023-01-01", periods=7))
        # portfolio = Portfolio(init_cash=100000)
        engine = BacktestEngine(
            init_cash=100000,
            fee_rate=0.001,
            slippage=0.0005,
        )
        strategy = SimpleMAStrategy(window=10)
        result = engine.run(df_slice, strategy)

        features = FeatureEngineer(df_slice)
        features.generate_features()
        features.plot_features(name, 500)

        image_names = [
            'trades_price',
            'trades_volume',
            'trades_direction',
            'trades_fee'
        ]
        df_trades = pd.read_csv(os.path.join(self.path_backtest, 'trades.csv'))
        df_equity = pd.read_csv(os.path.join(self.path_backtest, 'equity.csv'))
        df_sp500 = pd.read_csv(
            os.path.join(
                self.pm.data_archived,
                "macro",
                'us_sp500.csv'
            )
        )

        for i in range(len(image_names)):
            image_trade = os.path.join(
                self.path_backtest,
                image_names[i]
            )
            ImageUtils().plot_lines(
                df=df_trades,
                y_columns=i + 1,
                save_path=image_trade,
                bool_datetime=True
            )

        self.data_processing.normalized_compare_curves(
            dfs=[df_equity, df_sp500],
            x_col='date',
            y_cols=['value', 'value'],
            labels=['equity', 'SP500'],
            image_name='equity_vs_sp500'
        )

        equity_series = pd.Series(
            result["equity_curve"],
            index=df_slice.index,
        )

        metrics = PerformanceMetrics(equity_series)
        summary = metrics.summary()

        print("\n绩效指标：")
        for k, v in summary.items():
            print(f"{k}: {v:.4f}")

        # 输出报告
        latex = LatexQuant()
        date = f"{datetime.now().strftime('%Y%m%d')}"
        path_latex_images = os.path.join(
            self.pm.reports,
            f'quantitative_trading_{date}',
            "images"
        )
        for file in os.listdir(self.path_backtest):
            src_path = os.path.join(self.path_backtest, file)
            dst_path = os.path.join(path_latex_images, file)
            shutil.copy2(src_path, dst_path)
        for file in os.listdir(os.path.join(self.pm.images, "stock")):
            src_path = os.path.join(self.pm.images, "stock", file)
            dst_path = os.path.join(path_latex_images, file)
            shutil.copy2(src_path, dst_path)
        latex.report('20220101', result, summary)

