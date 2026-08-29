from windows_capture import WindowsCapture, Frame, InternalCaptureControl
import time
import os

class WindowCaptureManager:
    """窗口捕获管理器，封装启动/停止和帧回调"""

    def __init__(self):
        self.capture = None          # WindowsCapture 实例
        self.control = None          # InternalCaptureControl 对象，用于停止
        self._frame_saved = False    # 是否已执行自动保存

    def start(self, hwnd: int, on_frame=None, on_closed=None, save_first_frame: str = None):
        """
        启动指定窗口的捕获（后台线程）
        :param hwnd: 目标窗口句柄
        :param on_frame: 可选，自定义帧回调 (frame, control) -> None
        :param on_closed: 可选，捕获关闭回调
        :param save_first_frame: 可选，自动保存第一帧的完整路径（如 "capture.png"）
        """
        if self.capture is not None:
            raise RuntimeError("捕获已启动，请先调用 stop()")

        self._save_path = save_first_frame
        self._frame_saved = False

        self.capture = WindowsCapture(
            cursor_capture=False,
            draw_border=False,
            window_hwnd=hwnd
        )

        def frame_handler(frame: Frame, control: InternalCaptureControl):
            # 保存控制对象
            if self.control is None:
                self.control = control
                print("已获取捕获控制对象")

            # 自动保存第一帧（如果设置了路径）
            if self._save_path and not self._frame_saved:
                frame.save_as_image(self._save_path)
                print(f"图片已保存：{self._save_path}")
                self._frame_saved = True

            # 调用用户自定义回调
            if on_frame:
                on_frame(frame, control)

        def closed_handler():
            print("捕获会话已关闭")
            if on_closed:
                on_closed()

        # 正确注册回调：使用 on_frame_arrived 和 on_closed 方法
        self.capture.on_frame_arrived(frame_handler)
        self.capture.on_closed(closed_handler)

        # 启动后台捕获
        self.capture.start_free_threaded()
        print("捕获已启动（后台线程）")

    def stop(self):
        """停止捕获并释放资源"""
        if self.control:
            self.control.stop()
            self.control = None
            self.capture = None
            print("已调用 stop()，捕获停止")
        else:
            print("警告：未获取到控制对象，无法停止（窗口可能无帧更新）")


# ---------- 使用示例 ----------
if __name__ == "__main__":
    manager = WindowCaptureManager()

    # 自定义帧回调（可选）
    def my_frame_handler(frame, control):
        print("获取到了新帧")

    # 启动捕获，自动保存第一帧为 capture_.png
    manager.start(
        hwnd=2886632,
        on_frame=my_frame_handler,
        save_first_frame="capture_.png"
    )

    time.sleep(2)           # 主线程可做其他事
    manager.stop()          # 通过 stop() 关闭
    time.sleep(0.5)
from windows_capture import WindowsCapture, Frame, InternalCaptureControl
import time
import os
if __name__ == "__ain__":
    try:
        窗口句柄 = 526432
        捕获器 = WindowsCapture(cursor_capture=False, draw_border=False, window_hwnd=窗口句柄)

        控制对象 = None  # 用于保存回调中的控制对象

        已保存图片 = False  # 新增：标记是否已保存，避免每帧都存


        def on_frame_arrived(帧: Frame, 捕获控制: InternalCaptureControl):
            global 控制对象, 已保存图片
            if 控制对象 != 捕获控制:
                控制对象 = 捕获控制
                print("已获取捕获控制对象")

            # ---------- 保存图片到本地 ----------
            if not 已保存图片:
                # 生成不重复的文件名（含时间戳）
                文件名 = f"capture_.png"
                保存路径 = os.path.join(os.getcwd(), 文件名)
                帧.save_as_image(保存路径)
                print(f"图片已保存：{保存路径}")
                已保存图片 = True

            print("获取到了新帧")


        def on_closed():
            print("捕获会话已关闭")


        捕获器.event(on_frame_arrived)
        捕获器.event(on_closed)

        # 使用非阻塞方式启动
        捕获器.start_free_threaded()
        print("捕获已启动（后台线程）")

        # 等待 2 秒，期间主线程可以干别的事
        time.sleep(2)

        # 通过保存的控制对象停止捕获
        if 控制对象 is not None:
            控制对象.stop()
            print("已调用 stop()，捕获停止")
        else:
            print("警告：未获取到控制对象，无法停止（请检查窗口是否有帧更新）")

        # 给线程一点时间退出
        time.sleep(0.5)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        import traceback

        traceback.print_exc()
        input("按回车键退出...")

"""捕获器对象的所有公开方法：
  - event
  - on_closed
  - on_frame_arrived
  - start
  - start_free_threaded
获取到了新帧
捕获控制对象的方法：
  - stop
  ===== Frame 对象的所有成员 =====
['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', 
'__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__',
 '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__',
  '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__',
   '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 
   'convert_to_bgr', 'crop', 'frame_buffer', 'height', 'save_as_image', 'timespan', 'width']
================================
"""