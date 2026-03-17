'''
@Desc:   数据处理工具类
@Author: Dysin
@Date:   2026/3/12
'''
import os

import pandas as pd
from utils.paths import PathManager
from utils.files import FileUtils

class DataUtils:
    def __init__(self):
        self.pm = PathManager()
        # 实时stock数据路径
        self.path_dact_stock = os.path.join(
            self.pm.data_active,
            "stock"
        )
        # 实时macro数据路径
        self.path_dact_macro = os.path.join(
            self.pm.data_active,
            "macro"
        )
        # stock数据储存路径
        self.path_darc_stock = os.path.join(
            self.pm.data_archived,
            "stock"
        )
        # macro数据储存路径
        self.path_darc_macro = os.path.join(
            self.pm.data_archived,
            "macro"
        )

    def union_df_to_csv(
            self,
            df1: pd.DataFrame,
            df2: pd.DataFrame,
            output_path: str,
            sort_column=None,
    ) -> pd.DataFrame:
        """
        计算两个 DataFrame 的并集，并保存为 CSV 文件

        :param df1: 第一个 DataFrame
        :param df2: 第二个 DataFrame
        :param output_path: 输出 CSV 文件路径
        :param keep: 去重策略
                    "first"  -> 保留第一次出现的行
                    "last"   -> 保留最后一次出现的行
                    False    -> 删除所有重复行
        :param index: 是否在 CSV 中保存索引
        :return: [pd.DataFrame] 返回并集后的 DataFrame
        """
        # 1. 使用 concat 合并两个 DataFrame
        # 2. drop_duplicates() 去除完全重复的行，实现并集效果
        union_df = pd.concat([df1, df2]).drop_duplicates()

        # 3. 按指定列进行升序排序 (ascending=True 为默认)
        # ignore_index=True 重新重置索引，让序号从 0 开始排列
        if sort_column is None:
            sort_column = union_df.columns[0]
        union_df = union_df.sort_values(
            by=sort_column,
            ascending=True
        ).reset_index(drop=True)

        # 4. 保存为 CSV 文件
        # index=False 表示不保存索引列
        union_df.to_csv(output_path, index=False, encoding='utf-8-sig')

        print(f"文件已成功保存至: {output_path}")
        return union_df

    def update(
            self,
            path_active,
            path_archived,
            file_name
    ):
        """
        更新并保存实时数据
        :param file_name: 文件名
        :return:
        """
        csv_active = os.path.join(
            path_active,
            f"{file_name}.csv"
        )
        df_active = pd.read_csv(csv_active)
        csv_archived = os.path.join(
            path_archived,
            f"{file_name}.csv"
        )
        if not os.path.exists(csv_archived):
            file_utils = FileUtils(path_active)
            file_utils.copy(f"{file_name}.csv", path_archived)
        else:
            df_archived = pd.read_csv(csv_archived)
            self.union_df_to_csv(
                df1=df_active,
                df2=df_archived,
                output_path=csv_archived,
            )

    def update_all(self):
        file_utils = FileUtils(self.path_dact_stock)
        all_csv = file_utils.get_file_names_by_type("csv")
        for csv in all_csv:
            self.update(
                self.path_dact_stock,
                self.path_darc_stock,
                csv
            )
        file_utils = FileUtils(self.path_dact_macro)
        all_csv = file_utils.get_file_names_by_type("csv")
        for csv in all_csv:
            self.update(
                self.path_dact_macro,
                self.path_darc_macro,
                csv
            )

    def flatten_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        处理 MultiIndex 列（如 yfinance 多股票格式）
        """
        if isinstance(df.columns, pd.MultiIndex):
            # 方法1：只取第一层（最常用）
            df.columns = [col[0] for col in df.columns]
            # 方法2（可选）：拼接列名（适合多股票）
            # df.columns = ['_'.join(col).strip() for col in df.columns]
        return df

    def standardize_ohlcv(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        自动识别并标准化 OHLCV 列名为：
        date, open, high, low, close, volume
        """
        df = df.copy()
        # 1. 统一列名小写
        df.columns = [str(c).lower().strip() for c in df.columns]
        # 2. 处理日期列
        if df.index.name is not None:
            idx_name = df.index.name.lower()
        else:
            idx_name = ""
        # 情况1：日期在 index
        if "date" in idx_name or "time" in idx_name:
            df = df.reset_index()
            df.rename(columns={df.columns[0]: "date"}, inplace=True)
        # 情况2：日期在列中（各种可能命名）
        else:
            date_candidates = ["date", "datetime", "time", "timestamp"]
            for col in df.columns:
                if col in date_candidates:
                    df.rename(columns={col: "date"}, inplace=True)
                    break
            else:
                # 如果没有找到，默认第一列是时间
                df.rename(columns={df.columns[0]: "date"}, inplace=True)

        # 3. 映射 OHLCV
        col_map = {
            "open": ["open", "o"],
            "high": ["high", "h"],
            "low": ["low", "l"],
            "close": ["close", "c", "adj close", "adj_close"],
            "volume": ["volume", "vol", "v"]
        }
        new_columns = {}
        for std_col, candidates in col_map.items():
            for c in df.columns:
                if c in candidates:
                    new_columns[c] = std_col
                    break
        df.rename(columns=new_columns, inplace=True)

        # 4. 保留标准列（存在的）
        cols_order = ["date", "open", "high", "low", "close", "volume"]
        cols_exist = [c for c in cols_order if c in df.columns]
        df = df[cols_exist]

        # 5. 转换日期类型 + 排序
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        return df

if __name__ == "__main__":
    data_utils = DataUtils()
    data_utils.update_all()