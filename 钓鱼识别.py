import sys

from opencv识图 import 函数_在指定区域内进行模板匹配,函数_在指定区域内进行模板匹配返回横坐标范围
import time
from pathlib import Path
from 后台键盘鼠标 import  simulate_key_down, simulate_key_up, simulate_key_press_hold
from 后台截图 import 函数截图到内存

def 异环钓鱼(配置, 线程事件,):
    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent.absolute()
    else:
        current_dir = Path(__file__).parent.absolute()
    判断区域路径=current_dir/"判定区域.png"
    滑块路径=current_dir/"滑块.png"
    钓鱼成功判定图片=current_dir/"钓鱼成功判定图片.png"
    判断频率=0.005
    按键元组 = (0x41, 0x44, 0x46, 0x1B)
    _, _, hwnd, 窗口矩形, _ = 配置
    左a,右d,钓鱼f,退出esc=按键元组
    start_time = time.time()
    while time.time() - start_time < 60:
        time.sleep(判断频率)
        if not 线程事件.is_set():
            return
        png数据 = 函数截图到内存(hwnd, 窗口矩形)
        是否匹配,_ , _, _ = 函数_在指定区域内进行模板匹配(背景图片数据=png数据, 限定区域=(301, 288, 562, 427),
                                                                                        模板路径=钓鱼成功判定图片, 最低相似度=0.8)
        if 是否匹配:
            print("鱼耐力耗尽")
            break
        simulate_key_press_hold(hwnd, 钓鱼f, 0.01)
        _, _, 最小x, _, 最大x, _ = 函数_在指定区域内进行模板匹配返回横坐标范围(背景图片数据=png数据, 限定区域=(391, 33, 503, 43), 模板路径=判断区域路径, 最低相似度=0.9)

        _, _, x坐标2, _ = 函数_在指定区域内进行模板匹配(背景图片数据=png数据, 限定区域=(391, 33, 503, 43), 模板路径=滑块路径, 最低相似度=0.8)

        if 最小x < x坐标2 and 最大x > x坐标2:
            simulate_key_up(hwnd, 右d)
            simulate_key_up(hwnd, 左a)
        elif 最小x > x坐标2:
            simulate_key_up(hwnd, 左a)
            simulate_key_down(hwnd, 右d)
        else:
            simulate_key_up(hwnd, 右d)
            simulate_key_down(hwnd, 左a)

    simulate_key_up(hwnd, 右d)
    simulate_key_up(hwnd, 左a)