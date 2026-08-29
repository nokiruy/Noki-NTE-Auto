import pyaudiowpatch as pyaudio
import soundfile as sf
from scipy.signal import correlate, butter, sosfiltfilt,resample_poly
import time
import numpy as np
from pathlib import Path

import sys
import collections
import threading
import tkinter.messagebox as msgbox

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
        y_full, sr = sf.read(路径, dtype='float32')
        if y_full.ndim > 1:
            y_full = y_full.mean(axis=1)  # 立体声转单声道
        if sr != 采样率:
            print(f"[重采样] {路径} : {sr}Hz → {采样率}Hz")
            y_full = resample_poly(y_full, 采样率, sr)
            sr = 采样率
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
import json
from 根据txt执行脚本 import  预编译脚本动作
def 运行主循环(current_dir,环回设备, 采样率, 模板列表, 阈值, 冷却秒, 线程事件,
                采集块秒=0.04, 窗口余量秒=0.05, 缓冲区时长秒=None,
                模板滤波参数=None,句柄=None, 窗口矩形=None, 仅闪避=False,
                自定义闪避动作=None, 反击时闪避=False, 检测回调=None):
    闪避动作txt文件 = None
    弹刀动作txt文件 = None
    # 自定义且仅闪避时不读取全局“自动闪避弹刀”的动作配置。
    if 自定义闪避动作 is None or not 仅闪避:
        with open(current_dir.parent / "外置配置文件夹" / "任务选择设置.json", 'r', encoding='utf-8') as file:
            任务选择设置 = json.load(file)
        if 自定义闪避动作 is None:
            闪避动作txt文件名 = 任务选择设置["闪避动作自定义变量"]
            闪避动作txt文件 = (
                current_dir.parent / "外置配置文件夹" / "闪避弹刀自定义动作" / f"{闪避动作txt文件名}.txt"
            )
        if not 仅闪避:
            弹刀动作txt文件名 = 任务选择设置["弹刀动作自定义变量"]
            弹刀动作txt文件 = (
                current_dir.parent / "外置配置文件夹" / "闪避弹刀自定义动作" / f"{弹刀动作txt文件名}.txt"
            )

    闪避执行动作 = 自定义闪避动作 or 预编译脚本动作(闪避动作txt文件, 窗口矩形)
    弹刀执行动作 = None if 仅闪避 else 预编译脚本动作(弹刀动作txt文件, 窗口矩形)
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
    try:
        流 = p.open(format=pyaudio.paInt16, channels=声道数, rate=采样率, input=True, input_device_index=环回设备['index'], frames_per_buffer=块大小)
    except Exception as e:
        print(f"音频流获取错误：{e}")
        msgbox.showerror("错误", f"音频流获取错误：{e}")
        return
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
        while 线程事件.is_set() and len(缓冲区) < 检测窗口:
            数据 = 流.read(块大小, exception_on_overflow=False)
            int16 = np.frombuffer(数据, dtype=np.int16)
            if 声道数 == 2:
                int16 = int16.reshape(-1, 2).mean(axis=1)
            float32 = int16.astype(np.float32) / 32768.0
            缓冲区.extend(float32)

        if not 线程事件.is_set():
            print("[预采集] 收到停止信号")
            return

        print(f"[预采集] 完成 ({len(缓冲区)} 采样点)")

        while 线程事件.is_set():
            if not 线程事件.is_set():
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
                    if 检测回调 is not None:
                        检测回调(模板.名称, 相似度)
                    if 模板.名称 == "闪避":
                        闪避执行动作(句柄, 窗口矩形, 线程事件)
                    elif 模板.名称 == "反击":
                        if 反击时闪避:
                            闪避执行动作(句柄, 窗口矩形, 线程事件)
                        elif not 仅闪避:
                            弹刀执行动作(句柄, 窗口矩形, 线程事件)
                    上次触发时间 = 当前时间
            # print(time.time()-现在)
    except Exception as e:
        print(f"自动闪避弹刀任务错误：{e}")
        msgbox.showerror("错误",f"自动闪避弹刀任务错误：{e}")

    except KeyboardInterrupt:
        print("\n[信息] 收到 Ctrl+C")
    finally:
        流.stop_stream()
        流.close()
        p.terminate()
        print("[系统] 资源已释放")



# ==================== 入口 ====================
def 获取默认环回设备(p):
    """
    根据系统默认输出设备，寻找对应的 WASAPI 环回设备。
    返回设备字典，找不到则返回 None。
    """
    try:
        default_out = p.get_default_output_device_info()
        default_name = default_out['name'].strip()
    except Exception:
        # 无法获取默认输出设备时，回退到原逻辑
        default_name = None

    loopback_candidates = []
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        # 只考虑 WASAPI 的环回输入设备
        if dev['maxInputChannels'] > 0 and 'Loopback' in dev['name']:
            loopback_candidates.append(dev)

    if default_name:
        # 尝试精确匹配：环回设备名称通常为 “默认输出设备名称 (Loopback)” 或类似
        for dev in loopback_candidates:
            # 去除后缀可能的差异，例如 “扬声器 (Loopback)” -> “扬声器”
            dev_name_clean = dev['name'].replace('(Loopback)', '').replace('Loopback', '').strip()
            if dev_name_clean == default_name:
                return dev
        # 宽松匹配：默认输出名称包含在环回设备名中
        for dev in loopback_candidates:
            if default_name in dev['name']:
                return dev

    # 回退：返回找到的第一个环回设备（原逻辑）
    return loopback_candidates[0] if loopback_candidates else None
def 根据音频闪避反击任务(current_dir,句柄, 窗口矩形,线程控制事件,线程停止事件,阈值 = 0.2, 共享冷却秒 = 0.3,采集块秒 = 0.04,窗口余量秒 = 0.05,
                         自定义缓冲秒 = 0.2,最低频率hz = 2300,仅闪避=False,
                         自定义闪避动作=None,反击时闪避=False,检测回调=None):

    p_temp = pyaudio.PyAudio()
    环回设备 = 获取默认环回设备(p_temp)
    if not 环回设备:
        print("未找到环回设备！")
        msgbox.showerror("设备错误", "未找到任何可用的 WASAPI 环回设备，请检查声卡设置或安装虚拟音频电缆。")
        线程停止事件.clear()
        线程控制事件.clear()
        p_temp.terminate()
        return
    # 确保设备是输入设备
    if 环回设备['maxInputChannels'] <= 0:
        print(f"设备 {环回设备['name']} 不是输入设备，无法使用。")
        msgbox.showerror("设备错误", "所选环回设备没有输入通道，无法录制音频。")
        线程停止事件.clear()
        线程控制事件.clear()
        p_temp.terminate()
        return
    采样率 = int(环回设备['defaultSampleRate'])
    p_temp.terminate()
    print(f"[信息] 设备采样率: {采样率} Hz, 设备: {环回设备['name']} (索引 {环回设备['index']})")
    需闪避攻击路径 = current_dir / "异环图片" / "怪物反击闪避" / "闪避_缩混.wav"
    需反击音频路径 = current_dir / "异环图片" / "怪物反击闪避" / "反击_缩混.wav"
    需反击2音频路径 = current_dir / "异环图片" / "怪物反击闪避" / "反击2_缩混.wav"
    # 加载模板
    try:
        模板列表 = [音频模板(需闪避攻击路径, "闪避", 采样率, 截取范围=(0, 0.08))]
        if not 仅闪避 or 反击时闪避:
            模板列表.extend([
                音频模板(需反击音频路径, "反击", 采样率, 截取范围=(0, 0.08)),
                音频模板(需反击2音频路径, "反击", 采样率, 截取范围=(0, 0.08)),
            ])
    except Exception as e:
        print(f"模板列表初始化失败，{e}")
        msgbox.showerror("错误", f"模板列表初始化失败，{e}")
        线程停止事件.clear()
        线程控制事件.clear()
        return

    # 滤波配置：每个模板的 (能量比, 最低频率)


    模板滤波配置 = [(0.95, 最低频率hz)]
    if not 仅闪避 or 反击时闪避:
        模板滤波配置.extend([(1.0, 最低频率hz), (1.0, 最低频率hz)])
    运行主循环(current_dir,环回设备, 采样率, 模板列表, 阈值, 共享冷却秒, 线程控制事件,
            采集块秒, 窗口余量秒, 自定义缓冲秒, 模板滤波配置, 句柄,窗口矩形,
            仅闪避, 自定义闪避动作, 反击时闪避, 检测回调)
    线程停止事件.clear()


