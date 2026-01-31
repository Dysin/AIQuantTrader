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
logger = get_logger(__name__)

if __name__ == '__main__':
    path_manager = PathManager()
    path_stock = path_manager.data_stock_dir
    csv_stock = os.path.join(path_stock, 'us_stock_daily_AAPL.csv')
    df = pd.read_csv(csv_stock, parse_dates=["date"], index_col="date")
    calc = StockTradeCalculator(
        df,
        fee_buy=0.0003,
        fee_sell=0.0003,
        stamp_tax=0.001,
        annual_interest_rate=0.03
    )
    result = calc.calculate_trade(
        buy_time=pd.Timestamp("2013-10-01"),
        sell_time=pd.Timestamp("2014-08-01"),
        shares=1000
    )
    for k, v in result.items():
        logger.info(f"{k}: {v:.2f}")