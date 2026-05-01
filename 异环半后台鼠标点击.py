import win32gui
import win32con
import win32api
import time
from 后台键盘鼠标 import simulate_mouse_left_click_hold


def 真实鼠标传递坐标后台点击(句柄, 矩形, 坐标, 长按时间, 脱离时间):
    """
    异环只能通过传递真实鼠标坐标来实现鼠标模拟。
    参数:
        句柄 (int): 目标窗口的句柄（用于发送后台消息）。
        矩形 (tuple): 目标窗口的矩形区域，格式为 (left, top, right, bottom)。
                      当前仅使用 left 和 top 来进行坐标偏移计算。
        坐标 (tuple): 客户区内的相对坐标 (x, y)，表示要点击的位置（相对于窗口客户区左上角）。
    注意:
        - 移动鼠标到屏幕绝对坐标时，采用了 `实际坐标 = (坐标[0] + 矩形[0], 坐标[1] + 矩形[1])` 的偏移计算。
        - 但传递给 `simulate_key_press_hold` 的坐标参数仍然是客户区相对坐标 (坐标[0], 坐标[1])，
          这可能是因为该底层函数在发送消息时同样需要窗口内的相对位置（或依据句柄自动进行坐标转换）。
        - 如果窗口被移动或遮挡，真实鼠标移动后可能会影响前台用户操作，因此最后会将鼠标复原。
    """
    try:
        # 保存当前鼠标位置，以便操作完成后恢复
        原位置 = win32api.GetCursorPos()

        # 矩形[0] 为窗口左边界屏幕坐标，矩形[1] 为窗口客户区上边界屏幕坐标
        实际坐标 = (坐标[0] + 矩形[0], 坐标[1] + 矩形[1])
        # 移动真实鼠标到计算出的屏幕绝对位置
        win32api.SetCursorPos(实际坐标)
        # 向目标窗口发送后台长按点击消息，使用原始的客户区相对坐标
        simulate_mouse_left_click_hold(句柄, 坐标[0], 坐标[1], 长按时间)
        time.sleep(脱离时间)

        # 将鼠标光标移回原来的位置，减少对用户正常操作的干扰
        win32api.SetCursorPos(原位置)

    except Exception as e:

        print(e)
