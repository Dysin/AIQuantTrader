'''
@Desc:   log输出
@Author: Dysin
@Date:   2026/1/9
'''

import logging
import os
import sys
from pathlib import Path
from datetime import datetime

# ANSI颜色
COLOR_RESET = "\033[0m"
COLOR_DEBUG = "\033[36m"   # 青色
COLOR_INFO = "\033[37m"    # 白色
COLOR_WARNING = "\033[33m" # 黄色
COLOR_ERROR = "\033[31m"   # 红色
COLOR_CRITICAL = "\033[41m" # 红底

class ColoredFormatter(logging.Formatter):
    """控制台彩色日志"""
    LEVEL_COLOR = {
        "DEBUG": COLOR_DEBUG,
        "INFO": COLOR_INFO,
        "WARNING": COLOR_WARNING,
        "ERROR": COLOR_ERROR,
        "CRITICAL": COLOR_CRITICAL
    }

    def format(self, record):
        # 临时加颜色，不破坏原 record
        levelname = record.levelname
        color = self.LEVEL_COLOR.get(levelname, COLOR_INFO)
        record.levelname = f"{color}{levelname}{COLOR_RESET}"
        result = super().format(record)
        record.levelname = levelname  # 恢复原始值
        return result


def get_logger(name: str, path: str = None):
    current = Path(__file__).resolve()
    src_path_root = current.parent.parent
    print(src_path_root)
    if path is None:
        path = os.path.join(
            src_path_root.parent,
            'logs'
        )
    """获取 logger，控制台彩色，文件无色"""
    os.makedirs(path, exist_ok=True)

    log_file = os.path.join(
        path,
        f"{datetime.now().strftime(f'%Y%m%d%H')}.log"
    )

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if not logger.handlers:
        # 控制台 stdout (DEBUG/INFO)
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)
        stdout_handler.setFormatter(ColoredFormatter(
            "[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))

        # 控制台 stderr (WARNING+)
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.WARNING)
        stderr_handler.setFormatter(ColoredFormatter(
            "[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))

        # 文件输出（无颜色）
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            "[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))

        logger.addHandler(stdout_handler)
        logger.addHandler(stderr_handler)
        logger.addHandler(file_handler)

    return logger


if __name__ == '__main__':
    logger = get_logger(__name__)

    logger.debug("调试信息")  # 控制台青色，文件写入
    logger.info("INFO 白色")  # 控制台白色，文件写入
    logger.warning("WARNING 黄色")  # 控制台黄色，文件写入
    logger.error("ERROR 红色")  # 控制台红色，文件写入
    logger.critical("CRITICAL 红底")  # 控制台红底，文件写入
