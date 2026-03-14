'''
@Desc:   量化交易分析报告
@Author: Dysin
@Date:   2026/1/31
'''

import pandas as pd
from datetime import datetime
from report.latex_base import ReportBase

class LatexQuant(ReportBase):
    def __init__(self):
        self.date = f"{datetime.now().strftime('%Y%m%d')}"
        self.title = f"量化交易分析报告"
        report_dir = f'quantitative_trading_{self.date}'
        report_filename = f'{self.date}_{self.title}'
        super().__init__(
            report_dir,
            report_filename
        )

    def analysis(self, date_start, engine, metrics):
        self.latex.first_page(
            main_title=self.title,
            sub_title='股票'
        )
        date_start = pd.to_datetime(f"{date_start}").strftime("%Y-%m-%d")

        self.latex.code += (
            f"初始交易日期：{date_start}\n\n"
        )

        self.latex.code += (
            f"\\section{{策略收益指标}}\n"
        )

        self.latex.code += (
            '投资收益表如下：\n'
        )
        table_fin = [
            ['','CNY'],
            ['初始资金', f"{engine['init_cash']:.2f}"],
            ['最终资产', f"{engine['final_equity']:.2f}"],
            ['累计收益', f"{engine['cumulative_return']:.2f}"],
            ['总收益率', f"{engine['total_return']*100:.2f}\%"],
            ['年化收益', f"{metrics['annual_return']*100:.2f}\%"],
            ['年化波动率', f"{metrics['annual_volatility']*100:.2f}\%"],
            ['最大回撤', f"{metrics['max_drawdown']*100:.2f}\%"],
            ['胜率', f"{metrics['win_rate']*100:.2f}\%"],
            ['夏普比率', f"{metrics['sharpe_ratio']:.2f}"],
            ['索提诺比率', f"{metrics['sortino_ratio']:.2f}"],
            ['年化收益/最大回撤', f"{metrics['calmar_ratio']:.2f}"],
            ['交易次数', engine['trade_count']]
        ]
        self.latex.insert_table(
            data=table_fin,
            caption='投资收益表',
            label='fin',
            alignment='cc',
            position='H'
        )

        self.latex.code += (
            f"\\section{{净值曲线}}\n"
        )

        self.latex.code += (
            "净值曲线如图\\ref{fig: equity}所示：\n"
        )

        self.latex.insert_figure(
            name="equity",
            title="净值曲线",
            tag="equity",
            image_height=6
        )

        self.latex.code += (
            "策略净值与Benchmark对比曲线如图\\ref{fig: equity_vs_sp500}所示：\n"
        )

        self.latex.insert_figure(
            name="equity_vs_sp500",
            title="策略净值与SP500对比",
            tag="equity_vs_sp500",
            image_height=6
        )

        self.latex.code += (
            "累计收益曲线如图\\ref{fig: cumulative_return}所示：\n"
        )

        self.latex.insert_figure(
            name="cumulative_return",
            title="累计收益曲线",
            tag="cumulative_return",
            image_height=6
        )

        self.latex.save_and_compile()

if __name__ == '__main__':
    latex = LatexQuant()