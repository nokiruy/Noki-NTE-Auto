import time

import win32gui
import win32con
import ctypes
from ctypes import wintypes
import win32process
from pathlib import Path

import os
import sys
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi

# 定义 EnumWindows 的回调函数类型
EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
WM_ACTIVATE = win32con.WM_ACTIVATE
WA_ACTIVE = 1

import win32process

import subprocess
from typing import Optional
import win32gui

def has_parent_window(hwnd: int):
    """
    判断窗口是否有父窗口，如果有则打印父窗口信息。

    :param hwnd: 目标窗口句柄
    :return: 有父窗口返回 True，否则返回 False
    """
    parent = win32gui.GetParent(hwnd)
    if parent == 0:
        return False,0

    # 获取父窗口类名和标题
    class_name = win32gui.GetClassName(parent)
    title = win32gui.GetWindowText(parent)
    print(f"父窗口句柄: {parent}")
    print(f"父窗口类名: {class_name}")
    print(f"父窗口标题: {title}")
    return True,parent
def has_child_windows(hwnd: int) -> bool:
    """
    判断指定窗口句柄是否拥有子窗口。

    :param hwnd: 目标窗口的句柄（HWND）
    :return: 如果有至少一个子窗口返回 True，否则返回 False
    """
    found = False

    def enum_callback(child_hwnd, lparam):
        nonlocal found
        found = True
        # 返回 False 以停止继续枚举
        return False

    # 枚举所有子窗口，回调函数会在每个子窗口上被调用
    win32gui.EnumChildWindows(hwnd, enum_callback, None)
    return found
def find_child_window(parent_hwnd: int, class_name: str = None, window_title: str = None) -> int:
    """
    在指定父窗口下查找符合类名和/或标题的第一个子窗口。

    :param parent_hwnd: 父窗口句柄
    :param class_name: 窗口类名（可为 None，表示不限制）
    :param window_title: 窗口标题（可为 None，表示不限制）
    :return: 找到的子窗口句柄，如果未找到则返回 0
    """
    return win32gui.FindWindowEx(parent_hwnd, 0, class_name, window_title)
class MuteDLL:
    """调用 MuteLib.dll 静音指定窗口的进程音频"""
    def __init__(self, dll_path: Optional[str] = None):
        if getattr(sys, 'frozen', False):
            base_dir = Path(sys.executable).parent
        else:
            base_dir = Path(__file__).parent

        dll_path =str( base_dir / "UI" / "端口相关" / "mutedll.dll")

        self._dll = ctypes.CDLL(dll_path)
        self._dll.MuteProcessByHwnd.argtypes = [ctypes.c_uint64, ctypes.c_bool]
        self._dll.MuteProcessByHwnd.restype = ctypes.c_bool

    def mute(self, hwnd: int, mute: bool) -> bool:
        """
        设置窗口所属进程的静音状态
        :param hwnd: 窗口句柄（Python int）
        :param mute: True=静音, False=解除
        :return: 成功返回 True，否则 False
        """
        try:
            return self._dll.MuteProcessByHwnd(hwnd, mute)
        except Exception as e:
            # DLL 内已保证不崩溃，此处仅为极端兜底
            print(f"DLL调用异常: {e}")
            return False

# 全局单例（可根据需要调整）
_mute_dll = MuteDLL()

def 窗口静音(hwnd: int, mute: bool) -> bool:
    """
    通过 DLL 设置窗口所属进程的静音状态
    接口完全兼容原 subprocess 版本
    """

    print(f"窗口{hwnd}，静音{mute}")
    return _mute_dll.mute(hwnd, mute)

def 线程持续激活(句柄,线程事件,游戏静音=True):
    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
    Tool_path = Path(current_dir) / "Tool_Settings.json"
    with open(Tool_path, 'r', encoding='utf-8') as file:
        import json
        字典 = json.load(file)
        异环游戏静音 = int(字典["异环游戏静音变量"])
    if 异环游戏静音 and 游戏静音:
        窗口静音(句柄, True)
    while 线程事件.is_set():
        窗口假激活(句柄)
        for _ in range(6):
            if not 线程事件.is_set():
                break
            time.sleep(0.5)
    if 异环游戏静音 and 游戏静音:
        窗口静音(句柄, False)


def 窗口假激活(句柄):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    if 句柄:
        # 发送激活消息
        win32gui.SendMessage(句柄, WM_ACTIVATE, WA_ACTIVE, 0)
def 检查指定窗口句柄对应的应用是否仍然存在(hwnd):
    """
    检查指定窗口句柄对应的窗口/应用是否仍然存在。

    参数:
        hwnd (int): 窗口句柄（HWND）

    返回:
        bool: 窗口存在返回 True，否则返回 False；发生异常时返回 False
    """
    try:
        # 调用 user32.dll 的 IsWindow 函数
        return bool(ctypes.windll.user32.IsWindow(hwnd))
    except:
        # 任何异常（如参数类型错误、DLL 无法加载等）均视为窗口不存在
        return False
def 获取应用路径(hwnd):
    try:
        # 获取窗口所属的进程 ID
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        # 打开进程句柄
        process_handle = kernel32.OpenProcess(0x0400 | 0x0010, False, pid)
        if not process_handle:
            return None

        # 获取可执行文件名
        exe_name = ctypes.create_unicode_buffer(1024)
        psapi.GetModuleFileNameExW(process_handle, None, exe_name, 1024)
        kernel32.CloseHandle(process_handle)

        # 返回完整的可执行文件路径
        return exe_name.value if exe_name.value else None
    except Exception as e:
        print(f"获取应用路径时发生错误: {e}")
        return None
def 获取应用路径并保存(hwnd):


    exe_path = 获取应用路径(hwnd)
    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent.absolute()
    else:
        current_dir = Path(__file__).parent.absolute()

    txt_path = os.path.join(current_dir,  'app_path.txt')
    # 将 exe_path 写入到文件
    if hwnd:
        try:
            with open(txt_path, 'w', encoding='utf-8') as file:
                file.write(exe_path)
            print(f"路径已成功保存到 {txt_path}")
        except Exception as e:
            print(f"保存路径时出错: {e}")
def 从文件提取路径():

    # 获取当前脚本或可执行文件的目录
    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
    txt_path = os.path.join(current_dir, 'app_path.txt')

    # 打开文件并读取
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            path = file.read().strip()  # 读取文件内容并移除多余的换行符
            print(f"从文件中读取到的路径是：{path}")
            return path
    except Exception as e:
        print(f"读取文件时发生错误：{e}")
        return None

def 关闭电脑应用(hwnd):
    """
    根据窗口句柄关闭对应的应用
    """
    try:
        # 获取窗口所属的进程 ID
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        # 强制关闭进程
        PROCESS_TERMINATE = 1
        handle = kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
        if handle:
            kernel32.TerminateProcess(handle, 0)
            kernel32.CloseHandle(handle)
            print(f"已关闭窗口句柄为 {hwnd} 的应用")
        else:
            print(f"无法打开进程句柄，PID: {pid}")
    except Exception as e:
        print(f"关闭应用时发生错误: {e}")


