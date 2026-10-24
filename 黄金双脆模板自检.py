# -*- coding: utf-8 -*-
"""
黄金双脆 模板自检小工具（可选，不参与正式流程）

作用：
    不点游戏、不动游戏，只截一张图，然后用 异环图片/黄金双脆 下的四个模板，
    在程序里真正使用的限定区域中跑一遍匹配，把相似度和坐标打印出来，
    并保存一张画了红框的结果图。用来确认模板在你自己机器上是否还认得出。

用法：
    1. 把本文件放在 main.py 同目录（也就是异环图片、外置配置文件夹所在目录）
    2. 游戏打开并停在对应界面（活动页 / 匹配页 / 对局中 / 结算页）
    3. 运行：python 黄金双脆模板自检.py
    4. 看输出，或直接看生成的 黄金双脆自检结果.png

判定标准：
    相似度 >= 0.85 绿灯（程序里用的阈值）
    0.80 ~ 0.85    黄灯（能跑但容易漏）
    < 0.80         红灯，需要重新截这个模板
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import win32gui

current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from 游戏截图保存到内存 import 函数截图到内存直接返回NumPy数组  # noqa: E402
from opencv模板匹配找图 import 函数_在指定区域数组匹配, 根据模版路径返回配置元组  # noqa: E402

相似度阈值 = 0.85

# 与 异环任务.黄金双脆挂机 里完全一致的限定区域（1280x720 客户区坐标）
检测项 = [
    ("前往",       (940, 590, 340, 130), "活动页右下角【前往】"),
    ("开始匹配",   (940, 590, 340, 130), "匹配页右下角【开始匹配】"),
    ("确认",       (640, 410, 320, 120), "ESC 后弹窗里的【确认】（只截文字，避开取消）"),
    ("离开",       (940, 590, 340, 130), "结算页右下角【离开】"),
    ("对局中ESC",  (0, 0, 120, 110),     "对局左上角 ESC 图标"),
]


def 读取端游列表():
    try:
        with open(current_dir / "game.json", "r", encoding="utf-8") as f:
            return json.load(f).get("端游列表", [])
    except Exception:
        return [["UnrealWindow", "NTE  "], ["UnrealWindow", "异环  "]]


def 标题是否匹配(标题, 目标):
    标题 = 标题.strip()
    目标 = 目标.strip()
    if not 目标:
        return True
    if "*" in 目标:
        前缀, 后缀 = 目标.split("*", 1)
        return 标题.startswith(前缀) and 标题.endswith(后缀)
    return 标题 == 目标


def 查找游戏窗口():
    端游列表 = 读取端游列表()
    结果 = []

    def 回调(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        标题 = win32gui.GetWindowText(hwnd)
        类名 = win32gui.GetClassName(hwnd)
        for 目标类名, 目标标题 in 端游列表:
            if 目标类名 and not 目标类名胜配(类名, 目标类名):
                continue
            if 标题是否匹配(标题, 目标标题):
                结果.append((hwnd, 类名, 标题))
                return

    win32gui.EnumWindows(回调, None)
    return 结果


def 目标类名胜配(类名, 目标类名):
    目标类名 = 目标类名.strip()
    if not 目标类名:
        return True
    if "*" in 目标类名:
        前缀, 后缀 = 目标类名.split("*", 1)
        return 类名.startswith(前缀) and 类名.endswith(后缀)
    return 类名 == 目标类名


def 获取客户区矩形(hwnd):
    左, 上, 右, 下 = win32gui.GetClientRect(hwnd)
    坐标 = win32gui.ClientToScreen(hwnd, (左, 上))
    坐标2 = win32gui.ClientToScreen(hwnd, (右, 下))
    return (坐标[0], 坐标[1], 坐标2[0], 坐标2[1])


def 主流程():
    候选 = 查找游戏窗口()
    if not 候选:
        print("没找到游戏窗口。请先打开游戏（NTE / 异环），再运行本脚本。")
        return
    hwnd, 类名, 标题 = 候选[0]
    矩形 = 获取客户区矩形(hwnd)
    宽 = 矩形[2] - 矩形[0]
    高 = 矩形[3] - 矩形[1]
    print(f"游戏窗口：{类名} / {标题}")
    print(f"客户区：{宽}x{高}，矩形={矩形}")
    if (宽, 高) != (1280, 720):
        print("⚠ 客户区不是 1280x720，正式任务也会因分辨率不符而拒绝运行，"
              "请先把游戏分辨率调成 1280x720。以下结果仅供参考。")

    背景图片 = 函数截图到内存直接返回NumPy数组(hwnd, 矩形)
    if 背景图片 is None:
        print("截图失败")
        return
    print(f"截图尺寸：{背景图片.shape[1]}x{背景图片.shape[0]}")
    标注图 = 背景图片.copy()

    图片目录 = current_dir / "异环图片" / "黄金双脆"
    命中名单 = []
    for 名称, 区域, 说明 in 检测项:
        模板路径 = 图片目录 / f"{名称}.png"
        if not 模板路径.is_file():
            print(f"[缺图] {名称}.png 不存在：{模板路径}")
            continue
        配置元组 = 根据模版路径返回配置元组(模板路径, False, 矩形)
        if 配置元组[1] is None:
            continue
        是否匹配, 相似度, x, y = 函数_在指定区域数组匹配(
            背景图片=背景图片, 限定区域=区域, 最低相似度=相似度阈值, 配置列表=配置元组)
        模板高, 模板宽 = 配置元组[1].shape[:2]
        灯 = "绿灯" if 相似度 >= 相似度阈值 else ("黄灯" if 相似度 >= 0.80 else "红灯")
        print(f"[{灯}] {名称:8s} 相似度={相似度:.4f}  中心=({x + 模板宽 // 2},{y + 模板高 // 2})  {说明}")
        if 相似度 >= 0.80:
            命中名单.append(名称)
            颜色 = (0, 200, 0) if 相似度 >= 相似度阈值 else (0, 165, 255)
        else:
            颜色 = (0, 0, 255)
        cv2.rectangle(标注图, (x, y), (x + 模板宽, y + 模板高), 颜色, 2)
        cv2.putText(标注图, f"{名称} {相似度:.2f}", (x, max(14, y - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, 颜色, 1, cv2.LINE_AA)
        cv2.rectangle(标注图, (区域[0], 区域[1]),
                      (区域[0] + 区域[2], 区域[1] + 区域[3]), (128, 128, 128), 1)

    输出路径 = current_dir / "黄金双脆自检结果.png"
    cv2.imencode(".png", 标注图)[1].tofile(str(输出路径))
    print(f"\n标注图已保存：{输出路径}")
    if 命中名单:
        print(f"当前界面识别到：{'、'.join(命中名单)}")
        if len(命中名单) > 1:
            print("⚠ 同一张图命中多个模板，说明模板区分度不够，容易误判，请重截。")
    else:
        print("当前界面没认出任何模板：请确认游戏就停在对应界面，"
              "或按上面的红灯提示重新截图。")


if __name__ == "__main__":
    主流程()
    try:
        input("\n按回车键退出...")
    except EOFError:
        pass
