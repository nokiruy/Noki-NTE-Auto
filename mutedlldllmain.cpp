// MuteLib.cpp – 根据窗口句柄静音/解除静音，DLL 版本
// 导出函数：
//   BOOL MuteProcessByHwnd(UINT64 hwndValue, BOOL mute);
// 返回值 TRUE 表示操作成功。
#include "pch.h"
#include <windows.h>
#include <mmdeviceapi.h>
#include <audiopolicy.h>
#include <audioclient.h>

#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "winmm.lib")

// ----------------------------------------------------------------
// 辅助：通过窗口句柄获取进程 ID
// ----------------------------------------------------------------
static DWORD GetProcessIdFromHwnd(HWND hwnd) {
    DWORD pid = 0;
    GetWindowThreadProcessId(hwnd, &pid);
    return pid;
}

// ----------------------------------------------------------------
// 核心：为指定进程设置静音
// ----------------------------------------------------------------
static BOOL SetMuteForProcess(DWORD targetPid, BOOL mute) {
    HRESULT hr;
    BOOL success = FALSE;

    // 1. 初始化 COM（每次调用都自初始化，避免依赖外部环境）
    hr = CoInitializeEx(NULL, COINIT_MULTITHREADED);
    if (FAILED(hr))
        return FALSE;

    // RAII 自动卸载 COM
    struct ComGuard { ~ComGuard() { CoUninitialize(); } } guard;

    // 2. 创建设备枚举器
    IMMDeviceEnumerator* pEnumerator = NULL;
    hr = CoCreateInstance(__uuidof(MMDeviceEnumerator), NULL,
        CLSCTX_ALL, __uuidof(IMMDeviceEnumerator),
        (void**)&pEnumerator);
    if (FAILED(hr))
        return FALSE;

    // 3. 获取默认音频渲染设备
    IMMDevice* pDevice = NULL;
    hr = pEnumerator->GetDefaultAudioEndpoint(eRender, eConsole, &pDevice);
    if (FAILED(hr)) {
        pEnumerator->Release();
        return FALSE;
    }

    // 4. 激活 IAudioSessionManager2
    IAudioSessionManager2* pSessionManager2 = NULL;
    hr = pDevice->Activate(__uuidof(IAudioSessionManager2), CLSCTX_ALL,
        NULL, (void**)&pSessionManager2);
    if (FAILED(hr)) {
        pDevice->Release();
        pEnumerator->Release();
        return FALSE;
    }

    // 5. 获取会话枚举器
    IAudioSessionEnumerator* pSessionEnum = NULL;
    hr = pSessionManager2->GetSessionEnumerator(&pSessionEnum);
    if (FAILED(hr)) {
        pSessionManager2->Release();
        pDevice->Release();
        pEnumerator->Release();
        return FALSE;
    }

    // 6. 遍历会话，匹配进程 ID
    int count = 0;
    pSessionEnum->GetCount(&count);
    for (int i = 0; i < count; ++i) {
        IAudioSessionControl* pSessionCtrl = NULL;
        hr = pSessionEnum->GetSession(i, &pSessionCtrl);
        if (FAILED(hr)) continue;

        IAudioSessionControl2* pSessionCtrl2 = NULL;
        hr = pSessionCtrl->QueryInterface(__uuidof(IAudioSessionControl2),
            (void**)&pSessionCtrl2);
        if (SUCCEEDED(hr)) {
            DWORD pid = 0;
            pSessionCtrl2->GetProcessId(&pid);
            if (pid == targetPid) {
                ISimpleAudioVolume* pVolume = NULL;
                hr = pSessionCtrl->QueryInterface(__uuidof(ISimpleAudioVolume),
                    (void**)&pVolume);
                if (SUCCEEDED(hr)) {
                    hr = pVolume->SetMute(mute, NULL);
                    if (SUCCEEDED(hr))
                        success = TRUE;
                    pVolume->Release();
                }
            }
            pSessionCtrl2->Release();
        }
        pSessionCtrl->Release();
        if (success) break;
    }

    // 7. 释放资源
    pSessionEnum->Release();
    pSessionManager2->Release();
    pDevice->Release();
    pEnumerator->Release();

    return success;
}

// ----------------------------------------------------------------
// 导出给 Python 的接口
// 参数：
//   hwndValue - 窗口句柄（无符号 64 位整数）
//   mute      - TRUE=静音, FALSE=解除静音
// 返回：
//   TRUE=成功, FALSE=失败（任何异常均已内部捕获）
// ----------------------------------------------------------------
extern "C" __declspec(dllexport) BOOL MuteProcessByHwnd(
    UINT64 hwndValue, BOOL mute)
{
    // 参数校验
    HWND hwnd = reinterpret_cast<HWND>((INT_PTR)hwndValue);
    if (!IsWindow(hwnd))
        return FALSE;

    DWORD pid = GetProcessIdFromHwnd(hwnd);
    if (pid == 0)
        return FALSE;

    // 内部 try‑catch 保证 Python 进程绝对安全
    __try {
        return SetMuteForProcess(pid, mute);
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        return FALSE;
    }
}