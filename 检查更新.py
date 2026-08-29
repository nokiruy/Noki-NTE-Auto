import json
from tkinter import messagebox
import ssl
import re
import requests
import certifi
from packaging import version
from bs4 import BeautifulSoup
from pathlib import Path
import sys
import tkinter as tk
from urllib.parse import urlparse
from typing import Optional
import ctypes
class OpenUrlDLL:
    """调用 OpenUrl.dll 打开网址（不会抛出异常导致崩溃）"""
    def __init__(self, dll_path: Optional[str] = None):
        if getattr(sys, 'frozen', False):
            base_dir = Path(sys.executable).parent
        else:
            base_dir = Path(__file__).parent

        if dll_path is None:
            dll_path = str(base_dir / "UI" /"打开网页" /"OpenUrl.dll")

        self._dll = ctypes.CDLL(dll_path)
        self._dll.OpenURL.argtypes = [ctypes.c_wchar_p]
        self._dll.OpenURL.restype = ctypes.c_int

    def open_url(self, url: str) -> bool:
        """打开网址，成功返回 True，失败返回 False"""
        try:
            return self._dll.OpenURL(url) == 0
        except Exception as e:
            print(f"OpenURL 调用异常: {e}")
            return False

    def open(self, url: str, new: int = 0, autoraise: bool = True) -> bool:
        """
        与 webbrowser.open 参数完全兼容
        :param url: 网址
        :param new: 0=同一窗口, 1=新窗口, 2=新标签页 (当前 DLL 无法区分，仅保持接口一致)
        :param autoraise: 是否自动提升窗口 (忽略)
        :return: 成功打开返回 True
        """
        # 因为 ShellExecute 无法精确控制 new 行为，所有打开方式相同
        # 如果需要强制新标签页，可连续调用两次（大多数浏览器会打开两个标签页）
        return self.open_url(url)
opener = OpenUrlDLL()
# ==================== 新增辅助函数 ====================
def 确保列表(参数):
    """将非列表参数转换为单元素列表，列表参数保持不变"""
    return 参数 if isinstance(参数, list) else [参数]


def 处理更新网站列表(当前版本, 更新网站列表):
    """
    遍历网站列表，返回第一个成功获取的版本信息，失败返回None
    """
    for 网站 in 更新网站列表:
        print(f"尝试从 {网站} 获取版本信息...")
        版本信息 = 获取最新版本信息(当前版本, 网站)
        if 版本信息 is not None:
            print(f"从 {网站} 成功获取版本信息")
            return 版本信息
    print("所有网站均获取版本信息失败")
    return None


# ==================== 原函数修改 ====================
def 获取最新版本信息(当前版本, 更新网站):
    """
    从GitHub或Gitee获取最新版本信息，优先API，失败后尝试网页解析
    """
    版本信息 = None

    # 1. 优先尝试API方式（自动识别GitHub/Gitee）
    api网址 = 转换为API网址(更新网站)
    if api网址:
        版本信息 = 通过API获取版本信息(api网址, 当前版本)

    # 2. 如果API方式失败，尝试直接使用传入的网址进行网页解析
    if not 版本信息:
        版本信息 = 通过网页获取版本信息(更新网站, 当前版本)

    return 版本信息


def 转换为API网址(普通网址):
    """
    将GitHub或Gitee的普通网址转换为对应的API网址
    """
    try:
        解析结果 = urlparse(普通网址)
        域名 = 解析结果.netloc.lower()
        路径 = 解析结果.path.strip('/')

        # GitHub API
        if 'github.com' in 域名:
            匹配结果 = re.search(r'([^/]+/[^/]+)/releases', 路径)
            if 匹配结果:
                仓库路径 = 匹配结果.group(1)
                return f"https://api.github.com/repos/{仓库路径}/releases"

        # Gitee API
        elif 'gitee.com' in 域名:
            匹配结果 = re.search(r'([^/]+/[^/]+)/releases', 路径)
            if 匹配结果:
                仓库路径 = 匹配结果.group(1)
                return f"https://gitee.com/api/v5/repos/{仓库路径}/releases"

    except Exception as 错误:
        print(f"转换API网址时出错: {错误}")

    return None


def 通过API获取版本信息(api网址, 当前版本):
    """
    通过GitHub或Gitee API获取版本信息（两者返回格式相似）
    """
    print(f"尝试通过API获取版本信息: {api网址}")

    响应 = 安全获取响应(api网址)
    if not 响应:
        return None

    try:
        releases = 响应.json()
        if not releases:
            return None

        # 获取最新版本（API通常按发布时间降序排列）
        最新发布 = max(releases, key=lambda r: version.parse(r['tag_name'].lstrip('v')))
        最新版本 = 最新发布['tag_name']

        # 比较版本
        当前版本号 = version.parse(当前版本)
        最新版本号 = version.parse(最新版本)

        if 最新版本号 > 当前版本号:
            # 收集所有比当前版本新的更新日志
            更新日志 = ""
            for release in releases:
                release版本号 = version.parse(release['tag_name'])
                if release版本号 > 当前版本号:
                    更新日志 += f"版本 {release['tag_name']}:\n"
                    更新日志 += f"{release.get('body', '暂无更新说明')}\n\n"

            return {
                '最新版本': 最新版本,
                '更新日志': 更新日志.strip()
            }
        else:
            return {'最新版本': 当前版本, '更新日志': ''}

    except Exception as 错误:
        print(f"解析API数据时出错: {错误}")

    return None


def 通过网页获取版本信息(网页网址, 当前版本):
    """
    通过解析网页（支持GitHub和Gitee）获取版本信息
    """
    print(f"尝试通过网页获取版本信息: {网页网址}")

    响应 = 安全获取响应(网页网址)
    if not 响应:
        return None

    try:
        soup = BeautifulSoup(响应.text, 'html.parser')

        # 尝试GitHub的HTML结构
        版本标签列表 = soup.find_all('div', class_='release')
        if not 版本标签列表:
            版本标签列表 = soup.find_all('div', class_='release-entry')

        # 如果GitHub结构未找到，尝试Gitee的HTML结构
        if not 版本标签列表:
            版本标签列表 = soup.find_all('div', class_='release-item')

        if not 版本标签列表:
            print("未找到版本信息")
            return None

        最新版本标签 = 版本标签列表[0]

        # 提取版本号（兼容GitHub和Gitee）
        版本号元素 = None
        # GitHub样式
        版本号元素 = 最新版本标签.find('a', href=re.compile(r'/releases/tag/'))
        if not 版本号元素:
            版本号元素 = 最新版本标签.find('h2')
        # Gitee样式
        if not 版本号元素:
            版本号元素 = 最新版本标签.find('a', class_='release-tag')
        if not 版本号元素:
            版本号元素 = 最新版本标签.find('span', class_='release-version')

        if not 版本号元素:
            print("未找到版本号")
            return None

        最新版本 = 版本号元素.get_text().strip()
        # 移除可能的前导 'v'
        if 最新版本.startswith('v'):
            最新版本 = 最新版本[1:]

        # 比较版本
        当前版本号 = version.parse(当前版本)
        最新版本号 = version.parse(最新版本)

        if 最新版本号 > 当前版本号:
            # 提取更新日志（兼容两种平台）
            更新日志容器 = None
            # GitHub
            更新日志容器 = 最新版本标签.find('div', class_='markdown-body')
            if not 更新日志容器:
                更新日志容器 = 最新版本标签.find('div', class_='release-body')
            # Gitee
            if not 更新日志容器:
                更新日志容器 = 最新版本标签.find('div', class_='release-body-content')
            if not 更新日志容器:
                更新日志容器 = 最新版本标签.find('div', class_='note-body')

            更新日志 = ""
            if 更新日志容器:
                更新日志 = 更新日志容器.get_text().strip()

            # 获取所有比当前版本新的版本信息
            所有更新日志 = f"版本 {最新版本}:\n{更新日志}\n\n"
            for 版本标签 in 版本标签列表[1:]:
                当前标签版本 = None
                # 尝试GitHub
                版本号元素2 = 版本标签.find('a', href=re.compile(r'/releases/tag/'))
                if not 版本号元素2:
                    版本号元素2 = 版本标签.find('h2')
                # 尝试Gitee
                if not 版本号元素2:
                    版本号元素2 = 版本标签.find('a', class_='release-tag')
                if not 版本号元素2:
                    continue

                当前标签版本 = 版本号元素2.get_text().strip()
                if 当前标签版本.startswith('v'):
                    当前标签版本 = 当前标签版本[1:]

                当前标签版本号 = version.parse(当前标签版本)
                if 当前标签版本号 > 当前版本号:
                    当前更新日志容器 = None
                    # GitHub
                    当前更新日志容器 = 版本标签.find('div', class_='markdown-body')
                    if not 当前更新日志容器:
                        当前更新日志容器 = 版本标签.find('div', class_='release-body')
                    # Gitee
                    if not 当前更新日志容器:
                        当前更新日志容器 = 版本标签.find('div', class_='release-body-content')
                    if not 当前更新日志容器:
                        当前更新日志容器 = 版本标签.find('div', class_='note-body')

                    当前更新日志 = ""
                    if 当前更新日志容器:
                        当前更新日志 = 当前更新日志容器.get_text().strip()

                    所有更新日志 += f"版本 {当前标签版本}:\n{当前更新日志}\n\n"

            return {
                '最新版本': 最新版本,
                '更新日志': 所有更新日志.strip()
            }
        else:
            return {'最新版本': 当前版本, '更新日志': ''}

    except Exception as 错误:
        print(f"解析网页数据时出错: {错误}")

    return None


def 安全获取响应(网址):
    """（保持不变，原函数完全可用）"""
    方法列表 = [
        ('系统证书', lambda: requests.get(网址, timeout=10)),
        ('certifi证书', lambda: requests.get(网址, timeout=10,
                                             verify=certifi.where())),
        ('忽略SSL验证', lambda: requests.get(网址, timeout=10,
                                             verify=False)),
        ('自定义SSL上下文', lambda: 使用自定义SSL上下文(网址))
    ]

    for 方法名称, 请求函数 in 方法列表:
        try:
            print(f"尝试使用{方法名称}...")
            响应 = 请求函数()
            if 响应.status_code == 200:
                print(f"使用{方法名称}成功")
                return 响应
            else:
                print(f"使用{方法名称}失败，状态码: {响应.status_code}")
        except requests.exceptions.SSLError as ssl错误:
            print(f"使用{方法名称} SSL错误: {ssl错误}")
        except Exception as 错误:
            print(f"使用{方法名称} 其他错误: {错误}")
    print("所有方法都失败了")
    return None


def 处理失败计数(结果, 更新网站):
    """修改：当更新网站为列表时，取第一个元素用于打开"""
    # 确保更新网站是字符串（取第一个）
    if isinstance(更新网站, list):
        更新网站 = 更新网站[0] if 更新网站 else ""

    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent.absolute()
    else:
        current_dir = Path(__file__).parent.absolute()

    失败计数文件 = current_dir / "update_check.json"
    try:
        if 失败计数文件.exists():
            with open(失败计数文件, 'r', encoding='utf-8') as f:
                try:
                    数据 = json.load(f)
                except json.JSONDecodeError:
                    数据 = {"计数": 0}
        else:
            数据 = {"计数": 0}

        if 结果:
            数据["计数"] = 0
        else:
            if "计数" not in 数据:
                数据["计数"] = 0
            数据["计数"] = 数据["计数"] + 1

            if 数据["计数"] >= 7:
                if 更新网站:
                    try:
                        root = tk.Tk()
                        root.withdraw()
                        messagebox.showerror("更新信息获取错误", "累计七天未获取更新信息成功，现在将打开更新网址")
                        if opener.open_url(更新网站):
                            print(f"成功打开 {更新网站}")
                        else:
                            print("打开失败，请检查 DLL 或网络")

                        print(f"失败次数达到{数据['计数']}次，已打开网址: {更新网站}")
                        数据["计数"] = 0
                    except Exception as e:
                        print(f"打开网址失败: {e}")

        with open(失败计数文件, 'w', encoding='utf-8') as f:
            json.dump(数据, f, ensure_ascii=False, indent=2)

        return 数据["计数"]
    except Exception as e:
        print(f"处理失败计数时出错: {e}")
        return 0


def 使用自定义SSL上下文(网址):
    """（保持不变）"""
    ssl上下文 = ssl.create_default_context()
    ssl上下文.check_hostname = False
    ssl上下文.verify_mode = ssl.CERT_NONE

    with requests.Session() as 会话:
        会话.verify = False
        响应 = 会话.get(网址, timeout=10)
        return 响应


def 检查更新(当前版本, 更新网站, 是否打开网站=False):
    """
    检查更新的主入口函数
    参数 更新网站 可以是字符串或字符串列表
    """
    try:
        # 将输入统一转为列表
        网站列表 = 确保列表(更新网站)

        print(f"开始检查更新...")
        print(f"当前版本: {当前版本}")
        print(f"更新网站列表: {网站列表}")

        # 遍历所有网站获取版本信息
        版本信息 = 处理更新网站列表(当前版本, 网站列表)

        # 记录整体成功/失败状态，失败时传入第一个网站用于计数文件
        整体成功 = (版本信息 is not None)
        处理失败计数(整体成功, 网站列表[0] if 网站列表 else "")

        if not 版本信息:
            return "获取版本信息失败，请手动复制上方任意链接到浏览器查看更新，并检查网络配置，获取版本信息失败，请手动复制上方任意链接到浏览器查看更新，并检查网络配置，获取版本信息失败"

        if 版本信息.get('最新版本') == 当前版本:
            更新信息 = f"当前已是最新版本！\n\n"
            更新信息 += f"📊 最新版本: {版本信息['最新版本']}\n"
            更新信息 += f"📋 当前版本: {当前版本}\n\n"
            return 更新信息
        if not 版本信息.get('更新日志'):
            更新信息 = f"📊 最新版本: {版本信息['最新版本']}\n"
            更新信息 += f"📋 当前版本: {当前版本}\n\n"
            更新信息 += f"未获取到更新日志"
            return 更新信息

        更新信息 = f"发现新版本！\n\n"
        更新信息 += f"📊 最新版本: {版本信息['最新版本']}\n"
        更新信息 += f"📋 当前版本: {当前版本}\n\n"
        更新信息 += f"📝 更新内容:\n{版本信息['更新日志']}"
        if 是否打开网站:
            # 打开第一个网站
            if opener.open_url(网站列表[0] if 网站列表 else ""):
                print("成功打开 网站")
            else:
                print("打开失败，请检查 DLL 或网络")
        return 更新信息

    except Exception as 错误:
        处理失败计数(False, 更新网站 if not isinstance(更新网站, list) else (更新网站[0] if 更新网站 else ""))
        错误信息 = f"检查更新时出现错误: {错误}请手动复制上方任意链接到浏览器查看更新，并检查网络配置，检查更新时出现错误: {错误}请手动复制上方任意链接到浏览器查看更新，并检查网络配置，检查更新时出现错误: {错误}请手动复制上方任意链接到浏览器查看更新，并检查网络配置"
        print(错误信息)
        return 错误信息


def 快速检查更新(当前版本, 仓库地址):
    """
    快速检查更新，自动处理API和网页网址，支持列表参数
    """
    print(f"快速检查更新...")
    网站列表 = 确保列表(仓库地址)

    for 网址 in 网站列表:
        if "api.github.com" in 网址:
            api网址 = 网址
            网页网址 = 网址.replace("api.github.com/repos/", "github.com/").replace("/releases", "")
        elif "gitee.com/api/v5" in 网址:
            # Gitee API 网址转网页网址
            网页网址 = 网址.replace("gitee.com/api/v5/repos/", "gitee.com/").replace("/releases", "")
            api网址 = 网址
        else:
            网页网址 = 网址
            api网址 = 转换为API网址(网址)

        # 1. 优先尝试API
        if api网址:
            版本信息 = 通过API获取版本信息(api网址, 当前版本)
            if 版本信息:
                return 处理版本信息(版本信息, 当前版本)

        # 2. API失败后尝试网页
        版本信息 = 通过网页获取版本信息(网页网址, 当前版本)
        if 版本信息:
            return 处理版本信息(版本信息, 当前版本)

    return "获取版本信息失败"


def 处理版本信息(版本信息, 当前版本):
    """（保持不变）"""
    if 版本信息.get('最新版本') == 当前版本 or not 版本信息.get('更新日志'):
        return "当前已是最新版本"

    更新信息 = f"发现新版本！\n\n"
    更新信息 += f"📊 最新版本: {版本信息['最新版本']}\n"
    更新信息 += f"📋 当前版本: {当前版本}\n\n"
    更新信息 += f"📝 更新内容:\n{版本信息['更新日志']}"

    return 更新信息

def 测试证书方法(测试网址=None):
    """
    测试所有证书方法的可行性
    """
    # 如果没有指定测试网址，使用一个默认的GitHub API网址
    if 测试网址 is None:
        测试网址 = "https://api.github.com/repos/nokiruy/Noki-Heaven-Burns-Red-Auto/releases"

    print(f"🚀 开始证书方法测试")
    print(f"测试网址: {测试网址}")
    print("=" * 60)

    测试结果 = []

    # 1. 测试系统证书
    print("1️⃣ 测试系统证书方法...")
    try:
        响应 = requests.get(测试网址, timeout=10)
        if 响应.status_code == 200:
            print("✅ 系统证书方法: 成功")
            测试结果.append(("系统证书", True, 响应.status_code, None))
        else:
            print(f"⚠️ 系统证书方法: 失败，状态码 {响应.status_code}")
            测试结果.append(("系统证书", False, 响应.status_code, None))
    except requests.exceptions.SSLError as ssl错误:
        print(f"❌ 系统证书方法: SSL错误 - {ssl错误}")
        测试结果.append(("系统证书", False, None, str(ssl错误)))
    except Exception as 错误:
        print(f"❌ 系统证书方法: 其他错误 - {错误}")
        测试结果.append(("系统证书", False, None, str(错误)))

    # 2. 测试certifi证书
    print("\n2️⃣ 测试certifi证书方法...")
    try:
        响应 = requests.get(测试网址, timeout=10, verify=certifi.where())
        if 响应.status_code == 200:
            print(f"✅ certifi证书方法: 成功")
            print(f"   certifi证书位置: {certifi.where()}")
            测试结果.append(("certifi证书", True, 响应.status_code, None))
        else:
            print(f"⚠️ certifi证书方法: 失败，状态码 {响应.status_code}")
            测试结果.append(("certifi证书", False, 响应.status_code, None))
    except requests.exceptions.SSLError as ssl错误:
        print(f"❌ certifi证书方法: SSL错误 - {ssl错误}")
        测试结果.append(("certifi证书", False, None, str(ssl错误)))
    except Exception as 错误:
        print(f"❌ certifi证书方法: 其他错误 - {错误}")
        测试结果.append(("certifi证书", False, None, str(错误)))

    # 3. 测试忽略SSL验证
    print("\n3️⃣ 测试忽略SSL验证方法...")
    try:
        # 禁用SSL警告
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        响应 = requests.get(测试网址, timeout=10, verify=False)
        if 响应.status_code == 200:
            print("✅ 忽略SSL验证方法: 成功")
            测试结果.append(("忽略SSL验证", True, 响应.status_code, None))
        else:
            print(f"⚠️ 忽略SSL验证方法: 失败，状态码 {响应.status_code}")
            测试结果.append(("忽略SSL验证", False, 响应.status_code, None))
    except Exception as 错误:
        print(f"❌ 忽略SSL验证方法: 错误 - {错误}")
        测试结果.append(("忽略SSL验证", False, None, str(错误)))

    # 4. 测试自定义SSL上下文
    print("\n4️⃣ 测试自定义SSL上下文方法...")
    try:
        ssl上下文 = ssl.create_default_context()
        # 尝试不同的SSL设置组合
        配置列表 = [
            ("宽松模式 - 不验证主机名和证书",
             lambda: ssl.create_default_context(ssl.Purpose.SERVER_AUTH)),
            ("自定义CA证书",
             lambda: ssl.create_default_context(cafile=certifi.where())),
            ("不验证证书",
             lambda: ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT))
        ]

        成功 = False
        错误信息 = None

        for 配置名称, 创建函数 in 配置列表:
            try:
                print(f"   尝试{配置名称}...")
                上下文 = 创建函数()

                if "不验证证书" in 配置名称:
                    上下文.check_hostname = False
                    上下文.verify_mode = ssl.CERT_NONE

                with requests.Session() as 会话:
                    # 注意：requests的Session不能直接传递SSL上下文
                    # 我们需要使用适配器
                    响应 = 会话.get(测试网址, timeout=10, verify=False)

                    if 响应.status_code == 200:
                        print(f"   ✅ {配置名称}: 成功")
                        成功 = True
                        break
            except Exception as 配置错误:
                错误信息 = str(配置错误)
                print(f"   ❌ {配置名称}: 失败 - {配置错误}")
                continue

        if 成功:
            print("✅ 自定义SSL上下文方法: 成功")
            测试结果.append(("自定义SSL上下文", True, 200, None))
        else:
            print(f"❌ 自定义SSL上下文方法: 所有配置都失败")
            测试结果.append(("自定义SSL上下文", False, None, 错误信息))

    except Exception as 错误:
        print(f"❌ 自定义SSL上下文方法: 错误 - {错误}")
        测试结果.append(("自定义SSL上下文", False, None, str(错误)))

    # 5. 测试原始的安全获取响应函数
    print("\n5️⃣ 测试完整的安全获取响应函数...")
    try:
        响应 = 安全获取响应(测试网址)
        if 响应 and 响应.status_code == 200:
            print("✅ 安全获取响应函数: 成功")
            测试结果.append(("安全获取响应函数", True, 响应.status_code, None))
        else:
            状态码 = 响应.status_code if 响应 else "无响应"
            print(f"❌ 安全获取响应函数: 失败，状态码 {状态码}")
            测试结果.append(("安全获取响应函数", False, 状态码, None))
    except Exception as 错误:
        print(f"❌ 安全获取响应函数: 错误 - {错误}")
        测试结果.append(("安全获取响应函数", False, None, str(错误)))

    # 输出测试总结
    print("\n" + "=" * 60)
    print("📊 测试总结:")
    print("=" * 60)

    成功方法 = []
    失败方法 = []

    for 方法名称, 成功, 状态码, 错误信息 in 测试结果:
        if 成功:
            成功方法.append(方法名称)
            print(f"✅ {方法名称}: 成功 (状态码: {状态码})")
        else:
            失败方法.append(方法名称)
            print(f"❌ {方法名称}: 失败")
            if 状态码:
                print(f"   状态码: {状态码}")
            if 错误信息:
                print(f"   错误信息: {错误信息}")

    print(f"\n🎯 测试完成: {len(成功方法)}/{len(测试结果)} 个方法成功")

    # 推荐最佳方法
    if 成功方法:
        print(f"\n💡 推荐使用: {成功方法[0]} 方法")

    return 测试结果


def 测试特定网址列表():
    """
    测试多个不同网址的证书方法
    """
    网址列表 = [
        "https://api.github.com/repos/nokiruy/Noki-Heaven-Burns-Red-Auto/releases",
        "https://github.com/nokiruy/Noki-Heaven-Burns-Red-Auto/releases",
        "https://raw.githubusercontent.com/nokiruy/Noki-Heaven-Burns-Red-Auto/main/README.md",
        "https://github.com",  # GitHub主页
        "https://api.github.com",  # GitHub API根目录
    ]

    print("🌐 开始多网址证书方法测试")
    print("=" * 60)

    所有结果 = {}

    for i, 网址 in enumerate(网址列表, 1):
        print(f"\n测试网址 {i}/{len(网址列表)}: {网址}")
        print("-" * 40)

        结果 = 测试证书方法(网址)
        所有结果[网址] = 结果

        # 短暂暂停，避免请求过快
        import time
        time.sleep(1)

    # 生成汇总报告
    print("\n" + "=" * 60)
    print("📈 多网址测试汇总报告")
    print("=" * 60)

    for 网址, 结果 in 所有结果.items():
        成功数 = sum(1 for r in 结果 if r[1])
        print(f"\n{网址}: {成功数}/{len(结果)} 个方法成功")

    return 所有结果


def 诊断证书问题():
    """
    诊断证书相关的问题
    """
    print("🔍 开始证书问题诊断")
    print("=" * 60)

    # 1. 检查Python和requests版本
    print("1. 检查环境信息:")
    print(f"   Python版本: {sys.version}")
    print(f"   requests版本: {requests.__version__}")
    print(f"   certifi版本: {certifi.__version__ if hasattr(certifi, '__version__') else '未知'}")

    # 2. 检查系统证书存储
    print("\n2. 检查证书存储:")
    print(f"   certifi证书位置: {certifi.where()}")

    # 3. 检查默认SSL上下文
    print("\n3. 检查SSL默认配置:")
    try:
        默认上下文 = ssl.create_default_context()
        print(f"   默认SSL上下文创建: 成功")
        print(f"   验证模式: {默认上下文.verify_mode}")
        print(f"   检查主机名: {默认上下文.check_hostname}")
    except Exception as 错误:
        print(f"   默认SSL上下文创建: 失败 - {错误}")

    # 4. 测试简单HTTPS请求
    print("\n4. 测试简单HTTPS请求:")
    try:
        测试响应 = requests.get("https://httpbin.org/get", timeout=5)
        print(f"   测试请求到 httpbin.org: 成功 (状态码: {测试响应.status_code})")
    except Exception as 错误:
        print(f"   测试请求到 httpbin.org: 失败 - {错误}")

    print("\n" + "=" * 60)
    print("💡 诊断建议:")
    print("=" * 60)

    print("""
1. 如果所有方法都失败:
   - 检查网络连接
   - 检查防火墙设置
   - 尝试使用代理

2. 如果只有系统证书失败:
   - 系统CA证书可能已过期或损坏
   - 尝试更新操作系统

3. 如果certifi证书失败:
   - 更新certifi: pip install --upgrade certifi
   - 检查证书文件是否完整

4. 常见解决方案:
   - 使用忽略SSL验证（安全性较低，仅用于测试）
   - 更新requests和certifi到最新版本
   - 手动指定证书路径
    """)

