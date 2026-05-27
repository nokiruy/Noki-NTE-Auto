// ToastLib.cpp
// 导出函数：ShowToast(message, durationMs, textColor, bgColor)
// 参数说明：
//   message    - 要显示的文本（宽字符，Python 传 c_wchar_p）
//   durationMs - 显示毫秒数（>0，默认建议 3000）
//   textColor  - 文本颜色，格式为 0x00BBGGRR (COLORREF)，默认亮绿 0x0000FF00
//   bgColor    - 背景颜色，格式同上，默认非常浅蓝 0x00FFF8F0 (AliceBlue 的 COLORREF)
//
// 特性：
//   - 内部启动独立线程，立即返回，不阻塞调用者
//   - 所有异常在 DLL 内捕获，不会传播到外部
//   - 窗口无边框、置顶、不抢焦点，居中显示
//   - 点击窗口或定时到期自动关闭
//   - 支持多实例同时显示（各自独立线程）
#include "pch.h"
#include <windows.h>
#include <string>
#include <thread>
#include <memory>
#include <mutex>

// 避免 CRT 依赖，如需纯静态编译，使用 /MT 即可
#pragma comment(linker, "/subsystem:windows") // 无控制台窗口

// 全局窗口类名（只注册一次）
static const wchar_t CLASS_NAME[] = L"ToastLibWindowClass";
static std::once_flag g_classRegistered;

// 用于传递给窗口过程的参数
struct ToastParam {
    std::wstring message;
    COLORREF     textColor;
    COLORREF     bgColor;
    int          duration;
    // 允许构造
    ToastParam(const std::wstring& m, COLORREF tc, COLORREF bc, int d)
        : message(m), textColor(tc), bgColor(bc), duration(d) {
    }
};

// 窗口过程
LRESULT CALLBACK ToastWndProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    // 获取参数指针（在 WM_CREATE 时保存）
    ToastParam* pParam = reinterpret_cast<ToastParam*>(
        GetWindowLongPtrW(hWnd, GWLP_USERDATA));

    switch (msg) {
    case WM_CREATE: {
        // 取出 CREATESTRUCT 中的参数
        CREATESTRUCT* pCreate = reinterpret_cast<CREATESTRUCT*>(lParam);
        pParam = static_cast<ToastParam*>(pCreate->lpCreateParams);
        if (!pParam) return -1;
        SetWindowLongPtrW(hWnd, GWLP_USERDATA, reinterpret_cast<LONG_PTR>(pParam));
        // 设置定时器
        SetTimer(hWnd, 1, pParam->duration, nullptr);
        break;
    }
    case WM_TIMER:
        if (wParam == 1) {
            KillTimer(hWnd, 1);
            DestroyWindow(hWnd);
        }
        break;
    case WM_LBUTTONDOWN:
        DestroyWindow(hWnd);
        break;
    case WM_PAINT: {
        if (!pParam) break;
        PAINTSTRUCT ps;
        HDC hdc = BeginPaint(hWnd, &ps);
        RECT rect;
        GetClientRect(hWnd, &rect);

        // 背景
        HBRUSH hBrush = CreateSolidBrush(pParam->bgColor);
        FillRect(hdc, &rect, hBrush);
        DeleteObject(hBrush);

        // 文本
        SetBkMode(hdc, TRANSPARENT);
        SetTextColor(hdc, pParam->textColor);
        HFONT hFont = reinterpret_cast<HFONT>(GetStockObject(DEFAULT_GUI_FONT));
        SelectObject(hdc, hFont);
        DrawTextW(hdc, pParam->message.c_str(), -1, &rect,
            DT_CENTER | DT_VCENTER | DT_SINGLELINE | DT_NOPREFIX);

        EndPaint(hWnd, &ps);
        break;
    }
    case WM_DESTROY:
        PostQuitMessage(0);
        break;
    default:
        return DefWindowProc(hWnd, msg, wParam, lParam);
    }
    return 0;
}

// 线程主函数：创建窗口并运行消息循环
void ToastThread(ToastParam param) {
    try {
        // 确保窗口类已注册（只注册一次）
        std::call_once(g_classRegistered, []() {
            WNDCLASSEXW wc = { sizeof(WNDCLASSEXW) };
            wc.lpfnWndProc = ToastWndProc;
            wc.hInstance = GetModuleHandleW(nullptr);
            wc.hCursor = LoadCursorW(nullptr, IDC_ARROW);
            wc.hbrBackground = nullptr;
            wc.lpszClassName = CLASS_NAME;
            wc.style = CS_HREDRAW | CS_VREDRAW;
            RegisterClassExW(&wc);
            });

        // 测量文本尺寸，确定窗口大小
        HDC hdcScreen = GetDC(nullptr);
        HFONT hFont = reinterpret_cast<HFONT>(GetStockObject(DEFAULT_GUI_FONT));
        SelectObject(hdcScreen, hFont);
        RECT measureRect = {};
        DrawTextW(hdcScreen, param.message.c_str(), -1, &measureRect,
            DT_CALCRECT | DT_CENTER | DT_VCENTER | DT_SINGLELINE);
        ReleaseDC(nullptr, hdcScreen);

        int textW = measureRect.right - measureRect.left;
        int textH = measureRect.bottom - measureRect.top;
        int winW = max(180, textW + 40);
        int winH = max(50, textH + 30);

        // 屏幕居中
        int screenW = GetSystemMetrics(SM_CXSCREEN);
        int screenH = GetSystemMetrics(SM_CYSCREEN);
        int x = (screenW - winW) / 2;
        int y = (screenH - winH) / 2;

        // 创建窗口
        HWND hWnd = CreateWindowExW(
            WS_EX_TOPMOST | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW,
            CLASS_NAME,
            L"",
            WS_POPUP,
            x, y, winW, winH,
            nullptr, nullptr, GetModuleHandleW(nullptr),
            &param  // 传递参数指针
        );

        if (!hWnd)
            return;

        ShowWindow(hWnd, SW_SHOWNOACTIVATE);
        UpdateWindow(hWnd);

        // 消息循环
        MSG msg;
        while (GetMessageW(&msg, nullptr, 0, 0)) {
            TranslateMessage(&msg);
            DispatchMessageW(&msg);
        }
    }
    catch (...) {
        // 吞掉所有异常，绝不影响调用方
    }
}

// 导出函数：显示 Toast（非阻塞，立即返回）
extern "C" __declspec(dllexport) void ShowToast(
    const wchar_t* message,
    int            durationMs,
    unsigned int   textColor,
    unsigned int   bgColor
) {
    // 参数校验
    if (!message || !*message)
        return;
    if (durationMs <= 0)
        durationMs = 3000;

    // 启动线程
    try {
        std::thread t(ToastThread,
            ToastParam(message, static_cast<COLORREF>(textColor),
                static_cast<COLORREF>(bgColor), durationMs));
        t.detach(); // 独立运行，不阻塞
    }
    catch (...) {
        // 线程创建失败（几乎不可能），静默忽略
    }
}