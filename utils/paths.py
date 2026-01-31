"""
@Desc:   项目路径管理
@Author: Dysin
@Time:   2025/9/17
"""

from pathlib import Path


class PathManager:
    """
    项目路径管理类
    - 统一管理项目目录
    - 自动创建必要目录
    """

    def __init__(self, root: Path | None = None):
        # 项目根目录（允许外部传入，默认取当前文件上三级）
        self.root_dir = (
            root.resolve()
            if root
            else Path(__file__).resolve().parents[2]
        )

        # 目录结构统一定义
        self._dirs = {
            "images": self.root_dir / "images",
            "data": self.root_dir / "data",
            "data_macro": self.root_dir / "data" / "macro",
            "data_stock": self.root_dir / "data" / "stock",
            "logs": self.root_dir / "logs",
            "source": self.root_dir / "source",
            "third_party": self.root_dir / "source" / "third_party",
            "files": self.root_dir / "files",
        }

        # 自动创建目录
        for path in self._dirs.values():
            path.mkdir(parents=True, exist_ok=True)

    # ---------- 基础访问 ----------

    def get(self, name: str) -> Path:
        """获取目录 Path"""
        return self._dirs[name]

    def join(self, name: str, filename: str) -> Path:
        """在指定目录下拼接文件路径"""
        return self._dirs[name] / filename

    # ---------- 兼容原有接口（可选） ----------

    @property
    def images_dir(self) -> Path:
        return self._dirs["images"]

    @property
    def data_dir(self) -> Path:
        return self._dirs["data"]

    @property
    def data_stock_dir(self) -> Path:
        return self._dirs["data_stock"]

    @property
    def logs_dir(self) -> Path:
        return self._dirs["logs"]

if __name__ == '__main__':
    path_utils = PathManager()
    path = path_utils.get('images')
    print(path)