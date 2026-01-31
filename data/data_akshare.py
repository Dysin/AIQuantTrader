'''
@Desc:   基于AKShare获取数据
@Author: Dysin
@Date:   2025/10/7

AKShare
    - AKShare是一个基于Python的开源财经数据接口库
    - 它的目标是为量化分析、财经研究、学术科研提供 统一、便捷、免费 的数据接口
    - 它从多个公开数据源（政府网站、交易所、券商、基金网站等）自动抓取数据并封装成pandas DataFrame格式
网址：https://akshare.akfamily.xyz/index.html
'''

import os.path
import time
import pandas as pd
import akshare as ak
import inspect
from utils.paths import PathManager
from utils.logger import get_logger
logger = get_logger(__name__)

class AKShareData:
    def __init__(self):
        self.paths = PathManager()
        self.path_macro = self.paths.get_data_macro_dir()

    def str_to_kwargs(self, param):
        """
        将形如 "a=1 b=2 c=3" 的字符串转换为字典 {'a':'1', 'b':'2', 'c':'3'}。
        所有值都保持为字符串。
        """
        if not param or param.strip() == "":
            return {}

        kwargs = {}
        for item in param.strip().split():
            if "=" not in item:
                continue
            key, value = item.split("=", 1)  # 只分一次，防止 value 中有 '='
            key = key.strip()
            value = value.strip()
            kwargs[key] = value

        return kwargs

    def call_api(self, api_name, params):
        """
        动态调用 AKShare 的函数
        """
        if hasattr(ak, api_name):
            func = getattr(ak, api_name)
            # 检查是否需要参数（如 symbol 等）
            sig = inspect.signature(func)
            if len(sig.parameters) == 0:
                data = func()
            else:
                kwargs = self.str_to_kwargs(params)
                print(kwargs)
                data = func(**kwargs)
            return data
        else:
            logger.error(f"[ERROR] 未找到接口: {api_name}")
            return None

    def download(
            self,
            file_name,
            save_path,
            start_index,
            end_index,
            sleep_time=2
    ):
        """
        批量获取宏观数据并保存为 CSV。
        参数：
        - start_index: int，循环起始行索引（默认 0）
        - end_index: int 或 None，循环结束行索引（默认 None，遍历到最后）
        - sleep_time: int/float，每次请求后的暂停时间（秒）
        """
        df_akshare = pd.read_csv(
            self.paths.join_file_path(f'{file_name}.csv')
        )
        if end_index is None:
            end_index = len(df_akshare)

        for i in range(start_index, end_index):
            row = df_akshare.iloc[i]
            api_name = row["AKShare API"]
            csv_name = row["csv名"]
            params = row["参数"]
            logger.info(f"[INFO] 正在获取 {api_name}...")

            try:
                df_data = self.call_api(api_name, params)
                if df_data is not None and not df_data.empty:
                    file_csv = os.path.join(save_path, f'{csv_name}.csv')
                    df_data.to_csv(file_csv, index=False, encoding="utf-8-sig")
                    logger.info(f"[INFO] 已保存到 {file_csv}")
                else:
                    logger.warning(f"[WARNING] {api_name} 未返回数据")
            except Exception as e:
                logger.error(f"[ERROR] {api_name} 连接失败: {e}")

            time.sleep(sleep_time)

    def macro(self, start_index=0, end_index=None):
        file_name = 'download_akshare_macro_info'
        save_path = self.paths.get_data_macro_dir()
        self.download(
            file_name,
            save_path,
            start_index,
            end_index
        )

    def stock(self, start_index=1, end_index=None):
        '''
        下载AkShare股票信息
        :param start_index: 编号从1开始
        :param end_index:
        :return:
        '''
        file_name = 'download_akshare_stock_info'
        save_path = self.paths.get_data_stock_dir()
        self.download(
            file_name,
            save_path,
            start_index-1,
            end_index
        )

if __name__ == '__main__':
    akdata = AKShareData()
    # akdata.macro(start_index=64, end_index=None)
    akdata.stock(start_index=5, end_index=None)