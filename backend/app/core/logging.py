import logging
import sys


def setup_logging() -> None:
    """初始化全局日志配置，在应用启动时调用一次。

    basicConfig 是 Python 自带的日志快捷配置；这里统一了输出格式，
    并把日志打印到 stdout（终端），方便初学者直接看到运行日志。
    """
    logging.basicConfig(
        level=logging.INFO,  # 只输出 INFO 及以上级别日志
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],  # 输出到终端
    )
