#include <windows.h>
#include <string>
#include <filesystem>
#include <thread>
#include <chrono>
#include <commctrl.h>
#include <shellapi.h>

#pragma comment(lib, "comctl32.lib")
#pragma comment(lib, "shell32.lib")

namespace fs = std::filesystem;

HWND g_hWnd = NULL;
HWND g_hStaticText = NULL;
HWND g_hProgressBar = NULL;
const wchar_t* g_windowClass = L"NokiLauncherWindow";

void ShowErrorMessage(const std::wstring& message);
void checkAndLaunch(HWND hwnd);
void HandleErrorMessage(HWND hwnd, LPARAM lParam);
BOOL RegisterWindowClass(HINSTANCE hInstance);
HWND CreateMainWindow(HINSTANCE hInstance);
void UpdateProgress(int percentage, const std::wstring& message);
bool IsRunningAsAdmin();
bool RestartAsAdmin();

bool IsRunningAsAdmin() {
    BOOL isAdmin = FALSE;
    PSID adminGroup = NULL;

    SID_IDENTIFIER_AUTHORITY ntAuthority = SECURITY_NT_AUTHORITY;
    if (AllocateAndInitializeSid(&ntAuthority, 2, SECURITY_BUILTIN_DOMAIN_RID,
        DOMAIN_ALIAS_RID_ADMINS, 0, 0, 0, 0, 0, 0, &adminGroup)) {
        if (!CheckTokenMembership(NULL, adminGroup, &isAdmin)) {
            isAdmin = FALSE;
        }
        FreeSid(adminGroup);
    }

    return isAdmin == TRUE;
}

bool RestartAsAdmin() {
    wchar_t currentPath[MAX_PATH];
    GetModuleFileNameW(NULL, currentPath, MAX_PATH);

    SHELLEXECUTEINFOW sei = { sizeof(sei) };
    sei.lpVerb = L"runas";
    sei.lpFile = currentPath;
    sei.hwnd = NULL;
    sei.nShow = SW_NORMAL;

    return ShellExecuteExW(&sei) == TRUE;
}

void ShowErrorMessage(const std::wstring& message) {
    MessageBoxW(NULL, message.c_str(), L"启动器错误", MB_ICONERROR | MB_OK);
}

void UpdateProgress(int percentage, const std::wstring& message) {
    if (g_hStaticText) {
        SetWindowTextW(g_hStaticText, message.c_str());
    }
    if (g_hProgressBar) {
        SendMessage(g_hProgressBar, PBM_SETPOS, percentage, 0);
    }
}

void checkAndLaunch(HWND hwnd) {
    wchar_t current_path[MAX_PATH];
    GetModuleFileNameW(NULL, current_path, MAX_PATH);
    fs::path current_dir = fs::path(current_path).parent_path();

    fs::path exe_path = current_dir / "dist" / "Noki_HBR_Auto.exe";

    try {
        UpdateProgress(10, L"正在初始化...");
        std::this_thread::sleep_for(std::chrono::milliseconds(300));

        UpdateProgress(30, L"检查目标文件是否存在...");
        std::this_thread::sleep_for(std::chrono::milliseconds(500));

        if (fs::exists(exe_path)) {
            UpdateProgress(60, L"正在启动目标程序...");
            std::this_thread::sleep_for(std::chrono::milliseconds(500));

            STARTUPINFOW si = { sizeof(si) };
            PROCESS_INFORMATION pi;

            std::wstring exe_path_str = exe_path.wstring();
            wchar_t* cmd_line = &exe_path_str[0];

            if (CreateProcessW(
                NULL,
                cmd_line,
                NULL,
                NULL,
                FALSE,
                0,
                NULL,
                NULL,
                &si,
                &pi
            )) {
                CloseHandle(pi.hProcess);
                CloseHandle(pi.hThread);

                UpdateProgress(100, L"启动成功！");
                std::this_thread::sleep_for(std::chrono::milliseconds(1000));

                PostMessage(hwnd, WM_CLOSE, 0, 0);
            }
            else {
                DWORD error = GetLastError();
                std::wstring error_msg = L"无法启动程序: " + exe_path.wstring() +
                    L"\n错误代码: " + std::to_wstring(error);

                PostMessage(hwnd, WM_USER + 1, 0, (LPARAM)new std::wstring(error_msg));
            }
        }
        else {
            std::wstring error_msg = L"目标程序不存在:\n" + exe_path.wstring();
            PostMessage(hwnd, WM_USER + 1, 0, (LPARAM)new std::wstring(error_msg));
        }
    }
    catch (const std::exception& e) {
        std::string error_str = e.what();
        std::wstring error_msg = L"发生异常: " + std::wstring(error_str.begin(), error_str.end());
        PostMessage(hwnd, WM_USER + 1, 0, (LPARAM)new std::wstring(error_msg));
    }
}

void HandleErrorMessage(HWND hwnd, LPARAM lParam) {
    std::wstring* error_msg = (std::wstring*)lParam;
    ShowErrorMessage(*error_msg);
    delete error_msg; 

    PostMessage(hwnd, WM_CLOSE, 0, 0);
}

LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
    switch (uMsg) {
    case WM_CREATE:
    {
        HWND hTitle = CreateWindowW(
            L"STATIC",
            L"Noki启动器 (管理员模式)",
            WS_VISIBLE | WS_CHILD | SS_CENTER,
            10, 15, 380, 25,
            hwnd,
            NULL,
            (HINSTANCE)GetWindowLongPtr(hwnd, GWLP_HINSTANCE),
            NULL
        );

    
        HFONT hTitleFont = CreateFontW(
            20, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE,
            DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
            DEFAULT_QUALITY, DEFAULT_PITCH | FF_DONTCARE, L"微软雅黑"
        );
        SendMessage(hTitle, WM_SETFONT, (WPARAM)hTitleFont, TRUE);


        g_hStaticText = CreateWindowW(
            L"STATIC",
            L"正在初始化...",
            WS_VISIBLE | WS_CHILD | SS_CENTER,
            10, 50, 380, 25,
            hwnd,
            NULL,
            (HINSTANCE)GetWindowLongPtr(hwnd, GWLP_HINSTANCE),
            NULL
        );

  
        HFONT hStatusFont = CreateFontW(
            14, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE,
            DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
            DEFAULT_QUALITY, DEFAULT_PITCH | FF_DONTCARE, L"微软雅黑"
        );
        SendMessage(g_hStaticText, WM_SETFONT, (WPARAM)hStatusFont, TRUE);

 
        g_hProgressBar = CreateWindowW(
            PROGRESS_CLASSW,  
            NULL,
            WS_VISIBLE | WS_CHILD | PBS_SMOOTH,
            50, 85, 300, 20,
            hwnd,
            NULL,
            (HINSTANCE)GetWindowLongPtr(hwnd, GWLP_HINSTANCE),
            NULL
        );


        SendMessage(g_hProgressBar, PBM_SETRANGE, 0, MAKELPARAM(0, 100));
        SendMessage(g_hProgressBar, PBM_SETPOS, 0, 0);

        std::thread(checkAndLaunch, hwnd).detach();
    }
    break;

    case WM_DESTROY:
        PostQuitMessage(0);
        break;

    case WM_CLOSE:
        DestroyWindow(hwnd);
        break;

    case WM_USER + 1:
        HandleErrorMessage(hwnd, lParam);
        break;

    default:
        return DefWindowProc(hwnd, uMsg, wParam, lParam);
    }
    return 0;
}

BOOL RegisterWindowClass(HINSTANCE hInstance) {
    WNDCLASSW wc = {};
    wc.lpfnWndProc = WindowProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = g_windowClass;
    wc.hIcon = LoadIcon(hInstance, IDI_APPLICATION);
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    wc.lpszMenuName = NULL;
    wc.cbClsExtra = 0;
    wc.cbWndExtra = 0;
    wc.style = CS_HREDRAW | CS_VREDRAW;

    return RegisterClassW(&wc);
}

HWND CreateMainWindow(HINSTANCE hInstance) {
    HWND hwnd = CreateWindowExW(
        0,
        g_windowClass,
        L"Noki启动器 (管理员模式)",
        WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX,
        CW_USEDEFAULT, CW_USEDEFAULT, 420, 180,
        NULL,
        NULL,
        hInstance,
        NULL
    );

    return hwnd;
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {

    if (!IsRunningAsAdmin()) {

        if (RestartAsAdmin()) {
            return 0; 
        }
        else {
            ShowErrorMessage(L"需要管理员权限才能运行此程序。\n请右键点击程序，选择'以管理员身份运行'。");
            return 1;
        }
    }
  
    INITCOMMONCONTROLSEX icex;
    icex.dwSize = sizeof(INITCOMMONCONTROLSEX);
    icex.dwICC = ICC_PROGRESS_CLASS;
    InitCommonControlsEx(&icex);

 
    if (!RegisterWindowClass(hInstance)) {
        ShowErrorMessage(L"无法注册窗口类");
        return 1;
    }

    g_hWnd = CreateMainWindow(hInstance);
    if (!g_hWnd) {
        ShowErrorMessage(L"无法创建窗口");
        return 1;
    }

    RECT rc;
    GetWindowRect(g_hWnd, &rc);
    int x = (GetSystemMetrics(SM_CXSCREEN) - (rc.right - rc.left)) / 2;
    int y = (GetSystemMetrics(SM_CYSCREEN) - (rc.bottom - rc.top)) / 2;
    SetWindowPos(g_hWnd, NULL, x, y, 0, 0, SWP_NOSIZE | SWP_NOZORDER);

    ShowWindow(g_hWnd, nCmdShow);
    UpdateWindow(g_hWnd);

    MSG msg = {};
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    return 0;
}
