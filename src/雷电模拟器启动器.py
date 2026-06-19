import json
import subprocess
import tempfile
import os
import time
import logging
from pathlib import Path
# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


class Leidian非管理员启动器:
    def __init__(self, 播放器路径=None, 管理器路径=None):
        """
        初始化启动器
        :param 播放器路径: dnplayer.exe 路径（用于实际启动模拟器）
        :param 管理器路径: ldconsole.exe 路径（用于获取信息、启动等命令行操作）
        若未提供管理器路径，则自动从播放器路径构建
        """
        # 如果没有提供播放器路径，使用默认路径
        self.播放器路径 = Path(播放器路径 or self._默认播放器路径())
        # 如果没有提供管理器路径，自动构建
        self.管理器路径 = 管理器路径 or self._构建管理器路径(self.播放器路径)

        #logging.info(f"播放器路径: {self.播放器路径}")
        #logging.info(f"管理器路径: {self.管理器路径}")

    def _默认播放器路径(self):
        """返回雷电模拟器常见的默认安装路径"""
        # 常见安装路径（按优先级尝试）
        常见路径 = [
            r"C:\Program Files\Leidian\LDPlayer\dnplayer.exe",
            r"C:\Program Files\LDPlayer\LDPlayer4\dnplayer.exe",
            r"D:\Leidian\LDPlayer\dnplayer.exe",
            r"D:\Program Files\Leidian\LDPlayer\dnplayer.exe",
            r"E:\leidian\LDPlayer9\dnplayer.exe"
        ]
        for 路径 in 常见路径:
            if os.path.exists(路径):
                return 路径
        # 如果都不存在，返回第一个路径（用户可手动修改）
        return 常见路径[0]

    def _构建管理器路径(self, 播放器路径):
        """
        根据播放器路径自动构建管理器路径（ldconsole.exe 或 dnconsole.exe）
        参考：雷电模拟器命令行工具为 ldconsole.exe，也称为 dnconsole.exe[reference:0]
        """
        try:
            目录 = 播放器路径.parent
            # 可能的管理器文件名
            候选名单 = ["ldconsole.exe", "dnconsole.exe"]
            for 文件名 in 候选名单:
                管理器路径 = 目录 / 文件名
                if 管理器路径.exists():
                    return 管理器路径

            # 如果都不存在，尝试将 dnplayer 替换为 ldconsole
            原文件名 = 播放器路径.name
            新文件名 = 原文件名.replace("dnplayer", "ldconsole")
            if 新文件名 == 原文件名:
                新文件名 = 原文件名.replace("player", "console")
            管理器路径 = 目录 / 新文件名

            if not 管理器路径.exists():
                logging.warning(f"管理器路径不存在，请检查: {管理器路径}")
            return 管理器路径
        except Exception as 异常:
            logging.error(f"构建管理器路径失败: {异常}")
            # 返回一个默认的路径（尽管可能不存在）
            默认路径 = 播放器路径.parent / "ldconsole.exe"
            return 默认路径

    def _通过任务运行(self, 应用路径, 参数=""):
        """
        通过任务计划以非管理员权限运行程序（核心方法）
        与 MuMu 启动器相同，可直接复用
        """
        应用路径_str = str(应用路径)
        # 创建任务XML内容 - 使用 LeastPrivilege 避免管理员权限
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
            任务名称 = f"Leidian_Launch_{os.getpid()}_{int(time.time())}"

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
        使用 ldconsole.exe list2 命令，返回逗号分隔的列表[reference:1]
        """
        # 检查管理器路径是否存在
        if not self.管理器路径.exists():
            logging.error(f"管理器路径不存在: {self.管理器路径}")
            return ""

        try:
            # 使用二进制模式捕获输出，避免编码问题
            结果 = subprocess.run(
                [self.管理器路径, "list2"],
                capture_output=True,
                shell=True  # 添加 shell=True 有时能解决编码问题
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

            # 如果所有编码都失败，使用 ignore 模式
            return 结果.stdout.decode('utf-8', errors='ignore')
        except Exception as 异常:
            logging.error(f"获取模拟器信息失败: {异常}")
            return ""

    def 通过索引启动虚拟机(self, 虚拟机索引):
        """
        通过索引启动多开器中的模拟器（非管理员权限）
        使用 ldconsole.exe launch --index 命令[reference:2]
        """
        # 验证参数
        if not isinstance(虚拟机索引, (int, str)):
            logging.error(f"无效的虚拟机索引类型: {type(虚拟机索引)}")
            return False

        # 检查管理器路径是否存在
        if not self.播放器路径.exists():
            logging.error(f"管理器路径不存在: {self.管理器路径}")
            return False

        # 构建启动命令参数
        参数 = f"launch --index {虚拟机索引}"

        logging.info(f"尝试启动模拟器 虚拟机索引={虚拟机索引}")
        # 使用管理器路径启动（ldconsole.exe launch --index）
        return self._通过任务运行(self.管理器路径, 参数)

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

def 雷电判断模拟器是否完全启动(模拟器启动器,最大尝试次数=1,判断频率=1,判断列表=None,线程事件=None):

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
            信息 = 模拟器启动器.安全获取虚拟机信息()

            数据列表 = [行.strip().split(',') for 行 in 信息.split('\n') if 行.strip()]
            if int(数据列表[多开号][4])==1:
                print(f"模拟器 {多开号} 已成功启动 (尝试 {尝试次数} 次)")
                time.sleep(判断频率*3)
                是否启动 = True
                break
            elif int(数据列表[多开号][4])==0:
                print(f"模拟器 {多开号} 未启动 (尝试 {尝试次数} 次)")
            elif int(数据列表[多开号][4])==2:
                print(f"模拟器 {多开号} 启动中 (尝试 {尝试次数} 次)")
        if 线程事件.is_set():
            结果列表.append(是否启动)
    print(f"结果列表：{结果列表}")
    return 结果列表
def 获取雷电可用端口(模拟器启动器):
    信息 = 模拟器启动器.安全获取虚拟机信息()
    数据列表 = [行.strip().split(',') for 行 in 信息.split('\n') if 行.strip()]
    端口列表 = []
    for 数据 in 数据列表:
        if int(数据[4]) == 1 or int(数据[4]) == 2:
            端口号=数据[0]
            端口=("雷电", 端口号)
            端口列表.append(str(端口))
    return 端口列表
if __name__ == "__main__":
    import threading

    启动器 = Leidian非管理员启动器(播放器路径=r"E:\leidian\LDPlayer9\dnplayer.exe")
    列表 = 获取雷电可用端口(启动器)
    print(列表)
    # 获取所有模拟器信息
    信息 = 启动器.安全获取虚拟机信息()
    print(信息)# 索引，标题，顶层窗口句柄，绑定窗口句柄，是否进入android，进程PID，VBox进程PID
    print(type(信息))
    # 假设 信息 是你的多行字符串
    数据列表 = [行.strip().split(',') for 行 in 信息.split('\n') if 行.strip()]
    print(数据列表[1][4])
    print("处理后的数据：")
    for 行数据 in 数据列表:
        print(行数据)

    print(f"\n总行数：{len(数据列表)}")
    print(f"第一行数据：{数据列表[0]}")
    print(f"第一行第二个字段：{数据列表[0][1]}")

    # 启动索引为0的模拟器
    #启动器.通过索引启动虚拟机(1)
    最大尝试次数 = 60
    线程事件自定义战斗轴循环 = threading.Event()
    线程事件自定义战斗轴循环.set()
    print(雷电判断模拟器是否完全启动(启动器, 最大尝试次数=0, 判断频率=1, 判断列表=[1],
                                     线程事件=线程事件自定义战斗轴循环))
    #print(雷电判断模拟器是否完全启动(启动器, 最大尝试次数=最大尝试次数, 判断频率=1, 判断列表=[1],线程事件=线程事件自定义战斗轴循环))
    # 启动多个模拟器
    #启动器.启动多个虚拟机([0, 1, 2], 延迟=3)#E:\leidian\LDPlayer9\dnconsole.exe launch --index 0,E:\leidian\LDPlayer9\ldconsole.exe launch --index 0,ld input tap 373 178
    #input swipe 373 178 373 178 3000
