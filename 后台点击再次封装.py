from 游戏截图保存到内存 import 获取_png_data, 函数截图到内存直接返回NumPy数组
from opencv模板匹配找图 import 函数_在指定区域内进行模板匹配, 函数_在指定区域内进行内存图片匹配, 函数_在指定区域内进行模板匹配多, 函数_在指定区域数组匹配
from adb操作 import 长按,滑动
import time
import threading
import logging
import win32gui
import win32con
import win32api
from pathlib import Path
import cv2
import numpy as np
import queue
logger = logging.getLogger("database")
from 后台键鼠 import 真实鼠标坐标后台点击专用, PyAutoGUI_模拟按键按下, PyAutoGUI_模拟按键弹起, 模拟按键长按, PyAutoGUI_模拟鼠标左键单击
from 睡眠倍数模块 import 可变速等待
from PIL import Image, ImageDraw
x比例=1
y比例=1
def 判断线程与值的布尔函数(变量):
    """
    判断变量的布尔值
    :param 变量: threading.Event() 或者 int
    :return: 布尔值
    """
    if isinstance(变量, threading.Event):
        # threading.Event 对象需要使用 is_set() 判断
        return 变量.is_set()
    else:
        # int 或其他类型直接使用 bool() 转换
        return bool(变量)
def adjust_expanded_region(original_region, image_width=1280, image_height=720, expand=10):
    """
    扩大区域并确保不超出图片边界

    参数:
    original_region: (x, y, width, height) 原始区域
    image_width: 图片宽度 (默认1280)
    image_height: 图片高度 (默认720)
    expand: 扩大像素数 (默认10)

    返回:
    (x, y, width, height) 调整后的扩大区域
    """
    x, y, width, height = original_region

    # 计算扩大后的区域
    expanded_x = x - expand
    expanded_y = y - expand
    expanded_width = width + 2 * expand
    expanded_height = height + 2 * expand

    # 检查并调整边界
    # 左边界
    if expanded_x < 0:
        expanded_width += expanded_x  # 减少宽度来补偿超出部分
        expanded_x = 0

    # 上边界
    if expanded_y < 0:
        expanded_height += expanded_y  # 减少高度来补偿超出部分
        expanded_y = 0

    # 右边界
    if expanded_x + expanded_width > image_width:
        expanded_width = image_width - expanded_x

    # 下边界
    if expanded_y + expanded_height > image_height:
        expanded_height = image_height - expanded_y

    # 确保宽度和高度不为负数
    expanded_width = max(0, expanded_width)
    expanded_height = max(0, expanded_height)

    return expanded_x, expanded_y, expanded_width, expanded_height

class 队列点击执行器:
    """单线程顺序执行点击任务的执行器（支持顶级优先）"""
    def __init__(self):
        self.任务队列 = queue.Queue()           # 普通任务队列
        self.顶级任务队列 = queue.Queue()       # 顶级任务队列
        self.执行线程 = threading.Thread(target=self._执行循环, daemon=True)
        self.执行线程.start()

    # ---------- 普通提交（原有方法不变） ----------
    def 添加后台点击任务(self, 句柄, 矩形, 坐标, 延时, 等待, 鼠标回弹=True):
        """将后台点击任务加入普通队列"""
        任务 = ('后台', (句柄, 矩形, 坐标, 延时, 等待, 鼠标回弹))
        self.任务队列.put(任务)

    def 添加前台点击任务(self, x, y, 点击时间):
        """将前台点击任务加入普通队列"""
        任务 = ('前台', (x, y, 点击时间))
        self.任务队列.put(任务)

    # ---------- 顶级提交 ----------
    def 添加顶级后台点击任务(self, 句柄, 矩形, 坐标, 延时, 等待, 鼠标回弹=True):
        """顶级提交：清空普通队列，将此后台点击任务加入顶级队列"""
        self._清空普通队列并唤醒()
        任务 = ('后台', (句柄, 矩形, 坐标, 延时, 等待, 鼠标回弹))
        self.顶级任务队列.put(任务)

    def 添加顶级前台点击任务(self, x, y, 点击时间):
        """顶级提交：清空普通队列，将此前台点击任务加入顶级队列"""
        self._清空普通队列并唤醒()
        任务 = ('前台', (x, y, 点击时间))
        self.顶级任务队列.put(任务)

    def _清空普通队列并唤醒(self):
        """丢弃普通队列中的所有任务，并放入唤醒标记"""
        # 清空所有待处理任务
        while not self.任务队列.empty():
            try:
                self.任务队列.get_nowait()
                self.任务队列.task_done()   # 维护计数器，避免 join 死锁
            except queue.Empty:
                break
        # 放入内部唤醒标记，让可能阻塞在 get() 的执行线程立即返回
        self.任务队列.put(('内部唤醒', None))

    # ---------- 执行循环 ----------
    def _执行循环(self):
        """执行线程的主循环，优先处理顶级任务"""
        while True:
            try:
                # 1. 优先尝试从顶级队列获取任务（非阻塞）
                try:
                    任务类型, 参数 = self.顶级任务队列.get_nowait()
                    来源队列 = self.顶级任务队列
                except queue.Empty:
                    # 2. 顶级队列为空时，才从普通队列获取（阻塞等待）
                    任务类型, 参数 = self.任务队列.get()
                    来源队列 = self.任务队列

                # 3. 处理内部唤醒标记
                if 任务类型 == '内部唤醒':
                    continue   # 直接回到循环开头，重新检查顶级队列

                # 4. 执行真实任务
                if 任务类型 == '后台':
                    句柄, 矩形, 坐标, 延时, 等待, 鼠标回弹 = 参数
                    真实鼠标坐标后台点击专用(句柄, 矩形, 坐标, 延时, 等待, 鼠标回弹)
                elif 任务类型 == '前台':
                    x, y, 点击时间 = 参数
                    PyAutoGUI_模拟鼠标左键单击(x, y, 点击时间)
                else:
                    print(f"未知任务类型: {任务类型}")

            except Exception as e:
                print(f"执行器异常: {e}")
            finally:
                # 标记对应队列的任务完成（唤醒标记同样会调用，保持计数准确）
                来源队列.task_done()

    def 等待所有任务完成(self):
        """阻塞当前线程，直到所有队列（顶级+普通）中的任务执行完毕"""
        self.顶级任务队列.join()
        self.任务队列.join()

点击执行器 = 队列点击执行器()

def check_and_expand_region(original_region, image_width=1280, image_height=720):
    """
    检查原始区域是否有效，然后扩大区域
    """
    x, y, width, height = original_region

    # 首先检查原始区域是否在图片范围内
    if (x < 0 or y < 0 or
            x + width > image_width or
            y + height > image_height):
        print("警告: 原始区域已超出图片边界!")
        # 这里可以选择调整原始区域或直接返回
        return None

    # 扩大区域
    expanded_region = adjust_expanded_region(original_region, image_width, image_height)
    return expanded_region

def 移动后判断是否遇见怪物(adb路径, current_dir,线程事件):
    进入战斗 = False
    for _ in range(40):
        if not 线程事件.is_set():
            break  # 如果事件对象被清除，退出循环
        menyu_path = current_dir / "图片" / "UI界面" /'菜单.png'
        auto_off_path = current_dir / "图片" / "UI界面" / 'auto_off.png'
        png数据 = 获取_png_data(adb路径)
        if png数据:
            是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(
                背景图片数据=png数据,
                限定区域=(80, 650, 55, 45),
                模板路径=menyu_path,
                最低相似度=0.85
            )
            if 是否匹配:
                logger.debug("没有进入战斗")
                break
            else:
                是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(
                    背景图片数据=png数据,
                    限定区域=(196, 16, 110, 46),
                    模板路径=auto_off_path,
                    最低相似度=0.85
                )
                if 是否匹配:
                    logger.debug("进入战斗")
                    进入战斗 = True
                    return 进入战斗
                是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(
                    背景图片数据=png数据,
                    限定区域=(196, 16, 110, 46),
                    模板路径=current_dir / "图片" / "UI界面" / 'auto_on.png',
                    最低相似度=0.85
                )
                if 是否匹配:
                    长按(adb路径, 最大匹配x坐标, 最大匹配y坐标, 持续时间=100)
        可变速等待(0.5)
    return 进入战斗
def 多图返回最像的一个(adb路径,匹配列表):
    png数据 = 获取_png_data(adb路径)
    返回值=函数_在指定区域内进行模板匹配多(png数据, 匹配列表)
    # 从所有结果中找出置信值最高的那个
    if 返回值:
        最像的结果 = max(返回值, key=lambda x: x["最大置信值"])
        return 最像的结果
    else:
        # 如果没有结果，返回一个空的默认结构
        return {
            "模板路径": "",
            "是否匹配": False,
            "最大置信值": 0.0,
            "最大匹配x坐标": 0,
            "最大匹配y坐标": 0,
            "限定区域": (0, 0, 0, 0),
            "最低相似度": 0.0
        }
def 接受循环的变量增加点击时长(adb路径,i,坐标x,坐标y):
    无用, 端口, hwnd, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb路径
    if 窗口矩形:
        真实鼠标坐标后台点击专用(hwnd, 窗口矩形, (坐标x,坐标y),
                                 PC全局延迟 + 0.009*i, 0.5)
    else:
        长按(adb路径, 坐标x,坐标y, 持续时间=100+ 10*i)
def 循环x延时y检测区域内是否为目标图片不是则点击图片(adb路径,匹配列表,目标图片名,x,y,线程事件):
    无用, 端口, hwnd, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb路径
    任务完成=False
    失败再延迟=0
    for i in range(x):
        if not 线程事件.is_set():
            return False
        返回值 = 多图返回最像的一个(adb路径, 匹配列表)
        if 返回值 and "模板路径" in 返回值:
            if 返回值["是否匹配"]:
                if 目标图片名 in str(返回值["模板路径"]):
                    if 任务完成:
                        logger.info("匹配成功且为目标图片")
                        return True
                    任务完成 = True
                else:
                    if 窗口矩形:
                        真实鼠标坐标后台点击专用(hwnd, 窗口矩形, (返回值["最大匹配x坐标"], 返回值["最大匹配y坐标"]),
                                                 PC全局延迟 + 失败再延迟, 0.5)
                        失败再延迟 = 失败再延迟 + 0.009
                    else:
                        长按(adb路径, 返回值["最大匹配x坐标"], 返回值["最大匹配y坐标"], 持续时间=100+ int(失败再延迟*1000))
        可变速等待(y)
    return False

def 持续x除以y秒点击一个位置直到画面变化_多区域判断画面变化(位置, adb路径, x, y, 变化区域列表, 最低相似度,线程事件=1):
    无用, 端口, hwnd, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb路径
    失败再延迟 = 0
    是否匹配2 = False

    # 获取初始截图
    png数据 = 获取_png_data(adb路径)
    模板图片 = cv2.imdecode(np.frombuffer(png数据, dtype=np.uint8), cv2.IMREAD_COLOR)

    # 为每个区域保存初始图像数据
    区域数据列表 = []
    for 变化区域 in 变化区域列表:
        x坐标, y坐标, 宽度, 高度 = 变化区域
        内存图片数据 = 模板图片[y坐标:y坐标 + 高度, x坐标:x坐标 + 宽度]
        变化扩大区域 = check_and_expand_region(变化区域)
        区域数据列表.append((变化扩大区域, 内存图片数据))

    # 执行第一次点击
    if 窗口矩形:
        真实鼠标坐标后台点击专用(hwnd, 窗口矩形, (位置[0], 位置[1]),
                                 PC全局延迟 + 失败再延迟, 0.5)
        失败再延迟 = 失败再延迟 + 0.01
    else:
        长按(adb路径, 位置[0], 位置[1], 持续时间=100+ int(失败再延迟*1000))
    可变速等待(0.5)

    for _ in range(x):
        if not 判断线程与值的布尔函数(线程事件):
            return False
        可变速等待(y + 失败再延迟 * 20)

        png数据 = 获取_png_data(adb路径)

        # 检查所有区域，只要有一个区域变化就认为画面变化
        有任何变化 = False
        for 变化扩大区域, 内存图片数据 in 区域数据列表:
            是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行内存图片匹配(
                png数据, 变化扩大区域, 内存图片数据, 最低相似度
            )
            if not 是否匹配:  # 注意：是否匹配为False表示有变化
                有任何变化 = True
                break  # 只要有一个区域变化，就跳出循环

        if 有任何变化:
            # 画面有变化
            if 是否匹配2:
                # 第二次检测到变化，退出循环
                break
            else:
                是否匹配2 = True

                可变速等待(0.5)
        else:
            # 画面没有变化，继续点击
            if 窗口矩形:
                真实鼠标坐标后台点击专用(hwnd, 窗口矩形, (位置[0], 位置[1]),
                                         PC全局延迟 + 失败再延迟, 0.5)
                失败再延迟 = 失败再延迟 + 0.01
            else:
                长按(adb路径, 位置[0], 位置[1], 持续时间=100+ int(失败再延迟*1000))
            可变速等待(0.5)

    return 是否匹配2
def 持续x除以y秒点击一个位置直到画面变化(位置,adb路径,x,y,变化区域,最低相似度,线程事件=1):
    无用, 端口, hwnd, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb路径
    失败再延迟 = 0
    是否匹配2 = False
    png数据 = 获取_png_data(adb路径)

    模板图片 = cv2.imdecode(np.frombuffer(png数据, dtype=np.uint8), cv2.IMREAD_COLOR)

    x坐标, y坐标, 宽度, 高度 = 变化区域

    内存图片数据 = 模板图片[y坐标:y坐标 + 高度, x坐标:x坐标 + 宽度]
    变化扩大区域 = check_and_expand_region(变化区域)
    if 窗口矩形:
        真实鼠标坐标后台点击专用(hwnd, 窗口矩形, (位置[0], 位置[1]),
                                 PC全局延迟 + 失败再延迟, 0.5)
        失败再延迟 = 失败再延迟 + 0.01
    else:
        长按(adb路径, 位置[0], 位置[1], 持续时间=100+ int(失败再延迟*1000))
    可变速等待(0.5)
    for _ in range(x):
        if not 判断线程与值的布尔函数(线程事件):
            return False
        可变速等待(y + 失败再延迟 * 20)

        png数据 = 获取_png_data(adb路径)
        是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行内存图片匹配(png数据, 变化扩大区域,
                                                                                            内存图片数据, 最低相似度)
        if 是否匹配:
            if 窗口矩形:
                真实鼠标坐标后台点击专用(hwnd, 窗口矩形, (位置[0], 位置[1]),
                                         PC全局延迟 + 失败再延迟, 0.5)
                失败再延迟 = 失败再延迟 + 0.01
            else:
                长按(adb路径, 位置[0], 位置[1], 持续时间=100+ int(失败再延迟*1000))
            可变速等待(0.5)
        else:
            if 是否匹配2:
                break
            是否匹配2 = True
    return 是否匹配2
def 持续x除以y秒图未出现则点击一个位置(位置,adb路径,x,y,模板路径,限定区域,最低相似度,线程事件=1,真实鼠标=False,配置列表=None, 鼠标等待=0.5,鼠标回弹=True,共享截图=None,基础延迟=0.001):
    无用, 端口, hwnd, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb路径
    失败再延迟 = 0
    是否匹配2=False
    for _ in range(x):
        if not 判断线程与值的布尔函数(线程事件):
            return False

        if 配置列表:
            if 共享截图 is not None:
                锁, 容器 = 共享截图
                with 锁:
                    png数据1 = 容器[0]
            else:
                png数据1 = 函数截图到内存直接返回NumPy数组(hwnd, 窗口矩形)
            是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(
                背景图片=png数据1, 限定区域=限定区域, 最低相似度=最低相似度,
                配置列表=配置列表)
        else:
            png数据1 = 获取_png_data(adb路径)
            是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(png数据1, 限定区域, 模板路径, 最低相似度)
        if 是否匹配:
            if 是否匹配2:
                break
            是否匹配2 =True
        else:
            if 窗口矩形:
                if 真实鼠标:

                    if not 判断线程与值的布尔函数(线程事件):
                        break  # 如果事件对象被清除，退出循环
                    if 鼠标回弹:
                        当前活动窗口 = win32gui.GetForegroundWindow()
                        键 = "alt"
                        for _ in range(50):
                            if not 判断线程与值的布尔函数(线程事件):
                                break  # 如果事件对象被清除，退出循环
                            time.sleep(0.05 + PC键盘延迟)
                            当前窗口 = win32gui.GetForegroundWindow()
                            if 当前窗口 == hwnd:

                                PyAutoGUI_模拟按键按下(键)
                                time.sleep(0.075 + PC键盘延迟)

                                time.sleep(鼠标等待)
                                PyAutoGUI_模拟鼠标左键单击(位置[0] + 窗口矩形[0], 位置[1] + 窗口矩形[1], 0.05 + 失败再延迟+基础延迟)
                                time.sleep(鼠标等待)
                                PyAutoGUI_模拟按键弹起(键)
                                break
                            else:
                                try:
                                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                                    win32gui.SetForegroundWindow(hwnd)
                                except Exception:

                                    PyAutoGUI_模拟按键按下(键)
                                    time.sleep(0.075 + PC键盘延迟)
                                    PyAutoGUI_模拟按键弹起(键)
                                    time.sleep(鼠标等待)
                                    PyAutoGUI_模拟鼠标左键单击(位置[0] + 窗口矩形[0], 位置[1] + 窗口矩形[1], 0.05 + 失败再延迟+基础延迟)
                                    time.sleep(鼠标等待)
                                    PyAutoGUI_模拟按键弹起(键)
                        for _ in range(50):
                            if not 判断线程与值的布尔函数(线程事件):
                                break  # 如果事件对象被清除，退出循环
                            try:
                                win32gui.ShowWindow(当前活动窗口, win32con.SW_RESTORE)
                                win32gui.SetForegroundWindow(当前活动窗口)
                            except Exception:
                                pass
                            当前窗口 = win32gui.GetForegroundWindow()
                            if 当前窗口 == 当前活动窗口:
                                break
                            time.sleep(0.05 + PC键盘延迟)
                    else:
                        点击执行器.添加前台点击任务(位置[0] + 窗口矩形[0], 位置[1] + 窗口矩形[1], 0.05 + PC全局延迟 + 失败再延迟)
                        time.sleep(0.05 + PC全局延迟 + 失败再延迟)
                else:
                    点击执行器.添加后台点击任务(hwnd, 窗口矩形, (位置[0], 位置[1]),
                                          PC全局延迟 + 失败再延迟, 鼠标等待,鼠标回弹=鼠标回弹)
                    time.sleep(PC全局延迟 + 失败再延迟+鼠标等待)
                失败再延迟 = 失败再延迟 + 0.01
            else:
                长按(adb路径, 位置[0], 位置[1], 持续时间=100+ int(失败再延迟*1000))

        可变速等待(y)
    return 是否匹配2

def 多图匹配_图未出现则点击一个位置(位置,adb路径,x,y,匹配列表,匹配字符,线程事件=1):
    """
    循环点一个位置直到图片出现
    :param adb路径:
    :param y:
    :param 匹配字符:
    :param 线程事件:
    :param 匹配列表:
    :param 位置: 元组
    :param x: 循环的次数，循环的延时为 y 秒
    :return: 是否出现结果
    """
    无用, 端口, hwnd, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb路径
    失败再延迟 = 0
    是否匹配2=False
    for _ in range(x):
        if not 判断线程与值的布尔函数(线程事件):
            return False
        可变速等待(y+失败再延迟*20)
        返回值 = 多图返回最像的一个(adb路径, 匹配列表)
        if 返回值["是否匹配"] and 匹配字符 in str(返回值["模板路径"]):
            if 是否匹配2:
                break
            是否匹配2 =True
        else:
            if 窗口矩形:
                真实鼠标坐标后台点击专用(hwnd, 窗口矩形, (位置[0], 位置[1]),
                                          PC全局延迟 + 失败再延迟, 0.5)
                失败再延迟 = 失败再延迟 + 0.01
            else:
                长按(adb路径, 位置[0], 位置[1], 持续时间=100+ int(失败再延迟*1000))
    return 是否匹配2


def 调整限定区域(限定区域, 屏幕边界=(0, 0, 1280, 720)):
    """调整限定区域确保在屏幕边界内"""
    x, y, 宽度, 高度 = 限定区域
    屏幕宽度, 屏幕高度 = 屏幕边界[2], 屏幕边界[3]

    # 调整x和宽度
    if x < 0:
        宽度 += x  # x为负数，所以加上x相当于减去绝对值
        x = 0
    if x + 宽度 > 屏幕宽度:
        宽度 = 屏幕宽度 - x

    # 调整y和高度
    if y < 0:
        高度 += y
        y = 0
    if y + 高度 > 屏幕高度:
        高度 = 屏幕高度 - y

    # 确保不为负数
    宽度 = max(宽度, 0)
    高度 = max(高度, 0)

    return x, y, 宽度, 高度
def 多图匹配_图未出现则点击一个位置增加区域预筛选(位置,adb路径,x,y,模板路径,限定区域,最低相似度,匹配列表,扩大像素,线程事件=1):
    """
    循环点一个位置直到图片出现
    :param adb路径:
    :param y:
    :param 模板路径:
    :param 限定区域:
    :param 最低相似度:
    :param 匹配列表:
    :param 扩大像素:
    :param 线程事件:
    :param 位置: 元组
    :param x: 循环的次数，循环的延时为 y 秒
    :return: 是否出现结果
    """
    无用, 端口, hwnd, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb路径
    失败再延迟 = 0
    是否匹配2=False
    with Image.open(模板路径) as img:
        宽度, 高度 = img.size
    for _ in range(x):
        if not 判断线程与值的布尔函数(线程事件):
            return False
        png数据 = 获取_png_data(adb路径)
        是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(png数据, 限定区域, 模板路径, 最低相似度)
        if 是否匹配:
            重构限定区域=(最大匹配x坐标-扩大像素, 最大匹配y坐标-扩大像素,宽度+扩大像素*2, 高度+扩大像素*2)
            重构限定区域 = 调整限定区域(重构限定区域)
            重构匹配列表 = []
            for 匹配项 in 匹配列表:
                新匹配项 = {"限定区域": 重构限定区域, "模板路径": 匹配项["模板路径"], "最低相似度": 匹配项["最低相似度"]}
                重构匹配列表.append(新匹配项)
            返回值 = 多图返回最像的一个(adb路径, 重构匹配列表)
            if 返回值["是否匹配"] and 模板路径 == 返回值["模板路径"]:
                if 是否匹配2:
                    break
                是否匹配2 = True
            else:
                是否匹配 = False
        if not 是否匹配:
            if 窗口矩形:
                真实鼠标坐标后台点击专用(hwnd, 窗口矩形, (位置[0], 位置[1]), PC全局延迟 + 失败再延迟, 0.5)
                失败再延迟 = 失败再延迟 + 0.01
            else:
                长按(adb路径, 位置[0], 位置[1], 持续时间=100+ int(失败再延迟*1000))
        可变速等待(y + 失败再延迟 * 20)
    return 是否匹配2


def 持续x除以y秒图未出现且图片未变化则点击一个位置(位置,adb路径,x,y,模板路径,限定区域,最低相似度,变化区域=(1159, 32, 51, 59)):
    """
    循环点一个位置直到图片出现
    :param adb路径:
    :param y:
    :param 模板路径:
    :param 限定区域:
    :param 最低相似度:
    :param 变化区域:
    :param 位置: 元组
    :param x: 循环的次数，循环的延时为 y 秒
    :return: 是否出现结果
    """
    无用, 端口, hwnd, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb路径
    失败再延迟 = 0
    是否匹配2=False
    png数据 = 获取_png_data(adb路径)

    模板图片 = cv2.imdecode(np.frombuffer(png数据, dtype=np.uint8), cv2.IMREAD_COLOR)

    x坐标, y坐标, 宽度, 高度 = 变化区域

    内存图片数据 = 模板图片[y坐标:y坐标 + 高度, x坐标:x坐标 + 宽度]
    变化扩大区域 = check_and_expand_region(变化区域)
    for _ in range(x):
        可变速等待(y+失败再延迟*20)
        png数据 = 获取_png_data(adb路径)
        是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(png数据,限定区域,模板路径,最低相似度)
        if 是否匹配:
            if 是否匹配2:
                break
            是否匹配2 =True
        else:
            if 窗口矩形:
                是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行内存图片匹配(png数据, 变化扩大区域, 内存图片数据, 0.8)
                if 是否匹配:
                    真实鼠标坐标后台点击专用(hwnd, 窗口矩形, (位置[0], 位置[1]),
                                             PC全局延迟 + 失败再延迟, 0.5)
                    失败再延迟 = 失败再延迟 + 0.01
                else:
                    print("画面变动")
                    模板图片 = cv2.imdecode(np.frombuffer(png数据, dtype=np.uint8), cv2.IMREAD_COLOR)
                    x坐标, y坐标, 宽度, 高度 = 变化区域
                    内存图片数据 = 模板图片[y坐标:y坐标 + 高度, x坐标:x坐标 + 宽度]

            else:
                长按(adb路径, 位置[0], 位置[1], 持续时间=100+ int(失败再延迟*1000))
    return 是否匹配2
def 持续x除以y秒图存在则点击一个位置(位置,adb路径,x,y,模板路径,限定区域,最低相似度,线程事件=1,真实鼠标=False,配置列表=None, 鼠标等待=0.5,鼠标回弹=True,共享截图=None,基础延迟=0.001):
    """
    循环点一个位置直到图片消失
    :param adb路径:
    :param y:
    :param 模板路径:
    :param 限定区域:
    :param 最低相似度:
    :param 位置: 元组
    :param x: 循环的次数，循环的延时为 y 秒
    :return: 是否出现结果
    """
    无用, 端口, hwnd, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb路径
    失败再延迟 = 0
    是否匹配2=0
    for _ in range(x):
        if not 判断线程与值的布尔函数(线程事件):
            return False
        可变速等待(y+失败再延迟*20)
        if 配置列表:
            if 共享截图 is not None:
                锁, 容器 = 共享截图
                with 锁:
                    png数据1 = 容器[0]
            else:
                png数据1 = 函数截图到内存直接返回NumPy数组(hwnd, 窗口矩形)
            是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(
                背景图片=png数据1, 限定区域=限定区域, 最低相似度=最低相似度,
                配置列表=配置列表)
        else:
            png数据1 = 获取_png_data(adb路径)
            是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(png数据1, 限定区域, 模板路径, 最低相似度)
        if 是否匹配:
            是否匹配2 = 1
            if 窗口矩形:
                if 真实鼠标:

                    if not 判断线程与值的布尔函数(线程事件):
                        break  # 如果事件对象被清除，退出循环
                    if 鼠标回弹:
                        当前活动窗口 = win32gui.GetForegroundWindow()
                        键 = "alt"
                        for _ in range(50):
                            if not 判断线程与值的布尔函数(线程事件):
                                break  # 如果事件对象被清除，退出循环
                            time.sleep(0.05 + PC键盘延迟)
                            当前窗口 = win32gui.GetForegroundWindow()
                            if 当前窗口 == hwnd:

                                PyAutoGUI_模拟按键按下(键)
                                time.sleep(0.075 + PC键盘延迟)

                                time.sleep(鼠标等待)
                                PyAutoGUI_模拟鼠标左键单击(位置[0] + 窗口矩形[0], 位置[1] + 窗口矩形[1], 0.05 + 失败再延迟 + 基础延迟)
                                time.sleep(鼠标等待)
                                PyAutoGUI_模拟按键弹起(键)
                                break
                            else:
                                try:
                                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                                    win32gui.SetForegroundWindow(hwnd)
                                except Exception:

                                    PyAutoGUI_模拟按键按下(键)
                                    time.sleep(0.075 + PC键盘延迟)
                                    PyAutoGUI_模拟按键弹起(键)
                                    time.sleep(鼠标等待)
                                    PyAutoGUI_模拟鼠标左键单击(位置[0] + 窗口矩形[0], 位置[1] + 窗口矩形[1], 0.05 + 失败再延迟 + 基础延迟)
                                    time.sleep(鼠标等待)
                                    PyAutoGUI_模拟按键弹起(键)
                        for _ in range(50):
                            if not 判断线程与值的布尔函数(线程事件):
                                break  # 如果事件对象被清除，退出循环
                            try:
                                win32gui.ShowWindow(当前活动窗口, win32con.SW_RESTORE)
                                win32gui.SetForegroundWindow(当前活动窗口)
                            except Exception:
                                pass
                            当前窗口 = win32gui.GetForegroundWindow()
                            if 当前窗口 == 当前活动窗口:
                                break
                            time.sleep(0.05 + PC键盘延迟)
                    else:
                        点击执行器.添加前台点击任务(位置[0] + 窗口矩形[0], 位置[1] + 窗口矩形[1], 0.05 + PC全局延迟 + 失败再延迟)
                        time.sleep(0.05 + PC全局延迟 + 失败再延迟)
                else:
                    点击执行器.添加后台点击任务(hwnd, 窗口矩形, (位置[0], 位置[1]),
                                                PC全局延迟 + 失败再延迟, 鼠标等待, 鼠标回弹=鼠标回弹)
                    time.sleep(PC全局延迟 + 失败再延迟 + 鼠标等待)
                失败再延迟 = 失败再延迟 + 0.01
            else:
                长按(adb路径, 最大匹配x坐标, 最大匹配y坐标, 持续时间=100+ int(失败再延迟*1000))
        else:
            if 是否匹配2==2:
                return True
            if 是否匹配2==1:
                是否匹配2 = 2
    return False
def 持续x除以y秒按键一个图片并且失败增加时长(adb路径,x,y,按键码,模板路径,限定区域,最低相似度,线程事件=1,配置列表=None, 共享截图=None):
    """
        循环点一个图片到图片消失出现
        :param adb路径:
        :param y:
        :param 按键码:
        :param 模板路径:
        :param 限定区域:
        :param 最低相似度:
        :param 线程事件:
        :param x: 循环的次数，循环的延时为 y 秒
        :return: 是否出现结果
        """
    无用, 端口, hwnd, 窗口矩形, (_, _) = adb路径
    失败再延迟 = 0
    是否匹配2=False

    for _ in range(x):
        if not 判断线程与值的布尔函数(线程事件):
            return False

        if 配置列表:
            if 共享截图 is not None:
                锁, 容器 = 共享截图
                with 锁:
                    png数据1 = 容器[0]
            else:
                png数据1 = 函数截图到内存直接返回NumPy数组(hwnd, 窗口矩形)
            是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(
                背景图片=png数据1, 限定区域=限定区域, 最低相似度=最低相似度,
                配置列表=配置列表)
        else:
            png数据1 = 获取_png_data(adb路径)
            是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(png数据1, 限定区域, 模板路径, 最低相似度)
        if 是否匹配:
            是否匹配2 =True

            模拟按键长按(hwnd, 按键码,0.01 + 失败再延迟)
            失败再延迟 = 失败再延迟 + 0.009

            可变速等待(1)
        else:
            if 是否匹配2:
                break
        可变速等待(y)
    return 是否匹配2
def 持续x除以y秒按键到图出现(按键码,adb路径,x,y,模板路径,限定区域,最低相似度,线程事件=1,配置列表=None, 共享截图=None):
    """
    循环点一个位置直到图片出现
    :param adb路径:
    :param y:
    :param 模板路径:
    :param 限定区域:
    :param 最低相似度:
    :param 线程事件:
    :param 位置: 元组
    :param x: 循环的次数，循环的延时为 y 秒
    :return: 是否出现结果
    """
    无用, 端口, hwnd, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb路径
    失败再延迟 = 0
    是否匹配2=False
    for _ in range(x):
        if not 判断线程与值的布尔函数(线程事件):
            return False

        if 配置列表:
            if 共享截图 is not None:
                锁, 容器 = 共享截图
                with 锁:
                    png数据1 = 容器[0]
            else:
                png数据1 = 函数截图到内存直接返回NumPy数组(hwnd, 窗口矩形)
            是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(
                背景图片=png数据1, 限定区域=限定区域, 最低相似度=最低相似度,
                配置列表=配置列表)
        else:
            png数据1 = 获取_png_data(adb路径)
            是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(png数据1, 限定区域, 模板路径, 最低相似度)
        if 是否匹配:
            if 是否匹配2:
                break
            是否匹配2 =True
        else:
            if 窗口矩形:
                模拟按键长按(hwnd, 按键码,0.01 + 失败再延迟)
                失败再延迟 = 失败再延迟 + 0.01
            else:
                长按(adb路径, 位置[0], 位置[1], 持续时间=100+ int(失败再延迟*1000))
        可变速等待(y + 失败再延迟 * 20)
    return 是否匹配2
def 持续x除以y秒点击一个图片并且失败增加时长(adb路径,x,y,模板路径,限定区域,最低相似度,线程事件=1,真实鼠标=True,鼠标等待=0.5,配置列表=None,鼠标回弹=True, 共享截图=None):
    无用, 端口, hwnd, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb路径
    失败再延迟 = 0
    是否匹配2=0

    for _ in range(x):
        if not 判断线程与值的布尔函数(线程事件):
            return False

        if 配置列表:
            if 共享截图 is not None:
                锁, 容器 = 共享截图
                with 锁:
                    png数据1 = 容器[0]
            else:
                png数据1 = 函数截图到内存直接返回NumPy数组(hwnd, 窗口矩形)
            是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域数组匹配(
                背景图片=png数据1, 限定区域=限定区域, 最低相似度=最低相似度,
                配置列表=配置列表)
        else:
            png数据1 = 获取_png_data(adb路径)
            是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(png数据1,限定区域,模板路径,最低相似度)
        if 是否匹配:
            是否匹配2 =-1
            if 窗口矩形:
                if 真实鼠标:
                    if not 判断线程与值的布尔函数(线程事件):
                        break  # 如果事件对象被清除，退出循环
                    if 鼠标回弹:
                        当前活动窗口 = win32gui.GetForegroundWindow()
                        键 = "alt"
                        for _ in range(50):
                            if not 判断线程与值的布尔函数(线程事件):
                                break  # 如果事件对象被清除，退出循环
                            time.sleep(0.05 + PC键盘延迟)
                            当前窗口 = win32gui.GetForegroundWindow()
                            if 当前窗口 == hwnd:

                                PyAutoGUI_模拟按键按下(键)
                                time.sleep(0.075 + PC键盘延迟)
                                PyAutoGUI_模拟按键弹起(键)
                                time.sleep(鼠标等待)
                                PyAutoGUI_模拟鼠标左键单击(最大匹配x坐标 + 窗口矩形[0], 最大匹配y坐标 + 窗口矩形[1], 0.05 + 失败再延迟)
                                time.sleep(鼠标等待)
                                break
                            else:
                                try:
                                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                                    win32gui.SetForegroundWindow(hwnd)
                                except Exception:

                                    PyAutoGUI_模拟按键按下(键)
                                    time.sleep(0.075 + PC键盘延迟)
                                    PyAutoGUI_模拟按键弹起(键)
                                    time.sleep(鼠标等待)
                                    PyAutoGUI_模拟鼠标左键单击(最大匹配x坐标 + 窗口矩形[0], 最大匹配y坐标 + 窗口矩形[1], 0.05 + 失败再延迟)
                                    time.sleep(鼠标等待)
                        for _ in range(50):
                            if not 判断线程与值的布尔函数(线程事件):
                                break  # 如果事件对象被清除，退出循环
                            try:
                                win32gui.ShowWindow(当前活动窗口, win32con.SW_RESTORE)
                                win32gui.SetForegroundWindow(当前活动窗口)
                            except Exception:
                                pass
                            当前窗口 = win32gui.GetForegroundWindow()
                            if 当前窗口 == 当前活动窗口:
                                break
                            time.sleep(0.05 + PC键盘延迟)
                    else:
                        点击执行器.添加前台点击任务(最大匹配x坐标 + 窗口矩形[0], 最大匹配y坐标 + 窗口矩形[1], 0.05 + 失败再延迟)
                else:
                    点击执行器.添加后台点击任务(hwnd, 窗口矩形, (最大匹配x坐标, 最大匹配y坐标),
                                          延时=PC全局延迟 + 失败再延迟, 等待=鼠标等待,鼠标回弹=鼠标回弹)
                失败再延迟 = 失败再延迟 + 0.009
            else:
                长按(adb路径, 最大匹配x坐标, 最大匹配y坐标, 持续时间=100+ int(失败再延迟*1000))
        else:

            if 是否匹配2==-1:
                是否匹配2=True

                break
        可变速等待(y)
    if 是否匹配2==-1:
        是否匹配2=False
    return 是否匹配2
def 持续x除以y秒点击一个图片没钱卖鱼饵专用(adb路径,x,y,模板路径,限定区域,最低相似度,线程事件=1,真实鼠标=False,模板路径2=None):
    """
        循环点一个图片到图片消失出现
        :param adb路径:
        :param y:
        :param 模板路径:
        :param 限定区域:
        :param 最低相似度:
        :param 线程事件:
        :param x: 循环的次数，循环的延时为 y 秒
        :return: 是否出现结果
        """
    无用, 端口, hwnd, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb路径
    失败再延迟 = 0
    是否匹配2=False

    for _ in range(x):
        if not 判断线程与值的布尔函数(线程事件):
            return False
        开始时间=time.time()
        while time.time()-开始时间<y:
            png数据 = 获取_png_data(adb路径)
            if 模板路径2:
                是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(png数据, (498, 299, 282, 120), 模板路径2, 最低相似度)
                if 是否匹配:
                    return 模板路径2
            time.sleep(0.05)
        else:
            png数据 = 获取_png_data(adb路径)

        是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(png数据,限定区域,模板路径,最低相似度)
        if 是否匹配:
            是否匹配2 =True
            if 窗口矩形:
                if 真实鼠标:
                    if not 判断线程与值的布尔函数(线程事件):
                        break  # 如果事件对象被清除，退出循环
                    当前活动窗口 = win32gui.GetForegroundWindow()
                    键="alt"
                    for _ in range(50):
                        if not 判断线程与值的布尔函数(线程事件):
                            break  # 如果事件对象被清除，退出循环
                        time.sleep(0.05 + PC键盘延迟)
                        当前窗口 = win32gui.GetForegroundWindow()
                        if 当前窗口 == hwnd:

                            PyAutoGUI_模拟按键按下(键)
                            time.sleep(0.075 + PC键盘延迟)
                            PyAutoGUI_模拟按键弹起(键)
                            time.sleep(0.5)
                            PyAutoGUI_模拟鼠标左键单击(最大匹配x坐标 + 窗口矩形[0], 最大匹配y坐标 + 窗口矩形[1], 0.05 + 失败再延迟)
                            time.sleep(0.5)
                            break
                        else:
                            try:
                                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                                win32gui.SetForegroundWindow(hwnd)
                            except Exception:

                                PyAutoGUI_模拟按键按下(键)
                                time.sleep(0.075 + PC键盘延迟)
                                PyAutoGUI_模拟按键弹起(键)
                                time.sleep(0.5)
                                PyAutoGUI_模拟鼠标左键单击(最大匹配x坐标 + 窗口矩形[0], 最大匹配y坐标 + 窗口矩形[1], 0.05 + 失败再延迟)
                                time.sleep(0.5)
                    for _ in range(50):
                        if not 判断线程与值的布尔函数(线程事件):
                            break  # 如果事件对象被清除，退出循环
                        try:
                            win32gui.ShowWindow(当前活动窗口, win32con.SW_RESTORE)
                            win32gui.SetForegroundWindow(当前活动窗口)
                        except Exception:
                            pass
                        当前窗口 = win32gui.GetForegroundWindow()
                        if 当前窗口 == 当前活动窗口:
                            break
                        time.sleep(0.05 + PC键盘延迟)
                else:
                    真实鼠标坐标后台点击专用(hwnd, 窗口矩形, (最大匹配x坐标, 最大匹配y坐标),
                                          PC全局延迟 + 失败再延迟, 0.5)
                失败再延迟 = 失败再延迟 + 0.009
            else:
                长按(adb路径, 最大匹配x坐标, 最大匹配y坐标, 持续时间=100+ int(失败再延迟*1000))
            可变速等待(1)
        else:
            if 是否匹配2:
                break

    return 是否匹配2
def 多图匹配_点击一个图片(adb路径,x,y,匹配列表,匹配字符,线程事件=1):
    """
    循环点一个位置直到图片出现
    :param adb路径:
    :param y:
    :param 匹配列表:
    :param 匹配字符:
    :param 线程事件:
    :param x: 循环的次数，循环的延时为 y 秒
    :return: 是否出现结果
    """
    无用, 端口, hwnd, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb路径
    失败再延迟 = 0
    是否匹配2=False
    for _ in range(x):
        if not 判断线程与值的布尔函数(线程事件):
            return False
        可变速等待(y+失败再延迟*20)
        返回值 = 多图返回最像的一个(adb路径, 匹配列表)
        if 返回值["是否匹配"] and 匹配字符 in str(返回值["模板路径"]):
            是否匹配2 = True
            if 窗口矩形:
                真实鼠标坐标后台点击专用(hwnd, 窗口矩形, (返回值["最大匹配x坐标"], 返回值["最大匹配y坐标"]),
                                         PC全局延迟 + 失败再延迟, 0.5)
                失败再延迟 = 失败再延迟 + 0.009
            else:
                长按(adb路径, 返回值["最大匹配x坐标"], 返回值["最大匹配y坐标"], 持续时间=100 + int(失败再延迟 * 1000))
        else:
            if 是否匹配2:
                break
    return 是否匹配2

def 多图匹配_点击一个图片增加区域预筛选(adb路径,x,y,模板路径,限定区域,最低相似度,匹配列表,扩大像素,线程事件=1):
    """
    循环点一个位置直到图片出现
    :param adb路径:
    :param y:
    :param 模板路径:
    :param 限定区域:
    :param 最低相似度:
    :param 匹配列表:
    :param 扩大像素:
    :param 线程事件:
    :param x: 循环的次数，循环的延时为 y 秒
    :return: 是否出现结果
    """
    无用, 端口, hwnd, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb路径
    失败再延迟 = 0
    是否匹配2=False
    with Image.open(模板路径) as img:
        宽度, 高度 = img.size
    for _ in range(x):
        if not 判断线程与值的布尔函数(线程事件):
            return False
        png数据 = 获取_png_data(adb路径)
        是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(png数据, 限定区域, 模板路径, 最低相似度)
        if 是否匹配:
            重构限定区域 = (最大匹配x坐标 - 扩大像素, 最大匹配y坐标 - 扩大像素, 宽度 + 扩大像素 * 2, 高度 + 扩大像素 * 2)
            重构限定区域 = 调整限定区域(重构限定区域)
            重构匹配列表 = []
            for 匹配项 in 匹配列表:
                新匹配项 = {
                    "限定区域": 重构限定区域,
                    "模板路径": 匹配项["模板路径"],
                    "最低相似度": 匹配项["最低相似度"]
                }
                重构匹配列表.append(新匹配项)
            返回值 = 多图返回最像的一个(adb路径, 重构匹配列表)
            if 返回值["是否匹配"] and 模板路径 == 返回值["模板路径"]:
                是否匹配2 = True
                if 窗口矩形:
                    真实鼠标坐标后台点击专用(hwnd, 窗口矩形, (返回值["最大匹配x坐标"], 返回值["最大匹配y坐标"]),
                                             PC全局延迟 + 失败再延迟, 0.5)
                    失败再延迟 = 失败再延迟 + 0.009
                else:
                    长按(adb路径, 返回值["最大匹配x坐标"], 返回值["最大匹配y坐标"], 持续时间=100 + int(失败再延迟 * 1000))
            else:
                if 是否匹配2:
                    break
        else:
            if 是否匹配2:
                break
        可变速等待(y + 失败再延迟 * 20)
    return 是否匹配2

def 持续x除以2秒图未出现则点击一个位置(位置,hwnd,窗口矩形,PC全局延迟,adb路径,x,模板路径,限定区域,最低相似度):
    """
    循环点一个位置直到图片出现
    :param 位置: 元组
    :param hwnd:
    :param 窗口矩形:
    :param PC全局延迟:
    :param adb路径:
    :param x: 循环的次数，循环的延时为0.5秒
    :param 模板路径:
    :param 限定区域:
    :param 最低相似度:
    :return: 是否出现结果
    """
    失败再延迟 = 0
    是否匹配2=False
    for _ in range(x):
        可变速等待(0.6+失败再延迟*20)
        png数据 = 获取_png_data(adb路径)
        是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(png数据,限定区域,模板路径,最低相似度)
        if 是否匹配:
            if 是否匹配2:
                break
            是否匹配2 =True
        else:
            if 窗口矩形:
                真实鼠标坐标后台点击专用(hwnd, 窗口矩形, (位置[0], 位置[1]),
                                          PC全局延迟 + 失败再延迟, 0.5)
                失败再延迟 = 失败再延迟 + 0.009
            else:
                长按(adb路径, 位置[0], 位置[1], 持续时间=100+ int(失败再延迟*1000))
    return 是否匹配2
def 持续x除以2秒点击一个图片并且失败增加时长(hwnd,窗口矩形,PC全局延迟,adb路径,x,模板路径,限定区域,最低相似度):
    失败再延迟 = 0
    是否匹配2=False
    for _ in range(x):
        可变速等待(0.5)
        png数据 = 获取_png_data(adb路径)
        是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(png数据,限定区域,模板路径,最低相似度)
        if 是否匹配:
            是否匹配2 =True
            if 窗口矩形:
                真实鼠标坐标后台点击专用(hwnd, 窗口矩形, (最大匹配x坐标, 最大匹配y坐标),
                                          PC全局延迟 + 失败再延迟, 0.5)
                失败再延迟 = 失败再延迟 + 0.009
            else:
                长按(adb路径, 最大匹配x坐标, 最大匹配y坐标, 持续时间=100+ int(失败再延迟*1000))
            可变速等待(1)
        else:
            if 是否匹配2:
                break
    return 是否匹配2
def 持续x除以y秒点击一个区域中心图片不出现则增加时长(hwnd,窗口矩形,PC全局延迟,adb路径,x,y,模板路径,限定区域,最低相似度):
    失败再延迟 = 0
    是否匹配2=False
    x1,y1,x2,y2=限定区域
    for _ in range(x):
        可变速等待(y)
        png数据 = 获取_png_data(adb路径)
        是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(png数据,限定区域,模板路径,最低相似度)
        if 是否匹配:
            pass
        else:
            是否匹配2 =True
            if 窗口矩形:
                真实鼠标坐标后台点击专用(hwnd, 窗口矩形, (int(0.5*(x1+x2)), int(0.5*(y1+y2))),
                                          PC全局延迟 + 失败再延迟, 0.5)
                失败再延迟=失败再延迟+0.009
            else:
                长按(adb路径, 最大匹配x坐标, 最大匹配y坐标, 持续时间=100+ int(失败再延迟*1000)+ int(失败再延迟*1000))
            可变速等待(1)
    return 是否匹配2
def pc端单击键盘(hwnd,PC键盘延迟,键列表 ,次数,线程事件):
    """
    pc端单击键盘(hwnd, PC键盘延迟, ["w","s"], 1,线程事件)
    """
    当前活动窗口 = win32gui.GetForegroundWindow()
    for _ in range(1000):
        if not 线程事件.is_set():
            break  # 如果事件对象被清除，退出循环
        time.sleep(0.05+ PC键盘延迟)
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
        if not 线程事件.is_set():
            break  # 如果事件对象被清除，退出循环
        try:
            win32gui.ShowWindow(当前活动窗口, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(当前活动窗口)
        except Exception:
            pass
        当前窗口 = win32gui.GetForegroundWindow()
        if 当前窗口 == 当前活动窗口:
            break
        time.sleep(0.05+ PC键盘延迟)

def pc端单击键盘无线程事件(hwnd,PC键盘延迟,键列表 ,次数):
    """
    pc端单击键盘(hwnd, PC键盘延迟, ["w","s"], 1,线程事件)
    """
    当前活动窗口 = win32gui.GetForegroundWindow()
    for _ in range(1000):

        time.sleep(0.05+ PC键盘延迟)
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
        time.sleep(0.05+ PC键盘延迟)

def 拾取奖励模拟器(adb路径,current_dir,持续时间):
    无用, 端口, hwnd, 窗口矩形, (_, _) = adb路径
    start_time = time.time()
    结束时间 = 持续时间
    while time.time() - start_time < 结束时间:
        time.sleep(0.1)
        长按(adb路径, 640, 360, 持续时间=100)
        png数据 = 获取_png_data(adb路径)
        是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(
            背景图片数据=png数据,
            限定区域=(100, 400, 1080, 320),
            模板路径=current_dir / "图片" / "宝珠迷宫" / "UI界面" / "奖励圆圈.png",
            最低相似度=0.6
        )
        if 是否匹配:
            长按(adb路径, 最大匹配x坐标, 最大匹配y坐标, 持续时间=100)
        是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(
            背景图片数据=png数据,
            限定区域=(100, 400, 1080, 320),
            模板路径=current_dir / "图片" / "宝珠迷宫" / "UI界面" / "奖励圆圈1.png",
            最低相似度=0.6
        )
        if 是否匹配:
            长按(adb路径, 最大匹配x坐标, 最大匹配y坐标, 持续时间=100)


def pc端移动是否按f(键,是否,adb路径,current_dir,持续时间,线程事件):
    无用, 端口, hwnd, 窗口矩形, (PC全局延迟, PC键盘延迟) = adb路径
    if 窗口矩形:
        最大匹配x坐标 = 0
        最大匹配y坐标 = 0
        当前活动窗口 = win32gui.GetForegroundWindow()
        for _ in range(100):
            if not 线程事件.is_set():
                break  # 如果事件对象被清除，退出循环
            time.sleep(0.05)
            当前窗口 = win32gui.GetForegroundWindow()
            if 当前窗口 == hwnd:
                PyAutoGUI_模拟按键按下(键)
                start_time = time.time()
                结束时间=持续时间
                while time.time() - start_time < 结束时间:
                    当前窗口 = win32gui.GetForegroundWindow()
                    if 当前窗口 != hwnd:
                        PyAutoGUI_模拟按键弹起(键)
                        结束时间 = 结束时间 - (time.time() - start_time)
                        for _ in range(3000):
                            if not 线程事件.is_set():
                                break  # 如果事件对象被清除，退出循环
                            当前窗口 = win32gui.GetForegroundWindow()
                            if 当前窗口 == hwnd:
                                start_time = time.time()
                                PyAutoGUI_模拟按键按下(键)
                                break
                            else:
                                try:
                                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                                    win32gui.SetForegroundWindow(hwnd)
                                except Exception as e:
                                    PyAutoGUI_模拟按键按下("v")
                                    PyAutoGUI_模拟按键弹起("v")
                    if 是否:
                        PyAutoGUI_模拟按键按下("f")
                        time.sleep(0.075 + PC键盘延迟)
                        PyAutoGUI_模拟按键弹起("f")
                PyAutoGUI_模拟按键弹起(键)

                break
            else:
                try:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                except Exception:
                    PyAutoGUI_模拟按键按下("v")
                    PyAutoGUI_模拟按键弹起("v")
        for _ in range(100):
            if not 线程事件.is_set():
                break  # 如果事件对象被清除，退出循环
            try:
                win32gui.ShowWindow(当前活动窗口, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(当前活动窗口)
            except Exception:
                pass
            当前窗口 = win32gui.GetForegroundWindow()
            if 当前窗口 == 当前活动窗口:
                break
            time.sleep(0.05)
        失败再延迟 = 0
        if 窗口矩形:
            真实鼠标坐标后台点击专用(hwnd, 窗口矩形, (最大匹配x坐标, 最大匹配y坐标),
                                     0.009 + PC全局延迟 + 失败再延迟, 0.5)
        else:
            长按(adb路径, 最大匹配x坐标, 最大匹配y坐标, 持续时间=100+ int(失败再延迟*1000))
        失败再延迟 = 失败再延迟 + 0.002
        time.sleep(2)

    else:
        if 键=="a":
            x1=1200
            x2=0
        else:
            x1=80
            x2=1280
        if 是否:
            for _ in range(int(持续时间/0.5)):
                if not 线程事件.is_set():
                    break  # 如果事件对象被清除，退出循环
                滑动(adb路径, x1, 360, x2, 360, 持续时间=500)
                for intx in range(29):
                    长按(adb路径, 300 + 20 * intx, 549, 持续时间=5)

        else:
            滑动(adb路径, x1, 360, x2, 360, 持续时间=持续时间*1000)


def 判断键(最大匹配x坐标):
    if 最大匹配x坐标<269:
        return 0
    elif 最大匹配x坐标<419:
        return 1
    elif 最大匹配x坐标 < 567:
        return 2
    elif 最大匹配x坐标<711:
        return 3
    elif 最大匹配x坐标 < 859:
        return 4
    elif 最大匹配x坐标<1007:
        return 5
    else:
        return 0
def 判断区域(i):
    return (149+83*i, 441, 330, 95)
    if i ==0:
        return (149, 441, 330, 95)
    elif i ==1:
        return (232, 441, 330, 95)
    elif  i ==2:
        return (315, 441, 330, 95)
    elif  i ==3:
        return (398, 441, 330, 95)
    elif  i ==4:
        return (481, 441, 330, 95)
    elif i ==5:
        return (564, 441, 330, 95)
    else:
        return (149, 441, 993, 95)
    """ if i ==0:
        return (149, 441, 496, 95)
    elif i ==1:
        return (149, 441, 496, 95)
    elif  i ==2:
        return (299, 441, 496, 95)
    elif  i ==3:
        return (467, 441, 496, 95)
    elif  i ==4:
        return (640, 441, 496, 95)
    elif i ==5:
        return (640, 441, 496, 95)
    else:
        return (149, 441, 496, 95)"""
def 音游(current_dir,adb路径,线程事件):
    相似度 = 0.5
    区域1 = (199, 539, 42, 28)
    区域2 = (368, 540, 42, 28)
    区域3 = (540, 540, 42, 28)
    区域4 = (704, 540, 42, 28)
    区域5 = (870, 540, 42, 28)
    区域6 = (1036, 539, 42, 28)

    匹配列表 = [{"限定区域": 区域1, "模板路径": Path(rf"{current_dir}\图片\音游\Z.png"), "最低相似度": 相似度, },
                {"限定区域": 区域2, "模板路径": Path(rf"{current_dir}\图片\音游\X.png"), "最低相似度": 相似度, },
                {"限定区域": 区域3, "模板路径": Path(rf"{current_dir}\图片\音游\C.png"), "最低相似度": 相似度, },
                {"限定区域": 区域4, "模板路径": Path(rf"{current_dir}\图片\音游\V.png"), "最低相似度": 相似度, },
                {"限定区域": 区域5, "模板路径": Path(rf"{current_dir}\图片\音游\B.png"), "最低相似度": 相似度, },
                {"限定区域": 区域6, "模板路径": Path(rf"{current_dir}\图片\音游\N.png"), "最低相似度": 相似度, }, ]
    按键列表=["z","x","c","v","b","n"]
    按键按下时间字典 = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0}
    png数据列表=[]
    while 线程事件.is_set():
        png数据 = 获取_png_data(adb路径)
        返回值 = 函数_在指定区域内进行模板匹配多(png数据, 匹配列表)
        for i, 结果 in enumerate(返回值):
            if 结果["是否匹配"]:
                PyAutoGUI_模拟按键弹起(按键列表[i])
                按键按下时间字典[i]=0
            else:
                PyAutoGUI_模拟按键按下(按键列表[i])
                if 按键按下时间字典[i]:
                    if time.time()-按键按下时间字典[i]>0.1:
                        是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(背景图片数据=png数据, 限定区域=(141, 495, 998, 81), 模板路径=Path(rf"{current_dir}\图片\音游\中继键.png"), 最低相似度=0.8)
                        if 是否匹配:
                            返回值=判断键(最大匹配x坐标)
                            返回值=按键列表[返回值]
                            PyAutoGUI_模拟按键弹起(返回值)
                            PyAutoGUI_模拟按键按下(返回值)
                            PyAutoGUI_模拟按键弹起(返回值)
                            PyAutoGUI_模拟按键按下(返回值)
                        #相似度=0.6; 限定区域=判断区域(i); 模板路径 = Path(rf"{current_dir}\图片\音游\终点蓝键{i}.png"); 是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(背景图片数据=png数据, 限定区域=限定区域, 模板路径=模板路径, 最低相似度=相似度)if 是否匹配: 返回值 = 判断键(最大匹配x坐标); 返回值 = 按键列表[返回值]; PyAutoGUI_模拟按键弹起(返回值); PyAutoGUI_模拟按键按下(返回值)  #png数据列表.append({返回值:png数据}) 是否匹配, max_val, 最大匹配x坐标, 最大匹配y坐标 = 函数_在指定区域内进行模板匹配(背景图片数据=png数据, 限定区域=限定区域, 模板路径=Path(rf"{current_dir}\图片\音游\终点绿键.png"), 最低相似度=相似度) if 是否匹配: 返回值 = 判断键(最大匹配x坐标); 返回值 = 按键列表[返回值]; PyAutoGUI_模拟按键弹起(返回值); PyAutoGUI_模拟按键按下(返回值); PyAutoGUI_模拟按键按下(返回值); PyAutoGUI_模拟按键弹起(返回值); PyAutoGUI_模拟按键按下(返回值) #png数据列表.append({返回值:png数据})#if time.time() - 按键按下时间字典[i] > 1:#png数据列表.append(png数据)
                else:
                    按键按下时间字典[i] = time.time()
    for i, 结果 in enumerate(png数据列表):
        # 提取键
        key = list(结果.keys())[0]

        # 提取值
        value = list(结果.values())[0]
        filePath = Path(rf"{current_dir}\图片\音游\新建文件夹\{i}-{key}-screen.png")
        with open(filePath, 'wb') as f:
            f.write(value)
    for i in 按键列表:
        PyAutoGUI_模拟按键弹起(i)

