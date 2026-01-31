'''
@Desc:   Latex report基类
@Author: Dysin
@Date:   2026/1/21
'''

import os
from report.latex_utils import LatexUtils
from utils.params_manager import PathManager
from utils.files_utils import FileUtils
from utils.images_utils import ImageUtils
from utils.logger import get_logger
logger = get_logger(__name__)

class ReportBase(object):
    def __init__(
            self,
            path_root,
            report_dirname: str,
            report_filename: str,
            model_number: str,
            version_number: str,
    ):
        '''
        报告输出基类
        :param path_root: 项目路径
        :param report_dirname: 报告文件夹名
        :param report_filename: 报告文件名
        :param model_number: 项目型号
        :param version_number: 项目版本号
        '''
        self.pm = PathManager(path_root, False)
        self.report_dirname = report_dirname
        self.report_filename = report_filename

        self.path_latex = os.path.join(
            self.pm.path_reports,
            self.report_dirname,
        )
        self.path_latex_images = os.path.join(self.path_latex, 'images')
        os.makedirs(self.path_latex_images, exist_ok=True)
        self.latex_images_utils = FileUtils(
            self.path_latex_images
        )

        self.model_number = model_number
        self.proj_name = model_number.replace('-', '')
        self.version_number = version_number

        self.latex = LatexUtils(
            path=self.path_latex,
            file_name=self.report_filename
        )

    def convert_images(self):
        '''
        BMP图片转换为PNG，并从计算算例路径复制到报告images路径
        :return:
        '''
        path_simulation = os.path.join(
            self.pm.path_simulation,
            self.report_dirname
        )
        files_images = FileUtils(path_simulation)
        image_manager = ImageUtils()
        image_names = files_images.get_file_names_by_type('.bmp')
        logger.info(f'Starting image conversion and copying')
        for image_name in image_names:
            image_manager.bmp_to_png(
                path_simulation,
                self.path_latex_images,
                image_name,
                add_border=True
            )
        logger.info(f'Finished | {self.path_latex_images}')

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