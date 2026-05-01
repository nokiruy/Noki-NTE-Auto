import time
import win32gui
import ctypes
from PIL import Image
import win32clipboard
import io
import win32ui
import win32process
import win32api
import win32con
import ctypes

def 函数截图到内存(句柄, 矩形):
    """根据窗口信息进行截图并保存到内存，需管理员权限"""
    hdc = mfc_dc = save_dc = bitmap = None
    try:
        if not 句柄 or not 矩形:
            print("窗口信息未初始化，游戏可能未正确打开")
            if 句柄 and not 矩形:
                print("使用脚本要求分辨率")
                矩形=(0, 0, 1280, 720)


        left, top, right, bottom = 矩形
        width = right - left
        height = bottom - top

        hdc = win32gui.GetWindowDC(句柄)
        mfc_dc = win32ui.CreateDCFromHandle(hdc)
        save_dc = mfc_dc.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(bitmap)

        #print("调用 PrintWindow...")
        if ctypes.windll.user32.PrintWindow(句柄, save_dc.GetSafeHdc(), 3):
            bitmap_bits = bitmap.GetBitmapBits(True)
            img = Image.frombuffer("RGB", (width, height), bitmap_bits, "raw", "BGRX", 0, 1)

            with io.BytesIO() as output:
                img.save(output, format="PNG", compress_level=0)
                #img.save(f"frame_.png")#测试
                #print(1)
                return output.getvalue()

        else:
            print("PrintWindow调用失败,可能是游戏窗口一开始处于最小化导致的坐标不正确或者现在处于最小化导致的截图失败,")
    except Exception as e:
        print(f"截图失败: {str(e)}")

        return None
    finally:
        # 确保资源释放
        if bitmap:
            win32gui.DeleteObject(bitmap.GetHandle())
        if save_dc:
            save_dc.DeleteDC()
        if mfc_dc:
            mfc_dc.DeleteDC()
        if hdc:
            win32gui.ReleaseDC(句柄, hdc)
if __name__ == "__main__":
    句柄=3018758
    函数截图到内存(句柄, 0)