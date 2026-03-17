'''
@Desc:   下载股票数据
@Author: Dysin
@Date:   2026/3/13
'''

import os
# import pandas_datareader.data as web
from data.data_utils import DataUtils
from utils.logger import get_logger
import yfinance as yf

logger = get_logger(__name__)

class StockData(DataUtils):
    def __init__(self):
        super().__init__()

    def download_daily(self, name):
        logger.info(f"Download stock data: {name}")
        df = web.DataReader(
            name,
            "stooq",
            "2000-01-01"
        )
        # 1. 处理普通列
        df.columns = [str(col).lower() for col in df.columns]
        # 2. 处理索引名 (针对 MultiIndex 或 单 Index)
        if df.index.name:
            df.index.name = df.index.name.lower()
        elif df.index.names:
            df.index.names = [n.lower() if n else n for n in df.index.names]
        df = df.sort_index()
        path_csv = os.path.join(
            self.path_dact_stock,
            f"us_stock_daily_{name}.csv"
        )
        df.to_csv(path_csv)
        self.update(
            self.path_dact_stock,
            self.path_darc_stock,
            f"us_stock_daily_{name}"
        )
        logger.info(f"Download stock data successfully")

    def download_yfinance(self, name):
        df = yf.download(name, start='2000-01-01', end='2026-01-01')
        path_csv = os.path.join(
            self.path_dact_stock,
            f"us_stock_daily_{name}.csv"
        )
        df = self.flatten_columns(df)
        df = self.standardize_ohlcv(df)
        df.to_csv(path_csv, index=False)
        self.update(
            self.path_dact_stock,
            self.path_darc_stock,
            f"us_stock_daily_{name}"
        )
        logger.info(f"Download stock data successfully")

if __name__ == "__main__":
    stock_data = StockData()
    # stock_data.download_daily("AAPL")
    stock_data.download_yfinance("AAPL")