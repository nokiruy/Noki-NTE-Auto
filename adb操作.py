import subprocess
import time
import logging

from 后台键鼠 import 真实鼠标坐标后台点击,模拟平滑拖拽,后台粘贴文本
from 窗口假激活 import 窗口假激活
logger = logging.getLogger("database")
def 等待(线程事件,秒):
    if int(秒*10)<1:
        秒=0.1
    for _ in range(int(秒*10)):
        if 线程事件.is_set():
            time.sleep(0.095)
        else:
            break
# ======================== 核心操作函数 ========================
def 点击(adb_config, x, y):
    """点击指定设备的屏幕坐标"""
    adb路径, 端口,hwnd, 窗口矩形,(PC全局延迟,PC键盘延迟) = adb_config
    if 窗口矩形:
        窗口假激活(hwnd)
        真实鼠标坐标后台点击(hwnd,窗口矩形, (x, y), 0.002+PC全局延迟)
    else:
        命令=f"input tap {x} {y}"
        adb命令 = f'"{adb路径}" -s {端口} shell {命令}'
        subprocess.run(adb命令, shell=True)
def 输入文本(adb_config, text):
    """向设备输入文本"""
    adb路径, 端口,hwnd, 窗口矩形,(PC全局延迟,PC键盘延迟) = adb_config

    if hwnd:


        后台粘贴文本(hwnd)
    else:
        # 使用 ADB 的 input text 命令发送文本
        adb命令 = f'"{adb路径}" -s {端口} shell input text "{text}"'
        subprocess.run(adb命令, shell=True)
def 滑动(adb_config, x1, y1, x2, y2, 持续时间=200):
    """在指定设备上滑动"""
    adb路径, 端口,hwnd, 窗口矩形,(PC全局延迟,PC键盘延迟) = adb_config
    if 窗口矩形:
        模拟平滑拖拽(窗口矩形, hwnd, x1, y1, x2, y2, 拖拽时间=持续时间/1000, 步数=60)
    else:
        命令=f"input swipe {x1} {y1} {x2} {y2} {持续时间}"

        adb命令 = f'"{adb路径}" -s {端口} shell {命令}'
        subprocess.run(adb命令, shell=True)

def 雷电命令(adb路径, 端口,命令):
    adb命令=f'"{adb路径}" adb --index {端口} --command "shell {命令}"'
    try:
        subprocess.run(adb命令, shell=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"[{端口}] ADB命令失败:{e}" )
def 长按(adb_config, x, y, 持续时间=1000):
    """长按屏幕上的指定坐标"""
    adb路径, 端口,hwnd, 窗口矩形,(PC全局延迟,PC键盘延迟) = adb_config
    if 窗口矩形:
        窗口假激活(hwnd)
        真实鼠标坐标后台点击(hwnd,窗口矩形, (x, y), 0.009+PC全局延迟)
        time.sleep(持续时间/1000)
    else:
        命令=f"input swipe {x} {y} {x} {y} {持续时间}"

        
        adb命令 = f'"{adb路径}" -s {端口} shell {命令}'
        subprocess.run(adb命令, shell=True)
        time.sleep(0.005)
def 键盘按键(adb_config, key_event):
    """发送按键事件"""
    adb路径, 端口,hwnd, 窗口矩形,(PC全局延迟,PC键盘延迟) = adb_config
    adb命令 = f'"{adb路径}" -s {端口} shell input keyevent {key_event}'
    subprocess.run(adb命令, shell=True)
# ======================== 应用管理函数 ========================
def 列出所有应用包名(adb_config):
    """获取设备上的应用包名列表"""
    adb路径, 端口,hwnd, 窗口矩形,(PC全局延迟,PC键盘延迟) = adb_config
    adb命令 = f'"{adb路径}" -s {端口} shell pm list packages'
    try:
        output = subprocess.check_output(adb命令, shell=True, text=True, encoding='utf-8')
        包名列表 = [line.strip().replace('package:', '') for line in output.split('\n') if line.startswith('package:')]
        return 包名列表
    except subprocess.CalledProcessError as e:
        logger.error(f"[{端口}] ADB命令失败:{e}" )
        return []
def 启动应用(adb_config, 包名):
    """通过包名启动应用"""
    try:
        adb路径, 端口,hwnd, 窗口矩形,(PC全局延迟,PC键盘延迟) = adb_config
        命令=f"monkey -p {包名} -c android.intent.category.LAUNCHER 1"

        adb命令 = f'"{adb路径}" -s {端口} shell {命令}'
        subprocess.run(adb命令, shell=True)
        logger.info(f"启动游戏{包名}")
        time.sleep(3)
    except Exception as e:
        logger.error(f"启动应用失败: {str(e)}")
def 关闭应用(adb_config, 包名):
    """强制停止应用"""
    try:
        adb路径, 端口,hwnd, 窗口矩形,(PC全局延迟,PC键盘延迟) = adb_config
        命令 = f"am force-stop {包名}"

        adb命令 = f'"{adb路径}" -s {端口} shell {命令}'
        subprocess.run(adb命令, shell=True)
        logger.info(f"关闭游戏{包名}")
    except Exception as e:
        logger.error(f"关闭应用失败: {str(e)}")
def 检查应用日志(adb_config, 包名):
    """检查应用日志"""
    adb路径, 端口,hwnd, 窗口矩形,(PC全局延迟,PC键盘延迟) = adb_config
    adb命令 = f'"{adb路径}" -s {端口} logcat | findstr "{包名}"'
    subprocess.run(adb命令, shell=True)
from pathlib import Path
import sys
def 获取所有设备端口(adb路径):
    """
    获取当前通过ADB连接的所有设备的端口/序列号列表
    返回格式示例: ["emulator-5554", "127.0.0.1:16384"]
    """
    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent.absolute()
    else:
        current_dir = Path(__file__).parent.absolute()
    游戏列表 = ["异环", "幻塔"]
    for 游戏 in 游戏列表:
        target_path = current_dir / f"{游戏}图片"
        if target_path.exists() and target_path.is_dir():  # 判断文件是否存在
            if 游戏 == "异环":
                return []
    try:
        # 执行 adb devices 命令
        adb命令 = f'"{adb路径}" devices'
        output = subprocess.check_output(
            adb命令,
            shell=True,
            text=True,
            encoding='utf-8'
        )

        # 解析输出
        设备列表 = []
        for line in output.splitlines():
            # 跳过标题行和空行
            if line.strip() == "" or "List of devices" in line:
                continue

            # 提取设备序列号和状态
            parts = line.strip().split('\t')
            if len(parts) >= 2 and parts[1] == 'device':
                设备列表.append(parts[0])

        return 设备列表

    except subprocess.CalledProcessError as e:
        logger.error(f"ADB命令执行失败: {e}")
        return []
    except Exception as e:
        logger.error(f"未知错误: {e}")
        return []
# ======================== 使用示例 ========================
