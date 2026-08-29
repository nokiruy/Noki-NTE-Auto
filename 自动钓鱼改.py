import sys
import os
import ctypes

def 是否管理员():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not 是否管理员():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join([f'"{arg}"' for arg in sys.argv]), None, 1)
    sys.exit(0)

import json
import numpy as np
import win32gui
import win32con
from windows_capture import WindowsCapture, Frame, InternalCaptureControl

键_A = 0x41
键_D = 0x44
消息_激活 = win32con.WM_ACTIVATE
激活状态_活动 = 1
容差 = 5

def 窗口假激活(窗口句柄):
    win32gui.SendMessage(窗口句柄, 消息_激活, 激活状态_活动, 0)

def 按键按下(窗口句柄, 虚拟键):
    win32gui.PostMessage(窗口句柄, win32con.WM_KEYDOWN, 虚拟键, 0)

def 按键抬起(窗口句柄, 虚拟键):
    win32gui.PostMessage(窗口句柄, win32con.WM_KEYUP, 虚拟键, 0)

def 查找游戏窗口():
    候选窗口 = []
    def 回调函数(窗口句柄, _):
        标题 = win32gui.GetWindowText(窗口句柄)
        类名 = win32gui.GetClassName(窗口句柄)
        矩形 = win32gui.GetClientRect(窗口句柄)
        宽, 高 = 矩形[2], 矩形[3]
        if 宽 > 100 and 高 > 100:
            if "UnrealWindow" in 类名:
                print(f"  候选: 窗口句柄={窗口句柄} 类名={类名} 标题=[{标题}] 大小={宽}x{高}")
                候选窗口.append((窗口句柄, 宽 * 高))
        return True
    win32gui.EnumWindows(回调函数, None)
    if 候选窗口:
        候选窗口.sort(key=lambda x: -x[1])
        return 候选窗口[0][0]
    return None

def 加载颜色(路径):
    with open(路径, 'r', encoding='utf-8') as f:
        数据 = json.load(f)
    return np.array([项目["rgb"] for 项目 in 数据 if sum(项目["rgb"]) > 100], dtype=np.int16)

def 匹配掩码(图像_红绿蓝, 颜色集):
    图像 = 图像_红绿蓝.astype(np.int16)
    掩码 = np.zeros(图像.shape[:2], dtype=bool)
    for 颜色 in 颜色集:
        匹配结果 = np.all(np.abs(图像 - 颜色) <= 容差, axis=2)
        掩码 |= 匹配结果
    return 掩码

def 查找钓条(图像_红绿蓝, 区域颜色, 光标颜色):
    粗略掩码 = (图像_红绿蓝[:,:,0] > 25) & (图像_红绿蓝[:,:,0] < 60) & \
                 (图像_红绿蓝[:,:,1] > 180) & (图像_红绿蓝[:,:,1] < 235) & \
                 (图像_红绿蓝[:,:,2] > 165) & (图像_红绿蓝[:,:,2] < 205)

    行有 = 粗略掩码.any(axis=1)
    候选行 = -1
    最佳计数 = 0
    for 行 in np.where(行有)[0]:
        横坐标 = np.where(粗略掩码[行])[0]
        if len(横坐标) < 5:
            continue
        跨度 = int(横坐标[-1] - 横坐标[0])
        if 跨度 <= 250 and len(横坐标) > 最佳计数:
            最佳计数 = len(横坐标)
            候选行 = 行

    if 候选行 < 0:
        return None

    上边界 = max(0, 候选行 - 10)
    下边界 = min(图像_红绿蓝.shape[0], 候选行 + 10)
    带 = 图像_红绿蓝[上边界:下边界]

    区域掩码 = 匹配掩码(带, 区域颜色)
    绿区横坐标 = np.where(区域掩码.any(axis=0))[0]
    if len(绿区横坐标) < 5:
        return None
    区域最小 = int(绿区横坐标.min())
    区域最大 = int(绿区横坐标.max())
    if 区域最大 - 区域最小 > 250:
        return None

    光标掩码 = 匹配掩码(带, 光标颜色)
    列和 = 光标掩码.sum(axis=0)
    if 列和.max() < 2:
        return None
    光标横坐标 = int(np.argmax(列和))

    区域中心 = (区域最小 + 区域最大) // 2
    return 光标横坐标, 区域最小, 区域最大, 区域中心
import time
if __name__ == "__main__":
  try:
    脚本目录 = os.path.dirname(os.path.abspath(sys.argv[0]))
    区域颜色 = 加载颜色(os.path.join(脚本目录,"异环图片" ,"钓鱼" , "鱼的框_colors.json"))
    光标颜色 = 加载颜色(os.path.join(脚本目录,"异环图片" ,"钓鱼" , "钓鱼的框_colors.json"))
    print(f"加载颜色: 绿区{len(区域颜色)}种, 光标{len(光标颜色)}种")

    窗口句柄 = 查找游戏窗口()
    if not 窗口句柄:
        print("未找到异环窗口")
        input("按回车键退出...")
        sys.exit(1)

    print(f"找到窗口: {窗口句柄} [{win32gui.GetWindowText(窗口句柄)}]")
    if win32gui.IsIconic(窗口句柄):
        win32gui.ShowWindow(窗口句柄, win32con.SW_RESTORE)

        time.sleep(0.5)
    print("开始运行... (Ctrl+C 退出)")
    窗口假激活(窗口句柄)

    当前按键 = [None]
    帧计数 = [0]

    捕获 = WindowsCapture(cursor_capture=False, draw_border=False, window_hwnd=窗口句柄)

    @捕获.event
    def on_frame_arrived(帧: Frame, 捕获控制: InternalCaptureControl):  # 必须用这个英文名
        try:
            帧计数[0] += 1
            图像 = 帧.frame_buffer
            高 = 图像.shape[0]
            print(高)
            顶部区域 = 图像[:高 // 4, :, 2::-1]
            开始时间=time.time()
            结果 = 查找钓条(顶部区域, 区域颜色, 光标颜色)
            print(time.time()-开始时间)
            if 结果 is None:
                if 帧计数[0] % 60 == 0:
                    print(f"帧{帧计数[0]}: 未检测到钓鱼条")
                if 当前按键[0]:
                    按键抬起(窗口句柄, 当前按键[0])
                    当前按键[0] = None
                return

            光标横坐标, 区域最小, 区域最大, 区域中心 = 结果

            if 帧计数[0] % 60 == 0:
                print(f"光标:{光标横坐标} 绿区:{区域最小}-{区域最大}(中{区域中心})")

            if 光标横坐标 < 区域中心 - 10:
                if 当前按键[0] == 键_A:
                    按键抬起(窗口句柄, 键_A)
                if 当前按键[0] != 键_D:
                    按键按下(窗口句柄, 键_D)
                    当前按键[0] = 键_D
            elif 光标横坐标 > 区域中心 + 10:
                if 当前按键[0] == 键_D:
                    按键抬起(窗口句柄, 键_D)
                if 当前按键[0] != 键_A:
                    按键按下(窗口句柄, 键_A)
                    当前按键[0] = 键_A
            else:
                if 当前按键[0]:
                    按键抬起(窗口句柄, 当前按键[0])
                    当前按键[0] = None
        except Exception as e:
            print(f"回调错误: {e}")

    @捕获.event
    def on_closed():  # 必须用这个英文名
        pass

    try:
        捕获.start()
    except KeyboardInterrupt:
        pass
    finally:
        if 当前按键[0]:
            按键抬起(窗口句柄, 当前按键[0])
    print("已停止")
  except Exception as e:
    import traceback
    traceback.print_exc()
    input("按回车键退出...")