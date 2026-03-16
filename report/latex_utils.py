'''
@Desc:   输出latex报告
@Author: Dysin
@Date:   2025/10/13
'''

import sys
import os.path
import re
import subprocess
from utils.logger import get_logger
logger = get_logger(__name__)

class LatexUtils:
    def __init__(
            self,
            path,
            file_name,
            date=None
    ):
        self.date = date if date else r"\today"  # 默认为今天的日期
        self.path = path
        self.file_name = file_name
        self.latex_file = os.path.join(path, f'{file_name}.tex')
        self.code = ''
        self.preamble()

    def image_name_to_list(self, image_name):
        # 匹配：变量_轴值  例如 atomization_velocity_z5e-05
        pattern = r'([a-zA-Z_]+)_([xyz])([\-+]?\d*\.?\d+(?:[eE][\-+]?\d+)?)$'
        match = re.match(pattern, image_name)
        if match:
            var_name = match.group(1)  # 变量名，如 atomization_velocity
            axis = match.group(2)  # x/y/z
            value_str = match.group(3)  # 数值部分，含科学计数法
            try:
                value = float(value_str)
            except ValueError:
                raise ValueError(f"无法解析数值：{value_str}")
            # 返回最后一个字段的名字（如 velocity）
            return [var_name.split('_')[-1], axis, value]
        # 不匹配就原样返回，保证程序安全
        return image_name

    def preamble(self, header=None):
        image_path = os.path.join(self.path, 'images')
        image_path = image_path.replace('\\', '/')
        self.code += (
            '\\documentclass[12pt]{article}\n'
            '\\usepackage[utf8]{inputenc}\n'
            '\\usepackage{geometry}\n'
            '\\usepackage{ctex}  % 支持中文\n'
            '\\usepackage{graphicx} % 用于插入图片\n'
            '\\usepackage{caption} % 自定义图注\n'
            '\\usepackage{float} % 在导言区添加\n'
            '\\usepackage{subcaption} % 用于子图\n'
            '\\usepackage{fancyhdr} % 引入页眉页脚宏包\n'
            '\\usepackage{booktabs} % 用于绘制三线表\n'
            '\\usepackage{amsmath}  % 在导言区添加\n'
            '\\usepackage{hyperref} % 引用标签\n'
            '\\geometry{a4paper, margin=1in}\n\n'
        )
        if header is not None:
            self.code += (
                '\\pagestyle{fancy} %设置页面样式为fancy\n'
                '\\fancyhf{} %清除所有页眉页脚设置\n'
                f'\\fancyhead[L]{{{header}}} %中页眉\n'
                '\\renewcommand{\\headrulewidth}{0.2pt} %页眉下方横线宽度\n\n'
            )
        self.code += '\\begin{document}\n\n'
        self.code += (
            '% 图片路径设置（根据实际情况修改）\n'
            f'\\graphicspath{{{{{image_path}/}}}} % 图片存放在images文件夹中\n\n'
        )

    def insert_figure(
            self,
            name,
            title,
            tag,
            image_height=3,
            image_width=None
    ):
        if image_width is None:
            image_size_name = "height"
            image_size = image_height
        else:
            image_size_name = "width"
            image_size = image_width
        self.code += (
            '\\begin{figure}[H]\n'
            '\t\\centering\n'
            f'\t\\includegraphics[{image_size_name}={image_size}cm]{{{name}.png}} %图片文件名\n'
            f'\t\\caption{{{title}}}\n'
            f'\t\\label{{fig: {tag}}}\n'
            '\\end{figure}\n\n'
        )

    def insert_figures_per_row(
            self,
            image_names,
            captions,
            main_captions,
            width=None
    ):
        '''
        生成多页 LaTeX 图片代码（每行 m 列，共 n 行）
        :param image_names: list[list[str]] 二维列表，每行表示一行图片（n 行 m 列）
        :param captions: list[list[str]] | None与image_names对应的子图标题（可选）
        :param main_captions: list[str] 每页主标题（与 image_names 行数对应）
        :param width: 图片宽度
        :return:
        '''
        n_rows = len(image_names)
        print(f"[INFO] total rows: {n_rows}")
        print(f"[INFO] main captions num: {len(main_captions)}")
        assert len(main_captions) >= n_rows, "main_captions 数量不足"
        for i, row_images in enumerate(image_names):
            m_cols = len(row_images)
            row_captions = captions[i] if captions is not None else [None] * m_cols
            main_caption = main_captions[i]
            # 每个 figure 块
            self.code = "\\begin{figure}[H]\n    \\centering\n"
            lab_imgs = []
            for j, img in enumerate(row_images):
                if not img:
                    continue
                # 控制每张图的宽度（最大0.4）
                # - 2行：0.4
                # - 3行：0.3
                # - 4行：0.23
                if width is None:
                    width = min(round(0.9 / m_cols, 2), 0.4)
                self.code += f"    \\begin{{subfigure}}[b]{{{width}\\textwidth}}\n"
                self.code += f"        \\includegraphics[width=\\textwidth]{{{img}}}\n"
                if row_captions[j]:
                    self.code += f"        \\caption{{{row_captions[j]}}}\n"
                self.code += f"        \\label{{fig:{img}}}\n"
                self.code += f"    \\end{{subfigure}}\n"
                if j != m_cols - 1:
                    self.code += "    \\hfill\n"
                lab_imgs.append(img)
            lab_main = f'{lab_imgs[0]}_{lab_imgs[1]}'
            # 主标题
            self.code += f"\n    \\caption{{{main_caption}}}\n"
            self.code += f"    \\label{{fig:{lab_main}}}\n\\end{{figure}}\n\n"

    def insert_table(
            self,
            data,
            caption=None,
            label=None,
            alignment=None,
            position="htbp"
    ):
        """
        生成 LaTeX 三线表代码
        参数:
        data -- 二维列表，包含表格数据（第一行通常为表头）
        caption -- 表格标题（可选）
        label -- 表格引用标签（可选）
        alignment -- 列对齐方式字符串，如 "lcr"（可选，默认为所有列居中）
        position -- 表格位置参数，如 "htbp"（可选）
        """

        # 确定列数
        n_cols = len(data[0])

        # 设置默认对齐方式
        if alignment is None or len(alignment) != n_cols:
            alignment = "c" * n_cols

        # 确保 self.code 已初始化
        if not hasattr(self, "code") or self.code is None:
            self.code = ""

        # 表格环境开始
        self.code += f"\\begin{{table}}[{position}]\n"
        self.code += "\\centering\n"

        if caption:
            self.code += f"\\caption{{{caption}}}\n"
        if label:
            self.code += f"\\label{{{label}}}\n"

        # tabular 环境
        self.code += f"\\begin{{tabular}}{{{alignment}}}\n"
        self.code += "\\toprule\n"

        # 表头
        header = " & ".join(str(cell) for cell in data[0])
        self.code += header + " \\\\\n"
        self.code += "\\midrule\n"

        # 数据行
        for row in data[1:]:
            row_str = " & ".join(str(cell) for cell in row)
            self.code += row_str + " \\\\\n"

        # 表格结束
        self.code += "\\bottomrule\n"
        self.code += "\\end{tabular}\n"
        self.code += "\\end{table}\n\n"

    def first_page(
            self,
            main_title,
            sub_title
    ):
        self.code += (
            '\\begin{center}\n'
            '\t\\vspace*{3cm} % 顶部垂直间距调整\n\n'
            # '\t\\begin{figure}[H]\n'
            # '\t\\centering\n'
            # '\t\\includegraphics[height=5cm]{E:/1_Work/images/logo.jpg}\n'
            # '\t\\end{figure}\n\n'
            '\t\\vspace{3\\baselineskip}\n\n'
            '\t% 主标题（加大字号）\n'
            f'\t{{\\Huge \\textbf{{{main_title}}}}}\n\n'
            '\t\\bigskip\n\n'
            '\t% 副标题\n'
            f'\t{{\\Large {sub_title}}}\n\n'    
            '\t% 间隔N行\n'
            '\t\\vspace{10\\baselineskip}\n\n'   
            '\t\\vspace{1\\baselineskip} % 部门与姓名间距\n\n'
            '\t% 姓名\n'
            '\tDysin\n\n'
            '\t\\vspace{1\\baselineskip} % 姓名与日期间距\n\n'
            '\t% 日期（自动生成当前日期）\n'
            '\t\\today\n\n'
            '\\end{center}\n\n'
            '\\thispagestyle{empty} % 隐藏第一页页码\n\n'
            '\\newpage\n\n'
            '\\setcounter{page}{1} % 重置页码为1\n\n'
        )

    def end(self):
        self.code += (
            '\n\\end{document}\n'
        )

    def save_to_file(self):
        """
        将生成的 LaTeX 文档保存为 `.tex` 文件。
        :param filename: 文件名，默认是 `report.tex`
        """
        self.end()
        with open(self.latex_file, "w", encoding="utf-8") as f:
            f.write(self.code)
        logger.info(f"Latex file saved as {self.latex_file}")

    def compile_pdf(self, output_path=None, pdflatex_path=None):
        '''
        使用 pdflatex 编译生成 PDF 文件，并输出到指定路径。
        :param output_path: PDF 输出目录（可选，默认为源文件所在目录）
        :param pdflatex_path: pdflatex 可执行文件的完整路径（可选）
        :return:
        '''
        # 确定输出目录
        if output_path:
            # 确保输出目录存在
            os.makedirs(output_path, exist_ok=True)
        else:
            output_path = self.path
        # 确定 pdflatex 可执行文件路径
        if pdflatex_path:
            executable = pdflatex_path
        else:
            # 尝试自动查找常见路径
            if sys.platform.startswith('win'):
                executable = "pdflatex.exe"
            else:
                executable = "/usr/bin/pdflatex"
        try:
            # 构建编译命令
            command = [
                executable,
                "-interaction=nonstopmode",  # 非交互模式，遇到错误不暂停
                "-output-directory", output_path,  # 指定输出目录
                self.latex_file  # 源文件
            ]
            # 执行编译
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
            )
            # 检查编译日志
            if "Error" in result.stdout:
                logger.error("Compilation error occurred:")
                logger.error(result.stdout)
                return False
            logger.info(
                f'PDF compilation successful: ' +
                os.path.join(output_path, f'{self.file_name}.pdf')
            )
            return True
        except FileNotFoundError:
            logger.error(f"Pdflatex not found: {executable}")
            logger.error("Please ensure Latex is installed and added to PATH")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"PDF compilation failed with error code: {e.returncode}")
            return False

    def save_and_compile(self):
        self.save_to_file()
        self.compile_pdf()
        self.compile_pdf()