'''
@Desc:   主函数入口
@Author: Dysin
@Date:   2026/1/27
'''

import os.path
import pandas as pd
from utils.paths import PathManager
from utils.logger import get_logger
from backtest.stock_trade_calculator import StockTradeCalculator
from backtest.engine import BacktestEngine
from backtest.portfolio import Portfolio
from backtest.metrics import PerformanceMetrics
from strategy.simple_ma import SimpleMAStrategy
from utils.images import ImageUtils

logger = get_logger(__name__)

def workflow():
    pm = PathManager()
    path_stock = pm.data_stock
    csv_stock = os.path.join(
        path_stock,
        'us_stock_daily_AAPL.csv'
    )
    df = pd.read_csv(csv_stock, parse_dates=["date"], index_col="date")
    df_slice = df.loc["2022-01-01":"2025-10-30"]

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

    path_data = os.path.join(
        pm.results,
        'backtest',
        'data'
    )
    image_names = [
        'trades_price',
        'trades_volume',
        'trades_direction',
        'trades_fee'
    ]
    df_trades = pd.read_csv(os.path.join(path_data, 'trades.csv'))
    df_equity = pd.read_csv(os.path.join(path_data, 'equity.csv'))
    path_images = os.path.join(
            pm.results,
            'backtest',
            'images'
    )
    for i in range(len(image_names)):
        image_trade = os.path.join(
            path_images,
            image_names[i]
        )
        ImageUtils().plot_lines(
            df=df_trades,
            y_columns=i+1,
            save_path=image_trade,
            bool_datetime=True
        )
    image_equity = os.path.join(
        path_images,
        'equity'
    )
    ImageUtils().plot_lines(
        df=df_equity,
        y_columns=1,
        save_path=image_equity,
        bool_datetime=True
    )

    # 基础结果
    print("初始资金:", result["init_cash"])
    print("最终资产:", result["final_equity"])
    print("总收益率:", result["total_return"])
    print("交易次数:", result["trade_count"])

    # 资产净值曲线
    equity_curve = result["equity_curve"]
    print(equity_curve)

    # 交易记录
    for trade in result["trades"]:
        print(trade)

    equity_series = pd.Series(
        result["equity_curve"],
        index=df_slice.index,
    )

    metrics = PerformanceMetrics(equity_series)
    summary = metrics.summary()

    print("\n绩效指标：")
    for k, v in summary.items():
        print(f"{k}: {v:.4f}")



if __name__ == '__main__':
    path_manager = PathManager()
    path_stock = path_manager.data_stock
    csv_stock = os.path.join(path_stock, 'us_stock_daily_AAPL.csv')
    df = pd.read_csv(csv_stock, index_col="date")
    print(df)
    calc = StockTradeCalculator(
        df,
        fee_buy=0.0003,
        fee_sell=0.0003,
        stamp_tax=0.001,
        annual_interest_rate=0.03
    )
    result = calc.calculate_trade(
        buy_time=pd.Timestamp("2015-12-10"),
        sell_time=pd.Timestamp("2016-08-01"),
        shares=1000
    )
    for k, v in result.items():
        logger.info(f"{k}: {v:.2f}")

    print('================')

    workflow()