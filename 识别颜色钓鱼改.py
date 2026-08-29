import sys
import os
import ctypes
import json
import time
import numpy as np
import cv2
import win32gui
import win32con
import win32ui





def 窗口假激活(窗口句柄):
    win32gui.SendMessage(窗口句柄,  win32con.WM_ACTIVATE, 1, 0)


def 按键按下(窗口句柄, 虚拟键):
    win32gui.PostMessage(窗口句柄, win32con.WM_KEYDOWN, 虚拟键, 0)


def 按键抬起(窗口句柄, 虚拟键):
    win32gui.PostMessage(窗口句柄, win32con.WM_KEYUP, 虚拟键, 0)


# ---------- 窗口矩形更新 ----------
def _update_window_rect(游戏句柄):
    """更新窗口客户区矩形（屏幕坐标）"""
    for i in range(6):
        client_rect = win32gui.GetClientRect(游戏句柄)
        left, top = win32gui.ClientToScreen(游戏句柄, (client_rect[0], client_rect[1]))
        right, bottom = win32gui.ClientToScreen(游戏句柄, (client_rect[2], client_rect[3]))
        窗口矩形 = (left, top, right, bottom)
        if right - left < 10:
            # 窗口可能最小化或未激活，尝试激活
            win32gui.ShowWindow(游戏句柄, win32con.SW_RESTORE)
            time.sleep(1)
        else:
            break
        time.sleep(1)
    else:
        窗口矩形 = None
    return 窗口矩形


def 函数精确查找窗口句柄(目标窗口类名, 默认目标窗口标题):
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # 系统级DPI感知
    """精确查找目标窗口句柄，返回 (句柄, 矩形)"""
    游戏句柄 = win32gui.FindWindow(目标窗口类名, 默认目标窗口标题)
    if 游戏句柄:
        窗口矩形 = _update_window_rect(游戏句柄)
        print(f"找到目标窗口：句柄={游戏句柄}, 矩形={窗口矩形}")
        return 游戏句柄, 窗口矩形
    return None, None


# ---------- 截图函数（返回BGR图像，OpenCV格式） ----------
def 自动钓鱼改函数截图到内存(句柄, 矩形):
    """
    根据窗口句柄和矩形（屏幕坐标 left,top,right,bottom）截图，
    返回 BGR 格式的 numpy 数组（形状 H,W,3），失败返回 None。
    """
    if not 句柄 or not 矩形:
        return None
    left, top, right, bottom = 矩形
    width = right - left
    height = bottom - top
    if width <= 0 or height <= 0:
        return None

    # 确保窗口存在且可见
    if not win32gui.IsWindowVisible(句柄):
        print("窗口不可见")
        return None

    hdc = win32gui.GetWindowDC(句柄)
    mfc_dc = win32ui.CreateDCFromHandle(hdc)
    save_dc = mfc_dc.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(bitmap)

    try:
        # PrintWindow 参数 3 = PW_CLIENTONLY，只截客户区
        if not ctypes.windll.user32.PrintWindow(句柄, save_dc.GetSafeHdc(), 3):
            print("PrintWindow调用失败")
            return None
        bitmap_bits = bitmap.GetBitmapBits(True)
        # 位图格式为 BGRX（4 通道），转为 BGR 去掉 alpha
        img_array = np.frombuffer(bitmap_bits, dtype=np.uint8).reshape(height, width, 4)
        img_bgr = img_array[:, :, :3]  # BGR 顺序
        return img_bgr
    except Exception as e:
        print(f"截图异常: {e}")
        return None
    finally:
        win32gui.DeleteObject(bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(句柄, hdc)


# ---------- 颜色匹配（改用 OpenCV） ----------
容差 = 5


def 加载颜色(路径):
    """
    从 JSON 加载颜色，RGB 转为 BGR，返回 numpy 数组，形状 (N,3)
    """
    with open(路径, 'r', encoding='utf-8') as f:
        数据 = json.load(f)
    # 只取 sum(rgb)>100 的有效颜色，并将 RGB -> BGR
    颜色列表 = []
    for 项目 in 数据:
        r, g, b = 项目["rgb"]
        if (r + g + b) > 100:
            颜色列表.append((b, g, r))  # 转为 BGR 顺序
    return np.array(颜色列表, dtype=np.uint8)


def 匹配掩码(图像_bgr, 颜色集):
    """
    图像_bgr: H,W,3 BGR 图像
    颜色集: (N,3) BGR 颜色
    返回: 二值掩码 (H,W) dtype=uint8 (0/255)
    """
    if 颜色集 is None or len(颜色集) == 0:
        return np.zeros(图像_bgr.shape[:2], dtype=np.uint8)

    掩码 = np.zeros(图像_bgr.shape[:2], dtype=np.uint8)
    for 颜色 in 颜色集:
        lower = np.clip(颜色.astype(np.int16) - 容差, 0, 255).astype(np.uint8)
        upper = np.clip(颜色.astype(np.int16) + 容差, 0, 255).astype(np.uint8)
        m = cv2.inRange(图像_bgr, lower, upper)
        掩码 = cv2.bitwise_or(掩码, m)
    return 掩码


def 查找钓条(图像_bgr, 区域颜色, 光标颜色):

    """
    图像_bgr: BGR格式 (H,W,3)
    返回 (光标横坐标, 区域最小, 区域最大, 区域中心) 或 None
    """
    # 粗略掩码：原 RGB 阈值 (R:25-60, G:180-235, B:165-205) 转 BGR
    匹配结果=光标横坐标=区域最小=区域最大=0
    lower_rough = np.array([165, 180, 25], dtype=np.uint8)
    upper_rough = np.array([205, 235, 60], dtype=np.uint8)
    粗略掩码 = cv2.inRange(图像_bgr, lower_rough, upper_rough)

    # 寻找含目标像素最多的行
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
        return 匹配结果,光标横坐标, 区域最小, 区域最大

    # 截取候选行附近区域
    上边界 = max(0, 候选行 - 10)
    下边界 = min(图像_bgr.shape[0], 候选行 + 10)
    带 = 图像_bgr[上边界:下边界]

    # 区域掩码
    区域掩码 = 匹配掩码(带, 区域颜色)
    绿区横坐标 = np.where(区域掩码.any(axis=0))[0]
    if len(绿区横坐标) < 5:
        return 匹配结果,光标横坐标, 区域最小, 区域最大
    区域最小 = int(绿区横坐标.min())
    区域最大 = int(绿区横坐标.max())
    if 区域最大 - 区域最小 > 250:
        return 匹配结果,光标横坐标, 区域最小, 区域最大

    # 光标掩码
    光标掩码 = 匹配掩码(带, 光标颜色)
    列和 = 光标掩码.sum(axis=0)
    if 列和.max() < 2:
        return 匹配结果,光标横坐标, 区域最小, 区域最大
    光标横坐标 = int(np.argmax(列和))
    匹配结果=True
    return 匹配结果,光标横坐标, 区域最小, 区域最大

def 识别颜色钓鱼匹配函数(current_dir, 图像):
    开始时间 = time.time()
    # 第一次调用时加载颜色并缓存为函数属性
    if not hasattr(识别颜色钓鱼匹配函数, '区域颜色'):
        区域颜色路径 = current_dir / "异环图片" / "钓鱼" / "鱼的框_colors.json"
        光标颜色路径 = current_dir / "异环图片" / "钓鱼" / "钓鱼的框_colors.json"
        识别颜色钓鱼匹配函数.区域颜色 = 加载颜色(str(区域颜色路径))
        识别颜色钓鱼匹配函数.光标颜色 = 加载颜色(str(光标颜色路径))
        print(f"加载颜色: 绿区{len(识别颜色钓鱼匹配函数.区域颜色)}种, 光标{len(识别颜色钓鱼匹配函数.光标颜色)}种")

    高 = 图像.shape[0]
    顶部区域 = 图像[:高 // 4, :, :]


    匹配结果, 光标横坐标, 区域最小, 区域最大 = 查找钓条(
        顶部区域,
        识别颜色钓鱼匹配函数.区域颜色,
        识别颜色钓鱼匹配函数.光标颜色
    )
    print(f"匹配结果：{匹配结果},光标横坐标：{光标横坐标}, 区域最小：{区域最小}, 区域最大：{区域最大}，耗时：{(time.time() - 开始时间):.4f}秒 ")
    return 匹配结果, 光标横坐标, 区域最小, 区域最大
# ---------- 主程序 ----------
if __name__ == "__main__":
    # ---------- 窗口与按键辅助 ----------
    键_A = 0x41
    键_D = 0x44
    try:
        # 加载颜色配置（内部转为 BGR）
        import sys
        from pathlib import Path
        if getattr(sys, 'frozen', False):
            current_dir = Path(sys.executable).parent.absolute()
        else:
            current_dir = Path(__file__).parent.absolute()

        # 加载颜色（实际路径：外置配置文件夹/异环图片/钓鱼/...）


        # 精确查找窗口
        目标类名 = "UnrealWindow"
        目标标题 = ""
        窗口句柄, 窗口矩形 = 函数精确查找窗口句柄(目标类名, 目标标题)

        if not 窗口句柄 or not 窗口矩形:
            print("未找到目标窗口，尝试枚举所有UnrealWindow...")


            def enum_cb(hwnd, _):
                if "UnrealWindow" in win32gui.GetClassName(hwnd):
                    rect = _update_window_rect(hwnd)
                    if rect:
                        candidates.append((hwnd, rect, (rect[2] - rect[0]) * (rect[3] - rect[1])))
                return True


            candidates = []
            win32gui.EnumWindows(enum_cb, None)
            if candidates:
                candidates.sort(key=lambda x: -x[2])
                窗口句柄, 窗口矩形, _ = candidates[0]
                print(f"枚举找到窗口: {窗口句柄}, 矩形={窗口矩形}")
            else:
                print("未找到任何UnrealWindow窗口")
                input("按回车键退出...")
                sys.exit(1)

        if win32gui.IsIconic(窗口句柄):
            win32gui.ShowWindow(窗口句柄, win32con.SW_RESTORE)
            time.sleep(0.5)

        窗口假激活(窗口句柄)
        print("开始运行... (Ctrl+C 退出)")

        识别间隔 = 0.05
        当前按键 = None

        while True:
            time.sleep(0.05)
            图像 = 自动钓鱼改函数截图到内存(窗口句柄, 窗口矩形)  # 现在返回 BGR
            if 图像 is None:
                print("截图失败，尝试恢复窗口...")
                win32gui.ShowWindow(窗口句柄, win32con.SW_RESTORE)
                time.sleep(0.5)
                continue

            匹配结果, 光标横坐标, 区域最小, 区域最大=识别颜色钓鱼匹配函数(current_dir,图像)
            if 匹配结果:
                if 当前按键:
                    按键抬起(窗口句柄, 当前按键)
                    当前按键 = None
                # 控制逻辑：光标在绿区外才移动，否则停止
                if 光标横坐标 < 区域最小:
                    if 当前按键 == 键_A:
                        按键抬起(窗口句柄, 键_A)
                    if 当前按键 != 键_D:
                        按键按下(窗口句柄, 键_D)
                        当前按键 = 键_D
                elif 光标横坐标 > 区域最大:
                    if 当前按键 == 键_D:
                        按键抬起(窗口句柄, 键_D)
                    if 当前按键 != 键_A:
                        按键按下(窗口句柄, 键_A)
                        当前按键 = 键_A
                else:
                    if 当前按键:
                        按键抬起(窗口句柄, 当前按键)
                        当前按键 = None

    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        import traceback

        traceback.print_exc()
    finally:
        if '当前按键' in locals() and 当前按键:
            按键抬起(窗口句柄, 当前按键)
        print("已停止")
        input("按回车键退出...")