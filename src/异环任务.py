import io
import json

from 游戏截图保存到内存 import 获取_png_data,函数截图到内存直接返回NumPy数组

from 窗口假激活 import 窗口假激活

from opencv模板匹配找图 import 函数_在指定区域内进行模板匹配,  函数_在指定区域数组匹配,函数_在指定区域内进行模板匹配返回横坐标范围,函数_在指定区域内进行模板匹配_多目标,根据模版路径返回配置元组

import time
import threading
import logging
import win32gui
import win32con
import win32api
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
from pathlib import Path
logger = logging.getLogger("database")
from 后台键鼠 import 真实鼠标坐标后台点击专用, PyAutoGUI_模拟按键按下, PyAutoGUI_模拟按键弹起, 模拟按键按下, 模拟按键弹起, 模拟按键长按, 模拟按键点击, 模拟鼠标左键长按, 模拟鼠标中键点击, PyAutoGUI_模拟鼠标左键单击, 前台模拟鼠标左键单击绑定窗口
from 睡眠倍数模块 import 可变速等待

from 后台点击再次封装 import 持续x除以y秒按键一个图片并且失败增加时长, 持续x除以y秒点击一个图片并且失败增加时长, 持续x除以y秒按键到图出现, 持续x除以y秒图未出现则点击一个位置, 持续x除以y秒图存在则点击一个位置


import random
def random_non_negative(base: float, range_val: float) -> float:
    """
    生成一个基于原始值的随机非负数

    参数:
        base: 原始数值（浮点数）
        range_val: 随机正负范围（非负数）

    返回:
        在[base - range_val, base + range_val]区间内均匀分布的随机数，
        若结果小于0则返回0.0
    """
    # 生成区间内的随机数

    rand_val = random.uniform(base - range_val, base + range_val)
    # 确保结果非负
    return rand_val if rand_val >= 0 else 0.0
KEY_MAP = {
    'esc': 27, 'escape': 27,
    'f1': 112, 'f2': 113, 'f3': 114, 'f4': 115,
    'f5': 116, 'f6': 117, 'f7': 118, 'f8': 119,
    'f9': 120, 'f10': 121, 'f11': 122, 'f12': 123,
    'printscreen': 44, 'prtsc': 44, '打印屏幕': 44,
    'scrolllock': 145, '滚动锁定': 145,
    'pause': 19, 'break': 19, '暂停': 19,
    '`': 192, '~': 192, '波浪线': 192,
    '1': 49, '!': 49, '2': 50, '@': 50, '3': 51, '#': 51, '4': 52, '$': 52,
    '5': 53, '%': 53, '6': 54, '^': 54, '7': 55, '&': 55, '8': 56, '*': 56,
    '9': 57, '(': 57, '0': 48, ')': 48,
    '-': 189, '_': 189, '减号': 189, '=': 187, '+': 187, '加号': 187,
    'backspace': 8, '退格': 8, '删除': 8,
    'tab': 9,
    '[': 219, '{': 219, '左方括号': 219, ']': 221, '}': 221, '右方括号': 221,
    '\\': 220, '|': 220, '反斜杠': 220,
    'capslock': 20, '大写锁定': 20, '大写': 20,
    ';': 186, ':': 186, '分号': 186, "'": 222, '"': 222, '单引号': 222,
    'enter': 13, '回车': 13, '换行': 13,
    'shift': 160, '左shift': 160, 'leftshift': 160,
    '右shift': 161, 'rightshift': 161,
    'ctrl': 162, '左ctrl': 162, '左control': 162, 'leftctrl': 162,
    '右ctrl': 163, '右control': 163, 'rightctrl': 163,
    'alt': 164, '左alt': 164, 'leftalt': 164, '右alt': 165, 'rightalt': 165,
    'win': 91, '左win': 91, 'leftwin': 91, 'windows': 91, '右win': 92, 'rightwin': 92,
    '菜单': 93, '右键菜单': 93, 'apps': 93,
    'space': 32, '空格': 32,
    'insert': 45, 'ins': 45, '插入': 45, 'home': 36, 'pos1': 36, '起始': 36,
    'pageup': 33, 'pgup': 33, '上一页': 33, 'delete': 46, 'del': 46, '删除键': 46,
    'end': 35, '结束': 35, 'pagedown': 34, 'pgdn': 34, '下一页': 34,
    '上': 38, 'up': 38, '下': 40, 'down': 40, '左': 37, 'left': 37, '右': 39, 'right': 39,
    'numlock': 144, '数字锁定': 144, 'num': 144,
    '小键盘/': 111, 'numpad/': 111, '小键盘*': 106, 'numpad*': 106,
    '小键盘-': 109, 'numpad-': 109, '小键盘+': 107, 'numpad+': 107,
    '小键盘0': 96, 'numpad0': 96, '小键盘1': 97, 'numpad1': 97,
    '小键盘2': 98, 'numpad2': 98, '小键盘3': 99, 'numpad3': 99,
    '小键盘4': 100, 'numpad4': 100, '小键盘5': 101, 'numpad5': 101,
    '小键盘6': 102, 'numpad6': 102, '小键盘7': 103, 'numpad7': 103,
    '小键盘8': 104, 'numpad8': 104, '小键盘9': 105, 'numpad9': 105,
    '小键盘.': 110, '小键盘del': 110, 'numpad.': 110, 'numpaddel': 110,
    '小键盘回车': 13,
}

def 获取虚拟键码(键名: str) -> int:
    键名 = 键名.strip().lower()
    if len(键名) == 1 and 键名.isalpha():
        return ord(键名.upper())
    if len(键名) == 1 and 键名.isdigit():
        return ord(键名)
    if 键名 in KEY_MAP:
        return KEY_MAP[键名]
    raise ValueError(f"不支持的按键名称: {键名}")
def 异环钓鱼(adb路径, current_dir, 线程事件, ocr_engine):
    路径 = current_dir / "Tool_Settings.json"
    with open(路径, 'r', encoding='utf-8') as file:
        Tool_Settings = json.load(file)
    GPU加速 = bool(int(Tool_Settings["GPU加速识图变量"]))
    print(f"GPU加速:{GPU加速}")

    # ---------- 模板配置元组初始化 ----------
    判断区域路径配置元组 = 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\钓鱼\判定区域.png"), GPU加速)
    滑块路径配置元组 = 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\钓鱼\滑块.png"), GPU加速)
    滑块路径配置元组2 = 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\钓鱼\滑块2.png"), GPU加速)
    鱼舱已满路径配置元组 = 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\钓鱼\鱼舱已满.png"), GPU加速)
    鱼饵已空路径配置元组 = 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\钓鱼\鱼饵已空.png"), GPU加速)
    点击任意位置继续路径配置元组 = 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\钓鱼\点击任意位置继续.png"), GPU加速)

    # 新增的配置元组
    海上钓客配置元组 = 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\钓鱼\海上钓客.png"), GPU加速)
    渔具商店配置元组 = 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\钓鱼\渔具商店.png"), GPU加速)
    卖鱼配置元组 = 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\钓鱼\卖鱼.png"), GPU加速)
    月卡配置元组 = 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\钓鱼\月卡.png"), GPU加速)
    按F钓鱼配置元组 = 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\钓鱼\按F钓鱼.png"), GPU加速)
    开始钓鱼配置元组 = 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\钓鱼\开始钓鱼.png"), GPU加速)
    登录界面关闭游戏配置元组 = 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\钓鱼\登录界面关闭游戏.png"), GPU加速)
    确认配置元组 = 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\钓鱼\确认.png"), GPU加速)


    # ---------- 加载设置 ----------
    路径 = current_dir / "异环图片" / "钓鱼" / "钓鱼设置.json"
    with open(路径, 'r', encoding='utf-8') as file:
        字典 = json.load(file)
        判断频率 = float(字典["判断频率"])
        钓鱼次数 = int(字典["钓鱼次数"])
        钓鱼时间 = float(字典["异环钓鱼时间"])
        钓多少次卖鱼 = int(字典["钓多少次卖鱼"])
        钓多少次买饵 = int(字典["钓多少次买饵"])
        异环钓鱼上钩截图变量 = int(字典["异环钓鱼上钩截图变量"])
        异环鱼舱满卖鱼变量 = int(字典["异环鱼舱满卖鱼变量"])
        异环饵空卖饵变量 = int(字典["异环饵空卖饵变量"])
        判断区域识图相似度 = float(字典["判断区域识图相似度变量"])

    按键元组 = (0x41, 0x44, 0x46, 0x1B)
    _, 端口, hwnd, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb路径
    左a, 右d, 钓鱼1, 退出esc = 按键元组

    卖鱼次数 = 钓多少次卖鱼
    买饵次数 = 钓多少次买饵
    print(f"钓多少次卖鱼{钓多少次卖鱼}")

    filePath = current_dir / "异环图片" / "钓鱼" / "上钩截图"
    try:
        if filePath.exists():
            import shutil
            shutil.rmtree(filePath)
            filePath.mkdir(parents=True, exist_ok=True)
            print(f"已清空上钩截图文件夹: {filePath}")
        else:
            print(f"上钩截图文件夹不存在: {filePath}")
    except Exception as e:
        print(f"删除文件时出错: {e}")

    # ---------- 内部函数：回到钓鱼主界面 ----------
    def 回到钓鱼主界面():
        for i in range(15):
            for _ in range(6):
                if not 线程事件.is_set():
                    return
                png数据 = 函数截图到内存直接返回NumPy数组(hwnd, 窗口矩形)

                # 海上钓客
                是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(
                    背景图片=png数据, 限定区域=(6, 5, 222, 77), 最低相似度=0.8, 配置列表=海上钓客配置元组)
                if 是否匹配:
                    if 持续x除以y秒按键一个图片并且失败增加时长(adb路径, 10, 1, 退出esc,
                            Path(rf"{current_dir}\异环图片\钓鱼\海上钓客.png"), (6, 5, 222, 77), 0.7, 线程事件):
                        continue

                # 渔具商店
                是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(
                    背景图片=png数据, 限定区域=(11, 11, 187, 60), 最低相似度=0.8, 配置列表=渔具商店配置元组)
                if 是否匹配:
                    if 持续x除以y秒按键一个图片并且失败增加时长(adb路径, 10, 1, 退出esc,
                            Path(rf"{current_dir}\异环图片\钓鱼\渔具商店.png"), (11, 11, 187, 60), 0.7, 线程事件):
                        continue

                # 点击任意位置继续
                是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(
                    背景图片=png数据, 限定区域=(301, 288, 562, 427), 最低相似度=0.8, 配置列表=点击任意位置继续路径配置元组)
                if 是否匹配:
                    持续x除以y秒按键一个图片并且失败增加时长(adb路径, 18, 0.5, 退出esc,
                        Path(rf"{current_dir}\异环图片\钓鱼\点击任意位置继续.png"),
                        (301, 288, 562, 427), 0.8, 线程事件)
                    for _ in range(8):
                        time.sleep(0.5)
                        png数据 = 函数截图到内存直接返回NumPy数组(hwnd, 窗口矩形)
                        是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(
                            背景图片=png数据, 限定区域=(970, 613, 83, 89), 最低相似度=0.7, 配置列表=卖鱼配置元组)
                        if 是否匹配:
                            return
                    continue

                # 卖鱼
                是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(
                    背景图片=png数据, 限定区域=(970, 613, 83, 89), 最低相似度=0.7, 配置列表=卖鱼配置元组)
                if 是否匹配:
                    return

                # 月卡
                是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(
                    背景图片=png数据, 限定区域=(0, 0, 1280, 720), 最低相似度=0.8, 配置列表=月卡配置元组)
                if 是否匹配:
                    持续x除以y秒点击一个图片并且失败增加时长(adb路径, 10, 1,
                        Path(rf"{current_dir}\异环图片\钓鱼\月卡.png"), (0, 0, 1280, 720), 0.8, 线程事件)
                    time.sleep(5)
                    continue

                # 按F钓鱼
                是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(
                    背景图片=png数据, 限定区域=(717, 350, 220, 87), 最低相似度=0.8, 配置列表=按F钓鱼配置元组)
                if 是否匹配:
                    for _ in range(5):
                        模拟按键长按(hwnd, 钓鱼1, 0.05)
                    time.sleep(5)
                    continue

                # 开始钓鱼
                是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(
                    背景图片=png数据, 限定区域=(906, 586, 344, 85), 最低相似度=0.8, 配置列表=开始钓鱼配置元组)
                if 是否匹配:
                    持续x除以y秒点击一个图片并且失败增加时长(adb路径, 6, 1,
                        Path(rf"{current_dir}\异环图片\钓鱼\开始钓鱼.png"), (906, 586, 344, 85), 0.8, 线程事件)
                    time.sleep(5)
                    continue

                # 登录界面关闭游戏
                是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(
                    背景图片=png数据, 限定区域=(1, 631, 85, 73), 最低相似度=0.8, 配置列表=登录界面关闭游戏配置元组)
                if 是否匹配:
                    持续x除以y秒图存在则点击一个位置((620, 622), adb路径, 7, 1,
                        Path(rf"{current_dir}\异环图片\钓鱼\登录界面关闭游戏.png"), (1, 631, 85, 73), 0.8)

                time.sleep(0.5)

            if i == 0:
                for _ in range(20):
                    if not 线程事件.is_set():
                        return
                    模拟按键长按(hwnd, 钓鱼1, 0.005)
                    time.sleep(0.5)
                    png数据1 = 函数截图到内存直接返回NumPy数组(hwnd, 窗口矩形)
                    是否_匹配, _, _, _, _, _ = 函数_在指定区域内进行模板匹配返回横坐标范围(
                        背景图片=png数据1, 限定区域=(391, 33, 503, 43), 最低相似度=0.9,
                        配置列表=判断区域路径配置元组)
                    是否匹配_滑块, _, _, _ = 函数_在指定区域数组匹配(
                        背景图片=png数据1, 限定区域=(391, 33, 503, 43), 最低相似度=0.8,
                        配置列表=滑块路径配置元组)
                    if 是否_匹配 or 是否匹配_滑块:
                        return
            模拟按键长按(hwnd, 退出esc, 0.005)

        else:
            print("回到钓鱼主界面")

    # ---------- 内部函数：卖鱼 ----------
    def 卖鱼():
        出售成功 = False
        for _ in range(5):
            出售成功 = False
            回到钓鱼主界面()
            if 持续x除以y秒按键一个图片并且失败增加时长(adb路径, 10, 1, 81,
                    Path(rf"{current_dir}\异环图片\钓鱼\卖鱼.png"), (970, 613, 83, 89), 0.7, 线程事件):
                if 持续x除以y秒点击一个图片并且失败增加时长(adb路径, 10, 1,
                        Path(rf"{current_dir}\异环图片\钓鱼\鱼舱.png"), (82, 247, 38, 58), 0.8, 线程事件, 真实鼠标=True):
                    if 持续x除以y秒点击一个图片并且失败增加时长(adb路径, 10, 1,
                            Path(rf"{current_dir}\异环图片\钓鱼\一键出售.png"), (636, 615, 155, 64), 0.8, 线程事件, 真实鼠标=True):
                        for _ in range(5):
                            png数据 = 函数截图到内存直接返回NumPy数组(hwnd, 窗口矩形)
                            是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(
                                背景图片=png数据, 限定区域=(692, 443, 197, 53), 最低相似度=0.6, 配置列表=确认配置元组)
                            if 是否匹配:
                                出售成功 = True
                                break
                        if 持续x除以y秒图未出现则点击一个位置((779, 470), adb路径, 10, 1,
                                Path(rf"{current_dir}\异环图片\钓鱼\海上钓客.png"), (6, 5, 222, 77), 0.8, 线程事件, 真实鼠标=True):
                            pass
            else:
                回到钓鱼主界面()
                break
            回到钓鱼主界面()
            if 出售成功:
                break
        return 出售成功

    # ---------- 内部函数：买鱼饵 ----------
    def 买鱼饵(购买次):
        成功次数 = 0
        买饵成功 = False
        for _ in range(购买次 * 2 + 2):
            回到钓鱼主界面()
            if 持续x除以y秒按键一个图片并且失败增加时长(adb路径, 10, 1, 82,
                    Path(rf"{current_dir}\异环图片\钓鱼\卖鱼.png"), (970, 613, 83, 89), 0.7, 线程事件):
                time.sleep(2)
                png数据1 = 获取_png_data(adb路径, )
                最终结果 = 函数_在指定区域内进行模板匹配_多目标(png数据1, (19, 65, 448, 607),
                    Path(rf"{current_dir}\异环图片\钓鱼\万能鱼饵.png"), 0.8, nms_threshold=0.6)
                print(最终结果)
                for 最终结果i, (conf, x, y) in enumerate(最终结果):
                    if 持续x除以y秒图未出现则点击一个位置((x + 30, y + 30), adb路径, 7, 0.5,
                            Path(rf"{current_dir}\异环图片\钓鱼\消耗贝壳.png"), (1085, 567, 55, 50), 0.8, 线程事件, 真实鼠标=True):
                        if 持续x除以y秒图未出现则点击一个位置((x + 30, y + 30), adb路径, 10, 1,
                                Path(rf"{current_dir}\异环图片\钓鱼\万能鱼饵2.png"), (872, 109, 201, 189), 0.8, 线程事件, 真实鼠标=True):
                            if 持续x除以y秒图未出现则点击一个位置((1218, 634), adb路径, 10, 1,
                                    Path(rf"{current_dir}\异环图片\钓鱼\购买鱼饵拉满状态.png"), (1119, 602, 71, 73), 0.8, 线程事件, 真实鼠标=True):
                                if 持续x除以y秒点击一个图片并且失败增加时长(adb路径, 10, 1,
                                        Path(rf"{current_dir}\异环图片\钓鱼\购买鱼饵购买.png"), (1008, 655, 134, 56), 0.86, 线程事件, 真实鼠标=True):
                                    if 持续x除以y秒图未出现则点击一个位置((763, 473), adb路径, 6, 1,
                                            Path(rf"{current_dir}\异环图片\钓鱼\购买鱼饵购买.png"), (997, 662, 132, 45), 0.8, 线程事件, 真实鼠标=True):
                                        pass
                                    成功次数 = 成功次数 + 1
                        break
            else:
                回到钓鱼主界面()
                break
            print(f"需要购买的次数={购买次},购买成功的次数={成功次数}")
            回到钓鱼主界面()
            if 成功次数 >= 购买次:
                买饵成功 = True
                break
        return 买饵成功, 成功次数

    # ---------- 内部函数：换鱼饵 ----------
    def 换鱼饵():
        for _ in range(5):
            if not 线程事件.is_set():
                return
            回到钓鱼主界面()
            if 持续x除以y秒按键一个图片并且失败增加时长(adb路径, 10, 1, 69,
                    Path(rf"{current_dir}\异环图片\钓鱼\卖鱼.png"), (970, 613, 83, 89), 0.7, 线程事件):
                if 持续x除以y秒点击一个图片并且失败增加时长(adb路径, 10, 1,
                        Path(rf"{current_dir}\异环图片\钓鱼\万能鱼饵3更换.png"), (412, 293, 113, 125), 0.8, 线程事件, 真实鼠标=True):
                    if 持续x除以y秒图未出现则点击一个位置((848, 467), adb路径, 10, 1,
                            Path(rf"{current_dir}\异环图片\钓鱼\卖鱼.png"), (970, 613, 83, 89), 0.7, 线程事件, 真实鼠标=True):
                        break
        回到钓鱼主界面()
        if not 线程事件.is_set():
            return
        for _ in range(5):
            模拟按键长按(hwnd, 钓鱼1, 0.005)
            time.sleep(0.65)

    # ---------- 主循环 ----------
    钓鱼开始总时间=time.time()
    次数=0
    while True:
        if not 线程事件.is_set():
            return
        for _ in range(100):
            次数 = 次数 + 1
            if 次数 >= 钓鱼次数:
                return
            if time.time() - 钓鱼开始总时间 > 钓鱼时间 * 3600:
                print(f"钓鱼时间已达到设定时间，退出，")
                return
            if not 线程事件.is_set():
                return
            回到钓鱼主界面()

            if 次数 >= 卖鱼次数 and 钓多少次卖鱼:
                进入出售成功 = 卖鱼()
                if 进入出售成功:
                    卖鱼次数 = 卖鱼次数 + 钓多少次卖鱼

            if 次数 >= 买饵次数 and 钓多少次买饵:
                购买次数 = 钓多少次买饵 // 100 + 1
                print(f"购买次数={购买次数}")
                买饵成功, 成功次数 = 买鱼饵(购买次数)
                if 买饵成功:
                    买饵次数 = 买饵次数 + 钓多少次买饵
                    print(f"下一次买鱼饵次数={买饵次数},购买成功的次数={成功次数}")

            for _ in range(5):
                模拟按键长按(hwnd, 钓鱼1, 0.005)
                time.sleep(0.65)
                png数据 = 函数截图到内存直接返回NumPy数组(hwnd, 窗口矩形)

                if 异环鱼舱满卖鱼变量:
                    是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(
                        背景图片=png数据, 限定区域=(426, 309, 439, 93), 最低相似度=0.65, 配置列表=鱼舱已满路径配置元组)
                    if 是否匹配:
                        卖鱼()

                if 异环饵空卖饵变量:
                    是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(
                        背景图片=png数据, 限定区域=(426, 309, 439, 93), 最低相似度=0.65, 配置列表=鱼饵已空路径配置元组)
                    if 是否匹配:
                        买鱼饵(1)
                        换鱼饵()

                是否匹配, max_val, 最小x, 最小y, 最大x, 最大y = 函数_在指定区域内进行模板匹配返回横坐标范围(
                    背景图片=png数据, 限定区域=(391, 33, 503, 43), 最低相似度=0.9,
                    配置列表=判断区域路径配置元组)
                是否匹配滑块, 无语2, x坐标2, 无语2 = 函数_在指定区域数组匹配(
                    背景图片=png数据, 限定区域=(391, 33, 503, 43), 最低相似度=0.8,
                    配置列表=滑块路径配置元组)
                if 是否匹配 or 是否匹配滑块:
                    print("上钩进入判断")
                    break
                if not 线程事件.is_set():
                    return

            start_time = time.time()
            模拟按键弹起(hwnd, 右d)
            模拟按键按下(hwnd, 左a)

            while time.time() - start_time < 60:
                time.sleep(判断频率)
                if not 线程事件.is_set():
                    模拟按键弹起(hwnd, 右d)
                    模拟按键弹起(hwnd, 左a)
                    return

                截图开始时间 = time.time()
                png数据 = 函数截图到内存直接返回NumPy数组(hwnd, 窗口矩形)
                print(f"截图耗时：{(time.time() - 截图开始时间):.4f}秒")

                是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(
                    背景图片=png数据, 限定区域=(301, 288, 562, 427), 最低相似度=0.8,
                    配置列表=点击任意位置继续路径配置元组)
                if 是否匹配:
                    print("鱼耐力耗尽")
                    if 异环钓鱼上钩截图变量:
                        filePath = current_dir / "异环图片" / "钓鱼" / "上钩截图" / f"{次数}.jpg"
                        png数据 = 获取_png_data(adb路径, )
                        img = Image.open(io.BytesIO(png数据))
                        # 如果有透明通道且想大幅缩小，可选用量化（会有轻微质量损失）
                        # img = img.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
                        img.save(filePath.with_suffix('.jpg'), format='JPEG', quality=85)
                    break

                模拟按键长按(hwnd, 钓鱼1, 0.005)


                是否匹配判断区域, _, 最小x, _, 最大x, _ = 函数_在指定区域内进行模板匹配返回横坐标范围(
                    背景图片=png数据, 限定区域=(391, 33, 503, 43), 最低相似度=判断区域识图相似度,
                    配置列表=判断区域路径配置元组)

                if not 是否匹配判断区域:
                    print("判定区域识别失败，可能是鱼未上钩，钓鱼判定最优算法开启前置条件缺失，已回退为旧算法，如果鱼已上钩，推荐检查滤镜，护眼模式，hdr，色彩增强等是否开启大幅影响了游戏画面")
                    是否匹配, _, 最小x, _ = 函数_在指定区域数组匹配(
                        背景图片=png数据, 限定区域=(391, 33, 503, 43), 最低相似度=0.8,
                        配置列表=判断区域路径配置元组)


                是否匹配1, max_val1, x坐标_1, _ = 函数_在指定区域数组匹配(背景图片=png数据, 限定区域=(391, 33, 503, 43), 最低相似度=0.8, 配置列表=滑块路径配置元组)

                是否匹配2, max_val2, x坐标_2, _ = 函数_在指定区域数组匹配(背景图片=png数据, 限定区域=(391, 33, 503, 43), 最低相似度=0.8, 配置列表=滑块路径配置元组2)

                # 根据较大的 max_val 选择对应的 x 坐标
                if max_val1 >= max_val2:
                    x坐标2 = x坐标_1
                else:
                    x坐标2 = x坐标_2

                if 是否匹配判断区域:
                    if 最小x < x坐标2 < 最大x:
                        模拟按键弹起(hwnd, 右d)
                        模拟按键弹起(hwnd, 左a)
                    elif 最小x > x坐标2:
                        模拟按键弹起(hwnd, 左a)
                        模拟按键按下(hwnd, 右d)
                    elif x坐标2 > 最大x:
                        模拟按键弹起(hwnd, 右d)
                        模拟按键按下(hwnd, 左a)
                    else:
                        否则元组 = (右d, 左a)
                        随机元组 = random.sample(否则元组, 2)
                        模拟按键弹起(hwnd, 随机元组[0])
                        模拟按键按下(hwnd, 随机元组[1])
                else:
                    if 最小x > x坐标2:
                        模拟按键弹起(hwnd, 左a)
                        模拟按键按下(hwnd, 右d)
                    else:
                        模拟按键弹起(hwnd, 右d)
                        模拟按键按下(hwnd, 左a)

            else:
                from 连接adb import _update_window_rect
                窗口矩形2=_update_window_rect(hwnd)
                if 窗口矩形2[2]-窗口矩形2[0] !=窗口矩形[2]-窗口矩形[0] or 窗口矩形2[3]-窗口矩形2[1] !=窗口矩形[3]-窗口矩形[1]:
                    print(f"窗口矩形发生变化，本次检测到的窗口矩形为：{窗口矩形2}，参数窗口矩形为：{窗口矩形}")
                    return

                for _ in range(5):
                    模拟按键长按(hwnd, 钓鱼1, 0.005)
                    time.sleep(0.65)
                    png数据 = 函数截图到内存直接返回NumPy数组(hwnd, 窗口矩形)

                    if 异环鱼舱满卖鱼变量:
                        是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(
                            背景图片=png数据, 限定区域=(426, 309, 439, 93), 最低相似度=0.65,
                            配置列表=鱼舱已满路径配置元组)
                        if 是否匹配:
                            卖鱼()
                    if 异环饵空卖饵变量:
                        是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(
                            背景图片=png数据, 限定区域=(426, 309, 439, 93), 最低相似度=0.65,
                            配置列表=鱼饵已空路径配置元组)
                        if 是否匹配:
                            买鱼饵(1)
                            换鱼饵()

            模拟按键弹起(hwnd, 右d)
            模拟按键弹起(hwnd, 左a)

            for _ in range(20):
                print(f"第{次数 + 1}次钓鱼结束，还剩{钓鱼次数 - 次数 - 1}次")
        for _ in range(5):
            time.sleep(1)
            if not 线程事件.is_set():
                return
        # ---------- 模板配置元组初始化 ----------
        判断区域路径配置元组 = 根据模版路径返回配置元组(
            Path(rf"{current_dir}\异环图片\钓鱼\判定区域.png"), GPU加速)
        滑块路径配置元组 = 根据模版路径返回配置元组(
            Path(rf"{current_dir}\异环图片\钓鱼\滑块.png"), GPU加速)
        滑块路径配置元组2 = 根据模版路径返回配置元组(
            Path(rf"{current_dir}\异环图片\钓鱼\滑块2.png"), GPU加速)
        鱼舱已满路径配置元组 = 根据模版路径返回配置元组(
            Path(rf"{current_dir}\异环图片\钓鱼\鱼舱已满.png"), GPU加速)
        鱼饵已空路径配置元组 = 根据模版路径返回配置元组(
            Path(rf"{current_dir}\异环图片\钓鱼\鱼饵已空.png"), GPU加速)
        点击任意位置继续路径配置元组 = 根据模版路径返回配置元组(
            Path(rf"{current_dir}\异环图片\钓鱼\点击任意位置继续.png"), GPU加速)

        # 新增的配置元组
        海上钓客配置元组 = 根据模版路径返回配置元组(
            Path(rf"{current_dir}\异环图片\钓鱼\海上钓客.png"), GPU加速)
        渔具商店配置元组 = 根据模版路径返回配置元组(
            Path(rf"{current_dir}\异环图片\钓鱼\渔具商店.png"), GPU加速)
        卖鱼配置元组 = 根据模版路径返回配置元组(
            Path(rf"{current_dir}\异环图片\钓鱼\卖鱼.png"), GPU加速)
        月卡配置元组 = 根据模版路径返回配置元组(
            Path(rf"{current_dir}\异环图片\钓鱼\月卡.png"), GPU加速)
        按F钓鱼配置元组 = 根据模版路径返回配置元组(
            Path(rf"{current_dir}\异环图片\钓鱼\按F钓鱼.png"), GPU加速)
        开始钓鱼配置元组 = 根据模版路径返回配置元组(
            Path(rf"{current_dir}\异环图片\钓鱼\开始钓鱼.png"), GPU加速)
        登录界面关闭游戏配置元组 = 根据模版路径返回配置元组(
            Path(rf"{current_dir}\异环图片\钓鱼\登录界面关闭游戏.png"), GPU加速)
        确认配置元组 = 根据模版路径返回配置元组(
            Path(rf"{current_dir}\异环图片\钓鱼\确认.png"), GPU加速)


def 店长特供(adb路径, current_dir, 保持速切战斗线程事件对象):
    无用, 端口, 句柄, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb路径
    while 保持速切战斗线程事件对象.is_set():
        time.sleep(0.5)
        png数据 = 获取_png_data(adb路径, x1=0, y1=0, x2=0, y2=0)
        是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(背景图片数据=png数据, 限定区域=(10, 73, 1261, 314), 模板路径=Path(rf"{current_dir}\异环图片\店长特供\多人.png"), 最低相似度=0.91)
        if 是否匹配:
            真实鼠标坐标后台点击专用(句柄, 窗口矩形, (63,295),
                                     PC全局延迟, 0.5)
def 超强音(adb路径, current_dir, 线程事件):
    路径 = current_dir / "Tool_Settings.json"
    with open(路径, 'r', encoding='utf-8') as file:
        Tool_Settings = json.load(file)
    GPU加速 = bool(int(Tool_Settings["GPU加速识图变量"]))
    print(f"GPU加速:{GPU加速}")
    无用, 端口, 句柄, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb路径
    路径 = current_dir.parent / "外置配置文件夹" / "超强音设置.json"
    with open(路径, 'r', encoding='utf-8') as file:
        字典 = json.load(file)
        超强音按键长按时间 = float(字典["超强音按键长按时间"])
        超强音判断相似度 = float(字典["超强音判断相似度"])
        都市体力耗尽停下 = bool(字典["都市体力耗尽停下变量"])
        超强音演奏次数 = int(字典["超强音演奏次数变量"])

        控制键位K = int(字典["控制键位K变量"])
        控制键位J = int(字典["控制键位J变量"])
        控制键位F = int(字典["控制键位F变量"])
        控制键位D = int(字典["控制键位D变量"])
    print(f"超强音按键长按时间{超强音按键长按时间}")
    print(f"超强音判断相似度{超强音判断相似度}")
    窗口假激活(句柄)
    相似度=超强音判断相似度
    长按时间=超强音按键长按时间
    D路径元组 = 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\超强音\D.png"), GPU加速)
    FJ路径元组 = 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\超强音\FJ.png"), GPU加速)
    K路径元组 = 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\超强音\K.png"), GPU加速)
    开始演奏列表=根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\超强音\超强音选曲.png"), GPU加速)
    演奏完成配置元组 = 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\超强音\消耗活力.png"), GPU加速)
    都市体力耗尽配置元组 = 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\超强音\都市体力耗尽.png"), GPU加速)


    from concurrent.futures import ThreadPoolExecutor
    def 创建工作函数(键码, 限定区域, 模板元组, 相似度阈值, 句柄, 长按时间):
        """工厂函数：返回一个接受png数据的工作函数"""

        def 工作函数(png数据):
            是否匹配, _, _, _ = 函数_在指定区域数组匹配(
                背景图片=png数据,
                限定区域=限定区域,
                最低相似度=相似度阈值,
                配置列表=模板元组
            )
            if 是否匹配:
                time.sleep(0.01)
            else:
                模拟按键长按(句柄, 键码, 长按时间)
                time.sleep(0.01)

        return 工作函数

    def 主控循环(线程事件, 句柄, 长按时间, 相似度):
        """主循环：截图并分发给工作线程"""
        # 定义各键对应的参数
        键位配置 = []
        """ (0x44, (236, 502, 115, 115), D路径元组, 'D'),
            (0x46, (470, 511, 101, 106), FJ路径元组, 'F'),
            (74, (726, 518, 75, 81), FJ路径元组, 'J'),
            (75, (944, 525, 86, 82), K路径元组, 'K')"""

        if 控制键位D:
            键位配置.append((0x44, (236, 502, 115, 115), D路径元组, 'D'))
        if 控制键位F:
            键位配置.append((0x46, (470, 511, 101, 106), FJ路径元组, 'F'))
        if 控制键位J:
            键位配置.append((74, (726, 518, 75, 81), FJ路径元组, 'J'))
        if 控制键位K:
            键位配置.append((75, (944, 525, 86, 82), K路径元组, 'K'))
        # 创建工作函数列表
        工作函数列表 = []
        for 键码, 区域, 模板元组, _ in 键位配置:
            工作函数列表.append(创建工作函数(键码, 区域, 模板元组, 相似度, 句柄, 长按时间))

        with ThreadPoolExecutor(max_workers=4) as executor:
            while 线程事件.is_set():
                png数据 = 函数截图到内存直接返回NumPy数组(句柄, (0, 0, 1066, 651))
                # 提交所有任务
                futures = [executor.submit(工作函数, png数据) for 工作函数 in 工作函数列表]
                # 可选：等待本轮所有任务完成（若需要严格同步）
                for f in futures:
                     f.result()
                # 避免CPU空转，给其他线程一点时间
                是否匹配, _, _, _ = 函数_在指定区域数组匹配(背景图片=png数据, 限定区域=(7, 4, 175, 74), 最低相似度=0.8, 配置列表=开始演奏列表)
                if 是否匹配:
                    return
                是否匹配, _, _, _ = 函数_在指定区域数组匹配(背景图片=png数据, 限定区域=(424, 381, 101, 122), 最低相似度=0.8, 配置列表=演奏完成配置元组)
                if 是否匹配:
                    print("准备退出演奏")
                    return

                    # 启动线程（假设线程事件已在外部定义并设置）
    成功次数=0

    for _ in range(9999):
        if not 线程事件.is_set():
            return
        png数据 = 函数截图到内存直接返回NumPy数组(句柄, 窗口矩形)
        if 都市体力耗尽停下:
            是否匹配, _, _, _ = 函数_在指定区域数组匹配(背景图片=png数据, 限定区域=(413, 384, 446, 107), 最低相似度=0.9, 配置列表=都市体力耗尽配置元组)
            if 是否匹配:
                return
        print("准备进入演奏1")
        是否匹配, _, _, _ = 函数_在指定区域数组匹配(背景图片=png数据, 限定区域=(424, 381, 101, 122), 最低相似度=0.8, 配置列表=演奏完成配置元组)
        if 是否匹配:
            成功次数 = 成功次数 + 1
            if 成功次数>=超强音演奏次数:
                return
            持续x除以y秒按键一个图片并且失败增加时长(adb路径, 10, 1, 0x1B,
                                                     Path(rf"{current_dir}\异环图片\超强音\消耗活力.png"), (424, 381, 101, 122), 0.7, 线程事件)

            time.sleep(2)
            png数据 = 函数截图到内存直接返回NumPy数组(句柄, 窗口矩形)
        是否匹配, _, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(背景图片=png数据, 限定区域=(7, 4, 175, 74), 最低相似度=0.8, 配置列表=开始演奏列表)
        if 是否匹配:
            持续x除以y秒图存在则点击一个位置((1071,666), adb路径, 7, 1,
                                             Path(rf"{current_dir}\异环图片\超强音\超强音选曲.png"), (7, 4, 175, 74), 0.8, 线程事件, 真实鼠标=False)

        主线程 = threading.Thread(target=主控循环, args=(线程事件, 句柄, 长按时间, 相似度))
        主线程.start()

        # 主线程保持运行（例如等待停止信号）
        主线程.join()
        time.sleep(1)

def 鼠标快速打开esc界面(adb路径,  线程事件,线程事件2):
    _, _, 句柄, 窗口矩形, _ = adb路径
    游戏宽 = 窗口矩形[2] - 窗口矩形[0]
    缩放比=游戏宽/1920
    游戏高 = 窗口矩形[2] - 窗口矩形[0]
    缩放比2=游戏高/1920
    窗口假激活(句柄)
    time.sleep(0.05)
    模拟按键弹起(句柄, 获取虚拟键码("alt"))
    time.sleep(0.05)
    模拟按键按下(句柄, 获取虚拟键码("alt"))
    time.sleep(0.05)
    x = 游戏宽 - 80*缩放比*0.5
    y = 45*缩放比2*0.5
    前台模拟鼠标左键单击绑定窗口(int(x), int(y), 窗口矩形, 点击时间=0.05, 次数=1)
    time.sleep(0.05)
    模拟按键弹起(句柄, 获取虚拟键码("alt"))



    线程事件.clear()
    线程事件2.clear()
    print(f"任务鼠标快速打开esc界面结束")

def 自动剧情(current_dir,adb路径,  线程事件,线程事件2):
    路径 = current_dir / "Tool_Settings.json"
    with open(路径, 'r', encoding='utf-8') as file:
        Tool_Settings = json.load(file)
    GPU加速 = bool(int(Tool_Settings["GPU加速识图变量"]))
    print(f"GPU加速:{GPU加速}")
    _, _, 句柄, 窗口矩形, _ = adb路径


    对话配置列表= 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\剧情跳过\对话_1920x1080.png"), GPU加速,窗口矩形)
    跳过配置列表 = 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\剧情跳过\跳过_1920x1080.png"), GPU加速,窗口矩形)

    while 线程事件.is_set():
        time.sleep(0.2)
        png数据 = 函数截图到内存直接返回NumPy数组(句柄, 窗口矩形)

        是否匹配, _, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(背景图片=png数据, 限定区域=(1500, 0, 420, 140), 最低相似度=0.65, 配置列表=跳过配置列表)
        if 是否匹配:
            模拟按键长按(句柄, 27, 0.1 + random_non_negative(0.05, 0.01))  # esc27
        是否匹配, _, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(背景图片=png数据, 限定区域=(1500, 0, 420, 140), 最低相似度=0.65, 配置列表=对话配置列表)
        if 是否匹配:
            模拟按键长按(句柄, 32, 0.1 + random_non_negative(0.05, 0.01))#空格32
            模拟按键长按(句柄, 70, 0.1 + random_non_negative(0.05, 0.01))#F70
    线程事件2.clear()
    print(f"任务 自动剧情跳过 结束")
def 自动按F(current_dir,adb路径,  事件循环,事件停止,识图间隔):
    路径 = current_dir / "Tool_Settings.json"
    with open(路径, 'r', encoding='utf-8') as file:
        Tool_Settings = json.load(file)
    GPU加速 = bool(int(Tool_Settings["GPU加速识图变量"]))
    print(f"GPU加速:{GPU加速}")
    _, _, 句柄, 窗口矩形, _ = adb路径

    F配置列表= 根据模版路径返回配置元组(
        Path(rf"{current_dir}\异环图片\自动按F\F_1920x1080.png"), GPU加速,窗口矩形)
    限定区域1 = (900, 500, 300, 200)
    while 事件循环.is_set():
        time.sleep(识图间隔)
        png数据 = 函数截图到内存直接返回NumPy数组(句柄, 窗口矩形)

        是否匹配, _, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(背景图片=png数据, 限定区域=限定区域1, 最低相似度=0.635, 配置列表=F配置列表)
        if 是否匹配:
            pass
            模拟按键长按(句柄, 70, 0.01 + random_non_negative(0.05, 0.01))#F70
    事件停止.clear()
    print(f"任务 自动按F 结束")




def 速切宏战斗线程(保持速切战斗线程事件对象,线程事件,adb):
    无用, 端口, 句柄, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb
    while 保持速切战斗线程事件对象.is_set():

        模拟鼠标中键点击(句柄, 640, 360, 0.005 + random_non_negative(0.05, 0.01))
        time.sleep(0.005 + random_non_negative(0.05, 0.01))
        模拟按键长按(句柄, 0x31, 0.005 + random_non_negative(0.05, 0.01))
        time.sleep(0.005 + random_non_negative(0.05, 0.01))
        模拟按键长按(句柄, 0x34, 0.005 + random_non_negative(0.05, 0.01))
        time.sleep(0.005 + random_non_negative(0.05, 0.01))
        模拟按键长按(句柄, 0x32, 0.005 + random_non_negative(0.05, 0.01))
        time.sleep(0.005 + random_non_negative(0.05, 0.01))
        模拟按键长按(句柄, 0x33, 0.005 + random_non_negative(0.05, 0.01))
        time.sleep(0.005 + random_non_negative(0.05, 0.01))

    线程事件.clear()
    print(f"任务 速切宏战斗线程1 结束")

def 速切宏战斗线程2(保持速切战斗线程事件对象,线程事件,adb,变轨技能键码,极轨终结键码,弧盘技能键码):
    无用, 端口, 句柄, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb
    变轨技能键码 = 获取虚拟键码(变轨技能键码)
    极轨终结键码 = 获取虚拟键码(极轨终结键码)
    弧盘技能键码 = 获取虚拟键码(弧盘技能键码)
    while 保持速切战斗线程事件对象.is_set():
        模拟鼠标左键长按(句柄, 640, 360, 0.05+ random_non_negative(0.05, 0.01))
        模拟按键长按(句柄, 变轨技能键码, 0.005 + random_non_negative(0.05, 0.01))
        模拟按键长按(句柄, 极轨终结键码, 0.005 + random_non_negative(0.05, 0.01))
        模拟按键长按(句柄, 弧盘技能键码, 0.005 + random_non_negative(0.05, 0.01))

    线程事件.clear()
    print(f"任务 速切宏战斗线程2 结束")