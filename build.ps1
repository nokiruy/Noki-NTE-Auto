[CmdletBinding()]
param(
    [switch]$Clean,
    [switch]$SkipInstall,
    [switch]$SkipNative,
    [switch]$SkipPackage
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Utf8Encoding = New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding = $Utf8Encoding
[Console]::OutputEncoding = $Utf8Encoding
$OutputEncoding = $Utf8Encoding
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
& chcp.com 65001 | Out-Null

$Root = [IO.Path]::GetFullPath($PSScriptRoot)
$SourceRoot = Join-Path $Root "src"
$BuildRoot = Join-Path $Root "build"
$ReleaseRoot = Join-Path $Root "release"
$DistRoot = Join-Path $ReleaseRoot "dist"
$VenvRoot = Join-Path $BuildRoot "venv"
$Python = Join-Path $VenvRoot "Scripts\python.exe"

function Remove-WorkspaceDirectory {
    param([Parameter(Mandatory)][string]$Path)

    $FullPath = [IO.Path]::GetFullPath($Path)
    $WorkspacePrefix = $Root.TrimEnd("\") + "\"
    if (-not $FullPath.StartsWith($WorkspacePrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "拒绝删除工作区以外的目录: $FullPath"
    }
    if (Test-Path -LiteralPath $FullPath) {
        Remove-Item -LiteralPath $FullPath -Recurse -Force
    }
}

function Copy-ReleaseItem {
    param(
        [Parameter(Mandatory)][string]$Source,
        [Parameter(Mandatory)][string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        throw "发布文件不存在: $Source"
    }
    if ((Get-Item -LiteralPath $Source).PSIsContainer -and (Test-Path -LiteralPath $Destination)) {
        Remove-WorkspaceDirectory $Destination
    }
    $Parent = Split-Path -Parent $Destination
    if ($Parent) {
        New-Item -ItemType Directory -Path $Parent -Force | Out-Null
    }
    Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
}

function Get-Sha256 {
    param([Parameter(Mandatory)][string]$Path)

    $ResolvedPath = [IO.Path]::GetFullPath($Path)
    $Sha256 = [Security.Cryptography.SHA256]::Create()
    $Stream = [IO.File]::OpenRead($ResolvedPath)
    try {
        $HashBytes = $Sha256.ComputeHash($Stream)
        $Hash = -join ($HashBytes | ForEach-Object { $_.ToString("X2") })
    }
    finally {
        $Stream.Dispose()
        $Sha256.Dispose()
    }

    [PSCustomObject]@{
        Algorithm = "SHA256"
        Hash = $Hash
        Path = $ResolvedPath
    }
}

if ($Clean) {
    Remove-WorkspaceDirectory $BuildRoot
    Remove-WorkspaceDirectory $ReleaseRoot
}

New-Item -ItemType Directory -Path $BuildRoot, $ReleaseRoot, $DistRoot -Force | Out-Null

if (-not (Test-Path -LiteralPath $Python)) {
    Write-Host "[1/5] 创建 Python 3.12 构建环境"
    & py -3.12 -m venv $VenvRoot
    if ($LASTEXITCODE -ne 0) {
        throw "创建虚拟环境失败"
    }
}

if (-not $SkipInstall) {
    Write-Host "[2/5] 安装 Python 运行与打包依赖"
    & $Python -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        throw "升级 pip 失败"
    }
    & $Python -m pip install -r (Join-Path $Root "requirements-build.txt")
    if ($LASTEXITCODE -ne 0) {
        throw "安装依赖失败"
    }
}

Write-Host "[3/5] 验证源码依赖可导入"
& $Python -B -c "import sys; sys.path.insert(0, r'$SourceRoot'); import main; print('Python import smoke test: OK')"
if ($LASTEXITCODE -ne 0) {
    throw "主程序导入测试失败"
}

$NativeRoot = Join-Path $BuildRoot "native"
New-Item -ItemType Directory -Path $NativeRoot -Force | Out-Null

if (-not $SkipNative) {
    Write-Host "[4/5] 编译 Win32 DLL 和管理员启动器"
    $VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
    if (-not (Test-Path -LiteralPath $VsWhere)) {
        throw "未找到 vswhere.exe，请安装 Visual Studio 的 '使用 C++ 的桌面开发' 工作负载"
    }

    $VsPath = (& $VsWhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath).Trim()
    if (-not $VsPath) {
        throw "未找到 MSVC x64 编译工具"
    }

    $VcVars = Join-Path $VsPath "VC\Auxiliary\Build\vcvars64.bat"
    if (-not (Test-Path -LiteralPath $VcVars)) {
        throw "未找到 vcvars64.bat: $VcVars"
    }

    $NativeCommands = @(
        'cl /nologo /utf-8 /std:c++17 /O2 /EHsc /MT /DUNICODE /D_UNICODE /Fo"build\native\ToastLib.obj" /Fd"build\native\ToastLib.pdb" /LD "ToastLibdllmain.cpp" user32.lib gdi32.lib /link /OUT:"build\native\ToastLib.dll" /IMPLIB:"build\native\ToastLib.lib" /PDB:"build\native\ToastLib-link.pdb"',
        'cl /nologo /utf-8 /std:c++17 /O2 /EHsc /MT /DUNICODE /D_UNICODE /Fo"build\native\mutedll.obj" /Fd"build\native\mutedll.pdb" /LD "mutedlldllmain.cpp" user32.lib ole32.lib /link /OUT:"build\native\mutedll.dll" /IMPLIB:"build\native\mutedll.lib" /PDB:"build\native\mutedll-link.pdb"',
        'cl /nologo /utf-8 /std:c++17 /O2 /EHsc /MT /DUNICODE /D_UNICODE /Fo"build\native\OpenUrl.obj" /Fd"build\native\OpenUrl.pdb" /LD "OpenUrldllmain.cpp" user32.lib shell32.lib /link /OUT:"build\native\OpenUrl.dll" /IMPLIB:"build\native\OpenUrl.lib" /PDB:"build\native\OpenUrl-link.pdb"',
        'cl /nologo /utf-8 /std:c++17 /O2 /EHsc /MT /DUNICODE /D_UNICODE /Fo"build\native\Launcher.obj" /Fd"build\native\Launcher.pdb" "main.cpp" user32.lib gdi32.lib comctl32.lib shell32.lib advapi32.lib /link /SUBSYSTEM:WINDOWS /OUT:"release\Noki_NTE_Auto_Launcher.exe" /PDB:"build\native\Launcher-link.pdb"'
    )

    Push-Location $Root
    try {
        $CommandLine = "call `"$VcVars`" >nul && " + ($NativeCommands -join " && ")
        & cmd.exe /d /s /c $CommandLine
        if ($LASTEXITCODE -ne 0) {
            throw "原生组件编译失败，退出码: $LASTEXITCODE"
        }
    }
    finally {
        Pop-Location
    }
}

if (-not $SkipPackage) {
    Write-Host "[5/5] 使用 PyInstaller 生成单文件主程序"
    $RunningOutput = Get-Process -Name "Noki_NTE_Auto" -ErrorAction SilentlyContinue
    if ($RunningOutput) {
        $RunningIds = ($RunningOutput.Id -join ", ")
        throw "Noki_NTE_Auto.exe 仍在运行（PID: $RunningIds），请先关闭程序再重新构建"
    }
    & $Python -m PyInstaller `
        --noconfirm `
        --clean `
        --noupx `
        --onefile `
        --windowed `
        --name "Noki_NTE_Auto" `
        --icon (Join-Path $Root "异环图片\app_iconNTE.ico") `
        --distpath $DistRoot `
        --workpath (Join-Path $BuildRoot "pyinstaller") `
        --specpath $BuildRoot `
        --paths $SourceRoot `
        --hidden-import "pynput.mouse" `
        --collect-all "pyaudiowpatch" `
        (Join-Path $SourceRoot "main.py")
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller 打包失败"
    }
}

Write-Host "复制运行资源"
Copy-ReleaseItem (Join-Path $Root "UI") (Join-Path $DistRoot "UI")
Copy-ReleaseItem (Join-Path $Root "异环图片") (Join-Path $DistRoot "异环图片")
Copy-ReleaseItem (Join-Path $Root "外置配置文件夹") (Join-Path $ReleaseRoot "外置配置文件夹")

$RootFiles = @(
    "app_path.txt",
    "game.json",
    "settings.json",
    "Tool_Settings.json",
    "update.json",
    "update_check.json",
    "variable.json",
    "web_and_app.json",
    "异环钢琴自动演奏工具使用说明书.md"
)
foreach ($File in $RootFiles) {
    Copy-ReleaseItem (Join-Path $Root $File) (Join-Path $DistRoot $File)
}

Copy-ReleaseItem (Join-Path $NativeRoot "ToastLib.dll") (Join-Path $DistRoot "UI\脚本UI\ToastLib.dll")
Copy-ReleaseItem (Join-Path $NativeRoot "mutedll.dll") (Join-Path $DistRoot "UI\端口相关\mutedll.dll")
Copy-ReleaseItem (Join-Path $NativeRoot "OpenUrl.dll") (Join-Path $DistRoot "UI\打开网页\OpenUrl.dll")

$RequiredOutputs = @(
    (Join-Path $DistRoot "Noki_NTE_Auto.exe"),
    (Join-Path $DistRoot "UI"),
    (Join-Path $DistRoot "异环图片"),
    (Join-Path $ReleaseRoot "外置配置文件夹"),
    (Join-Path $ReleaseRoot "Noki_NTE_Auto_Launcher.exe"),
    (Join-Path $DistRoot "UI\脚本UI\ToastLib.dll"),
    (Join-Path $DistRoot "UI\端口相关\mutedll.dll"),
    (Join-Path $DistRoot "UI\打开网页\OpenUrl.dll")
)
foreach ($Output in $RequiredOutputs) {
    if (-not (Test-Path -LiteralPath $Output)) {
        throw "构建产物缺失: $Output"
    }
}

$Hashes = @(
    Get-Sha256 (Join-Path $DistRoot "Noki_NTE_Auto.exe")
    Get-Sha256 (Join-Path $ReleaseRoot "Noki_NTE_Auto_Launcher.exe")
)
$Hashes | Format-Table -AutoSize

Write-Host ""
Write-Host "构建完成: $ReleaseRoot"
