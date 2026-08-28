import os
import threading
import mido
import json
import time
from pathlib import Path
from project_paths import APP_ROOT
from 异环游戏特殊键盘 import 模拟按键弹起, 模拟按键按下

# ==================== 音符映射表（仅36~71，三个八度）====================
def 音符到按键映射(垂直反转映射=False, 水平反转映射=False):
    # 水平反转映射（每八度左右镜像）
    水平反转映射表 = {
        36: ("m", None), 37: ("m", "shift_left"),
        38: ("n", None), 39: ("b", "shift_left"),
        40: ("b", None), 41: ("v", "shift_left"),
        42: ("v", None), 43: ("c", None),
        44: ("c", "ctrl_left"), 45: ("x", None),
        46: ("z", "shift_left"), 47: ("z", None),

        48: ("j", None), 49: ("j", "ctrl_left"),
        50: ("h", None), 51: ("g", "shift_left"),
        52: ("g", None), 53: ("f", "shift_left"),
        54: ("f", None), 55: ("d", None),
        56: ("d", "ctrl_left"), 57: ("s", None),
        58: ("a", "shift_left"), 59: ("a", None),

        60: ("u", None), 61: ("u", "ctrl_left"),
        62: ("y", None), 63: ("t", "shift_left"),
        64: ("t", None), 65: ("r", "shift_left"),
        66: ("r", None), 67: ("e", None),
        68: ("e", "ctrl_left"), 69: ("w", None),
        70: ("q", "shift_left"), 71: ("q", None),
    }

    # 垂直反转映射（低音区与高音区互换，中音区不变）
    垂直反转映射表 = {
        36: ("q", None), 37: ("q", "shift_left"),
        38: ("w", None), 39: ("e", "ctrl_left"),
        40: ("e", None), 41: ("r", None),
        42: ("r", "shift_left"), 43: ("t", None),
        44: ("t", "shift_left"), 45: ("y", None),
        46: ("u", "ctrl_left"), 47: ("u", None),

        48: ("a", None), 49: ("a", "shift_left"),
        50: ("s", None), 51: ("d", "ctrl_left"),
        52: ("d", None), 53: ("f", None),
        54: ("f", "shift_left"), 55: ("g", None),
        56: ("g", "shift_left"), 57: ("h", None),
        58: ("j", "ctrl_left"), 59: ("j", None),

        60: ("z", None), 61: ("z", "shift_left"),
        62: ("x", None), 63: ("c", "ctrl_left"),
        64: ("c", None), 65: ("v", None),
        66: ("v", "shift_left"), 67: ("b", None),
        68: ("b", "shift_left"), 69: ("n", None),
        70: ("m", "ctrl_left"), 71: ("m", None),
    }

    # 全反转映射（水平 + 垂直，相当于上下左右都颠倒）
    全反转映射表 = {
        36: ("u", None), 37: ("u", "ctrl_left"),
        38: ("y", None), 39: ("t", "shift_left"),
        40: ("t", None), 41: ("r", "shift_left"),
        42: ("r", None), 43: ("e", None),
        44: ("e", "ctrl_left"), 45: ("w", None),
        46: ("q", "shift_left"), 47: ("q", None),

        48: ("j", None), 49: ("j", "ctrl_left"),
        50: ("h", None), 51: ("g", "shift_left"),
        52: ("g", None), 53: ("f", "shift_left"),
        54: ("f", None), 55: ("d", None),
        56: ("d", "ctrl_left"), 57: ("s", None),
        58: ("a", "shift_left"), 59: ("a", None),

        60: ("m", None), 61: ("m", "ctrl_left"),
        62: ("n", None), 63: ("b", "shift_left"),
        64: ("b", None), 65: ("v", "shift_left"),
        66: ("v", None), 67: ("c", None),
        68: ("c", "ctrl_left"), 69: ("x", None),
        70: ("z", "shift_left"), 71: ("z", None),
    }
    if 垂直反转映射 and 水平反转映射:
        return 全反转映射表
    elif 垂直反转映射:
        return 垂直反转映射表
    elif 水平反转映射:
        return 水平反转映射表

    # 原始映射（低、中、高三个八度）
    低音区 = {
        36: ("z", None),
        37: ("z", "shift_left"),
        38: ("x", None),
        39: ("c", "ctrl_left"),
        40: ("c", None),
        41: ("v", None),
        42: ("v", "shift_left"),
        43: ("b", None),
        44: ("b", "shift_left"),
        45: ("n", None),
        46: ("m", "ctrl_left"),
        47: ("m", None),
    }

    中音区 = {
        48: ("a", None),
        49: ("a", "shift_left"),
        50: ("s", None),
        51: ("d", "ctrl_left"),
        52: ("d", None),
        53: ("f", None),
        54: ("f", "shift_left"),
        55: ("g", None),
        56: ("g", "shift_left"),
        57: ("h", None),
        58: ("j", "ctrl_left"),
        59: ("j", None),
    }

    高音区 = {
        60: ("q", None),
        61: ("q", "shift_left"),
        62: ("w", None),
        63: ("e", "ctrl_left"),
        64: ("e", None),
        65: ("r", None),
        66: ("r", "shift_left"),
        67: ("t", None),
        68: ("t", "shift_left"),
        69: ("y", None),
        70: ("u", "ctrl_left"),
        71: ("u", None),
    }

    # 合并为原始映射
    原始映射 = {}
    原始映射.update(低音区)
    原始映射.update(中音区)
    原始映射.update(高音区)


    return 原始映射




def 分析MIDI文件(midi文件路径):
    """
    分析MIDI文件，提取音符事件（分音轨）
    使用直接简单的方法：分别处理每个音轨，独立计算时间
    """
    if not os.path.exists(midi文件路径):
        print(f"文件不存在: {midi文件路径}")
        # 可以改用文件选择对话框或让用户重新输入
    else:
        print(f"文件存在: {midi文件路径}")
    try:
        mid = mido.MidiFile(midi文件路径, clip=True)
        音轨事件字典 = {}

        print(f"MIDI文件包含 {len(mid.tracks)} 个音轨")

        # 创建一个字典来记录速度变化事件
        # 我们将收集所有音轨的速度变化事件，并假设它们是全局的
        全局速度事件 = []

        for 音轨号, 音轨 in enumerate(mid.tracks):
            当前tick = 0
            for msg in 音轨:
                当前tick += msg.time
                if msg.type == 'set_tempo':
                    全局速度事件.append((当前tick, msg.tempo))

        if not 全局速度事件:
            全局速度事件.append((0, 500000))

        全局速度事件.sort(key=lambda x: x[0])

        def tick转秒(tick值, ticks_per_beat, 速度事件列表):
            累计时间 = 0.0
            上一个tick = 0
            当前速度 = 速度事件列表[0][1]

            for i in range(len(速度事件列表)):
                tick, tempo = 速度事件列表[i]
                if tick > tick值:
                    break
                上一个tick = tick
                当前速度 = tempo

            tick差值 = tick值 - 上一个tick
            tick差值秒 = mido.tick2second(tick差值, ticks_per_beat, 当前速度)

            for i in range(len(速度事件列表)):
                tick, tempo = 速度事件列表[i]
                if tick >= 上一个tick:
                    break
                if i > 0:
                    上一个tick2, 上一个tempo = 速度事件列表[i - 1]
                    tick差值2 = tick - 上一个tick2
                    tick差值秒2 = mido.tick2second(tick差值2, ticks_per_beat, 上一个tempo)
                    累计时间 += tick差值秒2

            return 累计时间 + tick差值秒

        for 音轨号, 音轨 in enumerate(mid.tracks):
            事件列表 = []
            当前tick = 0
            音轨速度事件 = 全局速度事件.copy()

            for msg in 音轨:
                当前tick += msg.time

                if msg.type == 'note_on' and msg.velocity > 0:
                    时间秒 = tick转秒(当前tick, mid.ticks_per_beat, 音轨速度事件)
                    事件 = {
                        '时间': 时间秒,
                        '类型': '开始',
                        '音符': msg.note,
                        '力度': msg.velocity
                    }
                    事件列表.append(事件)

                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    时间秒 = tick转秒(当前tick, mid.ticks_per_beat, 音轨速度事件)
                    事件 = {
                        '时间': 时间秒,
                        '类型': '结束',
                        '音符': msg.note
                    }
                    事件列表.append(事件)

            if 事件列表:
                事件列表.sort(key=lambda x: x['时间'])
                音轨事件字典[音轨号] = 事件列表
                print(f"音轨 {音轨号}: 提取了 {len(事件列表)} 个音符事件")
            else:
                print(f"音轨 {音轨号}: 没有音符事件")

        return 音轨事件字典, mid.ticks_per_beat

    except Exception as e:
        print(f"分析MIDI文件时出错: {e}")
        import traceback
        traceback.print_exc()
        return {}, None



def 音符归一化(音符):
    while 音符 < 36:
        音符 += 12
    while 音符 > 71:
        音符 -= 12
    return 音符


def 整体加减key移调映射音名关系保留(音符列表, 目标最低=36, 目标最高=71):
    """
    根据优化策略计算原始音符到目标音符的映射。
    返回字典 {原始音符: 目标音符}
    """
    if not 音符列表:
        return {}
    最低原 = min(音符列表)
    最高原 = max(音符列表)
    原宽度 = 最高原 - 最低原
    目标宽度 = 目标最高 - 目标最低  # = 35

    # ------------------------------------------------------------
    # 情况1：原曲音域宽度 <= 目标宽度（可以尝试完美八度平移）
    # ------------------------------------------------------------
    if 原宽度 <= 目标宽度:
        # 尝试八度平移 (k 倍数)
        best_k = None
        for k in range(-3, 4):  # 尝试上下三个八度
            平移后最低 = 最低原 + 12 * k
            平移后最高 = 最高原 + 12 * k
            if 平移后最低 >= 目标最低 and 平移后最高 <= 目标最高:
                best_k = k
                break  # 找到即用，也可改为挑选最居中的
        if best_k is not None:
            # 完美八度平移
            return {原: 原 + 12 * best_k for 原 in 音符列表}
        # 没有完美八度平移，使用中心对齐移调 + 八度折叠
        # 计算中心对齐偏移
        原中心 = (最低原 + 最高原) / 2
        目标中心 = (目标最低 + 目标最高) / 2
        base_offset = int(round(目标中心 - 原中心))
        # 应用偏移后，再用八度折叠处理超出边界的音符
        def 八度折叠(音符):
            while 音符 < 目标最低:
                音符 += 12
            while 音符 > 目标最高:
                音符 -= 12
            return 音符
        return {原: 八度折叠(原 + base_offset) for 原 in 音符列表}

    # ------------------------------------------------------------
    # 情况2：原曲音域宽度 > 目标宽度
    # ------------------------------------------------------------
    # 1. 先做中心对齐移调
    原中心 = (最低原 + 最高原) / 2
    目标中心 = (目标最低 + 目标最高) / 2
    base_offset = int(round(目标中心 - 原中心))
    临时音符列表 = [原 + base_offset for 原 in 音符列表]

    # 2. 找出临时音符中的最低和最高
    临时最低 = min(临时音符列表)
    临时最高 = max(临时音符列表)

    # 3. 计算低音组需要统一加的12的倍数
    if 临时最低 < 目标最低:
        # 需要加多少个12才能让临时最低进入区间
        k_low = (目标最低 - 临时最低 + 11) // 12  # 向上取整
    else:
        k_low = 0
    # 计算高音组需要统一减的12的倍数
    if 临时最高 > 目标最高:
        k_high = (临时最高 - 目标最高 + 11) // 12  # 向上取整
    else:
        k_high = 0

    # 应用统一的八度调整
    映射 = {}
    for 原, 临 in zip(音符列表, 临时音符列表):
        最终 = 临
        if 临 < 目标最低:
            最终 = 临 + 12 * k_low
        elif 临 > 目标最高:
            最终 = 临 - 12 * k_high
        # 二次保险：如果仍有超出（极少情况），再单独修正一次
        while 最终 < 目标最低:
            最终 += 12
        while 最终 > 目标最高:
            最终 -= 12
        映射[原] = 最终
    return 映射
def 整体加减key移调映射直接裁剪(音符列表, 目标最低=36, 目标最高=71):
    """
    根据优化策略计算原始音符到目标音符的映射。
    返回字典 {原始音符: 目标音符}
    """
    if not 音符列表:
        return {}
    最低原 = min(音符列表)
    最高原 = max(音符列表)
    原宽度 = 最高原 - 最低原
    目标宽度 = 目标最高 - 目标最低  # = 35

    # ------------------------------------------------------------
    # 情况1：原曲音域宽度 <= 目标宽度（可以尝试完美八度平移）
    # ------------------------------------------------------------
    if 原宽度 <= 目标宽度:
        # 尝试八度平移 (k 倍数)
        best_k = None
        for k in range(-3, 4):  # 尝试上下三个八度
            平移后最低 = 最低原 + 12 * k
            平移后最高 = 最高原 + 12 * k
            if 平移后最低 >= 目标最低 and 平移后最高 <= 目标最高:
                best_k = k
                break  # 找到即用，也可改为挑选最居中的
        if best_k is not None:
            # 完美八度平移
            return {原: 原 + 12 * best_k for 原 in 音符列表}
        # 没有完美八度平移，使用中心对齐移调 + 八度折叠
        # 计算中心对齐偏移
        原中心 = (最低原 + 最高原) / 2
        目标中心 = (目标最低 + 目标最高) / 2
        base_offset = int(round(目标中心 - 原中心))
        # 应用偏移后，再用八度折叠处理超出边界的音符
        def 八度折叠(音符):
            while 音符 < 目标最低:
                音符 += 12
            while 音符 > 目标最高:
                音符 -= 12
            return 音符
        return {原: 八度折叠(原 + base_offset) for 原 in 音符列表}

    # ------------------------------------------------------------
    # 情况2：原曲音域宽度 > 目标宽度
    # ------------------------------------------------------------
    # 1. 先做中心对齐移调
    原中心 = (最低原 + 最高原) / 2
    目标中心 = (目标最低 + 目标最高) / 2
    base_offset = int(round(目标中心 - 原中心))
    临时音符列表 = [原 + base_offset for 原 in 音符列表]


    映射 = {}
    for 原, 临 in zip(音符列表, 临时音符列表):
        最终 = 临
        while 最终 < 目标最低:
            最终 += 12
        while 最终 > 目标最高:
            最终 -= 12
        映射[原] = 最终
    return 映射
def 整体加减八度移调映射音名关系保留(音符列表, 目标最低=36, 目标最高=71):
    """
    只允许整体做八度平移（±12的倍数），然后：
    - 低音组统一上移若干八度，保留组内音名关系
    - 高音组统一下移若干八度，保留组内音名关系
    返回字典 {原始音符: 目标音符}
    """
    if not 音符列表:
        return {}
    最低原 = min(音符列表)
    最高原 = max(音符列表)
    原中心 = (最低原 + 最高原) / 2
    目标中心 = (目标最低 + 目标最高) / 2

    # 1. 先尝试完美八度平移（整体放入目标区间）
    for k in range(-3, 4):  # 上下三个八度
        平移后最低 = 最低原 + 12 * k
        平移后最高 = 最高原 + 12 * k
        if 平移后最低 >= 目标最低 and 平移后最高 <= 目标最高:
            return {原: 原 + 12 * k for 原 in 音符列表}

    # 2. 没有完美八度平移 → 选择最接近目标中心的八度偏移
    k_shift = round((目标中心 - 原中心) / 12)
    k_shift = int(k_shift)  # 确保整数
    临时音符列表 = [原 + 12 * k_shift for 原 in 音符列表]

    # 3. 找出临时音符的最低和最高，计算统一的八度调整倍数
    临时最低 = min(临时音符列表)
    临时最高 = max(临时音符列表)

    if 临时最低 < 目标最低:
        k_low = (目标最低 - 临时最低 + 11) // 12  # 向上取整
    else:
        k_low = 0
    if 临时最高 > 目标最高:
        k_high = (临时最高 - 目标最高 + 11) // 12  # 向上取整
    else:
        k_high = 0

    # 4. 应用统一的八度调整，并二次保险
    映射 = {}
    for 原, 临 in zip(音符列表, 临时音符列表):
        最终 = 临
        if 临 < 目标最低:
            最终 = 临 + 12 * k_low
        elif 临 > 目标最高:
            最终 = 临 - 12 * k_high
        # 二次保险
        while 最终 < 目标最低:
            最终 += 12
        while 最终 > 目标最高:
            最终 -= 12
        映射[原] = 最终
    return 映射
def 整体加减八度移调映射直接裁剪(音符列表, 目标最低=36, 目标最高=71):
    """
    只允许整体做八度平移（±12的倍数），然后：
    - 越界的低音逐个八度上翻到低音区 [目标最低, 目标最低+11]
    - 越界的高音逐个八度下翻到高音区 [目标最高-11, 目标最高]
    返回字典 {原始音符: 目标音符}
    """
    if not 音符列表:
        return {}
    最低原 = min(音符列表)
    最高原 = max(音符列表)
    原中心 = (最低原 + 最高原) / 2
    目标中心 = (目标最低 + 目标最高) / 2

    # 1. 先尝试完美八度平移
    for k in range(-3, 4):
        平移后最低 = 最低原 + 12 * k
        平移后最高 = 最高原 + 12 * k
        if 平移后最低 >= 目标最低 and 平移后最高 <= 目标最高:
            return {原: 原 + 12 * k for 原 in 音符列表}

    # 2. 没有完美八度平移 → 最接近目标中心的八度偏移
    k_shift = round((目标中心 - 原中心) / 12)
    k_shift = int(k_shift)
    临时音符列表 = [原 + 12 * k_shift for 原 in 音符列表]

    # 3. 直接裁剪：低音进低音八度，高音进高音八度
    映射 = {}
    for 原, 临 in zip(音符列表, 临时音符列表):
        最终 = 临
        while 最终 < 目标最低:
            最终 += 12
        while 最终 > 目标最高:
            最终 -= 12
        映射[原] = 最终
    return 映射
def 以能被36个半音覆盖最多的音为中心移调整体加减key移调映射音名关系保留(音符列表, 目标最低=36, 目标最高=71):
    """
    在整体加减key移调映射音名关系保留的基础上，
    用'能被目标宽度（35半音）覆盖最多音符'的区间中心替代简单的最低最高中心。
    """
    if not 音符列表:
        return {}
    最低原 = min(音符列表)
    最高原 = max(音符列表)
    原宽度 = 最高原 - 最低原
    目标宽度 = 目标最高 - 目标最低

    # --- 计算最大覆盖窗口的中心 ---
    from collections import Counter
    cnt = Counter(音符列表)
    best_center = (最低原 + 最高原) / 2   # 默认
    max_count = -1
    for low in sorted(cnt.keys()):
        high = low + 目标宽度
        count = sum(cnt[n] for n in cnt if low <= n <= high)
        if count > max_count:
            max_count = count
            best_center = (low + high) / 2
        elif count == max_count:
            # 平局时选离原始极值中心更近的，保持对称
            default_center = (最低原 + 最高原) / 2
            if abs((low + high)/2 - default_center) < abs(best_center - default_center):
                best_center = (low + high) / 2
    原中心 = best_center
    目标中心 = (目标最低 + 目标最高) / 2

    # 情况1：原宽度 <= 目标宽度
    if 原宽度 <= 目标宽度:
        for k in range(-3, 4):
            平移后最低 = 最低原 + 12 * k
            平移后最高 = 最高原 + 12 * k
            if 平移后最低 >= 目标最低 and 平移后最高 <= 目标最高:
                return {原: 原 + 12 * k for 原 in 音符列表}
        # 没有完美八度平移，使用中心对齐移调 + 八度折叠
        base_offset = int(round(目标中心 - 原中心))
        def 八度折叠(音符):
            while 音符 < 目标最低:
                音符 += 12
            while 音符 > 目标最高:
                音符 -= 12
            return 音符
        return {原: 八度折叠(原 + base_offset) for 原 in 音符列表}

    # 情况2：原宽度 > 目标宽度
    base_offset = int(round(目标中心 - 原中心))
    临时音符列表 = [原 + base_offset for 原 in 音符列表]
    临时最低 = min(临时音符列表)
    临时最高 = max(临时音符列表)

    if 临时最低 < 目标最低:
        k_low = (目标最低 - 临时最低 + 11) // 12
    else:
        k_low = 0
    if 临时最高 > 目标最高:
        k_high = (临时最高 - 目标最高 + 11) // 12
    else:
        k_high = 0

    映射 = {}
    for 原, 临 in zip(音符列表, 临时音符列表):
        最终 = 临
        if 临 < 目标最低:
            最终 = 临 + 12 * k_low
        elif 临 > 目标最高:
            最终 = 临 - 12 * k_high
        while 最终 < 目标最低:
            最终 += 12
        while 最终 > 目标最高:
            最终 -= 12
        映射[原] = 最终
    return 映射
def 以能被36个半音覆盖最多的音为中心移调整体加减key移调映射直接裁剪(音符列表, 目标最低=36, 目标最高=71):
    """
    在整体加减key移调映射直接裁剪的基础上，
    用最大覆盖窗口中心替代简单最低最高中心。
    """
    if not 音符列表:
        return {}
    最低原 = min(音符列表)
    最高原 = max(音符列表)
    原宽度 = 最高原 - 最低原
    目标宽度 = 目标最高 - 目标最低

    # 最大覆盖窗口中心
    from collections import Counter
    cnt = Counter(音符列表)
    best_center = (最低原 + 最高原) / 2
    max_count = -1
    for low in sorted(cnt.keys()):
        high = low + 目标宽度
        count = sum(cnt[n] for n in cnt if low <= n <= high)
        if count > max_count:
            max_count = count
            best_center = (low + high) / 2
        elif count == max_count:
            default_center = (最低原 + 最高原) / 2
            if abs((low + high)/2 - default_center) < abs(best_center - default_center):
                best_center = (low + high) / 2
    原中心 = best_center
    目标中心 = (目标最低 + 目标最高) / 2

    if 原宽度 <= 目标宽度:
        for k in range(-3, 4):
            平移后最低 = 最低原 + 12 * k
            平移后最高 = 最高原 + 12 * k
            if 平移后最低 >= 目标最低 and 平移后最高 <= 目标最高:
                return {原: 原 + 12 * k for 原 in 音符列表}
        base_offset = int(round(目标中心 - 原中心))
        def 八度折叠(音符):
            while 音符 < 目标最低:
                音符 += 12
            while 音符 > 目标最高:
                音符 -= 12
            return 音符
        return {原: 八度折叠(原 + base_offset) for 原 in 音符列表}

    # 情况2
    base_offset = int(round(目标中心 - 原中心))
    临时音符列表 = [原 + base_offset for 原 in 音符列表]
    映射 = {}
    for 原, 临 in zip(音符列表, 临时音符列表):
        最终 = 临
        while 最终 < 目标最低:
            最终 += 12
        while 最终 > 目标最高:
            最终 -= 12
        映射[原] = 最终
    return 映射
def 以能被三个八度覆盖最多的音为中心移调整体加减八度移调映射音名关系保留(音符列表, 目标最低=36, 目标最高=71):
    """
    在整体加减八度移调映射音名关系保留的基础上，
    用最大覆盖窗口中心替代简单最低最高中心。
    """
    if not 音符列表:
        return {}
    最低原 = min(音符列表)
    最高原 = max(音符列表)
    目标宽度 = 目标最高 - 目标最低

    # 最大覆盖窗口中心
    from collections import Counter
    cnt = Counter(音符列表)
    best_center = (最低原 + 最高原) / 2
    max_count = -1
    for low in sorted(cnt.keys()):
        high = low + 目标宽度
        count = sum(cnt[n] for n in cnt if low <= n <= high)
        if count > max_count:
            max_count = count
            best_center = (low + high) / 2
        elif count == max_count:
            default_center = (最低原 + 最高原) / 2
            if abs((low + high)/2 - default_center) < abs(best_center - default_center):
                best_center = (low + high) / 2
    原中心 = best_center
    目标中心 = (目标最低 + 目标最高) / 2

    # 先尝试完美八度平移
    for k in range(-3, 4):
        平移后最低 = 最低原 + 12 * k
        平移后最高 = 最高原 + 12 * k
        if 平移后最低 >= 目标最低 and 平移后最高 <= 目标最高:
            return {原: 原 + 12 * k for 原 in 音符列表}

    # 没有完美八度平移，选择最接近目标中心的八度偏移
    k_shift = round((目标中心 - 原中心) / 12)
    k_shift = int(k_shift)
    临时音符列表 = [原 + 12 * k_shift for 原 in 音符列表]

    临时最低 = min(临时音符列表)
    临时最高 = max(临时音符列表)

    if 临时最低 < 目标最低:
        k_low = (目标最低 - 临时最低 + 11) // 12
    else:
        k_low = 0
    if 临时最高 > 目标最高:
        k_high = (临时最高 - 目标最高 + 11) // 12
    else:
        k_high = 0

    映射 = {}
    for 原, 临 in zip(音符列表, 临时音符列表):
        最终 = 临
        if 临 < 目标最低:
            最终 = 临 + 12 * k_low
        elif 临 > 目标最高:
            最终 = 临 - 12 * k_high
        while 最终 < 目标最低:
            最终 += 12
        while 最终 > 目标最高:
            最终 -= 12
        映射[原] = 最终
    return 映射
def 以能被三个八度覆盖最多的音为中心移调整体加减八度移调映射直接裁剪(音符列表, 目标最低=36, 目标最高=71):
    """
    在整体加减八度移调映射直接裁剪的基础上，
    用最大覆盖窗口中心替代简单最低最高中心。
    """
    if not 音符列表:
        return {}
    最低原 = min(音符列表)
    最高原 = max(音符列表)
    目标宽度 = 目标最高 - 目标最低

    # 最大覆盖窗口中心
    from collections import Counter
    cnt = Counter(音符列表)
    best_center = (最低原 + 最高原) / 2
    max_count = -1
    for low in sorted(cnt.keys()):
        high = low + 目标宽度
        count = sum(cnt[n] for n in cnt if low <= n <= high)
        if count > max_count:
            max_count = count
            best_center = (low + high) / 2
        elif count == max_count:
            default_center = (最低原 + 最高原) / 2
            if abs((low + high)/2 - default_center) < abs(best_center - default_center):
                best_center = (low + high) / 2
    原中心 = best_center
    目标中心 = (目标最低 + 目标最高) / 2

    # 先尝试完美八度平移
    for k in range(-3, 4):
        平移后最低 = 最低原 + 12 * k
        平移后最高 = 最高原 + 12 * k
        if 平移后最低 >= 目标最低 and 平移后最高 <= 目标最高:
            return {原: 原 + 12 * k for 原 in 音符列表}

    # 没有完美八度平移，最接近目标中心的八度偏移
    k_shift = round((目标中心 - 原中心) / 12)
    k_shift = int(k_shift)
    临时音符列表 = [原 + 12 * k_shift for 原 in 音符列表]

    映射 = {}
    for 原, 临 in zip(音符列表, 临时音符列表):
        最终 = 临
        while 最终 < 目标最低:
            最终 += 12
        while 最终 > 目标最高:
            最终 -= 12
        映射[原] = 最终
    return 映射
def 直接裁剪映射(音符列表, 目标最低=36, 目标最高=71):
    """
    直接裁剪：高于 C4 (60) 的音降八度到高音区 [60,71]；
    低于 C4 (60) 的音升八度到低音区 [36,59]。
    """
    映射 = {}
    for 音符 in 音符列表:
        目标音符 = 音符
        if 音符 >= 60:
            # 高于或等于 C4，保持在 60-71 区间（降八度循环）
            while 目标音符 > 71:
                目标音符 -= 12
        else:
            # 低于 C4，保持在 36-59 区间（升八度循环）
            while 目标音符 < 36:
                目标音符 += 12
        # 二次保险（虽然理论上不会越界）
        while 目标音符 < 36:
            目标音符 += 12
        while 目标音符 > 71:
            目标音符 -= 12
        映射[音符] = 目标音符
    return 映射

def 转换音符为按键操作(音符事件列表, 映射表, 压缩方式="最大覆盖中心八度直接裁剪", 外部映射字典=None):
    """
    将音符事件列表转换为按键操作列表，自动移调至游戏音域。
    新增参数：外部映射字典 —— 如果提供，则直接使用，实现全曲协调移调。
    """
    按键操作列表 = []

    # 决定使用哪个映射字典
    if 外部映射字典 is not None:
        print("外部映射字典 is not None")
        音符映射字典 = 外部映射字典
    else:
        # 原有的内部计算（用于单独调用某个音轨时）
        所有原始音符 = list({ev['音符'] for ev in 音符事件列表})
        if 压缩方式 == "整体加减key音名关系保留":
            音符映射字典 = 整体加减key移调映射音名关系保留(所有原始音符)
        elif 压缩方式 == "整体加减key直接裁剪":
            音符映射字典 = 整体加减key移调映射直接裁剪(所有原始音符)
        elif 压缩方式 == "整体加减八度音名关系保留":
            音符映射字典 = 整体加减八度移调映射音名关系保留(所有原始音符)
        elif 压缩方式 == "整体加减八度直接裁剪":
            音符映射字典 = 整体加减八度移调映射直接裁剪(所有原始音符)
        elif 压缩方式 == "最大覆盖中心key音名保留":
            音符映射字典 = 以能被36个半音覆盖最多的音为中心移调整体加减key移调映射音名关系保留(所有原始音符)
        elif 压缩方式 == "最大覆盖中心key直接裁剪":
            音符映射字典 = 以能被36个半音覆盖最多的音为中心移调整体加减key移调映射直接裁剪(所有原始音符)
        elif 压缩方式 == "最大覆盖中心八度音名保留":
            音符映射字典 = 以能被三个八度覆盖最多的音为中心移调整体加减八度移调映射音名关系保留(所有原始音符)
        elif 压缩方式 == "最大覆盖中心八度直接裁剪":
            音符映射字典 = 以能被三个八度覆盖最多的音为中心移调整体加减八度移调映射直接裁剪(所有原始音符)
        elif 压缩方式 == "直接裁剪":
            音符映射字典 = 直接裁剪映射(所有原始音符)
        else:
            # 回退为简单归一化（逐音符折叠）
            音符映射字典 = {音符: 音符归一化(音符) for 音符 in 所有原始音符}

    正在播放的音符 = {}

    for 事件 in 音符事件列表:
        时间 = 事件['时间']
        原始音符 = 事件['音符']
        类型 = 事件['类型']

        # 从映射字典中获取目标音符（若不存在则保留原音符，但理论上不会发生）
        音符 = 音符映射字典.get(原始音符, 原始音符)

        if 音符 in 映射表:
            按键信息 = 映射表[音符]
            主键, 修饰键 = 按键信息

            if 类型 == '开始':
                正在播放的音符[原始音符] = {
                    '开始时间': 时间,
                    '主键': 主键,
                    '修饰键': 修饰键,
                    '映射音符': 音符
                }
                if 修饰键:
                    按键操作列表.append({
                        '时间': 时间,
                        '操作': '按下',
                        '按键': 修饰键
                    })
                按键操作列表.append({
                    '时间': 时间,
                    '操作': '按下',
                    '按键': 主键
                })

            elif 类型 == '结束' and 原始音符 in 正在播放的音符:
                按键操作列表.append({
                    '时间': 时间,
                    '操作': '弹起',
                    '按键': 主键
                })
                if 修饰键:
                    按键操作列表.append({
                        '时间': 时间,
                        '操作': '弹起',
                        '按键': 修饰键
                    })
                del 正在播放的音符[原始音符]

    按键操作列表.sort(key=lambda x: x['时间'])
    return 按键操作列表


# ==================== JSON 存取 ====================
def 保存操作到JSON(按键操作列表, 输出文件路径):
    try:
        输出文件路径 = Path(输出文件路径)
        输出文件路径.parent.mkdir(parents=True, exist_ok=True)
        with open(输出文件路径, 'w', encoding='utf-8') as f:
            json.dump(按键操作列表, f, ensure_ascii=False, indent=2)
        print(f"操作已保存到: {输出文件路径}")
        return True
    except Exception as e:
        print(f"保存JSON文件时出错: {e}")
        return False


def 从JSON加载操作(文件路径):
    """
    从JSON文件加载按键操作
    """
    try:
        with open(文件路径, 'r', encoding='utf-8') as f:
            按键操作列表 = json.load(f)
        return 按键操作列表
    except Exception as e:
        print(f"加载JSON文件时出错: {e}")
        return []


# ==================== 演奏音轨 ====================
def 演奏音轨(游戏句柄, 按键操作列表, i=0, 线程事件=None,演奏速度=1.0):
    def 等待(总时间, 线程事件):
        if 总时间 < 1:
            if not 线程事件.is_set():
                return
            time.sleep(总时间)
        else:
            full_seconds = int(总时间)
            for _ in range(full_seconds):
                if not 线程事件.is_set():
                    return
                time.sleep(1)
            remaining = 总时间 - full_seconds
            if remaining > 0:
                if not 线程事件.is_set():
                    return
                time.sleep(remaining)

    if not 按键操作列表:
        print("没有可演奏的操作")
        return

    print(f"开始演奏音轨，共 {len(按键操作列表)} 个按键操作")

    开始时间 = time.time()
    当前索引 = 0
    按键操作列表 = [
        {**op, '时间': op['时间'] / 演奏速度} for op in 按键操作列表
    ]
    while 当前索引 < len(按键操作列表):
        if not 线程事件.is_set():
            return
        当前时间 = time.time() - 开始时间
        操作 = 按键操作列表[当前索引]

        if 操作['时间'] <= 当前时间:
            if not 线程事件.is_set():
                return
            if 操作['操作'] == '按下':
                模拟按键按下(游戏句柄, 操作['按键'])
            elif 操作['操作'] == '弹起':
                模拟按键弹起(游戏句柄, 操作['按键'])
            当前索引 += 1
        else:
            等待时间 = 操作['时间'] - 当前时间
            if 等待时间 > 0:
                if not 线程事件.is_set():
                    return
                等待(等待时间, 线程事件)


    print(f"音轨{i}演奏完成")


def 转换并保存MIDI_支持静音区间(midi文件路径, 输出json基础路径, 暂停区间字典=None, 保存文件=False,
                                 压缩方式="最大覆盖中心八度直接裁剪", 升降key=0,演奏轨道元组=(0,1,2,3,4,5,6),垂直反转映射=False,水平反转映射=False):
    音轨事件字典, tpb = 分析MIDI文件(midi文件路径)
    if not 音轨事件字典:
        return [] if 保存文件 else {}

    映射表 = 音符到按键映射(垂直反转映射,水平反转映射)


    json文件路径列表 = []
    音轨按键操作字典 = {}

    # ---------- 第一步：收集所有音轨的音符，并记录需要处理的音轨及事件 ----------
    全局原始音符集合 = set()
    待处理音轨 = []  # 元素: (音轨号, 过滤后的事件列表)

    for 音轨号, 事件列表 in 音轨事件字典.items():
        if 音轨号 in 演奏轨道元组:
            pass
        else:
            continue
        # 静音过滤
        if 暂停区间字典 and 音轨号 in 暂停区间字典:
            静音区间 = 暂停区间字典[音轨号]
            原数量 = len(事件列表)
            事件列表 = [ev for ev in 事件列表
                        if not any(start <= ev['时间'] <= end for start, end in 静音区间)]
            print(f"  过滤掉 {原数量 - len(事件列表)} 个位于静音区间的音符事件")
        if not 事件列表:
            print(f"  音轨{音轨号} 过滤后无音符，跳过")
            continue

        # ---- 升降key：在压缩前对音符进行整体移调 ----
        if 升降key != 0:
            for ev in 事件列表:
                ev['音符'] += 升降key
        # -------------------------------------------

        待处理音轨.append((音轨号, 事件列表))
        # 收集该轨所有（已移调）音符
        for ev in 事件列表:
            全局原始音符集合.add(ev['音符'])

    if not 待处理音轨:
        print("没有有效音轨可处理")
        return [] if 保存文件 else {}

    # ---------- 第二步：根据压缩方式计算全局移调映射 ----------
    所有原始音符列表 = list(全局原始音符集合)
    if 压缩方式 == "整体加减key音名关系保留":
        全局映射 = 整体加减key移调映射音名关系保留(所有原始音符列表)
    elif 压缩方式 == "整体加减key直接裁剪":
        全局映射 = 整体加减key移调映射直接裁剪(所有原始音符列表)
    elif 压缩方式 == "整体加减八度音名关系保留":
        全局映射 = 整体加减八度移调映射音名关系保留(所有原始音符列表)
    elif 压缩方式 == "整体加减八度直接裁剪":
        全局映射 = 整体加减八度移调映射直接裁剪(所有原始音符列表)
    elif 压缩方式 == "最大覆盖中心key音名保留":
        全局映射 = 以能被36个半音覆盖最多的音为中心移调整体加减key移调映射音名关系保留(所有原始音符列表)
    elif 压缩方式 == "最大覆盖中心key直接裁剪":
        全局映射 = 以能被36个半音覆盖最多的音为中心移调整体加减key移调映射直接裁剪(所有原始音符列表)
    elif 压缩方式 == "最大覆盖中心八度音名保留":
        全局映射 = 以能被三个八度覆盖最多的音为中心移调整体加减八度移调映射音名关系保留(所有原始音符列表)
    elif 压缩方式 == "最大覆盖中心八度直接裁剪":
        全局映射 = 以能被三个八度覆盖最多的音为中心移调整体加减八度移调映射直接裁剪(所有原始音符列表)
    elif 压缩方式 == "直接裁剪":
        全局映射 = 直接裁剪映射(所有原始音符列表)
    else:
        # 回退为归一化（保持一致性，但会破坏和声）
        全局映射 = {音符: 音符归一化(音符) for 音符 in 所有原始音符列表}

    print(f"使用压缩方式: {压缩方式}，全局映射包含 {len(全局映射)} 个音符")

    # ---------- 第三步：用同一全局映射转换每个音轨 ----------
    for 音轨号, 事件列表 in 待处理音轨:
        print(f"\n处理音轨 {音轨号}...")
        按键操作列表 = 转换音符为按键操作(事件列表, 映射表, 压缩方式, 外部映射字典=全局映射)

        if 保存文件:
            json文件路径 = 输出json基础路径/midi文件路径.stem/f"{midi文件路径.stem}_音轨{音轨号}.json"
            保存操作到JSON(按键操作列表, json文件路径)
        音轨按键操作字典[音轨号] = 按键操作列表

    return 音轨按键操作字典

from 窗口假激活 import 线程持续激活
def 多线程演奏_直接从内存(游戏句柄, 音轨按键操作字典, 线程事件,演奏速度=1.0):
    """
    直接从内存中的按键操作列表演奏多个音轨（不经过 JSON 文件）。
    音轨按键操作字典: {音轨号: 按键操作列表}
    """
    import pydirectinput

    # 录屏快捷键（开始）
    """  录屏开始按键列表 = ["shift", "ctrl", "alt", "k"]
    for 按键 in 录屏开始按键列表:
        pydirectinput.keyDown(按键)
        time.sleep(0.1)
    for 按键 in 录屏开始按键列表:
        pydirectinput.keyUp(按键)
        time.sleep(0.1)"""

    time.sleep(1)

    if not 音轨按键操作字典:
        print("没有可演奏的操作")
        return

    print(f"\n开始多线程演奏（直接内存），共 {len(音轨按键操作字典)} 个音轨")

    线程列表 = []
    for i, (音轨号, 按键操作列表) in enumerate(音轨按键操作字典.items()):
        if 按键操作列表:
            总时长 = max(op['时间'] for op in 按键操作列表) if 按键操作列表 else 0
            print(f"音轨 {音轨号} 总时长: {总时长:.2f} 秒")
            thread = threading.Thread(
                target=演奏音轨,
                args=(游戏句柄, 按键操作列表, 音轨号, 线程事件,演奏速度),
                name=f"音轨{音轨号}"
            )
            线程列表.append(thread)

    for thread in 线程列表:
        thread.start()

    for thread in 线程列表:
        thread.join()


    """ 录屏结束按键列表 = ["shift", "ctrl", "alt", "j"]
    for 按键 in 录屏结束按键列表:
        pydirectinput.keyDown(按键)
        time.sleep(0.1)
    for 按键 in 录屏结束按键列表:
        pydirectinput.keyUp(按键)
        time.sleep(0.1)"""

    if not 线程事件.is_set():  # 事件未设置 → 返回
        return
    演奏36个音(游戏句柄, 开始时间偏移=0.0, 音符间隔=0.1, 音符时长=0.01, 线程事件=线程事件)

# ==================== 多线程演奏（与原代码相同）====================
def 多线程演奏(游戏句柄, json文件路径列表,线程事件,演奏速度=1.0):
    import pydirectinput
    """录屏开始按键列表=["shift","ctrl","alt","k"]#obs快捷键
    for 按键 in 录屏开始按键列表:
        pydirectinput.keyDown(按键)
        time.sleep(0.1)
    for 按键 in 录屏开始按键列表:
        pydirectinput.keyUp(按键)
        time.sleep(0.1)"""


    time.sleep(1)

    """
    使用多线程同时演奏多个音轨
    """
    if not json文件路径列表:
        print("没有可演奏的JSON文件")
        return

    print(f"\n开始多线程演奏，共 {len(json文件路径列表)} 个音轨")

    # 创建并启动所有音轨的线程
    线程列表 = []
    for i, json文件 in enumerate(json文件路径列表):
        # 从JSON加载操作
        按键操作列表 = 从JSON加载操作(json文件)

        if 按键操作列表:
            # 计算总时长
            总时长 = max(op['时间'] for op in 按键操作列表) if 按键操作列表 else 0
            print(f"音轨 {i} 总时长: {总时长:.2f} 秒")

            # 创建线程
            thread = threading.Thread(
                target=演奏音轨,
                args=(游戏句柄, 按键操作列表,i,线程事件,演奏速度),
                name=f"音轨{i}"
            )
            线程列表.append(thread)

    # 同时启动所有线程
    for thread in 线程列表:
        thread.start()

    # 等待所有线程完成
    for thread in 线程列表:
        thread.join()

    """time.sleep(1)
    录屏结束按键列表 = ["shift","ctrl","alt", "j"]
    for 按键 in 录屏结束按键列表:
        pydirectinput.keyDown(按键)
        time.sleep(0.1)
    for 按键 in 录屏结束按键列表:
        pydirectinput.keyUp(按键)
        time.sleep(0.1)"""
    print("所有音轨演奏完成")
    if not 线程事件.is_set():  # 事件未设置 → 返回
        return
    time.sleep(1)
    if not 线程事件.is_set():  # 事件未设置 → 返回
        return
    演奏36个音(游戏句柄, 开始时间偏移=0.0, 音符间隔=0.1, 音符时长=0.01,线程事件=线程事件)


def 演奏36个音(游戏句柄, 开始时间偏移=0.0, 音符间隔=0.5, 音符时长=0.3,线程事件=None):
    """
    按顺序演奏36个音符（MIDI编号36~71），每个音符按下后保持一定时长再弹起。

    参数:
        游戏句柄: 目标窗口句柄
        开始时间偏移: 第一个音符开始的时间（秒），默认为0
        音符间隔: 相邻音符开始的时间间隔（秒），默认为0.5
        音符时长: 每个音符按下的持续时间（秒），默认为0.3
    """
    # 1. 生成模拟MIDI音符事件
    音符事件列表 = []
    当前时间 = 开始时间偏移

    for 音符 in range(36, 72):  # 36~71 共36个音
        # 音符开始
        音符事件列表.append({
            '时间': 当前时间,
            '类型': '开始',
            '音符': 音符,
            '力度': 80  # 力度值，不影响模拟按键
        })
        # 音符结束
        音符事件列表.append({
            '时间': 当前时间 + 音符时长,
            '类型': '结束',
            '音符': 音符
        })
        当前时间 += 音符间隔

    # 2. 获取音符到按键的映射表
    映射表 = 音符到按键映射()

    # 3. 转换为按键操作列表（自动处理修饰键）
    按键操作列表 = 转换音符为按键操作(音符事件列表, 映射表,)
    #print(按键操作列表)

    # 4. 调用演奏函数
    print(f"开始演奏36个音，共 {len(按键操作列表)} 个按键操作")
    演奏音轨(游戏句柄, 按键操作列表,1,线程事件)
if __name__ == "__main__":
    import win32gui
    import ctypes

    from tkinter import ttk
    from tkinter import messagebox
    import tkinter as tk
    线程事件 = threading.Event()
    线程事件停止= threading.Event()
    def 函数停止任务():
        print("发送停止信号")
        线程事件.clear()


    import sys
    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent.absolute()
    else:
        current_dir = APP_ROOT
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

    def 集合启动线程(任务名="异环钢琴单曲"):
        线程事件停止.set()
        线程事件.set()
        if 任务名 == "异环钢琴单曲":
            with open(current_dir / "外置配置文件夹"/"演奏文件列表.json", 'r', encoding='utf-8') as f:
                数据 = json.load(f)
            异环句柄 = 函数精确查找窗口句柄("UnrealWindow", "异环  ")#"异环  "/"NTE  "

            filepath = 数据.get("filepath")

            演奏轨道 = 数据.get("演奏轨道", (0, 1, 2, 3, 4, 5, 6))

            压缩方式 = 数据.get("压缩方式", "最大覆盖中心八度直接裁剪")

            key加减 = 数据.get("key加减", 0)

            生成json = 数据.get("生成json", False)

            垂直反转映射 = 数据.get("垂直反转映射变量", False)

            水平反转映射 = 数据.get("水平反转映射变量", False)
            演奏速度=数据.get("异环钢琴演奏速度变量", 1.0)
            # 调用转换函数（只使用选中的轨道）

            音轨按键操作字典 = 转换并保存MIDI_支持静音区间(

                Path(filepath), current_dir / "外置配置文件夹"/"演奏文件", 暂停区间字典=None,

                保存文件=生成json, 压缩方式=压缩方式, 升降key=key加减,

                演奏轨道元组=演奏轨道,垂直反转映射=垂直反转映射,水平反转映射=水平反转映射

            )

            if 音轨按键操作字典:

                多线程演奏_直接从内存(异环句柄, 音轨按键操作字典, 线程事件,演奏速度)

            else:

                print("没有可演奏的音轨")


        elif 任务名 == "异环钢琴JSON":
            with open(current_dir / "外置配置文件夹"/"演奏文件列表.json", 'r', encoding='utf-8') as f:
                数据 = json.load(f)
            folderpath = 数据.get("folderpath")
            异环句柄 = 函数精确查找窗口句柄("UnrealWindow", "异环  ")#"异环  "/"NTE  "
            演奏速度 = 数据.get("异环钢琴演奏速度变量", 1.0)

            # 直接演奏文件夹内所有 JSON

            json文件列表 = sorted(

                [os.path.join(folderpath, f) for f in os.listdir(folderpath) if f.endswith('.json')]

            )

            if json文件列表:

                多线程演奏(异环句柄, json文件列表, 线程事件,演奏速度)

            else:

                print("文件夹内无 JSON 文件")
        线程事件.clear()
        线程事件停止.clear()
        messagebox.showinfo("提示",
                            f"任务结束")
    def 集合启动任务(任务名="异环钢琴单曲"):
        if  线程事件停止.is_set():
            messagebox.showinfo("提示",
                                f"上一个任务未停下")
        else:
            threading.Thread(target=lambda :threading.Thread(target=集合启动线程,
                             args=(任务名,)).start(),
                             args=()).start()

    def 异环钢琴窗口创建():
        异环钢琴演奏子容器 = tk.Tk()


        title = f"异环钢琴"
        异环钢琴演奏子容器.title(title)
        def midi_to_note_name(midi):
            """将 MIDI 编号（0~127）转换为音名，例如 60 -> C4, 61 -> C#4, 36 -> C2"""
            notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            octave = midi // 12 - 1
            note = notes[midi % 12]
            return f"{note}{octave}"


        # 外部可用变量
        json_path = current_dir/ "外置配置文件夹" / "演奏文件列表.json"
        当前文件路径 = None  # 当前选中的文件/文件夹路径
        音轨复选框变量 = {}  # {音轨号: tk.BooleanVar}
        音轨内部框架 = None

        # ========== 文件选择区 ==========

        选择区 = ttk.LabelFrame(异环钢琴演奏子容器, text="选择演奏文件")
        选择区.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        选择区.grid_columnconfigure(0, weight=1)

        按钮框 = ttk.Frame(选择区)
        按钮框.grid(row=0, column=0, pady=5)
        from tkinter import filedialog

        def 选择文件(后缀):
            nonlocal 当前文件路径, 音轨内部框架, 音轨复选框变量
            initialdir = current_dir / "外置配置文件夹" / "midi"

            filepath = filedialog.askopenfilename(
                initialdir=initialdir, title=f"选择 {后缀} 文件",
                filetypes=[(f"{后缀} 文件", f"*{后缀}")]
            )
            if not filepath:
                return
            当前文件路径 = Path(filepath)
            当前文件标签.config(text=str(当前文件路径))

            # 清除旧的音轨框架
            if 音轨内部框架:
                音轨内部框架.destroy()
                音轨内部框架 = None
            音轨复选框变量.clear()

            # 分析 MIDI 文件
            try:
                from 异环钢琴main import 分析MIDI文件
                音轨事件字典, _ = 分析MIDI文件(str(当前文件路径))
            except Exception as e:

                messagebox.showerror("错误", f"分析 MIDI 失败：{e}")
                return

            if not 音轨事件字典:
                messagebox.showinfo("提示", "文件没有包含任何音符事件")
                return

            音轨内部框架 = ttk.Frame(音轨容器)
            音轨内部框架.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # 表头
            header = ttk.Frame(音轨内部框架)

            header.pack(fill=tk.X)
            ttk.Label(header, text="轨道", width=8).pack(side=tk.LEFT)
            ttk.Label(header, text="音域范围", width=16).pack(side=tk.LEFT)
            ttk.Label(header, text="音符数量", width=10).pack(side=tk.LEFT)
            ttk.Label(header, text="启用").pack(side=tk.LEFT)

            for 音轨号, 事件列表 in sorted(音轨事件字典.items()):
                音符列表 = [ev['音符'] for ev in 事件列表 if ev['类型'] == '开始']
                if not 音符列表:
                    continue
                最低音 = min(音符列表)
                最高音 = max(音符列表)
                音域 = f"({最低音}~{最高音}/{midi_to_note_name(最低音)}~{midi_to_note_name(最高音)})"
                数量 = len(音符列表)

                var = tk.BooleanVar(value=True)
                音轨复选框变量[音轨号] = var

                row = ttk.Frame(音轨内部框架)
                row.pack(fill=tk.X)
                ttk.Label(row, text=f"音轨 {音轨号}", width=8).pack(side=tk.LEFT)
                ttk.Label(row, text=音域, width=16).pack(side=tk.LEFT)
                ttk.Label(row, text=str(数量), width=10).pack(side=tk.LEFT)
                ttk.Checkbutton(row, variable=var).pack(side=tk.LEFT)

        def 选择json文件夹():
            nonlocal 当前文件路径, 音轨内部框架, 音轨复选框变量
            initialdir = current_dir / "外置配置文件夹" / "演奏文件"
            folder = filedialog.askdirectory(initialdir=initialdir, title="选择 JSON 文件夹")
            if not folder:
                return
            当前文件路径 = Path(folder)
            当前文件标签.config(text=str(当前文件路径))

            # 清除音轨内容（文件夹不需要音轨选择）
            if 音轨内部框架:
                音轨内部框架.destroy()
                音轨内部框架 = None
            音轨复选框变量.clear()
            音轨内部框架 = ttk.Frame(音轨容器)
            音轨内部框架.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # 表头
            header = ttk.Frame(音轨内部框架)
            header.pack(fill=tk.X)
            ttk.Label(header, text="json文件不能设置，请直接演奏", width=28).pack(side=tk.LEFT)

        ttk.Button(按钮框, text="1. 选择 .mid 文件",
                   command=lambda: 选择文件(".mid")).pack(side=tk.LEFT, padx=2)
        ttk.Button(按钮框, text="2. 选择 .midi 文件",
                   command=lambda: 选择文件(".midi")).pack(side=tk.LEFT, padx=2)
        ttk.Button(按钮框, text="3. 选择 JSON 文件夹",
                   command=选择json文件夹).pack(side=tk.LEFT, padx=2)

        当前文件标签 = ttk.Label(选择区, text="未选择文件", foreground="gray")
        当前文件标签.grid(row=1, column=0, sticky="w", padx=5)

        # ========== 音轨选择区 ==========
        音轨容器 = ttk.LabelFrame(异环钢琴演奏子容器, text="音轨设置选择(json文件不显示)")
        音轨容器.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # ========== 设置区 ==========
        设置区 = ttk.LabelFrame(异环钢琴演奏子容器, text="演奏设置1")
        设置区.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        设置行1 = ttk.Frame(设置区)
        设置行1.pack(fill=tk.X, pady=5, padx=5)

        tk.Label(设置行1, text="加减 Key:", font=("微软雅黑", 12)).pack(side=tk.LEFT)
        异环钢琴加减key变量 = tk.IntVar(value=0)
        tk.Spinbox(设置行1, from_=-100, to=100, increment=1,
                   textvariable=异环钢琴加减key变量, width=5).pack(side=tk.LEFT, padx=5)

        tk.Label(设置行1, text="压缩方式:", font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=(15, 0))
        异环钢琴压缩方式变量 = tk.StringVar(value="最大覆盖中心八度直接裁剪")
        ttk.Combobox(设置行1, textvariable=异环钢琴压缩方式变量,
                     values=["整体加减key音名关系保留", "整体加减key直接裁剪",
                             "整体加减八度音名关系保留", "整体加减八度直接裁剪",
                             "最大覆盖中心key音名保留", "最大覆盖中心key直接裁剪",
                             "最大覆盖中心八度音名保留", "最大覆盖中心八度直接裁剪",
                             "直接裁剪"], width=20).pack(side=tk.LEFT, padx=5)

        生成json演奏文件变量 = tk.IntVar(value=0)
        ttk.Checkbutton(设置行1, text="生成 JSON 演奏文件", variable=生成json演奏文件变量).pack(side=tk.LEFT, padx=20)
        设置区 = ttk.LabelFrame(异环钢琴演奏子容器, text="演奏设置2")
        设置区.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        设置行1 = ttk.Frame(设置区)
        设置行1.pack(fill=tk.X, pady=5, padx=5)
        tk.Label(设置行1, text="演奏速度:", font=("微软雅黑", 12)).pack(side=tk.LEFT)
        异环钢琴演奏速度变量 = tk.DoubleVar(value=1.0)
        tk.Spinbox(设置行1, from_=0.01, to=100, increment=0.1,
                   textvariable=异环钢琴演奏速度变量, width=5).pack(side=tk.LEFT, padx=5)
        tk.Label(设置行1, text="映射反转:", font=("微软雅黑", 12)).pack(side=tk.LEFT)
        水平反转映射变量 = tk.IntVar(value=0)
        ttk.Checkbutton(设置行1, text="水平反转", variable=水平反转映射变量).pack(side=tk.LEFT, padx=20)
        垂直反转映射变量 = tk.IntVar(value=0)
        ttk.Checkbutton(设置行1, text="垂直反转", variable=垂直反转映射变量).pack(side=tk.LEFT, padx=20)

        def 启动演奏():
            if not 当前文件路径:
                messagebox.showinfo("提示", "请先选择一个文件或文件夹")
                return

            # 保存设置到 JSON
            data = {
                "压缩方式": 异环钢琴压缩方式变量.get(),
                "key加减": 异环钢琴加减key变量.get(),
                "生成json": bool(生成json演奏文件变量.get()),
                "异环钢琴演奏速度变量": float(异环钢琴演奏速度变量.get()),
                "垂直反转映射变量": 垂直反转映射变量.get(),
                "水平反转映射变量": 水平反转映射变量.get(),
            }

            is_midi = 当前文件路径.suffix.lower() in ('.mid', '.midi')

            if is_midi:
                if not 音轨复选框变量:
                    messagebox.showinfo("提示", "尚未分析音轨，请重新选择文件")
                    return
                勾选音轨 = [音轨号 for 音轨号, var in 音轨复选框变量.items() if var.get()]
                if not 勾选音轨:
                    messagebox.showinfo("提示", "请至少勾选一个音轨")
                    return
                data["filepath"] = str(当前文件路径)
                data["演奏轨道"] = 勾选音轨
                任务名 = "异环钢琴单曲"
            else:
                data["folderpath"] = str(当前文件路径)
                任务名 = "异环钢琴JSON"

            try:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                messagebox.showwarning("警告", f"保存设置失败: {e}")

            # 启动任务（只传任务名）
            集合启动任务(任务名)

        # ========== 控制按钮 ==========
        控制区 = ttk.Frame(异环钢琴演奏子容器)
        控制区.grid(row=6, column=0, pady=10)

        ttk.Button(控制区, text="▶ 开始演奏", command=启动演奏).pack(side=tk.LEFT, padx=5)
        ttk.Button(控制区, text="■ 停止演奏", command=函数停止任务).pack(side=tk.LEFT, padx=5)
        ttk.Button(控制区, text="打开演奏文件夹", command=lambda: os.startfile(current_dir / "外置配置文件夹")).pack(side=tk.LEFT, padx=5)
        ttk.Button(控制区, text="打开说明书", command=lambda: os.startfile(current_dir /"异环钢琴自动演奏工具使用说明书.md")).pack(side=tk.LEFT, padx=5)

        # ---------- 内部函数 ----------

        def 加载设置():
            """UI 启动时从 JSON 恢复上次的设置"""
            if not json_path.exists():
                return
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception:
                return

            # 恢复压缩方式、key、生成json
            if "压缩方式" in data:
                异环钢琴压缩方式变量.set(data["压缩方式"])
            if "key加减" in data:
                异环钢琴加减key变量.set(data["key加减"])
            if "生成json" in data:
                生成json演奏文件变量.set(1 if data["生成json"] else 0)
            if "异环钢琴演奏速度变量" in data:
                异环钢琴演奏速度变量.set(data["异环钢琴演奏速度变量"])
            if "水平反转映射变量" in data:
                水平反转映射变量.set(1 if data["水平反转映射变量"] else 0)
            if "垂直反转映射变量" in data:
                垂直反转映射变量.set(1 if data["垂直反转映射变量"] else 0)

        # 初始化：加载上次设置
        加载设置()
        运行栏 = ttk.Frame(异环钢琴演奏子容器)
        运行栏.grid(row=7, column=0, pady=5)
        tk.Label(运行栏, text="工具设定音域：C2-B4/36-71", font=("楷体", 16, "bold", "italic"), fg="red").grid(row=1, column=0)
        异环钢琴演奏子容器.mainloop()


    异环钢琴窗口创建()
