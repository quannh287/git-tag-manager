"""
Git Tag Manager - Công cụ tự động hóa việc đánh version cho các dự án Git.

Hỗ trợ cả CLI và GUI, với dynamic pattern cho mọi định dạng tag.
"""

__version__ = "1.0.0"
__author__ = "QuanNH"

from .core import (
    CONFIG_PATH,
    load_config,
    save_config,
    run_git,
    get_tag_info,
    get_commit_info,
    open_config_file,
)

__all__ = [
    "__version__",
    "CONFIG_PATH",
    "load_config",
    "save_config",
    "run_git",
    "get_tag_info",
    "get_commit_info",
    "open_config_file",
]
