import time

import win32gui
import win32con
import ctypes
from ctypes import wintypes
import win32process

import subprocess
from pathlib import Path

import os
import sys
from project_paths import APP_ROOT
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi

# 定义 EnumWindows 的回调函数类型
EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
WM_ACTIVATE = win32con.WM_ACTIVATE
WA_ACTIVE = 1

import win32process
from pycaw.pycaw import AudioUtilities

def 窗口静音(hwnd: int, mute: bool) -> bool:
    """
       根据窗口句柄设置静音或解除静音（自动处理 COM 初始化）

       :param hwnd: 窗口句柄（整数）
       :param mute: True = 静音, False = 解除静音
       :return: 操作成功返回 True，未找到对应会话则返回 False
       """

    try:
        # 初始化当前线程的 COM 库（如果尚未初始化）
        ctypes.windll.ole32.CoInitialize(None)

        # 获取窗口所属进程的 PID
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid == 0:
            return False

        # 获取所有音频会话
        sessions = AudioUtilities.GetAllSessions()

        for session in sessions:
            if session.Process and session.Process.pid == pid:
                volume = session.SimpleAudioVolume
                volume.SetMute(mute, None)  # 第二个参数为事件上下文 GUID
                return True

        return False  # 未找到匹配的音频会话
    except Exception as e:
        print(f"操作失败: {e}")
        return False
    # 注意：不在此处调用 CoUninitialize，避免影响 pycaw 后续可能的 COM 操作
def 线程持续激活(句柄,线程事件,游戏静音=True):
    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        current_dir = str(APP_ROOT)
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
    if 句柄:
        # 发送激活消息
        win32gui.SendMessage(句柄, WM_ACTIVATE, WA_ACTIVE, 0)

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
        current_dir = APP_ROOT

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
        current_dir = str(APP_ROOT)
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


