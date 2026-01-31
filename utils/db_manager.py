'''
@Desc:   MySQL 数据库管理封装（支持自动创建数据库）
@Author: Dysin
@Date:   2025/10/6
'''

import pandas as pd
import pymysql
from sqlalchemy import create_engine, text
from utils.api_keys import MYSQL_CONFIG


class DBManager:
    """数据库管理器类 - 专用于 MySQL 连接与数据写入"""

    def __init__(self):
        # 初始化时建立 MySQL 连接
        self.engine = self._connect_mysql()

    # ==================== MySQL 连接部分 ====================
    def _connect_mysql(self):
        """建立 MySQL 连接（若数据库不存在则自动创建）"""
        cfg = MYSQL_CONFIG

        # 不指定数据库的连接字符串（用于创建数据库）
        base_conn_str = (
            f"mysql+pymysql://{cfg['user']}:{cfg['password']}"
            f"@{cfg['host']}:{cfg['port']}/?charset={cfg['charset']}"
        )

        # 目标数据库连接字符串
        target_conn_str = (
            f"mysql+pymysql://{cfg['user']}:{cfg['password']}"
            f"@{cfg['host']}:{cfg['port']}/{cfg['database']}?charset={cfg['charset']}"
        )

        try:
            # 1️⃣ 尝试连接目标数据库
            engine = create_engine(target_conn_str)
            with engine.connect():
                print(f"[Info] ✅ 已连接 MySQL 数据库：{cfg['database']}")
            return engine

        except pymysql.err.OperationalError as e:
            # 2️⃣ 捕获“数据库不存在”的错误号 1049
            if e.args[0] == 1049:
                print(f"[Warning] ⚠️ 数据库 '{cfg['database']}' 不存在，正在自动创建...")

                # 先连到 MySQL 根目录（不带数据库）
                base_engine = create_engine(base_conn_str)
                with base_engine.connect() as conn:
                    conn.execute(
                        text(f"CREATE DATABASE IF NOT EXISTS `{cfg['database']}` "
                             f"DEFAULT CHARACTER SET {cfg['charset']}")
                    )
                    print(f"[Success] ✅ 数据库 '{cfg['database']}' 已创建。")
                base_engine.dispose()

                # 再次连接新建的数据库
                engine = create_engine(target_conn_str)
                print(f"[Info] ✅ 已连接到新创建的数据库：{cfg['database']}")
                return engine

            else:
                raise e  # 其他错误直接抛出

        except Exception as e:
            print(f"[Error] ❌ 无法连接 MySQL：{e}")
            raise e

    # ==================== 数据保存部分 ====================
    def save_dataframe(self, df: pd.DataFrame, table_name: str, if_exists='replace'):
        """
        保存 DataFrame 到 MySQL 数据库
        :param df: pandas DataFrame
        :param table_name: 表名
        :param if_exists: 表已存在时的行为（默认'replace'，可选'append'）
        """
        if df.empty:
            print(f"[Warning] ⚠️ 表 {table_name} 数据为空，跳过保存。")
            return

        try:
            df.to_sql(
                name=table_name,
                con=self.engine,
                if_exists=if_exists,
                index=False
            )
            print(f"[Success] ✅ 数据已保存到表：{table_name}")
        except Exception as e:
            print(f"[Error] ❌ 数据库保存失败：{e}")
