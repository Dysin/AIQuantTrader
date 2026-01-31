'''
@Desc:   Latex report基类
@Author: Dysin
@Date:   2026/1/21
'''

import os
from report.latex_utils import LatexUtils
from utils.paths import PathManager
from utils.files import FileUtils
from utils.logger import get_logger
logger = get_logger(__name__)

class ReportBase(object):
    def __init__(
            self,
            report_dirname: str,
            report_filename: str,
    ):
        '''
        报告输出基类
        :param path_root: 项目路径
        :param report_dirname: 报告文件夹名
        :param report_filename: 报告文件名
        :param model_number: 项目型号
        :param version_number: 项目版本号
        '''
        self.pm = PathManager()
        self.report_dirname = report_dirname
        self.report_filename = report_filename

        self.path_latex = os.path.join(
            self.pm.reports,
            self.report_dirname,
        )
        self.path_latex_images = os.path.join(self.path_latex, 'images')
        os.makedirs(self.path_latex_images, exist_ok=True)
        self.latex_images_utils = FileUtils(
            self.path_latex_images
        )

        self.latex = LatexUtils(
            path=self.path_latex,
            file_name=self.report_filename
        )

    def embed_single_figure(
            self,
            txt,
            search_string,
            main_captions=None
    ):
        '''
        在文档中插入单个算例的一批图片，如压力云图等
        :return:
        '''

        image_names = self.latex_images_utils.filter_star_filenames(
            search_string=search_string,
            suffix_to_remove='.png'
        )
        if main_captions is None:
            main_captions = self.latex.pair_caption_list(image_names)
        res = (f'{self.model_number}不同{txt}如下图所示：\n')
        res += self.latex.insert_figures_per_row(
            image_names=image_names,
            captions=None,
            main_captions=main_captions
        )
        return res