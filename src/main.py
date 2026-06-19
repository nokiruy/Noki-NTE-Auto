print("开始初始化脚本UI界面等")
print("如果卡住请尝试按回车键(Enter),或者管理员身份重启脚本")
for _ in range(6):
    print("工具免费，禁止通过任何方式收费，如果付费请要求商家退款，并帮忙举报倒卖")
import tkinter as tk
import tempfile

from tkinter import ttk
import threading
import time
import os
import json
import ntplib
import datetime

import ctypes
from tkinter import messagebox
from pathlib import Path
import sys
import subprocess
from tkinter import scrolledtext
from io import BytesIO
import webbrowser
from PIL import Image, ImageDraw, ImageFont, ImageTk
import atexit
from tkinter import font
from ctypes import wintypes
import keyboard
import logging
import io
import shutil
import hashlib
from project_paths import APP_ROOT
from ui_theme import COLORS, apply_modern_theme, polish_legacy_widgets

from 任务执行器 import 执行器

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(lineno)d]%(message)s",
    handlers=[

        logging.StreamHandler()
    ]
)
logger = logging.getLogger("database")
logger.setLevel(logging.DEBUG)
# 屏蔽 PIL.PngImagePlugin 模块的日志
png_logger = logging.getLogger("PIL.PngImagePlugin")
png_logger.setLevel(logging.WARNING)


# 2. 屏蔽特定模块的日志
def suppress_module_logs(module_names, level=logging.WARNING):
    """屏蔽指定模块的日志输出"""
    for name in module_names:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        # 移除所有处理器，防止输出
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        # 阻止传播到根记录器
        logger.propagate = False


# 在导入任何模块前屏蔽日志
suppress_module_logs([
    "RapidOCR",  # 主模块
    "PIL",  # Python Imaging Library
    "PIL.PngImagePlugin"  # PNG处理插件
])




def set_best_dpi_awareness():
    """设置最佳的DPI感知级别"""
    try:
        # 尝试设置每显示器DPI感知
        awareness = ctypes.c_int(2)
        ctypes.windll.shcore.SetProcessDpiAwareness(awareness)
        print("ctypes.c_int(2)")
        return True
    except:
        try:
            # 回退到系统DPI感知
            awareness = ctypes.c_int(1)
            ctypes.windll.shcore.SetProcessDpiAwareness(awareness)
            print("ctypes.c_int(1)")
            return True
        except:
            print("ctypes.c_int(False)")
            return False  # 设置失败

set_best_dpi_awareness()




def get_system_dpi():
        # 加载用户 32 动态链接库
        user32 = ctypes.windll.user32
        # 获取系统 DPI
        dpi = wintypes.UINT()
        # 使用 GetDpiForSystem 函数获取系统 DPI
        # 注意：GetDpiForSystem 函数在 Windows 8.1 及更高版本中可用
        user32.GetDpiForSystem.restype = wintypes.UINT
        dpi.value = user32.GetDpiForSystem()
        return dpi.value
    # 输出系统的 DPI
print(f"系统 DPI：{get_system_dpi()}/96={int(get_system_dpi() / 96 * 100)}%")
系统DPI = get_system_dpi() / 96


import cv2
import logging

def 初始化OpenCL():
    """
    尝试启用 OpenCL 加速，返回是否可用。
    失败时不会崩溃，只记录日志。
    """
    try:
        # 有些 OpenCV 构建可能没有 ocl 模块
        if not hasattr(cv2, 'ocl'):
            logger.warning("当前 OpenCV 不包含 ocl 模块，GPU 加速不可用")
            return False

        # 先检查硬件支持
        if not cv2.ocl.haveOpenCL():
            logger.warning("系统不支持 OpenCL，GPU 加速不可用")
            return False

        # 启用全局 OpenCL 优先级
        cv2.ocl.setUseOpenCL(True)
        logger.info(f"OpenCL 已启用，使用设备: {cv2.ocl.Device.getDefault().name()}")
        return True

    except Exception as e:
        logger.error(f"初始化 OpenCL 时发生异常: {e}，将回退到 CPU")
        return False

# ---------- 尝试开启cv2GPU加速，是否使用由用户在GUI自行选择----------
使用OpenCL = 初始化OpenCL()
from 连接adb import 中途连接模拟器, 预先连接mumu模拟器2, 查找符合条件的顶级窗口, \
    get_window_handles_by_path_no_psutil, 根据窗口句柄获取窗口类名和标题
from mumu模拟器启动器 import MuMu非管理员启动器, MUMU判断模拟器是否完全启动, 获取mumu可用端口
from 雷电模拟器启动器 import 雷电判断模拟器是否完全启动 ,Leidian非管理员启动器,获取雷电可用端口
from 游戏截图保存到内存 import check_resolution,  获取_png_数据, 函数截图到内存, \
    获取_png_data
from 连接adb import 关闭电脑应用, 获取模拟器客户区句柄, 精确查找所有窗口句柄,从文件提取路径,get_seconds_to_target_time,函数精确查找窗口句柄
from 模拟器截图复制到剪切板 import  接收数据复制到剪切板
from adb操作 import 获取所有设备端口
from 窗口假激活 import 线程持续激活
from 检查更新 import 检查更新
from 异环任务 import  店长特供,超强音,异环钓鱼,速切宏战斗线程,速切宏战斗线程2,自动剧情,自动按F,鼠标快速打开esc界面


from 连接adb import  获取模拟器应用路径,monitor_and_restore_window_position
import 后台点击再次封装


import ast


if getattr(sys, 'frozen', False):
    current_dir = Path(sys.executable).parent.absolute()

else:
    current_dir = APP_ROOT

路径 = current_dir / "game.json"
路径.parent.mkdir(parents=True, exist_ok=True)
列表=[
    ["UnityWndClass", "HeavenBurnsRed"],
      ["UnrealWindow", "幻塔  "],
       ["UnrealWindow", "鸣潮  "],
["UnrealWindow", "NTE  "],
["UnrealWindow", "异环  "],
      ]

if not 路径.exists():
    with open(路径, 'w', encoding='utf-8') as file:
        json.dump({"端游列表": 列表}, file)  # 初始化为空列表，根据需求可改为{}

线程事件任务循环 = threading.Event()
# 将事件对象导出到睡眠倍数模块
import 睡眠倍数模块
睡眠倍数模块.线程事件任务循环 = 线程事件任务循环
脚本运行速度=1
睡眠倍数模块.脚本运行速度=脚本运行速度
线程事件任务循环.clear()
线程事件自定义战斗轴循环 = threading.Event()
线程事件自定义战斗轴循环.clear()
线程事件停止循环 = threading.Event()
线程事件停止循环.clear()
更新UI线程事件 = threading.Event()
更新UI线程事件.clear()

current_selected = -1  # 记录当前选中索引

notebook = None  # 存储Notebook对象
图标数据表 = []  # 存储每个选项卡的图标数据

import platform

print("初始化OCR实例成功")
def get_windows_version():
    """
    获取Windows版本信息
    返回: 字符串，如 'Windows-10', 'Windows-11'
    """
    # 首先检查是否是Windows系统
    if sys.platform != 'win32':
        return "Not Windows"

    # 获取系统版本信息
    version_info = platform.win32_ver()

    # win32_ver() 返回元组: (系统名称, 版本号, 补丁包, 处理器架构)
    # 例如: ('10', '10.0.19045', 'SP0', 'Multiprocessor Free')

    # 版本号判断
    # Windows 10: 10.0.10240 到 10.0.19045
    # Windows 11: 10.0.22000 及以上

    version_number = version_info[1]  # 例如: '10.0.19045'
    major_minor_build = version_number.split('.')

    if len(major_minor_build) >= 3:
        build_number = int(major_minor_build[2])

        if build_number >= 22000:
            print(f"当前系统:Windows 11")
            return True
        else:
            print(f"当前系统不是Windows 10")
            return False
    else:
        print(f"当前系统不是Windows 10")
        return False
当前为win11=get_windows_version()
def 限制脚本运行速度(value):
    """
    验证并转换脚本运行速度
    输入：从GUI获取的值（字符串或其他类型）
    输出：验证后的浮点数
    """
    try:
        # 尝试转换为浮点数
        speed = float(value)
    except (ValueError, TypeError):
        # 转换失败，返回默认值1
        return 1.0

    # 边界检查
    if speed < 0.1:
        return 0.1
    elif speed > 10.0:
        return 10.0
    else:
        return speed
def 检查窗口分辨率(矩形, 目标分辨率):
    x, y = 目标分辨率
    a, b, c, d = 矩形
    宽度 = c - a
    高度 = d - b
    后台点击再次封装.x比例=宽度/x
    后台点击再次封装.x比例 = 高度 / x
    resolution_valid = False
    if 宽度 == x and 高度 == y:
        logger.debug("分辨率正确101")
        resolution_valid = True
    else:
        错误信息 = f"游戏现在分辨率为: {宽度}x{高度}"
        logger.debug(错误信息)
        # 弹窗提示
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror(f"分辨率错误",
                             f"要求分辨率为{x}*{y}，{错误信息}"
                             f"\n请自行调整游戏分辨率，如果还是不行或者游戏调整不到这个分辨率，请严格按照下面步骤一步一步调整，不要跳过任何一步"
                             f"\n\n最好不要外接显示屏，然后请循环以下操作："
                             f"\n1.关闭游戏与启动器，"
                             f"\n2.调整电脑文本缩放为100%，"
                             f"\n3.打开游戏，把游戏分辨率调整为{x}*{y}，"
                             f"\n4.再次运行脚本，没有分辨率报错就是可以了"
                             f"\n5.如果依然报错且分辨率显示为{x}*xxx则进行以下步骤：把游戏分辨率调整到一个非全屏的16：9的分辨率（如2560*1440，1600*900）再调回{x}*{y}，然后运行脚本，"
                             f"\n6.依然同样报错显示现在分辨率显示为{x}*xxx则换一个非全屏的16：9的分辨率继续步骤5"
                             f"\n7.重复多次步骤5后依然分辨率不对则尝试电脑关机开机，然后继续从步骤3开始"
                             f"\n\n直至运行脚本不再分辨率报错")
        if getattr(sys, 'frozen', False):
            pass
        else:
            resolution_valid = True
            pass
    return resolution_valid
def 检查分辨率(adb路径):
    try:
        if check_resolution(adb路径):
            logger.debug("分辨率符合要求！")
            return True
        else:
            return False
    except RuntimeError as e:
        logger.error(f"分辨率不符合要求！{e}")
        return False
def 检查模拟器adb路径(adb_config):
    adb路径, 端口, hwnd, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb_config
    encoded_path = os.fsencode(adb路径)

    # 检查路径是否存在
    if not os.path.exists(encoded_path):
        error_message = f"路径文件不存在: {adb路径}"
        logger.error(error_message)
        错误信息 = f"模拟器adb不存在或者路径中存在脚本无法识别的字符: {error_message}"
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("路径错误", 错误信息)
        return False
    else:
        logger.debug(f"路径有效: {adb路径}")
        return True

def 获取模拟器路径并保存(hwnd):


    exe_path = 获取模拟器应用路径(hwnd)
    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent.absolute()
    else:
        current_dir = APP_ROOT

    txt_path = os.path.join(current_dir, 'app_path.txt')
    # 将 exe_path 写入到文件
    if hwnd:
        try:
            with open(txt_path, 'w', encoding='utf-8') as file:
                file.write(exe_path)
            logger.debug(f"路径已成功保存到 {txt_path}")
        except Exception as e:
            logger.warning(f"保存路径时出错: {e}")



def 安全打开应用(应用路径):
    """增强版：处理带引号、空格的路径"""
    try:
        # 去除首尾引号和空格
        应用路径 = 应用路径.strip().strip('"\'')

        if not os.path.exists(应用路径):
            logger.warning(f"应用程序路径不存在：{应用路径}")
            return False

        # 方法1：直接使用路径（推荐）
        subprocess.Popen([应用路径], shell=False)



        logger.info(f"成功打开应用：{应用路径}")
        return True
    except FileNotFoundError:
        logger.warning(f"应用程序不存在：{应用路径}")
        return False
    except PermissionError:
        logger.warning(f"没有权限执行应用程序：{应用路径}")
        return False
    except Exception as e:
        logger.warning(f"打开应用失败：{str(e)}")
        return False
def 安全打开文件(文件路径):
    """使用系统默认程序打开文件"""
    文件路径=str(文件路径)
    try:
        # 去除路径两端的引号、空格等多余字符
        文件路径 = 文件路径.strip().strip('"\'')
        if not os.path.exists(文件路径):
            logger.warning(f"文件路径不存在：{文件路径}")
            return False

        os.startfile(文件路径)  # Windows系统专用方法
        return True
    except Exception as e:
        logger.warning(f"打开文件失败：{str(e)}")
        return False
def 执行提示文本(配置键前缀):
    config_path = os.path.join(current_dir, 'web_and_app.json')
    if not os.path.exists(config_path):
        logger.warning(f"配置文件 {config_path} 不存在")
        return
    with open(config_path, "r", encoding="utf-8") as f:
        配置数据 = json.load(f)
    if 配置键前缀=="启动":
        if "脚本启动后提示文本变量" in 配置数据:
            if int(配置数据["脚本启动后提示文本变量"]):
                root = tk.Tk()
                root.withdraw()  # 隐藏主窗口
                messagebox.showinfo("脚本启动后提示", f"{配置数据['脚本启动后提示文本列表']}")

    elif 配置键前缀=="结束":
        if "脚本任务结束后提示文本变量" in 配置数据:
            if int(配置数据["脚本任务结束后提示文本变量"]):
                root = tk.Tk()
                root.withdraw()  # 隐藏主窗口
                messagebox.showinfo("脚本结束后提示", f"{配置数据['脚本任务结束后提示文本列表']}")
def 执行打开操作(配置键前缀, 打开类型):
    """通用打开操作函数
    参数说明：
        配置键前缀 - "脚本启动后" 或 "脚本任务结束后"
        打开类型 - "网站"/"应用"/"文件"
    """
    try:
        if getattr(sys, 'frozen', False):
            current_dir = Path(sys.executable).parent.absolute()
        else:
            current_dir = APP_ROOT

        config_path = os.path.join(current_dir, 'web_and_app.json')

        if not os.path.exists(config_path):
            logger.warning(f"配置文件 {config_path} 不存在")
            return

        with open(config_path, "r", encoding="utf-8") as f:
            配置数据 = json.load(f)

        # 检查开关状态
        开关状态 = 配置数据.get(f"{配置键前缀}打开{打开类型}变量", 0)
        if not 开关状态:
            logger.debug(f"{配置键前缀} {打开类型}打开开关未启用")
            return

        # 获取目标列表
        目标列表 = 配置数据.get(f"{配置键前缀}{打开类型}列表", "")
        targets = [t.strip() for t in 目标列表.split('\n') if t.strip()]

        if not targets:
            logger.warning(f"{配置键前缀} 未配置有效{打开类型}地址")
            return

        # 批量处理
        success_count = 0
        for target in targets:
            try:
                if 打开类型 == "网站":
                    if target.startswith(('http://', 'https://')):
                        webbrowser.open(target, new=2)
                        success_count += 1
                    else:
                        logger.warning(f"无效URL格式：{target}")
                elif 打开类型 == "应用":
                    if 安全打开应用(target):
                        success_count += 1
                elif 打开类型 == "文件":
                    if 安全打开文件(target):
                        success_count += 1
            except Exception as e:
                logger.warning(f"处理{打开类型} [{target}] 时出错：{str(e)}")

        logger.info(f"成功打开 {success_count}/{len(targets)} 个{打开类型}")

    except Exception as e:
        logger.warning(f"执行{打开类型}打开操作时发生全局错误：{str(e)}")
def 脚本启动后执行所有操作函数():
    for _ in range(10):
        time.sleep(1)
        if not 线程事件停止循环.is_set():
            logger.debug("开始执行脚本启动后行动")
            执行打开操作("脚本启动后", "文件")
            执行打开操作("脚本启动后", "网站")
            执行打开操作("脚本启动后", "应用")

            执行提示文本("启动")
            break
def 脚本启动后执行所有操作线程():
    threading.Thread(target=脚本启动后执行所有操作函数,
                     args=()).start()
def 任务结束后执行所有操作():
    执行打开操作("脚本任务结束后", "文件")
    执行打开操作("脚本任务结束后", "网站")
    执行打开操作("脚本任务结束后", "应用")

    执行提示文本("结束")
def hex_handle_to_decimal(hex_handle):
    """
    将十六进制窗口句柄转换为十进制

    参数:
        hex_handle (str): 十六进制表示的窗口句柄，如 "001B09D8"

    返回:
        int: 十进制表示的窗口句柄
    """
    try:
        # 去除可能的前缀（如果有的话）
        if hex_handle.startswith("0x"):
            hex_handle = hex_handle[2:]

        # 将十六进制字符串转换为十进制整数
        return int(hex_handle, 16)
    except ValueError as e:
        print(f"转换错误: {hex_handle} 不是有效的十六进制字符串")
        return None
def 获取adb路径并检查(检查线程=True,端口号=None,检查分辨率=True,事件循环=线程事件任务循环,事件停止=线程事件停止循环):
    if 端口号:
        hwnd=窗口矩形=PC全局延迟=PC键盘延迟=0
    else:

        with open(os.path.join(current_dir, 'Tool_Settings.json'), 'r', encoding='utf-8') as file:
            Tool_Settings = json.load(file)
        端口号 = Tool_Settings["端口号变量"]
        客户端选择 = int(Tool_Settings["客户端选择变量"])
        PC全局延迟 = float(Tool_Settings["PC全局延迟变量"])
        if PC全局延迟 < 0:
            PC全局延迟 = 0
        PC键盘延迟 = float(Tool_Settings["PC键盘延迟变量"])
        if PC键盘延迟 < 0:
            PC键盘延迟 = 0
        hwnd = 0
        窗口矩形 = 0
        if 客户端选择 == 1:
            路径 = current_dir / "game.json"
            with open(路径, 'r', encoding='utf-8') as file:
                data = json.load(file)
            端游列表 = data["端游列表"]
            hwnd = 0
            for 端游 in 端游列表:
                窗口列表 = 精确查找所有窗口句柄(端游[0], 端游[1], )
                if 窗口列表:
                    for 元组 in 窗口列表:
                        hwnd, 窗口矩形 = 元组

                        if str(hwnd) == str(端口号):
                            logger.debug(f"游戏句柄是：{hwnd}")
                            logger.debug(f"窗口矩形是：{窗口矩形}")
                            break
                    else:
                        hwnd = 0

                if hwnd:
                    break
            else:
                logger.debug("未能找到游戏窗口！")
                root = tk.Tk()
                root.withdraw()  # 隐藏主窗口
                messagebox.showerror("错误",
                                     "未能找到游戏窗口！\n请确保游戏已打开，然后在工具主界面重新绑定游戏")
                事件循环.clear()
                事件停止.clear()
                return  # 如果未找到窗口句柄，退出函数

            获取模拟器路径并保存(hwnd)
            目标分辨率 = (1280, 720)
            if 检查分辨率:
                resolution_valid = 检查窗口分辨率(窗口矩形, 目标分辨率)
                if not resolution_valid:
                    事件循环.clear()


        截图方式 = Tool_Settings["截图方式变量"]
        截图方式 = str(截图方式)
        if 客户端选择 == 1:
            截图方式 = "PC端窗口"
        else:
            中途连接模拟器()
            if 截图方式 == "PC端窗口":
                if "MuMu" in 端口号:
                    窗口列表 = 查找符合条件的顶级窗口(目标窗口类名="Qt5156QWindowIcon", 目标窗口标题="MuMuPlayer", )
                    if 窗口列表:
                        MuMu句柄 = 窗口列表[0]
                        print(f"MuMu句柄: {MuMu句柄}")
                        MuMupath = Path(获取模拟器应用路径(MuMu句柄))
                        启动器 = MuMu非管理员启动器(播放器路径=MuMupath)
                        端口元组 = ast.literal_eval(端口号)
                        多开号 = 端口元组[1]
                        信息 = 启动器.安全获取虚拟机信息("all")

                        数据 = json.loads(信息)

                        值 = 数据[多开号]
                        if "main_wnd" in 值:
                            hwnd = 值["main_wnd"]

                            hwnd=hex_handle_to_decimal(str(hwnd))

                            获取模拟器路径并保存(hwnd)
                            if 检查线程:
                                hwnd = 获取模拟器客户区句柄(hwnd, 事件循环)
                                if not hwnd:
                                    hwnd = 0
                                    事件循环.clear()
                            else:
                                hwnd = 0
                        else:
                            logger.error("main_wnd不存在，该端口PC端截图不可用")
                            return 0

                    else:
                        logger.error("未找到mumu窗口，可能是模拟器版本导致，该端口PC端截图不可用")
                        return 0


                elif "雷电" in 端口号:
                    窗口列表 = 查找符合条件的顶级窗口(目标窗口类名="RenderWindow", 目标窗口标题="TheRender", )
                    if 窗口列表:
                        雷电MuMu句柄 = 窗口列表[0]
                        print(f"雷电句柄: {雷电MuMu句柄}")
                        雷电MuMupath = Path(获取模拟器应用路径(雷电MuMu句柄))
                        启动器 = Leidian非管理员启动器(播放器路径=雷电MuMupath)
                        端口元组 = ast.literal_eval(端口号)
                        多开号 = 端口元组[1]
                        信息 = 启动器.安全获取虚拟机信息()
                        数据列表 = [行.strip().split(',') for 行 in 信息.split('\n') if 行.strip()]
                        hwnd=0
                        for 行数据 in 数据列表:
                            if 行数据[0]==str(多开号):
                                hwnd=int(行数据[2])
                                获取模拟器路径并保存(hwnd)
                                if 检查线程:
                                    hwnd = 获取模拟器客户区句柄(hwnd, 事件循环)
                                    if not hwnd:
                                        hwnd = 0
                                        事件循环.clear()
                                else:
                                    hwnd = 0
                else:
                    hwnd = 0
                    Tool_Settings["截图方式变量"]="模拟器ADB"
                    with open(Path(current_dir)/"Tool_Settings.json", 'w', encoding='utf-8') as file:
                        json.dump(Tool_Settings, file, ensure_ascii=False, indent=4)


            else:
                hwnd = 0


    if "MuMu" in 端口号:
        窗口列表 = 查找符合条件的顶级窗口(目标窗口类名="Qt5156QWindowIcon", 目标窗口标题="MuMuPlayer", )
        if 窗口列表:
            MuMu句柄 = 窗口列表[0]
            print(f"MuMu句柄: {MuMu句柄}")
            MuMupath = Path(获取模拟器应用路径(MuMu句柄))
            启动器 = MuMu非管理员启动器(播放器路径=MuMupath)
            if isinstance(MuMupath, str):
                MuMupath = Path(MuMupath)

                # 获取父目录，然后拼接adb.exe
            adb程序 = MuMupath.parent / "adb.exe"
            if adb程序.exists():
                logger.info(f"MuMuadb: {adb程序}")
            else:
                logger.error(f"文件；{adb程序}，不存在")
                return 0
        else:
            logger.error("未找到mumu窗口，可能是模拟器版本导致，该端口PC端截图不可用")
            return 0
        try:
            端口元组=ast.literal_eval(端口号)
        except (SyntaxError, ValueError) as e:
            logger.error(f"转换失败: {e}")
            logger.error(f"输入字符串: {端口号}")
            return 0
        except Exception as e:
            logger.error(f"未知错误: {e}")
            return 0
        多开号=端口元组[1]
        信息 = 启动器.安全获取虚拟机信息("all")
        try:
            数据 = json.loads(信息)

            值=数据[多开号]
            if "adb_host_ip" in 值:
                端口号 = f'{值["adb_host_ip"]}:{值["adb_port"]}'
            else:
                logger.error("adb_host_ip不存在")
                return 0
        except json.JSONDecodeError:
            logger.error(f"解析JSON数据失败")
            return 0
        command = [adb程序, 'connect', 端口号]
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    elif "雷电" in 端口号:
        窗口列表 = 查找符合条件的顶级窗口(目标窗口类名="RenderWindow", 目标窗口标题="TheRender", )
        if 窗口列表:
            雷电MuMu句柄 = 窗口列表[0]
            print(f"雷电句柄: {雷电MuMu句柄}")
            雷电MuMupath = Path(获取模拟器应用路径(雷电MuMu句柄))
            if isinstance(雷电MuMupath, str):
                雷电MuMupath = Path(雷电MuMupath)

                # 获取父目录，然后拼接adb.exe
            adb程序 = 雷电MuMupath.parent / "adb.exe"
            if adb程序.exists():
                logger.info(f"雷电adb: {雷电MuMupath}")
            else:
                logger.error(f"文件；{adb程序}，不存在")
                return 0
        else:
            return 0
        try:
            端口元组 = ast.literal_eval(端口号)
        except (SyntaxError, ValueError) as e:
            logger.error(f"转换失败: {e}")
            logger.error(f"输入字符串: {端口号}")
            return 0
        except Exception as e:
            logger.error(f"未知错误: {e}")
            return 0
        多开号 = 端口元组[1]
        端口号=f"emulator-{5554+2*(int(多开号))}"


    adb程序 = current_dir / "platform-tools" / "adb.exe"
    adb路径 = (adb程序, 端口号, hwnd, 窗口矩形, (PC全局延迟, PC键盘延迟))
    with open(os.path.join(current_dir, 'Tool_Settings.json'), 'r', encoding='utf-8') as file:
        Tool_Settings = json.load(file)
    客户端选择 = int(Tool_Settings["客户端选择变量"])

    if 检查线程:
        if 事件循环.is_set():
            if 客户端选择 == 2:
                if 获取_png_数据(adb路径, 包名="com.bilibili.heaven", x1=0, y1=0, x2=0, y2=0):
                    pass
                else:
                    事件循环.clear()
        if 事件循环.is_set():
            if 客户端选择 == 2:
                if 检查模拟器adb路径(adb路径):
                    pass
                else:
                    事件循环.clear()

        if 事件循环.is_set():
            if 客户端选择 == 2:
                if 检查分辨率(adb路径):
                    pass
                else:
                    事件循环.clear()

        if not 事件循环.is_set():

            adb路径=0
            print(f"not 事件循环.is_set()adb路径：{adb路径}")
    if getattr(sys, 'frozen', False):
        print(f"adb路径：{adb路径}")
    else:
        print(f"adb路径：{adb路径}")
    return adb路径

def 任务执行完成后关闭游戏(关闭游戏):
    with open(os.path.join(current_dir, 'Tool_Settings.json'), 'r', encoding='utf-8') as file:
        Tool_Settings = json.load(file)
    客户端选择 = int(Tool_Settings["客户端选择变量"])
    if 线程事件任务循环.is_set():
        if 关闭游戏:
            if 客户端选择 == 2:

                ds_path = os.path.join(current_dir, 'Tool_Settings.json')
                with open(ds_path, 'r', encoding='utf-8') as file:
                    Tool_Settings = json.load(file)
                端口号 = Tool_Settings["端口号变量"]
                if "MuMu" in 端口号:
                    窗口列表 = 查找符合条件的顶级窗口(目标窗口类名="Qt5156QWindowIcon", 目标窗口标题="MuMuPlayer", )
                    if 窗口列表:
                        MuMu句柄 = 窗口列表[0]
                        print(f"MuMu句柄: {MuMu句柄}")
                        MuMupath = Path(获取模拟器应用路径(MuMu句柄))
                        启动器 = MuMu非管理员启动器(播放器路径=MuMupath)
                        端口元组 = ast.literal_eval(端口号)
                        多开号 = 端口元组[1]
                        信息 = 启动器.安全获取虚拟机信息("all")

                        数据 = json.loads(信息)

                        值 = 数据[多开号]
                        if "main_wnd" in 值:
                            hwnd = 值["main_wnd"]
                            print(f"main_wnd:{hwnd}")
                            hwnd = hex_handle_to_decimal(str(hwnd))
                            关闭电脑应用(hwnd)
                elif "雷电" in 端口号:
                    窗口列表 = 查找符合条件的顶级窗口(目标窗口类名="RenderWindow", 目标窗口标题="TheRender", )
                    if 窗口列表:
                        雷电MuMu句柄 = 窗口列表[0]
                        print(f"雷电句柄: {雷电MuMu句柄}")
                        雷电MuMupath = Path(获取模拟器应用路径(雷电MuMu句柄))
                        启动器 = Leidian非管理员启动器(播放器路径=雷电MuMupath)
                        端口元组 = ast.literal_eval(端口号)
                        多开号 = 端口元组[1]
                        信息 = 启动器.安全获取虚拟机信息()
                        数据列表 = [行.strip().split(',') for 行 in 信息.split('\n') if 行.strip()]
                        hwnd = 0
                        for 行数据 in 数据列表:
                            if 行数据[0] == str(多开号):
                                hwnd = int(行数据[2])
                                关闭电脑应用(hwnd)

            elif 客户端选择 == 1:
                ds_path = os.path.join(current_dir, 'Tool_Settings.json')
                with open(ds_path, 'r', encoding='utf-8') as file:
                    Tool_Settings = json.load(file)
                端口号 = Tool_Settings["端口号变量"]
                路径 = current_dir / "game.json"
                with open(路径, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                端游列表 = data["端游列表"]
                hwnd = 0
                for 端游 in 端游列表:
                    窗口列表 = 精确查找所有窗口句柄(端游[0], 端游[1], )
                    if 窗口列表:
                        for 元组 in 窗口列表:
                            hwnd, 窗口矩形 = 元组

                            if str(hwnd) == str(端口号):
                                获取模拟器路径并保存(hwnd)
                                logger.debug(f"游戏句柄是：{hwnd}")
                                logger.debug(f"窗口矩形是：{窗口矩形}")
                                关闭电脑应用(hwnd)
                                break
                        else:
                            hwnd = None

                    if hwnd:
                        break

def 函数根据任务名启动任务线程(任务名):
    if "异环钢琴" in 任务名:
        adb路径 = 获取adb路径并检查(检查分辨率=False)
        游戏静音=False
    else:
        threading.Thread(target=monitor_and_restore_window_position,
                     args=(线程事件任务循环,)).start()
        adb路径 = 获取adb路径并检查(检查分辨率=True)
        游戏静音=True

    from 异环钢琴main import  转换并保存MIDI_支持静音区间, 多线程演奏_直接从内存, 多线程演奏
    if adb路径:
        _, _, 异环句柄, _, _ = adb路径
        threading.Thread(target=线程持续激活, args=(异环句柄, 线程事件任务循环, 游戏静音)).start()
        if 任务名 == "异环超强音":

            超强音(adb路径, current_dir, 线程事件任务循环)
        elif 任务名 == "异环店长特供":

            店长特供(adb路径, current_dir, 线程事件任务循环)
        elif 任务名 == "异环钓鱼":


            异环钓鱼(adb路径, current_dir, 线程事件任务循环, None)
            路径 = current_dir / "异环图片" / "钓鱼" / "钓鱼设置.json"
            with open(路径, 'r', encoding='utf-8') as file:
                字典 = json.load(file)
                异环钓鱼运行完毕后电脑关机 = int(字典["异环钓鱼运行完毕后电脑关机变量"])
                异环钓鱼运行完毕后关闭游戏 = int(字典["异环钓鱼运行完毕后关闭游戏变量"])


            if 线程事件任务循环.is_set():
                if 异环钓鱼运行完毕后电脑关机:
                    os.system('shutdown -s -t 0')
            任务执行完成后关闭游戏(异环钓鱼运行完毕后关闭游戏)


        elif 任务名 == "异环钢琴单曲":

            with open(current_dir.parent / "外置配置文件夹"/"演奏文件列表.json", 'r', encoding='utf-8') as f:
                数据 = json.load(f)


            filepath = 数据.get("filepath")

            演奏轨道 = 数据.get("演奏轨道", (0, 1, 2, 3, 4, 5, 6))

            压缩方式 = 数据.get("压缩方式", "最大覆盖中心八度直接裁剪")

            key加减 = 数据.get("key加减", 0)

            生成json = 数据.get("生成json", False)

            垂直反转映射 = 数据.get("垂直反转映射变量", False)

            水平反转映射 = 数据.get("水平反转映射变量", False)
            演奏速度=数据.get("异环钢琴演奏速度变量", 1.0)
            # 调用转换函数（只使用选中的轨道）

            音轨按键操作字典 = 转换并保存MIDI_支持静音区间(

                Path(filepath), current_dir.parent / "外置配置文件夹"/"演奏文件", 暂停区间字典=None,

                保存文件=生成json, 压缩方式=压缩方式, 升降key=key加减,

                演奏轨道元组=演奏轨道,垂直反转映射=垂直反转映射,水平反转映射=水平反转映射

            )

            if 音轨按键操作字典:

                多线程演奏_直接从内存(异环句柄, 音轨按键操作字典, 线程事件任务循环,演奏速度)

            else:

                print("没有可演奏的音轨")


        elif 任务名 == "异环钢琴JSON":
            with open(current_dir.parent / "外置配置文件夹"/"演奏文件列表.json", 'r', encoding='utf-8') as f:
                数据 = json.load(f)
            folderpath = 数据.get("folderpath")
            _, _, 异环句柄, _, _ = adb路径
            演奏速度 = 数据.get("异环钢琴演奏速度变量", 1.0)

            # 直接演奏文件夹内所有 JSON

            json文件列表 = sorted(

                [os.path.join(folderpath, f) for f in os.listdir(folderpath) if f.endswith('.json')]

            )

            if json文件列表:

                多线程演奏(异环句柄, json文件列表, 线程事件任务循环,演奏速度)

            else:

                print("文件夹内无 JSON 文件")

        elif 任务名=="测试":
            if getattr(sys, 'frozen', False):
                线程事件任务循环.clear()
            else:
                pass
            messagebox.showinfo("提示",
                                f"测试任务为空，任务结束")
            线程事件任务循环.clear()
            线程事件停止循环.clear()
            return
    messagebox.showinfo("提示",
                        f"运行任务结束")
    线程事件任务循环.clear()
    线程事件停止循环.clear()
def 函数根据任务名启动任务(任务名):
    线程事件任务循环.set()
    线程事件停止循环.set()
    threading.Thread(target=函数根据任务名启动任务线程,
                     args=(任务名,)).start()
def 预先连接mumu模拟器启动线程():
    threading.Thread(target=预先连接mumu模拟器2,
                     args=()).start()





def 函数停止任务():
    if 线程事件停止循环.is_set():
        logger.debug("正在停止当前任务")
    else:
        logger.debug("没有正在运行的任务")
    线程事件任务循环.clear()

def 调整列表字符串长度(字符串列表):
    """
    将字符串列表中的每个元素调整为与最长字符串相同长度，左右均匀补全角空格

    参数：
        字符串列表: list[str] - 需要调整的原始字符串列表

    返回：
        list[str] - 调整后的字符串列表，所有元素长度一致（使用全角空格\u3000填充）
    """
    if not 字符串列表:
        return []

    # 获取最长字符串长度
    最长长度 = max(len(s) for s in 字符串列表)

    调整后列表 = []
    for 字符串 in 字符串列表:
        # 计算需要补齐的总空格数
        差额 = 最长长度 - len(字符串)
        if 差额 <= 0:
            调整后列表.append(字符串)
            continue

        # 分配左右空格数
        左空格 = 差额 // 2
        右空格 = 差额 - 左空格

        # 使用全角空格构建新字符串
        全角空格 = "\u3000"  # Unicode全角空格
        新字符串 = 全角空格 * 左空格 + 字符串 + 全角空格 * 右空格
        调整后列表.append(新字符串)

    return 调整后列表
global 测试面板adb路径
测试面板adb路径=None
global 战斗轴字典
战斗轴字典={}
global 战斗轴窗口字典
战斗轴窗口字典={}

class 子窗口管理器:
    def __init__(self, 父窗口, 图标路径=None):
        """
        初始化子窗口管理器

        参数:
            父窗口: 父级窗口对象
            图标路径: 窗口图标路径（可选）
        """
        self.父窗口 = 父窗口
        self.图标路径 = 图标路径
        self.窗口对象 = None

    def 创建子窗口(self, 标题="子窗口", 相对于鼠标=True, 父窗口对象=None, 水平偏移=0, 垂直偏移=-160):
        """
        创建并配置子窗口

        参数:
            标题: 窗口标题
            相对于鼠标: 是否根据鼠标位置调整窗口位置
            父窗口对象: 用于计算鼠标位置的父窗口（如为None则使用self.父窗口）
            水平偏移: 水平方向偏移量
            垂直偏移: 垂直方向偏移量

        返回:
            创建好的窗口对象
        """
        # 创建子窗口
        self.窗口对象 = tk.Toplevel(self.父窗口)

        # 记录鼠标位置（如果需要）
        if 相对于鼠标:
            参考窗口 = 父窗口对象 if 父窗口对象 else self.父窗口
            鼠标x = 参考窗口.winfo_pointerx()
            鼠标y = 参考窗口.winfo_pointery()
        else:
            鼠标x, 鼠标y = 0, 0

        # 初始隐藏窗口以配置
        self.窗口对象.withdraw()
        self.窗口对象.title(标题)

        # 设置图标（如果提供了路径）
        if self.图标路径:
            try:
                self.窗口对象.iconbitmap(self.图标路径)
            except:
                pass  # 图标设置失败时忽略

        # 窗口配置完成后，返回窗口对象供添加控件
        return self.窗口对象, 鼠标x, 鼠标y

    def 调整窗口位置(self, 窗口对象=None, 鼠标x=0, 鼠标y=0, 水平偏移=0, 垂直偏移=-160):
        """
        调整窗口位置，确保在屏幕内显示

        参数:
            窗口对象: 要调整的窗口（如为None则使用self.窗口对象）
            鼠标x: 鼠标水平坐标
            鼠标y: 鼠标垂直坐标
            水平偏移: 水平方向偏移量
            垂直偏移: 垂直方向偏移量
        """
        if 窗口对象 is None:
            窗口对象 = self.窗口对象

        if 窗口对象 is None:
            raise ValueError("未找到窗口对象，请先调用创建子窗口()")

        # 更新窗口以获取正确的尺寸
        窗口对象.update_idletasks()

        # 获取窗口尺寸
        窗口宽度 = 窗口对象.winfo_width()
        窗口高度 = 窗口对象.winfo_height()

        # 获取屏幕尺寸
        屏幕宽度 = 窗口对象.winfo_screenwidth()
        屏幕高度 = 窗口对象.winfo_screenheight()

        # 显示窗口
        窗口对象.deiconify()

        # 重新获取窗口尺寸（显示后可能变化）
        窗口宽度 = 窗口对象.winfo_width()
        窗口高度 = 窗口对象.winfo_height()

        # 计算调整后的位置，确保窗口完全在屏幕内
        # 如果窗口右边超出屏幕，调整到左侧显示
        if 鼠标x + 窗口宽度 > 屏幕宽度:
            调整x = max(0, 屏幕宽度 - 窗口宽度)
        else:
            调整x = 鼠标x

        # 如果窗口底部超出屏幕，调整到上方显示
        if 鼠标y + 窗口高度 > 屏幕高度:
            调整y = max(0, 屏幕高度 - 窗口高度)
        else:
            调整y = 鼠标y

        # 确保窗口不会超出屏幕左侧和顶部
        调整x = max(0, 调整x) + 水平偏移
        调整y = max(0, 调整y) + 垂直偏移
        调整x = max(0, 调整x)
        调整y = max(0, 调整y)
        # 设置窗口位置
        窗口对象.geometry(f"+{调整x}+{调整y}")

        return 调整x, 调整y

    def 快速创建(self, 标题="子窗口", 相对于鼠标=True, 父窗口对象=None, 水平偏移=0, 垂直偏移=-160):
        """
        快速创建并定位子窗口（一步完成）

        返回:
            创建好的窗口对象
        """
        窗口对象, 鼠标x, 鼠标y = self.创建子窗口(
            标题=标题,
            相对于鼠标=相对于鼠标,
            父窗口对象=父窗口对象,
            水平偏移=水平偏移,
            垂直偏移=垂直偏移
        )

        self.调整窗口位置(
            窗口对象=窗口对象,
            鼠标x=鼠标x,
            鼠标y=鼠标y,
            水平偏移=水平偏移,
            垂直偏移=垂直偏移
        )

        return 窗口对象

    def 获取窗口对象(self):
        """获取当前管理的窗口对象"""
        return self.窗口对象

    def 销毁窗口(self):
        """销毁当前管理的窗口"""
        if self.窗口对象:
            self.窗口对象.destroy()
            self.窗口对象 = None





def 函数主程序():

    global 幻塔脚本运行
    global 异环脚本运行
    幻塔脚本运行 = 0
    异环脚本运行 = 0
    游戏列表 = ["异环", "幻塔"]
    for 游戏 in 游戏列表:
        target_path = current_dir / f"{游戏}图片"
        if target_path.exists() and target_path.is_dir():#判断文件是否存在
            if 游戏 =="异环":
                异环脚本运行 = 1
                break
            elif 游戏 =="幻塔":
                幻塔脚本运行 = 1
                break
        else:
            print(f"文件夹 {target_path} 不存在")

    def 函数保存设置():
        global 脚本运行速度
        if getattr(sys, 'frozen', False):
            current_dir = os.path.dirname(os.path.abspath(sys.executable))
        else:
            current_dir = str(APP_ROOT)
        保存网站应用文件配置(current_dir)
        settings = {
            "定时启动变量": 定时启动变量.get(),
            "定时时间变量": 定时时间变量.get(),
            "客户端选择变量": 客户端选择变量.get(),
            "截图方式变量": 截图方式变量.get(),
            "端口号变量": 端口号变量.get(),
            "PC全局延迟变量": PC全局延迟变量.get(),
            "PC键盘延迟变量": PC键盘延迟变量.get(),
            "脚本运行速度变量": 脚本运行速度变量.get(),
            "异环游戏静音变量" :异环游戏静音变量.get(),
            "GPU加速识图变量": GPU加速识图变量.get(),
        }
        try:
            with open(Path(current_dir)/"Tool_Settings.json", 'w', encoding='utf-8') as file:
                json.dump(settings, file, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"保存设置时出错: {e}")
        脚本运行速度 = 限制脚本运行速度(脚本运行速度变量.get())
        睡眠倍数模块.脚本运行速度 = 脚本运行速度
        try:
            脚本运行速度 = float(脚本运行速度变量.get())
        except Exception as e:
            脚本运行速度 = 1


    def 加载设置():
        global 红烧脚本运行
        线程事件停止循环.set()
        if getattr(sys, 'frozen', False):
            current_dir = os.path.dirname(os.path.abspath(sys.executable))
        else:
            current_dir = str(APP_ROOT)
        加载网站应用文件配置(current_dir)

        Tool_path = Path(current_dir) / "Tool_Settings.json"
        try:

            with open(Tool_path, 'r', encoding='utf-8') as file:
                Tool_Settings = json.load(file)
            # 应用定时设置
            if "定时启动变量" in Tool_Settings:
                定时启动变量.set(Tool_Settings["定时启动变量"])

            if "定时时间变量" in Tool_Settings:
                定时时间变量.set(Tool_Settings["定时时间变量"])

            if "客户端选择变量" in Tool_Settings:
                客户端选择变量.set(Tool_Settings["客户端选择变量"])

            if "截图方式变量" in Tool_Settings:
                截图方式变量.set(Tool_Settings["截图方式变量"])

            if "端口号变量" in Tool_Settings:
                端口号变量.set(Tool_Settings["端口号变量"])

            if "PC全局延迟变量" in Tool_Settings:
                PC全局延迟变量.set(Tool_Settings["PC全局延迟变量"])

            if "PC键盘延迟变量" in Tool_Settings:
                PC键盘延迟变量.set(Tool_Settings["PC键盘延迟变量"])

            if "脚本运行速度变量" in Tool_Settings:
                脚本运行速度变量.set(Tool_Settings["脚本运行速度变量"])
            if "异环游戏静音变量" in Tool_Settings:
                异环游戏静音变量.set(Tool_Settings["异环游戏静音变量"])
            if "GPU加速识图变量" in Tool_Settings:
                GPU加速识图变量.set(Tool_Settings["GPU加速识图变量"])
        except FileNotFoundError:
            logger.warning(f"设置文件 {Tool_path} 不存在，将使用默认设置")
        except json.JSONDecodeError:
            logger.error(f"设置文件 {Tool_path} 格式错误，将使用默认设置")
        except Exception as e:
            logger.error(f"设置时出错: {e}")





        线程事件停止循环.clear()



    global logger
    class TextVariableWrapper:
        """自定义文本变量绑定器"""

        def __init__(self, text_widget):
            self.text_widget = text_widget
            # 绑定文本修改事件（可根据需要添加更多事件）
            self.text_widget.bind("<<Modified>>", self._on_text_change)
            self._variable = tk.StringVar()

        def _on_text_change(self, event=None):
            """当文本内容变化时更新变量"""
            if self.text_widget.edit_modified():
                self._variable.set(self.text_widget.get("1.0", "end-1c"))
                self.text_widget.edit_modified(False)  # 重置修改标志

        @property
        def variable(self):
            """获取绑定变量"""
            return self._variable

        def set(self, value):
            """设置文本框内容"""
            self.text_widget.delete("1.0", "end")
            self.text_widget.insert("1.0", value)
            self._variable.set(value)
    global notebook, 图标数据表, current_selected

    def 加载选项卡图标(选项卡配置列表):
        """
        加载每个选项卡的选中/未选中图标对
        参数：
            current_dir: Path 图片目录
            选项卡配置列表: list[tuple] 每个元组包含(选中图标路径, 未选中图标路径)
        返回：
            list[tuple] 加载后的图标对象列表
        """
        图标列表 = []
        for 选中图标, 未选中图标 in 选项卡配置列表:
            try:
                图标列表.append((选中图标, 未选中图标))
            except Exception as e:
                logger.error(f"加载图标失败：{str(e)}")
                # 创建备用空白图标
                空图标 = tk.PhotoImage(width=50, height=50)
                图标列表.append((空图标, 空图标))
        return 图标列表

    def 加载图片到标签(归属, 图片路径=current_dir / "UI" / "端口相关" / "端口不可用或未连接.png", 目标高度=100,
                       图片加载失败文本="加载失败"):
        try:
            # 加载默认错误提示图片 # 确保图片文件存在
            if not 图片路径.exists():
                raise FileNotFoundError(f"默认图片不存在: {图片路径}")

            img = Image.open(图片路径)
            # 保持相同的缩放比例
            原始宽度, 原始高度 = img.size
            目标高度 = 目标高度
            目标宽度 = int(原始宽度 * 目标高度 / 原始高度)

            img_resized = img.resize(
                (目标宽度, 目标高度),
                Image.Resampling.LANCZOS
            )

            # 更新显示
            default_photo = ImageTk.PhotoImage(img_resized)
            归属.config(image=default_photo)
            归属.image = default_photo
        except Exception as e:
            logger.error(f"加载默认图片失败: {str(e)}")
            try:
                # 创建纯黑背景图片
                目标宽度 = 目标高度  # 保持正方形显示
                黑色图片 = Image.new('RGB', (目标宽度, 目标高度), color='black')

                # 准备绘制文字
                draw = ImageDraw.Draw(黑色图片)

                font_size = max(14, 目标高度 // 8)
                font = None
                font_candidates = [
                    "arial.ttf",  # 跨平台
                    "msyh.ttc",  # Windows
                    "/System/Library/Fonts/SFNS.ttf",  # macOS
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Linux
                ]
                for font_path in font_candidates:
                    try:
                        font = ImageFont.truetype(font_path, font_size)
                        break
                    except:
                        continue
                if font is None:
                    font = ImageFont.load_default()
                    font.size = font_size  # 手动设置字号

                # 计算文字位置
                text = 图片加载失败文本
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (目标宽度 - text_width) / 2
                y = (目标高度 - text_height) / 2

                # 绘制带背景的文字
                draw.rectangle(
                    [x - 1, y - 1, x + text_width + 2, y + text_height + 2],
                    fill="black"
                )
                draw.text((x, y), text, fill="white", font=font)

                # 更新显示
                error_photo = ImageTk.PhotoImage(黑色图片)
                归属.config(image=error_photo)
                归属.error_image = error_photo
                logger.info("已显示错误替代图片")

            except Exception as inner_e:
                logger.critical(f"连错误图片都无法生成: {str(inner_e)}...")
                # 终极降级处理
                归属.config(image='')
                归属.image = None

    def 创建选项卡(选项卡标题, 图标对):
        """创建单个选项卡并初始化"""
        global notebook
        tab = ttk.Frame(
            notebook,
            style="App.TFrame",
            padding=(18, 16, 18, 16),
        )
        notebook.add(
            tab,
            text=选项卡标题,
            image=图标对[1],  # 初始显示未选中图标
            compound="top"
        )
        return tab

    def 调整图片返回元组(current_dir, 原始图片列表, 目标像素元组=(50, 50)):
        """
        精确缩放图片到目标尺寸（支持任意尺寸转换）
        参数：
            current_dir: Path对象，图片所在目录
            原始图片列表: list[str]，图片文件名列表
            目标像素元组: tuple[int, int]，目标宽高
        返回：
            list[tk.PhotoImage] 调整后的图片对象列表
        """
        调整后图像列表 = []
        宽度,高度=目标像素元组
        目标像素元组=(int(宽度*系统DPI), int(高度*系统DPI))
        for 图片文件名 in 原始图片列表:
            图片路径 = current_dir / 图片文件名

            if not 图片路径.exists():
                raise FileNotFoundError(f"图片文件 {图片路径} 不存在")

            try:
                # 加载原始图片
                原始图片 = tk.PhotoImage(file=图片路径)
                原始宽度 = 原始图片.width()
                原始高度 = 原始图片.height()
                目标宽度, 目标高度 = 目标像素元组

                # ========== 核心修正部分 ==========
                # 计算精确缩放比例（带小数保留）
                宽比例 = 目标宽度 / 原始宽度
                高比例 = 目标高度 / 原始高度

                # 第一阶段：使用subsample缩小
                if 宽比例 < 1 or 高比例 < 1:
                    # 计算最大缩小比例（取整避免小数）
                    subsample_x = max(1, round(1 / 宽比例))
                    subsample_y = max(1, round(1 / 高比例))
                    调整后图片 = 原始图片.subsample(subsample_x, subsample_y)
                else:
                    # 需要放大时直接使用zoom
                    zoom_x = max(1, round(宽比例))
                    zoom_y = max(1, round(高比例))
                    调整后图片 = 原始图片.zoom(zoom_x, zoom_y)

                # 第二阶段：精确调整
                current_width = 调整后图片.width()
                current_height = 调整后图片.height()

                # 计算剩余需要调整的比例（确保不小于1）
                delta_x = max(1, 目标宽度 / current_width)
                delta_y = max(1, 目标高度 / current_height)

                # 使用二次缩放补足差值
                调整后图片 = 调整后图片.zoom(
                    int(delta_x),
                    int(delta_y)
                )

                # 第三阶段：裁剪到精确尺寸（防止超出目标尺寸）
                调整后图片 = 调整后图片.subsample(
                    max(1, 调整后图片.width() // 目标宽度),
                    max(1, 调整后图片.height() // 目标高度)
                )
                # ========== 修正结束 ==========

                调整后图像列表.append(调整后图片)

                # 调试输出
                #logger.debug(f"[成功] {图片文件名} 原始尺寸：{原始宽度}x{原始高度}")
                #logger.debug(f"       -> 调整后尺寸：{调整后图片.width()}x{调整后图片.height()}")

            except Exception as e:
                raise RuntimeError(f"处理图片 {图片文件名} 失败: {str(e)}")
        调整后图像元组 = tuple(调整后图像列表)
        return 调整后图像元组

    def 更新图标状态(event=None):
        """更新所有选项卡的图标显示状态"""
        global current_selected, 图标数据表

        # 获取新选中索引
        new_selected = notebook.index("current")

        # 更新前一个选中项
        if current_selected != -1:
            notebook.tab(current_selected, image=图标数据表[current_selected][1])

        # 更新新选中项
        if new_selected != -1:
            notebook.tab(new_selected, image=图标数据表[new_selected][0])

        current_selected = new_selected


    脚本运行 = True

    def 脚本启动后执行所有操作():
        脚本启动后执行所有操作线程()

    def 新方式集合启动任务(任务名):
        if 线程事件停止循环.is_set():
            error_message = f"线程事件对象已经存在: {线程事件任务循环}"
            错误信息 = f"当前还有任务正在运行，请关闭该弹窗后，点击任意停止按钮等待任务停止后重试，或者重新打开脚本\n  {error_message}"
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("线程错误", 错误信息)
        else:
            函数保存设置()

            线程事件停止循环.set()

            函数根据任务名启动任务(任务名)







    app_icon_path = current_dir / "图片" / "app_iconhbr.png"
    if 幻塔脚本运行:
        app_icon_path = current_dir / "幻塔图片" / "app_iconHottA.png"
    elif 异环脚本运行:
        app_icon_path = current_dir / "异环图片" / "app_iconNTE.png"
    app_logo_path = app_icon_path
    window = tk.Tk()
    window.withdraw()  # 隐藏窗口
    current_version = "0.0.1"
    if 幻塔脚本运行:
        current_version ="0.0.1"
    if 异环脚本运行:
        current_version = "1.5.43"
    title = f"NHAuto-v{current_version} bilibili@NOKIRUY"
    window.title(title)

    def 版本更新提示窗口(文本, 标题="版本更新提示"):
        global 幻塔脚本运行
        tooltip_window = tk.Toplevel(window)
        鼠标x = window.winfo_pointerx()
        鼠标y = window.winfo_pointery()

        tooltip_window.withdraw()

        tooltip_window.title(标题)
        tooltip_window.iconbitmap(app_icon_path)  # 设置图标
        if 幻塔脚本运行:
            entry = tk.Entry(tooltip_window, font=("微软雅黑", 16),)
            entry.insert(0, "更新网站: https://github.com/nokiruy/Noki-NTE-Auto/releases")
            entry.pack(fill=tk.BOTH, expand=True)
        if 异环脚本运行:
            entry = tk.Entry(tooltip_window, font=("微软雅黑", 16), )
            entry.insert(0, "github: https://github.com/nokiruy/Noki-NTE-Auto/releases"
                            )
            entry.pack(fill=tk.BOTH, expand=True)
            entry = tk.Entry(tooltip_window, font=("微软雅黑", 16), )
            entry.insert(0,
                            "百度网盘:https://pan.baidu.com/s/1k02bSxDGAkqbqt4com68Ng?pwd=saki 提取码: saki")
            entry.pack(fill=tk.BOTH, expand=True)

            entry = tk.Entry(tooltip_window, font=("微软雅黑", 16), )
            entry.insert(0,
                         "123网盘(下载速度快):https://1835681195.share.123pan.cn/123pan/1WJ4Td-9SxP3?pwd=saki# 提取码：saki")
            entry.pack(fill=tk.BOTH, expand=True)
        tooltip_label = tk.Label(
            tooltip_window,
            text=文本,
            font=("微软雅黑", 20),
            justify=tk.LEFT,
            padx=10,
            pady=10
        )
        tooltip_label.pack(fill=tk.BOTH, expand=True)

        tooltip_window.update_idletasks()

        # 获取窗口尺寸
        窗口宽度 = tooltip_window.winfo_width()
        窗口高度 = tooltip_window.winfo_height()

        # 获取屏幕尺寸
        屏幕宽度 = tooltip_window.winfo_screenwidth()
        屏幕高度 = tooltip_window.winfo_screenheight()

        tooltip_window.deiconify()

        # 获取窗口尺寸
        窗口宽度 = tooltip_window.winfo_width()
        窗口高度 = tooltip_window.winfo_height()

        print(f"{窗口宽度}x{窗口高度},{屏幕宽度}x{屏幕高度}")
        # 计算调整后的位置，确保窗口完全在屏幕内
        # 如果窗口右边超出屏幕，调整到左侧显示
        if 鼠标x + 窗口宽度 > 屏幕宽度:
            调整x = max(0, 屏幕宽度 - 窗口宽度)
        else:
            调整x = 鼠标x

        # 如果窗口底部超出屏幕，调整到上方显示
        if 鼠标y + 窗口高度 > 屏幕高度:
            调整y = max(0, 屏幕高度 - 窗口高度)
        else:
            调整y = 鼠标y

        # 确保窗口不会超出屏幕左侧和顶部
        调整x = max(0, 调整x)
        调整y = max(0, 调整y)

        print(f"{窗口宽度}x{窗口高度},{屏幕宽度}x{屏幕高度},{调整x}x{调整y}")

        # 设置窗口位置并显示
        tooltip_window.geometry(f"+{调整x}+{调整y}")
        tooltip_window.attributes('-topmost', True)  # 置顶

    def create_temp_ico():
        img = Image.open(app_icon_path)

        # 创建内存中的ICO文件
        with tempfile.NamedTemporaryFile(suffix='.ico', delete=False) as tmp:
            img.save(tmp, format='ICO', sizes=[(32, 32), (48, 48), (64, 64)])
            temp_path = tmp.name

        # 注册退出时删除临时文件
        atexit.register(os.remove, temp_path)
        return temp_path

    app_icon_path = create_temp_ico()

    window.iconbitmap(app_icon_path)
    窗口管理器 = 子窗口管理器(window, 图标路径=app_icon_path)
    style = apply_modern_theme(window)
    style.configure("TNotebook", tabposition="wn")

    屏幕宽度 = window.winfo_screenwidth()
    屏幕高度 = window.winfo_screenheight()
    窗口宽度 = min(1460, int(屏幕宽度 * 0.92))
    窗口高度 = min(900, int(屏幕高度 * 0.88))
    窗口x = max(0, (屏幕宽度 - 窗口宽度) // 2)
    窗口y = max(0, (屏幕高度 - 窗口高度) // 2)
    window.geometry(f"{窗口宽度}x{窗口高度}+{窗口x}+{窗口y}")
    window.minsize(min(1080, 屏幕宽度 - 80), min(680, 屏幕高度 - 80))

    主窗口外壳 = ttk.Frame(window, style="App.TFrame", padding=(16, 14, 16, 16))
    主窗口外壳.pack(fill="both", expand=True)

    顶栏 = ttk.Frame(主窗口外壳, style="Header.TFrame", padding=(16, 12))
    顶栏.pack(fill="x", pady=(0, 12))
    顶栏.columnconfigure(1, weight=1)

    try:
        顶栏图标图像 = Image.open(app_logo_path).convert("RGBA")
        顶栏图标图像.thumbnail((44, 44), Image.Resampling.LANCZOS)
        顶栏图标 = ImageTk.PhotoImage(顶栏图标图像)
        顶栏图标标签 = ttk.Label(顶栏, image=顶栏图标, style="Card.TLabel")
        顶栏图标标签.image = 顶栏图标
        顶栏图标标签.grid(row=0, column=0, rowspan=2, padx=(0, 12))
    except Exception as e:
        logger.debug(f"顶栏图标加载失败: {e}")

    ttk.Label(顶栏, text="Noki NTE Auto", style="HeaderTitle.TLabel").grid(
        row=0, column=1, sticky="sw"
    )
    ttk.Label(
        顶栏,
        text="异环自动化工具 · 任务、截图与运行设置集中管理",
        style="HeaderSubtitle.TLabel",
    ).grid(row=1, column=1, sticky="nw")
    ttk.Label(顶栏, text=f"v{current_version}", style="Badge.TLabel").grid(
        row=0, column=2, rowspan=2, padx=(8, 0)
    )
    ttk.Label(顶栏, text="免费开源", style="SuccessBadge.TLabel").grid(
        row=0, column=3, rowspan=2, padx=(8, 0)
    )

    # 创建 Notebook 并指定样式
    notebook = ttk.Notebook(主窗口外壳, style="TNotebook")
    notebook.pack(fill="both", expand=True)
    # 绑定事件
    notebook.bind("<<NotebookTabChanged>>", 更新图标状态)
    UI路径 = current_dir / "UI" / "脚本UI"
    后缀 = ""

    选项卡配置 = [
        调整图片返回元组(UI路径, [f"任务蓝{后缀}.png", f"任务黑{后缀}.png"], (28, 28)),
        调整图片返回元组(UI路径, [f"其他任务蓝{后缀}.png", f"其他任务黑{后缀}.png"], (28, 28)),
        调整图片返回元组(UI路径, [f"启动结束蓝{后缀}.png", f"启动结束黑{后缀}.png"], (28, 28)),
        调整图片返回元组(UI路径, [f"其他蓝{后缀}.png", f"其他黑{后缀}.png"], (28, 28)),

    ]
    选项卡标签列表 = ["任务中心", "任务详情", "启动与结束", "通用设置"]
    调整后列表 = 选项卡标签列表

    图标数据表 = 加载选项卡图标(选项卡配置)
    配置序号 = 0
    选项卡任务列表 = 创建选项卡(调整后列表[配置序号], 图标数据表[配置序号])
    配置序号 = 配置序号 + 1

    选项卡其他任务加载 = 创建选项卡(调整后列表[配置序号], 图标数据表[配置序号])
    配置序号 = 配置序号 + 1

    其他任务设置 = 创建选项卡(调整后列表[配置序号], 图标数据表[配置序号])
    配置序号 = 配置序号 + 1

    其他任务设置2 = 创建选项卡(调整后列表[配置序号], 图标数据表[配置序号])
    配置序号 = 配置序号 + 1

    配置序号 = 配置序号 + 1

    选项卡任务列表.grid_columnconfigure(0, weight=0)  # 容器1，不扩展
    选项卡任务列表.grid_columnconfigure(1, weight=1)  # 容器2，可扩展
    选项卡任务列表.grid_columnconfigure(2, weight=0)  # 容器3，不扩展
    选项卡任务列表.grid_rowconfigure(0, weight=1)  # 行0可扩展

    其他任务设置.columnconfigure(0, weight=1)

    其他任务设置2.columnconfigure(0, weight=1)

    按钮基础样式 = {
        "bg": COLORS["accent"],
        "fg": "#FFFFFF",
        "activebackground": COLORS["accent_hover"],
        "activeforeground": "#FFFFFF"
    }

    def 创建按钮2grid(归属, 标签, 绑定函数, 字体配置=("微软雅黑", 12), width=8, height=1, 位置=0, 位置2=0,sy="" ,**kwargs):
        显式样式 = kwargs.pop("style", None)
        任务按钮标签 = {
            "异环钢琴", "异环钓鱼", "店长特供", "超强音",
            "自动战斗", "自动闪避弹刀", "自动按F", "更多任务",
        }
        if 显式样式:
            style_name = 显式样式
        elif 标签 in {"❓", "?"}:
            style_name = "Icon.TButton"
        elif "停止" in 标签 or "结束任务" in 标签:
            style_name = "Danger.TButton"
        elif "启动任务" in 标签 or "开始演奏" in 标签 or "点击启用" in 标签:
            style_name = "Primary.TButton"
        elif 标签 in 任务按钮标签:
            style_name = "Task.TButton"
        else:
            style_name = "TButton"


        按钮实例 = ttk.Button(
            归属,
            text=标签,
            command=绑定函数,
            style=style_name,
            width=width,
            cursor="hand2",
            **kwargs
        )

        按钮实例.grid(row=位置, column=位置2, padx=5, pady=5, sticky=sy or "ew")
        return 按钮实例
    复选框基础样式 = {
        "bg": COLORS["surface"],
        "fg": COLORS["text"],
        "activebackground": COLORS["surface"],
        "activeforeground": COLORS["accent"],
        "highlightthickness": 0,
    }

    def 创建复选框grid(current_dir, 归属, 标签, 绑定变量, font=("微软雅黑", 12), 位置=0, 位置2=0, 边距x=0, 边距y=0, sy=tk.W, **kwargs):
        宽度 = int(45 * 系统DPI)
        高度 = int(宽度 / 2)

        # 初始化缓存字典（只执行一次）
        if not hasattr(创建复选框grid, "_img_cache"):
            创建复选框grid._img_cache = {}

        def 获取图片(文件名, 尺寸):
            路径 = current_dir / "UI" / "脚本UI" / 文件名
            key = (str(路径), 尺寸)  # 路径 + 尺寸做唯一键
            if key not in 创建复选框grid._img_cache:
                img = Image.open(路径)
                img = img.resize(尺寸)
                创建复选框grid._img_cache[key] = ImageTk.PhotoImage(img)
            return 创建复选框grid._img_cache[key]

        on_image = 获取图片("开关-开.png", (宽度, 高度))
        off_image = 获取图片("开关-关.png", (宽度, 高度))

        复选框实例 = tk.Checkbutton(
            归属,
            text=标签,
            variable=绑定变量,
            font=font,
            image=off_image,
            selectimage=on_image,
            indicatoron=False,
            onvalue=1,
            offvalue=0,
            compound=tk.LEFT,
            relief=tk.FLAT,
            overrelief=tk.FLAT,
            bd=0,
            **kwargs
        )
        复选框实例.grid(row=位置, column=位置2, padx=边距x, pady=边距y, sticky=sy)

        # 图片引用仍可保存，避免被回收（事实上缓存已经持有）
        复选框实例.off_image = off_image
        复选框实例.on_image = on_image

        def 鼠标进入事件(event):
            复选框实例.config(cursor="hand2")

        def 鼠标离开事件(event):
            复选框实例.config(cursor="")

        复选框实例.bind("<Enter>", 鼠标进入事件)
        复选框实例.bind("<Leave>", 鼠标离开事件)
        return 复选框实例

    def 创建单选框grid(current_dir, 归属, 标签, 绑定变量, 绑定变量值, font=("微软雅黑", 12), 位置=0, 位置2=0, 边距x=0, 边距y=0, sy="", **kwargs):
        图片大小 = int(25 * 系统DPI)

        if not hasattr(创建单选框grid, "_img_cache"):
            创建单选框grid._img_cache = {}

        def 获取图片(文件名, 尺寸):
            路径 = current_dir / "UI" / "脚本UI" / 文件名
            key = (str(路径), 尺寸)
            if key not in 创建单选框grid._img_cache:
                img = Image.open(路径)
                img = img.resize(尺寸)
                创建单选框grid._img_cache[key] = ImageTk.PhotoImage(img)
            return 创建单选框grid._img_cache[key]

        on_image = 获取图片("单选框-选中.png", (图片大小, 图片大小))
        off_image = 获取图片("单选框-未选中.png", (图片大小, 图片大小))

        单选框实例 = tk.Radiobutton(
            归属, text=标签, variable=绑定变量, value=绑定变量值,
            image=off_image, selectimage=on_image,
            indicatoron=False, compound=tk.LEFT, font=font,
            relief=tk.FLAT, overrelief=tk.FLAT, bd=0, **kwargs
        )
        单选框实例.grid(row=位置, column=位置2, padx=边距x, pady=边距y, sticky=sy)

        单选框实例.off_image = off_image
        单选框实例.on_image = on_image

        def 鼠标进入事件(event):
            单选框实例.config(cursor="hand2")

        def 鼠标离开事件(event):
            单选框实例.config(cursor="")

        单选框实例.bind("<Enter>", 鼠标进入事件)
        单选框实例.bind("<Leave>", 鼠标离开事件)
        return 单选框实例

    单选框基础样式 = {
        "bg": COLORS["surface"],
        "fg": COLORS["text"],
        "activebackground": COLORS["surface"],
        "activeforeground": COLORS["accent"],
        "highlightthickness": 0,
    }
    工具任务启动在这=True

    if 工具任务启动在这:

        选项卡任务列表容器3 = ttk.Frame(
            选项卡任务列表,
            style="Card.TFrame",
            padding=(14, 12),
        )
        选项卡任务列表容器3.grid(
            row=0, column=2, sticky="nsew", padx=(12, 0)
        )
        选项卡任务列表容器3.columnconfigure(0, weight=1)  # 设置第0列的权重为1

        选项卡任务列表容器3.columnconfigure(0, weight=1)  # 设置第0列的权重为1

        选项卡任务列表容器3_0 = ttk.Frame(
            选项卡任务列表容器3, style="Card.TFrame"
        )
        选项卡任务列表容器3_0.grid(row=0, column=0, sticky=tk.W,)
        选项卡任务列表容器3_0.columnconfigure(0, weight=1)
        选项卡任务列表容器3_0.columnconfigure(1, weight=1)

        模拟器标题标签 = tk.Label(
            选项卡任务列表容器3_0,
            text="客户端选择：",
            font=("微软雅黑", 16)
        )
        模拟器标题标签.grid(row=0, column=0)
        客户端选择变量 = tk.IntVar()

        创建单选框grid(current_dir, 选项卡任务列表容器3_0, "PC", 客户端选择变量, 1, font=("微软雅黑", 16),
                       位置=0, 位置2=1, 边距x=25, 边距y=0, **单选框基础样式)

        #创建单选框grid(current_dir, 选项卡任务列表容器3_0, "", 客户端选择变量, 2, font=("微软雅黑", 12), 位置=0, 位置2=2, 边距x=25, 边距y=0, **单选框基础样式)

        # 配置父容器（选项卡任务列表容器3）的列权重
        选项卡任务列表容器3.columnconfigure(1, weight=1)  # 设置第0列的权重为1
        选项卡任务列表容器3_1 = ttk.LabelFrame(
            选项卡任务列表容器3, text="连接状态"
        )
        选项卡任务列表容器3_1.grid(row=1, column=0, sticky="ew", )
        选项卡任务列表容器3_1.columnconfigure(0, weight=1)


        选项卡任务列表容器3.columnconfigure(2, weight=1)  # 设置第0列的权重为1
        选项卡任务列表容器3_3 = ttk.LabelFrame(
            选项卡任务列表容器3, text="截图来源"
        )
        选项卡任务列表容器3_3.grid(row=2, column=0, sticky="ew", )
        选项卡任务列表容器3_3.columnconfigure(0, weight=1)
        标签 = tk.Label(选项卡任务列表容器3_3, text="截图方式:", font=("微软雅黑", 16))
        标签.grid(row=0, column=0,sticky=tk.W,)
        截图方式变量 = tk.StringVar()

        截图方式下拉框 = ttk.Combobox(选项卡任务列表容器3_3, textvariable=截图方式变量,
                                      values=["模拟器ADB", "PC端窗口"], font=("楷体", 16, "bold"), width=15)
        截图方式下拉框.grid(row=0, column=1)
        截图方式变量.set("模拟器ADB")

        def 截图方式提示窗口(文本, 标题="版本更新提示"):
            tooltip_window = tk.Toplevel(window)
            鼠标x = window.winfo_pointerx()
            鼠标y = window.winfo_pointery()

            tooltip_window.withdraw()
            tooltip_window.title(标题)
            文本容器 = ttk.LabelFrame(tooltip_window)
            文本容器.grid(row=0, column=0)
            tooltip_window.iconbitmap(app_icon_path)  # 设置图标
            tooltip_label = tk.Label(
                文本容器,
                text=文本,
                font=("微软雅黑", 20),
                justify=tk.LEFT,
                padx=10,
                pady=10
            )
            tooltip_label.pack(fill=tk.BOTH, expand=True)
            # 更新窗口以获取正确的尺寸
            tooltip_window.update_idletasks()

            # 获取窗口尺寸
            窗口宽度 = tooltip_window.winfo_width()
            窗口高度 = tooltip_window.winfo_height()

            # 获取屏幕尺寸
            屏幕宽度 = tooltip_window.winfo_screenwidth()
            屏幕高度 = tooltip_window.winfo_screenheight()

            tooltip_window.deiconify()

            # 获取窗口尺寸
            窗口宽度 = tooltip_window.winfo_width()
            窗口高度 = tooltip_window.winfo_height()

            print(f"{窗口宽度}x{窗口高度},{屏幕宽度}x{屏幕高度}")
            # 计算调整后的位置，确保窗口完全在屏幕内
            # 如果窗口右边超出屏幕，调整到左侧显示
            if 鼠标x + 窗口宽度 > 屏幕宽度:
                调整x = max(0, 屏幕宽度 - 窗口宽度)
            else:
                调整x = 鼠标x

            # 如果窗口底部超出屏幕，调整到上方显示
            if 鼠标y + 窗口高度 > 屏幕高度:
                调整y = max(0, 屏幕高度 - 窗口高度)
            else:
                调整y = 鼠标y

            # 确保窗口不会超出屏幕左侧和顶部
            调整x = max(0, 调整x)
            调整y = max(0, 调整y)

            print(f"{窗口宽度}x{窗口高度},{屏幕宽度}x{屏幕高度},{调整x}x{调整y}")

            # 设置窗口位置并显示
            tooltip_window.geometry(f"+{调整x}+{调整y - 160}")

        def 截图方式帮助说明():
            战斗功能提示文本 = ("模拟器用户可以使用ADB端口的截图方式，\n也可以使用更快的窗口截图，\n但只有被标识为雷电或者MuMu的端口才能使用\n\n"
                                "PC端用户请使用窗口截图，也只能使用窗口截图\n\n\n"

                                "窗口截图有以下要求：\n"
                                "1.不能有滤镜作用在电脑屏幕或者模拟器窗口上(比如显卡软件滤镜，护眼模式,HDR，机械革命控制台的色彩增强等等)\n"
                                "2.不能最小化，但可以完全遮挡\n"
                                "3.使用外接显示屏可能导致游戏无法调整到某些分辨率或者窗口坐标分辨率获取错误等，等等问题，不过问题很少发生\n"
                                "以上是根据我另一款windows后台脚本的经验所得出的结论，欢迎补充"
                                )
            os.startfile(Path(current_dir / r"UI\帮助说明\端口和模拟器窗口截图说明.png"))
            截图方式提示窗口(战斗功能提示文本, 标题="截图方式设置帮助说明")

        创建按钮2grid(选项卡任务列表容器3_3, "❓", lambda: 执行器.提交任务(截图方式帮助说明, 异步=False),
                      字体配置=("微软雅黑", 14), width=2, height=1, 位置=0, 位置2=2, )

        选项卡任务列表容器3.columnconfigure(3, weight=1)  # 设置第0列的权重为1
        选项卡任务列表容器3_2 = ttk.LabelFrame(
            选项卡任务列表容器3, text="设备与窗口"
        )
        选项卡任务列表容器3_2.grid(row=3, column=0, sticky="ew", )
        选项卡任务列表容器3_2.columnconfigure(0, weight=1)

        端口号标签 = tk.Label(选项卡任务列表容器3_2, text="端 口:", font=("微软雅黑", 16))
        端口号标签.grid(row=0, column=0,sticky=tk.W,)

        # 创建下拉框
        端口号变量 = tk.StringVar()
        with open(os.path.join(current_dir, 'Tool_Settings.json'), 'r', encoding='utf-8') as file:
            Tool_Settings = json.load(file)
        if "端口号变量" in Tool_Settings:
            端口号 =Tool_Settings["端口号变量"]


        端口号变量.set(端口号)  # 默认值
        端口号下拉框 = ttk.Combobox(选项卡任务列表容器3_2, textvariable=端口号变量, font=("微软雅黑", 11), width=12)
        端口号下拉框.grid(row=0, column=1)
        创建按钮2grid(选项卡任务列表容器3_2, "❓", lambda: 执行器.提交任务(截图方式帮助说明, 异步=False),
                      字体配置=("微软雅黑", 14), width=2, height=1, 位置=0, 位置2=5, )
        选项卡任务列表容器3.columnconfigure(4, weight=1)  # 设置第0列的权重为1
        选项卡任务列表容器3_4 = ttk.LabelFrame(
            选项卡任务列表容器3, text="输入延迟"
        )
        选项卡任务列表容器3_4.grid(row=4, column=0, sticky="ew", )
        选项卡任务列表容器3_4.columnconfigure(0, weight=1)
        标签 = tk.Label(选项卡任务列表容器3_4, text="PC鼠标延迟:", font=("微软雅黑", 16))
        标签.grid(row=0, column=0,sticky=tk.W,)
        PC全局延迟变量 = tk.DoubleVar()
        PC全局延迟微调框 = tk.Spinbox(
            选项卡任务列表容器3_4,
            from_=0,  # 最小值
            to=0.05,  # 最大值
            increment=0.001,  # 步长
            textvariable=PC全局延迟变量,
            font=("微软雅黑", 16),
            relief="solid",
            width=15
        )
        PC全局延迟微调框.grid(row=0, column=1)
        标签 = tk.Label(选项卡任务列表容器3_4, text="PC键盘延迟:", font=("微软雅黑", 16))
        标签.grid(row=1, column=0,sticky=tk.W,)
        PC键盘延迟变量 = tk.DoubleVar()
        PC键盘延迟微调框 = tk.Spinbox(
            选项卡任务列表容器3_4,
            from_=0,  # 最小值
            to=0.05,  # 最大值
            increment=0.005,  # 步长
            textvariable=PC键盘延迟变量,
            font=("微软雅黑", 16),
            relief="solid",
            width=15
        )
        PC键盘延迟微调框.grid(row=1, column=1)

        def PC全局延迟帮助说明():
            战斗功能提示文本 = (
                "仅PC端生效，可以更改后台鼠标和键盘的点击动作的额外延迟，如遇见键鼠模拟失败的情况，可以尝试加大对应延迟\n单位: 秒\n鼠标步长: 0.001秒\n键盘步长: 0.005秒"
                "\n\n\n特别是使用电脑多开用户的建议延迟都调到0.03左右，还是有动作失败则继续调高"

                )
            截图方式提示窗口(战斗功能提示文本, 标题="PC全局延迟设置帮助说明")

        创建按钮2grid(选项卡任务列表容器3_4, "❓", lambda : 执行器.提交任务(PC全局延迟帮助说明,异步=False),
                      字体配置=("微软雅黑", 14), width=2, height=1, 位置=0, 位置2=2, )
        创建按钮2grid(选项卡任务列表容器3_4, "❓", lambda : 执行器.提交任务(PC全局延迟帮助说明,异步=False),
                      字体配置=("微软雅黑", 14), width=2, height=1, 位置=1, 位置2=2, )

        选项卡任务列表容器3.columnconfigure(5, weight=1)  # 设置第0列的权重为1
        缩略图容器 = ttk.LabelFrame(
            选项卡任务列表容器3, text="执行速度"
        )
        缩略图容器.grid(row=5, column=0, sticky="ew", pady=5, )

        标签 = tk.Label(
            缩略图容器,
            text="脚本运行速度x",
            font=("微软雅黑", 16),
            fg="red"
        )
        标签.grid(row=0, column=0, padx=0, pady=0, sticky="news")
        脚本运行速度变量 = tk.DoubleVar()
        脚本运行速度变量.set(1.0)  # 设置默认值为1
        脚本运行速度变量微调框 = tk.Spinbox(
            缩略图容器,
            from_=0.5,  # 最小值
            to=10.0,  # 最大值
            increment=0.1,  # 步长
            textvariable=脚本运行速度变量,
            font=("微软雅黑", 16),
            relief="solid",
            width=4
        )
        脚本运行速度变量微调框.grid(row=0, column=1)
        标签 = tk.Label(
            缩略图容器,
            text="倍",
            font=("微软雅黑", 16),
            fg="red"
        )
        标签.grid(row=0, column=2, padx=0, pady=0, sticky="news")

        缩略图容器 = ttk.LabelFrame(选项卡任务列表容器3, text="端口缩略图")
        缩略图容器.grid(row=6, column=0, sticky="ew", )
        缩略图容器.columnconfigure(0, weight=1)
        # 强制更新界面后获取实际宽度
        选项卡任务列表容器3.update_idletasks()
        缩略图容器width = 缩略图容器.winfo_width()
        #print(f"缩略图容器宽度: {width}像素")
        缩略图标签 = tk.Label(缩略图容器)
        缩略图标签.pack()

        def 动态等比例缩放并更新图片(*args):
            """非阻塞方式更新图片"""
            try:
                _执行图片更新任务()
            except Exception as e:
                logger.debug(f"提交图片更新任务失败: {str(e)}")
            #if not 线程事件停止循环.is_set():

        def _执行图片更新任务():
            """实际执行图片更新的工作函数"""
            函数保存设置()
            try:
                if 端口号变量.get() in 端口号下拉框["values"]:
                    logger.debug("端口可用，开始更新图片")

                    # 获取最新端口号
                    with open(os.path.join(current_dir, 'Tool_Settings.json'), 'r', encoding='utf-8') as file:
                        Tool_Settings = json.load(file)
                    客户端选择 = int(Tool_Settings["客户端选择变量"])

                    # 获取图片数据
                    png_data = None
                    路径 = current_dir / "game.json"
                    with open(路径, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    端游列表 = data["端游列表"]
                    hwnd = 0
                    for 端游 in 端游列表:
                        窗口列表 = 精确查找所有窗口句柄(端游[0], 端游[1], )
                        if 窗口列表:
                            for 元组 in 窗口列表:
                                hwnd, 窗口矩形 = 元组
                                if str(hwnd) == str(端口号变量.get()):
                                    png_data = 函数截图到内存(hwnd, 窗口矩形)
                                    客户端选择变量.set(1)
                                    截图方式变量.set("PC端窗口")
                                    logger.debug(f"设置客户端为PC，截图方式为窗口{hwnd}")
                                    break
                            else:
                                hwnd = None

                        if hwnd:
                            break
                    logger.debug(f"游戏窗口：{hwnd}，端口：{端口号变量.get()}")
                    if str(hwnd) == str(端口号变量.get()):
                        pass

                    else:
                        客户端选择变量.set(2)
                        logger.debug("设置客户端为模拟器")
                        png_data = _模拟器模式更新端口图()
                        if "雷电" in str(端口号变量.get()) or "MuMu" in str(端口号变量.get()):
                            pass
                        else:
                            截图方式变量.set("模拟器ADB")

                    if png_data:
                        # 在后台线程处理图片
                        img = Image.open(BytesIO(png_data))
                        原始宽度, 原始高度 = img.size
                        if 原始宽度 > 原始高度:
                            目标宽度 = 缩略图容器.winfo_width() - 20
                        else:
                            目标宽度 = int(缩略图容器.winfo_width() / 2)
                        目标高度 = int(目标宽度 * (原始高度 / 原始宽度))
                        img_resized = img.resize(
                            (目标宽度, 目标高度),
                            Image.Resampling.LANCZOS
                        )

                        # 切换到主线程更新UI
                        缩略图标签.after(0, lambda: _更新UI图片(img_resized))
                    else:
                        缩略图标签.after(0, _显示错误图片)
                else:
                    缩略图标签.after(0, _显示错误图片)
            except Exception as e:
                logger.error(f"处理图片数据时出现异常: {str(e)}")
                缩略图标签.after(0, _显示错误图片)

        def _模拟器模式更新端口图():
            """模拟器模式获取图片"""
            try:
                adb路径 = 获取adb路径并检查(检查线程=False,端口号=str(端口号变量.get()))
                return 获取_png_data(adb路径, x1=0, y1=0, x2=0, y2=0)
            except Exception as e:
                logger.error(f"模拟器截图失败: {str(e)}")
                return None

        def _更新UI图片(img_resized):
            """在主线程中更新UI"""
            try:
                photo = ImageTk.PhotoImage(img_resized)
                缩略图标签.config(image=photo)
                缩略图标签.image = photo  # 保持引用
                logger.debug("图片更新成功")
            except Exception as e:
                logger.error(f"更新UI图片失败: {str(e)}")
                _显示错误图片()

        def _显示错误图片():
            """显示错误占位图"""
            try:
                logger.warning(f"端口不可用")
                加载图片到标签(缩略图标签,
                               目标高度=150,
                               图片加载失败文本="加载失败")

            except Exception as e:
                # 创建黑色占位图
                黑色图片 = Image.new('RGB', (250, 100), color='black')
                error_photo = ImageTk.PhotoImage(黑色图片)
                缩略图标签.config(image=error_photo)
                缩略图标签.error_image = error_photo  # 保持引用
                logger.error(f"显示错误图片失败: {str(e)}")

        # 绑定变量监听
        端口号变量.trace_add("write", lambda *args: 执行器.提交任务(动态等比例缩放并更新图片,))

        # 创建执行器实例
        def 刷新端口列表2():
            def 子函数():
                路径 = current_dir / "game.json"
                with open(路径, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                端游列表 = data["端游列表"]
                hwnd = 0
                端口列表 = []
                for 端游 in 端游列表:
                    窗口列表 = 精确查找所有窗口句柄(端游[0], 端游[1], )
                    if 窗口列表:
                        for 元组 in 窗口列表:
                            hwnd, 窗口矩形 = 元组
                            端口列表.append(str(hwnd))
                if str(hwnd) == str(端口号变量.get()):
                    客户端选择变量.set(1)
                    截图方式变量.set("PC端窗口")
                else:
                    try:
                        变量 = int(端口号变量.get())
                        客户端选择变量.set(1)
                        截图方式变量.set("PC端窗口")
                    except:
                        客户端选择变量.set(2)
                        if "雷电" in str(端口号变量.get()) or "MuMu" in str(端口号变量.get()):
                            if 截图方式变量.get() != "PC端窗口":
                                print(截图方式变量.get())
                        else:
                            截图方式变量.set("模拟器ADB")

                窗口列表 = 查找符合条件的顶级窗口(目标窗口类名="RenderWindow", 目标窗口标题="TheRender", )
                if 窗口列表:
                    雷电句柄 = 窗口列表[0]
                    print(f"雷电句柄: {雷电句柄}")
                    雷电path = Path(获取模拟器应用路径(雷电句柄))
                    print(雷电path)
                    启动器= Leidian非管理员启动器(播放器路径=雷电path)
                    列表=获取雷电可用端口(启动器)
                    print(列表)
                    端口列表=端口列表+列表

                窗口列表 = 查找符合条件的顶级窗口(目标窗口类名="Qt5156QWindowIcon", 目标窗口标题="MuMuPlayer", )
                if 窗口列表:
                    MuMu句柄 = 窗口列表[0]
                    print(f"MuMu句柄: {MuMu句柄}")

                    MuMupath = Path(获取模拟器应用路径(MuMu句柄))
                    print(MuMupath)
                    启动器 = MuMu非管理员启动器(播放器路径=MuMupath)
                    列表 = 获取mumu可用端口(启动器)
                    print(列表)
                    端口列表 = 端口列表 + 列表

                adb程序 = current_dir / "platform-tools" / "adb.exe"

                所有设备 = 获取所有设备端口(adb程序)
                所有设备 =  端口列表 +所有设备

                if 所有设备:
                    if len(所有设备) < 4:
                        所有设备 = 所有设备 + [""]
                    # 更新下拉框内容
                    端口号下拉框["values"] = 所有设备

            for i in range(6):
                执行器.提交任务(子函数, )
                time.sleep(10)
        def 刷新端口列表():

                函数保存设置()
                端口列表 = []
                路径 = current_dir /  "game.json"
                with open(路径, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                端游列表 = data["端游列表"]
                hwnd = 0
                for 端游 in 端游列表:
                    窗口列表 = 精确查找所有窗口句柄(端游[0], 端游[1], )
                    if 窗口列表:
                        for 元组 in 窗口列表:
                            hwnd, 窗口矩形 = 元组
                            端口列表.append(str(hwnd))
                窗口列表 = 查找符合条件的顶级窗口(目标窗口类名="RenderWindow", 目标窗口标题="TheRender", )
                if 窗口列表:
                    雷电句柄 = 窗口列表[0]
                    print(f"雷电句柄: {雷电句柄}")
                    雷电path = Path(获取模拟器应用路径(雷电句柄))
                    print(雷电path)
                    启动器 = Leidian非管理员启动器(播放器路径=雷电path)
                    列表 = 获取雷电可用端口(启动器)
                    print(列表)
                    端口列表 = 端口列表 + 列表

                窗口列表 = 查找符合条件的顶级窗口(目标窗口类名="Qt5156QWindowIcon", 目标窗口标题="MuMuPlayer", )
                if 窗口列表:
                    MuMu句柄 = 窗口列表[0]
                    print(f"MuMu句柄: {MuMu句柄}")

                    MuMupath = Path(获取模拟器应用路径(MuMu句柄))
                    print(MuMupath)
                    启动器 = MuMu非管理员启动器(播放器路径=MuMupath)
                    列表 = 获取mumu可用端口(启动器)
                    print(列表)
                    端口列表 = 端口列表 + 列表

                with open(os.path.join(current_dir, 'Tool_Settings.json'), 'r', encoding='utf-8') as file:
                    Tool_Settings = json.load(file)
                客户端选择 = int(Tool_Settings["客户端选择变量"])


                if str(hwnd) == str(端口号变量.get()):
                    客户端选择变量.set(1)
                    截图方式变量.set("PC端窗口")
                else:
                    try:
                        变量 = int(端口号变量.get())
                        客户端选择变量.set(1)
                        截图方式变量.set("PC端窗口")
                    except:
                        客户端选择变量.set(2)
                        if "雷电" in str(端口号变量.get()) or "MuMu" in str(端口号变量.get()):
                            if 截图方式变量.get() != "PC端窗口":
                                print(截图方式变量.get())
                        else:
                            截图方式变量.set("模拟器ADB")

                adb程序 = current_dir / "platform-tools" / "adb.exe"

                所有设备 = 获取所有设备端口(adb程序)

                所有设备 = 端口列表 + 所有设备
                logger.debug(f"所有设备{所有设备}")
                端口号 = "无可用端口"
                if 所有设备:
                    if len(所有设备) < 4:
                        所有设备 = 所有设备 + [""]
                    # 更新下拉框内容
                    端口号下拉框["values"] = 所有设备
                    if 客户端选择 == 1:
                        if hwnd:
                            端口号 = hwnd
                        else:
                            if 端口号变量.get() in 所有设备:
                                端口号 = 端口号变量.get()
                            elif Tool_Settings["端口号变量"] in 所有设备:
                                端口号 = Tool_Settings["端口号变量"]
                            else:
                                端口号 = 所有设备[0]
                    else:
                        if 端口号变量.get() in 所有设备:
                            端口号 = 端口号变量.get()
                        elif Tool_Settings["端口号变量"] in 所有设备:
                            端口号 = Tool_Settings["端口号变量"]
                        else:
                            端口号 = 所有设备[0]
                else:
                    端口号 = Tool_Settings["端口号变量"]
                Tool_Settings_path = os.path.join(current_dir, 'Tool_Settings.json')
                with open(Tool_Settings_path, 'r', encoding='utf-8') as file:
                    Tool_Settings = json.load(file)
                    文件中的端口号 = Tool_Settings["端口号变量"]
                    if "雷电" in str(文件中的端口号) or "MuMu" in str(文件中的端口号):
                        端口号=文件中的端口号
                端口号变量.set(端口号)


        创建按钮2grid(选项卡任务列表容器3_2, "刷新", lambda: 执行器.提交任务(刷新端口列表,),
                      字体配置=("微软雅黑", 16), width=4, height=1, 位置=0, 位置2=2, )




        创建按钮2grid(选项卡任务列表容器3_2, "截图", lambda: 执行器.提交任务(截图到剪切板,),
                      字体配置=("微软雅黑", 16), width=4, height=1, 位置=0, 位置2=3, )

    其他任务设置在这 = True
    if 其他任务设置在这:
        定时启动变量 = tk.IntVar()
        其他任务设置2_1_1 = ttk.Frame(
            其他任务设置2, style="Card.TFrame", padding=(18, 16)
        )
        其他任务设置2_1_1.grid(row=0, column=0, sticky="new")

        ttk.Label(
            其他任务设置2_1_1,
            text="定时启动",
            style="CardSection.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        其他任务设置2_1_12 = ttk.Frame(
            其他任务设置2_1_1, style="Card.TFrame"
        )
        其他任务设置2_1_12.grid(row=1, column=0)

        创建复选框grid(current_dir, 其他任务设置2_1_12, "定时启动", 定时启动变量,
                       font=("微软雅黑", 16), 位置=0, 位置2=0, 边距x=5, 边距y=2, **复选框基础样式)

        定时时间标签 = tk.Label(
            其他任务设置2_1_12,
            text="时间(HH:MM):",
            font=("微软雅黑", 16)
        )
        定时时间标签.grid(row=0, column=1)  # 紧跟复选框

        定时时间变量 = tk.StringVar()
        定时时间变量.set("06:00")  # 默认值
        定时时间输入框 = tk.Entry(
            其他任务设置2_1_12,
            textvariable=定时时间变量,
            font=("微软雅黑", 16),
            width=6
        )
        定时时间输入框.grid(row=0, column=2)



    启动项结束项在这=True
    if 启动项结束项在这:
        if 系统DPI<=1:
            减少长度=0
        elif 系统DPI<=1.25:
            减少长度=6
        elif 系统DPI <= 1.5:
            减少长度 = 6
        elif 系统DPI >= 1.75:
            减少长度 = 6
        else:
            减少长度 = 0
        print(f"长度：{减少长度}")
        文本框长度=55-减少长度
        文本框宽度=3
        脚本启动结束容器 = ttk.Frame(
            其他任务设置, style="App.TFrame"
        )
        脚本启动结束容器.grid(row=0, column=0, sticky="news")

        style = ttk.Style()
        # 设置标签的字体颜色为红色
        style.configure(
            "Red.TLabel",
            background=COLORS["danger_soft"],
            foreground=COLORS["danger"],
            font=("Microsoft YaHei UI", 10, "bold"),
            padding=(12, 8),
        )
        label = ttk.Label(
            其他任务设置,
            text="安全提示：启动/结束自动打开文件或应用，可能触发杀毒软件误报。",
            style="Red.TLabel"  # 设置字体和大小
        )
        label.grid(row=1, column=0, sticky="news") # 设置标签的位置

        脚本启动结束容器1_1 = ttk.LabelFrame(脚本启动结束容器)
        脚本启动结束容器1_1.grid(row=0, column=0, sticky="news")

        脚本启动后开始任务变量 = tk.IntVar()

        创建复选框grid(current_dir, 脚本启动结束容器1_1, "脚本启动后开始任务", 脚本启动后开始任务变量,
                       font=("微软雅黑", 16), 位置=0, 位置2=0, 边距x=0, 边距y=0, **复选框基础样式)

        脚本启动结束容器1_2 = ttk.LabelFrame(脚本启动结束容器)
        脚本启动结束容器1_2.grid(row=1, column=0, sticky="news")
        脚本启动后打开网站变量 = tk.IntVar()
        创建复选框grid(current_dir, 脚本启动结束容器1_2, "脚本启动后打开以下网站:", 脚本启动后打开网站变量,
                       font=("微软雅黑", 16), 位置=0, 位置2=0, 边距x=0, 边距y=0, **复选框基础样式)


        # 创建文本框（接之前的代码）
        脚本启动后网站列表多行输入框 = scrolledtext.ScrolledText(
            脚本启动结束容器1_2,
            font=("微软雅黑", 12),
            wrap=tk.WORD,
            width=文本框长度,
            height=文本框宽度
        )
        脚本启动后网站列表多行输入框.grid(row=1, column=0)

        # 创建绑定器实例
        文本框变量管理器 = TextVariableWrapper(脚本启动后网站列表多行输入框)

        脚本启动结束容器1_3 = ttk.LabelFrame(脚本启动结束容器)
        脚本启动结束容器1_3.grid(row=1, column=1, sticky="news")
        脚本任务结束后打开网站变量 = tk.IntVar()
        创建复选框grid(current_dir, 脚本启动结束容器1_3, "脚本任务结束后打开以下网站:", 脚本任务结束后打开网站变量,
                       font=("微软雅黑", 16), 位置=0, 位置2=0, 边距x=0, 边距y=0, **复选框基础样式)


        # 任务结束后网站列表输入框
        脚本任务结束后网站列表多行输入框 = scrolledtext.ScrolledText(
            脚本启动结束容器1_3,
            font=("微软雅黑", 12),
            wrap=tk.WORD,
            width=文本框长度,
            height=文本框宽度
        )
        脚本任务结束后网站列表多行输入框.grid(row=1, column=0)  #

        # 创建任务结束后文本框的变量管理器
        文本框变量管理器2 = TextVariableWrapper(脚本任务结束后网站列表多行输入框)  # 新实例

        脚本启动结束容器1_4 = ttk.LabelFrame(脚本启动结束容器)
        脚本启动结束容器1_4.grid(row=2, column=0, sticky="news")

        脚本启动后打开应用变量 = tk.IntVar()

        创建复选框grid(current_dir, 脚本启动结束容器1_4, "脚本启动后打开以下应用:", 脚本启动后打开应用变量,
                       font=("微软雅黑", 16), 位置=0, 位置2=0, 边距x=0, 边距y=0, **复选框基础样式)
        脚本启动后打开应用列表多行输入框 = scrolledtext.ScrolledText(
            脚本启动结束容器1_4,
            font=("微软雅黑", 12),
            wrap=tk.WORD,
            width=文本框长度,
            height=文本框宽度
        )
        脚本启动后打开应用列表多行输入框.grid(row=1, column=0)  #

        文本框变量管理器3 = TextVariableWrapper(脚本启动后打开应用列表多行输入框)  # 新实例

        脚本启动结束容器1_5 = ttk.LabelFrame(脚本启动结束容器)
        脚本启动结束容器1_5.grid(row=2, column=1, sticky="news")
        脚本任务结束后打开应用变量 = tk.IntVar()
        创建复选框grid(current_dir, 脚本启动结束容器1_5, "脚本任务结束后打开以下应用:", 脚本任务结束后打开应用变量,
                       font=("微软雅黑", 16), 位置=0, 位置2=0, 边距x=0, 边距y=0, **复选框基础样式)


        脚本任务结束后打开应用列表多行输入框 = scrolledtext.ScrolledText(
            脚本启动结束容器1_5,
            font=("微软雅黑", 12),
            wrap=tk.WORD,
            width=文本框长度,
            height=文本框宽度
        )
        脚本任务结束后打开应用列表多行输入框.grid(row=1, column=0)  #

        文本框变量管理器4 = TextVariableWrapper(脚本任务结束后打开应用列表多行输入框)  # 新实例

        脚本启动结束容器1_6 = ttk.LabelFrame(脚本启动结束容器)
        脚本启动结束容器1_6.grid(row=3, column=0, sticky="news")
        脚本启动后打开文件变量 = tk.IntVar()
        创建复选框grid(current_dir, 脚本启动结束容器1_6, "脚本启动后打开以下文件:", 脚本启动后打开文件变量,
                       font=("微软雅黑", 16), 位置=0, 位置2=0, 边距x=0, 边距y=0, **复选框基础样式)


        脚本启动后打开文件列表多行输入框 = scrolledtext.ScrolledText(
            脚本启动结束容器1_6,
            font=("微软雅黑", 12),
            wrap=tk.WORD,
            width=文本框长度,
            height=文本框宽度
        )
        脚本启动后打开文件列表多行输入框.grid(row=1, column=0)

        文本框变量管理器5 = TextVariableWrapper(脚本启动后打开文件列表多行输入框)  # 新实例

        脚本启动结束容器1_6 = ttk.LabelFrame(脚本启动结束容器)
        脚本启动结束容器1_6.grid(row=3, column=1, sticky="news")
        脚本任务结束后打开文件变量 = tk.IntVar()
        创建复选框grid(current_dir, 脚本启动结束容器1_6, "脚本任务结束后打开以下文件:", 脚本任务结束后打开文件变量,
                       font=("微软雅黑", 16), 位置=0, 位置2=0, 边距x=0, 边距y=0, **复选框基础样式)

        脚本任务结束后打开文件列表多行输入框 = scrolledtext.ScrolledText(
            脚本启动结束容器1_6,
            font=("微软雅黑", 12),
            wrap=tk.WORD,
            width=文本框长度,
            height=文本框宽度
        )
        脚本任务结束后打开文件列表多行输入框.grid(row=1, column=0)

        文本框变量管理器6 = TextVariableWrapper(脚本任务结束后打开文件列表多行输入框)  # 新实例

        ######################
        脚本启动结束容器1_6 = ttk.LabelFrame(脚本启动结束容器)
        脚本启动结束容器1_6.grid(row=4, column=0, sticky="news")
        脚本启动后提示文本变量 = tk.IntVar()
        创建复选框grid(current_dir, 脚本启动结束容器1_6, "脚本启动后提示以下文本:", 脚本启动后提示文本变量,
                       font=("微软雅黑", 16), 位置=0, 位置2=0, 边距x=0, 边距y=0, **复选框基础样式)

        脚本启动后提示文本列表多行输入框 = scrolledtext.ScrolledText(
            脚本启动结束容器1_6,
            font=("微软雅黑", 12),
            wrap=tk.WORD,
            width=文本框长度,
            height=文本框宽度
        )
        脚本启动后提示文本列表多行输入框.grid(row=1, column=0)

        文本框变量管理器7 = TextVariableWrapper(脚本启动后提示文本列表多行输入框)  # 新实例

        脚本启动结束容器1_6 = ttk.LabelFrame(脚本启动结束容器)
        脚本启动结束容器1_6.grid(row=4, column=1, sticky="news")
        脚本任务结束后提示文本变量 = tk.IntVar()
        创建复选框grid(current_dir, 脚本启动结束容器1_6, "脚本任务结束后提示以下文本:", 脚本任务结束后提示文本变量,
                       font=("微软雅黑", 16), 位置=0, 位置2=0, 边距x=0, 边距y=0, **复选框基础样式)

        脚本任务结束后提示文本列表多行输入框 = scrolledtext.ScrolledText(
            脚本启动结束容器1_6,
            font=("微软雅黑", 12),
            wrap=tk.WORD,
            width=文本框长度,
            height=文本框宽度
        )
        脚本任务结束后提示文本列表多行输入框.grid(row=1, column=0)

        文本框变量管理器8 = TextVariableWrapper(脚本任务结束后提示文本列表多行输入框)  # 新实例




        # 修改保存函数 ↓
        def 保存网站应用文件配置(current_dir):
            配置数据 = {
                # 原有配置
                "脚本启动后打开网站变量": 脚本启动后打开网站变量.get(),
                "脚本启动后网站列表": 文本框变量管理器.variable.get(),

                # 新增任务结束后配置
                "脚本任务结束后打开网站变量": 脚本任务结束后打开网站变量.get(),  # 新键
                "脚本任务结束后网站列表": 文本框变量管理器2.variable.get(),

                "脚本启动后打开应用变量": 脚本启动后打开应用变量.get(),
                "脚本启动后应用列表": 文本框变量管理器3.variable.get(),

                "脚本任务结束后打开应用变量": 脚本任务结束后打开应用变量.get(),
                "脚本任务结束后应用列表": 文本框变量管理器4.variable.get(),

                "脚本启动后打开文件变量": 脚本启动后打开文件变量.get(),
                "脚本启动后文件列表": 文本框变量管理器5.variable.get(),

                "脚本任务结束后打开文件变量": 脚本任务结束后打开文件变量.get(),
                "脚本任务结束后文件列表": 文本框变量管理器6.variable.get(),

                "脚本启动后提示文本变量": 脚本启动后提示文本变量.get(),
                "脚本启动后提示文本列表": 文本框变量管理器7.variable.get(),

                "脚本任务结束后提示文本变量": 脚本任务结束后提示文本变量.get(),
                "脚本任务结束后提示文本列表": 文本框变量管理器8.variable.get(),

            }

            # 保持原有保存路径逻辑

            web_and_app_Path = os.path.join(current_dir, 'web_and_app.json')
            with open(web_and_app_Path, "w", encoding="utf-8") as f:
                json.dump(配置数据, f, ensure_ascii=False, indent=2)

        # 修改加载函数 ↓
        def 加载网站应用文件配置(current_dir):
            try:

                with open(os.path.join(current_dir, 'web_and_app.json'), "r", encoding="utf-8") as f:
                    配置数据 = json.load(f)

                    # 加载原有配置
                    if "脚本启动后打开网站变量" in 配置数据:
                        脚本启动后打开网站变量.set(配置数据["脚本启动后打开网站变量"])
                    if "脚本启动后网站列表" in 配置数据:
                        文本框变量管理器.set(配置数据["脚本启动后网站列表"])

                    # 加载新增配置
                    if "脚本任务结束后打开网站变量" in 配置数据:  # 新增判断
                        脚本任务结束后打开网站变量.set(配置数据["脚本任务结束后打开网站变量"])
                    if "脚本任务结束后网站列表" in 配置数据:  # 新增判断
                        文本框变量管理器2.set(配置数据["脚本任务结束后网站列表"])

                    if "脚本启动后打开应用变量" in 配置数据:
                        脚本启动后打开应用变量.set(配置数据["脚本启动后打开应用变量"])
                    if "脚本启动后应用列表" in 配置数据:
                        文本框变量管理器3.set(配置数据["脚本启动后应用列表"])

                    # 加载新增配置
                    if "脚本任务结束后打开应用变量" in 配置数据:  # 新增判断
                        脚本任务结束后打开应用变量.set(配置数据["脚本任务结束后打开应用变量"])
                    if "脚本任务结束后应用列表" in 配置数据:  # 新增判断
                        文本框变量管理器4.set(配置数据["脚本任务结束后应用列表"])

                    if "脚本启动后打开文件变量" in 配置数据:
                        脚本启动后打开文件变量.set(配置数据["脚本启动后打开文件变量"])
                    if "脚本启动后文件列表" in 配置数据:
                        文本框变量管理器5.set(配置数据["脚本启动后文件列表"])

                    # 加载新增配置
                    if "脚本任务结束后打开文件变量" in 配置数据:  # 新增判断
                        脚本任务结束后打开文件变量.set(配置数据["脚本任务结束后打开文件变量"])
                    if "脚本任务结束后文件列表" in 配置数据:  # 新增判断
                        文本框变量管理器6.set(配置数据["脚本任务结束后文件列表"])

                    if "脚本启动后提示文本变量" in 配置数据:
                        脚本启动后提示文本变量.set(配置数据["脚本启动后提示文本变量"])
                    if "脚本启动后提示文本列表" in 配置数据:
                        文本框变量管理器7.set(配置数据["脚本启动后提示文本列表"])

                    # 加载新增配置
                    if "脚本任务结束后提示文本变量" in 配置数据:  # 新增判断
                        脚本任务结束后提示文本变量.set(配置数据["脚本任务结束后提示文本变量"])
                    if "脚本任务结束后提示文本列表" in 配置数据:  # 新增判断
                        文本框变量管理器8.set(配置数据["脚本任务结束后提示文本列表"])

            except FileNotFoundError:
                logger.debug("首次运行，未找到配置文件")
            except KeyError as e:
                logger.warning(f"配置文件缺少必要键：{e}")

        # 最后记得调用加载配置（比如在程序启动时）

    def 截图到剪切板():
        函数保存设置()
        adb路径 = 获取adb路径并检查(检查线程=False,检查分辨率=False)
        if adb路径:
            png_data = 获取_png_data(adb路径, x1=0, y1=0, x2=0, y2=0)
            #截取炼金图片(adb路径, current_dir, 0, ocr_engine)

            logger.info("正在复制到剪切板")
            # 复制到剪切板
            接收数据复制到剪切板(png_data)

            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            messagebox.showinfo("截图成功", f"截图已经复制到剪切板，现在你可以在画图软件中粘贴并编辑")
        else:
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            messagebox.showinfo("截图失败", "请更换成可用端口")

    if 异环脚本运行:
        if 异环脚本运行:
            选项卡任务列表容器1 = ttk.Frame(
                选项卡任务列表, style="App.TFrame"
            )
            选项卡任务列表容器1.grid(
                row=0, column=0, padx=0, pady=0, sticky="nsew"
            )
            选项卡任务列表容器1_2 = ttk.Frame(
                选项卡任务列表容器1,
                style="Card.TFrame",
                padding=(14, 12),
            )
            选项卡任务列表容器1_2.grid(row=0, column=0, sticky="new")
            选项卡任务列表容器1_2.columnconfigure(1, weight=1)
            选项卡任务列表容器1_2.columnconfigure(2, weight=1)
            ttk.Label(
                选项卡任务列表容器1_2,
                text="常用任务",
                style="CardSection.TLabel",
            ).grid(row=0, column=1, columnspan=2, sticky="w", padx=5, pady=(0, 8))
            小功能按钮字体 = 11
            小功能按钮长度 = 13
            小功能位置列表 = [1, 1, 2, 2, 3, 3, 4]

            异环钓鱼子容器 = ttk.Frame(选项卡其他任务加载)
            异环钢琴演奏子容器 = ttk.Frame(选项卡其他任务加载)
            幻塔钓鱼子容器 = ttk.Frame(选项卡其他任务加载)
            异环店长特供子容器 = ttk.Frame(选项卡其他任务加载)
            异环超强音子容器 = ttk.Frame(选项卡其他任务加载)
            异环其他任务子容器= ttk.Frame(选项卡其他任务加载)
            # 将三个子容器存入字典，方便后续切换
            子容器字典 = {
                "异环钓鱼": 异环钓鱼子容器,
                "异环钢琴": 异环钢琴演奏子容器,
                "幻塔钓鱼": 幻塔钓鱼子容器,
                "异环店长特供": 异环店长特供子容器,
                "异环超强音": 异环超强音子容器,
                "异环其他任务": 异环其他任务子容器,
            }

            # 将所有子容器放置在相同位置，并立即隐藏
            for container in 子容器字典.values():
                container.grid(row=0, column=0)

            if 异环脚本运行:
                def 异环钢琴窗口创建():
                    def midi_to_note_name(midi):
                        """将 MIDI 编号（0~127）转换为音名，例如 60 -> C4, 61 -> C#4, 36 -> C2"""
                        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                        octave = midi // 12 - 1
                        note = notes[midi % 12]
                        return f"{note}{octave}"
                    for widget in 异环钢琴演奏子容器.winfo_children():
                        widget.destroy()

                    # 外部可用变量
                    json_path = current_dir.parent / "外置配置文件夹" / "演奏文件列表.json"
                    当前文件路径 = None  # 当前选中的文件/文件夹路径
                    音轨复选框变量 = {}  # {音轨号: tk.BooleanVar}
                    音轨内部框架 = None

                    # ========== 文件选择区 ==========
                    选择区 = ttk.LabelFrame(异环钢琴演奏子容器, text="选择演奏文件")
                    选择区.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
                    选择区.grid_columnconfigure(0, weight=1)

                    按钮框 = ttk.Frame(选择区)
                    按钮框.grid(row=0, column=0, pady=5)
                    from tkinter import filedialog
                    def 选择文件(后缀):
                        nonlocal 当前文件路径, 音轨内部框架, 音轨复选框变量
                        initialdir =current_dir.parent / "外置配置文件夹"/"midi"

                        filepath = filedialog.askopenfilename(
                            initialdir=initialdir, title=f"选择 {后缀} 文件",
                            filetypes=[(f"{后缀} 文件", f"*{后缀}")]
                        )
                        if not filepath:
                            return
                        当前文件路径 = Path(filepath)
                        当前文件标签.config(text=str(当前文件路径))

                        # 清除旧的音轨框架
                        if 音轨内部框架:
                            音轨内部框架.destroy()
                            音轨内部框架 = None
                        音轨复选框变量.clear()

                        # 分析 MIDI 文件
                        try:
                            from 异环钢琴main import 分析MIDI文件
                            音轨事件字典, _ = 分析MIDI文件(str(当前文件路径))
                        except Exception as e:
                            messagebox.showerror("错误", f"分析 MIDI 失败：{e}")
                            return

                        if not 音轨事件字典:
                            messagebox.showinfo("提示", "文件没有包含任何音符事件")
                            return

                        音轨内部框架 = ttk.Frame(音轨容器)
                        音轨内部框架.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                        # 表头
                        header = ttk.Frame(音轨内部框架)
                        header.pack(fill=tk.X)
                        ttk.Label(header, text="轨道", width=8).pack(side=tk.LEFT)
                        ttk.Label(header, text="音域范围", width=16).pack(side=tk.LEFT)
                        ttk.Label(header, text="音符数量", width=10).pack(side=tk.LEFT)
                        ttk.Label(header, text="启用").pack(side=tk.LEFT)

                        for 音轨号, 事件列表 in sorted(音轨事件字典.items()):
                            音符列表 = [ev['音符'] for ev in 事件列表 if ev['类型'] == '开始']
                            if not 音符列表:
                                continue
                            最低音 = min(音符列表)
                            最高音 = max(音符列表)
                            音域 = f"({最低音}~{最高音}/{midi_to_note_name(最低音)}~{midi_to_note_name(最高音)})"
                            数量 = len(音符列表)

                            var = tk.BooleanVar(value=True)
                            音轨复选框变量[音轨号] = var

                            row = ttk.Frame(音轨内部框架)
                            row.pack(fill=tk.X)
                            ttk.Label(row, text=f"音轨 {音轨号}", width=8).pack(side=tk.LEFT)
                            ttk.Label(row, text=音域, width=16).pack(side=tk.LEFT)
                            ttk.Label(row, text=str(数量), width=10).pack(side=tk.LEFT)
                            ttk.Checkbutton(row, variable=var).pack(side=tk.LEFT)

                    def 选择json文件夹():
                        nonlocal 当前文件路径, 音轨内部框架, 音轨复选框变量
                        initialdir = current_dir.parent / "外置配置文件夹"/"演奏文件"
                        folder = filedialog.askdirectory(initialdir=initialdir, title="选择 JSON 文件夹")
                        if not folder:
                            return
                        当前文件路径 = Path(folder)
                        当前文件标签.config(text=str(当前文件路径))

                        # 清除音轨内容（文件夹不需要音轨选择）
                        if 音轨内部框架:
                            音轨内部框架.destroy()
                            音轨内部框架 = None
                        音轨复选框变量.clear()
                        音轨内部框架 = ttk.Frame(音轨容器)
                        音轨内部框架.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                        # 表头
                        header = ttk.Frame(音轨内部框架)
                        header.pack(fill=tk.X)
                        ttk.Label(header, text="json文件不能设置，请直接演奏", width=28).pack(side=tk.LEFT)
                    ttk.Button(按钮框, text="1. 选择 .mid 文件",
                               command=lambda: 选择文件(".mid")).pack(side=tk.LEFT, padx=2)
                    ttk.Button(按钮框, text="2. 选择 .midi 文件",
                               command=lambda: 选择文件(".midi")).pack(side=tk.LEFT, padx=2)
                    ttk.Button(按钮框, text="3. 选择 JSON 文件夹",
                               command=选择json文件夹).pack(side=tk.LEFT, padx=2)

                    当前文件标签 = ttk.Label(选择区, text="未选择文件", foreground="gray")
                    当前文件标签.grid(row=1, column=0, sticky="w", padx=5)

                    # ========== 音轨选择区 ==========
                    音轨容器 = ttk.LabelFrame(异环钢琴演奏子容器, text="音轨设置选择(json文件不显示)")
                    音轨容器.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

                    # ========== 设置区 ==========
                    设置区 = ttk.LabelFrame(异环钢琴演奏子容器, text="演奏设置1")
                    设置区.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

                    设置行1 = ttk.Frame(设置区)
                    设置行1.pack(fill=tk.X, pady=5, padx=5)

                    tk.Label(设置行1, text="加减 Key:", font=("微软雅黑", 12)).pack(side=tk.LEFT)
                    异环钢琴加减key变量 = tk.IntVar(value=0)
                    tk.Spinbox(设置行1, from_=-100, to=100, increment=1,
                               textvariable=异环钢琴加减key变量, width=5).pack(side=tk.LEFT, padx=5)

                    tk.Label(设置行1, text="压缩方式:", font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=(15, 0))
                    异环钢琴压缩方式变量 = tk.StringVar(value="最大覆盖中心八度直接裁剪")
                    ttk.Combobox(设置行1, textvariable=异环钢琴压缩方式变量,
                                 values=["整体加减key音名关系保留", "整体加减key直接裁剪",
                                         "整体加减八度音名关系保留", "整体加减八度直接裁剪",
                                         "最大覆盖中心key音名保留", "最大覆盖中心key直接裁剪",
                                         "最大覆盖中心八度音名保留", "最大覆盖中心八度直接裁剪",
                                         "直接裁剪"], width=20).pack(side=tk.LEFT, padx=5)

                    生成json演奏文件变量 = tk.IntVar(value=0)
                    ttk.Checkbutton(设置行1, text="生成 JSON 演奏文件", variable=生成json演奏文件变量).pack(side=tk.LEFT, padx=20)
                    设置区 = ttk.LabelFrame(异环钢琴演奏子容器, text="演奏设置2")
                    设置区.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
                    设置行1 = ttk.Frame(设置区)
                    设置行1.pack(fill=tk.X, pady=5, padx=5)
                    tk.Label(设置行1, text="演奏速度:", font=("微软雅黑", 12)).pack(side=tk.LEFT)
                    异环钢琴演奏速度变量 = tk.DoubleVar(value=1.0)
                    tk.Spinbox(设置行1, from_=0.01, to=100, increment=0.1,
                               textvariable=异环钢琴演奏速度变量, width=5).pack(side=tk.LEFT, padx=5)
                    tk.Label(设置行1, text="映射反转:", font=("微软雅黑", 12)).pack(side=tk.LEFT)
                    水平反转映射变量 = tk.IntVar(value=0)
                    ttk.Checkbutton(设置行1, text="水平反转", variable=水平反转映射变量).pack(side=tk.LEFT, padx=20)
                    垂直反转映射变量 = tk.IntVar(value=0)
                    ttk.Checkbutton(设置行1, text="垂直反转", variable=垂直反转映射变量).pack(side=tk.LEFT, padx=20)
                    def 启动演奏():
                        if not 当前文件路径:
                            messagebox.showinfo("提示", "请先选择一个文件或文件夹")
                            return

                        # 保存设置到 JSON
                        data = {
                            "压缩方式": 异环钢琴压缩方式变量.get(),
                            "key加减": 异环钢琴加减key变量.get(),
                            "生成json": bool(生成json演奏文件变量.get()),
                            "异环钢琴演奏速度变量": float(异环钢琴演奏速度变量.get()),
                            "垂直反转映射变量": 垂直反转映射变量.get(),
                            "水平反转映射变量": 水平反转映射变量.get(),
                        }

                        is_midi = 当前文件路径.suffix.lower() in ('.mid', '.midi')

                        if is_midi:
                            if not 音轨复选框变量:
                                messagebox.showinfo("提示", "尚未分析音轨，请重新选择文件")
                                return
                            勾选音轨 = [音轨号 for 音轨号, var in 音轨复选框变量.items() if var.get()]
                            if not 勾选音轨:
                                messagebox.showinfo("提示", "请至少勾选一个音轨")
                                return
                            data["filepath"] = str(当前文件路径)
                            data["演奏轨道"] = 勾选音轨
                            任务名 = "异环钢琴单曲"
                        else:
                            data["folderpath"] = str(当前文件路径)
                            任务名 = "异环钢琴JSON"

                        try:
                            with open(json_path, 'w', encoding='utf-8') as f:
                                json.dump(data, f, ensure_ascii=False, indent=2)
                        except Exception as e:
                            messagebox.showwarning("警告", f"保存设置失败: {e}")

                        # 启动任务（只传任务名）
                        新方式集合启动任务(任务名)
                    # ========== 控制按钮 ==========
                    控制区 = ttk.Frame(异环钢琴演奏子容器)
                    控制区.grid(row=6, column=0, pady=10)

                    ttk.Button(控制区, text="▶ 开始演奏", command=启动演奏).pack(side=tk.LEFT, padx=5)
                    ttk.Button(控制区, text="■ 停止演奏", command=函数停止任务).pack(side=tk.LEFT, padx=5)
                    ttk.Button(控制区, text="打开演奏文件夹", command=lambda :os.startfile( current_dir.parent / "外置配置文件夹")).pack(side=tk.LEFT, padx=5)
                    ttk.Button(控制区, text="打开说明书", command=lambda: os.startfile(current_dir / "异环钢琴自动演奏工具使用说明书.txt")).pack(side=tk.LEFT, padx=5)
                    ttk.Button(控制区, text="MIDI推荐网站", command=lambda: webbrowser.open("https://www.midishow.com/")).pack(side=tk.LEFT, padx=5)

                    # ---------- 内部函数 ----------




                    def 加载设置():
                        """UI 启动时从 JSON 恢复上次的设置"""
                        if not json_path.exists():
                            return
                        try:
                            with open(json_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                        except Exception:
                            return

                        # 恢复压缩方式、key、生成json
                        if "压缩方式" in data:
                            异环钢琴压缩方式变量.set(data["压缩方式"])
                        if "key加减" in data:
                            异环钢琴加减key变量.set(data["key加减"])
                        if "生成json" in data:
                            生成json演奏文件变量.set(1 if data["生成json"] else 0)
                        if "异环钢琴演奏速度变量" in data:
                            异环钢琴演奏速度变量.set(data["异环钢琴演奏速度变量"])
                        if "水平反转映射变量" in data:
                            水平反转映射变量.set(1 if data["水平反转映射变量"] else 0)
                        if "垂直反转映射变量" in data:
                            垂直反转映射变量.set(1 if data["垂直反转映射变量"] else 0)


                    # 初始化：加载上次设置
                    加载设置()
                    运行栏 = ttk.Frame(异环钢琴演奏子容器)
                    运行栏.grid(row=7, column=0, pady=5)
                    tk.Label(运行栏, text="工具设定音域：C2-B4/36-71", font=("楷体", 16, "bold", "italic"), fg="red").grid(row=1, column=0)

                def 显示任务窗口(任务):
                    for container in 子容器字典.values():
                        container.grid_remove()
                        # 显示目标子容器
                    子容器字典[任务].grid()
                    notebook.select(选项卡其他任务加载)

                异环钢琴窗口创建()



                def 异环店长特供窗口创建():
                    文本容器 = ttk.Frame(异环店长特供子容器)
                    文本容器.grid(row=0, column=0, pady=10, sticky="w")

                    def 启动异环店长特供任务():

                        新方式集合启动任务("异环店长特供")
                    创建按钮2grid(文本容器, f"启动任务", 启动异环店长特供任务, 字体配置=("微软雅黑", int(14)), width=11, height=1, 位置=0, 位置2=0, )
                    创建按钮2grid(文本容器, f"停止任务", 函数停止任务, 字体配置=("微软雅黑", int(14)), width=11, height=1, 位置=1, 位置2=0, )

                    tk.Label(文本容器, text="暂时只做了锤人，请携带娜娜莉并激活锤人加分天赋，\n在锤人时会占用鼠标，要刷都市体力还是推荐钓鱼\n"
                                            "多人时任务占用鼠标频率可能过快，\n这时需要停止请使用全局停止热键:Alt+V", font=("楷体", 16, "bold", "italic"), fg="blue").grid(row=2, column=0, sticky="w")


                def 异环超强音窗口创建():

                    文本容器 = ttk.LabelFrame(异环超强音子容器)
                    文本容器.grid(row=0, column=0, pady=10, sticky="w")
                    tk.Label(文本容器, text="按键长按时间：", font=("微软雅黑", 16), ).grid(row=0, column=0)
                    超强音按键长按时间 = tk.DoubleVar(value=0.01)
                    tk.Spinbox(文本容器, from_=0.001, to=0.5, increment=0.001, textvariable=超强音按键长按时间,
                               font=("微软雅黑", 16), relief="solid", width=5).grid(row=0, column=1)

                    tk.Label(文本容器, text="判断相似度：", font=("微软雅黑", 16), ).grid(row=0, column=2)
                    超强音判断相似度 = tk.DoubleVar(value=0.95)
                    tk.Spinbox(文本容器, from_=0.3, to=0.98, increment=0.05, textvariable=超强音判断相似度,
                               font=("微软雅黑", 16), relief="solid", width=5).grid(row=0, column=5)

                    文本容器 = ttk.LabelFrame(异环超强音子容器)
                    文本容器.grid(row=1, column=0, pady=10, sticky="w")
                    tk.Label(文本容器, text="工具控制键位:", font=("微软雅黑", 12), ).grid(row=0, column=0)
                    控制键位D变量 = tk.IntVar(value=0)
                    ttk.Checkbutton(文本容器, text="D", variable=控制键位D变量).grid(row=0, column=1)
                    控制键位F变量 = tk.IntVar(value=0)
                    ttk.Checkbutton(文本容器, text="F", variable=控制键位F变量).grid(row=0, column=2)
                    控制键位J变量 = tk.IntVar(value=0)
                    ttk.Checkbutton(文本容器, text="J", variable=控制键位J变量).grid(row=0, column=3)
                    控制键位K变量 = tk.IntVar(value=0)
                    ttk.Checkbutton(文本容器, text="K", variable=控制键位K变量).grid(row=0, column=4)


                    文本容器 = ttk.LabelFrame(异环超强音子容器)
                    文本容器.grid(row=5, column=0, pady=10, sticky="w")
                    tk.Label(文本容器, text="演奏次数:", font=("微软雅黑", 16), ).grid(row=0, column=0)
                    超强音演奏次数变量 = tk.IntVar(value=1)
                    tk.Spinbox(文本容器, from_=1, to=999, increment=1, textvariable=超强音演奏次数变量,
                               font=("微软雅黑", 16), relief="solid", width=5).grid(row=0, column=1)

                    tk.Label(文本容器, text="判断相似度：", font=("微软雅黑", 16), ).grid(row=0, column=2)
                    都市体力耗尽停下变量 = tk.BooleanVar(value=True)
                    创建复选框grid(current_dir, 文本容器, "都市体力耗尽停下", 都市体力耗尽停下变量,
                                 font=("微软雅黑", 16), 位置=0, 位置2=3, 边距x=0, 边距y=0, **复选框基础样式)

                    文本容器 = ttk.LabelFrame(异环超强音子容器)
                    文本容器.grid(row=7, column=0, pady=10, sticky="w")
                    def 加载异环超强音任务设置():
                        if getattr(sys, 'frozen', False):
                            current_dir = Path(sys.executable).parent.absolute()
                        else:
                            current_dir = APP_ROOT
                        路径 = current_dir.parent / "外置配置文件夹" / "超强音设置.json"

                        try:
                            if 路径.exists():
                                with open(路径, 'r', encoding='utf-8') as f:
                                    设置数据 = json.load(f)

                                # 加载各项设置到对应的变量
                                if "超强音按键长按时间" in 设置数据:
                                    超强音按键长按时间.set(设置数据["超强音按键长按时间"])
                                if "超强音判断相似度" in 设置数据:
                                    超强音判断相似度.set(设置数据["超强音判断相似度"])
                                if "超强音演奏次数变量" in 设置数据:
                                    超强音演奏次数变量.set(设置数据["超强音演奏次数变量"])
                                if "都市体力耗尽停下变量" in 设置数据:
                                    都市体力耗尽停下变量.set(设置数据["都市体力耗尽停下变量"])

                                if "控制键位D变量" in 设置数据:
                                    控制键位D变量.set(设置数据["控制键位D变量"])
                                if "控制键位F变量" in 设置数据:
                                    控制键位F变量.set(设置数据["控制键位F变量"])
                                if "控制键位J变量" in 设置数据:
                                    控制键位J变量.set(设置数据["控制键位J变量"])
                                if "控制键位K变量" in 设置数据:
                                    控制键位K变量.set(设置数据["控制键位K变量"])



                                print("超强音设置加载成功")
                            else:
                                print("未找到设置文件，使用默认设置")
                        except Exception as e:
                            print(f"加载设置时出错: {e}")
                            # 可以选择显示错误提示

                    def 保存异环超强音任务设置():
                        if getattr(sys, 'frozen', False):
                            current_dir = Path(sys.executable).parent.absolute()
                        else:
                            current_dir = APP_ROOT

                        路径 = current_dir.parent / "外置配置文件夹" / "超强音设置.json"
                        脚本运行速度 = 限制脚本运行速度(脚本运行速度变量.get())
                        睡眠倍数模块.脚本运行速度 = 脚本运行速度
                        try:
                            脚本运行速度 = float(脚本运行速度变量.get())
                        except Exception as e:
                            脚本运行速度 = 1
                            脚本运行速度变量.set(1)
                        try:
                            # 确保目录存在
                            路径.parent.mkdir(parents=True, exist_ok=True)

                            # 准备要保存的数据
                            设置数据 = {
                                "超强音按键长按时间": 超强音按键长按时间.get(),
                                "超强音判断相似度": 超强音判断相似度.get(),
                                "超强音演奏次数变量": 超强音演奏次数变量.get(),
                                "都市体力耗尽停下变量": 都市体力耗尽停下变量.get(),

                                "控制键位K变量": 控制键位K变量.get(),
                                "控制键位J变量": 控制键位J变量.get(),
                                "控制键位F变量": 控制键位F变量.get(),
                                "控制键位D变量": 控制键位D变量.get(),

                            }
                            # 保存到文件
                            with open(路径, 'w', encoding='utf-8') as f:
                                json.dump(设置数据, f, ensure_ascii=False, indent=4)

                            print("超强音设置保存成功")
                        except Exception as e:
                            print(f"保存设置时出错: {e}")
                            # 可以选择显示错误提示

                    def 启动异环超强音任务():
                        保存异环超强音任务设置()
                        新方式集合启动任务("异环超强音")

                    加载异环超强音任务设置()
                    创建按钮2grid(文本容器, f"启动任务", 启动异环超强音任务, 字体配置=("微软雅黑", int(14)), width=11, height=1, 位置=0, 位置2=0, )
                    创建按钮2grid(文本容器, f"停止任务", 函数停止任务, 字体配置=("微软雅黑", int(14)), width=11, height=1, 位置=0, 位置2=1, )
                    文本容器 = ttk.LabelFrame(异环超强音子容器)
                    文本容器.grid(row=9, column=0, pady=10, sticky="w")
                    tk.Label(文本容器, text="不追求S随意\n但如果追求 S 评分，请最好按照以下配置：\n\n游戏最好放置前台！以获得更好的响应效果和帧率稳定”\n不出意外应该是能每次都S\n\n\n"
                                            "1.画质请调整为性能，\n\n2.在稳定帧率的前提下，帧率越高应该会表现更好，\n包括开启2倍插帧,2倍以上插帧就没有试过了\n\n3.一定要保证帧率稳定", font=("楷体", 16, "bold", "italic"), fg="blue").grid(row=2, column=0, sticky="w")

                def 打开异环演示视频():
                    webbrowser.open("https://www.bilibili.com/video/BV1dbogBaE8x/")
                def 异环钓鱼窗口创建():
                    文本容器 = ttk.LabelFrame(异环钓鱼子容器)
                    文本容器.grid(row=0, column=0, pady=10,sticky="w")

                    卖鱼容器 = ttk.Frame(文本容器)
                    卖鱼容器.grid(row=0, column=0, pady=10, sticky="w")
                    tk.Label(卖鱼容器, text="钓鱼次数：", font=("微软雅黑", 16), ).grid(row=0, column=0)
                    异环钓鱼次数 = tk.IntVar(value=350)
                    tk.Spinbox(卖鱼容器, from_=1, to=99999, increment=10, textvariable=异环钓鱼次数,
                               font=("微软雅黑", 16), relief="solid", width=5).grid(row=0, column=1)
                    tk.Label(卖鱼容器, text="钓鱼时间(小时)：", font=("微软雅黑", 16), ).grid(row=0, column=2)
                    异环钓鱼时间 = tk.DoubleVar(value=66.6)
                    tk.Spinbox(卖鱼容器, from_=0.1, to=99999, increment=0.5, textvariable=异环钓鱼时间,
                               font=("微软雅黑", 16), relief="solid", width=5).grid(row=0, column=3)
                    text = "达到最大钓鱼次数或者达到最大钓鱼时间都会停止任务，\n如：设定钓鱼次数999，钓鱼时间1小时，1小时后钓鱼次数肯定没有达到999次，但这时依然会停止任务"
                    创建按钮2grid(卖鱼容器, "❓", lambda 文本=text: 截图方式提示窗口(文本, 标题="钓多少次买饵说明"), 字体配置=("微软雅黑", 14), width=2, height=1, 位置=0, 位置2=6, )



                    卖鱼容器 = ttk.Frame(文本容器)
                    卖鱼容器.grid(row=5, column=0, pady=10, sticky="w")

                    tk.Label(卖鱼容器, text="判断区域识图相似度：", font=("微软雅黑", 16), ).grid(row=0, column=2)
                    判断区域识图相似度变量 = tk.DoubleVar(value=0.9)
                    tk.Spinbox(卖鱼容器, from_=0.5, to=1, increment=0.052, textvariable=判断区域识图相似度变量,
                               font=("微软雅黑", 16), relief="solid", width=5).grid(row=0, column=3)
                    text = "默认0.9，\n需要到和判断区域颜色相近的区域钓鱼请尝试提高相似度\n还是不行的话就没有办法了"
                    创建按钮2grid(卖鱼容器, "❓", lambda 文本=text: 截图方式提示窗口(文本, 标题="判断区域识图相似度"), 字体配置=("微软雅黑", 14), width=2, height=1, 位置=0, 位置2=4, )
                    tk.Label(卖鱼容器, text="\u3000识图判断间隔(秒)：", font=("微软雅黑", 16), ).grid(row=0, column=5)
                    异环钓鱼识图判断频率变量 = tk.DoubleVar(value=0.05)
                    tk.Spinbox(卖鱼容器, from_=0.001, to=999, increment=0.005, textvariable=异环钓鱼识图判断频率变量,
                               font=("微软雅黑", 16), relief="solid", width=5).grid(row=0, column=6)

                    卖鱼容器 = ttk.Frame(文本容器)
                    卖鱼容器.grid(row=10, column=0, pady=10, sticky="w")
                    卖鱼容器1 = ttk.Frame(卖鱼容器)
                    卖鱼容器1.grid(row=0, column=0, pady=10, sticky="w")
                    tk.Label(卖鱼容器1, text="钓多少次卖鱼：", font=("微软雅黑", 16), ).grid(row=0, column=0)
                    钓多少次卖鱼 = tk.IntVar(value=200)
                    tk.Spinbox(卖鱼容器1, from_=1, to=99999, increment=10, textvariable=钓多少次卖鱼,
                               font=("微软雅黑", 16), relief="solid", width=5).grid(row=0, column=1)


                    异环鱼舱满卖鱼变量 = tk.IntVar(value=0)
                    创建复选框grid(current_dir, 卖鱼容器1, "舱满卖鱼", 异环鱼舱满卖鱼变量,
                                   font=("微软雅黑", 16), 位置=0, 位置2=3, 边距x=(0,50), 边距y=0, **复选框基础样式)
                    卖鱼容器2 = ttk.Frame(卖鱼容器)
                    卖鱼容器2.grid(row=1, column=0, pady=10, sticky="w")
                    tk.Label(卖鱼容器2, text="钓多少次买饵：", font=("微软雅黑", 16), ).grid(row=0, column=4)
                    钓多少次买饵 = tk.IntVar(value=200)
                    tk.Spinbox(卖鱼容器2, from_=1, to=99999, increment=10, textvariable=钓多少次买饵,
                               font=("微软雅黑", 16), relief="solid", width=5).grid(row=0, column=5)
                    text = "买鱼饵只会买万能鱼饵(售价5贝壳)，\n购买规则为：钓100次买饵就买2组99，钓200次买饵就买3组99，以此类推\n所以如果你要开启买鱼饵，必须装备万能鱼饵去钓鱼，\n卖鱼买饵都有失败卡住重试机制，触发重试时间应该不超过30秒"
                    创建按钮2grid(卖鱼容器2, "❓", lambda 文本=text: 截图方式提示窗口(文本, 标题="钓多少次买饵说明"), 字体配置=("微软雅黑", 14), width=2, height=1, 位置=0, 位置2=6, )


                    异环饵空卖饵变量 = tk.IntVar(value=0)
                    创建复选框grid(current_dir, 卖鱼容器2, "饵空卖万能饵，并切换万能饵", 异环饵空卖饵变量,
                                   font=("微软雅黑", 16), 位置=0, 位置2=7, 边距x=(0), 边距y=0, **复选框基础样式)
                    text = "买鱼饵只会买万能鱼饵(售价5贝壳)，\n鱼饵空了就只买一组99的万能鱼饵。并切换万能饵\n卖鱼买饵都有失败卡住重试机制，触发重试时间应该不超过30秒"
                    创建按钮2grid(卖鱼容器2, "❓", lambda 文本=text: 截图方式提示窗口(文本, 标题="饵空卖万能饵，并切换万能饵说明"), 字体配置=("微软雅黑", 14), width=2, height=1, 位置=0, 位置2=8, )
                    tk.Label(选项卡任务列表容器1_2, text="", font=("微软雅黑", 16)).grid(row=0, column=7, sticky=tk.W, )
                    文本容器 = ttk.LabelFrame(异环钓鱼子容器)
                    文本容器.grid(row=1, column=0, pady=10, sticky="w")
                    卖鱼容器 = ttk.Frame(文本容器)
                    卖鱼容器.grid(row=1, column=0, pady=10, sticky="w")
                    异环钓鱼上钩截图变量 = tk.IntVar()
                    创建复选框grid(current_dir, 卖鱼容器, "上钩截图", 异环钓鱼上钩截图变量,
                                   font=("微软雅黑", 16), 位置=0, 位置2=4, 边距x=0, 边距y=0, **复选框基础样式)
                    上钩截图路径 = current_dir / "异环图片" / "钓鱼" / "上钩截图"
                    创建按钮2grid(卖鱼容器, f"打开保存文件夹", lambda :os.startfile(上钩截图路径), 字体配置=("微软雅黑", int(14)), width=14, height=1, 位置=0, 位置2=5, )
                    卖鱼容器 = ttk.Frame(文本容器)
                    卖鱼容器.grid(row=2, column=0, pady=10, sticky="w")
                    异环钓鱼运行完毕后关闭游戏变量 = tk.IntVar()
                    创建复选框grid(current_dir, 卖鱼容器, "运行完关闭游戏", 异环钓鱼运行完毕后关闭游戏变量,
                                   font=("微软雅黑", 16), 位置=0, 位置2=7, 边距x=0, 边距y=0, **复选框基础样式)

                    异环钓鱼运行完毕后电脑关机变量 = tk.IntVar()
                    创建复选框grid(current_dir, 卖鱼容器, "运行完电脑关机", 异环钓鱼运行完毕后电脑关机变量,
                                   font=("微软雅黑", 16), 位置=0, 位置2=9, 边距x=0, 边距y=0, **复选框基础样式)

                    #tk.Label(文本容器, text="买鱼饵只会买万能鱼饵(售价5贝壳)，\n购买规则为：钓100次买饵就买2组99，钓200次买饵就买3组99，以此类推\n所以如果你要开启买鱼饵，必须装备万能鱼饵去钓鱼，\n卖鱼买饵都有失败卡住重试机制，触发重试时间应该不超过30秒", font=("楷体", 16, "bold", "italic"), fg="green").grid(row=0, column=4, sticky="w")
                    文本容器 = ttk.LabelFrame(异环钓鱼子容器)
                    文本容器.grid(row=3, column=0, pady=10,sticky="w")

                    def 加载异环钓鱼设置():
                        if getattr(sys, 'frozen', False):
                            current_dir = Path(sys.executable).parent.absolute()
                        else:
                            current_dir = APP_ROOT
                        路径 = current_dir / "异环图片" / "钓鱼" / "钓鱼设置.json"

                        try:
                            if 路径.exists():
                                with open(路径, 'r', encoding='utf-8') as f:
                                    设置数据 = json.load(f)

                                # 加载各项设置到对应的变量
                                if "钓鱼次数" in 设置数据:
                                    异环钓鱼次数.set(设置数据["钓鱼次数"])
                                if "异环钓鱼时间" in 设置数据:
                                    异环钓鱼时间.set(设置数据["异环钓鱼时间"])
                                if "判断频率" in 设置数据:
                                    异环钓鱼识图判断频率变量.set(设置数据["判断频率"])
                                if "钓多少次卖鱼" in 设置数据:
                                    钓多少次卖鱼.set(设置数据["钓多少次卖鱼"])
                                if "钓多少次买饵" in 设置数据:
                                    钓多少次买饵.set(设置数据["钓多少次买饵"])
                                if "异环钓鱼运行完毕后关闭游戏变量" in 设置数据:
                                    异环钓鱼运行完毕后关闭游戏变量.set(设置数据["异环钓鱼运行完毕后关闭游戏变量"])
                                if "异环钓鱼运行完毕后电脑关机变量" in 设置数据:
                                    异环钓鱼运行完毕后电脑关机变量.set(设置数据["异环钓鱼运行完毕后电脑关机变量"])

                                if "异环钓鱼上钩截图变量" in 设置数据:
                                    异环钓鱼上钩截图变量.set(设置数据["异环钓鱼上钩截图变量"])
                                if "异环鱼舱满卖鱼变量" in 设置数据:
                                    异环鱼舱满卖鱼变量.set(设置数据["异环鱼舱满卖鱼变量"])
                                if "异环饵空卖饵变量" in 设置数据:
                                    异环饵空卖饵变量.set(设置数据["异环饵空卖饵变量"])
                                if "判断区域识图相似度变量" in 设置数据:
                                    判断区域识图相似度变量.set(设置数据["判断区域识图相似度变量"])



                                print("钓鱼设置加载成功")
                            else:
                                print("未找到设置文件，使用默认设置")
                        except Exception as e:
                            print(f"加载设置时出错: {e}")
                            # 可以选择显示错误提示

                    def 保存异环钓鱼设置():
                        if getattr(sys, 'frozen', False):
                            current_dir = Path(sys.executable).parent.absolute()
                        else:
                            current_dir = APP_ROOT

                        路径 = current_dir / "异环图片" / "钓鱼" / "钓鱼设置.json"
                        脚本运行速度 = 限制脚本运行速度(脚本运行速度变量.get())
                        睡眠倍数模块.脚本运行速度 = 脚本运行速度
                        try:
                            脚本运行速度 = float(脚本运行速度变量.get())
                        except Exception as e:
                            脚本运行速度 = 1
                            脚本运行速度变量.set(1)
                        try:
                            # 确保目录存在
                            路径.parent.mkdir(parents=True, exist_ok=True)

                            # 准备要保存的数据
                            设置数据 = {
                                "钓鱼次数": 异环钓鱼次数.get(),
                                "异环钓鱼时间": 异环钓鱼时间.get(),
                                "判断频率": 异环钓鱼识图判断频率变量.get(),
                                "异环钓鱼运行完毕后关闭游戏变量": 异环钓鱼运行完毕后关闭游戏变量.get(),
                                "异环钓鱼运行完毕后电脑关机变量": 异环钓鱼运行完毕后电脑关机变量.get(),


                                "钓多少次卖鱼": 钓多少次卖鱼.get(),
                                "钓多少次买饵": 钓多少次买饵.get(),
                                "异环钓鱼上钩截图变量": 异环钓鱼上钩截图变量.get(),
                                "异环鱼舱满卖鱼变量": 异环鱼舱满卖鱼变量.get(),
                                "异环饵空卖饵变量": 异环饵空卖饵变量.get(),
                                "判断区域识图相似度变量": 判断区域识图相似度变量.get(),

                            }
                            # 保存到文件
                            with open(路径, 'w', encoding='utf-8') as f:
                                json.dump(设置数据, f, ensure_ascii=False, indent=4)

                            print("钓鱼设置保存成功")
                        except Exception as e:
                            print(f"保存设置时出错: {e}")
                            # 可以选择显示错误提示

                    def 启动异环钓鱼任务():
                        保存异环钓鱼设置()
                        新方式集合启动任务("异环钓鱼")

                    加载异环钓鱼设置()
                    创建按钮2grid(文本容器, f"启动任务", 启动异环钓鱼任务, 字体配置=("微软雅黑", int(14)), width=11, height=1, 位置=0, 位置2=0, )
                    创建按钮2grid(文本容器, f"停止任务", 函数停止任务, 字体配置=("微软雅黑", int(14)), width=11, height=1, 位置=0, 位置2=2, )
                    创建按钮2grid(文本容器, f"帮助说明",
                                  lambda: os.startfile(Path(rf"{current_dir}\异环图片\钓鱼\帮助说明.png")),
                                  字体配置=("微软雅黑", int(14)), width=11, height=1,
                                  位置=0, 位置2=3, )


                    创建按钮2grid(文本容器, f"打开演示视频", 打开异环演示视频, 字体配置=("微软雅黑", int(14)), width=11, height=1, 位置=0, 位置2=3, )
                    tk.Label(文本容器, text="看看你的运行效果和演示视频是否一致", font=("楷体", 16, "bold", "italic"), fg="green").grid(row=0, column=4, sticky="w")
                    文本容器 = ttk.Frame(异环钓鱼子容器)
                    文本容器.grid(row=4, column=0, pady=10,sticky="w")


                    tk.Label(文本容器, text="1.请确保钓鱼背景和判断区域不相似(比如背景是海，都是蓝色)，\n不然会判断失败，如果相似请更换钓鱼点位\n\n关闭游戏和显卡驱动插帧，AMD显卡请在显卡驱动和游戏关闭FSR等相关功能", font=("楷体", 16, "bold", "italic"), fg="red").grid(row=0, column=0, sticky="w")

                    #tk.Label(文本容器, text="\n\n异环虽然能后台传递鼠标坐标，但不知道为什么很多地方真实鼠标不在那个位置就不能点击\n"
                                            #"而有的地方则可以不用真实鼠标在那个地方就能点击，很迷，所以卖鱼买饵时会占用一点点鼠标", font=("楷体", 16, "bold", "italic"), fg="red").grid(row=9, column=0,sticky="w")

                异环钓鱼窗口创建()
                异环店长特供窗口创建()
                异环超强音窗口创建()
                任务1选择变量=None
                任务2选择变量 = None
                创建按钮2grid(选项卡任务列表容器1_2, "异环钢琴", lambda: 执行器.提交任务(显示任务窗口, "异环钢琴", 异步=False),
                              字体配置=("微软雅黑", 小功能按钮字体), width=小功能按钮长度, height=1, 位置=1, 位置2=1)
                创建按钮2grid(选项卡任务列表容器1_2, "异环钓鱼", lambda: 执行器.提交任务(显示任务窗口,"异环钓鱼", 异步=False),
                              字体配置=("微软雅黑", 小功能按钮字体), width=小功能按钮长度, height=1, 位置=1, 位置2=2)
                创建按钮2grid(选项卡任务列表容器1_2, "店长特供", lambda: 执行器.提交任务(显示任务窗口,"异环店长特供", 异步=False),
                              字体配置=("微软雅黑", 小功能按钮字体), width=小功能按钮长度, height=1, 位置=2, 位置2=1)
                创建按钮2grid(选项卡任务列表容器1_2, "超强音", lambda: 执行器.提交任务(显示任务窗口,"异环超强音", 异步=False),
                              字体配置=("微软雅黑", 小功能按钮字体), width=小功能按钮长度, height=1, 位置=2, 位置2=2)

                def auto_battle_task(设置任务名,设置任务编号=1):
                    try:
                        if 设置任务编号==1:
                            任务1选择变量.set(设置任务名)
                        elif 设置任务编号==2:
                            任务2选择变量.set(设置任务名)
                        else:
                            任务1选择变量.set(设置任务名)
                        执行器.提交任务(显示任务窗口, "异环其他任务", 异步=False)
                    except Exception as e:
                        print(e)

                创建按钮2grid(选项卡任务列表容器1_2, "自动战斗", lambda :auto_battle_task("自动战斗"),
                              字体配置=("微软雅黑", 小功能按钮字体), width=小功能按钮长度, height=1, 位置=3, 位置2=1)
                创建按钮2grid(选项卡任务列表容器1_2, "自动闪避弹刀", lambda: auto_battle_task("自动闪避弹刀",2),
                              字体配置=("微软雅黑", 小功能按钮字体), width=小功能按钮长度, height=1, 位置=3, 位置2=2)


                创建按钮2grid(选项卡任务列表容器1_2, "自动按F", lambda :auto_battle_task("自动按F"),
                              字体配置=("微软雅黑", 小功能按钮字体), width=小功能按钮长度, height=1, 位置=4, 位置2=1)

                创建按钮2grid(选项卡任务列表容器1_2, "更多任务", lambda: 执行器.提交任务(显示任务窗口,"异环其他任务", 异步=False),
                              字体配置=("微软雅黑", 小功能按钮字体), width=小功能按钮长度, height=1, 位置=4, 位置2=2)


                def 手动检查更新():
                    网页网址 = "https://github.com/nokiruy/Noki-Heaven-Burns-Red-Auto/releases"
                    if 异环脚本运行:
                        网页网址 = "https://github.com/nokiruy/Noki-NTE-Auto/releases"
                    if 幻塔脚本运行:
                        网页网址 = "https://github.com/nokiruy/Noki-Hotta-Auto/releases"
                    文本 = 检查更新(f"v{current_version}", 网页网址)
                    print(文本)
                    if 文本 != False:
                        版本更新提示窗口(文本, 标题="版本更新提示")
                创建按钮2grid(选项卡任务列表容器1_2, "检查更新", lambda: 执行器.提交任务(手动检查更新,  异步=True),
                              字体配置=("微软雅黑", 小功能按钮字体), width=小功能按钮长度, height=1, 位置=5, 位置2=2)

                选项卡任务列表容器1_2 = ttk.Frame(
                    选项卡任务列表容器1,
                    style="Card.TFrame",
                    padding=(14, 12),
                )
                选项卡任务列表容器1_2.grid(
                    row=1, column=0, padx=0, pady=(12, 0), sticky="new"
                )

                ttk.Label(
                    选项卡任务列表容器1_2,
                    text="运行偏好",
                    style="CardSection.TLabel",
                ).grid(row=0, column=0, sticky="w", pady=(0, 8))
                异环游戏静音容器 = ttk.Frame(
                    选项卡任务列表容器1_2, style="Card.TFrame"
                )
                异环游戏静音容器.grid(row=1, column=0, padx=0, pady=0, sticky=tk.W, )
                异环游戏静音变量=tk.IntVar(value=0)
                创建复选框grid(current_dir=current_dir, 归属=异环游戏静音容器, 标签="运行任务时游戏静音", 绑定变量=异环游戏静音变量, font=("微软雅黑", 14, "bold",), 位置=0, 位置2=0, 边距x=10, 边距y=0, **复选框基础样式)
                创建按钮2grid(异环游戏静音容器, "❓", lambda: os.startfile(Path(current_dir / r"UI\帮助说明\游戏静音.png")), 字体配置=("微软雅黑", 14), width=2, height=1, 位置=0, 位置2=1, )
                GPU加速识图容器 = ttk.Frame(
                    选项卡任务列表容器1_2, style="Card.TFrame"
                )
                GPU加速识图容器.grid(row=2, column=0, padx=0, pady=0, sticky=tk.W, )
                GPU加速识图变量 = tk.IntVar(value=0)
                创建复选框grid(current_dir=current_dir, 归属=GPU加速识图容器, 标签="GPU加速OpenCV", 绑定变量=GPU加速识图变量, font=("微软雅黑", 14, "bold",), 位置=0, 位置2=0, 边距x=10, 边距y=0, **复选框基础样式)
                创建按钮2grid(GPU加速识图容器, "❓", lambda 文本="稍微好一点的cpu就不用开启这个了\n识图速度慢，或者想在高频识图任务有更好表现的可以尝试开启\n比如超强音任务": 截图方式提示窗口(文本, 标题="GPU加速OpenCV"), 字体配置=("微软雅黑", 14), width=2, height=1, 位置=0, 位置2=1, )

                ttk.Separator(选项卡任务列表容器1_2).grid(
                    row=3, column=0, sticky="ew", pady=10
                )
                from 后台键鼠 import set_process_priority,find_pids_by_exe
                异环工具优先级配置文件= current_dir.parent / "外置配置文件夹"/"进程优先级.json"
                if getattr(sys, 'frozen', False):
                    异环工具路径 = current_dir / "Noki_NTE_Auto.exe"
                else:
                    异环工具路径 = None  # 非打包环境，不需要操作该 exe
                异环工具优先级容器 = ttk.Frame(
                    选项卡任务列表容器1_2, style="Card.TFrame"
                )
                异环工具优先级容器.grid(row=4, column=0, padx=0, pady=0)
                tk.Label(异环工具优先级容器, text="进程优先级:", font=("微软雅黑", 16)).grid(row=0, column=0, sticky=tk.W, )
                异环工具优先级变量=tk.StringVar(value="正常（默认）")

                异环工具优先级下拉框 = ttk.Combobox(异环工具优先级容器, textvariable=异环工具优先级变量, font=("微软雅黑", 11), width=12)
                异环工具优先级下拉框.grid(row=0, column=1)
                异环工具优先级下拉框["values"]=["实时（最高，慎用）","高","高于正常","正常（默认）"]
                PRIORITY_MAP = {"实时（最高，慎用）": "REALTIME", "高": "HIGH", "高于正常": "ABOVE_NORMAL", "正常（默认）": "NORMAL",}

                def 读取进程优先级配置():
                    """从 JSON 文件读取之前保存的优先级配置"""
                    默认值 = "正常（默认）"
                    try:
                        if 异环工具优先级配置文件.exists():
                            with open(异环工具优先级配置文件, "r", encoding="utf-8") as f:
                                config = json.load(f)
                            return config.get("priority", 默认值)
                    except Exception as e:
                        print(f"读取进程优先级配置失败: {e}")
                    return 默认值

                def 保存进程优先级配置(priority):
                    """保存当前优先级到 JSON 文件"""
                    try:
                        异环工具优先级配置文件.parent.mkdir(parents=True, exist_ok=True)
                        with open(异环工具优先级配置文件, "w", encoding="utf-8") as f:
                            json.dump({"priority": priority}, f, ensure_ascii=False, indent=2)
                    except Exception as e:
                        print(f"保存进程优先级配置失败: {e}")

                def 设置异环进程优先级(priority_display):
                    """根据下拉框显示值，找到异环工具进程并设置优先级"""
                    if not 异环工具路径:
                        print("非打包环境，无需操作")
                        # 非打包环境，无需操作
                        return

                    # 将显示值转换为 API 需要的字符串
                    api_priority = PRIORITY_MAP.get(priority_display)
                    if not api_priority:
                        print(f"未知优先级选项: {priority_display}")
                        return

                    try:
                        pids = find_pids_by_exe(str(异环工具路径))
                        if not pids:
                            # 进程未运行，只保存配置，不设置
                            return
                        # 如果存在多个同名进程，默认处理第一个（通常只有一个）
                        for pid in pids:
                            threading.Thread(target=set_process_priority, args=(pid, api_priority), daemon=True).start()
                    except Exception as e:
                        print(f"设置进程优先级异常: {e}")

                def 应用初始进程优先级():
                    """启动时读取配置并设置优先级"""
                    saved_priority = 读取进程优先级配置()
                    异环工具优先级变量.set(saved_priority)
                    # 如果有 exe 路径，尝试设置一次
                    设置异环进程优先级(saved_priority)

                def 下拉框改变事件(event=None):
                    """当下拉框手动改变时，保存并设置优先级"""
                    selected = 异环工具优先级变量.get()
                    保存进程优先级配置(selected)
                    设置异环进程优先级(selected)

                # 绑定下拉框选择事件
                异环工具优先级下拉框.bind("<<ComboboxSelected>>", 下拉框改变事件)

                # 初始化：读取配置并应用到 UI 和进程
                应用初始进程优先级()


                异环工具优先级说明容器 = ttk.Frame(
                    选项卡任务列表容器1_2, style="Card.TFrame"
                )
                异环工具优先级说明容器.grid(row=5, column=0, padx=0, pady=0)

                选项卡任务列表中间容器 = ttk.Frame(
                    选项卡任务列表,
                    style="Card.TFrame",
                    padding=(18, 16),
                )
                选项卡任务列表中间容器.grid(
                    row=0, column=1, padx=(12, 0), pady=0, sticky="new"
                )
                选项卡任务列表中间容器.columnconfigure(0, weight=1)

                ttk.Label(
                    选项卡任务列表中间容器,
                    text="使用前检查",
                    style="CardSection.TLabel",
                ).grid(row=0, column=0, sticky="w")
                ttk.Label(
                    选项卡任务列表中间容器,
                    text=(
                        "运行图像识别任务前，请确认：\n\n"
                        "• 关闭 HDR、滤镜、护眼模式和色彩增强\n"
                        "• 关闭性能监控浮窗，避免遮挡游戏画面\n"
                        "• 关闭游戏与显卡驱动插帧\n"
                        "• AMD 显卡建议关闭 FSR 等画面处理"
                    ),
                    style="CardMuted.TLabel",
                    justify="left",
                ).grid(row=1, column=0, sticky="w", pady=(10, 14))
                ttk.Separator(选项卡任务列表中间容器).grid(
                    row=2, column=0, sticky="ew", pady=(0, 12)
                )
                ttk.Label(
                    选项卡任务列表中间容器,
                    text="工具永久免费，禁止倒卖。",
                    style="CardSection.TLabel",
                ).grid(row=3, column=0, sticky="w")
                ttk.Label(
                    选项卡任务列表中间容器,
                    text="如遇到问题，可先对照演示视频检查运行环境。",
                    style="CardMuted.TLabel",
                ).grid(row=4, column=0, sticky="w", pady=(5, 10))
                创建按钮2grid(
                    选项卡任务列表中间容器,
                    "查看演示视频",
                    lambda: 执行器.提交任务(打开异环演示视频, 异步=False),
                    字体配置=("微软雅黑", 小功能按钮字体),
                    width=小功能按钮长度,
                    height=1,
                    位置=5,
                    位置2=0,
                    style="Primary.TButton",
                )

                任务1选择变量 = tk.StringVar(value="自动战斗")
                任务2选择变量 = tk.StringVar(value="自动跳过剧情")
                任务3选择变量 = tk.StringVar(value="自动按F")
                任务4选择变量 = tk.StringVar(value="鼠标快速打开esc界面")

                识图间隔变量 = tk.DoubleVar(value=0.1)
                变轨技能自定义按键 = tk.StringVar(value="E")
                极轨终结自定义按键 = tk.StringVar(value="Q")
                弧盘技能自定义按键 = tk.StringVar(value="R")

                # 四个任务的线程事件（每个任务独立）
                线程事件停止循环1 = threading.Event()
                线程事件任务循环1 = threading.Event()
                线程事件停止循环2 = threading.Event()
                线程事件任务循环2 = threading.Event()
                线程事件停止循环3 = threading.Event()
                线程事件任务循环3 = threading.Event()
                线程事件停止循环4 = threading.Event()
                线程事件任务循环4 = threading.Event()

                # 用于保存和加载的映射（辅助）
                任务选择变量列表 = [任务1选择变量, 任务2选择变量, 任务3选择变量, 任务4选择变量]
                任务事件对列表 = [
                    (线程事件停止循环1, 线程事件任务循环1),
                    (线程事件停止循环2, 线程事件任务循环2),
                    (线程事件停止循环3, 线程事件任务循环3),
                    (线程事件停止循环4, 线程事件任务循环4),
                ]

                异环自定义txt任务文件夹=current_dir.parent / "外置配置文件夹"/"txt自定义脚本"

                任务状态标签列表=[]
                def 函数保存其他任务设置():
                    路径 = current_dir.parent / "外置配置文件夹" / "任务选择设置.json"
                    设置数据 = {
                        "识图间隔变量": 识图间隔变量.get(),
                        "变轨技能自定义按键": 变轨技能自定义按键.get(),
                        "极轨终结自定义按键": 极轨终结自定义按键.get(),
                        "弧盘技能自定义按键": 弧盘技能自定义按键.get(),
                    }
                    for i, var in enumerate(任务选择变量列表, 1):
                        设置数据[f"任务{i}选择变量"] = var.get()
                    with open(路径, 'w', encoding='utf-8') as f:
                        json.dump(设置数据, f, ensure_ascii=False, indent=4)
                def 创建单个任务界面(父容器, 行, 列, 任务编号, 默认值, 热键提示文本):
                    """
                    在指定网格位置创建一个完整的任务选择区域（下拉框、动态配置、提示标签等）
                    返回该任务的选择变量 (tk.StringVar)
                    """
                    # 根据任务编号获取对应的变量名，动态赋值给模块级变量
                    var_name = f"任务{任务编号}选择变量" if 任务编号 != 1 else "任务1选择变量"
                    if 任务编号 == 1:
                        var_name = "任务1选择变量"  # 方便统一
                    # 实际上我们已经在全局定义好了变量，这里直接获取引用
                    if 任务编号 == 1:
                        选择变量 = 任务1选择变量
                    elif 任务编号 == 2:
                        选择变量 = 任务2选择变量
                    elif 任务编号 == 3:
                        选择变量 = 任务3选择变量
                    else:
                        选择变量 = 任务4选择变量

                    子容器 = ttk.LabelFrame(父容器,text=f"任务{任务编号}")
                    子容器.grid(
                        row=行,
                        column=列,
                        pady=8,
                        padx=8,
                        sticky="nsew",
                    )
                    父容器.columnconfigure(列, weight=1)
                    文本容器 = ttk.Frame(子容器, style="Card.TFrame")
                    文本容器.grid(row=0, column=0, pady=4, sticky="nsew")
                    容器 = ttk.Frame(文本容器, style="Card.TFrame")
                    容器.grid(row=0, column=0, pady=10, sticky="w")

                    tk.Label(容器, text=f"任务{任务编号}选择:", font=("微软雅黑", 16)).grid(row=0, column=0, sticky=tk.W)

                    固定任务列表 = ["自动战斗", "自动跳过剧情", "自动按F", "鼠标快速打开esc界面","自动闪避弹刀"]
                    下拉框 = ttk.Combobox(容器, textvariable=选择变量, font=("微软雅黑", 16), width=20)
                    下拉框.grid(row=0, column=1)

                    def 刷新任务列表():
                        新列表 = list(固定任务列表)
                        try:
                            if 异环自定义txt任务文件夹.exists() and 异环自定义txt任务文件夹.is_dir():
                                txt文件列表 = list(异环自定义txt任务文件夹.glob("*.txt"))
                                for txt文件 in txt文件列表:
                                    显示名 = f"[txt]{txt文件.stem}"
                                    新列表.append(显示名)
                        except Exception as e:
                            print(f"扫描txt任务文件夹失败：{e}")
                        下拉框["values"] = 新列表
                        if 选择变量.get() not in 新列表:
                            选择变量.set(默认值)

                    刷新按钮 = ttk.Button(容器, text="刷新", command=刷新任务列表)
                    刷新按钮.grid(row=0, column=2)
                    刷新任务列表()

                    动态配置容器 = ttk.Frame(文本容器)
                    动态配置容器.grid(row=1, column=0, pady=5, sticky="w")

                    def 强制换行文本(文本: str, 最大长度: int = 24) -> str:
                        """辅助函数，用于txt注释换行"""
                        行列表 = []
                        for 原始行 in 文本.splitlines():
                            当前行 = 原始行.rstrip('\n')
                            if len(当前行) <= 最大长度:
                                行列表.append(当前行)
                            else:
                                for i in range(0, len(当前行), 最大长度):
                                    行列表.append(当前行[i:i + 最大长度])
                        return '\n'.join(行列表)

                    def 任务切换回调(*args):
                        for child in 动态配置容器.winfo_children():
                            child.destroy()
                        当前选择 = 选择变量.get()

                        if 当前选择 == "自动按F":
                            ttk.Label(动态配置容器, text="识图间隔：", font=("微软雅黑", 16)).grid(row=0, column=0, padx=5, sticky="w")
                            tk.Spinbox(动态配置容器, from_=0.001, to=5.0, increment=0.05,
                                       textvariable=识图间隔变量, font=("微软雅黑", 16),
                                       relief="solid", width=5).grid(row=0, column=1, padx=5)
                            ttk.Label(动态配置容器, text="(单位：秒，支持小数)", font=("微软雅黑", 10),
                                      foreground="gray").grid(row=0, column=2, columnspan=2, sticky="w", padx=5)

                        elif 当前选择 == "自动战斗":
                            ttk.Label(动态配置容器, text="变轨技能按键：").grid(row=0, column=0, padx=5, pady=5, sticky="e")
                            tk.Entry(动态配置容器, textvariable=变轨技能自定义按键, width=10).grid(row=0, column=1, padx=5, pady=5, sticky="w")
                            ttk.Label(动态配置容器, text="极轨终结按键：").grid(row=1, column=0, padx=5, pady=5, sticky="e")
                            tk.Entry(动态配置容器, textvariable=极轨终结自定义按键, width=10).grid(row=1, column=1, padx=5, pady=5, sticky="w")
                            ttk.Label(动态配置容器, text="弧盘技能按键：").grid(row=2, column=0, padx=5, pady=5, sticky="e")
                            tk.Entry(动态配置容器, textvariable=弧盘技能自定义按键, width=10).grid(row=2, column=1, padx=5, pady=5, sticky="w")
                        elif 当前选择 == "自动闪避弹刀":

                            ttk.Label(动态配置容器, text="(提醒：通过音频波形判定，电脑和游戏不能静音，\n最好也不要播放除了异环游戏外的其他声音)",
                                      font=("微软雅黑", 14), foreground="gray").grid(row=0, column=0,  sticky="w", padx=5)
                            """     自动闪避弹刀容器 = ttk.Frame(动态配置容器)
                            自动闪避弹刀容器.grid(row=1, column=0, pady=5, sticky="w")
                            ttk.Label(自动闪避弹刀容器, text="带通能量占比：", font=("微软雅黑", 16)).grid(row=0, column=0, padx=5, sticky="w")
                            tk.Spinbox(自动闪避弹刀容器, from_=0.001, to=5.0, increment=0.05,
                                       textvariable=识图间隔变量, font=("微软雅黑", 16),
                                       relief="solid", width=5).grid(row=0, column=1, padx=5)
                            ttk.Label(自动闪避弹刀容器, text="高通截止频率：", font=("微软雅黑", 16)).grid(row=1, column=0, padx=5, sticky="w")
                            tk.Spinbox(自动闪避弹刀容器, from_=0.001, to=5.0, increment=0.05,
                                       textvariable=识图间隔变量, font=("微软雅黑", 16),
                                       relief="solid", width=5).grid(row=1, column=1, padx=5)"""
                        elif 当前选择 == "鼠标快速打开esc界面":
                            ttk.Label(动态配置容器, text="(提醒：如果用键盘触发，键盘Alt按下后，再按下V/T，\n短暂等待esc界面明显打开后再弹起两个按键)",
                                      font=("微软雅黑", 14), foreground="gray").grid(row=0, column=2, columnspan=2, sticky="w", padx=5)

                        elif 当前选择 == "自动跳过剧情":
                            ttk.Label(动态配置容器, text="识图控制，遇到对话按空格，跳过键按esc",
                                      font=("微软雅黑", 16), foreground="gray").grid(row=0, column=2, columnspan=2, sticky="w", padx=5)

                        elif 当前选择.startswith("[txt]"):
                            显示名 = 当前选择[5:]
                            txt文件名 = 显示名 + ".txt"
                            txt路径 = 异环自定义txt任务文件夹 / txt文件名
                            注释文本 = ""
                            try:
                                if txt路径.exists():
                                    with open(txt路径, 'r', encoding='utf-8') as f:
                                        内容 = f.read()
                                    first_pos = 内容.find('#')
                                    last_pos = 内容.rfind('#')
                                    if first_pos != -1 and last_pos != -1 and last_pos > first_pos:
                                        原始注释 = 内容[first_pos + 1:last_pos].strip()
                                        注释文本 = 强制换行文本(原始注释, 40)
                                    else:
                                        注释文本 = "该脚本无有效注释（缺少 #...# 包裹内容）"
                                else:
                                    注释文本 = f"脚本文件不存在：{txt文件名}"
                            except Exception as e:
                                注释文本 = f"读取注释失败：{e}"

                            # 创建滚动文本框，初始高度为1（避免临时过大）
                            text_box = scrolledtext.ScrolledText(
                                动态配置容器,
                                width=48,  # 宽度与强制换行宽度匹配
                                height=1,  # 临时高度，稍后动态调整
                                font=("楷体", 13, "bold", "italic"),
                                wrap='word',  # 自动按单词换行
                                foreground="gray",
                                relief='sunken',
                                bg='#f0f0f0'
                            )

                            # 插入注释文本（尚未 grid，不可见）
                            text_box.insert('1.0', 注释文本)

                            # 获取实际显示行数（包括自动折行产生的行）
                            try:
                                # 使用 Tk 底层方法计算从第一行到末尾的显示行数
                                display_lines = int(text_box.tk.call(text_box._w, 'count', '-displaylines', '1.0', 'end'))
                            except Exception:
                                # 降级方案：按已有换行符估算（精度稍低）
                                display_lines = 注释文本.count('\n') + 1

                            max_lines = 10
                            height = min(display_lines, max_lines)  # 动态高度，超出则滚动
                            text_box.config(height=height)  # 应用计算后的高度

                            # 放置到网格中
                            text_box.grid(row=0, column=2, columnspan=2, sticky="w", padx=5)

                        else:
                            ttk.Label(动态配置容器, text="该任务无额外配置", font=("微软雅黑", 12), foreground="blue").grid(row=0, column=0, padx=5, sticky="w")

                    选择变量.trace_add("write", 任务切换回调)

                    tk.Label(文本容器, text=热键提示文本, font=("微软雅黑", 14)).grid(row=99, column=0, sticky=tk.W)

                    # 新增：任务状态标签 (row=98，放在热键提示上方)
                    状态标签 = tk.Label(文本容器, text="未运行", fg="red", font=("微软雅黑", 12, "bold"))
                    状态标签.grid(row=98, column=0, sticky=tk.W, pady=(0, 5))

                    任务切换回调()  # 初始化动态配置
                    return 选择变量, 状态标签  # 返回两个对象
                try:
                    路径 = current_dir.parent / "外置配置文件夹" / "任务选择设置.json"
                    if 路径.exists():
                        with open(路径, 'r', encoding='utf-8') as f:
                            设置数据 = json.load(f)
                        for i, var in enumerate(任务选择变量列表, 1):
                            key = f"任务{i}选择变量"
                            if key in 设置数据:
                                var.set(设置数据[key])
                        if "变轨技能自定义按键" in 设置数据:
                            变轨技能自定义按键.set(设置数据["变轨技能自定义按键"])
                        if "极轨终结自定义按键" in 设置数据:
                            极轨终结自定义按键.set(设置数据["极轨终结自定义按键"])
                        if "弧盘技能自定义按键" in 设置数据:
                            弧盘技能自定义按键.set(设置数据["弧盘技能自定义按键"])
                        if "识图间隔变量" in 设置数据:
                            识图间隔变量.set(设置数据["识图间隔变量"])
                        print("其他任务设置加载成功")
                    else:
                        print("未找到其他任务设置，使用默认设置")
                except Exception as e:
                    print(f"加载其他任务设置时出错: {e}")
                def 异环其他任务窗口创建():


                    _, 状态3 = 创建单个任务界面(异环其他任务子容器, 1, 0, 任务编号=3, 默认值="自动按F",
                                                热键提示文本="选择好任务3后，使用快捷键：鼠标上侧键 触发/停止任务")
                    _, 状态4 = 创建单个任务界面(异环其他任务子容器, 1, 1, 任务编号=4, 默认值="鼠标快速打开esc界面",
                                                热键提示文本="选择好任务4后，使用快捷键：鼠标下侧键 触发/停止任务")

                    任务状态标签列表 = [0, 0, 状态3, 状态4]  # 方便后续按编号索引

                    def 启用鼠标侧键():

                            # 启动鼠标监听线程（只启动一次）
                            from pynput import mouse
                            任务3启动 = 创建任务启动函数(3, 任务3选择变量, 线程事件停止循环3, 线程事件任务循环3, 任务状态标签列表[2])
                            任务4启动 = 创建任务启动函数(4, 任务4选择变量, 线程事件停止循环4, 线程事件任务循环4, 任务状态标签列表[3])
                            def on_click(x, y, button, pressed):
                                if pressed:
                                    if button == mouse.Button.x1:
                                        任务4启动()
                                    elif button == mouse.Button.x2:
                                        任务3启动()

                            鼠标监听器 = mouse.Listener(on_click=on_click)
                            鼠标监听器.start()
                            启用按钮.config(state="disabled", text="鼠标侧键已启用")
                            print("鼠标侧键热键已启用")

                    容器 = ttk.Frame(异环其他任务子容器)
                    容器.grid(row=2, column=0,pady=5)
                    启用按钮 = tk.Button(容器, text="点击启用鼠标侧键热键", command=启用鼠标侧键, font=("楷体", 14, "bold", "italic"),fg="blue")
                    启用按钮.grid(row=0, column=0,  pady=5)
                    def 使用中文编写脚本教程():
                        webbrowser.open("https://www.bilibili.com/video/BV1dbogBaE8x?vd_source=afc5352f066b8a32af43098464fb5654&p=3&spm_id_from=333.788.videopod.episodes")
                        webbrowser.open("https://chat.deepseek.com/share/t0c6l71ctt2km79gyv")
                    创建按钮2grid(容器, f"中文编写脚本网页教程", lambda :webbrowser.open("https://chat.deepseek.com/share/t0c6l71ctt2km79gyv"),
                                  字体配置=("微软雅黑", int(14)), width=20, height=1, 位置=0, 位置2=2, )
                    创建按钮2grid(容器, f"中文编写脚本视频教程",
                                  lambda :webbrowser.open("https://www.bilibili.com/video/BV1dbogBaE8x?vd_source=afc5352f066b8a32af43098464fb5654&p=3&spm_id_from=333.788.videopod.episodes")
                                  , 字体配置=("微软雅黑", int(14)), width=20, height=1, 位置=1, 位置2=2, )
                    创建按钮2grid(容器, f"打开脚本存放文件夹", lambda :os.startfile(异环自定义txt任务文件夹), 字体配置=("微软雅黑", int(14)), width=20, height=1, 位置=2, 位置2=2, )




                异环其他任务窗口创建()

                def 创建任务启动函数(任务编号, 选择变量, 事件停止, 事件循环, 状态标签):
                    """返回一个无参函数，用于热键触发"""

                    def update_status(running):
                        """主线程安全更新状态标签"""
                        text = f"{选择变量.get()}任务运行中" if running else "未运行"
                        color = "green" if running else "red"
                        # 假设 root 是全局主窗口变量，请根据实际变量名调整
                        window.after(0, lambda: 状态标签.config(text=text, fg=color))
                    last_trigger_time = 0
                    def 任务启动():
                        nonlocal last_trigger_time
                        current_time = time.time()
                        # 防抖：300毫秒内的重复触发直接忽略
                        if current_time - last_trigger_time < 0.5:
                            print(f"任务{任务编号}触发被防抖忽略，间隔{current_time - last_trigger_time:.3f}秒")
                            return
                        last_trigger_time = current_time
                        print(f"任务{任务编号}热键触发")
                        if 事件停止.is_set():
                            if not 事件循环.is_set():
                                return
                            事件循环.clear()
                            while True:
                                time.sleep(0.1)
                                事件循环.clear()
                                if not 事件停止.is_set():
                                    break
                            update_status(False)
                        else:
                            update_status(True)
                            事件循环.set()
                            事件停止.set()
                            函数保存设置()  # 保存全部任务设置
                            adb路径 = 获取adb路径并检查(检查分辨率=False,事件循环=事件循环,事件停止=事件停止)
                            try:
                                _, _, 异环句柄, 窗口矩形, _ = adb路径
                            except Exception:
                                return
                            游戏静音 = True
                            from 根据txt执行脚本 import 执行脚本内容

                            当前任务 = 选择变量.get()
                            if 当前任务 == "自动跳过剧情":

                                threading.Thread(target=自动剧情, args=(current_dir, adb路径, 事件循环, 事件停止)).start()
                            elif 当前任务 == "自动按F":

                                threading.Thread(target=自动按F, args=(current_dir, adb路径, 事件循环, 事件停止, 识图间隔变量.get())).start()
                            elif 当前任务 == "自动战斗":
                                threading.Thread(target=速切宏战斗线程, args=(事件循环, 事件停止, adb路径)).start()
                                threading.Thread(target=速切宏战斗线程2, args=(事件循环, 事件停止, adb路径, 变轨技能自定义按键.get(), 极轨终结自定义按键.get(), 弧盘技能自定义按键.get())).start()
                            elif 当前任务 == "自动闪避弹刀":
                                游戏静音=False
                                from 音频闪避反击 import 根据音频闪避反击任务
                                selected = 异环工具优先级变量.get()
                                if selected=="高于正常" or selected=="实时（最高，慎用）":
                                    pass
                                else:
                                    异环工具优先级变量.set("高于正常")
                                threading.Thread(target=根据音频闪避反击任务, args=(current_dir,异环句柄,事件循环, 事件停止)).start()
                            elif 当前任务 == "鼠标快速打开esc界面":
                                threading.Thread(target=鼠标快速打开esc界面, args=(adb路径, 事件循环, 事件停止)).start()
                            elif "[txt]" in 当前任务:
                                显示名 = 当前任务
                                if 显示名.startswith("[txt]"):
                                    脚本名 = 显示名[5:]
                                else:
                                    脚本名 = 显示名
                                脚本文件路径 = current_dir.parent / "外置配置文件夹" / "txt自定义脚本" / f"{脚本名}.txt"
                                try:
                                    with open(脚本文件路径, 'r', encoding='utf-8') as f:
                                        脚本内容 = f.read()
                                except Exception as e:
                                    messagebox.showerror("读取失败", f"读取脚本文件失败：{e}")
                                    return

                                def 执行脚本():
                                    执行脚本内容(异环句柄, 窗口矩形, 事件循环, 脚本内容)
                                    事件停止.clear()
                                    print(f"任务{当前任务}结束")

                                threading.Thread(target=执行脚本).start()
                            threading.Thread(target=线程持续激活, args=(异环句柄, 事件循环, 游戏静音)).start()
                            函数保存其他任务设置()
                            def 标签变化():
                                while True:
                                    time.sleep(0.5)
                                    if not 事件停止.is_set():
                                        break
                                update_status(False)

                            threading.Thread(target=标签变化, args=()).start()



                    return 任务启动

                def 注册其他任务宏热键():
                    _, 状态1 = 创建单个任务界面(异环其他任务子容器, 0, 0, 任务编号=1, 默认值="自动战斗",
                                                热键提示文本="选择好任务1后，使用快捷键：Alt+V  触发/停止任务")
                    _, 状态2 = 创建单个任务界面(异环其他任务子容器, 0, 1, 任务编号=2, 默认值="自动跳过剧情",
                                                热键提示文本="选择好任务2后，使用快捷键：Alt+T 触发/停止任务")
                    任务状态标签列表 = [状态1, 状态2]
                    任务1启动 = 创建任务启动函数(1, 任务1选择变量, 线程事件停止循环1, 线程事件任务循环1, 任务状态标签列表[0])
                    任务2启动 = 创建任务启动函数(2, 任务2选择变量, 线程事件停止循环2, 线程事件任务循环2,任务状态标签列表[1])





                    # 键盘热键绑定（始终有效）
                    keyboard.add_hotkey('alt+v', 任务1启动)
                    keyboard.add_hotkey('alt+t', 任务2启动)

                    # 鼠标监听不在这里自动启动，改为由按钮触发

                    logger.info("键盘热键绑定成功，鼠标侧键需手动启用")
                    keyboard.wait()

                threading.Thread(target=注册其他任务宏热键,
                                 args=()).start()

            for container in 子容器字典.values():
                container.grid_remove()  # 隐藏



    def 检查更新并弹窗():

        update_path = os.path.join(current_dir, 'update.json')
        with open(update_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        上次检查时间 = data["time"]
        # 将字符串转换为 datetime.date 对象
        上次检查时间 = datetime.date.fromisoformat(上次检查时间)
        logger.debug(f"上次检查更新时间：{上次检查时间}")
        today = datetime.date.today()
        logger.debug(f"现在时间：{today}")
        if today > 上次检查时间:
            update_settings = {"time": today.isoformat()}
            with open(update_path, 'w', encoding='utf-8') as file:
                json.dump(update_settings, file, ensure_ascii=False, indent=4)
            logger.debug("开始检查更新和获取兑换码")

            网页网址 = "https://github.com/nokiruy/Noki-Heaven-Burns-Red-Auto/releases"
            if 异环脚本运行:
                网页网址 = "https://github.com/nokiruy/Noki-NTE-Auto/releases"
            elif 幻塔脚本运行:
                网页网址 = "https://github.com/nokiruy/Noki-Hotta-Auto/releases"

            文本 = 检查更新(f"v{current_version}", 网页网址)
            print(文本)
            if 文本 != False and  "当前已是最新版本" not in 文本:
                版本更新提示窗口(文本, 标题="版本更新提示")
        else:

            logger.debug("距离上次检查更新不足一天，跳过")

    加载设置()

    threading.Thread(target=检查更新并弹窗,
                     args=()).start()


    threading.Thread(target=脚本启动后执行所有操作(),
                     args=()).start()
    threading.Thread(target=预先连接mumu模拟器启动线程,
                     args=()).start()

    threading.Thread(target=刷新端口列表,
                     args=()).start()
    threading.Thread(target=刷新端口列表2,
                     args=()).start()
    window.update_idletasks()
    polish_legacy_widgets(window)
    # 部分任务详情会在后台线程注册后补充控件，再做一次轻量外观整理。
    window.after(350, lambda: polish_legacy_widgets(window))
    window.deiconify()  # 显示窗口

    window.mainloop()

if __name__ == "__main__":
    开发环境跳过管理员检查 = os.environ.get("NOKI_DEV_SKIP_ADMIN", "") == "1"
    if not 开发环境跳过管理员检查 and ctypes.windll.shell32.IsUserAnAdmin() == 0:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()
    函数主程序()
