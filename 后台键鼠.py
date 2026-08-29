import win32gui
import win32con
import win32api
import time
import threading
from 窗口假激活 import 窗口假激活,has_child_windows,find_child_window,has_parent_window
import math
import pydirectinput
from ctypes import wintypes
import ctypes


from tkinter import Tk

def copy_to_clipboard(text: str) -> None:
    """
    将文本复制到系统剪贴板（使用 tkinter）。
    """
    root = Tk()
    root.withdraw()          # 隐藏主窗口
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()            # 保持剪贴板内容
    root.destroy()
def 后台输入字符(句柄, 文本):

    """向窗口后台逐个发送字符"""
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
            copy_to_clipboard(文本)
            模拟按键按下(句柄, 162)
            time.sleep(0.5)
            模拟按键按下(句柄, 86)
            time.sleep(0.5)

            模拟按键弹起(句柄, 86)
            time.sleep(0.5)
            模拟按键弹起(句柄, 162)

    else:
        for ch in 文本:
            time.sleep(0.1)
            # 发送字符消息（lParam 可以按标准填写，简单用 0 也可以）
            win32gui.PostMessage(句柄, win32con.WM_CHAR, ord(ch), 0)
            time.sleep(0.01)  # 适当延时，避免丢失

def 游戏_窗口置顶(hwnd: int, topmost: bool) -> bool:
    """
    置顶或取消置顶窗口。
    返回 True 表示成功，False 表示失败。
    """
    flags = win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
    insert_after = win32con.HWND_TOPMOST if topmost else win32con.HWND_NOTOPMOST
    return bool(win32gui.SetWindowPos(hwnd, insert_after, 0, 0, 0, 0, flags))
# 辅助：构造 MAKELONG 和 MAKEWPARAM
def MAKELONG(low, high):
    """将两个16位值合并为一个32位整数"""
    return (low & 0xFFFF) | ((high & 0xFFFF) << 16)

def MAKEWPARAM(low, high):
    """构造 wParam，高16位为 delta，低16位为按键状态"""
    return MAKELONG(low, high)


# 定义必要的常量和结构体
MOUSEEVENTF_WHEEL = 0x0800
WHEEL_DELTA = 120

# 定义 MOUSEINPUT 结构体[reference:12][reference:13]
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
    ]

# 定义 INPUT 结构体[reference:14]
class INPUT(ctypes.Structure):
    class _INPUT_UNION(ctypes.Union):
        _fields_ = [
            ("mi", MOUSEINPUT),
            # 此处省略 ki (键盘) 和 hi (硬件) 结构体
        ]
    _fields_ = [
        ("type", wintypes.DWORD),
        ("u", _INPUT_UNION)
    ]

def scroll_wheel(amount=1):
    """使用 SendInput 模拟鼠标滚轮向下滚动"""
    # 创建并填充 INPUT 结构体
    input_struct = INPUT()
    input_struct.type = 0  # INPUT_MOUSE
    input_struct.u.mi = MOUSEINPUT(
        dx=0,
        dy=0,
        mouseData=WHEEL_DELTA * amount,  # 正值向上，负值向下[reference:15][reference:16]
        dwFlags=MOUSEEVENTF_WHEEL,
        time=0,
        dwExtraInfo=None
    )

    # 发送输入事件
    ctypes.windll.user32.SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(INPUT))



def 模拟鼠标滚轮(句柄, x, y, 滚动量, 长按时间=0, 前台=False,窗口矩形=(0,0,1280,720),硬件命令=False):
    """
    后台或前台模拟鼠标滚轮

    :param 句柄: 目标窗口句柄
    :param x: 客户区坐标 x（相对于窗口左上角）
    :param y: 客户区坐标 y
    :param 滚动量: 正数向上滚，负数向下滚，标准单位 1 对应 120
    :param 长按时间: 用于前台模式时滚轮后的保持时间（后台模式仅保留兼容，无实际效果）
    :param 前台: False 为后台发送消息，True 为前台物理模拟（会激活窗口并移动鼠标）
    """
    硬件命令 = False
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            _ = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
            硬件命令 = True
            前台=True
    try:
        if 前台:
            # 激活目标窗口
            win32gui.SetForegroundWindow(句柄)
            time.sleep(0.05)  # 等待窗口切换完成，可根据需要调整

            # 将客户区坐标转换为屏幕坐标
            screen_x, screen_y = x+窗口矩形[0], y+窗口矩形[1]
            win32api.SetCursorPos((screen_x, screen_y))
            if 硬件命令:
                for _ in range(20):
                    scroll_wheel(滚动量)
                    time.sleep(0.05)
            else:
                # 滚轮事件，dwData 正数向上，WHEEL_DELTA = 120
                win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, 滚动量 * 120, 0)

            if 长按时间 > 0:
                time.sleep(长按时间)
        else:
            # 后台发送 WM_MOUSEWHEEL 消息
            delta = 滚动量 * 120  # WHEEL_DELTA = 120
            wParam = MAKEWPARAM(0, delta)
            lParam = MAKELONG(x+窗口矩形[0], y+窗口矩形[1])
            win32gui.PostMessage(句柄, win32con.WM_MOUSEWHEEL, wParam, lParam)

            if 长按时间 > 0:
                time.sleep(长按时间)
    except Exception as e:
        print(f"模拟滚轮失败: {e}")

def 模拟按键按下(句柄, vk_code):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    win32gui.PostMessage(句柄, win32con.WM_KEYDOWN, vk_code, 0)
def 模拟按键弹起(句柄, vk_code):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    win32gui.PostMessage(句柄, win32con.WM_KEYUP, vk_code, 0)
    time.sleep(0.01)
def 模拟按键长按(句柄, vk_code, 长按时间=0.05):
    """
    使用窗口消息模拟按键长按（可在后台工作，但兼容性较差）

    参数:
    句柄: 目标窗口句柄 (int)
    vk_code: 虚拟键码 (int)
    长按时间: 按键持续时间 (秒)
    """
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    # 生成正确的lParam值

    def make_key_lparam(vk):
        scan_code = win32api.MapVirtualKey(vk, 0)  # 获取扫描码
        # 构造lParam (详见WM_KEYDOWN文档)
        return (1 | (scan_code << 16) | (0 << 24) | (0 << 29) | (0 << 30) | (0 << 31))

    # 发送按键按下消息
    win32gui.PostMessage(句柄, win32con.WM_KEYDOWN, vk_code, make_key_lparam(vk_code))
    # 保持按键状态
    time.sleep(长按时间)
    # 发送按键释放消息
    win32gui.PostMessage(句柄, win32con.WM_KEYUP, vk_code, 0xC0000000 | make_key_lparam(vk_code))
    time.sleep(0.01)

def 前台模拟鼠标左键按下绑定窗口(x, y, 窗口矩形):
    try:

        x = x + 窗口矩形[0]
        y = y + 窗口矩形[1]
        pydirectinput.mouseDown(x=x, y=y, button='left')
    except Exception as e:
        print(f"PyAutoGUI_模拟鼠标左键按下出现错误，详情：{e}")

def 前台模拟鼠标左键弹起绑定窗口(x, y, 窗口矩形):
    try:
        x = x + 窗口矩形[0]
        y = y + 窗口矩形[1]
        pydirectinput.mouseUp(x=x, y=y, button='left')
        time.sleep(0.01)
    except Exception as e:
        print(f"PyAutoGUI_模拟鼠标左键弹起出现错误，详情：{e}")

def 前台模拟鼠标左键单击绑定窗口(x, y, 窗口矩形, 点击时间=0.05, 次数=1):
    print(f"点击{x}，{y}")
    try:
        x = x + 窗口矩形[0]
        y = y + 窗口矩形[1]
        for _ in range(次数):
            pydirectinput.mouseDown(x=x, y=y, button='left')
            time.sleep(点击时间)
            pydirectinput.mouseUp(x=x, y=y, button='left')
            time.sleep(0.01)
    except Exception as e:
        print(f"PyAutoGUI_模拟鼠标左键单击，详情：{e} 坐标={x}，{y}")
def 后台模拟鼠标左键按下(句柄,):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    try:
        win32gui.PostMessage(句柄, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, MAKELONG(640, 360))

        time.sleep(0.01)
    except Exception as e:
        print(f"{e}")

def 后台模拟鼠标右键按下(句柄,):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    win32gui.PostMessage(句柄, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, MAKELONG(640, 360))
    time.sleep(0.01)
def 后台模拟鼠标左键弹起(句柄,):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    try:

        win32gui.PostMessage(句柄, win32con.WM_LBUTTONUP, 0, MAKELONG(640, 360))

    except Exception as e:
        print(f"{e}")

def 后台模拟鼠标右键弹起(句柄, ):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    win32gui.PostMessage(句柄, win32con.WM_RBUTTONUP, 0, MAKELONG(640, 360))
def 后台模拟鼠标左键点击(句柄,长按时间=0.05):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    try:
        win32gui.PostMessage(句柄, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, MAKELONG(640, 360))
        time.sleep(长按时间)
        win32gui.PostMessage(句柄, win32con.WM_LBUTTONUP, 0, MAKELONG(640, 360))
        time.sleep(0.01)
    except Exception as e:
        print(f"{e}")

def 后台模拟鼠标右键长按(句柄, 长按时间=0.05):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    win32gui.PostMessage(句柄, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, MAKELONG(640, 360))
    time.sleep(长按时间)
    win32gui.PostMessage(句柄, win32con.WM_RBUTTONUP, 0, MAKELONG(640, 360))
    time.sleep(0.01)

def 后台模拟鼠标中键长按(句柄,  长按时间=0.05):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    # 发送鼠标中键按下消息
    win32gui.PostMessage(句柄, win32con.WM_MBUTTONDOWN, 0, MAKELONG(640, 360))
    time.sleep(长按时间)
    # 发送鼠标中键释放消息
    win32gui.PostMessage(句柄, win32con.WM_MBUTTONUP, 0, MAKELONG(640, 360))
    time.sleep(0.01)


def 游戏_等待(总时间, 线程事件):
    if 总时间 < 1:
        if not 线程事件.is_set():
            return
        time.sleep(总时间)
    else:
        full_seconds = int(总时间)
        for _ in range(full_seconds):
            if not 线程事件.is_set():
                return
            time.sleep(1)
        remaining = 总时间 - full_seconds
        if remaining > 0:
            if not 线程事件.is_set():
                return
            time.sleep(remaining)


def 模拟鼠标右键长按(句柄, x, y, 长按时间):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    win32gui.PostMessage(句柄, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, MAKELONG(x, y))
    time.sleep(长按时间)
    win32gui.PostMessage(句柄, win32con.WM_RBUTTONUP, 0, MAKELONG(x, y))
def 模拟鼠标中键长按(句柄, x, y, 长按时间):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    # 发送鼠标中键按下消息
    win32gui.PostMessage(句柄, win32con.WM_MBUTTONDOWN, 0, MAKELONG(x, y))
    time.sleep(长按时间)
    # 发送鼠标中键释放消息
    win32gui.PostMessage(句柄, win32con.WM_MBUTTONUP, 0, MAKELONG(x, y))




def 模拟鼠标中键点击(句柄, x, y, 长按时间):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    # 发送鼠标中键按下消息
    win32gui.PostMessage(句柄, win32con.WM_MBUTTONDOWN, 0, MAKELONG(x, y))
    time.sleep(长按时间)
    # 发送鼠标中键释放消息
    win32gui.PostMessage(句柄, win32con.WM_MBUTTONUP, 0, MAKELONG(x, y))




def 模拟鼠标左键长按(句柄, x, y, 长按时间):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    try:
        win32gui.PostMessage(句柄, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, MAKELONG(x, y))
        time.sleep(长按时间)
        win32gui.PostMessage(句柄, win32con.WM_LBUTTONUP, 0, MAKELONG(x, y))
    except Exception as e:
        print(f"{e}")
def 模拟鼠标左键按下(句柄, x, y, 延时=0.001):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")

    win32gui.PostMessage(句柄, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, MAKELONG(x, y))
    time.sleep(延时)
def 模拟鼠标左键弹起(句柄, x, y, 延时=0.001):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    win32gui.PostMessage(句柄, win32con.WM_LBUTTONUP, x, y)
    time.sleep(延时)
def 模拟按键点击(句柄, vk_code):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    win32gui.PostMessage(句柄, win32con.WM_KEYDOWN, vk_code, 0)
    win32gui.PostMessage(句柄, win32con.WM_KEYUP, vk_code, 0)
def 模拟鼠标左键点击(句柄, x, y):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")

    win32gui.PostMessage(句柄, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, MAKELONG(x, y))
    win32gui.PostMessage(句柄, win32con.WM_LBUTTONUP, 0, MAKELONG(x, y))
def 模拟鼠标右键点击(句柄, x, y):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    win32gui.PostMessage(句柄, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, MAKELONG(x, y))
    win32gui.PostMessage(句柄, win32con.WM_RBUTTONUP, 0, MAKELONG(x, y))



# 模拟鼠标按下

def 模拟鼠标右键按下(句柄, x, y, 延时=0.001):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    win32gui.PostMessage(句柄, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, MAKELONG(x, y))
    time.sleep(延时)

# 模拟鼠标移动
def 模拟鼠标移动(句柄, x, y):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    win32gui.PostMessage(句柄, win32con.WM_MOUSEMOVE, 0, MAKELONG(x, y))

def 弹起所有按键(句柄):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    模拟按键弹起(句柄, 0x71)#F2
    模拟按键弹起(句柄, 0x51)
    模拟按键弹起(句柄, 0x45)
    模拟按键弹起(句柄, 0x52)
    模拟按键弹起(句柄, 0x46)
    模拟按键弹起(句柄, 0x58)
    模拟按键弹起(句柄, 0x54)
    模拟按键弹起(句柄, 0x4D)
    模拟按键弹起(句柄, 0x31)
    模拟按键弹起(句柄, 0x32)
    模拟按键弹起(句柄, 0x33)
    模拟按键弹起(句柄, 0x34)
    模拟按键弹起(句柄, 0xA0)
    模拟按键弹起(句柄, 0x20)
    模拟按键弹起(句柄, 0x04)
    模拟按键弹起(句柄, 0x04)
    # 添加WASD键弹起
    模拟按键弹起(句柄, 0x57)  # W
    模拟按键弹起(句柄, 0x41)  # A
    模拟按键弹起(句柄, 0x53)  # S
    模拟按键弹起(句柄, 0x44)  # D
    模拟按键弹起(句柄, 0x1B)  # esc
    # 弹起鼠标左键
    win32gui.PostMessage(句柄, win32con.WM_LBUTTONUP, 0, 0)
    # 弹起鼠标右键
    win32gui.PostMessage(句柄, win32con.WM_RBUTTONUP, 0,0)
def 后台粘贴文本(句柄):
    """
    在指定窗口后台执行粘贴操作
    参数:
        句柄: 目标窗口句柄
    """
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    # 发送Ctrl+V组合键
    模拟按键按下(句柄, 0xA2)  # 0xA2 是Ctrl键的虚拟键码
    模拟按键按下(句柄, 0x56)  # 0x56 是V键的虚拟键码
    time.sleep(0.05)  # 短暂延迟确保组合键生效

    # 释放按键
    模拟按键弹起(句柄, 0x56)  # 先释放V键
    模拟按键弹起(句柄, 0xA2)  # 再释放Ctrl键
def 鼠标相对移动(移动x,移动y):
    (x,y)  = win32api.GetCursorPos()
    print((x,y))
    for i in range(移动y):
        win32api.SetCursorPos((x, y +i+1))


def 真实鼠标移动(窗口矩形, 坐标):
    """
    优化的鼠标移动函数 - 只在出错时进行计算
    """
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            # 第一次尝试直接移动，不进行预计算
            if retry_count == 0:
                x, y = 坐标
                abs_x = x + 窗口矩形[0]
                abs_y = y + 窗口矩形[1]
                win32api.SetCursorPos((abs_x, abs_y))
                return True

            # 如果第一次失败，重试时进行计算和验证
            else:
                x, y = 坐标
                abs_x = x + 窗口矩形[0]
                abs_y = y + 窗口矩形[1]

                # 只在重试时获取屏幕尺寸
                screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)

                screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

                # 调整超出边界的坐标
                if abs_x < 0 or abs_x >= screen_width or abs_y < 0 or abs_y >= screen_height:
                    #print(f"调整坐标: ({abs_x}, {abs_y}) -> ", end="")
                    abs_x = max(0, min(abs_x, screen_width - 1))
                    abs_y = max(0, min(abs_y, screen_height - 1))
                    #print(f"({abs_x}, {abs_y})")

                win32api.SetCursorPos((abs_x, abs_y))
                return True

        except Exception as e:
            retry_count += 1
            print(f"鼠标移动失败 (尝试 {retry_count}/{max_retries}): {e}")

            if retry_count >= max_retries:
                return False
            time.sleep(0.1)

    return False


def 真实鼠标拖拽(窗口矩形,句柄,start_x, start_y,points,每步延时):

    原位置 = win32api.GetCursorPos()

    # 移动到目标坐标
    win32api.SetCursorPos((start_x+窗口矩形[0], start_y+窗口矩形[1]))

    for x, y in points:
        win32api.SetCursorPos((x+窗口矩形[0], y+窗口矩形[1]))
        模拟鼠标移动(句柄, x, y)
        time.sleep(每步延时)
    # 移回原位置
    win32api.SetCursorPos(原位置)
# 执行按键和鼠标操作
# 按键顺序：F2, Q, E, R, F, X, T, M, 1, 2, 3, 4, Shift（左）
总按键列表 = [
    0x71,  # F2
    0x51,             # Q
    0x45,             # E
    0x52,             # R
    0x46,             # F
    0x58,             # X
    0x54,             # T
    0x4D,             # M
    0x31,             # 1
    0x32,             # 2
    0x33,             # 3
    0x34,             # 4
    0xA0,    # 左 Shift
    0x20,    # 空格键
    0x04,    # 鼠标中键
    0x57,    # W
    0x41,    # A
    0x53,    # S
    0x44,    # D
    0x1B,    #esc
    0xA4,     #alt
    0x09,   #TAB
]

# 定义一个事件对象用于控制线程的暂停和恢复
暂停事件 = threading.Event()
暂停事件.set()  # 初始状态为运行
# 定义一个退出事件
退出事件 = threading.Event()
# 速切战斗线程
def 速切不开R战斗单线程(句柄,战斗频率):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    延时 = 0.05
    for _ in range(战斗频率):
        模拟按键长按(句柄, 0x45, 延时)
        模拟按键长按(句柄, 0x51, 延时)
        模拟按键长按(句柄, 0x31, 延时)
        模拟按键长按(句柄, 0x32, 延时)
        模拟按键长按(句柄, 0x33, 延时)
        模拟鼠标左键长按(句柄, 640, 360, 延时)
        模拟鼠标左键长按(句柄, 640, 360, 延时)
def 速切战斗单线程(句柄,战斗频率):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    for _ in range(战斗频率):
            模拟按键点击(句柄, 0x52)
            模拟按键点击(句柄, 0x45)
            模拟按键点击(句柄, 0x51)
            模拟按键点击(句柄, 0x31)
            模拟按键点击(句柄, 0x32)
            模拟按键点击(句柄, 0x33)
            模拟鼠标左键点击(句柄, 640, 360)
            模拟鼠标左键点击(句柄, 640, 360)
            time.sleep(0.05)
def 不切人战斗单线程(句柄,战斗频率):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    for _ in range(战斗频率//2+1):
            模拟按键点击(句柄, 0x52)
            模拟按键点击(句柄, 0x45)
            模拟按键点击(句柄, 0x51)
            模拟按键点击(句柄, 0x31)
            模拟鼠标左键长按(句柄, 640, 360,0.1)
            模拟鼠标左键长按(句柄, 640, 360,0.1)
            time.sleep(0.05)
def 选择对应坐标角色(最大匹配y坐标,句柄,长按时间):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    if 最大匹配y坐标 < 195:
        模拟按键长按(句柄, 0x31, 长按时间)
    elif 最大匹配y坐标 < 281:
        模拟按键长按(句柄, 0x32, 长按时间)
    elif 最大匹配y坐标 < 365:
        模拟按键长按(句柄, 0x33, 长按时间)
def 速切战斗线程(句柄,事件对象,保持速切战斗线程事件对象,执行速切战斗线程事件对象):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
        延时 = 0.005
        #延时2=0.05
        while 保持速切战斗线程事件对象.is_set():
            for _ in range(3):
                if 执行速切战斗线程事件对象.is_set():
                    #模拟按键长按(句柄, 0x52, 延时)
                    模拟鼠标左键长按(句柄, 640, 360, 延时)
                    模拟按键长按(句柄, 0x45, 延时)
                    模拟鼠标左键长按(句柄, 640, 360, 延时)
                    模拟按键长按(句柄, 0x51, 延时)
                    模拟鼠标左键长按(句柄, 640, 360, 延时)
                    模拟按键长按(句柄, 0x31, 延时)
                    模拟鼠标左键长按(句柄, 640, 360, 延时)
                    模拟按键长按(句柄, 0x32, 延时)
                    模拟鼠标左键长按(句柄, 640, 360, 延时)
                    模拟按键长按(句柄, 0x33, 延时)
                    模拟鼠标左键长按(句柄, 640, 360, 延时)
                else:
                    time.sleep(0.1)
                    break
            if not 事件对象.is_set():
                break

'''
            if not 执行速切战斗线程事件对象.is_set():
                #print(f"暂停不切人:{执行速切战斗线程事件对象.is_set()}")
                模拟按键长按(句柄, 0x31, 延时2)
                模拟按键长按(句柄, 0x32, 延时2)
                模拟按键长按(句柄, 0x33, 延时2)
                #模拟按键长按(句柄, 0x20, 延时2)
            else:
            if not 执行不切人战斗线程事件对象.is_set():
                #print(f"暂停切人:{执行不切人战斗线程事件对象.is_set()}")
                模拟按键长按(句柄, 0x31, 延时2)
                模拟按键长按(句柄, 0x32, 延时2)
                模拟按键长按(句柄, 0x33, 延时2)
                #模拟按键长按(句柄, 0x20, 延时2)
            else:
'''
def 速切宏战斗线程(句柄,保持速切战斗线程事件对象, 执行速切战斗线程事件对象,hotkey):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    延时 = 0.005

    def 普攻x秒():
        开始时间 = time.time()
        while time.time() - 开始时间 < 1.9:
            for _ in range(2):
                模拟鼠标左键长按(句柄, 640, 360, 延时)
                模拟按键长按(句柄, 0x52, 延时)
                模拟鼠标左键长按(句柄, 640, 360, 延时)
                模拟按键长按(句柄, 0x45, 延时)
                模拟鼠标左键长按(句柄, 640, 360, 延时)
                模拟按键长按(句柄, 0x51, 延时)
                模拟鼠标左键长按(句柄, 640, 360, 延时)
    """
         while 保持速切战斗线程事件对象.is_set():
        for _ in range(20):
            if 执行速切战斗线程事件对象.is_set():

                模拟按键长按(句柄, 0x31, 延时)
                普攻x秒()
                模拟按键长按(句柄, 0x34, 延时)
                普攻x秒()
                模拟鼠标中键点击(句柄, 640, 360, 0.09)
                模拟按键长按(句柄, 0x32, 延时)
                普攻x秒()
                模拟按键长按(句柄, 0x33, 延时)
                普攻x秒()
                模拟按键长按(句柄, 0x34, 延时)
                普攻x秒()
        while 保持速切战斗线程事件对象.is_set():
        for _ in range(20):
            if 执行速切战斗线程事件对象.is_set():
                模拟按键长按(句柄, 0x52, 延时)
                模拟鼠标左键长按(句柄, 640, 360, 延时)
                模拟按键长按(句柄, 0x45, 延时)
                模拟鼠标左键长按(句柄, 640, 360, 延时)
                模拟按键长按(句柄, 0x51, 延时)
                模拟鼠标左键长按(句柄, 640, 360, 延时)
                模拟按键长按(句柄, 0x31, 延时)
                模拟鼠标左键长按(句柄, 640, 360, 延时)
                模拟按键长按(句柄, 0x32, 延时)
                模拟鼠标左键长按(句柄, 640, 360, 延时)
                模拟按键长按(句柄, 0x33, 延时)
                模拟鼠标左键长按(句柄, 640, 360, 延时)
    """

    while 保持速切战斗线程事件对象.is_set():
        if has_child_windows(句柄):
            hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
            if hwnd:
                句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
        for _ in range(20):
            if 执行速切战斗线程事件对象.is_set():
                模拟鼠标中键点击(句柄, 640, 360, 延时)
                模拟按键长按(句柄, 0x52, 延时)
                模拟鼠标左键长按(句柄, 640, 360, 延时)
                模拟按键长按(句柄, 0x45, 延时)
                模拟鼠标左键长按(句柄, 640, 360, 延时)
                模拟按键长按(句柄, 0x51, 延时)
                模拟鼠标左键长按(句柄, 640, 360, 延时)
                模拟按键长按(句柄, 0x31, 延时)
                模拟鼠标左键长按(句柄, 640, 360, 延时)
                模拟按键长按(句柄, 0x34, 延时)
                模拟鼠标左键长按(句柄, 640, 360, 延时)
                模拟按键长按(句柄, 0x32, 延时)
                模拟鼠标左键长按(句柄, 640, 360, 延时)
                模拟按键长按(句柄, 0x33, 延时)
                模拟鼠标左键长按(句柄, 640, 360, 延时)
            else:
                time.sleep(0.3)
            if not 保持速切战斗线程事件对象.is_set():
                break
        if not 执行速切战斗线程事件对象.is_set():
             print(f"正在等待热键{hotkey}按下后启动速切")
def 不切人战斗线程(句柄,事件对象,保持不切人战斗线程事件对象,执行不切人战斗线程事件对象):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    #延时2=0.05
    while 保持不切人战斗线程事件对象.is_set():
        if 执行不切人战斗线程事件对象.is_set():

            模拟按键点击(句柄, 0x52)
            模拟按键点击(句柄, 0x45)
            模拟按键点击(句柄, 0x51)
            模拟按键点击(句柄, 0x31)
            模拟鼠标左键长按(句柄, 640, 360, 0.1)
            模拟鼠标左键长按(句柄, 640, 360, 0.1)
        else:
            time.sleep(0.1)
        for _ in range(10):
            if 执行不切人战斗线程事件对象.is_set():

                模拟鼠标左键长按(句柄, 640, 360, 0.1)
            else:
                break

        if not 事件对象.is_set():
            break
def 特殊战斗线程(句柄,事件对象,保持特殊战斗线程事件对象,执行特殊战斗线程事件对象,普攻模式=1,主角色按键码=0x31):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    #延时2=0.05
    while 保持特殊战斗线程事件对象.is_set():

        if 执行特殊战斗线程事件对象.is_set():
            if 普攻模式 == 2:
                for _ in range(30):
                    模拟按键点击(句柄, 主角色按键码)
                    模拟鼠标左键长按(句柄, 640, 360, 0.05)
                    模拟鼠标左键长按(句柄, 640, 360, 0.05)
                    if not 执行特殊战斗线程事件对象.is_set():
                        break
                模拟按键点击(句柄, 主角色按键码)
                模拟鼠标左键按下(句柄, 640, 360, 0.1)
                for _ in range(20):
                    if 执行特殊战斗线程事件对象.is_set():
                        time.sleep(0.2)
                        模拟按键点击(句柄, 主角色按键码)
                    else:
                        break
                模拟鼠标左键弹起(句柄, 278, 334, 延时=0.001)
                if 执行特殊战斗线程事件对象.is_set():
                    模拟鼠标左键按下(句柄, 640, 360, 0.1)
                    模拟按键点击(句柄, 主角色按键码)
            elif 普攻模式 == 1:
                for _ in range(20):
                    if 执行特殊战斗线程事件对象.is_set():
                        模拟按键点击(句柄, 主角色按键码)
                        for _ in range(20):
                            if 执行特殊战斗线程事件对象.is_set():
                                模拟按键点击(句柄, 主角色按键码)
                                模拟鼠标左键长按(句柄, 640, 360, 0.05)
                                模拟鼠标左键长按(句柄, 640, 360, 0.05)
                                模拟按键点击(句柄, 0x45)
                                模拟按键点击(句柄, 主角色按键码)
                                模拟按键点击(句柄, 0x45)
                                模拟按键点击(句柄, 0x51)
                                模拟鼠标左键长按(句柄, 640, 360, 0.05)
                                模拟鼠标左键长按(句柄, 640, 360, 0.05)
                            else:
                                break
                    else:
                        break
        else:
            time.sleep(0.1)
        if not 事件对象.is_set():
            break
    #模拟鼠标左键弹起(句柄, 278, 334, 延时=0.01)

def 模拟鼠标拖拽(句柄, start_x, start_y, end_x, end_y, 拖拽时间=0.5, 步数=20):
    """
    在后台窗口模拟鼠标拖拽操作
    参数:
        句柄: 目标窗口句柄
        start_x, start_y: 拖拽起始坐标
        end_x, end_y: 拖拽结束坐标
        拖拽时间: 整个拖拽过程的持续时间（秒）
        步数: 拖拽过程中的中间步数
    """
    # 计算每步的时间间隔
    每步延时 = 拖拽时间 / 步数

    # 移动到起始位置
    模拟鼠标移动(句柄, start_x, start_y)
    time.sleep(0.05)  # 短暂延迟确保移动完成

    # 在起始位置按下鼠标左键
    模拟鼠标左键按下(句柄, start_x, start_y)
    time.sleep(0.05)  # 短暂延迟确保按下

    # 计算每一步的坐标变化
    x_step = (end_x - start_x) / 步数
    y_step = (end_y - start_y) / 步数

    # 逐步移动鼠标（模拟拖拽）
    for i in range(1, 步数 + 1):
        current_x = int(start_x + i * x_step)
        current_y = int(start_y + i * y_step)
        模拟鼠标移动(句柄, current_x, current_y)
        time.sleep(每步延时)

    # 在结束位置释放鼠标左键
    模拟鼠标左键弹起(句柄, end_x, end_y)
    time.sleep(0.05)  # 短暂延迟确保释放


# 新增：平滑拖拽（带曲线效果）
def 模拟平滑拖拽(窗口矩形,句柄, start_x, start_y, end_x, end_y, 拖拽时间=0.5, 步数=30):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    """
    在后台窗口模拟平滑的拖拽操作（带曲线效果）
    参数:
        句柄: 目标窗口句柄
        start_x, start_y: 拖拽起始坐标
        end_x, end_y: 拖拽结束坐标
        拖拽时间: 整个拖拽过程的持续时间（秒）
        步数: 拖拽过程中的中间步数
    """
    # 计算每步的时间间隔
    每步延时 = 拖拽时间 / 步数

    # 移动到起始位置
    模拟鼠标移动(句柄, start_x, start_y)
    time.sleep(0.05)

    # 在起始位置按下鼠标左键
    模拟鼠标左键按下(句柄, start_x, start_y)
    time.sleep(0.05)

    # 计算控制点（创建曲线效果）
    ctrl_x = start_x + (end_x - start_x) // 2
    ctrl_y = start_y - (end_y - start_y) // 3

    # 使用贝塞尔曲线计算路径
    points = []
    for t in range(步数 + 1):
        t_normal = t / 步数
        # 二次贝塞尔曲线公式
        x = (1 - t_normal) ** 2 * start_x + 2 * (1 - t_normal) * t_normal * ctrl_x + t_normal ** 2 * end_x
        y = (1 - t_normal) ** 2 * start_y + 2 * (1 - t_normal) * t_normal * ctrl_y + t_normal ** 2 * end_y
        points.append((int(x), int(y)))

    真实鼠标拖拽(窗口矩形,句柄, start_x, start_y, points,每步延时)

    # 在结束位置释放鼠标左键
    模拟鼠标左键弹起(句柄, end_x, end_y)
    time.sleep(0.05)
def 模拟平滑移动(窗口矩形,句柄, start_x, start_y, end_x, end_y, 拖拽时间=0.5, 步数=30):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    """
    在后台窗口模拟平滑的拖拽操作（带曲线效果）
    参数:
        句柄: 目标窗口句柄
        start_x, start_y: 拖拽起始坐标
        end_x, end_y: 拖拽结束坐标
        拖拽时间: 整个拖拽过程的持续时间（秒）
        步数: 拖拽过程中的中间步数
    """
    # 计算每步的时间间隔
    每步延时 = 拖拽时间 / 步数

    # 移动到起始位置
    模拟鼠标移动(句柄, start_x, start_y)
    time.sleep(0.05)

    # 计算控制点（创建曲线效果）
    ctrl_x = start_x + (end_x - start_x) // 2
    ctrl_y = start_y - (end_y - start_y) // 3

    # 使用贝塞尔曲线计算路径
    points = []
    for t in range(步数 + 1):
        t_normal = t / 步数
        # 二次贝塞尔曲线公式
        x = (1 - t_normal) ** 2 * start_x + 2 * (1 - t_normal) * t_normal * ctrl_x + t_normal ** 2 * end_x
        y = (1 - t_normal) ** 2 * start_y + 2 * (1 - t_normal) * t_normal * ctrl_y + t_normal ** 2 * end_y
        points.append((int(x), int(y)))
    真实鼠标拖拽(窗口矩形, 句柄, start_x, start_y, points, 每步延时)


    # 在结束位置释放鼠标左键

    time.sleep(0.05)

# 新增：圆形拖拽（演示拖拽路径）
def 模拟圆形拖拽(窗口矩形,句柄, center_x, center_y, 半径=100, 拖拽时间=1.0, 步数=50):
    if has_child_windows(句柄):
        hwnd = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if hwnd:
            句柄 = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    """
    在后台窗口模拟圆形拖拽操作
    参数:
        句柄: 目标窗口句柄
        center_x, center_y: 圆心坐标
        半径: 圆形半径
        拖拽时间: 整个拖拽过程的持续时间（秒）
        步数: 拖拽过程中的中间步数
    """
    # 计算每步的时间间隔
    每步延时 = 拖拽时间 / 步数

    # 计算起始点
    start_x = center_x
    start_y = center_y - 半径

    # 移动到起始位置
    模拟鼠标移动(句柄, start_x, start_y)
    time.sleep(0.05)

    # 在起始位置按下鼠标左键
    模拟鼠标左键按下(句柄, start_x, start_y)
    time.sleep(0.05)

    # 计算圆形路径
    points = []
    for i in range(步数 + 1):
        angle = 2 * math.pi * i / 步数
        x = center_x + int(半径 * math.cos(angle))
        y = center_y + int(半径 * math.sin(angle))
        points.append((x, y))

    # 执行圆形拖拽
    真实鼠标拖拽(窗口矩形,句柄,start_x, start_y, points,每步延时)

    # 在结束位置释放鼠标左键
    模拟鼠标左键弹起(句柄, points[-1][0], points[-1][1])
    time.sleep(0.05)

pydirectinput.PAUSE = 0
# 鼠标右键操作

# 鼠标左键操作
def PyAutoGUI_模拟鼠标左键按下(x, y):
    try:


        pydirectinput.mouseDown(x=x, y=y, button='left')
    except Exception as e:
        print(f"PyAutoGUI_模拟鼠标左键按下出现错误，详情：{e}")

def PyAutoGUI_模拟鼠标左键弹起(x, y):

    try:
        pydirectinput.mouseUp(x=x, y=y, button='left')
    except Exception as e:
        print(f"PyAutoGUI_模拟鼠标左键弹起出现错误，详情：{e}")

def PyAutoGUI_模拟鼠标左键单击(x, y,点击时间,点击后等待=0.001):

    try:
        pydirectinput.mouseDown(x=x, y=y, button='left')
        time.sleep(点击时间)
        pydirectinput.mouseUp(x=x, y=y, button='left')
        time.sleep(点击后等待)
    except Exception as e:
        print(f"PyAutoGUI_模拟鼠标左键单击，详情：{e} 坐标={x}，{y}")






def PyAutoGUI_模拟鼠标右键按下(x, y):
    try:
        pydirectinput.mouseDown(x=x, y=y, button='right')
    except Exception as e:
        print(f"PyAutoGUI_模拟鼠标右键按下出现错误，详情：{e}")

def PyAutoGUI_模拟鼠标右键弹起(x, y):
    try:
        pydirectinput.mouseUp(x=x, y=y, button='right')
    except Exception as e:
        print(f"PyAutoGUI_模拟鼠标右键弹起出现错误，详情：{e}")



def PyAutoGUI_模拟滚轮滚动(滚动值):
    try:
        pydirectinput.scroll(滚动值)
    except Exception as e:
        print(f"PyAutoGUI_模拟滚轮滚动出现错误，详情：{e}")

def PyAutoGUI_模拟水平滚轮(水平值):
    try:
        pydirectinput.hscroll(水平值)
    except Exception as e:
        print(f"PyAutoGUI_模拟水平滚轮出现错误，详情：{e}")

def PyAutoGUI_模拟中键按下(x, y):
    try:
        pydirectinput.mouseDown(x=x, y=y, button='middle')
    except Exception as e:
        print(f"PyAutoGUI_模拟中键按下出现错误，详情：{e}")

def PyAutoGUI_模拟中键弹起(x, y):
    try:
        pydirectinput.mouseUp(x=x, y=y, button='middle')
    except Exception as e:
        print(f"PyAutoGUI_模拟中键弹起出现错误，详情：{e}")

def PyAutoGUI_模拟按键按下(按键):
    try:
        pydirectinput.keyDown(按键)
    except Exception as e:
        print(f"PyAutoGUI_模拟按键按下{e}")

def PyAutoGUI_模拟按键弹起(按键):
    try:
        pydirectinput.keyUp(按键)
    except Exception as e:
        print(e)



def activate_and_click_center(hwnd, window_rect=None):

    """
    激活指定窗口并点击窗口矩形中心

    参数:
    hwnd: 目标窗口句柄 (int)
    window_rect: 窗口矩形坐标 (tuple: (left, top, right, bottom))
    """
    if has_child_windows(hwnd):
        句柄 = find_child_window(hwnd, "Qt51517QWindowIcon", "NTECloudGame")
        if 句柄:
            hwnd = find_child_window(hwnd, "WLCloudGameClient", "WLCloudGame")
    # 确保窗口句柄有效
    if not win32gui.IsWindow(hwnd):
        raise ValueError("无效的窗口句柄")
    # 获取窗口矩形（如果未提供）
    if window_rect is None:
        window_rect = win32gui.GetWindowRect(hwnd)
    # 计算中心坐标
    left, top, right, bottom = window_rect
    center_x = left + (right - left) // 2
    center_y = top + (bottom - top) // 2
    # 激活窗口到前台
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)
    # 等待窗口激活（0.5秒）
    time.sleep(0.5)
    # 移动鼠标到中心位置
    win32api.SetCursorPos((center_x, center_y))

    # 模拟鼠标点击（按下+释放）
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, center_x, center_y, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, center_x, center_y, 0, 0)


import win32api
import win32con
import time


def 调整坐标到屏幕范围内(坐标):
    """确保坐标在屏幕范围内"""
    try:
        x, y = 坐标
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        # 调整到有效范围内
        x = max(0, min(x, screen_width - 1))
        y = max(0, min(y, screen_height - 1))
        return (x, y)
    except:
        # 如果获取屏幕尺寸失败，返回一个安全的默认位置
        return (100, 100)


def 安全设置鼠标位置(坐标, 描述=""):
    """安全地设置鼠标位置，包含错误处理和重试"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            安全坐标 = 调整坐标到屏幕范围内(坐标)
            win32api.SetCursorPos(安全坐标)

            # 验证鼠标是否真的移动到了目标位置
            time.sleep(0.01)  # 短暂延迟让系统更新
            当前位置 = win32api.GetCursorPos()

            # 如果移动成功，返回True
            if abs(当前位置[0] - 安全坐标[0]) <= 2 and abs(当前位置[1] - 安全坐标[1]) <= 2:
                return True
            else:
                pass
                #print(f"{描述}: 鼠标位置验证失败 (尝试 {attempt + 1}/{max_retries})")

        except Exception as e:
            pass
            #print(f"{描述}: 设置鼠标位置失败 (尝试 {attempt + 1}/{max_retries}): {e}")

        # 重试前短暂等待
        if attempt < max_retries - 1:
            time.sleep(0.05)

    return False


def 真实鼠标传递坐标后台点击(句柄, 矩形, 坐标,长按时间,脱离时间):
    """异环只能通过传递真实鼠标坐标实现鼠标模拟"""
    try:

        原位置 = win32api.GetCursorPos()
        win32api.SetCursorPos(坐标)
        模拟鼠标左键长按(句柄, 坐标[0], 坐标[1], 长按时间)
        time.sleep(脱离时间)
        win32api.SetCursorPos(原位置)
    except Exception as e:
        print(e)

def 真实鼠标坐标后台点击专用(句柄, 矩形, 坐标, 延时, 等待,鼠标回弹=True):
    """异环只能通过传递真实鼠标坐标实现鼠标模拟"""
    真实鼠标 = True
    hwnd1=0
    当前活动窗口 = 0
    try:
        if has_child_windows(句柄):
            hwnd1 = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
            hwnd2=句柄
            if hwnd1:
                句柄 = find_child_window(hwnd1, "WLCloudGameClient", "WLCloudGame")
                当前活动窗口 = win32gui.GetForegroundWindow()
                键 = "alt"
                PC键盘延迟=0.005
                for _ in range(50):

                    time.sleep(0.05+ PC键盘延迟)
                    当前窗口 = win32gui.GetForegroundWindow()
                    if 当前窗口 == hwnd2:

                        PyAutoGUI_模拟按键按下(键)
                        if 鼠标回弹:
                            原位置 = win32api.GetCursorPos()


                        time.sleep(0.075 + PC键盘延迟)
                        time.sleep(延时)
                        PyAutoGUI_模拟鼠标左键单击(坐标[0] + 矩形[0], 坐标[1] + 矩形[1], 0.08 + 延时)
                        time.sleep(等待+2)
                        PyAutoGUI_模拟按键弹起(键)
                        if 鼠标回弹:
                            win32api.SetCursorPos(原位置)
                            现位置 = win32api.GetCursorPos()
                            if 现位置 == 原位置:
                                pass
                            else:
                                win32api.SetCursorPos(原位置)
                        break
                    else:
                        try:
                            win32gui.ShowWindow(hwnd2, win32con.SW_RESTORE)
                            win32gui.SetForegroundWindow(hwnd2)
                        except Exception:

                            PyAutoGUI_模拟按键按下(键)
                            time.sleep(0.075 + PC键盘延迟)
                            time.sleep(延时)
                            PyAutoGUI_模拟鼠标左键单击(坐标[0] + 矩形[0], 坐标[1] + 矩形[1], 0.05 + 延时 + 等待)
                            time.sleep(等待)
                            PyAutoGUI_模拟按键弹起(键)
                for _ in range(50):

                    try:
                        win32gui.ShowWindow(当前活动窗口, win32con.SW_RESTORE)
                        win32gui.SetForegroundWindow(当前活动窗口)
                    except Exception:
                        pass
                    当前窗口 = win32gui.GetForegroundWindow()
                    if 当前窗口 == 当前活动窗口:
                        break
                    time.sleep(0.05 + PC键盘延迟)

        else:

                x, y = 坐标
                if 真实鼠标:
                    if 鼠标回弹:
                        原位置 = win32api.GetCursorPos()

                    # 移动鼠标到目标位置
                    if not 真实鼠标移动(矩形, (x, y)):
                        # print("鼠标移动失败，跳过点击操作")
                        return False

                time.sleep(延时)
                模拟鼠标左键长按(句柄, x, y, 0.01 + 延时)
                time.sleep(等待)
                if 真实鼠标:
                    if 鼠标回弹:
                        win32api.SetCursorPos(原位置)
                        现位置 = win32api.GetCursorPos()
                        if 现位置 == 原位置:
                            pass
                        else:
                            win32api.SetCursorPos(原位置)


        return True

    except Exception as e:
        # print(f"原鼠标位置: {原位置}")
        # print(f"真实鼠标坐标后台点击专用整体失败: {e}")
        return False
def 真实鼠标坐标后台点击专用店长特供(句柄, 矩形, 坐标, 延时, 等待,鼠标回弹=True,真实鼠标=False):
    """异环只能通过传递真实鼠标坐标实现鼠标模拟"""
    try:
        x, y = 坐标


        if 鼠标回弹:
            原位置 = win32api.GetCursorPos()


        # 移动鼠标到目标位置
        if not 真实鼠标移动(矩形, (x, y)):
            #print("鼠标移动失败，跳过点击操作")
            return False

        time.sleep(延时)
        if 真实鼠标:
            PyAutoGUI_模拟鼠标左键单击(x + 矩形[0], y + 矩形[1], 延时 )
        else:
            模拟鼠标左键长按(句柄, x, y, 延时)
        time.sleep(延时)
        if 鼠标回弹:
            win32api.SetCursorPos(原位置)
            现位置 = win32api.GetCursorPos()
            if 现位置 == 原位置:
                pass
            else:
                win32api.SetCursorPos(原位置)
        return True

    except Exception as e:
        #print(f"原鼠标位置: {原位置}")
        #print(f"真实鼠标坐标后台点击专用整体失败: {e}")
        return False
def 真实鼠标坐标后台点击(句柄,矩形,坐标,延时):
    原位置 =(1280,720)
    x, y = 坐标

    try:

        窗口假激活(句柄)
        原位置 = win32api.GetCursorPos()
        真实鼠标移动(矩形, (x, y))
        模拟鼠标左键长按(句柄, x, y, 0.009 + 延时)
        time.sleep(0.009 + 延时)

    except Exception as e:
        print(e)
    try:
        win32api.SetCursorPos(原位置)
        现位置 = win32api.GetCursorPos()
        if 现位置 == 原位置:
            pass
        else:
            win32api.SetCursorPos(原位置)
            # print(f"鼠标位置未恢复 (尝试第 {i + 1}次")

    except Exception as e:
        pass


# ======================= 功能键区 =======================
功能键区 = [
    27,  # Esc
    112,  # F1
    113,  # F2
    114,  # F3
    115,  # F4
    116,  # F5
    117,  # F6
    118,  # F7
    119,  # F8
    120,  # F9
    121,  # F10
    122,  # F11
    123,  # F12
    44,  # Print Screen
    145,  # Scroll Lock
    19  # Pause/Break
]

# ======================= 主键盘区 =======================
主键盘区 = [
    # 数字行
    192,  # ` ~
    49,  # 1 !
    50,  # 2 @
    51,  # 3 #
    52,  # 4 $
    53,  # 5 %
    54,  # 6 ^
    55,  # 7 &
    56,  # 8 *
    57,  # 9 (
    48,  # 0 )
    189,  # - _
    187,  # = +
    8,  # Backspace

    # 第一字母行
    9,  # Tab
    81,  # Q
    87,  # W
    69,  # E
    82,  # R
    84,  # T
    89,  # Y
    85,  # U
    73,  # I
    79,  # O
    80,  # P
    219,  # [ {
    221,  # ] }
    220,  # \ |

    # 第二字母行
    20,  # Caps Lock
    65,  # A
    83,  # S
    68,  # D
    70,  # F
    71,  # G
    72,  # H
    74,  # J
    75,  # K
    76,  # L
    186,  # ; :
    222,  # ' "
    13,  # Enter

    # 第三字母行
    160,  # 左 Shift
    90,  # Z
    88,  # X
    67,  # C
    86,  # V
    66,  # B
    78,  # N
    77,  # M
    188,  # , <
    190,  # . >
    191,  # / ?
    161,  # 右 Shift

    # 控制键行
    162,  # 左 Ctrl
    91,  # 左 Win
    164,  # 左 Alt
    32,  # Space
    165,  # 右 Alt
    92,  # 右 Win
    93,  # 右键菜单
    163  # 右 Ctrl
]

# ======================= 编辑键区 =======================
编辑键区 = [
    45,  # Insert
    36,  # Home
    33,  # Page Up
    46,  # Delete
    35,  # End
    34  # Page Down
]

# ======================= 方向键区 =======================
方向键区 = [
    38,  # ↑
    37,  # ←
    40,  # ↓
    39  # →
]

# ======================= 小键盘区 =======================
小键盘区 = [
    144,  # Num Lock
    111,  # /
    106,  # *
    109,  # -

    103,  # 7 (Home)
    104,  # 8 (↑)
    105,  # 9 (Page Up)
    107,  # +

    100,  # 4 (←)
    101,  # 5
    102,  # 6 (→)

    97,  # 1 (End)
    98,  # 2 (↓)
    99,  # 3 (Page Down)
    13,  # Enter

    96,  # 0 (Insert)
    110  # . (Delete)
]

# ======================= 鼠标键 =======================
鼠标键 = [
    4  # 鼠标中键
]

# ======================= 完整键盘列表 =======================
完整键盘列表 = 功能键区 + 主键盘区 + 编辑键区 + 方向键区 + 小键盘区 + 鼠标键


# 定义 Windows API 中优先级常量
PRIORITY_CLASSES = {
    'IDLE': 0x00000040,          # 空闲（最低优先级）
    'BELOW_NORMAL': 0x00004000,  # 低于正常
    'NORMAL': 0x00000020,        # 正常（默认）
    'ABOVE_NORMAL': 0x00008000,  # 高于正常
    'HIGH': 0x00000080,          # 高
    'REALTIME': 0x00000100       # 实时（最高，慎用）
}

# 所需权限
PROCESS_SET_INFORMATION = 0x0200

# 加载 kernel32.dll
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)


def set_process_priority(pid: int, priority: str) -> bool:
    """设置指定进程的优先级

    Args:
        pid: 目标进程的进程ID
        priority: 优先级字符串，可选值:
                  'IDLE', 'BELOW_NORMAL', 'NORMAL',
                  'ABOVE_NORMAL', 'HIGH', 'REALTIME'

    Returns:
        bool: 成功返回True，失败返回False

    Raises:
        ValueError: 如果priority不是有效值
    """
    if priority not in PRIORITY_CLASSES:
        raise ValueError(
            f"无效的优先级 '{priority}'，可选值: {list(PRIORITY_CLASSES.keys())}"
        )

    # 打开进程句柄
    hProcess = kernel32.OpenProcess(PROCESS_SET_INFORMATION, False, pid)
    if not hProcess:
        error = ctypes.get_last_error()
        print(f"无法打开进程 PID={pid}，错误代码: {error}")
        return False

    # 设置优先级
    priority_class = PRIORITY_CLASSES[priority]
    result = kernel32.SetPriorityClass(hProcess, priority_class)

    # 关闭句柄
    kernel32.CloseHandle(hProcess)

    if not result:
        error = ctypes.get_last_error()
        print(f"设置优先级失败，错误代码: {error}")
        return False

    print(f"成功将进程 PID={pid} 的优先级设置为 {priority}")
    return True
import os
def find_pids_by_exe(exe_path: str) -> list[int]:
    """
    根据可执行文件路径查找所有匹配的进程 PID（使用 pywin32）。
    仅适用于 Windows。
    """
    pids = []
    # 规范化目标路径
    target_path = os.path.normpath(os.path.normcase(exe_path))
    name_only = not (os.path.sep in target_path or '/' in target_path)

    # 枚举所有进程
    import win32process
    process_ids = win32process.EnumProcesses()

    for pid in process_ids:
        if pid == 0:  # 系统空闲进程，跳过
            continue
        try:
            # 打开进程，查询信息需要特定权限
            hProcess = win32api.OpenProcess(
                win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                False,
                pid
            )
        except win32api.error:
            # 无权限打开的进程（如系统进程）直接跳过
            continue

        try:
            # 获取可执行文件完整路径
            proc_exe = win32process.GetModuleFileNameEx(hProcess, 0)
            proc_name = os.path.basename(proc_exe)
        except win32api.error:
            # 某些保护进程可能获取不到路径
            proc_exe = None
            proc_name = None

        if proc_exe:
            # 按完整路径比较
            if os.path.normpath(os.path.normcase(proc_exe)) == target_path:
                pids.append(pid)
            elif name_only and proc_name and proc_name.lower() == target_path.lower():
                pids.append(pid)

        win32api.CloseHandle(hProcess)

    return pids
if __name__ == "__main__":


    import win32gui
    import win32con


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


    句柄 = 3019012

    if has_child_windows(句柄):
        print("该窗口有子窗口")
    else:
        print("该窗口没有子窗口")
    print("1111111111111111111111")
    句柄 = 3019012

    结果,父窗口句柄=has_parent_window(句柄)
    if 结果:

        print("该窗口有父窗口")
        结果, 父窗口句柄 = has_parent_window(父窗口句柄)
        if 结果:

            print("该窗口有父窗口")
            结果, 父窗口句柄 = has_parent_window(父窗口句柄)
        else:
            print("该窗口没有父窗口（或为顶级窗口）")
    else:
        print("该窗口没有父窗口（或为顶级窗口）")
    print("1111111111111111111111")
    if has_child_windows(句柄):
        print("该窗口有子窗口")


        def enum_children(hwnd_parent):
            """枚举并打印父窗口的所有直接子窗口信息"""

            def callback(child_hwnd, lparam):
                class_name = win32gui.GetClassName(child_hwnd)
                title = win32gui.GetWindowText(child_hwnd)
                print(f"句柄: {child_hwnd}, 类名: '{class_name}', 标题: '{title}'")
                return True  # 继续枚举

            print(f"开始枚举窗口 {hwnd_parent} 的子窗口：")
            win32gui.EnumChildWindows(hwnd_parent, callback, None)


        # 使用
        enum_children(句柄)
        句柄 = find_child_window(句柄, "Qt51517QWindowIcon", "NTECloudGame")
        if 句柄:
            print(句柄)
            句柄 = find_child_window(句柄, "WLCloudGameClient", "WLCloudGame")
            print(句柄)
        else:
            print("未找到对应子窗口")
    #窗口假激活(句柄)  # WLCloudGameClient#标题:WLCloudGame
    模拟按键长按(句柄, 0x46, 0.5)