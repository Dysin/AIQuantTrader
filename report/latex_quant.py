'''
@Desc:   量化交易分析报告
@Author: Dysin
@Date:   2026/1/31
'''

from datetime import datetime
from report.latex_base import ReportBase

class LatexQuant(ReportBase):
    def __init__(self):
        self.date = f"{datetime.now().strftime('%Y%m%d')}"
        self.title = f"量化交易分析报告"
        report_dir = 'quantitative_trading'
        report_filename = f'{self.date}_{self.title}'
        super().__init__(
            report_dir,
            report_filename
        )

    def analysis(self):
        self.latex.first_page(
            main_title=self.title,
            sub_title='股票'
        )
        self.latex.code += (
            '投资收益表如下：\n'
        )
        table_fin = [
            ['','值'],
            ['初始交易时间', ''],
            ['初始资金',''],
            ['总收益率', ''],
            ['交易次数','']
        ]
        self.latex.code += self.latex.insert_table(
            data=table_fin,
            caption='投资收益表',
            label='fin',
            alignment='cc',
            position='H'
        )
        self.latex.save_and_compile()

if __name__ == '__main__':
    latex = LatexQuant()
    latex.analysis()