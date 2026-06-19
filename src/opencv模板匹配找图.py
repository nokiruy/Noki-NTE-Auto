import numpy as np
from tkinter import messagebox
import cv2
import tkinter as tk
import os
from PIL import Image
import time
import logging

from pathlib import Path
import re
logger = logging.getLogger("database")
GPU_BLACKLIST = [
    "月卡.png",
    "点击任意位置继续.png"
]



def 根据模版路径返回配置元组(模板路径, 检测是否符合GPU加速, 游戏窗口矩形=None):
    """
    加载模板，并根据游戏窗口实际分辨率自动寻找最佳适配图片。
    返回：(最终模板路径, 模板图片, 是否开启GPU加速, 图片要求分辨率, 限定区域要求分辨率)
    """
    # ------------------ 解析原始模板路径 ------------------
    原始路径 = Path(模板路径)
    目录 = 原始路径.parent
    stem = 原始路径.stem       # 例：对话 或 对话_1920x1080
    suffix = 原始路径.suffix   # 例：.png
    最终模板路径 = 模板路径
    图片要求分辨率 = None      # 模板对应的原始分辨率
    限定区域要求分辨率 = None  # 用于限定区域缩放的分辨率参考

    # 判断传入的模板路径是否自身带有分辨率信息（如 对话_1920x1080.png）
    自带分辨率匹配 = re.search(r'_(\d+)x(\d+)$', stem)
    if 自带分辨率匹配:
        自带宽 = int(自带分辨率匹配.group(1))
        自带高 = int(自带分辨率匹配.group(2))
        基础stem = stem[:-len(自带分辨率匹配.group(0))]  # 真实的 stem，如“对话”
    else:
        基础stem = stem
        自带宽, 自带高 = None, None  # 未自带分辨率时无默认值

    # ------------------ 根据游戏窗口矩形进行分辨率适配 ------------------
    if 游戏窗口矩形 is not None:
        游戏宽 = 游戏窗口矩形[2] - 游戏窗口矩形[0]
        游戏高 = 游戏窗口矩形[3] - 游戏窗口矩形[1]
        if 游戏宽 > 0 and 游戏高 > 0:
            游戏分辨率 = (游戏宽, 游戏高)

            # 收集所有候选图片（包括自身）
            if 自带分辨率匹配:
                # 若传入模板自带分辨率，使用基础 stem 搜索同系列图片
                pattern = f"{基础stem}_*x*{suffix}"
            else:
                # 若不携带分辨率，则 stem 即为 base，但自身可能无分辨率信息，这里按原逻辑仅搜索带分辨率的
                pattern = f"{stem}_*x*{suffix}"

            候选文件 = list(目录.glob(pattern))
            候选列表 = []

            for f in 候选文件:
                # 提取文件名中的分辨率
                f_stem = f.stem
                # 需要安全地提取末尾的 _WIDTHxHEIGHT
                # 先确定 base_stem：如果原始 stem 自带分辨率就用 基础stem，否则用 stem
                base = 基础stem if 自带分辨率匹配 else stem
                if not f_stem.startswith(base):
                    continue
                remainder = f_stem[len(base):]  # 例如 _1920x1080
                match = re.search(r'_?(\d+)x(\d+)$', remainder)
                if match:
                    w = int(match.group(1))
                    h = int(match.group(2))
                    候选列表.append((w, h, str(f)))

            if 候选列表:
                # ---------- 新排序策略：比例优先 → 可缩小优先 → 面积最接近 ----------
                def 排序键(item):
                    w, h, _ = item
                    # 1. 比例差异（越小越好）
                    比例差 = abs(游戏宽/游戏高 - w/h) if 游戏高 and h else float('inf')
                    # 2. 是否可缩小（True=可缩小，False=需放大）
                    可缩小 = (w * h) >= (游戏宽 * 游戏高)
                    # 3. 面积差异（越小越接近，当同比例且同为缩小/放大时进一步优选）
                    面积差 = abs(w * h - 游戏宽 * 游戏高)
                    # not 可缩小 使得可缩小(True→0)排在需放大(False→1)前面
                    return (比例差, not 可缩小, 面积差)

                候选列表.sort(key=排序键)
                最佳宽, 最佳高, 选中路径 = 候选列表[0]
                最终模板路径 = 选中路径
                图片要求分辨率 = [最佳宽, 最佳高]
                限定区域要求分辨率 = [最佳宽, 最佳高]  # 如果后续需要缩放限定区域
                print(f"选中最佳匹配: {最终模板路径} (分辨率 {最佳宽}x{最佳高})")

                # 如果选中的是自身且自身与游戏分辨率不匹配，依旧会进行后续缩放
                # 若选中的恰好是精确匹配，则后续缩放步骤会发现分辨率相等而跳过缩放
            else:
                print("未找到其他分辨率图片，将继续使用传入模板并缩放")
                # 此时若自带分辨率，就用自带的作为要求分辨率
                if 自带分辨率匹配:
                    图片要求分辨率 = [自带宽, 自带高]
                    限定区域要求分辨率 = [自带宽, 自带高]

    # ------------------ 加载模板图片 ------------------
    try:
        with Image.open(最终模板路径) as img:
            模板图片 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"模板图片加载失败: {最终模板路径}, {e}")
        messagebox.showerror("路径错误", f"模板匹配文件不存在: {最终模板路径}")
        return 最终模板路径, None, False, None, None

    if 模板图片 is None:
        return 最终模板路径, None, False, None, None

    # ------------------ 根据图片要求分辨率与游戏分辨率的差异进行缩放 ------------------
    if 游戏窗口矩形 is not None and 图片要求分辨率 is not None:
        游戏分辨率 = [游戏宽, 游戏高]
        if 游戏分辨率 != 图片要求分辨率:
            src_w, src_h = 图片要求分辨率
            dst_w, dst_h = 游戏分辨率
            if src_w <= 0 or src_h <= 0:
                print(f"错误：模板原始分辨率无效 {图片要求分辨率}")
                return 最终模板路径, 模板图片, False, None, 限定区域要求分辨率

            scale_x = dst_w / src_w
            scale_y = dst_h / src_h
            h, w = 模板图片.shape[:2]
            new_w = int(round(w * scale_x))
            new_h = int(round(h * scale_y))

            if new_w < 5 or new_h < 5:
                print(f"缩放后模板尺寸过小 ({new_w}, {new_h})，放弃缩放")
            else:
                模板图片 = cv2.resize(模板图片, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
                print(f"模板已缩放: {最终模板路径} {w}x{h} → {new_w}x{new_h} "
                      f"(游戏分辨率 {游戏分辨率} vs 模板分辨率 {图片要求分辨率})")

    # ------------------ GPU 加速可行性检测 ------------------
    if 检测是否符合GPU加速 and 模板图片 is not None and cv2.ocl.haveOpenCL():
        if Path(最终模板路径).name in GPU_BLACKLIST:
            print(f"{最终模板路径} 位于 GPU 黑名单，强制使用 CPU")
            是否开启GPU加速 = False
        else:
            h, w = 模板图片.shape[:2]
            if w >= 16 and h >= 16 and w * h >= 256:
                是否开启GPU加速 = True
                print(f"{最终模板路径}支持GPU加速识图，图片大小：{模板图片.shape[:2]}")
            else:
                print(f"{最终模板路径}不支持GPU加速识图，图片大小：{模板图片.shape[:2]}")
                是否开启GPU加速 = False
    else:
        是否开启GPU加速 = False

    return 最终模板路径, 模板图片, 是否开启GPU加速, 游戏窗口矩形, 限定区域要求分辨率
def _gpu_match_template(image, templ, method, use_gpu,模版路径):
    """
    智能选择 GPU/CPU 进行模板匹配。
    当 GPU 返回可疑结果（如 1.00）时，自动回退 CPU 验证。
    """
    if use_gpu and cv2.ocl.haveOpenCL():
        # 确保内存连续
        if not image.flags['C_CONTIGUOUS']:
            image = np.ascontiguousarray(image)
        if not templ.flags['C_CONTIGUOUS']:
            templ = np.ascontiguousarray(templ)

        # 尝试 GPU 匹配
        result_um = cv2.matchTemplate(cv2.UMat(image), cv2.UMat(templ), method)
        result_gpu = result_um.get()

        # 获取 GPU 结果中的最大值
        min_val, max_val, _, _ = cv2.minMaxLoc(result_gpu)

        # 如果 GPU 返回了可疑的 1.00（可能是 OpenCL bug），回退 CPU
        if max_val >= 0.9999:
            logger.warning(
                f"{模版路径}GPU 返回异常高相似度 {max_val:.4f}，回退 CPU 重新匹配以确保准确性"
            )
            result_cpu = cv2.matchTemplate(image, templ, method)
            _, max_val_cpu, _, _ = cv2.minMaxLoc(result_cpu)
            logger.info(f"{模版路径}CPU 匹配结果: {max_val_cpu:.4f}")
            return result_cpu

        return result_gpu

    # 默认：CPU 匹配
    return cv2.matchTemplate(image, templ, method)
def 函数_在指定区域数组匹配(背景图片, 限定区域, 最低相似度, 配置列表):
    """
    背景图片: numpy BGR 数组
    模板缓存: dict {路径: cv2 BGR 模板数组}，若提供则优先从中获取，避免重复加载
    使用GPU加速: 是否尝试使用 OpenCL GPU 加速（默认为 True）
    """

    开始时间=time.time()
    模板路径, 模板图片, 使用GPU加速,游戏窗口矩形,限定区域要求分辨率 = 配置列表
    if 背景图片 is None:
        print("[错误] 截图数据为空，跳过本次匹配")
        return False, 0, 0, 0

    # ------------------ 模板获取（从缓存或磁盘） -----------------

    try:
        if 背景图片.ndim == 3 and 背景图片.shape[2] == 3:
            pass  # 正常 BGR，直接使用
        elif 背景图片.ndim == 3 and 背景图片.shape[2] == 4:
            背景图片 = cv2.cvtColor(背景图片, cv2.COLOR_BGRA2BGR)  # BGRA → BGR
        elif 背景图片.ndim == 2:  # 灰度图
            背景图片 = cv2.cvtColor(背景图片, cv2.COLOR_GRAY2BGR)
        else:
            print(f"不支持的背景图片格式: ndim={背景图片.ndim}, shape={背景图片.shape}")
            return False, 0, 0, 0
    except Exception as e:
        print(e)
        return False, 0, 0, 0


    # ---------- 分辨率自适应：缩放限定区域 ----------
    # 提取限定区域
    x坐标, y坐标, 宽度, 高度 = 限定区域
    if 限定区域要求分辨率 is not None:
        限定宽, 限定高 = 限定区域要求分辨率
        # 获取当前背景图片的实际尺寸（注意：OpenCV 形状是 (高, 宽)）
        游戏宽 = 游戏窗口矩形[2] - 游戏窗口矩形[0]
        游戏高 = 游戏窗口矩形[3] - 游戏窗口矩形[1]
        if 限定宽 != 游戏宽 or 限定高 != 游戏高:
            scale_x = 游戏宽 / 限定宽
            scale_y = 游戏高 / 限定高
            x坐标 = int(round(x坐标 * scale_x))
            y坐标 = int(round(y坐标 * scale_y))
            宽度 = int(round(宽度 * scale_x))
            高度 = int(round(高度 * scale_y))

            # ---------- 增加边界保护 ----------
            背景高, 背景宽 = 背景图片.shape[:2]
            # 裁剪坐标，确保左上角不超出图片
            x坐标 = max(0, min(x坐标, 背景宽 - 1))
            y坐标 = max(0, min(y坐标, 背景高 - 1))
            # 裁剪尺寸，确保右下角不超出图片
            宽度 = min(宽度, 背景宽 - x坐标)
            高度 = min(高度, 背景高 - y坐标)
            # ---------------------------------

            print(f"限定区域已缩放: ({限定区域[0]},{限定区域[1]},{限定区域[2]},{限定区域[3]}) → ({x坐标},{y坐标},{宽度},{高度})")
    # ---------- 缩放结束 ----------
    限定区域图片 = 背景图片[y坐标:y坐标 + 高度, x坐标:x坐标 + 宽度]

    # 确保模板尺寸小于限定区域尺寸
    if 模板图片.shape[0] > 限定区域图片.shape[0] or 模板图片.shape[1] > 限定区域图片.shape[1]:
        root = tk.Tk()
        root.withdraw()
        print(f"模板尺寸 {模板图片.shape} 大于限定区域尺寸 {限定区域图片.shape}，{模板路径}")
        messagebox.showinfo(
            "严重警告",
            f"模板尺寸必须小于或等于限定区域尺寸,模板尺寸 {模板图片.shape} 大于限定区域尺寸 {限定区域图片.shape}，{模板路径}"
        )
        time.sleep(2)
        return False, 0, 0, 0

    # ---------- 核心改动：调用 GPU 加速匹配 ----------
    匹配结果 = _gpu_match_template(限定区域图片, 模板图片, cv2.TM_CCOEFF_NORMED, 使用GPU加速,模板路径)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(匹配结果)

    最大匹配x坐标 = max_loc[0] + x坐标
    最大匹配y坐标 = max_loc[1] + y坐标
    是否匹配 = max_val >= 最低相似度

    if 是否匹配:
        logger.info(
            f"✅ 匹配成功，路径：{模板路径},"
            f"相似: {max_val:.2f},坐标: ({最大匹配x坐标}, {最大匹配y坐标})，耗时：{(time.time()-开始时间):.4f},区域:{限定区域}，GPU加速:{使用GPU加速}")
    else:
        logger.error(
            f"❌ 匹配失败，路径：{模板路径},"
            f"相似: {max_val:.2f},坐标: ({最大匹配x坐标}, {最大匹配y坐标})，耗时：{(time.time()-开始时间):.4f},区域:{限定区域}，GPU加速:{使用GPU加速}")

    return 是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标




def 函数_在指定区域内进行模板匹配返回横坐标范围(
    背景图片, 限定区域,  最低相似度,  配置列表
):
    """
    在背景图片的指定区域内进行模板匹配，并返回匹配结果。

    参数:
        使用GPU加速: 是否尝试使用 OpenCL GPU 加速（默认为 True）

    返回:
        (是否匹配, max_val, 最小x, 最小y, 最大x, 最大y)
    """
    开始时间 = time.time()
    模板路径, 模板图片, 使用GPU加速,图片要求分辨率,限定区域要求分辨率 = 配置列表
    if 背景图片 is None:
        print("[错误] 截图数据为空，跳过本次匹配")
        return False, 0, 0, 0, 0, 0



    try:
        if 背景图片.ndim == 3 and 背景图片.shape[2] == 3:
            pass  # 正常 BGR，直接使用
        elif 背景图片.ndim == 3 and 背景图片.shape[2] == 4:
            背景图片 = cv2.cvtColor(背景图片, cv2.COLOR_BGRA2BGR)  # BGRA → BGR
        elif 背景图片.ndim == 2:  # 灰度图
            背景图片 = cv2.cvtColor(背景图片, cv2.COLOR_GRAY2BGR)
        else:
            print(f"不支持的背景图片格式: ndim={背景图片.ndim}, shape={背景图片.shape}")
            return False, 0, 0, 0, 0, 0
    except Exception as e:
        print(e)
        return False, 0, 0, 0, 0, 0
    # ------------------ 模板获取（从缓存或磁盘） ------------------
    if 模板图片 is None:
        print("从路径加载")
        if not os.path.exists(模板路径):
            messagebox.showerror("路径错误", f"模板图片文件不存在: {模板路径}")
            return False, 0, 0, 0
        try:
            with Image.open(模板路径) as img:
                模板图片 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"模板图片加载失败: {模板路径}, {e}")
            messagebox.showerror("路径错误", f"模板匹配文件不存在: {模板路径}")
            return False, 0, 0, 0

        # ---------- 分辨率自适应：缩放限定区域 ----------
        # 提取限定区域
    x坐标, y坐标, 宽度, 高度 = 限定区域
    if 限定区域要求分辨率 is not None and 图片要求分辨率 is not None:
        # 计算当前游戏的实际分辨率（从矩形中提取宽高）
        游戏宽,游戏高=限定区域要求分辨率
        src_w, src_h = 图片要求分辨率
        if 游戏宽 != src_w or 游戏高 != src_h:
            # 计算缩放比例（与模板缩放保持一致，使用浮点数）
            scale_x = 游戏宽 / src_w
            scale_y = 游戏高 / src_h
            # 将限定区域坐标映射到当前分辨率
            x坐标 = int(round(x坐标 * scale_x))
            y坐标 = int(round(y坐标 * scale_y))
            宽度 = int(round(宽度 * scale_x))
            高度 = int(round(高度 * scale_y))
            print(f"限定区域已缩放: ({限定区域[0]},{限定区域[1]},{限定区域[2]},{限定区域[3]}) → ({x坐标},{y坐标},{宽度},{高度})")
    # ---------- 缩放结束 ----------
    限定区域图片 = 背景图片[y坐标:y坐标 + 高度, x坐标:x坐标 + 宽度]

    if 模板图片.shape[0] > 限定区域图片.shape[0] or 模板图片.shape[1] > 限定区域图片.shape[1]:
        root = tk.Tk()
        root.withdraw()
        print(f"模板尺寸 {模板图片.shape} 大于限定区域尺寸 {限定区域图片.shape}，{模板路径}")
        messagebox.showinfo(
            "严重警告",
            f"模板尺寸必须小于或等于限定区域尺寸,模板尺寸 {模板图片.shape} 大于限定区域尺寸 {限定区域图片.shape}，{模板路径}"
        )
        time.sleep(2)
        return False, 0, 0, 0, 0, 0

    # ---------- 核心改动：调用 GPU 加速匹配 ----------
    匹配结果 = _gpu_match_template(限定区域图片, 模板图片, cv2.TM_CCOEFF_NORMED, 使用GPU加速,模板路径)

    # 找出所有满足最低相似度的匹配位置
    匹配位置 = np.where(匹配结果 >= 最低相似度)

    if len(匹配位置[0]) == 0:
        是否匹配 = False
        max_val = float(np.max(匹配结果))
        最小x, 最小y, 最大x, 最大y = 0, 0, 0, 0
    else:
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(匹配结果)

        loc_x = 匹配位置[1]
        loc_y = 匹配位置[0]

        abs_x = loc_x + x坐标
        abs_y = loc_y + y坐标

        最小x = int(np.min(abs_x))
        最小y = int(np.min(abs_y))
        最大x = int(np.max(abs_x) + 模板图片.shape[1])
        最大y = int(np.max(abs_y) + 模板图片.shape[0])

        是否匹配 = True




    if 是否匹配:
        logger.info(
            f"✅ 匹配成功，路径：{模板路径},"
            f"相似: {max_val:.2f},区域: ({最小x},{最小y})-({最大x},{最大y})，耗时：{(time.time()-开始时间):.4f},GPU加速:{使用GPU加速}")
    else:
        logger.error(
            f"❌ 无匹配点满足阈值，路径：{模板路径},耗时：{(time.time()-开始时间):.4f},GPU加速:{使用GPU加速}"
            f"最高相似: {max_val:.2f}")

    return 是否匹配, max_val, 最小x, 最小y, 最大x, 最大y

def 函数_在指定区域内进行模板匹配(背景图片数据, 限定区域, 模板路径, 最低相似度):
    """
    在背景图片的指定区域内进行模板匹配，并返回匹配结果。
    """
    if 背景图片数据 is None:
        # 打印日志以便定位
        logger.error("[错误] 截图数据为空，跳过本次匹配")
        return False, 0, 0, 0
    # start_time = time.time()
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
        logger.error(error_message)
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror("背景图片加载失败", error_message)
        return False, 0, 0, 0
    try:
        with Image.open(模板路径) as img:
            模板图片 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        error_message = f"模板图片加载失败: {模板路径}, 错误信息: {e}"
        logger.error(error_message)
        错误信息 = f"模板匹配文件不存在或者路径中有中文: {error_message}"
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror("路径错误", 错误信息)

        return False, 0, 0, 0

    if 模板图片 is None:
        error_message = f"路径中有中文或者错误: {模板路径}"
        logger.error(error_message)
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
        logger.error(f"模板尺寸 {模板图片.shape} 大于限定区域尺寸 {限定区域图片.shape}，{模板路径}")
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

            logger.info(
                f"✅ 匹配成功，路径：{提取内容},模板: {模板图片.shape},限定: {限定区域图片.shape},"
                f"相似: {max_val:.2f},坐标: ({最大匹配x坐标}, {最大匹配y坐标})")
        else:
            logger.error(
                f"❌ 匹配失败，路径：{提取内容},模板: {模板图片.shape},限定: {限定区域图片.shape},"
                f"相似: {max_val:.2f},坐标: ({最大匹配x坐标}, {最大匹配y坐标})")

    # print(f"截图完成（无裁剪），总耗时：{time.time() - start_time:.4f}秒")#返回结果
    return 是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标
def 函数_在指定区域内进行模板匹配多分辨率(背景图片数据, 限定区域, 模板路径, 最低相似度):
    """
    在背景图片的指定区域内进行模板匹配，并返回匹配结果。
    """

    # start_time = time.time()
    if not os.path.exists(模板路径):
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror("路径错误", f"模板图片文件不存在: {模板路径}")
        return False, 0, 0, 0

    背景图片 = cv2.imdecode(np.frombuffer(背景图片数据, dtype=np.uint8), cv2.IMREAD_COLOR)
    if 背景图片 is None:
        error_message = "背景图片加载失败"
        logger.error(error_message)
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror("背景图片加载失败", error_message)
        return False, 0, 0, 0
    try:
        with Image.open(模板路径) as img:
            模板图片 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        error_message = f"模板图片加载失败: {模板路径}, 错误信息: {e}"
        错误信息 = f"模板匹配文件不存在或者路径中有识别不了的字符: {error_message}"

        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror("路径错误", 错误信息)

        return False, 0, 0, 0

    if 模板图片 is None:
        error_message = f"路径中有中文或者错误: {模板路径}"
        错误信息 = f"模板匹配文件不存在或者路径中有识别不了的字符: {error_message}"
        print(错误信息)

        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror("路径错误", 错误信息)
        return False, 0, 0, 0
    基准宽度=1280
    基准高度=720
    背景高度, 背景宽度 = 背景图片.shape[:2]
    模板高度, 模板宽度 = 模板图片.shape[:2]

    宽度比例 = 背景宽度 / 基准宽度
    高度比例 = 背景高度 / 基准高度
    x坐标, y坐标, 宽度, 高度 = 限定区域
    需要缩放 = False
    if 背景宽度 > 基准宽度 and 背景高度 > 基准高度:
        背景图片 = cv2.resize(背景图片, (1280, 720), interpolation=cv2.INTER_AREA)
        logger.info(f"分辨率大于720p")
        需要缩放=True
    elif 背景宽度 < 基准宽度 and 背景高度 < 基准高度:
        模板图片 = cv2.resize(模板图片,(int(模板宽度 * 宽度比例), int(模板高度 * 高度比例)),interpolation=cv2.INTER_AREA)
        x坐标 = int(x坐标 * 宽度比例)
        y坐标 = int(y坐标 * 高度比例)
        宽度 = int(宽度 * 宽度比例)
        高度 = int(高度 * 高度比例)
        logger.info(f"分辨率小于720p")
    限定区域图片 = 背景图片[y坐标:y坐标 + 高度, x坐标:x坐标 + 宽度]

    if 模板图片.shape[0] > 限定区域图片.shape[0] or 模板图片.shape[1] > 限定区域图片.shape[1]:
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        print(f"模板尺寸 {模板图片.shape} 大于限定区域尺寸 {限定区域图片.shape}，{模板路径}")
        messagebox.showinfo("严重警告",
                            f"模板尺寸必须小于或等于限定区域尺寸,模板尺寸 {模板图片.shape} 大于限定区域尺寸 {限定区域图片.shape}，{模板路径}")
        time.sleep(2)
        return False, 0, 0, 0
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

            logger.info(
                f"✅ 匹配成功，路径：{提取内容},模板: {模板图片.shape},限定: {限定区域图片.shape},"
                f"相似: {max_val:.2f},坐标: ({最大匹配x坐标}, {最大匹配y坐标})")
        else:
            logger.error(
                f"❌ 匹配失败，路径：{提取内容},模板: {模板图片.shape},限定: {限定区域图片.shape},"
                f"相似: {max_val:.2f},坐标: ({最大匹配x坐标}, {最大匹配y坐标})")

    # print(f"截图完成（无裁剪），总耗时：{time.time() - start_time:.4f}秒")#返回结果
    if 需要缩放:
        最大匹配x坐标=int(最大匹配x坐标*宽度比例)
        最大匹配y坐标=int(最大匹配y坐标*高度比例)
    return 是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标

def 从模板图片中移除绿幕背景并设置透明(模板路径, 输出路径, 绿色下界, 绿色上界):
    """
    从模板图片中移除绿幕背景，并将背景设置为透明，然后保存新的模板图片。
    """
    # 加载模板图片
    模板图片 = cv2.imread(模板路径, cv2.IMREAD_UNCHANGED)

    if 模板图片 is None:
        raise FileNotFoundError(f"模板图片加载失败: {模板路径}")

    # 如果图片没有 Alpha 通道，添加一个 Alpha 通道
    if 模板图片.shape[2] == 3:  # 没有 Alpha 通道
        模板图片 = cv2.cvtColor(模板图片, cv2.COLOR_BGR2BGRA)

    # 将模板图片从 BGR 转换为 HSV 颜色空间
    hsv模板 = cv2.cvtColor(模板图片[:, :, :3], cv2.COLOR_BGR2HSV)

    # 创建掩膜，标识出绿幕区域
    掩膜 = cv2.inRange(hsv模板, 绿色下界, 绿色上界)

    # 将绿幕区域的 Alpha 通道设置为 0（透明）
    模板图片[:, :, 3] = cv2.bitwise_not(掩膜)

    # 保存处理后的模板图片
    cv2.imwrite(输出路径, 模板图片)
    print(f"处理后的模板图片已保存到: {输出路径}")

def 从模板图片中移除绿幕背景(模板路径, 输出路径, 绿色下界, 绿色上界):
    """
    从模板图片中移除绿幕背景，并保存新的模板图片。
    """
    # 加载模板图片
    模板图片 = cv2.imread(模板路径)

    if 模板图片 is None:
        raise FileNotFoundError(f"模板图片加载失败: {模板路径}")

    # 将模板图片从BGR颜色空间转换到HSV颜色空间
    hsv模板 = cv2.cvtColor(模板图片, cv2.COLOR_BGR2HSV)

    # 创建掩膜，标识出绿幕区域
    掩膜 = cv2.inRange(hsv模板, 绿色下界, 绿色上界)

    # 将绿幕区域设置为透明（或黑色）
    模板图片[掩膜 != 0] = [0, 0, 0]  # 设置为黑色

    # 保存处理后的模板图片
    cv2.imwrite(输出路径, 模板图片)
    print(f"处理后的模板图片已保存到: {输出路径}")
def 函数_在指定区域内进行内存图片匹配(背景图片数据, 限定区域, 内存图片数据, 最低相似度):
    """
    在背景图片的指定区域内进行模板匹配，并返回匹配结果。
    """
    if 背景图片数据 is None:
        # 打印日志以便定位
        print("[错误] 截图数据为空，跳过本次匹配")
        return False, 0, 0, 0
    背景图片 = cv2.imdecode(np.frombuffer(背景图片数据, dtype=np.uint8), cv2.IMREAD_COLOR)


    if 背景图片 is None or 内存图片数据 is None:
        # 弹窗提示
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror("路径错误", "背景图片或内存图片数据加载失败")
        return False, 0, 0, 0
    # 提取限定区域
    x坐标, y坐标, 宽度, 高度 = 限定区域
    限定区域图片 = 背景图片[y坐标:y坐标+高度, x坐标:x坐标+宽度]
    """
    # 打印尺寸进行调试
    print(f"模板尺寸: {模板图片.shape}")
    print(f"限定区域尺寸: {限定区域图片.shape}")
    # 确保模板尺寸小于限定区域尺寸    
    """
    # 模板匹配
    匹配结果 = cv2.matchTemplate(限定区域图片, 内存图片数据, cv2.TM_CCOEFF_NORMED)

    # 获取最值
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(匹配结果)

    # 计算最大匹配坐标
    最大匹配x坐标 = max_loc[0] + x坐标
    最大匹配y坐标 = max_loc[1] + y坐标

    # 判断是否匹配成功
    是否匹配 = max_val >= 最低相似度

    # 输出结果
    print(f"结果: {是否匹配},相似: {max_val:.4f},最大坐标: ({最大匹配x坐标}, {最大匹配y坐标})路径:变量")

    # 返回结果
    return 是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标



def 函数_在指定区域内进行模板匹配多个结果(背景图片数据, 限定区域, 模板路径, 最低相似度):
    """
    在背景图片的指定区域内进行模板匹配，并返回所有大于最低相似度的匹配结果，且满足模板图片大小的距离条件。
    """
    if 背景图片数据 is None:
        # 打印日志以便定位
        print("[错误] 截图数据为空，跳过本次匹配")
        return [], 0
    # 检查模板图片路径是否存在
    if not os.path.exists(模板路径):
        raise FileNotFoundError(f"模板图片文件不存在: {模板路径}")

    # 加载背景图片（从内存数据）
    背景图片 = cv2.imdecode(np.frombuffer(背景图片数据, dtype=np.uint8), cv2.IMREAD_COLOR)
    模板图片 = cv2.imread(模板路径)

    if 背景图片 is None or 模板图片 is None:
        error_message = f"路径中有中文或者错误: {模板路径}"
        print(error_message)
        错误信息 = f"模板匹配文件不存在或者路径中有中文: {error_message}"
        # 弹窗提示
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror("路径错误", 错误信息)
        raise FileNotFoundError("背景图片或模板图片加载失败，请检查路径！")

    # 提取限定区域
    x坐标, y坐标, 宽度, 高度 = 限定区域
    限定区域图片 = 背景图片[y坐标:y坐标+高度, x坐标:x坐标+宽度]

    # 确保模板尺寸小于限定区域尺寸
    if 模板图片.shape[0] > 限定区域图片.shape[0] or 模板图片.shape[1] > 限定区域图片.shape[1]:
        raise ValueError("模板尺寸必须小于或等于限定区域尺寸")

    # 模板匹配
    匹配结果 = cv2.matchTemplate(限定区域图片, 模板图片, cv2.TM_CCOEFF_NORMED)

    # 获取所有大于最低相似度的匹配结果
    匹配位置 = np.where(匹配结果 >= 最低相似度)

    # 计算匹配点的全局坐标
    匹配结果列表 = []
    for 点 in zip(*匹配位置[::-1]):
        全局x坐标 = 点[0] + x坐标
        全局y坐标 = 点[1] + y坐标
        匹配相似度 = 匹配结果[点[1], 点[0]]
        匹配结果列表.append((全局x坐标, 全局y坐标, 匹配相似度))

    # 筛选满足距离条件的匹配结果
    模板宽度 = 模板图片.shape[1]
    模板高度 = 模板图片.shape[0]
    筛选结果 = []

    for i, (x, y, sim) in enumerate(匹配结果列表):
        if not 筛选结果:
            筛选结果.append((x, y, sim))
        else:
            # 检查是否满足距离条件
            满足条件 = True
            for (sx, sy, _) in 筛选结果:
                if x < sx + 模板宽度 and y < sy + 模板高度:
                    满足条件 = False
                    break
            if 满足条件:
                筛选结果.append((x, y, sim))

    # 打印结果
    print(f"找到 {len(筛选结果)} 个匹配结果，最低相似度: {最低相似度}")
    个数=len(筛选结果)
    匹配结果信息 = []
    for i, (x, y, sim) in enumerate(筛选结果):
        匹配结果信息.append(f"(x, y) = ({x}, {y})")
        print(f"(x, y) = ({x}, {y})")
    """
        for i, (x, y, sim) in enumerate(筛选结果):
        匹配结果信息.append(f"匹配结果 {i+1}: (x, y) = ({x}, {y}), 相似度 = {sim:.4f}")
        print(f"匹配结果 {i+1}: (x, y) = ({x}, {y}), 相似度 = {sim:.4f}")
    """
    # 返回匹配结果信息
    return 匹配结果信息,个数


def 唯一区域内进行唯一相似度要求的多文件模板匹配(背景图片数据, 限定区域, 最低相似度, 文件列表):
    """
    在背景图片的同一指定区域内，使用相同相似度要求进行多个文件的模板匹配，并返回所有匹配结果。

    参数:
        背景图片数据: 背景图片的二进制数据
        限定区域: (x, y, width, height) 格式的元组，指定匹配区域
        最低相似度: 浮点数，所有模板使用相同的相似度阈值
        文件列表: 包含多个模板文件路径的列表，格式: ["模板路径1", "模板路径2", ...]

    返回:
        匹配结果字典: 以模板路径为键，匹配结果详情为值的字典
        {
            "图片路径1": {
                "是否匹配": True/False,
                "最大置信值": float,
                "最大匹配x坐标": int,
                "最大匹配y坐标": int,
                "限定区域": (x, y, width, height),
                "最低相似度": float
            },
            "图片路径2": {
                ...
            },
            "相似度最高的返回结果":{
                "图片路径":图片路径,
                "是否匹配": True/False,
                "最大置信值": float,
                "最大匹配x坐标": int,
                "最大匹配y坐标": int,
                "限定区域": (x, y, width, height),
                "最低相似度": float
            }
        }
    """
    if 背景图片数据 is None:
        # 打印日志以便定位
        print("[错误] 截图数据为空，跳过本次匹配")
        return {}
    结果字典 = {}

    # 加载背景图片（从内存数据）
    背景图片 = cv2.imdecode(np.frombuffer(背景图片数据, dtype=np.uint8), cv2.IMREAD_COLOR)
    if 背景图片 is None:
        logger.error("背景图片加载失败")
        return 结果字典

    # 提取限定区域
    x坐标, y坐标, 宽度, 高度 = 限定区域

    # 检查限定区域是否在图片范围内
    if (x坐标 + 宽度 > 背景图片.shape[1] or y坐标 + 高度 > 背景图片.shape[0] or
            x坐标 < 0 or y坐标 < 0):
        logger.warning(f"限定区域 {限定区域} 超出背景图片范围 {背景图片.shape}")
        # 返回所有文件的失败结果
        for 模板路径 in 文件列表:
            结果字典[模板路径] = {
                "是否匹配": False,
                "最大置信值": 0.0,
                "最大匹配x坐标": -1,
                "最大匹配y坐标": -1,
                "限定区域": 限定区域,
                "最低相似度": 最低相似度
            }
        return 结果字典

    # 提取限定区域图片
    限定区域图片 = 背景图片[y坐标:y坐标 + 高度, x坐标:x坐标 + 宽度]

    # 用于记录相似度最高的结果
    最高相似度 = -1.0
    最高相似度结果 = None
    最高相似度路径 = None

    for 模板路径 in 文件列表:
        # 初始化默认结果
        单次结果 = {
            "是否匹配": False,
            "最大置信值": 0.0,
            "最大匹配x坐标": -1,
            "最大匹配y坐标": -1,
            "限定区域": 限定区域,
            "最低相似度": 最低相似度
        }

        # 检查模板图片路径是否存在
        if not os.path.exists(模板路径):
            logger.warning(f"模板图片文件不存在: {模板路径}")
            结果字典[模板路径] = 单次结果
            continue

        # 使用 PIL 加载模板图片（支持中文路径）
        try:
            with Image.open(模板路径) as img:
                模板图片 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            logger.error(f"模板图片加载失败: {模板路径}, 错误信息: {e}")
            结果字典[模板路径] = 单次结果
            continue

        if 模板图片 is None:
            logger.error(f"模板图片加载失败: {模板路径}")
            结果字典[模板路径] = 单次结果
            continue

        # 检查模板尺寸是否小于限定区域尺寸
        if 模板图片.shape[0] > 限定区域图片.shape[0] or 模板图片.shape[1] > 限定区域图片.shape[1]:
            logger.warning(f"模板尺寸 {模板图片.shape} 大于限定区域尺寸 {限定区域图片.shape}, 路径: {模板路径}")
            结果字典[模板路径] = 单次结果
            continue

        # 进行模板匹配
        try:
            匹配结果 = cv2.matchTemplate(限定区域图片, 模板图片, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(匹配结果)

            # 计算最大匹配坐标（转换为全局坐标）
            最大匹配x坐标 = max_loc[0] + x坐标
            最大匹配y坐标 = max_loc[1] + y坐标

            # 判断是否匹配成功
            是否匹配 = max_val >= 最低相似度

            # 更新结果
            单次结果.update({
                "是否匹配": 是否匹配,
                "最大置信值": max_val,
                "最大匹配x坐标": 最大匹配x坐标,
                "最大匹配y坐标": 最大匹配y坐标
            })

            # 更新最高相似度记录
            if max_val > 最高相似度:
                最高相似度 = max_val
                最高相似度结果 = 单次结果.copy()
                最高相似度路径 = 模板路径

            """if 是否匹配:
                logger.info(
                    f"✅ 匹配成功，多文件匹配路径：{模板路径}, 模板: {模板图片.shape}, 限定: {限定区域图片.shape}, "
                    f"相似: {max_val:.4f}, 坐标: ({最大匹配x坐标}, {最大匹配y坐标})")
            else:
                logger.error(
                    f"❌ 匹配失败, 多文件匹配路径：{模板路径}, 模板: {模板图片.shape}, 限定: {限定区域图片.shape}, "
                    f"相似: {max_val:.4f}, 坐标: ({最大匹配x坐标}, {最大匹配y坐标})")"""

        except Exception as e:
            logger.error(f"模板匹配过程中出错: {模板路径}, 错误: {e}")

        结果字典[模板路径] = 单次结果

    # 添加相似度最高的返回结果
    if 最高相似度结果 is not None and 最高相似度路径 is not None:
        结果字典["相似度最高的返回结果"] = {
            "图片路径": 最高相似度路径,
            "是否匹配": 最高相似度结果["是否匹配"],
            "最大置信值": 最高相似度结果["最大置信值"],
            "最大匹配x坐标": 最高相似度结果["最大匹配x坐标"],
            "最大匹配y坐标": 最高相似度结果["最大匹配y坐标"],
            "限定区域": 最高相似度结果["限定区域"],
            "最低相似度": 最高相似度结果["最低相似度"]
        }
        logger.info(f"📊 相似度最高的模板: {最高相似度路径}, 相似度: {最高相似度:.4f}")
    else:
        logger.warning("未找到任何有效的模板匹配结果")
        结果字典["相似度最高的返回结果"] = {
            "图片路径": "",
            "是否匹配": False,
            "最大置信值": 0.0,
            "最大匹配x坐标": -1,
            "最大匹配y坐标": -1,
            "限定区域": 限定区域,
            "最低相似度": 最低相似度
        }

    return 结果字典
def 函数_在指定区域内进行模板匹配多(背景图片数据, 匹配列表):
    """
    在背景图片的多个指定区域内进行模板匹配，并返回所有匹配结果。

    参数:
        背景图片数据: 背景图片的二进制数据
        匹配列表: 包含多个匹配配置的列表，每个配置为字典，格式如下:
            [{
                "限定区域": (x, y, width, height),
                "模板路径": "图片路径",
                "最低相似度": 0.8
            }, ...]

    返回:
        匹配结果列表: 每个元素为字典，包含匹配结果
            [{
                "模板路径": "图片路径",
                "是否匹配": True/False,
                "最大置信值": float,
                "最大匹配x坐标": int,
                "最大匹配y坐标": int,
                "限定区域": (x, y, width, height),
                "最低相似度": float
            }, ...]
           匹配结果字典:
           {"图片路径":{
                "是否匹配": True/False,
                "最大置信值": float,
                "最大匹配x坐标": int,
                "最大匹配y坐标": int,
                "限定区域": (x, y, width, height),
                "最低相似度": float
            }, ...
            ,}
    """

    if 背景图片数据 is None:
        # 打印日志以便定位
        print("[错误] 截图数据为空，跳过本次匹配")
        return []
    结果列表 = []

    # 加载背景图片（从内存数据）
    背景图片 = cv2.imdecode(np.frombuffer(背景图片数据, dtype=np.uint8), cv2.IMREAD_COLOR)
    if 背景图片 is None:
        logger.error("背景图片加载失败")
        return 结果列表

    for 匹配配置 in 匹配列表:
        限定区域 = 匹配配置.get("限定区域")
        模板路径 = 匹配配置.get("模板路径")
        最低相似度 = 匹配配置.get("最低相似度", 0.8)

        # 初始化默认结果
        单次结果 = {
            "模板路径": 模板路径,
            "是否匹配": False,
            "最大置信值": 0.0,
            "最大匹配x坐标": -1,
            "最大匹配y坐标": -1,
            "限定区域": 限定区域,
            "最低相似度": 最低相似度
        }

        # 检查模板图片路径是否存在
        if not os.path.exists(模板路径):
            logger.warning(f"模板图片文件不存在: {模板路径}")
            结果列表.append(单次结果)
            continue

        # 使用 PIL 加载模板图片（支持中文路径）
        try:
            with Image.open(模板路径) as img:
                模板图片 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            logger.error(f"模板图片加载失败: {模板路径}, 错误信息: {e}")
            结果列表.append(单次结果)
            continue

        if 模板图片 is None:
            logger.error(f"模板图片加载失败: {模板路径}")
            结果列表.append(单次结果)
            continue

        # 提取限定区域
        x坐标, y坐标, 宽度, 高度 = 限定区域

        # 检查限定区域是否在图片范围内
        if (x坐标 + 宽度 > 背景图片.shape[1] or y坐标 + 高度 > 背景图片.shape[0] or
                x坐标 < 0 or y坐标 < 0):
            logger.warning(f"限定区域 {限定区域} 超出背景图片范围 {背景图片.shape}")
            结果列表.append(单次结果)
            continue

        限定区域图片 = 背景图片[y坐标:y坐标 + 高度, x坐标:x坐标 + 宽度]

        # 检查模板尺寸是否小于限定区域尺寸
        if 模板图片.shape[0] > 限定区域图片.shape[0] or 模板图片.shape[1] > 限定区域图片.shape[1]:
            logger.warning(f"模板尺寸 {模板图片.shape} 大于限定区域尺寸 {限定区域图片.shape}, 路径: {模板路径}")
            结果列表.append(单次结果)
            continue

        # 进行模板匹配
        try:
            匹配结果 = cv2.matchTemplate(限定区域图片, 模板图片, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(匹配结果)

            # 计算最大匹配坐标（转换为全局坐标）
            最大匹配x坐标 = max_loc[0] + x坐标
            最大匹配y坐标 = max_loc[1] + y坐标

            # 判断是否匹配成功
            是否匹配 = max_val >= 最低相似度

            # 更新结果
            单次结果.update({
                "是否匹配": 是否匹配,
                "最大置信值": max_val,
                "最大匹配x坐标": 最大匹配x坐标,
                "最大匹配y坐标": 最大匹配y坐标
            })

            # 记录日志
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
                    f"✅ 匹配成功，多图匹配路径：{提取内容}, 模板: {模板图片.shape}, 限定: {限定区域图片.shape}, "
                    f"相似: {max_val:.4f}, 坐标: ({最大匹配x坐标}, {最大匹配y坐标})")
            else:
                logger.error(
                    f"❌ 匹配失败,多图匹配路径：{提取内容}, 模板: {模板图片.shape}, 限定: {限定区域图片.shape}, "
                    f" 相似: {max_val:.4f}, 坐标: ({最大匹配x坐标}, {最大匹配y坐标})")

        except Exception as e:
            logger.error(f"模板匹配过程中出错: {模板路径}, 错误: {e}")

        结果列表.append(单次结果)

    return 结果列表


def 函数_在指定区域内进行模板匹配_多目标(背景图片数据, 限定区域, 模板路径, 最低相似度, nms_threshold=0.6):
    """
    在背景图片的指定区域内进行模板匹配，找出所有符合条件的匹配结果
    使用非极大值抑制(NMS)来避免重叠的检测结果

    参数:
        背景图片数据: 背景图片的二进制数据
        限定区域: (x, y, width, height) 限定搜索区域
        模板路径: 模板图片路径
        最低相似度: 最低匹配相似度阈值
        nms_threshold: 非极大值抑制阈值，用于控制重叠检测的合并

    返回:
        匹配结果列表: 每个元素为(相似度, x坐标, y坐标)的元组，按相似度从高到低排序
    """
    if 背景图片数据 is None:
        # 打印日志以便定位
        print("[错误] 截图数据为空，跳过本次匹配")
        return []
    # 检查模板图片路径是否存在
    if not os.path.exists(模板路径):
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror("路径错误", f"模板图片文件不存在: {模板路径}")
        return []

    # 加载背景图片（从内存数据）
    背景图片 = cv2.imdecode(np.frombuffer(背景图片数据, dtype=np.uint8), cv2.IMREAD_COLOR)

    # 使用 PIL 加载模板图片（支持中文路径）
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
        return []

    if 背景图片 is None:
        error_message = f"路径错误: {模板路径}"
        print(error_message)
        错误信息 = f"函数_在指定区域内进行模板匹配_多目标模板匹配文件不存在: {error_message}"
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror("路径错误", 错误信息)
        return []

    # 提取限定区域
    x坐标, y坐标, 宽度, 高度 = 限定区域
    限定区域图片 = 背景图片[y坐标:y坐标 + 高度, x坐标:x坐标 + 宽度]

    # 确保模板尺寸小于限定区域尺寸
    if 模板图片.shape[0] > 限定区域图片.shape[0] or 模板图片.shape[1] > 限定区域图片.shape[1]:
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showinfo("严重警告", f"模板尺寸必须小于或等于限定区域尺寸,路径：{str(模板路径)}")
        return []

    # 模板匹配
    匹配结果 = cv2.matchTemplate(限定区域图片, 模板图片, cv2.TM_CCOEFF_NORMED)

    # 获取所有超过阈值的匹配位置
    locations = np.where(匹配结果 >= 最低相似度)
    匹配列表 = list(zip(locations[1], locations[0]))  # (x, y) 坐标
    置信度列表 = 匹配结果[locations[0], locations[1]]

    # 将坐标和置信度组合
    检测结果 = []
    for (x, y), confidence in zip(匹配列表, 置信度列表):
        检测结果.append((confidence, x, y))

    # 按置信度排序（从高到低）
    检测结果.sort(key=lambda x: x[0], reverse=True)

    # 应用非极大值抑制(NMS)来去除重叠的检测结果
    final_results = []
    template_h, template_w = 模板图片.shape[:2]

    while 检测结果:
        # 取置信度最高的结果
        current = 检测结果.pop(0)
        final_results.append(current)

        # 计算与当前结果重叠的其他结果
        keep_indices = []
        for i, (conf, x, y) in enumerate(检测结果):
            # 计算两个矩形框的重叠面积
            current_rect = [current[1], current[2], current[1] + template_w, current[2] + template_h]
            other_rect = [x, y, x + template_w, y + template_h]

            # 计算IoU（交并比）
            x1 = max(current_rect[0], other_rect[0])
            y1 = max(current_rect[1], other_rect[1])
            x2 = min(current_rect[2], other_rect[2])
            y2 = min(current_rect[3], other_rect[3])

            intersection = max(0, x2 - x1) * max(0, y2 - y1)
            area_current = (current_rect[2] - current_rect[0]) * (current_rect[3] - current_rect[1])
            area_other = (other_rect[2] - other_rect[0]) * (other_rect[3] - other_rect[1])
            union = area_current + area_other - intersection

            iou = intersection / union if union > 0 else 0

            # 如果重叠度小于阈值，则保留
            if iou < nms_threshold:
                keep_indices.append(i)

        # 更新检测结果列表，只保留不重叠的结果
        检测结果 = [检测结果[i] for i in keep_indices]

    # 将坐标转换回原图坐标系
    最终结果 = []
    for conf, x, y in final_results:
        原图x坐标 = x + x坐标
        原图y坐标 = y + y坐标
        最终结果.append((conf, 原图x坐标, 原图y坐标))

    # 记录日志
    路径部分 = str(模板路径)
    if "图片" in 路径部分:
        路径部分 = 路径部分.split(r"图片")
        if 路径部分:
            提取内容 = 路径部分[1]
        else:
            提取内容 = 模板路径
    else:
        提取内容 = 模板路径

    if 最终结果:
        logger.info(
            f"✅ 匹配成功，多目标匹配 - 路径：{提取内容}, 找到 {len(最终结果)} 个匹配, 模板: {模板图片.shape}, 限定: {限定区域图片.shape}")
        for i, (conf, x, y) in enumerate(最终结果):
            logger.info(f"  匹配{i + 1}: 相似度: {conf:.4f}, 坐标: ({x}, {y})")
    else:
        logger.error(f"❌ 匹配失败,多目标匹配 - 路径：{提取内容},  模板: {模板图片.shape}, 限定: {限定区域图片.shape}")

    return 最终结果


def 函数_查找指定点的颜色是否为目标颜色(背景图片数据, 指定点, 目标颜色):
    """
    在背景图片的指定点检查颜色是否与目标颜色匹配

    参数:
        背景图片数据: 字节流形式的图片数据
        指定点: (x坐标, y坐标) 元组
        目标颜色: (B, G, R) 元组，OpenCV使用BGR格式

    返回:
        (是否匹配, 实际颜色, 与目标颜色的差异)
    """
    if 背景图片数据 is None:
        # 打印日志以便定位
        print("[错误] 截图数据为空，跳过本次匹配")
        return False, (0, 0, 0), 255
    # 解码背景图片
    背景图片 = cv2.imdecode(np.frombuffer(背景图片数据, dtype=np.uint8), cv2.IMREAD_COLOR)

    if 背景图片 is None:
        logger.error("背景图片加载失败")
        return False, (0, 0, 0), 255  # 最大差异值

    # 获取指定点坐标
    点x, 点y = 指定点

    # 检查坐标是否在图片范围内
    if 点x < 0 or 点x >= 背景图片.shape[1] or 点y < 0 or 点y >= 背景图片.shape[0]:
        logger.error(f"指定点({点x}, {点y})超出图片范围(宽度:{背景图片.shape[1]}, 高度:{背景图片.shape[0]})")
        return False, (0, 0, 0), 255

    # 获取指定点的颜色（OpenCV使用BGR格式）
    实际颜色 = 背景图片[点y, 点x]  # 注意：OpenCV是行(y)列(x)顺序

    # 计算颜色差异（欧几里得距离）
    差异 = np.sqrt(np.sum((实际颜色 - np.array(目标颜色)) ** 2))

    # 判断是否匹配（差异为0表示完全匹配）
    是否匹配 = np.array_equal(实际颜色, 目标颜色)

    if 是否匹配:
        logger.info(f"✅ 颜色匹配成功，坐标: ({点x}, {点y})，颜色: BGR{tuple(实际颜色)}")
    else:
        logger.warning(
            f"❌ 颜色匹配失败，坐标: ({点x}, {点y})，实际颜色: BGR{tuple(实际颜色)}，目标颜色: BGR{目标颜色}，差异: {差异:.2f}")

    return 是否匹配, tuple(实际颜色), 差异


# 增强版本：支持颜色容差范围匹配
def 函数_查找指定点的颜色是否在容差范围内(背景图片数据, 指定点, 目标颜色, 容差=10):
    """
    在背景图片的指定点检查颜色是否在目标颜色的容差范围内

    参数:
        背景图片数据: 字节流形式的图片数据
        指定点: (x坐标, y坐标) 元组
        目标颜色: (B, G, R) 元组，OpenCV使用BGR格式
        容差: 每个颜色通道允许的最大差异值

    返回:
        (是否匹配, 实际颜色, 各通道差异)
    """

    # 解码背景图片
    if 背景图片数据 is None:
        # 打印日志以便定位
        print("[错误] 截图数据为空，跳过本次匹配")
        return False, (0, 0, 0), (255, 255, 255)
    背景图片 = cv2.imdecode(np.frombuffer(背景图片数据, dtype=np.uint8), cv2.IMREAD_COLOR)

    if 背景图片 is None:
        logger.error("背景图片加载失败")
        return False, (0, 0, 0), (255, 255, 255)

    # 获取指定点坐标
    点x, 点y = 指定点

    # 检查坐标是否在图片范围内
    if 点x < 0 or 点x >= 背景图片.shape[1] or 点y < 0 or 点y >= 背景图片.shape[0]:
        logger.error(f"指定点({点x}, {点y})超出图片范围(宽度:{背景图片.shape[1]}, 高度:{背景图片.shape[0]})")
        return False, (0, 0, 0), (255, 255, 255)

    # 获取指定点的颜色
    实际颜色 = 背景图片[点y, 点x]

    # 计算各通道差异
    通道差异 = (
        abs(int(实际颜色[0]) - int(目标颜色[0])),  # B通道差异
        abs(int(实际颜色[1]) - int(目标颜色[1])),  # G通道差异
        abs(int(实际颜色[2]) - int(目标颜色[2]))  # R通道差异
    )

    # 判断是否在容差范围内
    是否匹配 = all(差异 <= 容差 for 差异 in 通道差异)

    # 计算总差异（欧几里得距离）
    总差异 = np.sqrt(np.sum(np.array(通道差异) ** 2))

    if 是否匹配:
        logger.info(f"✅ 颜色匹配成功(容差:{容差})，坐标: ({点x}, {点y})，实际颜色: BGR{tuple(实际颜色)}，差异: {通道差异}")
    else:
        logger.warning(
            f"❌ 颜色匹配失败(容差:{容差})，坐标: ({点x}, {点y})，实际颜色: BGR{tuple(实际颜色)}，目标颜色: BGR{目标颜色}，差异: {通道差异}")

    return 是否匹配, tuple(实际颜色), 通道差异
def 函数_检查区域内是否存在目标颜色(背景图片数据, 区域, 目标颜色,容差=10):
    """
    检查指定区域内颜色与目标颜色匹配的像素比例

    参数:
        背景图片数据: 字节流形式的图片数据
        区域: (x, y, 宽度, 高度) 元组
        目标颜色: (B, G, R) 元组，OpenCV使用BGR格式
        容差: 每个颜色通道允许的最大差异值

    返回:
        是否存在
    """

    # 解码背景图片
    if 背景图片数据 is None:
        # 打印日志以便定位
        print("[错误] 截图数据为空，跳过本次匹配")
        return False
    背景图片 = cv2.imdecode(np.frombuffer(背景图片数据, dtype=np.uint8), cv2.IMREAD_COLOR)

    if 背景图片 is None:
        logger.error("背景图片加载失败")
        return False

    # 提取区域
    x, y, 宽度, 高度 = 区域
    区域图片 = 背景图片[y:y + 高度, x:x + 宽度]

    if 区域图片.size == 0:
        logger.error(f"区域({x}, {y}, {宽度}, {高度})无效或超出图片范围")
        return False

    # 计算颜色差异
    颜色差异 = np.abs(区域图片 - np.array(目标颜色))

    # 检查每个像素是否在容差范围内
    匹配掩码 = np.all(颜色差异 <= 容差, axis=2)

    匹配像素数 = np.sum(匹配掩码)


    是否存在 = 匹配像素数 > 0

    if 是否存在:
        logger.info(f"✅ 匹配成功，颜色: BGR{目标颜色}, 区域: {区域}")
    else:
        logger.warning(f"❌ 匹配失败，颜色: {目标颜色}, 区域: {区域}")

    return 是否存在


def 函数_检查区域内是否存在目标颜色v2(背景图片数据, 区域, 目标颜色, 容差=10):
    """
    检查指定区域内是否存在目标颜色，并可选地返回最匹配点的信息

    参数:
        背景图片数据: 字节流形式的图片数据
        区域: (x, y, 宽度, 高度) 元组
        目标颜色: (B, G, R) 元组，OpenCV使用BGR格式
        容差: 每个颜色通道允许的最大差异值
        返回最匹配点: 是否返回最匹配点的详细信息

    返回:
        如果返回最匹配点为False: 是否存在
        如果返回最匹配点为True: (是否存在, 最匹配点实际颜色, 最匹配点坐标, 最匹配点差异值)
    """

    # 解码背景图片
    if 背景图片数据 is None:
        # 打印日志以便定位
        print("[错误] 截图数据为空，跳过本次匹配")
        结果 = (False, (0, 0, 0), (0, 0), 255)
        return 结果
    背景图片 = cv2.imdecode(np.frombuffer(背景图片数据, dtype=np.uint8), cv2.IMREAD_COLOR)

    if 背景图片 is None:
        logger.error("背景图片加载失败")
        结果 = (False, (0, 0, 0), (0, 0), 255)
        return 结果

    # 提取区域
    x, y, 宽度, 高度 = 区域
    区域图片 = 背景图片[y:y + 高度, x:x + 宽度]

    if 区域图片.size == 0:
        logger.error(f"区域({x}, {y}, {宽度}, {高度})无效或超出图片范围")
        结果 =(False, (0, 0, 0), (0, 0), 255)
        return 结果

    # 计算颜色差异（使用欧几里得距离计算每个像素的差异）
    颜色差异图 = np.sqrt(np.sum((区域图片.astype(np.float32) - np.array(目标颜色)) ** 2, axis=2))

    # 找到差异最小的点
    最小差异 = np.min(颜色差异图)
    最小差异位置 = np.unravel_index(np.argmin(颜色差异图), 颜色差异图.shape)

    # 最小差异点在区域内的坐标
    最小差异点_区域y, 最小差异点_区域x = 最小差异位置
    最小差异点_全局x = x + 最小差异点_区域x
    最小差异点_全局y = y + 最小差异点_区域y

    # 获取最小差异点的实际颜色
    最小差异点实际颜色 = 区域图片[最小差异点_区域y, 最小差异点_区域x]

    # 判断是否存在匹配（使用容差标准）
    是否存在 = 最小差异 <= 容差 * np.sqrt(3)  # 欧几里得距离阈值

    if 是否存在:
        logger.info(
            f"✅ 颜色匹配成功，颜色: BGR{目标颜色}, 区域: {区域}, 最匹配点: ({最小差异点_全局x}, {最小差异点_全局y}), 颜色: BGR{tuple(最小差异点实际颜色)}, 差异: {最小差异:.2f}")
    else:
        logger.warning(
            f"❌ 颜色匹配失败，颜色: {目标颜色}, 区域: {区域}, 最接近点: ({最小差异点_全局x}, {最小差异点_全局y}), 颜色: BGR{tuple(最小差异点实际颜色)}, 差异: {最小差异:.2f}")
    结果=(是否存在, tuple(最小差异点实际颜色), (最小差异点_全局x, 最小差异点_全局y), 最小差异)

    return 结果

def 函数_检查区域内颜色分布(背景图片数据, 区域, 目标颜色, 比例阈值=0.8, 容差=10):
    """
    检查指定区域内颜色与目标颜色匹配的像素比例

    参数:
        背景图片数据: 字节流形式的图片数据
        区域: (x, y, 宽度, 高度) 元组
        目标颜色: (B, G, R) 元组，OpenCV使用BGR格式
        比例阈值: 匹配像素的比例阈值，默认0.8表示80%
        容差: 每个颜色通道允许的最大差异值

    返回:
        (是否达到比例, 匹配比例, 匹配像素数, 总像素数)
    """

    # 解码背景图片
    if 背景图片数据 is None:
        # 打印日志以便定位
        print("[错误] 截图数据为空，跳过本次匹配")
        return False, 0.0, 0, 0
    背景图片 = cv2.imdecode(np.frombuffer(背景图片数据, dtype=np.uint8), cv2.IMREAD_COLOR)

    if 背景图片 is None:
        logger.error("背景图片加载失败")
        return False, 0.0, 0, 0

    # 提取区域
    x, y, 宽度, 高度 = 区域
    区域图片 = 背景图片[y:y + 高度, x:x + 宽度]

    if 区域图片.size == 0:
        logger.error(f"区域({x}, {y}, {宽度}, {高度})无效或超出图片范围")
        return False, 0.0, 0, 0

    # 计算颜色差异
    颜色差异 = np.abs(区域图片 - np.array(目标颜色))

    # 检查每个像素是否在容差范围内
    匹配掩码 = np.all(颜色差异 <= 容差, axis=2)

    # 统计匹配像素
    匹配像素数 = np.sum(匹配掩码)
    总像素数 = 区域图片.shape[0] * 区域图片.shape[1]
    匹配比例 = 匹配像素数 / 总像素数 if 总像素数 > 0 else 0.0

    # 判断是否达到比例阈值
    是否达到 = 匹配比例 >= 比例阈值

    if 是否达到:
        logger.info(f"✅ 匹配成功，颜色: {目标颜色}, 区域: {区域}，匹配比例: {匹配比例:.2%}")
    else:
        logger.warning(f"❌ 匹配失败，颜色: {目标颜色}, 区域: {区域}，匹配比例: {匹配比例:.2%}")

    return 是否达到, 匹配比例, 匹配像素数, 总像素数


def 函数_查找图片数据内指定点的颜色并输出(背景图片数据, 指定点, 颜色格式="BGR"):
    """
    查找图片数据内指定点的颜色并以指定格式输出

    参数:
        背景图片数据: 字节流形式的图片数据
        指定点: (x坐标, y坐标) 元组
        颜色格式: "BGR", "RGB", "HEX", "HEX_BGR", "HEX_RGB" 或 "灰度"

    返回:
        (是否成功, 颜色值, 颜色信息字符串)
    """
    if 背景图片数据 is None:
        # 打印日志以便定位
        print("[错误] 截图数据为空，跳过本次匹配")
        return False, None, "error_msg"
    try:
        # 解码背景图片
        背景图片 = cv2.imdecode(np.frombuffer(背景图片数据, dtype=np.uint8), cv2.IMREAD_COLOR)

        if 背景图片 is None:
            error_msg = "背景图片加载失败"
            logger.error(error_msg)
            return False, None, error_msg

        # 获取指定点坐标
        点x, 点y = 指定点

        # 检查坐标是否在图片范围内
        图片高度, 图片宽度, _ = 背景图片.shape
        if 点x < 0 or 点x >= 图片宽度 or 点y < 0 or 点y >= 图片高度:
            error_msg = f"指定点({点x}, {点y})超出图片范围(宽度:{图片宽度}, 高度:{图片高度})"
            logger.error(error_msg)
            return False, None, error_msg

        # 获取指定点的颜色（OpenCV使用BGR格式）
        bgr颜色 = 背景图片[点y, 点x]
        b, g, r = bgr颜色

        # 根据颜色格式进行处理
        if 颜色格式.upper() == "BGR":
            颜色值 = (int(b), int(g), int(r))
            颜色信息 = f"BGR颜色: ({颜色值[0]}, {颜色值[1]}, {颜色值[2]})"

        elif 颜色格式.upper() == "RGB":
            颜色值 = (int(r), int(g), int(b))
            颜色信息 = f"RGB颜色: ({颜色值[0]}, {颜色值[1]}, {颜色值[2]})"

        elif 颜色格式.upper() == "HEX" or 颜色格式.upper() == "HEX_RGB":
            # HEX格式通常指RGB的十六进制表示
            hex_color = f"#{r:02x}{g:02x}{b:02x}".upper()
            颜色值 = hex_color
            颜色信息 = f"HEX颜色: {hex_color}"

        elif 颜色格式.upper() == "HEX_BGR":
            # BGR的十六进制表示
            hex_color = f"#{b:02x}{g:02x}{r:02x}".upper()
            颜色值 = hex_color
            颜色信息 = f"HEX_BGR颜色: {hex_color}"

        elif 颜色格式.upper() == "灰度":
            # 转换为灰度值 (使用标准公式: 0.299*R + 0.587*G + 0.114*B)
            灰度值 = int(0.299 * r + 0.587 * g + 0.114 * b)
            颜色值 = 灰度值
            颜色信息 = f"灰度值: {灰度值}"

        else:
            error_msg = f"不支持的颜色格式: {颜色格式}，支持的格式: BGR, RGB, HEX, HEX_BGR, 灰度"
            logger.error(error_msg)
            return False, None, error_msg

        # 记录结果
        logger.info(f"✅ 获取颜色成功，坐标: ({点x}, {点y})，{颜色信息}")

        return True, 颜色值, 颜色信息

    except Exception as e:
        error_msg = f"获取颜色时发生异常: {str(e)}"
        logger.error(error_msg)
        return False, None, error_msg
def clamp_region(x, y, width, height, max_width=1280, max_height=720):
    """
    确保矩形区域完全位于指定的最大边界内

    Args:
        x: 矩形左上角x坐标
        y: 矩形左上角y坐标
        width: 矩形宽度
        height: 矩形高度
        max_width: 最大宽度边界，默认为1280
        max_height: 最大高度边界，默认为720

    Returns:
        tuple: 调整后的(x, y, width, height)
    """
    # 确保宽度和高度为正数且不超过最大边界
    width = max(0, min(width, max_width))
    height = max(0, min(height, max_height))

    # 调整x坐标，确保矩形在水平边界内
    x = max(0, min(x, max_width - width))

    # 调整y坐标，确保矩形在垂直边界内
    y = max(0, min(y, max_height - height))

    return (x, y, width, height)

from typing import List, Tuple


def sort_points_left_to_right_top_to_bottom(points: List[Tuple]) -> List[Tuple[int, int]]:
    """
    将点列表按照从左到右、从上到下的顺序排序
    优先按x坐标排序（从左到右），然后按y坐标排序（从上到下）

    Args:
        points: 包含坐标的列表，每个坐标可以是np.int64或整数

    Returns:
        排序后的整数元组列表
    """
    if not points:
        return []

    # 转换为Python内置整数元组
    int_points = [(int(x), int(y)) for (x, y) in points]

    # 按照先x后y的顺序排序，实现从左到右、从上到下
    sorted_points = sorted(int_points, key=lambda point: (point[0], point[1]))

    return sorted_points
def 测试GPU可靠性():
    """用已知图片测试 GPU 匹配是否正常"""
    if not cv2.ocl.haveOpenCL():
        print("GPU 可靠性测试不通过")
        return False

    # 创建一张 200x200 的纯黑图和一个 32x32 的纯白模板
    test_img = np.zeros((200, 200, 3), dtype=np.uint8)
    test_tpl = np.ones((32, 32, 3), dtype=np.uint8) * 255

    # GPU 匹配
    result_gpu = cv2.matchTemplate(
        cv2.UMat(test_img), cv2.UMat(test_tpl), cv2.TM_CCOEFF_NORMED
    ).get()
    _, max_val_gpu, _, _ = cv2.minMaxLoc(result_gpu)

    # CPU 匹配
    result_cpu = cv2.matchTemplate(test_img, test_tpl, cv2.TM_CCOEFF_NORMED)
    _, max_val_cpu, _, _ = cv2.minMaxLoc(result_cpu)

    # 允许浮点误差的阈值（1e-5）
    if abs(max_val_gpu - max_val_cpu) > 1e-5:
        print(
            f"GPU 匹配结果 ({max_val_gpu:.6f}) 与 CPU ({max_val_cpu:.6f}) 不符，"
            f"建议关闭 GPU 加速"
        )
        return False
    print(
        f"GPU 匹配结果 ({max_val_gpu:.6f}) 与 CPU ({max_val_cpu:.6f}) "

    )

    print("GPU 可靠性测试通过")
    return True

if __name__ == "__main__":
    print(cv2.ocl.haveOpenCL())  # 必须为 True
    print(cv2.ocl.useOpenCL())  # 查看当前是否启用
    cv2.ocl.setUseOpenCL(True)  # 强制启用
    print("OpenCV 版本:", cv2.__version__)
    print("OpenCL 可用:", cv2.ocl.haveOpenCL())
    print("OpenCL 已启用:", cv2.ocl.useOpenCL())
    测试GPU可靠性()
