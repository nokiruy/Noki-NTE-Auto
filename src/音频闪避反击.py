import pyaudiowpatch as pyaudio
import numpy as np
import librosa
import time
from pathlib import Path
from scipy.signal import correlate, butter, sosfiltfilt
import pydirectinput
import sys
import collections
import threading
import multiprocessing
import tkinter.messagebox as msgbox
from project_paths import APP_ROOT

# ==================== 路径 ====================




# ==================== 音频工具函数 ====================
def 计算主频带(模板, 采样率, 能量比=0.95, 最低频率=3000):
    """
    返回 (低频截止, 高频截止)。
    若能量比==1，只做高通滤波，此时返回 (最低频率, 采样率/2)。
    """
    if 能量比 >= 1.0:
        return 最低频率, 采样率 / 2  # 高通模式

    fft_vals = np.abs(np.fft.rfft(模板))
    freqs = np.fft.rfftfreq(len(模板), 1 / 采样率)
    总能量 = np.sum(fft_vals ** 2)
    累积 = np.cumsum(fft_vals ** 2)

    低频索引 = np.where(累积 >= 总能量 * (1 - 能量比))[0]
    高频索引 = np.where(累积 >= 总能量 * 能量比)[0]
    低频 = freqs[低频索引[0]] if len(低频索引) > 0 else 0
    高频 = freqs[高频索引[0]] if len(高频索引) > 0 else 采样率 / 2

    低频 = max(低频, 最低频率)
    高频 = min(高频, 采样率 / 2 - 1)
    return 低频, 高频

def 设计滤波器(低切, 高切, 采样率, order=4):
    """
    若低切 <= 20 且高切 >= 采样率/2-1，则不过滤，返回 None。
    若高切 >= 采样率/2-1，则设计高通滤波器；否则设计带通滤波器。
    """
    if 低切 <= 20 and 高切 >= 采样率 / 2 - 1:
        return None  # 不需要滤波
    if 高切 >= 采样率 / 2 - 1:
        # 高通
        sos = butter(order, 低切, btype='highpass', fs=采样率, output='sos')
    else:
        sos = butter(order, [低切, 高切], btype='band', fs=采样率, output='sos')
    return sos

def 应用滤波器(信号, sos):
    """零相位滤波"""
    if sos is None:
        return 信号
    return sosfiltfilt(sos, 信号)

# ==================== 音频模板类 ====================
class 音频模板:
    def __init__(self, 路径, 名称, 采样率, 截取范围=(0, None)):
        """
        截取范围: (起始秒, 结束秒)，结束秒为 None 表示到文件末尾，但最多取 0.5 秒
        """
        self.名称 = 名称
        起始秒, 结束秒 = 截取范围
        if 结束秒 is not None and 结束秒 <= 起始秒:
            msgbox.showerror("参数错误", f"模板 '{名称}' 截取范围无效: 起始={起始秒}, 结束={结束秒}")
            raise ValueError("截取范围无效")
        # 加载原始音频
        y_full, sr = librosa.load(路径, sr=采样率, duration=None)
        total_duration = len(y_full) / sr
        if 结束秒 is None:
            实际结束秒 = min(total_duration, 0.5)
        else:
            实际结束秒 = 结束秒
        if 实际结束秒 > total_duration:
            msgbox.showerror("时长不足", f"模板 '{名称}' 文件时长不足：需要 {实际结束秒:.2f}s，实际只有 {total_duration:.2f}s")
            raise ValueError("文件时长不足")
        起始采样点 = int(起始秒 * sr)
        结束采样点 = int(实际结束秒 * sr)
        y = y_full[起始采样点:结束采样点]
        if len(y) == 0:
            msgbox.showerror("截取错误", f"模板 '{名称}' 截取后长度为0")
            raise ValueError("截取后长度为0")
        y = y - np.mean(y)
        self.模板 = y / (np.std(y) + 1e-8)
        self.长度 = len(self.模板)

# ==================== 极速归一化互相关 ====================
def 极速匹配(信号, 模板):
    L = len(模板)
    if len(信号) < L:
        return 0.0
    cumsum = np.cumsum(信号)
    cumsum_sq = np.cumsum(信号 ** 2)
    win_sum = cumsum[L-1:] - np.concatenate(([0], cumsum[:-L]))
    win_sum_sq = cumsum_sq[L-1:] - np.concatenate(([0], cumsum_sq[:-L]))
    win_mean = win_sum / L
    win_var = (win_sum_sq / L) - win_mean ** 2
    win_std = np.sqrt(np.maximum(win_var, 0.0)) + 1e-8
    raw_corr = correlate(信号, 模板, mode='valid', method='fft')
    ncc = raw_corr / (win_std * L)
    return float(np.max(ncc))

# ==================== 主处理循环（支持事件控制） ====================
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
from 后台键鼠 import 模拟鼠标左键长按,模拟按键长按

def 运行主循环(环回设备, 采样率, 模板列表, 阈值, 冷却秒, 控制事件,
                采集块秒=0.04, 窗口余量秒=0.05, 缓冲区时长秒=None,
                模板滤波参数=None,句柄=None):
    if 模板滤波参数 is None:
        模板滤波参数 = [(0.95, 3000)] * len(模板列表)

    最长模板长度 = max(t.长度 for t in 模板列表)
    最小缓冲秒 = 最长模板长度 / 采样率 + 0.05

    if 缓冲区时长秒 is None:
        缓冲区时长秒 = 最小缓冲秒
    elif 缓冲区时长秒 < 最小缓冲秒:
        msgbox.showerror("参数错误", f"缓冲区时长不足！最小需要 {最小缓冲秒:.3f}s，当前设置 {缓冲区时长秒:.3f}s")
        return

    检测窗口 = 最长模板长度 + int(窗口余量秒 * 采样率)

    p = pyaudio.PyAudio()
    声道数 = min(环回设备['maxInputChannels'], 2)
    块大小 = int(采样率 * 采集块秒)

    流 = p.open(format=pyaudio.paInt16,
                channels=声道数,
                rate=采样率,
                input=True,
                input_device_index=环回设备['index'],
                frames_per_buffer=块大小)

    缓冲区长度 = int(缓冲区时长秒 * 采样率)
    缓冲区 = collections.deque(maxlen=缓冲区长度)
    上次触发时间 = 0.0

    # ---------- 构建滤波器 + 滤波模板 ----------
    滤波器列表 = []
    滤波后模板列表 = []
    for 模板, (能量比, 最低频率) in zip(模板列表, 模板滤波参数):
        低切, 高切 = 计算主频带(模板.模板, 采样率, 能量比=能量比, 最低频率=最低频率)
        sos = 设计滤波器(低切, 高切, 采样率)
        滤波器列表.append(sos)

        # 对模板应用相同滤波，并重新归一化
        模板滤波后 = 应用滤波器(模板.模板, sos)
        模板滤波后 = 模板滤波后 - np.mean(模板滤波后)
        模板滤波后 = 模板滤波后 / (np.std(模板滤波后) + 1e-8)
        滤波后模板列表.append(模板滤波后)

        模式 = "高通" if 能量比 >= 1.0 else "带通"
        print(f"[特征] {模板.名称} ({模式}) 截止: {低切:.0f}-{高切:.0f} Hz")

    print(f"[系统] 启动 (阈值:{阈值}, 冷却:{冷却秒}s, 块:{块大小}, 缓冲:{缓冲区时长秒:.2f}s)")

    try:
        print("[预采集] 等待缓冲区填充...")
        while 控制事件.is_set() and len(缓冲区) < 检测窗口:
            数据 = 流.read(块大小, exception_on_overflow=False)
            int16 = np.frombuffer(数据, dtype=np.int16)
            if 声道数 == 2:
                int16 = int16.reshape(-1, 2).mean(axis=1)
            float32 = int16.astype(np.float32) / 32768.0
            缓冲区.extend(float32)

        if not 控制事件.is_set():
            print("[预采集] 收到停止信号")
            return

        print(f"[预采集] 完成 ({len(缓冲区)} 采样点)")

        while 控制事件.is_set():
            if not 控制事件.is_set():
                break
            数据 = 流.read(块大小, exception_on_overflow=False)
            int16 = np.frombuffer(数据, dtype=np.int16)
            if 声道数 == 2:
                int16 = int16.reshape(-1, 2).mean(axis=1)
            float32 = int16.astype(np.float32) / 32768.0

            缓冲区.extend(float32)

            当前时间 = time.time()
            if 当前时间 - 上次触发时间 < 冷却秒:
                continue

            快照 = np.array(缓冲区)[-检测窗口:]
            # 现在 = time.time()
            for i, 模板 in enumerate(模板列表):
                滤波后快照 = 应用滤波器(快照, 滤波器列表[i])
                相似度 = 极速匹配(滤波后快照, 滤波后模板列表[i])
                if 相似度 >= 阈值:
                    print(f"✅检测到 {模板.名称} 相似度:{相似度:.3f}")
                    if 模板.名称 == "闪避":
                        模拟按键长按(句柄, 0xA0, 0.01 + random_non_negative(0.05, 0.01))
                    elif 模板.名称 == "反击":
                        模拟鼠标左键长按(句柄, 640, 360, 0.05 + random_non_negative(0.05, 0.01))
                    上次触发时间 = 当前时间
            # print(time.time()-现在)


    except KeyboardInterrupt:
        print("\n[信息] 收到 Ctrl+C")
    finally:
        流.stop_stream()
        流.close()
        p.terminate()
        print("[系统] 资源已释放")



# ==================== 入口 ====================
def 根据音频闪避反击任务(current_dir,句柄,线程控制事件,线程停止事件,阈值 = 0.2, 共享冷却秒 = 0.3,采集块秒 = 0.04,窗口余量秒 = 0.05,
                         自定义缓冲秒 = 0.2,最低频率hz = 2300):
    p_temp = pyaudio.PyAudio()
    环回设备 = None
    for i in range(p_temp.get_device_count()):
        dev = p_temp.get_device_info_by_index(i)
        if "Loopback" in dev['name'] and dev['maxInputChannels'] > 0:
            环回设备 = dev
            break
    if not 环回设备:
        msgbox.showerror("设备错误", "未找到环回设备！")
        线程停止事件.clear()
        exit()
    采样率 = int(环回设备['defaultSampleRate'])
    p_temp.terminate()
    print(f"[信息] 设备采样率: {采样率} Hz")
    需闪避攻击路径 = current_dir / "异环图片" / "怪物反击闪避" / "闪避_缩混.wav"
    需反击音频路径 = current_dir / "异环图片" / "怪物反击闪避" / "反击_缩混.wav"
    需反击2音频路径 = current_dir / "异环图片" / "怪物反击闪避" / "反击2_缩混.wav"
    # 加载模板
    try:
        模板列表 = [
            音频模板(需闪避攻击路径, "闪避", 采样率, 截取范围=(0, 0.08)),
            音频模板(需反击音频路径, "反击", 采样率, 截取范围=(0, 0.08)),
            音频模板(需反击2音频路径, "反击", 采样率, 截取范围=(0, 0.08)),
        ]
    except Exception as e:
        msgbox.showerror("错误", f"模板列表初始化失败，{e}")
        线程停止事件.clear()
        exit()

    # 滤波配置：每个模板的 (能量比, 最低频率)


    模板滤波配置 = [
        (0.95, 最低频率hz),
        (1.0, 最低频率hz),
        (1.0, 最低频率hz),

    ]
    运行主循环(环回设备, 采样率, 模板列表, 阈值, 共享冷却秒, 线程控制事件,
            采集块秒, 窗口余量秒, 自定义缓冲秒, 模板滤波配置, 句柄)
    线程停止事件.clear()
if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        当前目录 = Path(sys.executable).parent.absolute()
    else:
        当前目录 = APP_ROOT
    import win32gui
    import ctypes
    def 函数精确查找窗口句柄(目标窗口类名, 默认目标窗口标题):

        """精确查找目标窗口句柄"""
        # 先尝试根据标题和类名查找窗口
        游戏句柄 = win32gui.FindWindow(目标窗口类名, 默认目标窗口标题)
        if 游戏句柄:

            print(f"找到目标窗口：句柄={游戏句柄}")
            return 游戏句柄
        else:
            print(f"未找到目标窗口")
        return None, None  # 没有找到窗口时返回 None
    p_temp = pyaudio.PyAudio()
    环回设备 = None
    for i in range(p_temp.get_device_count()):
        dev = p_temp.get_device_info_by_index(i)
        if "Loopback" in dev['name'] and dev['maxInputChannels'] > 0:
            环回设备 = dev
            break
    if not 环回设备:
        msgbox.showerror("设备错误", "未找到环回设备！")
        exit()
    采样率 = int(环回设备['defaultSampleRate'])
    p_temp.terminate()
    print(f"[信息] 设备采样率: {采样率} Hz")
    需闪避攻击路径 = 当前目录 / "异环图片" / "怪物反击闪避" / "闪避_缩混.wav"
    需反击音频路径 = 当前目录 / "异环图片" / "怪物反击闪避" / "反击_缩混.wav"
    需反击2音频路径 = 当前目录 / "异环图片" / "怪物反击闪避" / "反击2_缩混.wav"
    # 加载模板
    try:
        模板列表 = [
            音频模板(需闪避攻击路径, "闪避", 采样率, 截取范围=(0, 0.08)),
            音频模板(需反击音频路径, "反击", 采样率, 截取范围=(0, 0.08)),
            音频模板(需反击2音频路径, "反击", 采样率, 截取范围=(0, 0.08)),
        ]
    except ValueError:
        exit()

    # 配置参数
    阈值 = 0.2
    共享冷却秒 = 0.3
    采集块秒 = 0.04
    窗口余量秒 = 0.05
    自定义缓冲秒 = 0.2

    # 滤波配置：每个模板的 (能量比, 最低频率)

    最低频率hz=2300
    模板滤波配置 = [
        (0.95, 最低频率hz),
        (1.0, 最低频率hz),
        (1.0, 最低频率hz),

    ]

    # ========== 线程启动演示 ==========
    print("\n===== 线程启动演示 =====")
    异环句柄 = 函数精确查找窗口句柄("UnrealWindow", "异环  ")  # "异环  "/"NTE  "
    线程控制事件 = threading.Event()
    线程控制事件.set()

    线程 = threading.Thread(
        target=运行主循环,
        args=(环回设备, 采样率, 模板列表, 阈值, 共享冷却秒, 线程控制事件,
              采集块秒, 窗口余量秒, 自定义缓冲秒, 模板滤波配置,异环句柄),
        daemon=True
    )
    线程.start()

    input("按回车停止线程...\n")
    线程控制事件.clear()
    线程.join()

    # ========== 进程启动演示 ==========
    print("\n===== 进程启动演示 =====")
    进程控制事件 = multiprocessing.Event()
    进程控制事件.set()

    进程 = multiprocessing.Process(
        target=运行主循环,
        args=(环回设备, 采样率, 模板列表, 阈值, 共享冷却秒, 进程控制事件,
              采集块秒, 窗口余量秒, 自定义缓冲秒, 模板滤波配置)
    )
    进程.start()

    input("按回车停止进程...\n")
    进程控制事件.clear()
    进程.join()
