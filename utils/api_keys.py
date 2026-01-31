'''
@Desc:   存放各类网站 API Key
@Author: Dysin
@Date:   2025/10/5
'''

class APIKey:
    '''
    美国 FRED
    网址：https://fred.stlouisfed.org/
    '''
    fred = "c6be0c00e85f28241281a8b75320a9b3"

    '''
    网址：https://tushare.pro/
    '''
    tushare = "53b40ebf619a61b51d5b8ff1f6dcbbc3302eb388ff95ecdb11411eef"

    '''
    Trading Economics
        - 提供各国宏观经济、指标、预测数据，覆盖国别很多，适合做跨国比较与宏观事件分析。
        - 免费 API 限制比较严格；有些深度数据需要订阅。
    网址：https://developer.tradingeconomics.com/
    获取API Key：https://developer.tradingeconomics.com/Home/Keys
    '''
    trading_economics = 'd46f36fd76934c5:fx47591iprf95nl'

    '''
    AKShare
        - AKShare是一个基于Python的开源财经数据接口库
        - 它的目标是为量化分析、财经研究、学术科研提供 统一、便捷、免费 的数据接口
        - 它从多个公开数据源（政府网站、交易所、券商、基金网站等）自动抓取数据并封装成pandas DataFrame格式
    网址：https://akshare.akfamily.xyz/index.html
    '''


# ---------- 数据库配置 ----------
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '8008',
    'database': 'financial_data',
    'charset': 'utf8mb4'
}