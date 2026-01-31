'''
@Desc:   
@Author: Dysin
@Date:   2025/10/5
'''

import os
import pandas as pd
import numpy as np
from utils.paths import PathManager
from utils.images import ImageUtils


class MacroAnalysis:
    """
    中美宏观数据分析与绘图类
    - 从 CSV 文件读取数据
    - 绘制折线图 / 柱状图
    """

    def __init__(self):
        """
        初始化分析类
        """
        self.paths = PathManager()
        self.path_macro = self.paths.get_data_macro_dir()
        self.plot_manager = ImageUtils()
        self.akshare_info = pd.read_csv(
            self.paths.join_file_path('plt_akshare_macro_info.csv')
        )

    def split_df_by_column(self, df, col_index):
        '''
        根据指定列号拆分 DataFrame，将相同值归为一个 DataFrame。
        :param col_index: 要根据此列号拆分
        :return: dict，键是列值，值是对应的 DataFrame
        '''
        # 获取列名
        col_name = df.columns[col_index]
        # 按列分组并存入字典
        return {k: v for k, v in df.groupby(col_name)}

    def plot_data(self, folder_name, star_index=1):
        path_data = os.path.join(self.paths.get_data_dir(), f'{folder_name}')
        path_save = os.path.join(self.paths.get_images_dir(), f'{folder_name}')
        os.makedirs(path_save, exist_ok=True)
        plt_csv_name = self.paths.join_file_path(f'plt_akshare_{folder_name}_info.csv')
        akshare_info = pd.read_csv(plt_csv_name)
        for i in range(star_index-1, len(akshare_info)):
            row = akshare_info.iloc[i]
            title = row['图标题']
            csv_name = row["csv名"]
            y_label = row['图Y轴名']
            img_name = row['图片名']
            x_col = row['图X轴列号']
            y_str = row['图Y轴列号']
            # 假设 y_str 可能是字符串或单个整数
            if isinstance(y_str, (int, np.integer)):
                y_cols = [int(y_str)]  # 单个整数转列表
            elif isinstance(y_str, str):
                y_cols = list(map(int, y_str.split()))  # 字符串形式 "1 2 3"
            else:
                raise ValueError(f"y_str 类型不支持: {type(y_str)}")
            split_col = row['分类列号']
            try:
                df = pd.read_csv(
                    os.path.join(
                        path_data,
                        f'{csv_name}.csv'
                    )
                )
                df = df.iloc[1:].reset_index(drop=True)
                if pd.isna(split_col):
                    file_img = os.path.join(path_save, f'{img_name}.png')
                    self.plot_manager.plot_lines(
                        df,
                        y_columns=y_cols,
                        x_column=x_col,
                        x_label='Date',
                        y_label=f'{y_label}',
                        title=f'{title}',
                        save_path=file_img,
                        bool_datetime=True
                    )
                else:
                    dfs = self.split_df_by_column(df, int(split_col))
                    for key, sub_df in dfs.items():
                        file_img = os.path.join(path_save, f'{img_name}_{key}.png')
                        self.plot_manager.plot_lines(
                            sub_df,
                            y_columns=y_cols,
                            x_column=x_col,
                            x_label='Date',
                            y_label=f'{y_label}',
                            title=f'{title}_{key}',
                            save_path=file_img,
                            bool_datetime=True
                        )
                print(f'[INFO] 绘制{title}曲线')
            except:
                print(f'[ERROR] 未找到文件{csv_name}.csv')


# ===============================
# 示例主程序
# ===============================
if __name__ == "__main__":
    analysis = MacroAnalysis()
    # analysis.plot_data('macro', star_index=3)
    analysis.plot_data('stock', star_index=2)


