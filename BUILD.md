# 构建说明

## 构建环境

- Windows 10/11 x64
- Python 3.12 x64，并可通过 `py -3.12` 调用
- Visual Studio 2022 或更高版本
  - 安装“使用 C++ 的桌面开发”工作负载
  - 包含 MSVC x64 工具链和 Windows SDK
- 首次构建需要联网下载 Python 依赖

## 一键构建

在仓库根目录打开 PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1 -Clean
```

脚本会依次完成：

1. 在 `build/venv` 创建隔离的 Python 3.12 环境。
2. 安装 `requirements-build.txt` 中的运行和打包依赖。
3. 导入 `src/main.py`，提前检查缺失依赖。
4. 使用 MSVC x64 编译：
   - `ToastLib.dll`
   - `mutedll.dll`
   - `OpenUrl.dll`
   - `Noki_NTE_Auto_Launcher.exe`
5. 使用 PyInstaller 将 `src/main.py` 打包为单文件 GUI 程序。
6. 按程序的相对路径约定复制 UI、图片和配置文件。

## 增量构建

依赖已经安装后：

```powershell
.\build.ps1 -SkipInstall
```

只重新编译 C++ 原生组件：

```powershell
.\build.ps1 -SkipInstall -SkipPackage
```

只重新打包 Python 主程序：

```powershell
.\build.ps1 -SkipInstall -SkipNative
```

## 发布目录

构建成功后产物位于：

```text
release/
├─ Noki_NTE_Auto_Launcher.exe
├─ 外置配置文件夹/
└─ dist/
   ├─ Noki_NTE_Auto.exe
   ├─ UI/
   ├─ 异环图片/
   └─ *.json / app_path.txt / 使用说明书.md
```

正常发布时应打包整个 `release` 目录，不能只复制单独的 EXE。

## 源码目录

全部 Python 源码位于 `src/`。开发环境直接运行：

```powershell
.\build\venv\Scripts\python.exe .\src\main.py
```

`src/project_paths.py` 负责统一解析资源根目录：

- 源码运行时指向仓库根目录。
- PyInstaller 打包后指向主 EXE 所在的 `dist` 目录。

## 测试说明

正式运行会请求管理员权限。自动化冒烟测试可以临时设置：

```powershell
$env:NOKI_DEV_SKIP_ADMIN = "1"
.\release\Noki_NTE_Auto_Launcher.exe
Remove-Item Env:NOKI_DEV_SKIP_ADMIN
```

`NOKI_DEV_SKIP_ADMIN` 仅用于本地构建测试，不应写入用户系统环境变量。
