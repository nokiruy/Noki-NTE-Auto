import subprocess
from PIL import Image
from io import BytesIO
from pathlib import Path
from tkinter import messagebox
import time
import sys
import os
import logging
import ctypes
import io
import win32ui
logger = logging.getLogger("database")
import win32gui
import win32con
import win32api
import pydirectinput
import numpy as np
def 获取顶级父窗口句柄(窗口句柄):
    """
    查找给定窗口句柄的顶级父窗口句柄

    参数:
        窗口句柄: 要查找父窗口的子窗口句柄

    返回:
        顶级父窗口句柄，如果找不到则返回0
    """
    if not 窗口句柄 or 窗口句柄 == 0:
        return 0

    # 获取当前窗口的父窗口
    父窗口句柄 = win32gui.GetParent(窗口句柄)

    # 循环查找直到找到顶级父窗口（没有父窗口的窗口）
    while 父窗口句柄 and 父窗口句柄 != 0:
        # 保存当前的父窗口句柄
        当前句柄 = 父窗口句柄
        # 继续向上查找父窗口
        父窗口句柄 = win32gui.GetParent(当前句柄)

        # 如果没有父窗口了，当前句柄就是顶级父窗口
        if 父窗口句柄 == 0:
            return 当前句柄

    # 如果本身就是顶级窗口，直接返回
    return 窗口句柄
def 获取窗口信息(窗口句柄):
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
def PyAutoGUI_模拟按键按下(按键):
    pydirectinput.keyDown(按键)

def PyAutoGUI_模拟按键弹起(按键):
    pydirectinput.keyUp(按键)
def pc端单击键盘无线程事件(hwnd, PC键盘延迟, 键列表, 次数):
    """
    pc端单击键盘(hwnd, PC键盘延迟, ["w","s"], 1,线程事件)
    """
    当前活动窗口 = win32gui.GetForegroundWindow()
    for _ in range(1000):

        time.sleep(0.05 + PC键盘延迟)
        当前窗口 = win32gui.GetForegroundWindow()
        if 当前窗口 == hwnd:
            for _ in range(次数):
                for 键 in 键列表:
                    PyAutoGUI_模拟按键按下(键)
                    time.sleep(0.075 + PC键盘延迟)
                    PyAutoGUI_模拟按键弹起(键)
            break
        else:
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
            except Exception:
                for 键 in 键列表:
                    PyAutoGUI_模拟按键按下(键)
                    time.sleep(0.075 + PC键盘延迟)
                    PyAutoGUI_模拟按键弹起(键)
    for _ in range(1000):

        try:
            win32gui.ShowWindow(当前活动窗口, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(当前活动窗口)
        except Exception:
            pass
        当前窗口 = win32gui.GetForegroundWindow()
        if 当前窗口 == 当前活动窗口:
            break
        time.sleep(0.05 + PC键盘延迟)
def 函数截图到内存直接返回NumPy数组(句柄, 矩形):
    """根据窗口信息进行截图并保存为无损PNG到内存"""
    #start_time = time.time()
    hdc = mfc_dc = save_dc = bitmap = None

    try:
        if not 句柄 or not 矩形:

            if 句柄:
                if 矩形 == 0:
                    矩形 = (0, 0, 1280, 720)#使用脚本要求分辨率
            else:
                logger.error(f"窗口信息未初始化")
                messagebox.showerror("错误", f"窗口信息未初始化,句柄:{句柄}，矩形：{矩形}")
                return _load_fallback_image()

        left, top, right, bottom = 矩形
        width = right - left
        height = bottom - top

        if not win32gui.IsWindowVisible(句柄):
            logger.error("目标窗口不可见")
            顶级父窗口 = 获取顶级父窗口句柄(句柄)
            pc端单击键盘无线程事件(顶级父窗口, 0.001, ["w"], 1)
            print(f"窗口前置：{顶级父窗口}")
            return _load_fallback_image()
        hdc = win32gui.GetWindowDC(句柄)
        mfc_dc = win32ui.CreateDCFromHandle(hdc)
        save_dc = mfc_dc.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(bitmap)
        if ctypes.windll.user32.PrintWindow(句柄, save_dc.GetSafeHdc(), 3):
            bitmap_bits = bitmap.GetBitmapBits(True)
            # 直接构造 BGR 矩阵（BGRX -> BGR）

            img_bgr = np.frombuffer(bitmap_bits, dtype=np.uint8).reshape(height, width, 4)[:, :, :3].copy()
            return img_bgr

        else:
            logger.error("PrintWindow调用失败")
            顶级父窗口 = 获取顶级父窗口句柄(句柄)
            pc端单击键盘无线程事件(顶级父窗口, 0.001, ["w"], 1)
            print(f"窗口前置：{顶级父窗口}")
            return _load_fallback_image()

    except Exception as e:
        logger.error(f"截图失败: {str(e)}")
        return _load_fallback_imageNumPy数组()
    finally:
        # 资源释放（保持不变）
        if bitmap: win32gui.DeleteObject(bitmap.GetHandle())
        if save_dc: save_dc.DeleteDC()
        if mfc_dc: mfc_dc.DeleteDC()
        if hdc: win32gui.ReleaseDC(句柄, hdc)
def 函数截图到内存(句柄, 矩形):
    """根据窗口信息进行截图并保存为无损PNG到内存"""
    #start_time = time.time()
    hdc = mfc_dc = save_dc = bitmap = None

    try:
        if not 句柄 or not 矩形:

            if 句柄:
                if 矩形 == 0:
                    矩形 = (0, 0, 1280, 720)#使用脚本要求分辨率
            else:
                logger.error(f"窗口信息未初始化")
                messagebox.showerror("错误", f"窗口信息未初始化,句柄:{句柄}，矩形：{矩形}")
                return _load_fallback_image()

        left, top, right, bottom = 矩形
        width = right - left
        height = bottom - top

        if not win32gui.IsWindowVisible(句柄):
            logger.error("目标窗口不可见")
            顶级父窗口 = 获取顶级父窗口句柄(句柄)
            pc端单击键盘无线程事件(顶级父窗口, 0.001, ["w"], 1)
            print(f"窗口前置：{顶级父窗口}")
            return _load_fallback_image()
        hdc = win32gui.GetWindowDC(句柄)
        mfc_dc = win32ui.CreateDCFromHandle(hdc)
        save_dc = mfc_dc.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(bitmap)
        if ctypes.windll.user32.PrintWindow(句柄, save_dc.GetSafeHdc(), 3):
            bitmap_bits = bitmap.GetBitmapBits(True)
            img = Image.frombuffer("RGB", (width, height), bitmap_bits, "raw", "BGRX", 0, 1)

            with io.BytesIO() as output:
                # 修改点：保存为无损PNG
                img.save(output, format="PNG", compress_level=0)
                #img.save(f"frame_.png")
                #print(f"窗口截图完成（无裁剪），总耗时：{time.time() - start_time:.2f}秒")

                return output.getvalue()

        else:
            logger.error("PrintWindow调用失败")
            顶级父窗口 = 获取顶级父窗口句柄(句柄)
            pc端单击键盘无线程事件(顶级父窗口, 0.001, ["w"], 1)
            print(f"窗口前置：{顶级父窗口}")
            return _load_fallback_image()

    except Exception as e:
        logger.error(f"截图失败: {str(e)}")
        return _load_fallback_image()
    finally:
        # 资源释放（保持不变）
        if bitmap: win32gui.DeleteObject(bitmap.GetHandle())
        if save_dc: save_dc.DeleteDC()
        if mfc_dc: mfc_dc.DeleteDC()
        if hdc: win32gui.ReleaseDC(句柄, hdc)
def 启动应用(adb_config, 包名):
    """通过包名启动应用"""
    adb路径, 端口,hwnd, 窗口矩形,(PC全局延迟,PC键盘延迟) = adb_config
    adb命令 = f'"{adb路径}" -s {端口} shell monkey -p {包名} -c android.intent.category.LAUNCHER 1'
    subprocess.run(adb命令, shell=True)
    logger.debug(f"启动游戏{包名}")
    time.sleep(3)
def 弹出提示图片():
    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent.absolute()
    else:
        current_dir = Path(__file__).parent.absolute()
    ds_path = current_dir / 'ds.json'
    # 若不存在，则向上回溯三级目录
    if not ds_path.exists():
        current_dir = current_dir.parent.parent.parent  # 三级回溯
    target_image_path=Path(rf"{current_dir}\图片\UI界面\战斗轴\新版本端口说明.png")
    os.startfile(target_image_path)
def 雷电命令(adb路径, 端口,命令):
    adb命令=f'"{adb路径}" adb --index {端口} --command "shell {命令}"'
    try:
        subprocess.run(adb命令, shell=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"[{端口}] ADB命令失败:{e}" )


def 雷电模拟器截图返回png数据(ldconsole_path,模拟器索引):
    """
       直接截取雷电模拟器画面到内存，无需保存到文件

       参数:
           ldconsole_path: ldconsole.exe的完整路径
           模拟器索引: 模拟器的索引号

       返回:
           bytes: PNG格式的图片数据
       """
    start_time = time.time()
    截图命令 = f'"{ldconsole_path}" adb --index {模拟器索引} --command "shell screencap -p /sdcard/screen.png"'
    subprocess.run(截图命令, shell=True, capture_output=True, text=True, check=True)


    # 拉取截图到本地
    拉取命令 = f'"{ldconsole_path}" adb --index {模拟器索引} --command "pull /sdcard/screen.png ./screen.png"'
    subprocess.run(拉取命令, shell=True, capture_output=True, text=True, check=True)

    with Image.open('screen.png') as image:
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        png数据 = buffer.getvalue()
        print(f"耗时：{time.time()-start_time}.2f")
        return png数据
def 获取_png_数据(adb_config,包名, x1=0, y1=0, x2=0, y2=0):
    """通过 ADB 截图并返回 PNG 字节数据"""
    adb路径, 端口,hwnd, 窗口矩形,(PC全局延迟,PC键盘延迟) = adb_config
    正确=False
    # 构建截图命令
    try:

        png_data = subprocess.check_output(
                [adb路径, '-s', 端口, 'exec-out', 'screencap', '-p'],
                stderr=subprocess.STDOUT,
                timeout=5  # 添加超时防止设备无响应
        )
        原始图片路径 = 'screen.png'
        with open(原始图片路径, 'wb') as f:
            f.write(png_data)
        with Image.open('screen.png') as image:
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            # 检查图片尺寸是否包含目标点
            width, height = image.size
            if 1279 >= width or 719 >= height:
                logger.warning(
                    f"截图尺寸({width}x{height})不包含目标点(1279,719)，猜测应该是游戏未启动，现在尝试打开游戏")
                命令 = f"monkey -p {包名} -c android.intent.category.LAUNCHER 1"

                启动应用(adb_config, 包名)
                time.sleep(3)
        正确 = True
    except subprocess.CalledProcessError as e:
        弹出提示图片()
        messagebox.showerror("错误", f"ADB命令执行失败,端口不可用，请在脚本主界面更换端口，或者尝试重启电脑")
        messagebox.showerror("错误", f"错误信息：{e}")
        正确 = False
    except Exception as e:
        弹出提示图片()
        messagebox.showerror("错误", f"获取截图时发生错误,端口不可用，请在脚本主界面更换端口，或者尝试重启电脑")
        messagebox.showerror("错误", f"错误信息：{e}")
        正确 = False
    return 正确


    if x1 == 0 and y1 == 0 and x2 == 0 and y2 == 0:
        adb命令 = f'"{adb路径}" -s {端口} shell screencap -p /sdcard/screen.png'
    else:
        adb命令 = f'"{adb路径}" -s {端口} shell screencap -p /sdcard/screen.png | "{adb路径}" -s {端口} shell crop {x1} {y1} {x2} {y2}'

    try:
        # 执行截图命令
        adb命令 = f'"{adb路径}" -s {端口} shell screencap -p /sdcard/screen.png'
        subprocess.run(adb命令, shell=True, capture_output=True, check=True)

        # 拉取截图到本地
        pull命令 = f'"{adb路径}" -s {端口} pull /sdcard/screen.png ./screen.png'
        subprocess.run(pull命令, shell=True, capture_output=True, check=True)

        # 读取并转换图片

        with Image.open('screen.png') as image:
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            png数据 = buffer.getvalue()

            # 检查图片尺寸是否包含目标点
            width, height = image.size
            if 1279 >= width or 719 >= height:
                logger.warning(f"截图尺寸({width}x{height})不包含目标点(1279,719)，猜测应该是游戏未启动，现在尝试打开游戏")
                命令 = f"monkey -p {包名} -c android.intent.category.LAUNCHER 1"
                if "ld.exe" in str(adb路径):
                    雷电命令(adb路径, 端口, 命令)
                else:
                    启动应用(adb_config, 包名)
                time.sleep(3)
        正确 = True
    except subprocess.CalledProcessError as e:
        弹出提示图片()
        messagebox.showerror("错误", f"ADB命令执行失败,端口不可用，请在脚本主界面更换端口，或者尝试重启电脑")
        messagebox.showerror("错误", f"错误信息：{e}")
        正确 = False
    except Exception as e:
        弹出提示图片()
        messagebox.showerror("错误", f"获取截图时发生错误,端口不可用，请在脚本主界面更换端口，或者尝试重启电脑")
        messagebox.showerror("错误", f"错误信息：{e}")
        正确 = False
    return 正确

# ======================== 核心截图函数 ========================
def 获取_png_data(adb_config, x1=0, y1=0, x2=0, y2=0):
    """通过 ADB 截图并返回 PNG 字节数据（优化版）"""

    adb路径, 端口,hwnd, 窗口矩形,(PC全局延迟,PC键盘延迟)= adb_config

    png_data = None
    if hwnd:
        return 函数截图到内存(hwnd,窗口矩形)
    start_time = time.time()
    try:

        png_data = subprocess.check_output(
                [adb路径, '-s', 端口, 'exec-out', 'screencap', '-p'],
                stderr=subprocess.STDOUT,
                timeout=10  # 添加超时防止设备无响应
        )
        return png_data
    except subprocess.CalledProcessError as e:
        messagebox.showerror("ADB错误", "命令执行失败，请检查设备连接")
        messagebox.showerror("详细信息", f"错误输出：{e.output.decode('utf-8', 'ignore')}")
        print(f"截图时发生异常：{str(e)}")
        return _load_fallback_image()
    except subprocess.TimeoutExpired:
        print("超时错误，设备在5秒内未响应截图请求，等待10秒后继续截图")
        time.sleep(10)
        return _load_fallback_image()
    except Exception as e:
        messagebox.showerror("未知错误", f"截图时发生异常：{str(e)}")
        print(f"截图时发生异常：{str(e)}")
        return _load_fallback_image()



def _load_fallback_imageNumPy数组():
    """
    备用图像加载（返回与正常截图一致的 BGR NumPy 数组）
    若无法加载，则生成 1280x720 黑色图片
    """
    try:
        # 确定图片路径
        if getattr(sys, 'frozen', False):
            current_dir = Path(sys.executable).parent.absolute()
        else:
            current_dir = Path(__file__).parent.absolute()
        path = Path(rf"{current_dir}\UI\端口相关\端口不可用或未连接.png")

        if not path.exists():
            raise FileNotFoundError(f"备用图片不存在: {path}")

        # 用 PIL 读取，并转为 BGR NumPy 数组
        pil_img = Image.open(path).convert('RGB')
        img_rgb = np.array(pil_img)                # shape (H, W, 3), dtype uint8, RGB 顺序
        img_bgr = img_rgb[:, :, ::-1].copy()       # 转为 BGR
        return img_bgr

    except FileNotFoundError as e:
        logger.error(str(e))
        messagebox.showerror("备用文件缺失", f"未找到备用截图文件：{path}")
    except Exception as e:
        logger.error(f"加载备用图像失败: {str(e)}")
        messagebox.showerror("备用加载失败", f"加载备用图像时出错：{str(e)}")

    # 所有异常情况统一返回 1280x720 的黑色 BGR 图像
    logger.warning("使用 1280x720 黑色图像作为最终备用")
    return np.zeros((720, 1280, 3), dtype=np.uint8)
def _load_fallback_image():
    """备用图像加载（保持与原逻辑一致）"""
    try:
        if getattr(sys, 'frozen', False):
            current_dir = Path(sys.executable).parent.absolute()
        else:
            current_dir = Path(__file__).parent.absolute()
        路径=Path(rf"{current_dir}\UI\端口相关\端口不可用或未连接.png")
        with Image.open(路径) as image:
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
    except FileNotFoundError:
        messagebox.showerror("备用文件缺失", "未找到screen.png备用截图文件")
        return b''
    except Exception as e:
        messagebox.showerror("备用加载失败", f"加载备用图像时出错：{str(e)}")
        return b''

def 获取图片_png_data(adb_config, x1=0, y1=0, x2=0, y2=0):
    """通过 ADB 截图并返回 PNG 字节数据"""
    adb路径, 端口,hwnd, 窗口矩形,(PC全局延迟,PC键盘延迟) = adb_config

    # 构建截图命令
    if x1 == 0 and y1 == 0 and x2 == 0 and y2 == 0:
        adb命令 = f'"{adb路径}" -s {端口} shell screencap -p /sdcard/screen.png'
    else:
        adb命令 = f'"{adb路径}" -s {端口} shell screencap -p /sdcard/screen.png | "{adb路径}" -s {端口} shell crop {x1} {y1} {x2} {y2}'

    try:
        # 执行截图命令
        subprocess.run(adb命令, shell=True, capture_output=True, check=True)

        # 拉取截图到本地
        pull命令 = f'"{adb路径}" -s {端口} pull /sdcard/screen.png ./screen.png'
        subprocess.run(pull命令, shell=True, capture_output=True, check=True)
        # 读取并转换图片
        with Image.open('screen.png') as image:
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()

    except subprocess.CalledProcessError as e:
        logger.debug(f"ADB命令执行失败,端口不可用，请在脚本主界面更换端口，或者尝试重启电脑")
        logger.debug(f"错误信息：{e}")
    except Exception as e:
        logger.debug("错误,获取截图时发生错误,端口不可用，请在脚本主界面更换端口，或者尝试重启电脑")
        logger.debug(f"错误信息：{e}")
    return False


# ======================== 分辨率检查函数 ========================
def check_resolution(adb_config):
    """通过 ADB 截图并返回 PNG 字节数据"""
    adb路径, 端口, hwnd, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb_config
    正确 = False
    # 构建截图命令
    if 窗口矩形:
        x, y = (1280,720)
        a, b, c, d = 窗口矩形
        宽度 = c - a
        高度 = d - b


        if 宽度 == x and 高度 == y:
            logger.debug("分辨率正确101")
            return  True
        else:
            错误信息 = f"游戏现在分辨率为: {宽度}x{高度}"
            logger.debug(错误信息)
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
            return False


    try:

        png_data = subprocess.check_output(
                [adb路径, '-s', 端口, 'exec-out', 'screencap', '-p'],
                stderr=subprocess.STDOUT,
                timeout=5  # 添加超时防止设备无响应
        )
        原始图片路径 = 'screen.png'
        with open(原始图片路径, 'wb') as f:
            f.write(png_data)
        with Image.open('screen.png') as image:
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            # 检查图片尺寸是否包含目标点
            width, height = image.size
            if int(width) in [1280,720]:
                if int(width)*int(height)==1280*720:
                    return True
            messagebox.showerror(f"分辨率错误",
                                 f"要求分辨率为{1280}*{720}，"
                                 f"\n请自行调整游戏或者模拟器分辨率")
            return False


    except subprocess.CalledProcessError as e:
        弹出提示图片()
        messagebox.showerror("错误", f"ADB命令执行失败,端口不可用，请在脚本主界面更换端口，或者尝试重启电脑")
        messagebox.showerror("错误", f"错误信息：{e}")

    except Exception as e:
        弹出提示图片()
        messagebox.showerror("错误", f"获取截图时发生错误,端口不可用，请在脚本主界面更换端口，或者尝试重启电脑")
        messagebox.showerror("错误", f"错误信息：{e}")




# ======================== 文件保存函数 ========================
def 保存截图文件(adb_config, x1=0, y1=0, x2=0, y2=0, 文件名='领取奖励记录.png'):
    """保存截图到文件"""
    try:
        png_data = 获取_png_data(adb_config, x1, y1, x2, y2)
        with open(文件名, 'wb') as f:
            f.write(png_data)
        logger.info(f"截图已保存至: {Path(文件名).resolve()}")
        return True
    except Exception as e:
        logger.error(f"保存失败: {e}")
        return False


# ======================== 主程序 ========================
if __name__ == "__main__":
    # 假设连接adb模块已返回 (adb路径, 端口) 元组

    目标窗口标题 = "MuMu模拟器12"
    句柄 = win32gui.FindWindow(None, 目标窗口标题)
    # 句柄 =1706984
    print(句柄)
    截图区域 = (0, 0, 1280, 720)  # 根据实际情况调整
    start = time.time()
    for _ in range(100):  # 模拟高频截图

        函数截图到内存(句柄, 截图区域)

    print(f"平均帧率: {100 / (time.time() - start):.2f} FPS")
