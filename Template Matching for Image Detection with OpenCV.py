import numpy as np
from tkinter import messagebox
import cv2
import tkinter as tk
import os
from PIL import Image
import time
import logging

logger = logging.getLogger(__name__)


def template_matching_in_region(background_image_data, search_region, template_path, min_similarity):
    """
    Perform template matching within a specified region of a background image

    Args:
        background_image_data: Raw image data of the background image
        search_region: Tuple (x, y, width, height) defining the search area
        template_path: Path to the template image file
        min_similarity: Minimum similarity threshold (0-1) for a valid match

    Returns:
        tuple: (is_matched, similarity_score, matched_x, matched_y)
               is_matched: Boolean indicating if match was found
               similarity_score: Actual similarity value (0-1)
               matched_x: X coordinate of match in original image
               matched_y: Y coordinate of match in original image
    """
    if not os.path.exists(template_path):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("路径错误", f"模板图片文件不存在: {template_path}")
        return False, 0, 0, 0

    background_image = cv2.imdecode(np.frombuffer(background_image_data, dtype=np.uint8), cv2.IMREAD_COLOR)

    try:
        with Image.open(template_path) as img:
            template_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        error_message = f"模板图片加载失败: {template_path}, 错误信息: {e}"
        print(error_message)
        error_info = f"模板匹配文件不存在或者路径中有中文: {error_message}"
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("路径错误", error_info)
        return False, 0, 0, 0

    if background_image is None or template_image is None:
        error_message = f"路径中有中文或者错误: {template_path}"
        print(error_message)
        error_info = f"模板匹配文件不存在或者路径中有中文: {error_message}"
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("路径错误", error_info)
        return False, 0, 0, 0
    x, y, width, height = search_region
    region_image = background_image[y:y + height, x:x + width]
    if template_image.shape[0] > region_image.shape[0] or template_image.shape[1] > region_image.shape[1]:
        root = tk.Tk()
        root.withdraw()  # Hide main window
        messagebox.showinfo("严重警告", f"模板尺寸必须小于或等于限定区域尺寸,路径：{str(template_path)}")
        time.sleep(2)
        is_matched, max_val, matched_x, matched_y = (False, 0, 0, 0)
    else:
        match_result = cv2.matchTemplate(region_image, template_image, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_result)
        matched_x = max_loc[0] + x
        matched_y = max_loc[1] + y
        is_matched = max_val >= min_similarity
        path_part = str(template_path)
        if "图片" in path_part:
            path_parts = path_part.split(r"图片")
            if path_parts:
                extracted_content = path_parts[1]
            else:
                extracted_content = template_path
        else:
            extracted_content = template_path
        if is_matched:
            logger.info(
                f"路径：{extracted_content},模板: {template_image.shape},限定: {region_image.shape},"
                f"匹配: {is_matched},相似: {max_val:.4f},坐标: ({matched_x}, {matched_y})")
        else:
            logger.debug(
                f"路径：{extracted_content},模板: {template_image.shape},限定: {region_image.shape},"
                f"匹配: {is_matched},相似: {max_val:.4f},坐标: ({matched_x}, {matched_y})")
    return is_matched, max_val, matched_x, matched_y