import ast
import ctypes
import time
import win32process
import win32gui
import subprocess
import json
from pathlib import Path
import sys
from project_paths import APP_ROOT
psapi = ctypes.windll.psapi
import os
import tkinter.messagebox as msgbox
import tkinter as tk
import ctypes
from ctypes import wintypes
import logging
#from typing import List, Set
# 定义 EnumWindows 的回调函数类型
EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
import threading
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
WM_CLOSE = 0x0010

logger = logging.getLogger("database")
from datetime import datetime, timedelta
from 后台点击再次封装 import pc端单击键盘, pc端单击键盘无线程事件





def get_seconds_to_target_time(parameter):
    """
    计算当前时间到指定时间点的秒数。

    参数:
    - parameter: 字符串类型的参数，格式为 "HH:MM"，例如 "15:36"。

    返回:
    - 返回从当前时间到指定时间点的秒数（始终为非负值）。
    """
    # 解析当前时间
    current_time = datetime.now()

    # 解析输入的小时和分钟
    try:
        target_hour, target_minute = map(int, parameter.split(':'))
    except ValueError:
        # 如果参数格式不正确，返回 None
        return None

    # 构建目标时间（不包含日期，只包含时间部分）
    today = datetime.today()
    target_time = today.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

    # 如果当前时间晚于目标时间，则将目标时间设置为明天的时间
    if current_time >= target_time:
        target_time += timedelta(days=1)

    # 计算当前时间到目标时间的秒数
    time_difference = target_time - current_time
    return int(time_difference.total_seconds())


def 精确查找所有窗口句柄(目标窗口类名=None, 目标窗口标题=None):
    """
    查找所有匹配指定类名和/或标题的窗口句柄

    参数:
        目标窗口类名: 窗口类名，可以为 None（匹配所有类名）
        目标窗口标题: 窗口标题，可以为 None（匹配所有标题）

    返回:
        匹配的窗口句柄列表
    """
    # 设置DPI感知
    ctypes.windll.shcore.SetProcessDpiAwareness(2)

    匹配窗口列表 = []

    def 枚举窗口回调(句柄, 参数):
        # 获取窗口类名
        窗口类名 = win32gui.GetClassName(句柄)

        # 获取窗口标题
        窗口标题 = win32gui.GetWindowText(句柄)

        # 检查是否匹配
        类名匹配 = (目标窗口类名 is None or 窗口类名 == 目标窗口类名)
        标题匹配 = (目标窗口标题 is None or 窗口标题 == 目标窗口标题)

        if 类名匹配 and 标题匹配:
            矩形 = _update_window_rect(句柄)
            匹配窗口列表.append((句柄,矩形))

        # 返回 True 继续枚举
        return True

    # 枚举所有顶层窗口
    win32gui.EnumWindows(枚举窗口回调, None)

    return 匹配窗口列表
def 断开所有adb设备连接(adb路径):
    try:
        # 执行 adb disconnect 命令
        结果 = subprocess.run([adb路径, "disconnect"], capture_output=True, text=True, shell=True)

        # 检查命令是否成功执行
        if "successfully disconnected" in 结果.stdout or "no devices/emulators found" in 结果.stdout:
            logger.debug("所有 ADB 设备已断开连接")
        else:
            logger.debug("断开连接失败")
            logger.debug(结果.stdout)
            logger.debug(结果.stderr)
    except Exception as e:
        logger.debug(f"断开连接时发生错误: {e}")


def 关闭电脑应用exe_path(hwnd):
     result = user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
     if result:
         logger.debug(f"已向窗口发送关闭消息: {hwnd}")
         return True
     else:
         logger.debug(f"发送关闭消息失败: {hwnd}")
         return False

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
            logger.debug(f"已关闭窗口句柄为 {hwnd} 的应用")
        else:
            logger.debug(f"无法打开进程句柄，PID: {pid}")
    except Exception as e:
        logger.debug(f"关闭应用时发生错误: {e}")


def 打开电脑应用(exe_path):
    """
    根据可执行文件路径打开应用
    """
    try:
        if os.path.exists(exe_path):
            # 使用 subprocess 启动应用
            print("尝试不使用管理员权限")
            import tempfile

            def run_via_task(app_path):
                # 创建临时任务XML文件
                xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
            <Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
              <Principals>
                <Principal id="Author">
                  <RunLevel>LeastPrivilege</RunLevel>
                </Principal>
              </Principals>
              <Actions Context="Author">
                <Exec>
                  <Command>{app_path}</Command>
                </Exec>
              </Actions>
            </Task>'''

                # 保存为临时文件
                with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-16') as f:
                    f.write(xml_content)
                    xml_file = f.name

                try:
                    # 创建并运行一次性任务
                    task_name = f"TempTask_{os.getpid()}"
                    subprocess.run([
                        'schtasks', '/create', '/tn', task_name,
                        '/xml', xml_file, '/f'
                    ], shell=True, capture_output=True)

                    subprocess.run([
                        'schtasks', '/run', '/tn', task_name
                    ], shell=True, capture_output=True)

                    # 删除任务
                    subprocess.run([
                        'schtasks', '/delete', '/tn', task_name, '/f'
                    ], shell=True, capture_output=True)
                finally:
                    os.unlink(xml_file)

            run_via_task(exe_path)
            #subprocess.Popen([exe_path])
            logger.debug(f"已打开应用: {exe_path}")
        else:
            logger.debug(f"应用路径不存在: {exe_path}")
    except Exception as e:
        logger.debug(f"打开应用时发生错误: {e}")

def 弹出错误提示框(模拟器窗口句柄列表,模拟器标题变量):
    if not 模拟器窗口句柄列表:
        错误消息 = f"未找到标题包含{模拟器标题变量}的窗口！,你可能要自定义修改脚本查找的标题,该功能用于获取exe路径从而启动定时任务，可无视该提醒"
    else:
        # 动态生成包含所有窗口标题的错误消息
        错误消息 = f"找到多个标题包含{模拟器标题变量}的窗口：\n"

        for hwnd in 模拟器窗口句柄列表:
            title = win32gui.GetWindowText(hwnd)
            错误消息 += f"标题: {title}\n"


    # 使用 ctypes 调用 Windows API 弹出消息框
    MessageBox = ctypes.windll.user32.MessageBoxW
    MessageBox(None, f"你需要自定义修改脚本查找的标题,该功能用于获取exe路径从而启动定时任务，可无视该提醒\n{错误消息}", "发生了一个可忽略的错误", 0x10 | 0x0)

def 获取模拟器应用路径(hwnd):
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
        logger.debug("应用路径获取成功")
        return exe_name.value if exe_name.value else None
    except Exception as e:
        logger.debug(f"获取应用路径时发生错误: {e}")
        return None

def 获取模拟器应用目录(hwnd):
    try:
        # 调用获取应用路径的函数
        exe_path = 获取模拟器应用路径(hwnd)

        if exe_path:
            # 提取目录部分
            return exe_path[:exe_path.rfind("\\") + 1]
        else:
            return None
    except Exception as e:
        logger.debug(f"获取应用目录时发生错误: {e}")
        return None




def 中途连接模拟器():
    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent.absolute()
    else:
        current_dir = APP_ROOT
    游戏列表 = ["异环", "幻塔"]
    for 游戏 in 游戏列表:
        target_path = current_dir / f"{游戏}图片"
        if target_path.exists() and target_path.is_dir():  # 判断文件是否存在
            if 游戏 == "异环":
                return
    ds_path = current_dir / 'game.json'
    if not ds_path.exists():
        current_dir = current_dir.parent.parent.parent  # 三级回溯
        ds_path = current_dir / 'game.json'
    app_path = current_dir / "platform-tools" / "adb.exe"
    with open(os.path.join(current_dir, 'Tool_Settings.json'), 'r', encoding='utf-8') as file:
        Tool_Settings = json.load(file)
    端口号 = Tool_Settings["端口号变量"]
    # 构建连接到MuMu模拟器的命令

    command = [app_path, 'connect', 端口号]
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    if result.stdout is not None and 'connected' in result.stdout:
        logger.debug("成功连接到模拟器")
    else:
        logger.debug("连接失败:未知错误")





def 从文件提取路径():
    import os
    import sys
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
            logger.debug(f"从文件中读取到的路径是：{path}")
            return path
    except Exception as e:
        logger.info(f"读取文件时发生错误：{e}")
        return None

def 预先连接mumu模拟器2():
    # 获取adb路径
    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent.absolute()
    else:
        current_dir = APP_ROOT
    游戏列表 = ["异环", "幻塔"]
    for 游戏 in 游戏列表:
        target_path = current_dir / f"{游戏}图片"
        if target_path.exists() and target_path.is_dir():  # 判断文件是否存在
            if 游戏 == "异环":
                return

    app_path = current_dir / "platform-tools" / "adb.exe"
    def 连接模拟器端口(adb_path, 端口):
        """连接单个端口的函数"""
        command = [adb_path, 'connect', 端口]
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        if result.stdout and 'connected' in result.stdout:
            logger.debug(f"成功连接到模拟器端口: {端口}")
            return True
        else:
            if getattr(sys, 'frozen', False):
                pass
            else:
                #logger.debug(f"连接失败端口: {端口}")
                pass
            return False
    端口列表=[ '127.0.0.1:5554', '127.0.0.1:5555', '127.0.0.1:21503', '127.0.0.1:5556', '127.0.0.1:5558',
              '127.0.0.1:5560', '127.0.0.1:5557', '127.0.0.1:5559', '127.0.0.1:5561', '127.0.0.1:62001', '127.0.0.1:59865',
              '127.0.0.1:7555', '127.0.0.1:16384', '127.0.0.1:5545', '127.0.0.1:16385', '127.0.0.1:5546', '127.0.0.1:16416',
              '127.0.0.1:16417', '127.0.0.1:16448', '127.0.0.1:5565', '127.0.0.1:16449', '127.0.0.1:5566', '127.0.0.1:16480',
              '127.0.0.1:5575', '127.0.0.1:16481', '127.0.0.1:5576', '127.0.0.1:16512', '127.0.0.1:5585', '127.0.0.1:16513',
              '127.0.0.1:5586', '127.0.0.1:16544', '127.0.0.1:5595', '127.0.0.1:16545', '127.0.0.1:5596', '127.0.0.1:16576',
              '127.0.0.1:5605', '127.0.0.1:16577', '127.0.0.1:5606', '127.0.0.1:16608', '127.0.0.1:5615', '127.0.0.1:16609',
              '127.0.0.1:5616', '127.0.0.1:16640', '127.0.0.1:5625', '127.0.0.1:16641', '127.0.0.1:5626', '127.0.0.1:16672',
              '127.0.0.1:5635', '127.0.0.1:16673', '127.0.0.1:5636']

    def 使用线程():

        for 端口 in 端口列表:
            threading.Thread(target=连接模拟器端口,
                             args=(app_path, 端口)).start()
            time.sleep(0.1)

        logger.debug("所有连接启动完成")
    # 选择一种方案执行
    使用线程()  # 或 使用线程()
def 预先连接mumu模拟器():
    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent.absolute()
    else:
        current_dir = APP_ROOT
    游戏列表 = ["异环", "幻塔"]
    for 游戏 in 游戏列表:
        target_path = current_dir / f"{游戏}图片"
        if target_path.exists() and target_path.is_dir():  # 判断文件是否存在
            if 游戏 == "异环":
                return
    app_path = current_dir / "platform-tools" / "adb.exe"
    with open(os.path.join(current_dir, 'Tool_Settings.json'), 'r', encoding='utf-8') as file:
        Tool_Settings = json.load(file)
    端口号 = Tool_Settings["端口号变量"]
    # 构建连接到MuMu模拟器的命令
    command = [app_path, 'connect', 端口号]
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    if result.stdout is not None and 'connected' in result.stdout:
        logger.debug("成功连接到模拟器")
    else:
        logger.debug(f"连接失败，未知错误")
    command = [app_path, 'connect', f"127.0.0.1:16384"]
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    if result.stdout is not None and 'connected' in result.stdout:
        logger.debug("成功连接到模拟器")
        成功 = True
        return 成功
    command = [app_path, 'connect', f"127.0.0.1:7555"]
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    if result.stdout is not None and 'connected' in result.stdout:
        logger.debug("成功连接到模拟器")
        成功 = True
        return 成功
    command = [app_path, 'connect', f"127.0.0.1:5555"]
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    if result.stdout is not None and 'connected' in result.stdout:
        logger.debug("成功连接到模拟器")
        成功 = True
        return 成功
def 连接模拟器判断(i):
    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent.absolute()
    else:
        current_dir = APP_ROOT
    游戏列表 = ["异环", "幻塔"]
    for 游戏 in 游戏列表:
        target_path = current_dir / f"{游戏}图片"
        if target_path.exists() and target_path.is_dir():  # 判断文件是否存在
            if 游戏 == "异环":
                return
    成功 = False
    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent.absolute()
    else:
        current_dir = APP_ROOT
    app_path = current_dir / "platform-tools" / "adb.exe"
    端口序列 = 5545
    command = [app_path, 'connect', f"127.0.0.1:{端口序列 +i*10}"]
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    if result.stdout is not None and 'connected' in result.stdout:
        logger.debug("成功连接到模拟器")
        成功 = True
    command = [app_path, 'connect', f"127.0.0.1:{端口序列 +1+ i * 10}"]
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    if result.stdout is not None and 'connected' in result.stdout:
        logger.debug("成功连接到模拟器")
        成功 = True
    if i == 0:
        command = [app_path, 'connect', f"127.0.0.1:7555"]
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        if result.stdout is not None and 'connected' in result.stdout:
            logger.debug("成功连接到模拟器")
            成功 = True
        command = [app_path, 'connect', f"127.0.0.1:16384"]
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        if result.stdout is not None and 'connected' in result.stdout:
            logger.debug("成功连接到模拟器")
            成功 = True
        端口号列表 = [5554,5555,21503,5556, 5558, 5560,5557, 5559, 5561, 62001, 59865]
        for 端口 in 端口号列表:
            command = [app_path, 'connect', f"127.0.0.1:{端口}"]
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
            if result.stdout is not None and 'connected' in result.stdout:
                logger.debug("成功连接到模拟器")
                成功 = True
    端口序列=16384
    command = [app_path, 'connect', f"127.0.0.1:{端口序列 + 32 * i}"]
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    if result.stdout is not None and 'connected' in result.stdout:
        logger.debug("成功连接到模拟器")
        成功=True
    command = [app_path, 'connect', f"127.0.0.1:{端口序列 +1+ 32 * i}"]
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    if result.stdout is not None and 'connected' in result.stdout:
        logger.debug("成功连接到模拟器")
        成功 = True

    return 成功


def 函数精确查找窗口句柄(目标窗口类名, 默认目标窗口标题):

    ctypes.windll.shcore.SetProcessDpiAwareness(2) # 系统级DPI感知
    """精确查找目标窗口句柄"""
    # 先尝试根据标题和类名查找窗口
    游戏句柄 = win32gui.FindWindow(目标窗口类名, 默认目标窗口标题)
    if 游戏句柄:
        窗口矩形 = _update_window_rect(游戏句柄)
        print(f"找到目标窗口：句柄={游戏句柄}, 矩形={窗口矩形}")
        return 游戏句柄, 窗口矩形
    return None, None  # 没有找到窗口时返回 None
def 函数模糊查找窗口句柄(目标窗口标题):
    result = []

    def callback(hwnd, _):
        current_title = win32gui.GetWindowText(hwnd)
        if 目标窗口标题.lower() in current_title.lower():  # 不区分大小写的模糊匹配
            窗口矩形 = _update_window_rect(hwnd)
            # 保存句柄、矩形和完整标题用于错误提示
            result.append((hwnd, 窗口矩形, current_title))
        return True  # 继续枚举所有窗口

    win32gui.EnumWindows(callback, None)

    if not result:
        root = tk.Tk()
        root.withdraw()
        msgbox.showerror("未找到", f"用户截图方式选择了窗口截图，但未找到包含'{目标窗口标题}'的窗口！\n\n"
                                   f"可以尝试在脚本界面根据模拟器设置的窗口模拟器标题")
        root.destroy()
        logger.debug(f"未找到包含'{目标窗口标题}'的窗口！")
        return None, None
    elif len(result) == 1:
        return result[0][0], result[0][1]  # 返回句柄和矩形
    else:
        # 构建错误信息
        error_msg = f"找到{len(result)}个匹配窗口（目标标题：'{目标窗口标题}'）:\n\n"
        for idx, (hwnd, _, title) in enumerate(result, 1):
            error_msg += f"{idx}. 句柄: {hwnd}, 完整标题: '{title}'\n"

        # 初始化Tk并隐藏主窗口
        root = tk.Tk()
        root.withdraw()
        msgbox.showerror("发现多个匹配窗口", f"用户截图方式选择了窗口截图，但发现多个匹配窗口\n\n"
                                             f"可以尝试在脚本界面设置更详细的窗口模拟器标题\n\n{error_msg}")
        root.destroy()
        return None, None


def move_window(窗口句柄, x, y):
    """移动窗口到指定坐标"""
    # 先获取当前窗口大小
    left, top, right, bottom = win32gui.GetWindowRect(窗口句柄)
    width = right - left
    height = bottom - top

    # 移动窗口到新位置，保持原大小
    win32gui.MoveWindow(窗口句柄, x, y, width, height, True)
def GetWindowRec_rect(游戏句柄):
    """获取整个窗口矩形（包括标题栏、边框等）"""
    # 获取整个窗口的矩形
    整个窗口矩形 = win32gui.GetWindowRect(游戏句柄)
    return 整个窗口矩形
import win32con
def _update_window_rect(游戏句柄):
    """窗口矩形逻辑"""
    for i in range(6):
        client_rect = win32gui.GetClientRect(游戏句柄)
        left, top = win32gui.ClientToScreen(游戏句柄, (client_rect[0], client_rect[1]))
        right, bottom = win32gui.ClientToScreen(游戏句柄, (client_rect[2], client_rect[3]))
        窗口矩形 = (left, top, right, bottom)
        if right - left < 10:
            pc端单击键盘无线程事件(游戏句柄, 0.001, ["w"], 1)
        else:
            break
        time.sleep(1)
    else:
        窗口矩形 = None
    return 窗口矩形

def 循环移动窗口(hwnd):
    for i in range(6):
        # 使用 SetWindowPos，不改变大小，只改变位置
        # 参数：hwnd, hWndInsertAfter, x, y, cx, cy, uFlags
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, -720*i, 0, 0,
                            win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
        time.sleep(1)


def monitor_and_restore_window_position(线程事件):
    """
    监控窗口位置并在客户区变化时恢复窗口位置
    """
    print("未找到目标窗口，无法监控")
    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent.absolute()
    else:
        current_dir = APP_ROOT
    with open(os.path.join(current_dir, 'Tool_Settings.json'), 'r', encoding='utf-8') as file:
        Tool_Settings = json.load(file)
    客户端选择 = int(Tool_Settings["客户端选择变量"])
    if 客户端选择 == 2:
        print("用户选择的客户端是模拟器，不用监控")
        return
    hwnd = None
    窗口矩形 = None
    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent.absolute()
    else:
        current_dir = APP_ROOT
    with open(os.path.join(current_dir, 'Tool_Settings.json'), 'r', encoding='utf-8') as file:
        Tool_Settings = json.load(file)
    端口号 = Tool_Settings["端口号变量"]
    路径 = current_dir / "game.json"
    with open(路径, 'r', encoding='utf-8') as file:
        data = json.load(file)
    端游列表 = data["端游列表"]
    for 端游 in 端游列表:
        窗口列表 = 精确查找所有窗口句柄(端游[0], 端游[1], )
        if 窗口列表:
            for 元组 in 窗口列表:
                hwnd,窗口矩形=元组

                if str(hwnd) == str(端口号):
                    logger.debug(f"游戏句柄是：{hwnd}")
                    logger.debug(f"窗口矩形是：{窗口矩形}")
                    break
            else:
                hwnd = None

        if hwnd:
            break
    else:
        return

    try:

        # 获取整个窗口矩形
        try:
            整个窗口矩形 = GetWindowRec_rect(hwnd)
            print(f"初始整个窗口矩形: {整个窗口矩形}")
            print(f"初始客户区窗口矩形: {窗口矩形}")

            # 记录初始客户区位置
            初始客户区位置 = (窗口矩形[0], 窗口矩形[1])
        except Exception as e:
            print(f"获取窗口矩形时发生错误: {e}")
            return

        # 延时5秒的循环检查
        print("开始监控...")
        while 线程事件.is_set():
            try:
                # 检查窗口是否仍然存在
                if not IsWindow(hwnd):
                    print("目标窗口已关闭，停止监控")
                    break

                # 获取当前客户区矩形
                当前客户区矩形 = _update_window_rect(hwnd)
                if not 当前客户区矩形:
                    print("无法获取客户区矩形，窗口可能已关闭")
                    break

                当前客户区位置 = (当前客户区矩形[0], 当前客户区矩形[1])

                # 检查客户区位置是否变化
                if 当前客户区位置 != 初始客户区位置:
                    print(f"检测到客户区位置变化: {初始客户区位置} -> {当前客户区位置}")

                    # 移动窗口回原始位置
                    print(f"移动窗口到原始位置: ({整个窗口矩形[0]}, {整个窗口矩形[1]})")

                    # 检查窗口是否仍然存在
                    if not IsWindow(hwnd):
                        print("窗口在移动前被关闭")
                        break

                    success = move_window(hwnd, 整个窗口矩形[0], 整个窗口矩形[1])
                    if not success:
                        print("移动窗口失败")
                        continue

                    # 短暂延时让窗口移动完成
                    time.sleep(0.1)

                    # 检查窗口是否仍然存在
                    if not IsWindow(hwnd):
                        print("窗口在移动后被关闭")
                        break

                    # 检查是否归位
                    移动后客户区矩形 = _update_window_rect(hwnd)
                    if not 移动后客户区矩形:
                        print("无法获取移动后的客户区矩形")
                        continue

                    移动后客户区位置 = (移动后客户区矩形[0], 移动后客户区矩形[1])

                    if 移动后客户区位置 != 初始客户区位置:
                        print(f"错误: 窗口移动后客户区未归位!")
                        print(f"期望位置: {初始客户区位置}")
                        print(f"实际位置: {移动后客户区位置}")
                    else:
                        print("窗口已成功归位")

                time.sleep(5)  # 每5秒检查一次

            except Exception as e:
                print(f"监控过程中发生错误: {e}")
                # 可以选择继续监控或退出
                time.sleep(5)
                continue

    except Exception as e:
        print(f"监控函数发生未预期错误: {e}")
    finally:
        print("窗口位置监控结束")
def IsWindow(hwnd):
    """
    检查窗口句柄是否仍然有效
    如果您的环境中有可用的Win32 API，可以使用win32gui.IsWindow
    否则需要根据您的环境实现此函数
    """
    try:
        # 假设您有访问Win32 API的方式
        import win32gui
        return win32gui.IsWindow(hwnd)
    except ImportError:
        # 如果没有win32gui，可以使用其他方法检查窗口是否存在
        try:
            # 尝试获取窗口标题，如果失败则窗口不存在
            title = win32gui.GetWindowText(hwnd)
            return True
        except:
            return False
    except Exception:
        return False
def 函数查找子窗口句柄(父窗口句柄, 目标子窗口类名, 目标子窗口标题):
    """精确查找目标子窗口句柄"""
    # 先尝试根据标题和类名直接查找子窗口
    子句柄 = win32gui.FindWindowEx(父窗口句柄, None, 目标子窗口类名, 目标子窗口标题)
    if 子句柄:
        return 子句柄
    else:
        return None
def 查找符合条件的顶级窗口(目标窗口类名=None, 目标窗口标题=None):
    """
    查找所有符合条件的顶级窗口

    参数:
        目标窗口类名: 要匹配的窗口类名（字符串或列表）
        目标窗口标题: 要匹配的窗口标题（字符串或列表）
        包含匹配: True表示包含匹配，False表示精确匹配

    返回:
        符合条件的窗口句柄列表
    """
    符合条件的窗口 = []

    def 回调函数(窗口句柄, 参数):
        # 检查窗口是否可见（可选，可根据需要调整）
        if not win32gui.IsWindowVisible(窗口句柄):
            return True

        子句柄=函数查找子窗口句柄(窗口句柄, 目标窗口类名, 目标窗口标题)
        if 子句柄:
            符合条件的窗口.append(窗口句柄)
            窗口类名 = win32gui.GetClassName(窗口句柄)
            窗口标题 = win32gui.GetWindowText(窗口句柄)
            print(f"{窗口类名}，{窗口标题}")

        return True

    # 枚举所有顶级窗口
    win32gui.EnumWindows(回调函数, None)

    return 符合条件的窗口
def 函数精确查找子窗口句柄(父窗口句柄, 目标子窗口类名, 默认子窗口标题):
    """精确查找目标子窗口句柄"""
    # 先尝试根据标题和类名直接查找子窗口
    子句柄 = win32gui.FindWindowEx(父窗口句柄, None, 目标子窗口类名, 默认子窗口标题)
    if 子句柄:
        子窗口矩形 = _update_window_rect(子句柄)
        logger.debug(f"找到目标子窗口：句柄={子句柄}, 矩形={子窗口矩形}")
        return 子句柄, 子窗口矩形

    # 如果未找到，再尝试仅根据类名查找子窗口
    result = []

    def callback(hwnd, _):
        if win32gui.GetClassName(hwnd) == 目标子窗口类名:
            子窗口矩形 = _update_window_rect(hwnd)
            logger.debug(f"找到目标子窗口：句柄={hwnd}, 矩形={子窗口矩形}")
            result.append((hwnd, 子窗口矩形))
            return False  # 停止枚举

    win32gui.EnumChildWindows(父窗口句柄, callback, None)
    if result:
        子句柄, 子窗口矩形 = result[0]
        return 子句柄, 子窗口矩形
    else:
        logger.debug("未找到目标子窗口！")
        return None, None  # 没有找到子窗口时返回 None





def 根据窗口句柄获取窗口类名和标题(窗口句柄):
    """
    根据窗口句柄获取窗口类名和标题

    参数：
        窗口句柄 (int) - 目标窗口的句柄

    返回值：
        tuple: (类名, 窗口标题) 如果成功
        None: 如果句柄无效或获取失败
    """
    try:
        # 获取窗口类名
        类名 = win32gui.GetClassName(窗口句柄)

        # 获取窗口标题
        标题 = win32gui.GetWindowText(窗口句柄)

        return (类名, 标题)
    except Exception as e:
        logger.debug(f"获取窗口信息失败，错误：{str(e)}")
        类名=None
        标题 = None
        return (类名, 标题)
def resize_window(hwnd, x, y, width, height):
    win32gui.MoveWindow(hwnd, x, y, width, height, True)
def 调整窗口尺寸(窗口句柄,线程事件任务循环,类名="Qt5156QWindowIcon",标题="MuMuPlayer"):
    for o in range(3):
        if not 线程事件任务循环.is_set():
            return None# 如果事件对象被清除，退出循环
        宽 = 1280
        高 = 740
        条件2成立 = 0
        条件1成立 = 0
        for i in range(500):
            if not 线程事件任务循环.is_set():
                return None # 如果事件对象被清除，退出循环
            if 宽 > 1800:
                宽 = 1800
            if 高 > 1000:
                高 = 1000

            游戏句柄, 窗口矩形 = 函数精确查找子窗口句柄(窗口句柄, 类名, 标题)
            if  窗口矩形[2] - 窗口矩形[0]<窗口矩形[3] - 窗口矩形[1]:
                if getattr(sys, 'frozen', False):
                    current_dir = Path(sys.executable).parent.absolute()
                else:
                    current_dir = APP_ROOT
                with open(os.path.join(current_dir, 'Tool_Settings.json'), 'r', encoding='utf-8') as file:
                    Tool_Settings = json.load(file)
                端口号 = Tool_Settings["端口号变量"]
                adb程序 = current_dir / "platform-tools" / "adb.exe"
                if "MuMu" in 端口号:
                    端口元组 = ast.literal_eval(端口号)
                    多开号 = 端口元组[1]
                    端口号=f"127.0.0.1:{16384+int(多开号)*32}"
                    command = [adb程序, 'connect', f"{端口号}"]
                    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
                    if result.stdout is not None and 'connected' in result.stdout:
                        logger.debug("成功连接到模拟器")
                    else:
                        logger.debug("连接失败:未知错误")
                        端口号 = f"127.0.0.1:{16385 + int(多开号) * 32}"
                        command = [adb程序, 'connect', f"{端口号}"]
                        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
                        if result.stdout is not None and 'connected' in result.stdout:
                            logger.debug("成功连接到模拟器")
                        else:
                            logger.debug("连接失败:未知错误")
                    logger.info(端口号)
                elif "雷电" in 端口号:
                    端口元组 = ast.literal_eval(端口号)
                    多开号 = 端口元组[1]
                    端口号=f"emulator-{5554+2*(int(多开号))}"




                连接adb关闭应用(adb程序, 包名="com.bilibili.heaven", 端口=端口号)
                time.sleep(3)
                连接adb启动应用(adb程序,  包名="com.bilibili.heaven", 端口=端口号)
            # logger.debug(窗口矩形)

            if 窗口矩形[2] - 窗口矩形[0] < 1280:
                条件1成立 = 0
                宽 = 宽 + 1
            elif 窗口矩形[2] - 窗口矩形[0] > 1280:
                条件1成立 = 0
                宽 = 宽 - 1
            if 窗口矩形[2] - 窗口矩形[0] < 1290 and 窗口矩形[2] - 窗口矩形[0] > 1270:
                条件1成立 = 1
            if 窗口矩形[3] - 窗口矩形[1] < 720:
                条件2成立 = 0
                高 = 高 + 1
            elif 窗口矩形[3] - 窗口矩形[1] > 720:
                条件2成立 = 0
                高 = 高 - 1

            if 窗口矩形[3] - 窗口矩形[1] < 730 and 窗口矩形[3] - 窗口矩形[1] > 710:
                条件2成立 = 1

            if 条件1成立 == 1 and 条件2成立 == 1:
                logger.info(f"{宽}，{o}，{i}，{高}")
                logger.info("条件成立")
                logger.info(f"{窗口矩形[2] - 窗口矩形[0]}，{o}，{i}，{窗口矩形[3] - 窗口矩形[1]}")
                return 游戏句柄
            else:
                logger.debug(f"{宽}，{o}，{i}，{高}")
                logger.debug("条件不成立")
                logger.debug(f"{窗口矩形[2] - 窗口矩形[0]}{o}{i}{窗口矩形[3] - 窗口矩形[1]}")
                resize_window(窗口句柄, 200, 100, 宽, 高)
        time.sleep(2)

    root = tk.Tk()
    root.withdraw()
    msgbox.showerror("调整窗口错误", f"标题为：{标题}，类名为：{类名}的窗口反复调整还是无法达到1280*720的要求分辨率\n\n"
                                     f"可能你将模拟器窗口最小化或者最大化了\n\n"
                                   f"可将整个过程再次运行录屏，提供录屏给作者\n\n"
                                   f"注：脚本输出信息和游戏画面都要录进去")
    return None
def 连接adb启动应用(adb_config, 包名,端口):
    """通过包名启动应用"""
    try:
        adb命令 = f'"{adb_config}" -s {端口} shell monkey -p {包名} -c android.intent.category.LAUNCHER 1'
        subprocess.run(adb命令, shell=True)
        logger.debug(f"启动游戏{包名}")
        time.sleep(3)
    except Exception as e:
        logger.error(f"启动应用失败: {str(e)}")
def 连接adb关闭应用(adb_config, 包名,端口):
    """强制停止应用"""
    try:
        命令 = f"am force-stop {包名}"

        adb命令 = f'"{adb_config}" -s {端口} shell {命令}'
        subprocess.run(adb命令, shell=True)
        logger.info(f"关闭游戏{包名}")
    except Exception as e:
        logger.error(f"关闭应用失败: {str(e)}")
def 获取模拟器客户区句柄(窗口句柄,线程事件任务循环):
    系统DPI = 1.0

    if 系统DPI == 1.0:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # 系统级DPI感知
        # 定义获取系统 DPI 的函数


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
    pc端单击键盘(窗口句柄, 0.001, ["w"], 1, 线程事件任务循环)
    类名, 标题=根据窗口句柄获取窗口类名和标题(窗口句柄)
    if "MuMu" in str(标题) or "Qt5156QWindowIcon" in str(类名):
        客户区句柄=调整窗口尺寸(窗口句柄,线程事件任务循环,类名="Qt5156QWindowIcon",标题="MuMuPlayer")
    elif "雷电" in str(标题) or "LDPlayerMainFrame" in str(类名):
        客户区句柄 = 调整窗口尺寸(窗口句柄,线程事件任务循环, 类名="RenderWindow", 标题="TheRender")
    else:
        root = tk.Tk()
        root.withdraw()
        msgbox.showerror("窗口不支持", f"标题为：{标题}，类名为：{类名}的窗口不支持窗口截图模式\n\n"
                                             f"只支持模拟器：MuMu模拟器，雷电模拟器\n\n"
                                       f"如果希望我添加模拟器，可以告诉我哪个模拟器")

        root.destroy()
        客户区句柄=None
    return 客户区句柄


import win32gui
import win32process
import win32api


def get_window_handles_by_path_no_psutil(app_path, window_title="HeavenBurnsRed", window_class="UnityWndClass"):
    """
    不使用psutil，仅通过pywin32获取窗口句柄
    添加窗口标题和类名参数进行筛选，只返回一个匹配的句柄

    Args:
        app_path: 应用程序路径
        window_title: 窗口标题（可选，支持部分匹配）
        window_class: 窗口类名（可选）

    Returns:
        匹配的窗口句柄，如果没有找到则返回None
    """
    if not os.path.isabs(app_path):
        app_path = os.path.abspath(app_path)

    window_handles = []
    norm_app_path = os.path.normcase(os.path.abspath(app_path))

    def enum_windows_callback(hwnd, handles):
        try:
            # 获取窗口进程ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            # 获取进程句柄
            process_handle = win32api.OpenProcess(
                0x0410,  # PROCESS_QUERY_INFORMATION | PROCESS_VM_READ
                False,
                pid
            )

            if process_handle:
                # 获取可执行文件路径
                exe_path = win32process.GetModuleFileNameEx(process_handle, 0)
                win32api.CloseHandle(process_handle)

                if exe_path:
                    norm_exe_path = os.path.normcase(os.path.abspath(exe_path))
                    if norm_app_path == norm_exe_path:
                        if win32gui.IsWindowVisible(hwnd):
                            handles.append(hwnd)
        except:
            pass
        return True

    # 首先找到所有匹配路径的可见窗口句柄
    win32gui.EnumWindows(enum_windows_callback, window_handles)

    # 如果没有找到任何句柄，直接返回None
    if not window_handles:
        return None

    # 如果有标题或类名参数，进行进一步筛选
    if window_title is not None or window_class is not None:
        filtered_handles = []

        for hwnd in window_handles:
            match = True

            # 检查窗口标题
            if window_title is not None:
                try:
                    actual_title = win32gui.GetWindowText(hwnd)
                    # 支持部分匹配（判断window_title是否在actual_title中）
                    if window_title not in actual_title:
                        match = False
                except:
                    match = False

            # 检查窗口类名（如果标题已匹配且需要检查类名）
            if match and window_class is not None:
                try:
                    actual_class = win32gui.GetClassName(hwnd)
                    if window_class != actual_class:
                        match = False
                except:
                    match = False

            if match:
                filtered_handles.append(hwnd)

        # 更新句柄列表为筛选后的结果
        window_handles = filtered_handles

    # 只返回一个句柄（如果有多个匹配，返回第一个）
    return window_handles[0] if window_handles else None
if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent.absolute()
    else:
        current_dir = APP_ROOT
    with open(os.path.join(current_dir, 'Tool_Settings.json'), 'r', encoding='utf-8') as file:
        Tool_Settings = json.load(file)
    端口号 = Tool_Settings["端口号变量"]
    路径 = current_dir / "game.json"
    with open(路径, 'r', encoding='utf-8') as file:
        data = json.load(file)
    端游列表 = data["端游列表"]

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
                hwnd = None

        if hwnd:
            break
    else:
        move_window(hwnd, 0, 0)
