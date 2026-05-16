import json
import os
import subprocess
import tempfile
import time
import logging
from pathlib import Path
import win32gui
import win32process
# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


class MuMu非管理员启动器:
    def __init__(self, 播放器路径=None):
        """
        初始化启动器
        :param 播放器路径: MuMuPlayer.exe路径（用于实际启动）
        管理器路径会自动从播放器路径构建
        """
        # 如果没有提供播放器路径，使用默认路径
        self.播放器路径 = Path(播放器路径 or r"D:\Progam Files\Netease\MuMu Player 12\shell\MuMuPlayer.exe")

        # 自动构建管理器路径（替换MuMuPlayer为MuMuManager）
        self.管理器路径 = self._构建管理器路径(self.播放器路径)

        #logging.info(f"播放器路径: {self.播放器路径}")
        #logging.info(f"管理器路径: {self.管理器路径}")

    def _构建管理器路径(self, 播放器路径):
        """
        根据播放器路径自动构建管理器路径
        """
        try:
            # 获取父目录
            父目录 = 播放器路径.parent

            # 获取文件名
            文件名 = 播放器路径.name

            # 替换文件名中的Player为Manager
            新文件名 = 文件名.replace("MuMuPlayer", "MuMuManager")
            if 新文件名 == 文件名:
                # 如果没有替换成功，尝试其他命名模式
                新文件名 = 文件名.replace("Player", "Manager")

            管理器路径 = 父目录 / 新文件名

            # 验证路径是否存在
            if not 管理器路径.exists():
                logging.warning(f"管理器路径不存在，请检查: {管理器路径}")
                # 尝试其他可能的命名
                备选文件名 = "MuMuManager.exe" if 文件名 == "MuMuPlayer.exe" else "Manager.exe"
                备选路径 = 父目录 / 备选文件名
                if 备选路径.exists():
                    return 备选路径

                # 如果都不存在，返回原路径但会有警告
                return 管理器路径

            return 管理器路径
        except Exception as 异常:
            logging.error(f"构建管理器路径失败: {异常}")
            # 返回一个默认的路径（尽管可能不存在）
            默认路径 = 播放器路径.parent / "MuMuManager.exe"
            return 默认路径

    def _通过任务运行(self, 应用路径, 参数=""):
        """
        通过任务计划以非管理员权限运行程序（核心方法）
        """
        # 将Path对象转换为字符串
        应用路径_str = str(应用路径)

        # 创建任务XML内容 - 使用LeastPrivilege避免管理员权限
        xml内容 = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Principals>
    <Principal id="Author">
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Actions Context="Author">
    <Exec>
      <Command>{应用路径_str}</Command>
      <Arguments>{参数}</Arguments>
    </Exec>
  </Actions>
</Task>'''

        # 保存为临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-16') as 临时文件:
            临时文件.write(xml内容)
            xml文件路径 = 临时文件.name

        try:
            # 生成唯一的任务名称
            任务名称 = f"MuMu_Launch_{os.getpid()}_{int(time.time())}"

            # 创建一次性任务（不存储密码）
            创建命令 = f'schtasks /create /tn "{任务名称}" /xml "{xml文件路径}" /f'
            结果 = subprocess.run(创建命令, shell=True, capture_output=True, text=True)
            if 结果.returncode != 0:
                logging.warning(f"创建任务失败: {结果.stderr}")

            # 运行任务
            运行命令 = f'schtasks /run /tn "{任务名称}"'
            结果 = subprocess.run(运行命令, shell=True, capture_output=True, text=True)

            # 删除任务
            删除命令 = f'schtasks /delete /tn "{任务名称}" /f'
            subprocess.run(删除命令, shell=True, capture_output=True, text=True)

            return 结果.returncode == 0
        except Exception as 异常:
            logging.error(f"任务计划执行出错: {异常}")
            return False
        finally:
            # 清理临时文件
            try:
                os.unlink(xml文件路径)
            except Exception as 异常:
                logging.debug(f"清理临时文件失败: {异常}")

    def 安全获取虚拟机信息(self, 虚拟机索引="all"):
        """
        安全获取模拟器信息，避免编码错误
        """
        # 检查管理器路径是否存在
        if not self.管理器路径.exists():
            logging.error(f"管理器路径不存在: {self.管理器路径}")
            return ""

        try:
            # 使用二进制模式捕获输出，避免编码问题
            结果 = subprocess.run(
                [str(self.管理器路径), "info", "--vmindex", str(虚拟机索引)],
                capture_output=True,
                shell=True  # 添加shell=True有时能解决编码问题
            )

            # 尝试多种编码方式解码
            编码列表 = ['gbk', 'utf-8', 'gb2312', 'latin-1']
            for 编码 in 编码列表:
                try:
                    输出 = 结果.stdout.decode(编码, errors='strict')
                    if 输出.strip():
                        return 输出
                except UnicodeDecodeError:
                    continue

            # 如果所有编码都失败，使用ignore模式
            return 结果.stdout.decode('utf-8', errors='ignore')
        except Exception as 异常:
            logging.error(f"获取模拟器信息失败: {异常}")
            return ""

    def 通过索引启动虚拟机(self, 虚拟机索引):
        """
        通过索引启动多开器中的模拟器（非管理员权限）
        """
        # 验证参数
        if not isinstance(虚拟机索引, (int, str)):
            logging.error(f"无效的虚拟机索引类型: {type(虚拟机索引)}")
            return False

        # 检查播放器路径是否存在
        if not self.播放器路径.exists():
            logging.error(f"播放器路径不存在: {self.播放器路径}")
            return False

        # 构建启动命令参数
        参数 = f"-v {虚拟机索引}"

        logging.info(f"尝试启动模拟器 虚拟机索引={虚拟机索引}")
        return self._通过任务运行(self.播放器路径, 参数)

    def 启动多个虚拟机(self, 虚拟机索引列表, 延迟=2):
        """
        启动多个模拟器
        """
        成功计数 = 0
        总数 = len(虚拟机索引列表)

        for 序号, 虚拟机索引 in enumerate(虚拟机索引列表, 1):
            logging.info(f"[{序号}/{总数}] 启动模拟器 {虚拟机索引}")
            if self.通过索引启动虚拟机(虚拟机索引):
                成功计数 += 1
                logging.info(f"模拟器 {虚拟机索引} 启动成功")
                # 如果不是最后一个，添加延时
                if 序号 < 总数 and 延迟 > 0:
                    time.sleep(延迟)
            else:
                logging.error(f"模拟器 {虚拟机索引} 启动失败")

        logging.info(f"启动完成: {成功计数}/{总数} 成功")
        return 成功计数


def MUMU判断模拟器是否完全启动(模拟器启动器,最大尝试次数=1,判断频率=1,判断列表=None,线程事件=None):

    结果列表=[]
    for 多开号 in 判断列表:
        尝试次数 = 0
        是否启动=False
        while 尝试次数 < 最大尝试次数:
            if not 线程事件.is_set():
                结果列表.append(是否启动)
                break
            time.sleep(判断频率)
            尝试次数 += 1
            信息 = 模拟器启动器.安全获取虚拟机信息("all")

            try:
                数据 = json.loads(信息)
                if 数据 and str(多开号) in 数据:
                    if "is_android_started" in 数据[str(多开号)]:
                        是否启动 = 数据[str(多开号)]["is_android_started"]
                        if 是否启动:
                            print(f"模拟器 {多开号} 已成功启动 (尝试 {尝试次数} 次)")
                            time.sleep(判断频率)
                            是否启动 =True
                            break
                        else:
                            print(f"等待模拟器启动... (已等待 {尝试次数} 秒)")
                    else:
                        print(f"等待数据就绪... (已等待 {尝试次数} 秒)")
                else:
                    print(f"等待模拟器信息... (已等待 {尝试次数} 秒)")
            except json.JSONDecodeError:
                print(f"解析JSON数据失败，等待重试... (已等待 {尝试次数} 秒)")
        if 线程事件.is_set():
            结果列表.append(是否启动)
    print(f"结果列表：{结果列表}")
    return 结果列表
def 获取mumu可用端口(模拟器启动器):
    信息 = 模拟器启动器.安全获取虚拟机信息("all")
    端口列表 = []
    try:
        数据 = json.loads(信息)

        for 键,值 in 数据.items():
            if "adb_host_ip" in 值:
                端口 = ("MuMu", 键)
                端口列表.append(str(端口))


    except json.JSONDecodeError:
        print(f"解析JSON数据失败")
    return 端口列表
def 根据pid获取句柄(pid):
    """获取进程的主窗口句柄"""

    def callback(hwnd, result):
        if win32gui.IsWindowVisible(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid and win32gui.GetWindowTextLength(hwnd) > 0:
                result.append(hwnd)
        return True

    result = []
    win32gui.EnumWindows(callback, result)
    return result[0] if result else None
def 根据多开号获取句柄(模拟器启动器,多开号):
    信息 = 模拟器启动器.安全获取虚拟机信息("all")

    数据 = json.loads(信息)

    值 = 数据[多开号]
    if "pid" in 值:
        pid = int(值["pid"])
        hwnd = 根据pid获取句柄(pid)
        return hwnd


def hex_handle_to_decimal(hex_handle):
    """
    将十六进制窗口句柄转换为十进制

    参数:
        hex_handle (str): 十六进制表示的窗口句柄，如 "001B09D8"

    返回:
        int: 十进制表示的窗口句柄
    """
    try:
        # 去除可能的前缀（如果有的话）
        if hex_handle.startswith("0x"):
            hex_handle = hex_handle[2:]

        # 将十六进制字符串转换为十进制整数
        return int(hex_handle, 16)
    except ValueError as e:
        print(f"转换错误: {hex_handle} 不是有效的十六进制字符串")
        return None
if __name__ == "__main__":
    # 演示自定义路径调用
    路径 = r"D:\Program Files\Netease\MuMu Player 12\shell\MuMuPlayer.exe"
    启动器 = MuMu非管理员启动器(路径)
    import threading

    根据pid获取句柄(19060)

    线程事件自定义战斗轴循环 = threading.Event()
    线程事件自定义战斗轴循环.set()
    信息 = 启动器.安全获取虚拟机信息("all")
    print(信息)
    脚本运行 = 0
    if 脚本运行:
        信息 = 启动器.安全获取虚拟机信息("0")
        if 信息:
            print("\n模拟器信息:")
            print(信息)
        else:
            print("无法获取模拟器信息")

        # 启动单个模拟器（索引0）
        print("\n启动模拟器索引0...")
        多开号 = 0
        成功 = 启动器.通过索引启动虚拟机(多开号)
        print(f"启动结果: {'成功' if 成功 else '失败'}")




        # 启动多个模拟器
        print("\n启动模拟器索引2...")
        成功计数 = 启动器.启动多个虚拟机([2], 延迟=3)
        print(f"成功启动了 {成功计数} 个模拟器")
        最大尝试次数 = 60  # 最多等待60秒

        状态列表=MUMU判断模拟器是否完全启动(启动器, 最大尝试次数=最大尝试次数, 判断频率=1, 判断列表=[0, 2],线程事件=线程事件自定义战斗轴循环)
        # 批量启动示例
        # print("\n批量启动1-3号模拟器...")
        # 启动器.启动多个虚拟机([1, 2, 3], 延迟=3)

    print("\n程序执行完成")
    状态列表 = MUMU判断模拟器是否完全启动(启动器, 最大尝试次数=1, 判断频率=1, 判断列表=[0, 2],
                                              线程事件=线程事件自定义战斗轴循环)
    print(状态列表)