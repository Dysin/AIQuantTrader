'''
@Desc:   数据处理
@Author: Dysin
@Date:   2026/3/11
'''
import os.path

import pandas as pd
from utils.images import ImageUtils

class DataProcessing:
    def __init__(self, path):
        self.path = path

    def normalized_compare_curves(
            self,
            dfs: list,
            x_col: str,
            y_cols: list,
            labels: list,
            image_name: str,
            how: str = 'inner'  # 'inner' 取交集, 'outer' 取并集
    ):
        """
        合并多个 DataFrame，进行归一化处理并绘图
        :param dfs: DataFrame 列表
        :param x_col: 用作 X 轴的列名 (需各 DF 通用)
        :param y_cols: 每个 DF 中对应的数值列名列表
        :param labels: 最终图例显示的名称列表
        """
        if not (len(dfs) == len(y_cols) == len(labels)):
            raise ValueError("dfs, y_cols, labels 的长度必须一致")

        # 1. 预处理：确保 X 轴为 datetime 并设置为索引
        processed_dfs = []
        for i, df in enumerate(dfs):
            temp_df = df[[x_col, y_cols[i]]].copy()
            temp_df[x_col] = pd.to_datetime(temp_df[x_col])
            temp_df = temp_df.set_index(x_col)
            # 临时重命名以防合并冲突
            temp_df.columns = [f"val_{i}"]
            processed_dfs.append(temp_df)

        # 2. 合并所有数据 (按时间轴对齐)
        merged_df = processed_dfs[0]
        for next_df in processed_dfs[1:]:
            merged_df = merged_df.merge(next_df, left_index=True, right_index=True, how=how)

        merged_df = merged_df.sort_index().dropna()  # 剔除无法对齐的空值

        # 3. 归一化处理 (以合并后的第一行为基准 1.0)
        norm_columns = []
        for i in range(len(dfs)):
            col_name = f"norm_{labels[i]}"
            # 增加安全检查：防止分母为 0
            base_val = merged_df[f"val_{i}"].iloc[0]
            if base_val == 0 or pd.isna(base_val):
                merged_df[col_name] = 0  # 或根据业务逻辑处理
            else:
                merged_df[col_name] = merged_df[f"val_{i}"] / base_val
            norm_columns.append(col_name)

        # 重置索引以便绘图函数读取 x_col
        final_df = merged_df.reset_index()

        # 4. 调用绘图工具
        # 注意：这里的 dfs 列表里传的都是合并后的 final_df
        path_img = os.path.join(
            self.path,
            f'{image_name}.png'
        )
        ImageUtils().plot_lines(
            df=final_df,
            y_columns=[c for c in norm_columns],
            save_path=path_img,
            bool_datetime=True,
            line_labels=labels,
            title="Normalized Performance Comparison"
        )

        return final_df
