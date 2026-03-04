'''
@Desc:   宏观经济数据采集与分析模块
@Author: Dysin
@Date:   2025/10/5

该模块用于获取宏观经济层面的关键指标数据，包括：
    - GDP（经济周期判断）
    - CPI、PPI（通胀指标）
    - 利率（货币政策信号）
    - M2货币供应量（流动性指标）
    - 失业率（就业情况）
    - PMI（经济景气指数）

数据来源：
    - Tushare（中国数据）
    - FRED：https://fred.stlouisfed.org/

本地MySQL路径：C:\ProgramData\MySQL\MySQL Server 8.0\Data\financial_data
'''

import os
import pandas as pd
from utils.api_keys import *
from fredapi import Fred
import tushare as ts
from utils.paths import PathManager
from utils.db_manager import DBManager

class MacroDataFetcher:
    """
    中美宏观经济数据抓取类

    功能：
    - 美国数据：优先 FRED，失败则 Yahoo Finance
    - 中国数据：优先 Tushare，失败则 Yahoo Finance 指数替代
    - 数据自动保存到指定路径
    - 指标 mapping 扩展为常用宏观经济指标，带对股市影响说明
    """

    # ======= 中美宏观指标 mapping =======
    us_mapping = {
        "GDP": "^GSPC",        # GDP 增长加快 → 股市上涨
        "CPI": "^IRX",         # 通胀过高 → 股市承压
        "FEDFUNDS": "^IRX",    # 利率上升 → 股市承压
        "UNRATE": "^TNX",      # 失业率上升 → 股市承压
        "PCE": "^CPI",         # 通胀指标 → 股市波动
        "M2": "^M2SL",         # 货币供应量 → 股市宽松/紧缩
        "SP500": "^GSPC",      # 标普500指数
        "NASDAQ": "^IXIC",     # 纳斯达克指数
    }

    cn_mapping = {
        "GDP": "000001.SS",           # 上证指数近似 GDP 走势
        "CPI": "000001.SS",           # CPI 替代
        "M2": "CNY=X",                # 人民币汇率作为货币流动性参考
        "PMI": "399001.SZ",           # 制造业活跃度
        "SHIBOR": "^CNYIR",           # 银行间拆借利率
        "失业率": "000001.SS",        # 失业率近似股市趋势
        "财政支出": "000001.SS",      # 财政扩张 → 股市利好
        "上证指数": "000001.SS",      # 上证综指
        "深证成指": "399001.SZ",     # 深证成指
        "人民币汇率": "CNY=X",        # 人民币升值/贬值影响外资流入
    }

    def __init__(self):
        # 获取数据保存路径
        paths = PathManager()
        self.base_dir = paths.get_data_dir()
        self.us_dir = os.path.join(self.base_dir, "us")
        self.cn_dir = os.path.join(self.base_dir, "cn")
        self._ensure_dir(self.us_dir)
        self._ensure_dir(self.cn_dir)

        # 初始化 Tushare
        ts.set_token(APIKeys().tushare)
        self.pro = ts.pro_api()

        # 初始化数据管理器
        self.db = DBManager()

    @staticmethod
    def _ensure_dir(path: str):
        """确保目录存在"""
        os.makedirs(path, exist_ok=True)

    def _save_data(self, df: pd.DataFrame, path: str, table_name: str):
        """保存 DataFrame 到 CSV"""
        df.reset_index(inplace=True)
        df.columns = ["date", "value"]
        df.to_csv(path, index=False)
        self.db.save_dataframe(df, table_name)
        print(f"[Info] 数据已保存: {path}")

    # ==================== 美国宏观数据 ====================
    def fetch_us_data(self, series_name: str):
        """
        获取美国宏观数据并保存
        """
        file_path = os.path.join(self.us_dir, f"{series_name}.csv")
        df = None

        try:
            fred = Fred(api_key=APIKeys().fred)
            print(f"[Info] 从 FRED 获取美国数据：{series_name}")
            data = fred.get_series(series_name)
            print(data)
            df = pd.DataFrame(data, columns=['value'])
        except Exception as e:
            print(f"[Warning] FRED 获取失败：{e}")

        self._save_data(df, file_path, table_name=f'US_{series_name}')

    # ==================== 中国宏观数据 ====================
    def fetch_cn_data(self, series_name: str):
        """
        获取中国宏观数据并保存
        优先 Tushare，失败则 Yahoo Finance 替代
        """
        file_path = os.path.join(self.cn_dir, f"{series_name}.csv")
        df = None

        # 1️⃣ 优先使用 Tushare
        try:
            print(f"[Info] 从 Tushare 获取中国数据：{series_name}")
            if series_name == "GDP":
                df = self.pro.cn_gdp(year='', fields='year,gdp')  # 年度 GDP
                df.rename(columns={'gdp': 'value', 'year': 'date'}, inplace=True)
                df['date'] = pd.to_datetime(df['date'].astype(str))
                df.set_index('date', inplace=True)
            elif series_name == "CPI":
                df = self.pro.cn_cpi(start_date='20100101')      # 月度 CPI
                df.rename(columns={'cpi': 'value', 'date': 'date'}, inplace=True)
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
            elif series_name == "M2":
                df = self.pro.cn_m2(start_date='20100101')       # 月度 M2
                df.rename(columns={'m2': 'value', 'date': 'date'}, inplace=True)
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
            elif series_name == "PMI":
                df = self.pro.cn_pmi(start_date='20100101')      # 月度 PMI
                df.rename(columns={'pmi': 'value', 'date': 'date'}, inplace=True)
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
        except Exception as e:
            print(f"[Warning] Tushare 获取失败：{e}")

        self._save_data(df, file_path, table_name=f'US_{series_name}')


# ===============================
# 主程序示例
# ===============================
if __name__ == "__main__":
    fetcher = MacroDataFetcher()

    # 获取美国宏观指标
    us_series = [
        # "GDP",
        # "CPIAUCSL",
        "FEDFUNDS",
        # "UNRATE",
        # "SP500"
    ]
    for s in us_series:
        fetcher.fetch_us_data(s)

    # 获取中国宏观指标
    cn_series = [
        "GDP",
        "CPI",
        "M2",
        "PMI",
        "上证指数",
        "深证成指",
        "人民币汇率"
    ]
    for s in cn_series:
        fetcher.fetch_cn_data(s)