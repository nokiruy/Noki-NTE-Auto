import numpy as np
from tkinter import messagebox
import cv2
import tkinter as tk
import os
from PIL import Image
import time
import logging

logger = logging.getLogger(__name__)




def 函数_在指定区域内进行模板匹配返回横坐标范围(背景图片数据, 限定区域, 模板路径, 最低相似度):
    """
    在背景图片的指定区域内进行模板匹配，并返回匹配结果。

    返回:
        (是否匹配, max_val, 最小x, 最小y, 最大x, 最大y)
        其中：
        - 是否匹配: bool，是否有至少一个匹配点满足最低相似度
        - max_val: float，匹配结果中最高相似度
        - 最小x, 最小y, 最大x, 最大y: int，所有满足阈值的匹配位置构成的包围矩形（右下角已包含模板尺寸）
    """

    # 检查模板图片路径是否存在
    if not os.path.exists(模板路径):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("路径错误", f"模板图片文件不存在: {模板路径}")
        return False, 0, 0, 0, 0, 0

    # 加载背景图片（从内存数据）
    背景图片 = cv2.imdecode(np.frombuffer(背景图片数据, dtype=np.uint8), cv2.IMREAD_COLOR)
    if 背景图片 is None:
        error_message = "背景图片加载失败"
        print(error_message)
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("背景图片加载失败", error_message)
        return False, 0, 0, 0, 0, 0

    try:
        with Image.open(模板路径) as img:
            模板图片 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        error_message = f"模板图片加载失败: {模板路径}, 错误信息: {e}"
        print(error_message)
        错误信息 = f"模板匹配文件不存在: {error_message}"
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("路径错误", 错误信息)
        return False, 0, 0, 0, 0, 0

    if 模板图片 is None:
        error_message = f"路径中有中文或者错误: {模板路径}"
        print(error_message)
        错误信息 = f"模板匹配文件不存在或者路径中有中文: {error_message}"
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("路径错误", 错误信息)
        return False, 0, 0, 0, 0, 0

    # 提取限定区域
    x坐标, y坐标, 宽度, 高度 = 限定区域
    限定区域图片 = 背景图片[y坐标:y坐标 + 高度, x坐标:x坐标 + 宽度]

    # 确保模板尺寸小于限定区域尺寸
    if 模板图片.shape[0] > 限定区域图片.shape[0] or 模板图片.shape[1] > 限定区域图片.shape[1]:
        root = tk.Tk()
        root.withdraw()
        print(f"模板尺寸 {模板图片.shape} 大于限定区域尺寸 {限定区域图片.shape}，{模板路径}")
        messagebox.showinfo("严重警告",
                            f"模板尺寸必须小于或等于限定区域尺寸,模板尺寸 {模板图片.shape} 大于限定区域尺寸 {限定区域图片.shape}，{模板路径}")
        time.sleep(2)
        return False, 0, 0, 0, 0, 0

    # 模板匹配
    匹配结果 = cv2.matchTemplate(限定区域图片, 模板图片, cv2.TM_CCOEFF_NORMED)

    # 找出所有满足最低相似度的匹配位置
    匹配位置 = np.where(匹配结果 >= 最低相似度)

    if len(匹配位置[0]) == 0:
        # 没有任何点满足阈值
        是否匹配 = False
        max_val = float(np.max(匹配结果))  # 仍然给出最高相似度供参考
        最小x, 最小y, 最大x, 最大y = 0, 0, 0, 0
    else:
        # 获取最高相似度
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(匹配结果)

        # all matched positions (relative to limited region)
        loc_x = 匹配位置[1]
        loc_y = 匹配位置[0]

        # 转换为原图坐标
        abs_x = loc_x + x坐标
        abs_y = loc_y + y坐标

        # 包围矩形的左上角为最小x,y，右下角为最大x,y + 模板尺寸
        最小x = int(np.min(abs_x))
        最小y = int(np.min(abs_y))
        最大x = int(np.max(abs_x) + 模板图片.shape[1])
        最大y = int(np.max(abs_y) + 模板图片.shape[0])

        是否匹配 = True

    # 路径提取（与原逻辑一致）
    路径部分 = str(模板路径)
    if "图片" in 路径部分:
        路径部分 = 路径部分.split(r"图片")
        if 路径部分:
            提取内容 = 路径部分[1]
        else:
            提取内容 = 模板路径
    else:
        提取内容 = 模板路径

    if 是否匹配:
        logger.info(
            f"✅ 匹配成功，路径：{提取内容},模板: {模板图片.shape},限定: {限定区域图片.shape},"
            f"相似: {max_val:.2f},区域: ({最小x},{最小y})-({最大x},{最大y})")
    else:
        logger.error(
            f"❌ 无匹配点满足阈值，路径：{提取内容},模板: {模板图片.shape},限定: {限定区域图片.shape},"
            f"最高相似: {max_val:.2f}")

    return 是否匹配, max_val, 最小x, 最小y, 最大x, 最大y



def 函数_在指定区域内进行模板匹配(背景图片数据, 限定区域, 模板路径, 最低相似度):
    """
    在背景图片的指定区域内进行模板匹配，并返回匹配结果。
    """
    # 检查模板图片路径是否存在
    if not os.path.exists(模板路径):
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror("路径错误", f"模板图片文件不存在: {模板路径}")
        return False, 0, 0, 0

    # 加载背景图片（从内存数据）
    背景图片 = cv2.imdecode(np.frombuffer(背景图片数据, dtype=np.uint8), cv2.IMREAD_COLOR)
    if 背景图片 is None:
        error_message = "背景图片加载失败"
        print(error_message)
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror("背景图片加载失败", error_message)
        return False, 0, 0, 0
    try:
        with Image.open(模板路径) as img:
            模板图片 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        error_message = f"模板图片加载失败: {模板路径}, 错误信息: {e}"
        print(error_message)
        错误信息 = f"模板匹配文件不存在或者路径中有中文: {error_message}"
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror("路径错误", 错误信息)

        return False, 0, 0, 0

    if 模板图片 is None:
        error_message = f"路径中有中文或者错误: {模板路径}"
        print(error_message)
        错误信息 = f"模板匹配文件不存在或者路径中有中文: {error_message}"
        # 弹窗提示
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror("路径错误", 错误信息)
        return False, 0, 0, 0

    # 提取限定区域
    x坐标, y坐标, 宽度, 高度 = 限定区域
    限定区域图片 = 背景图片[y坐标:y坐标 + 高度, x坐标:x坐标 + 宽度]

    # 打印尺寸进行调试
    # print(f"模板尺寸: {模板图片.shape}")
    # print(f"限定区域尺寸: {限定区域图片.shape}")

    # 确保模板尺寸小于限定区域尺寸
    if 模板图片.shape[0] > 限定区域图片.shape[0] or 模板图片.shape[1] > 限定区域图片.shape[1]:
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        print(f"模板尺寸 {模板图片.shape} 大于限定区域尺寸 {限定区域图片.shape}，{模板路径}")
        messagebox.showinfo("严重警告",
                            f"模板尺寸必须小于或等于限定区域尺寸,模板尺寸 {模板图片.shape} 大于限定区域尺寸 {限定区域图片.shape}，{模板路径}")
        time.sleep(2)
        是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = (False, 0, 0, 0)
    else:
        # 模板匹配
        匹配结果 = cv2.matchTemplate(限定区域图片, 模板图片, cv2.TM_CCOEFF_NORMED)

        # 获取最值
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(匹配结果)

        # 计算最大匹配坐标
        最大匹配x坐标 = max_loc[0] + x坐标
        最大匹配y坐标 = max_loc[1] + y坐标

        # 判断是否匹配成功
        是否匹配 = max_val >= 最低相似度
        路径部分 = str(模板路径)
        # 使用 split 方法将路径按反斜杠分割
        if "图片" in 路径部分:
            路径部分 = 路径部分.split(r"图片")  # 以 "图片\" 为分隔符
            # 如果路径中包含 "图片\"，则提取后面的部分
            if 路径部分:
                提取内容 = 路径部分[1]  # 获取 "图片\" 后面的内容
            else:
                提取内容 = 模板路径  # 如果没有找到 "图片\"，则返回原路径
        else:
            提取内容 = 模板路径

        if 是否匹配:
            # 输出结果

            print(
                f"✅ 匹配成功，路径：{提取内容},模板: {模板图片.shape},限定: {限定区域图片.shape},"
                f"相似: {max_val:.2f},坐标: ({最大匹配x坐标}, {最大匹配y坐标})")
        else:
            print(
                f"❌ 匹配失败，路径：{提取内容},模板: {模板图片.shape},限定: {限定区域图片.shape},"
                f"相似: {max_val:.2f},坐标: ({最大匹配x坐标}, {最大匹配y坐标})")

    return 是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标
