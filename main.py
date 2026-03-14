'''
@Desc:   主函数入口
@Author: Dysin
@Date:   2026/1/27
'''

from workflow.stock import WorkflowStock

if __name__ == '__main__':
    # path_manager = PathManager()
    # path_stock = path_manager.data_stock
    # csv_stock = os.path.join(path_stock, 'us_stock_daily_AAPL.csv')
    # df = pd.read_csv(csv_stock, index_col="date")
    # print(df)
    # calc = StockTradeCalculator(
    #     df,
    #     fee_buy=0.0003,
    #     fee_sell=0.0003,
    #     stamp_tax=0.001,
    #     annual_interest_rate=0.03
    # )
    # result = calc.calculate_trade(
    #     buy_time=pd.Timestamp("2015-12-10"),
    #     sell_time=pd.Timestamp("2016-08-01"),
    #     shares=1000
    # )
    # for k, v in result.items():
    #     logger.info(f"{k}: {v:.2f}")
    #
    # print('================')


    WorkflowStock().test()