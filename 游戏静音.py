import win32gui
import win32process
import win32con
import win32api
from pycaw.pycaw import AudioUtilities
import time


def mute_window_by_hwnd_safe(hwnd):
    """通过窗口句柄静音应用 - 安全方法"""
    try:
        # 获取进程ID
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        print(f"窗口句柄: {hwnd}, 进程ID: {pid}")

        # 获取窗口标题
        title = win32gui.GetWindowText(hwnd)
        print(f"窗口标题: {title}")

        # 获取音频会话
        sessions = AudioUtilities.GetAllSessions()
        found = False

        for session in sessions:
            try:
                if session.Process and session.Process.pid == pid:
                    volume = session.SimpleAudioVolume
                    # 获取当前静音状态
                    is_muted = volume.GetMute()
                    print(f"当前静音状态: {is_muted}")

                    # 切换静音状态
                    new_mute_state = not is_muted
                    volume.SetMute(new_mute_state, None)

                    # 验证
                    time.sleep(0.1)
                    verified = volume.GetMute()
                    print(f"设置后静音状态: {verified}")

                    if verified == new_mute_state:
                        print(f"成功{'静音' if new_mute_state else '取消静音'}进程: {pid}")
                    else:
                        print(f"设置静音状态失败")

                    found = True
                    break
            except Exception as e:
                print(f"处理音频会话时出错: {e}")
                continue

        if not found:
            print(f"未找到进程 {pid} 的音频会话")
            # 尝试查找进程名
            import psutil
            try:
                proc = psutil.Process(pid)
                print(f"进程名: {proc.name()}")
            except:
                pass

        return found

    except Exception as e:
        print(f"静音失败: {str(e)}")
        return False


def find_all_windows_with_title(title_part):
    """查找所有包含指定标题的窗口"""
    windows = []

    def enum_windows_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if title_part.lower() in window_title.lower():
                windows.append((hwnd, window_title))
        return True

    win32gui.EnumWindows(enum_windows_callback, None)
    return windows


if __name__ == "__main__":
    # 查找所有包含"HeavenBurnsRed"的窗口
    windows = find_all_windows_with_title("HeavenBurnsRed")

    if not windows:
        # 尝试其他可能的标题
        possible_titles = ["Heaven", "Burns", "Red", "天", "堂"]
        for title in possible_titles:
            windows = find_all_windows_with_title(title)
            if windows:
                break

    if windows:
        print(f"找到 {len(windows)} 个窗口:")
        for hwnd, title in windows:
            print(f"  句柄: {hwnd}, 标题: {title}")

        # 静音第一个找到的窗口
        hwnd, title = windows[0]
        mute_window_by_hwnd_safe(hwnd)
    else:
        print("未找到匹配的窗口")