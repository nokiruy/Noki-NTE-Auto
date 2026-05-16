import time
import logging
logger = logging.getLogger("database")

def 可变速等待(秒: float = 1.0, 检查间隔: float = 0.1) -> bool:
    """
    可变速度的等待函数，支持线程中断

    Args:
        秒: 等待的总秒数
        检查间隔: 检查线程事件的时间间隔（实际时间，不考虑速度因子）

    Returns:
        bool: True表示正常等待完成，False表示被中断
    """
    global 线程事件任务循环,脚本运行速度

    if not 线程事件任务循环.is_set():

        return False
    if 秒 <= 0:
        return True

    if 脚本运行速度 <= 0:
        logger.warning("脚本运行速度不能小于等于0，使用默认值1.0")
        实际速度 = 1.0
    else:
        实际速度 = 脚本运行速度

    # 计算实际需要等待的时间
    实际等待时间 = 秒 / 实际速度

    # 计算需要检查的次数
    检查次数 = max(1, int(实际等待时间 / 检查间隔))
    最后等待时间 = 实际等待时间 - (检查次数 - 1) * 检查间隔
    #logger.debug(f"{脚本运行速度}and {线程事件任务循环.is_set()}and{实际等待时间}")
    try:
        for i in range(检查次数):
            if not 线程事件任务循环.is_set():
                return False

            # 最后一次等待使用剩余时间
            if i == 检查次数 - 1 and 最后等待时间 > 0:
                time.sleep(最后等待时间)
            else:
                time.sleep(检查间隔)

        return True

    except KeyboardInterrupt:
        logger.debug("等待被键盘中断")
        return False
    except Exception as e:
        logger.error(f"等待过程中发生错误: {e}")
        return False


