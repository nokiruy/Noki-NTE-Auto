import win32gui
import win32con
import win32api
import time



vk_code字典 = {
    # 字母键 (A-Z)
    "a": 0x41, "b": 0x42, "c": 0x43, "d": 0x44, "e": 0x45,
    "f": 0x46, "g": 0x47, "h": 0x48, "i": 0x49, "j": 0x4A,
    "k": 0x4B, "l": 0x4C, "m": 0x4D, "n": 0x4E, "o": 0x4F,
    "p": 0x50, "q": 0x51, "r": 0x52, "s": 0x53, "t": 0x54,
    "u": 0x55, "v": 0x56, "w": 0x57, "x": 0x58, "y": 0x59,
    "z": 0x5A,

    # 功能键 (F1-F12)
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73,
    "f5": 0x74, "f6": 0x75, "f7": 0x76, "f8": 0x77,
    "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,

    # Shift键 (左右Shift)
    "shift": 0x10,  # 通用Shift键
    "shift_left": 0xA0,  # 左Shift键
    "shift_right": 0xA1,  # 右Shift键

    # Ctrl键 (左右Ctrl)
    "ctrl": 0x11,  # 通用Ctrl键
    "ctrl_left": 0xA2,  # 左Ctrl键
    "ctrl_right": 0xA3,  # 右Ctrl键

    # Alt键 (左右Alt)
    "alt": 0x12,  # 通用Alt键
    "alt_left": 0xA4,  # 左Alt键
    "alt_right": 0xA5,  # 右Alt键

    # 其他常用键（可根据需要添加）
    "space": 0x20,  # 空格键
    "enter": 0x0D,  # 回车键
    "esc": 0x1B,  # ESC键
    "backspace": 0x08,  # 退格键
    "tab": 0x09,  # Tab键
    "capslock": 0x14,  # Caps Lock键
    "windows_left": 0x5B,  # 左Windows键
    "windows_right": 0x5C  # 右Windows键
}
def 模拟按键按下(游戏句柄, 按键名):
    try:

        vk_code = vk_code字典[按键名]
        win32gui.PostMessage(游戏句柄, win32con.WM_KEYDOWN, vk_code, 0)
    except Exception as e:
        print(f"模拟按键按下出现错误，详情：{e}")


# 模拟按键弹起
def 模拟按键弹起(游戏句柄, 按键名):
    try:
        vk_code = vk_code字典[按键名]
        win32gui.PostMessage(游戏句柄, win32con.WM_KEYUP, vk_code, 0)
    except Exception as e:
        print(f"模拟按键弹起出现错误，详情：{e}")


def 模拟按键按下弹起(游戏句柄, 按键名,延时1=0.001,延时2=0.001):
    try:
        vk_code = vk_code字典[按键名]
        win32gui.PostMessage(游戏句柄, win32con.WM_KEYDOWN, vk_code, 0)
        time.sleep(延时1)
        win32gui.PostMessage(游戏句柄, win32con.WM_KEYUP, vk_code, 0)
        time.sleep(延时2)
    except Exception as e:
        print(f"模拟按键按下弹起出现错误，详情：{e}")


if __name__ == "__main__":
    游戏句柄=2561366
    for 键,值 in vk_code字典.items():
        模拟按键按下弹起(游戏句柄, 键, 延时1=0.001, 延时2=0.001)