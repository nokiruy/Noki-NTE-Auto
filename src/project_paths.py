"""统一管理源码目录与打包后程序目录。"""

from pathlib import Path
import sys


SOURCE_DIR = Path(__file__).resolve().parent

if getattr(sys, "frozen", False):
    APP_ROOT = Path(sys.executable).resolve().parent
else:
    APP_ROOT = SOURCE_DIR.parent

