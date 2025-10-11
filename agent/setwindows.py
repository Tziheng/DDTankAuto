# 调整窗口大小等功能

from .utils.logger import logger

def list_all_windows():
    import win32gui
    import win32process

    """列出所有顶级窗口的标题、句柄、类名、位置尺寸、进程ID及进程名称、EXE路径"""
    windows = []
    def callback(hwnd, results):
        """回调函数：收集窗口详细信息"""
        if win32gui.IsWindowVisible(hwnd):  # 仅获取可见窗口（可选）
            title = win32gui.GetWindowText(hwnd)
            if title:  # 过滤空标题窗口
                # 获取窗口类名
                class_name = win32gui.GetClassName(hwnd)
                # 获取窗口位置和尺寸
                rect = win32gui.GetWindowRect(hwnd)
                left, top, right, bottom = rect
                width = right - left
                height = bottom - top
                # 获取进程ID
                _, process_id = win32process.GetWindowThreadProcessId(hwnd)
                # 将信息存入字典
                window_info = {
                    "handle": hwnd,
                    "title": title,
                    "class_name": class_name,
                    "position": (left, top),
                    "size": (width, height),
                    "process_id": process_id
                }
                windows.append(window_info)
        return True  # 继续枚举
    win32gui.EnumWindows(callback, windows)  # 枚举所有顶级窗口
    return windows

def list_windows_by_title(title):
  
    import re

    selected_windows = []
    """根据窗口标题查找窗口句柄"""
    windows = list_all_windows()
    for window in windows:
        if re.match(title,window["title"]):
            selected_windows.append(window)
    for window in selected_windows:
        logger.info(f"""窗口信息：
        句柄: {window["handle"]}
        标题: {window["title"]}
        类名: {window["class_name"]}
        位置: {window["position"]} (尺寸: {window["size"]})
        进程ID: {window["process_id"]}""")
    return selected_windows


def detect_newline_type(file_path):
    """检测文件的换行符类型"""
    with open(file_path, 'rb') as f:
        content = f.read()
    if b'\r\n' in content:
        return 'CRLF'
    elif b'\n' in content:
        return 'LF'
    else:
        return 'Unknown'

def convert_to_crlf_if_needed(file_path):
    """转换LF文件为CRLF，CRLF文件保持不变"""
    newline_type = detect_newline_type(file_path)
    if newline_type == 'LF':
        with open(file_path, 'r', newline='',encoding='utf-8') as f:
            content = f.read()
        converted_content = content.replace('\n', '\r\n')
        with open(file_path, 'w', newline='',encoding='utf-8') as f:
            f.write(converted_content)


def batch_convert_directory(directory, extensions=['.md']):
    import os
    """批量转换目录下指定扩展名的文件"""
    for root, _, files in os.walk(directory):
        for filename in files:
            if any(filename.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, filename)
                convert_to_crlf_if_needed(file_path)
    # print("Conversion completed.")

def get_window_client_rect(hwnd):
    import win32gui
 

    """获取窗口的客户区坐标（仅内容区域）"""
    client_left, client_top, client_right, client_bottom = win32gui.GetClientRect(hwnd)
    # 转换为屏幕坐标
    screen_left, screen_top = win32gui.ClientToScreen(hwnd, (client_left, client_top))
    screen_right, screen_bottom = win32gui.ClientToScreen(hwnd, (client_right, client_bottom))
    return (screen_left, screen_top, screen_right, screen_bottom)

def resize_notepad_width():
    import math
    import win32gui
    import win32con
  
    init_target_width=1202
    init_target_height=720
    init_white_height=44
    windows = list_windows_by_title("^新弹弹堂$")
    if len(windows)==0:
        logger.warning("未找到符合条件的窗口，请确保已打开新弹弹堂窗口！")
        return
    
    for window in windows:
        hwnd = window["handle"]
            
        # 获取当前窗口位置和大小
        left, top = window["position"]
        width, height = window["size"]
        client_left, client_top, client_right, client_bottom = get_window_client_rect(hwnd)
        client_width, client_height = client_right - client_left, client_bottom - client_top
        border_width, border_height = width - client_width, height - client_height
        white_height = math.floor(client_height - 9*client_width/16)
        if abs(white_height - init_white_height) <= 2:
            white_height = init_white_height
        target_width = init_target_width*white_height//init_white_height
        target_height = init_target_height*white_height//init_white_height
        print(white_height,target_height,target_width)

 
        win32gui.SetWindowPos(
            hwnd, None,
            left, top,  # 保持位置不变
            target_width + border_width, target_height + border_height,  # 设置新宽度，保持原高度
            win32con.SWP_NOMOVE | win32con.SWP_NOZORDER
        )
