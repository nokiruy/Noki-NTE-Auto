import json
import webbrowser
from tkinter import messagebox

import requests
import certifi
import ssl
import re
from packaging import version
from bs4 import BeautifulSoup
from pathlib import Path
import sys

import tkinter as tk


def 获取最新版本信息(当前版本, 更新网站):
    """
    从GitHub获取最新版本信息，优先API，失败后尝试网页解析
    """
    版本信息 = None

    # 1. 优先尝试API方式
    if "api.github.com" not in 更新网站:
        # 如果是普通网址，转换为API网址
        api网址 = 转换为API网址(更新网站)
        if api网址:
            版本信息 = 通过API获取版本信息(api网址, 当前版本)

    # 2. 如果API方式失败或没有API网址，尝试直接使用传入的网址
    if not 版本信息:
        版本信息 = 通过网页获取版本信息(更新网站, 当前版本)

    return 版本信息


def 转换为API网址(普通网址):
    """
    将GitHub普通网址转换为API网址
    """
    try:
        # 提取仓库路径
        匹配结果 = re.search(r'github\.com/([^/]+/[^/]+)', 普通网址)
        if 匹配结果:
            仓库路径 = 匹配结果.group(1)
            return f"https://api.github.com/repos/{仓库路径}/releases"
    except Exception as 错误:
        print(f"转换API网址时出错: {错误}")

    return None


def 通过API获取版本信息(api网址, 当前版本):
    """
    通过GitHub API获取版本信息
    """
    print(f"尝试通过API获取版本信息: {api网址}")

    响应 = 安全获取响应(api网址)
    if not 响应:
        return None

    try:
        # 解析JSON数据
        releases = 响应.json()
        if not releases:
            return None

        # 获取最新版本
        最新版本 = releases[0]['tag_name']

        # 比较版本
        当前版本号 = version.parse(当前版本)
        最新版本号 = version.parse(最新版本)

        if 最新版本号 > 当前版本号:
            # 获取更新日志
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
    通过解析GitHub网页获取版本信息
    """
    print(f"尝试通过网页获取版本信息: {网页网址}")

    响应 = 安全获取响应(网页网址)
    if not 响应:
        return None

    try:
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(响应.text, 'html.parser')

        # 查找最新版本标签
        版本标签列表 = soup.find_all('div', class_='release')
        if not 版本标签列表:
            版本标签列表 = soup.find_all('div', class_='release-entry')

        if not 版本标签列表:
            print("未找到版本信息")
            return None

        # 获取最新版本信息
        最新版本标签 = 版本标签列表[0]

        # 提取版本号
        版本号元素 = 最新版本标签.find('a', href=re.compile(r'/releases/tag/'))
        if not 版本号元素:
            版本号元素 = 最新版本标签.find('h2')

        if not 版本号元素:
            print("未找到版本号")
            return None

        最新版本 = 版本号元素.get_text().strip()

        # 比较版本
        当前版本号 = version.parse(当前版本)
        最新版本号 = version.parse(最新版本)

        if 最新版本号 > 当前版本号:
            # 提取更新日志
            更新日志容器 = 最新版本标签.find('div', class_='markdown-body')
            if not 更新日志容器:
                更新日志容器 = 最新版本标签.find('div', class_='release-body')

            更新日志 = ""
            if 更新日志容器:
                更新日志 = 更新日志容器.get_text().strip()

            # 获取所有比当前版本新的版本信息
            所有更新日志 = f"版本 {最新版本}:\n{更新日志}\n\n"
            for i, 版本标签 in enumerate(版本标签列表[1:], start=1):
                当前版本标签号元素 = 版本标签.find('a', href=re.compile(r'/releases/tag/'))
                if 当前版本标签号元素:
                    当前标签版本 = 当前版本标签号元素.get_text().strip()
                    当前标签版本号 = version.parse(当前标签版本)

                    if 当前标签版本号 > 当前版本号:
                        当前更新日志容器 = 版本标签.find('div', class_='markdown-body')
                        if not 当前更新日志容器:
                            当前更新日志容器 = 版本标签.find('div', class_='release-body')

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
    """
    安全获取HTTP响应，成功获取后立即停止
    """
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


# 检查文件是否存在
def 处理失败计数(结果, 更新网站):
    # 获取文件路径
    if getattr(sys, 'frozen', False):
        current_dir = Path(sys.executable).parent.absolute()
    else:
        current_dir = Path(__file__).parent.absolute()

    失败计数文件 = current_dir / "update_check.json"
    try:
        # 如果文件存在，读取当前计数
        if 失败计数文件.exists():
            with open(失败计数文件, 'r', encoding='utf-8') as f:
                try:
                    数据 = json.load(f)
                except json.JSONDecodeError:
                    # 如果文件内容不是有效的JSON，则重置数据
                    数据 = {"计数": 0}
        else:
            # 如果文件不存在，初始化数据
            数据 = {"计数": 0}

        # 根据结果更新计数
        if 结果:
            数据["计数"] = 0
        else:
            # 确保有"计数"键
            if "计数" not in 数据:
                数据["计数"] = 0
            数据["计数"] = 数据["计数"] + 1

            # 检查失败计数是否大于等于7
            if 数据["计数"] >= 7:
                # 打开网址
                if 更新网站:
                    try:
                        root = tk.Tk()
                        root.withdraw()
                        messagebox.showerror("更新信息获取错误", "累计七天未获取更新信息成功，现在将打开更新网址")
                        webbrowser.open(更新网站)
                        print(f"失败次数达到{数据['计数']}次，已打开网址: {更新网站}")
                        # 归零计数
                        数据["计数"] = 0
                    except Exception as e:
                        print(f"打开网址失败: {e}")



        # 写入json文件
        with open(失败计数文件, 'w', encoding='utf-8') as f:
            json.dump(数据, f, ensure_ascii=False, indent=2)

        return 数据["计数"]

    except Exception as e:
        print(f"处理失败计数时出错: {e}")
        # 出错时返回0或适当的值
        return 0


def 使用自定义SSL上下文(网址):
    """
    使用自定义的SSL上下文
    """
    ssl上下文 = ssl.create_default_context()
    ssl上下文.check_hostname = False
    ssl上下文.verify_mode = ssl.CERT_NONE

    with requests.Session() as 会话:
        会话.verify = False
        响应 = 会话.get(网址, timeout=10)
        return 响应


def 检查更新(当前版本, 更新网站,是否打开网站=False):
    """
    检查更新的主入口函数
    """
    try:
        print(f"开始检查更新...")
        print(f"当前版本: {当前版本}")
        print(f"更新网站: {更新网站}")






        # 获取最新版本信息
        版本信息 = 获取最新版本信息(当前版本, 更新网站)
        处理失败计数(版本信息, 更新网站)

        if not 版本信息:
            return "获取版本信息失败，请手动复制上方任意链接到浏览器查看更新，并检查网络配置，获取版本信息失败，请手动复制上方任意链接到浏览器查看更新，并检查网络配置，获取版本信息失败"

        if 版本信息.get('最新版本') == 当前版本:
            更新信息 = f"当前已是最新版本！\n\n"
            更新信息 += f"📊 最新版本: {版本信息['最新版本']}\n"
            更新信息 += f"📋 当前版本: {当前版本}\n\n"
            return 更新信息
        if  not 版本信息.get('更新日志'):

            更新信息 = f"📊 最新版本: {版本信息['最新版本']}\n"
            更新信息 += f"📋 当前版本: {当前版本}\n\n"
            更新信息 += f"未获取到更新日志"
            return 更新信息

        # 生成更新信息
        更新信息 = f"发现新版本！\n\n"
        更新信息 += f"📊 最新版本: {版本信息['最新版本']}\n"
        更新信息 += f"📋 当前版本: {当前版本}\n\n"
        更新信息 += f"📝 更新内容:\n{版本信息['更新日志']}"
        if 是否打开网站:
            webbrowser.open(更新网站)
        return 更新信息

    except Exception as 错误:
        处理失败计数(False, 更新网站)

        错误信息 = f"检查更新时出现错误: {错误}请手动复制上方任意链接到浏览器查看更新，并检查网络配置，检查更新时出现错误: {错误}请手动复制上方任意链接到浏览器查看更新，并检查网络配置，检查更新时出现错误: {错误}请手动复制上方任意链接到浏览器查看更新，并检查网络配置"
        print(错误信息)
        return 错误信息


def 快速检查更新(当前版本, 仓库地址):
    """
    快速检查更新，自动处理API和网页网址
    """
    print(f"快速检查更新...")

    # 如果传入的是API网址，直接使用
    if "api.github.com" in 仓库地址:
        api网址 = 仓库地址
        网页网址 = 仓库地址.replace("api.github.com/repos/", "github.com/").replace("/releases", "")
    else:
        # 否则尝试构建API网址
        网页网址 = 仓库地址
        api网址 = 转换为API网址(仓库地址)

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
    """
    处理版本信息并生成更新消息
    """
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

# 如果直接运行此脚本，执行测试
if __name__ == "__main__":
    def 测试失败计数功能():
        """
        测试函数：模拟多次失败和成功的情况
        """
        # 测试用的网址
        测试网址 = "https://github.com/nokiruy/Noki-Heaven-Burns-Red-Auto/releases"

        print("开始测试失败计数功能...")
        print("=" * 50)

        # 模拟多次失败
        print("模拟连续失败:")
        for i in range(1, 11):
            当前计数 = 处理失败计数(False, 测试网址)
            print(f"  第{i}次失败，当前计数: {当前计数}")

            if i % 7 == 0:
                print(f"  → 已触发第{i}次失败，应已打开网址并重置计数")

        print("-" * 30)

        # 模拟一次成功（应重置计数）
        print("模拟一次成功:")
        最终计数 = 处理失败计数(True, 测试网址)
        print(f"  成功处理后，当前计数: {最终计数}")

        print("-" * 30)

        # 再次模拟失败
        print("再次模拟失败:")
        for i in range(1, 4):
            当前计数 = 处理失败计数(False, 测试网址)
            print(f"  第{i}次失败，当前计数: {当前计数}")

        print("=" * 50)
        print("测试完成!")

        # 读取并显示最终文件内容
        if getattr(sys, 'frozen', False):
            current_dir = Path(sys.executable).parent.absolute()
        else:
            current_dir = Path(__file__).parent.absolute()

        失败计数文件 = current_dir / "update_check.json"
        if 失败计数文件.exists():
            with open(失败计数文件, 'r', encoding='utf-8') as f:
                try:
                    最终数据 = json.load(f)
                    print(f"最终文件内容: {最终数据}")
                except json.JSONDecodeError:
                    print("文件内容不是有效的JSON")
    测试失败计数功能()
"""if __name__ == "__main__":
    # 设置当前版本
    当前版本 = "v3.68.84"

    print("GitHub Release更新检查工具")
    print(f"当前版本: {当前版本}")
    print()

    # 示例1：使用API网址
    print("=" * 50)
    print("示例1: 使用API网址")
    print("=" * 50)
    api网址 = "https://api.github.com/repos/nokiruy/Noki-Heaven-Burns-Red-Auto/releases"
    更新信息1 = 快速检查更新(当前版本, api网址)
    print(更新信息1)

    # 示例2：使用网页网址（自动转换为API）
    print("\n" + "=" * 50)
    print("示例2: 使用网页网址")
    print("=" * 50)
    网页网址 = "https://github.com/nokiruy/Noki-Heaven-Burns-Red-Auto/releases"
    更新信息2 = 快速检查更新(当前版本, 网页网址)
    print(更新信息2)

    # 示例3：使用完整函数
    print("\n" + "=" * 50)
    print("示例3: 使用完整函数")
    print("=" * 50)
    网页网址 = "https://github.com/nokiruy/Noki-Heaven-Burns-Red-Auto/releases"
    更新信息3 = 检查更新(当前版本, 网页网址)
    print(更新信息3)
if __name__ == "__main__":
    import sys

    print("🔧 GitHub更新检查工具 - 证书方法测试")
    print("=" * 60)

    # 让用户选择测试模式
    print("请选择测试模式:")
    print("1. 测试单个网址")
    print("2. 测试多个网址")
    print("3. 诊断证书问题")
    print("4. 运行所有测试")

    选择 = input("请输入选择 (1-4): ").strip()

    if 选择 == "1":
        # 测试单个网址
        测试网址 = input("请输入测试网址 (直接回车使用默认): ").strip()
        if not 测试网址:
            测试网址 = None
        测试证书方法(测试网址)

    elif 选择 == "2":
        # 测试多个网址
        测试特定网址列表()

    elif 选择 == "3":
        # 诊断证书问题
        诊断证书问题()

    elif 选择 == "4":
        # 运行所有测试
        print("\n" + "=" * 60)
        print("开始所有测试")
        print("=" * 60)

        # 1. 测试单个网址
        print("\n📋 测试1: 单个网址测试")
        测试证书方法()

        # 2. 测试多个网址
        print("\n\n📋 测试2: 多网址测试")
        测试特定网址列表()

        # 3. 诊断证书问题
        print("\n\n📋 测试3: 证书问题诊断")
        诊断证书问题()

    else:
        print("无效选择，使用默认测试")
        测试证书方法()"""