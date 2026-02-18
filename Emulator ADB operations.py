import subprocess
import time
import logging
from pathlib import Path
import sys

logger = logging.getLogger(__name__)


def long_press(adb_config, x, y, duration=1000):
    """
    Long press on specified screen coordinates

    Args:
        adb_config: Tuple containing (adb_path, port)
        x: X coordinate to press
        y: Y coordinate to press
        duration: Press duration in milliseconds (default: 1000)
    """
    adb_path, port = adb_config
    adb_command = f'"{adb_path}" -s {port} shell input swipe {x} {y} {x} {y} {duration}'
    subprocess.run(adb_command, shell=True)
    time.sleep(0.005)


def swipe(adb_config, x1, y1, x2, y2, duration=200):
    """
    Swipe between two points on the device screen

    Args:
        adb_config: Tuple containing (adb_path, port)
        x1: Start X coordinate
        y1: Start Y coordinate
        x2: End X coordinate
        y2: End Y coordinate
        duration: Swipe duration in milliseconds (default: 200)
    """
    adb_path, port = adb_config
    adb_command = f'"{adb_path}" -s {port} shell input swipe {x1} {y1} {x2} {y2} {duration}'
    subprocess.run(adb_command, shell=True)


def launch_app(adb_config, package_name):
    """
    Launch application by package name

    Args:
        adb_config: Tuple containing (adb_path, port)
        package_name: Android application package name to launch
    """
    adb_path, port = adb_config
    adb_command = f'"{adb_path}" -s {port} shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1'
    subprocess.run(adb_command, shell=True)
    time.sleep(3)


def close_app(adb_config, package_name):
    """
    Force stop application

    Args:
        adb_config: Tuple containing (adb_path, port)
        package_name: Android application package name to close
    """
    adb_path, port = adb_config
    adb_command = f'"{adb_path}" -s {port} shell am force-stop {package_name}'
    subprocess.run(adb_command, shell=True)


def get_all_device_ports(adb_path):
    """
    Get list of all connected ADB device ports/serial numbers

    Args:
        adb_path: Path to adb executable

    Returns:
        list: Device port/serial numbers in format like ["emulator-5554", "127.0.0.1:16384"]
    """
    try:
        # Execute adb devices command
        adb_command = f'"{adb_path}" devices'
        output = subprocess.check_output(
            adb_command,
            shell=True,
            text=True,
            encoding='utf-8'
        )

        device_list = []
        for line in output.splitlines():
            # Skip empty lines and header
            if line.strip() == "" or "List of devices" in line:
                continue

            # Parse device information
            parts = line.strip().split('\t')
            if len(parts) >= 2 and parts[1] == 'device':
                device_list.append(parts[0])

        return device_list

    except subprocess.CalledProcessError as e:
        logger.error(f"ADB命令执行失败: {e}")
        return []
    except Exception as e:
        logger.error(f"未知错误: {e}")
        return []


def connect_emulator(current_dir, i):
    """
    Connect to emulator and return success status

    Args:
        current_dir: Current working directory path
        i: Index for calculating port number

    Returns:
        bool: True if connection successful, False otherwise
    """
    app_path = current_dir / "platform-tools" / "adb.exe"

    base_port = 16384
    command = [app_path, 'connect', f"127.0.0.1:{base_port + 32 * i}"]
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    if result.stdout is not None and 'connected' in result.stdout:
        logger.debug("成功连接到模拟器")
        return True
    else:
        # Try alternative port
        command = [app_path, 'connect', f"127.0.0.1:{base_port + 1 + 32 * i}"]
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        if result.stdout is not None and 'connected' in result.stdout:
            logger.debug("成功连接到模拟器")
            return True
    return False