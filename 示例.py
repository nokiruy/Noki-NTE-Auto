
if __name__ == "__main__":
    import sys
    from pathlib import Path

    import ctypes
    from ctypes import wintypes


    def get_window_handle(class_name: str = None, window_title: str = None):
        """
        根据类名和/或窗口标题获取窗口句柄。
        参数为 None 时表示不限制该条件。
        返回窗口句柄（整数），若未找到返回 None。
        """
        user32 = ctypes.windll.user32
        user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
        user32.FindWindowW.restype = wintypes.HWND

        hwnd = user32.FindWindowW(class_name, window_title)
        if hwnd == 0:
            return None
        return hwnd
    import time
    hwnd=get_window_handle("UnrealWindow","异环  ")
    from 后台键盘鼠标 import fake_activate_window,simulate_key_press_hold
    from 异环半后台鼠标点击 import 真实鼠标传递坐标后台点击
    fake_activate_window(hwnd)
    真实鼠标传递坐标后台点击(hwnd, (0,0,1280,720), (640,500), 0.05, 0.05)
    time.sleep(1)
    simulate_key_press_hold(hwnd, 0x46, 0.05)
    from 后台截图 import 函数截图到内存
    png数据=函数截图到内存(hwnd, 0)
    from opencv识图 import 函数_在指定区域内进行模板匹配

    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent.absolute()
    else:
        current_dir = Path(__file__).parent.absolute()
    result =函数_在指定区域内进行模板匹配(png数据, (10,10,600,300), current_dir/"滑块.png", 0.8)
    if result[0]:
        print("找到图片")
    else:
        print("未找到图片")

