"""
1.需要指定坐标的鼠标左键点击只能用前台，不指定坐标的鼠标左键动作可以后台(比如角色的普攻和重击)
2.其他命令后台前台都支持
3.即使是后台命令游戏窗口也不能最小化，但可以被遮挡，比如你可以全屏玩其他游戏和看视频
4.txt文件必须防在"外置配置文件夹\txt自定义脚本"中，GUI只会识别这个路径下的txt文件
5.坐标是游戏窗口内部的像素位置。想了解如何获取坐标，请看对应图文详解，在工具UI中点击“使用中文编写脚本教程”按钮会弹出来。
6.如何裁剪出用于匹配的图片，也请看图文教程，在工具UI中点击“使用中文编写脚本教程”按钮会弹出来。
"""
import re
import threading
import time
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

import win32gui
import win32con
import win32api
import ctypes

# 后台键鼠模块
from 后台键鼠 import (模拟按键弹起, 模拟按键按下, 模拟按键长按,
                     后台模拟鼠标左键点击, 后台模拟鼠标右键长按, 后台模拟鼠标中键长按,
                     后台模拟鼠标左键按下, 后台模拟鼠标左键弹起,
                     后台模拟鼠标右键按下, 后台模拟鼠标右键弹起,
                     前台模拟鼠标左键单击绑定窗口, 前台模拟鼠标左键按下绑定窗口,
                     前台模拟鼠标左键弹起绑定窗口, 游戏_等待, 游戏_窗口置顶)
from 游戏截图保存到内存 import 函数截图到内存直接返回NumPy数组
from opencv模板匹配找图 import 根据模版路径返回配置元组, 函数_在指定区域数组匹配

# ---------- 全局工作目录定义 ----------
if getattr(sys, 'frozen', False):
    当前执行目录 = Path(sys.executable).parent.absolute()
    工作目录 = 当前执行目录.parent / "外置配置文件夹"
else:
    当前执行目录 = Path(__file__).parent.absolute()
    工作目录 = 当前执行目录.parent / "外置配置文件夹"
# ---------- 完整键盘映射表 ----------
KEY_MAP = {
    'esc': 27, 'escape': 27,
    'f1': 112, 'f2': 113, 'f3': 114, 'f4': 115,
    'f5': 116, 'f6': 117, 'f7': 118, 'f8': 119,
    'f9': 120, 'f10': 121, 'f11': 122, 'f12': 123,
    'printscreen': 44, 'prtsc': 44,
    'scrolllock': 145,
    'pause': 19, 'break': 19,
    '`': 192, '~': 192,
    '1': 49, '!': 49, '2': 50, '@': 50, '3': 51, '#': 51, '4': 52, '$': 52,
    '5': 53, '%': 53, '6': 54, '^': 54, '7': 55, '&': 55, '8': 56, '*': 56,
    '9': 57, '(': 57, '0': 48, ')': 48,
    '-': 189, '_': 189, '=': 187, '+': 187,
    'backspace': 8,
    'tab': 9,
    '[': 219, '{': 219, ']': 221, '}': 221,
    '\\': 220, '|': 220,
    'capslock': 20,
    ';': 186, ':': 186, "'": 222, '"': 222,
    'enter': 13,
    'shift': 160, '左shift': 160, '右shift': 161,
    'ctrl': 162, '左ctrl': 162, '右ctrl': 163,
    'alt': 164, '左alt': 164, '右alt': 165,
    'win': 91, '左win': 91, '右win': 92,
    '菜单': 93, 'apps': 93,
    'space': 32,
    'insert': 45, 'ins': 45, 'home': 36, 'pageup': 33, 'pgup': 33,
    'delete': 46, 'del': 46, 'end': 35, 'pagedown': 34, 'pgdn': 34,
    '上': 38, 'up': 38, '下': 40, 'down': 40, '左': 37, 'left': 37, '右': 39, 'right': 39,
    'numlock': 144,
    '小键盘/': 111, '小键盘*': 106, '小键盘-': 109, '小键盘+': 107,
    '小键盘0': 96, '小键盘1': 97, '小键盘2': 98, '小键盘3': 99,
    '小键盘4': 100, '小键盘5': 101, '小键盘6': 102, '小键盘7': 103,
    '小键盘8': 104, '小键盘9': 105,
    '小键盘.': 110, '小键盘del': 110,
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


# ---------- 原有单行动作解析 ----------
def 执行脚本行(句柄, 窗口矩形, 线程事件, 行: str):
    """执行单行动作指令（键盘、鼠标、等待、置顶等）"""
    line = 行.strip()
    if not line:
        return

    # 按下按键
    m = re.match(r'^按下按键\s+(.+)$', line)
    if m:
        vk = 获取虚拟键码(m.group(1))
        模拟按键按下(句柄, vk)
        return
    # 弹起按键
    m = re.match(r'^弹起按键\s+(.+)$', line)
    if m:
        vk = 获取虚拟键码(m.group(1))
        模拟按键弹起(句柄, vk)
        return
    # 长按按键
    m = re.match(r'^长按按键\s+(.+?)(?:\s+([\d.]+))?$', line)
    if m:
        vk = 获取虚拟键码(m.group(1))
        时长 = float(m.group(2)) if m.group(2) else 0.05
        模拟按键长按(句柄, vk, 时长)
        return

    # 后台鼠标
    if '后台角色普攻重击' in line:
        时长 = re.search(r'([\d.]+)', line)
        时长 = float(时长.group(1)) if 时长 else 0.05
        后台模拟鼠标左键点击(句柄, 时长)
        return
    if '后台右键长按' in line:
        时长 = re.search(r'([\d.]+)', line)
        时长 = float(时长.group(1)) if 时长 else 0.05
        后台模拟鼠标右键长按(句柄, 时长)
        return
    if '后台中键长按' in line:
        时长 = re.search(r'([\d.]+)', line)
        时长 = float(时长.group(1)) if 时长 else 0.05
        后台模拟鼠标中键长按(句柄, 时长)
        return

    # ---------- 新增：后台鼠标按下/弹起支持 ----------
    if line == '后台左键按下':
        后台模拟鼠标左键按下(句柄)
        return
    if line == '后台左键弹起':
        后台模拟鼠标左键弹起(句柄)
        return
    if line == '后台右键按下':
        后台模拟鼠标右键按下(句柄)
        return
    if line == '后台右键弹起':
        后台模拟鼠标右键弹起(句柄)
        return

    # 前台鼠标点击
    m = re.match(r'^前台左键(?:单击|点击)\s+([\d.]+)\s*[,，]\s*([\d.]+)(?:\s+([\d.]+))?(?:\s+(\d+))?$', line)
    if m:
        x, y = int(float(m.group(1))), int(float(m.group(2)))
        点击时间 = float(m.group(3)) if m.group(3) else 0.05
        次数 = int(m.group(4)) if m.group(4) else 1
        前台模拟鼠标左键单击绑定窗口(x, y, 窗口矩形, 点击时间, 次数)
        return
    m = re.match(r'^前台左键按下\s+([\d.]+)\s*[,，]\s*([\d.]+)$', line)
    if m:
        x, y = int(float(m.group(1))), int(float(m.group(2)))
        前台模拟鼠标左键按下绑定窗口(x, y, 窗口矩形)
        return
    m = re.match(r'^前台左键弹起\s+([\d.]+)\s*[,，]\s*([\d.]+)$', line)
    if m:
        x, y = int(float(m.group(1))), int(float(m.group(2)))
        前台模拟鼠标左键弹起绑定窗口(x, y, 窗口矩形)
        return

    # 等待
    m = re.match(r'^等待\s+([\d.]+)$', line)
    if m:
        游戏_等待(float(m.group(1)), 线程事件)
        return

    # 窗口置顶
    if '窗口置顶' in line and '取消' not in line:
        游戏_窗口置顶(句柄, True)
        time.sleep(1)
        游戏_窗口置顶(句柄, False)
        return

    print(f"警告：无法识别的指令 -> {line}")


# ===================== 路径处理函数 =====================
def 标准化图片路径(原始路径字符串: str) -> str:
    """将脚本中的图片路径转换为可用的绝对路径，返回标准化后的相对路径字符串"""
    raw = 原始路径字符串.strip()

    if "外置配置文件夹" in raw:
        parts = raw.split("外置配置文件夹", 1)
        if len(parts) == 2:
            relative_protrail = parts[1].lstrip("\\/")
            abs_path = 工作目录 / relative_protrail
        else:
            messagebox.showerror("路径错误", f"图片路径格式不正确：{raw}")
            return None
    else:
        if "外置配置文件夹" in raw:
            idx = raw.find("外置配置文件夹")
            sub_path = raw[idx:]
            parts = sub_path.split("外置配置文件夹", 1)
            relative_protrail = parts[1].lstrip("\\/")
            abs_path = 工作目录 / relative_protrail
        else:
            messagebox.showerror("路径错误",
                                 f"图片路径必须位于“外置配置文件夹”内，无法识别：{raw}")
            return None

    if not abs_path.exists():
        messagebox.showerror("文件缺失",
                             f"模板图片不存在：{abs_path}\n请检查路径是否正确。")
        return None

    return f"外置配置文件夹\\{relative_protrail}"


def 获取完整图片路径(相对路径: str) -> Path:
    """根据标准化后的相对路径返回绝对路径"""
    parts = 相对路径.split("外置配置文件夹", 1)
    if len(parts) == 2:
        sub = parts[1].lstrip("\\/")
        return 工作目录 / sub
    else:
        return 工作目录 / 相对路径


# ===================== 指令解析（修改循环解析部分） =====================
def _parse_instructions(所有行):
    """
    解析支持识图、条件、跳出循环的指令列表
    循环指令格式：
        循环 <数字>            -> 次数循环
        循环 <数字>s           -> 时间循环
        循环结束
    识图指令格式：
        识图并返回匹配结果与x与y (x1,y1,x2,y2) 相似度 "路径"
    """
    指令列表 = []
    for i, raw_line in enumerate(所有行):
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue

        # 循环开始（无名称）
        m = re.match(r'^\s*循环\s+(\d+(?:\.\d+)?)\s*(s)?\s*$', line)
        if m:
            num_str = m.group(1)
            suffix = m.group(2)  # None 或 's'
            if suffix:  # 时间循环
                dur = float(num_str)
                if dur <= 0:
                    dur = 0
                指令列表.append(('loop_start', 'time', dur, i))
            else:  # 次数循环
                cnt = int(float(num_str))  # 允许浮点数但转为整数
                if cnt <= 0:
                    cnt = 0
                指令列表.append(('loop_start', 'count', cnt, i))
            continue

        # 循环结束
        if re.match(r'^\s*循环结束\s*$', line):
            指令列表.append(('loop_end', i))
            continue

        # 识图指令
        m = re.match(r'^识图并返回匹配结果与x与y\s+\((\d+)\s*[,，]\s*(\d+)\s*[,，]\s*(\d+)\s*[,，]\s*(\d+)\)\s+([\d.]+)\s+"(.+)"$', line)
        if m:
            x1 = int(m.group(1))
            y1 = int(m.group(2))
            x2 = int(m.group(3))
            y2 = int(m.group(4))
            threshold = float(m.group(5))
            path = m.group(6).strip()

            width = x2 - x1
            height = y2 - y1
            if width <= 0 or height <= 0:
                raise Exception(f"识图区域无效：({x1},{y1},{x2},{y2}) 宽或高为非正数（行{i+1}）")

            指令列表.append(('match', (x1, y1, width, height), threshold, path, i))
            continue

        # 条件开始
        if re.match(r'^匹配结果为真则\s*$', line):
            指令列表.append(('cond_start', 'true', i))
            continue
        if re.match(r'^匹配结果为假则\s*$', line):
            指令列表.append(('cond_start', 'false', i))
            continue

        # 条件结束
        if re.match(r'^匹配结果为真条件结束\s*$', line):
            指令列表.append(('cond_end', 'true', i))
            continue
        if re.match(r'^匹配结果为假条件结束\s*$', line):
            指令列表.append(('cond_end', 'false', i))
            continue

        # 跳出循环
        if re.match(r'^跳出循环\s*$', line):
            指令列表.append(('break_loop', i))
            continue

        # 普通动作
        指令列表.append(('action', line, i))

    # 配对检查：循环（无名称，仅校验括号匹配）
    loop_end_of_start = {}
    start_of_loop_end = {}
    loop_stack = []  # 只存储开始指令的索引
    for idx, inst in enumerate(指令列表):
        if inst[0] == 'loop_start':
            loop_stack.append(idx)
        elif inst[0] == 'loop_end':
            if not loop_stack:
                raise Exception(f"循环结束没有对应的开始（行{inst[1] + 1}）")
            start_idx = loop_stack.pop()
            loop_end_of_start[start_idx] = idx
            start_of_loop_end[idx] = start_idx
    if loop_stack:
        raise Exception(f"存在未结束的循环，开始位置：{[i+1 for i in loop_stack]}")

    # 条件配对（保持不变）
    cond_end_of_start = {}
    start_of_cond_end = {}
    cond_stack = []
    for idx, inst in enumerate(指令列表):
        if inst[0] == 'cond_start':
            cond_stack.append((inst[1], idx))
        elif inst[0] == 'cond_end':
            typ = inst[1]
            if not cond_stack:
                raise Exception(f"条件结束“{typ}”没有对应的开始（行{inst[2] + 1}）")
            top_typ, start_idx = cond_stack.pop()
            if top_typ != typ:
                raise Exception(f"条件结束“{typ}”与开始“{top_typ}”不匹配（行{inst[2] + 1}）")
            cond_end_of_start[start_idx] = idx
            start_of_cond_end[idx] = start_idx
    if cond_stack:
        raise Exception(f"存在未结束的条件：{[t for t, _ in cond_stack]}")

    return 指令列表, loop_end_of_start, start_of_loop_end, cond_end_of_start, start_of_cond_end


# ===================== 模板预加载 =====================
def 预加载模板(指令列表, 窗口矩形):
    """提前加载所有模板"""
    配置字典 = {}
    for inst in 指令列表:
        if inst[0] == 'match':
            rel_path = inst[3]
            abs_path = 获取完整图片路径(rel_path)
            abs_str = str(abs_path)
            if abs_str not in 配置字典:
                try:
                    配置 = 根据模版路径返回配置元组(abs_str, False, 窗口矩形)
                    配置字典[abs_str] = 配置
                except Exception as e:
                    messagebox.showerror("模板加载失败",
                                         f"加载模板失败：{abs_str}\n错误：{e}")
                    return None
    return 配置字典

def 去除注释(文本: str) -> str:
    """移除脚本中的注释块，注释格式：#注释内容...结尾的#"""
    行列表 = 文本.splitlines()
    结果行 = []
    注释中 = False
    for line in 行列表:
        stripped = line.strip()
        if 注释中:
            # 处于注释块内，一直跳过直到遇到以#结尾的行
            if stripped.endswith('#'):
                注释中 = False
            continue
        else:
            # 不在注释块内
            if stripped.startswith('#') and not stripped.endswith('#'):
                # 多行注释开始
                注释中 = True
                continue
            elif stripped.startswith('#') and stripped.endswith('#'):
                # 单行注释
                continue
            elif stripped.endswith('#'):
                # 以#结尾但不是以#开头，可能是孤立的多行注释结束行（防止边界异常）
                continue
            else:
                # 正常指令行
                结果行.append(line)
    return '\n'.join(结果行)
# ===================== 主执行引擎 =====================
def 执行脚本内容(句柄, 窗口矩形, 线程事件, 脚本内容: str):
    """执行完整脚本，包含坐标转换处理"""
    # ---------- 第一步：预处理脚本内容，标准化图片路径 ----------
    脚本内容=去除注释(脚本内容)
    lines = 脚本内容.splitlines()
    processed_lines = []
    for line in lines:
        m = re.match(r'^(识图并返回匹配结果与x与y\s+\(\d+\s*[,，]\s*\d+\s*[,，]\s*\d+\s*[,，]\s*\d+\)\s+[\d.]+\s+)"([^"]+)"', line)
        if m:
            prefix = m.group(1)
            original_path = m.group(2)
            new_path = 标准化图片路径(original_path)
            if new_path is None:
                messagebox.showerror("路径错误", f"脚本中识图指令的图片路径无效，已终止执行。\n原始行：{line}")
                return
            line = f'{prefix}"{new_path}"'
        processed_lines.append(line)

    脚本内容 = "\n".join(processed_lines)

    # ---------- 第二步：解析指令 ----------
    所有行 = 脚本内容.strip().splitlines()
    try:
        指令列表, loop_end_of_start, start_of_loop_end, cond_end_of_start, start_of_cond_end = _parse_instructions(所有行)
    except Exception as e:
        messagebox.showerror("脚本语法错误", f"脚本解析失败：{e}")
        return

    # 初始化识图结果变量
    match_result = False
    match_x = 0
    match_y = 0

    # 预加载模板
    模板配置字典 = 预加载模板(指令列表, 窗口矩形)
    if 模板配置字典 is None:
        messagebox.showerror("初始化失败", "模板预加载失败，无法执行脚本。")
        return

    # 运行时状态
    循环栈 = []  # 每个元素为 (类型, 数据, 开始索引)  类型: 'count'或'time'
    break_level = 0
    PC = 0

    while PC < len(指令列表):
        if not 线程事件.is_set():
            print("脚本被中断。")
            return

        inst = 指令列表[PC]

        # 跳出循环处理
        if break_level > 0:
            if inst[0] == 'loop_start':
                PC = loop_end_of_start[PC] + 1
                continue
            elif inst[0] == 'cond_start':
                PC = cond_end_of_start[PC] + 1
                continue
            elif inst[0] == 'loop_end':
                start_idx = start_of_loop_end[PC]
                # 从栈中移除对应的循环（必须是栈顶）
                if 循环栈 and 循环栈[-1][2] == start_idx:
                    循环栈.pop()
                else:
                    # 若不在栈顶，则从栈中删除指定项（理论上不会发生）
                    循环栈 = [entry for entry in 循环栈 if entry[2] != start_idx]
                break_level -= 1
                PC += 1
                continue
            elif inst[0] == 'cond_end':
                PC += 1
                continue
            else:
                PC += 1
                continue

        typ = inst[0]

        if typ == 'action':
            line = inst[1]
            # 变量替换
            line = re.sub(r'\bx\b', str(match_x), line)
            line = re.sub(r'\by\b', str(match_y), line)
            print(f"执行行 {inst[2] + 1}: {line}")
            try:
                执行脚本行(句柄, 窗口矩形, 线程事件, line)
            except Exception as e:
                messagebox.showerror("动作执行错误", f"执行行 {inst[2] + 1} 出错：{line}\n错误：{e}")
            PC += 1

        elif typ == 'loop_start':
            ltype = inst[1]   # 'count' or 'time'
            param = inst[2]   # 次数 或 时长秒数
            start_idx = inst[3]
            if param <= 0:
                PC = loop_end_of_start[PC] + 1
                continue
            if ltype == 'count':
                print(f"→ 进入次数循环 (剩余次数:{param})")
                循环栈.append(('count', param, start_idx))
            else:
                deadline = time.time() + param
                print(f"→ 进入时间循环 (时长:{param}秒)")
                循环栈.append(('time', deadline, start_idx))
            PC += 1

        elif typ == 'loop_end':
            if not 循环栈:
                messagebox.showerror("循环错误", f"意外的循环结束（行{inst[1] + 1}）")
                return
            ltype, data, start_idx = 循环栈[-1]

            if ltype == 'count':
                remaining = data
                if remaining > 1:
                    print(f"↻ 次数循环 还剩 {remaining - 1} 次")
                    循环栈[-1] = ('count', remaining - 1, start_idx)
                    PC = start_idx + 1   # 跳回循环开始的下一条指令（即循环体开始）
                else:
                    print(f"← 退出次数循环")
                    循环栈.pop()
                    PC += 1
            else:  # time
                deadline = data
                if time.time() < deadline:
                    循环栈[-1] = ('time', deadline, start_idx)
                    PC = start_idx + 1
                else:
                    print(f"← 退出时间循环 (已超时)")
                    循环栈.pop()
                    PC += 1

        elif typ == 'cond_start':
            cond_type = inst[1]
            if cond_type == 'true' and not match_result:
                PC = cond_end_of_start[PC] + 1
                continue
            elif cond_type == 'false' and match_result:
                PC = cond_end_of_start[PC] + 1
                continue
            PC += 1

        elif typ == 'cond_end':
            PC += 1

        elif typ == 'match':
            region = inst[1]
            threshold = inst[2]
            img_path = inst[3]
            abs_path = 获取完整图片路径(img_path)
            abs_str = str(abs_path)
            配置 = 模板配置字典.get(abs_str)
            if not 配置:
                messagebox.showerror("模板缺失", f"未找到模板配置：{img_path}")
                match_result = False
                match_x = match_y = 0
            else:
                背景数组 = 函数截图到内存直接返回NumPy数组(句柄, 窗口矩形)
                if 背景数组 is not None:
                    try:
                        is_match, max_val, mx, my = 函数_在指定区域数组匹配(背景数组, region, threshold, 配置)
                        match_result = is_match
                        match_x = mx
                        match_y = my
                    except Exception as e:
                        messagebox.showerror("识图异常", f"识图过程出错：{e}")
                        match_result = False
                        match_x = match_y = 0
                else:
                    messagebox.showerror("截图失败", "无法获取游戏画面截图。")
                    match_result = False
                    match_x = match_y = 0
            PC += 1

        elif typ == 'break_loop':
            print("触发跳出循环")
            break_level = 1
            PC += 1

        else:
            print(f"未知指令类型：{inst}")
            PC += 1

    print("脚本执行完毕。")

