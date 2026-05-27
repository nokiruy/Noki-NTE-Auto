#include "pch.h"
#include <windows.h>
#include <shellapi.h>

// 导出函数：成功返回 0，失败返回非 0 错误码
extern "C" __declspec(dllexport) int OpenURL(const wchar_t* url)
{
    // 1. 参数有效性检查
    if (url == nullptr || wcslen(url) == 0) {
        return -1;   // 无效参数
    }

    try {
        // 2. 调用 ShellExecuteW 打开默认浏览器
        HINSTANCE hResult = ShellExecuteW(
            nullptr,           // 父窗口句柄
            L"open",           // 操作：打开
            url,               // 网址（宽字符串）
            nullptr,           // 参数
            nullptr,           // 工作目录
            SW_SHOWNORMAL      // 显示方式：正常窗口
        );

        // 3. 检查返回值：>32 表示成功
        if ((INT_PTR)hResult > 32) {
            return 0;          // 成功
        }
        else {
            // ShellExecute 返回的错误码 <=32，直接返回让 Python 端查询
            return (int)(INT_PTR)hResult;
        }
    }
    catch (...) {
        // 4. 捕获所有意外异常，保证不崩溃
        return -2;             // 未知内部异常
    }
}