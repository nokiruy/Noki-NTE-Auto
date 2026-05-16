import subprocess
from PIL import Image
import win32clipboard  # 需要安装 pywin32 库
import numpy as np
import io
import win32ui
import win32con


def 关联调试桥(adb路径):
    """关联调试桥（仅需脚本开头调用一次）"""
    return adb路径


def 截屏(adb_config, x1, y1, x2, y2):
    """通过 ADB 截图并返回 PNG 字节数据"""
    adb路径, 端口 ,hwnd= adb_config

    # 构建截图命令
    if x1 == 0 and y1 == 0 and x2 == 0 and y2 == 0:
        adb命令 = f'"{adb路径}" -s {端口} shell screencap -p /sdcard/screen.png'
    else:
        adb命令 = f'"{adb路径}" -s {端口} shell screencap -p /sdcard/screen.png | "{adb路径}" -s {端口} shell crop {x1} {y1} {x2} {y2}'

    # 执行截图命令
    subprocess.run(adb命令, shell=True, capture_output=True)

    # 拉取截图到本地
    pull命令 = f'"{adb路径}" -s {端口} pull /sdcard/screen.png ./screen.png'
    subprocess.run(pull命令, shell=True, capture_output=True)


def 接收数据复制到剪切板(png_data):
    """将PNG图像数据复制到剪切板"""
    try:
        # 将PNG字节数据转换为图像对象
        image = Image.open(io.BytesIO(png_data))

        # 关键修改：直接保存为DIB格式，跳过格式转换步骤
        output = io.BytesIO()
        image.save(output, 'DIB')  # 直接生成DIB格式数据
        dib_data = output.getvalue()
        output.close()

        # 将图像数据复制到剪切板
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, dib_data)
        win32clipboard.CloseClipboard()
    except Exception as e:
        print(f"复制到剪切板时出错: {e}")
def 复制到剪切板():
    """将截图复制到剪切板"""
    try:
        # 打开截图文件
        图像 = Image.open('screen.png')

        # 将图像转换为RGB模式
        图像 = 图像.convert('RGB')

        # 转换为Win32的内存设备描述表
        import win32ui
        width, height = 图像.size
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(win32ui.GetForegroundWindow().GetDC(), width, height)
        memorydc = win32ui.CreateDCFromHandle(win32ui.GetForegroundWindow().GetDC().GetSafeHdc())
        memdc = memorydc.CreateCompatibleDC()
        memdc.SelectObject(bitmap)
        memdc.BitBlt((0, 0), (width, height), memorydc, (0, 0), win32con.SRCCOPY)

        # 将位图复制到剪切板
        output = io.BytesIO()
        图像.convert('RGB').save(output, 'BMP')
        data = output.getvalue()[14:]  # 跳过BMP文件头
        output.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
    except Exception as e:
        print(f"复制到剪切板时出错: {e}")

if __name__ == "__main__":
    # 设置 ADB 路径
    from 连接adb import 连接adb
    import threading

    线程事件 = threading.Event()
    线程事件.set()  # 初始状态设置为运行
    from pathlib import Path
    import sys
    from hbr2.adb操作 import 获取所有设备端口

    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent.absolute()
    else:
        current_dir = Path(__file__).parent.absolute()

    # 定义队伍目录
    adb程序 = current_dir / "platform-tools" / "adb.exe"
    所有设备 = 获取所有设备端口(adb程序)

    if 所有设备:
        print("已连接的设备列表:")
        for i, 设备 in enumerate(所有设备, 1):
            print(f"设备{i}: {设备}")

        # 创建设备配置元组列表
        设备配置列表 = [(adb程序, 端口) for 端口 in 所有设备]
        print("\n生成的设备配置元组:", 设备配置列表)
    else:
        print("未找到已连接的ADB设备")
    print(设备配置列表[0])
    adb路径 = 设备配置列表[0]
    adb路径 = "D:\\Program Files\\Netease\\MuMu Player 12\\shell\\adb.exe"
    '''
    "E:/leidian/LDPlayer9/adb.exe"
    "D:\\Program Files\\Netease\\MuMu Player 12\\shell\\adb.exe"
    "D:\\Program Files\\Netease\\MuMu Player 12\\hell\\adb.exe"
    "D:\\leidian\\LDPlayerVK\\adb.exe"
    '''


    # 截屏（全屏参数：0,0,0,0）
    截屏(adb路径, 0, 0, 0, 0)

    # 复制到剪切板
    复制到剪切板()
