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

