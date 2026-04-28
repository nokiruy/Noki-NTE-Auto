import win32gui
import win32con
import time
import threading
import win32api

"""
Virtual key codes for common keys:
Key Code List = [
    0x71,  # F2
    0x51,  # Q
    0x45,  # E
    0x52,  # R
    0x46,  # F
    0x58,  # X
    0x54,  # T
    0x4D,  # M
    0x31,  # 1
    0x32,  # 2
    0x33,  # 3
    0x34,  # 4
    0xA0,  # Left Shift
    0x20,  # Space
    0x04,  # Middle Mouse Button
    0x57,  # W
    0x41,  # A
    0x53,  # S
    0x44,  # D
    0x1B,  # ESC
    0xA4,  # ALT
    0x09,  # TAB
]
"""

def fake_activate_window(hwnd):
    """Activate a background window so that it can receive background keyboard and mouse commands."""
    try:
        win32gui.SendMessage(hwnd, WM_ACTIVATE, WA_ACTIVE, 0)
    except Exception as e:
        print(e)
def simulate_key_press_hold(handle, vk_code, duration):
    """
    Simulates pressing and holding a key for a specified duration

    Args:
        handle: Window handle to send the key event to
        vk_code: Virtual key code of the key to press
        duration: How long to hold the key (in seconds)
    """
    try:
        win32gui.PostMessage(handle, win32con.WM_KEYDOWN, vk_code, 0)
        time.sleep(duration)
        win32gui.PostMessage(handle, win32con.WM_KEYUP, vk_code, 0)
    except Exception as e:
        print(e)
        time.sleep(1)


def simulate_key_down(handle, vk_code):
    """
    Simulates pressing a key down (without releasing)

    Args:
        handle: Window handle to send the key event to
        vk_code: Virtual key code of the key to press down
    """
    try:
        win32gui.PostMessage(handle, win32con.WM_KEYDOWN, vk_code, 0)
    except Exception as e:
        print(e)
        time.sleep(1)


def simulate_key_up(handle, vk_code):
    """
    Simulates releasing a key

    Args:
        handle: Window handle to send the key event to
        vk_code: Virtual key code of the key to release
    """
    try:
        win32gui.PostMessage(handle, win32con.WM_KEYUP, vk_code, 0)
    except Exception as e:
        print(e)
        time.sleep(1)


def MAKELONG(low, high):
    """
    Creates a LONG value from two 16-bit values (used for mouse coordinates)

    Args:
        low: Low-order word (typically X coordinate)
        high: High-order word (typically Y coordinate)

    Returns:
        Combined LONG value
    """
    return (high << 16) | (low & 0xFFFF)


def simulate_mouse_left_click_hold(handle, x, y, duration):
    """
    Simulates pressing and holding the left mouse button for a specified duration

    Args:
        handle: Window handle to send the mouse event to
        x: X coordinate for the mouse event
        y: Y coordinate for the mouse event
        duration: How long to hold the mouse button (in seconds)
    """
    try:
        win32gui.PostMessage(handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, MAKELONG(x, y))
        time.sleep(duration)
        win32gui.PostMessage(handle, win32con.WM_LBUTTONUP, 0, MAKELONG(x, y))
    except Exception as e:
        print(e)
        time.sleep(1)


def simulate_mouse_left_down(handle, x, y, delay=0.001):
    """
    Simulates pressing down the left mouse button (without releasing)

    Args:
        handle: Window handle to send the mouse event to
        x: X coordinate for the mouse event
        y: Y coordinate for the mouse event
        delay: Short delay after the action (in seconds)
    """
    try:
        win32gui.PostMessage(handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, MAKELONG(x, y))
        time.sleep(delay)
    except Exception:
        pass


def simulate_mouse_left_up(handle, x, y, delay=0.001):
    """
    Simulates releasing the left mouse button

    Args:
        handle: Window handle to send the mouse event to
        x: X coordinate for the mouse event
        y: Y coordinate for the mouse event
        delay: Short delay after the action (in seconds)
    """
    try:
        win32gui.PostMessage(handle, win32con.WM_LBUTTONUP, 0, MAKELONG(x, y))
        time.sleep(delay)
    except Exception:

        pass
