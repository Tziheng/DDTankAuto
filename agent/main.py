# -*- coding: utf-8 -*-

import os
import sys
import json
import subprocess
from pathlib import Path
import re
import math


# utf-8
sys.stdout.reconfigure(encoding="utf-8")

# 获取当前main.py路径并设置上级目录为工作目录
current_file_path = os.path.abspath(__file__)
current_script_dir = os.path.dirname(current_file_path)  # 包含此脚本的目录
project_root_dir = os.path.dirname(current_script_dir)  # 假定的项目根目录

# 更改CWD到项目根目录
if os.getcwd() != project_root_dir:
    os.chdir(project_root_dir)
print(f"set cwd: {os.getcwd()}")

# 将脚本自身的目录，和项目目录添加到sys.path，以便导入utils、maa等模块
sys.path.insert(0, current_script_dir)
sys.path.insert(0, project_root_dir)

from utils import logger


VENV_NAME = ".venv"  # 虚拟环境目录的名称
VENV_DIR = Path(project_root_dir) / VENV_NAME

### 虚拟环境相关 ###


def _is_running_in_our_venv():
    """检查脚本是否在此脚本管理的特定venv中运行。"""
    current_python = Path(sys.executable).resolve()

    logger.debug(f"当前Python解释器: {current_python}")

    if sys.platform.startswith("win"):
        # Windows: 如果在虚拟环境中，Python应该在 Scripts 目录下
        if current_python.parent.name == "Scripts":
            return True
        else:
            logger.debug("当前不在目标虚拟环境中")
            return False
    else:
        # Linux/Unix: 如果在虚拟环境中，Python应该在 bin 目录下
        if current_python.parent.name == "bin":
            return True
        else:
            logger.debug("当前不在目标虚拟环境中")
            return False


def ensure_venv_and_relaunch_if_needed():
    """
    确保venv存在，并且如果尚未在脚本管理的venv中运行，
    则在其中重新启动脚本。支持Linux和Windows系统。
    """
    logger.info(f"检测到系统: {sys.platform}。当前Python解释器: {sys.executable}")

    if _is_running_in_our_venv():
        logger.info(f"已在目标虚拟环境 ({VENV_DIR}) 中运行。")
        return

    if not VENV_DIR.exists():
        logger.info(f"正在 {VENV_DIR} 创建虚拟环境...")
        try:
            # 使用当前运行此脚本的Python（系统/外部Python）
            subprocess.run(
                [sys.executable, "-m", "venv", str(VENV_DIR)],
                check=True,
                capture_output=True,
            )
            logger.info(f"创建成功")
        except subprocess.CalledProcessError as e:
            logger.error(
                f"创建失败: {e.stderr.decode(errors='ignore') if e.stderr else e.stdout.decode(errors='ignore')}"
            )
            logger.error("正在退出")
            sys.exit(1)
        except FileNotFoundError:
            logger.error(
                f"命令 '{sys.executable} -m venv' 未找到。请确保 'venv' 模块可用。"
            )
            logger.error("无法在没有虚拟环境的情况下继续。正在退出。")
            sys.exit(1)

    if sys.platform.startswith("win"):
        python_in_venv = VENV_DIR / "Scripts" / "python.exe"
    else:
        python3_path = VENV_DIR / "bin" / "python3"
        python_path = VENV_DIR / "bin" / "python"
        if python3_path.exists():
            python_in_venv = python3_path
        elif python_path.exists():
            python_in_venv = python_path
        else:
            python_in_venv = python3_path  # 默认使用python3，让后续错误处理捕获

    if not python_in_venv.exists():
        logger.error(f"在虚拟环境 {python_in_venv} 中未找到Python解释器。")
        logger.error("虚拟环境创建可能失败或虚拟环境结构异常。")
        sys.exit(1)

    logger.info(f"正在使用虚拟环境Python重新启动")

    try:
        cmd = [str(python_in_venv)] + sys.argv
        logger.info(f"执行命令: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            cwd=os.getcwd(),
            env=os.environ.copy(),
            check=False,  # 不在非零退出码时抛出异常
        )
        # 退出时使用子进程的退出码
        sys.exit(result.returncode)

    except Exception as e:
        logger.exception(f"在虚拟环境中重新启动脚本失败: {e}")
        sys.exit(1)


### 配置相关 ###




def read_pip_config() -> dict:
    config_dir = Path("./config")
    config_dir.mkdir(exist_ok=True)
    config_path = config_dir / "pip_config.json"
    default_config = {
        "enable_pip_install": True,
        "mirror": "https://pypi.tuna.tsinghua.edu.cn/simple",
        "backup_mirror": "https://mirrors.ustc.edu.cn/pypi/simple",
    }
    if not config_path.exists():
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        return default_config
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        logger.exception("读取pip配置失败，使用默认配置")
        return default_config


### 依赖安装相关 ###


def find_local_wheels_dir():
    """查找本地deps目录中的whl文件"""
    project_root = Path(project_root_dir)
    deps_dir = project_root / "deps"

    if deps_dir.exists() and any(deps_dir.glob("*.whl")):
        whl_count = len(list(deps_dir.glob("*.whl")))
        logger.info(f"发现本地deps目录包含 {whl_count} 个 whl 文件")
        return deps_dir

    logger.debug("未找到deps目录或目录中无 whl 文件")
    return None


def _run_pip_command(cmd_args: list, operation_name: str) -> bool:
    try:
        logger.info(f"开始 {operation_name}")
        logger.debug(f"执行命令: {' '.join(cmd_args)}")

        # 使用subprocess.Popen进行实时输出
        process = subprocess.Popen(
            cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # 将stderr重定向到stdout
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,  # 行缓冲
            universal_newlines=True,
        )

        # 收集所有输出用于日志记录
        all_output = []

        # 实时读取并显示输出
        for line in iter(process.stdout.readline, ""):
            line = line.rstrip("\n\r")
            if line.strip():  # 只显示非空行
                print(line)  # 实时显示到终端
                all_output.append(line)  # 收集到列表中

        # 等待进程结束
        return_code = process.wait()

        # 记录完整输出到日志
        if all_output:
            full_output = "\n".join(all_output)
            logger.debug(f"{operation_name} 输出:\n{full_output}")

        if return_code == 0:
            logger.info(f"{operation_name} 完成")
            return True
        else:
            logger.error(f"{operation_name} 时出错。返回码: {return_code}")
            return False

    except Exception as e:
        logger.exception(f"{operation_name} 时发生未知异常: {e}")
        return False


def install_requirements(req_file="requirements.txt", pip_config=None) -> bool:
    req_path = Path(project_root_dir) / req_file  # 确保相对于项目根目录
    if not req_path.exists():
        logger.error(f"{req_file} 文件不存在于 {req_path.resolve()}")
        return False

    # 查找本地deps目录
    deps_dir = find_local_wheels_dir()
    if deps_dir:
        logger.info(f"使用本地 whl 文件安装，目录: {deps_dir}")

        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-U",
            "-r",
            str(req_path),
            "--no-warn-script-location",
            "--break-system-packages",
            "--find-links",
            str(deps_dir),  # pip会优先使用这里的文件
            "--no-index",  # 禁止在线索引
        ]

        if _run_pip_command(cmd, f"从本地deps安装依赖"):
            return True
        else:
            logger.warning("本地deps安装失败，回退到纯在线安装")

    # 回退到在线安装
    primary_mirror = pip_config.get("mirror", "")
    backup_mirror = pip_config.get("backup_mirror", "")

    if primary_mirror:
        # 使用主镜像源，只添加一个备用源避免冲突
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-U",
            "-r",
            str(req_path),
            "--no-warn-script-location",
            "--break-system-packages",
            "-i",
            primary_mirror,
        ]

        # 只添加一个备用源
        if backup_mirror:
            cmd.extend(["--extra-index-url", backup_mirror])
            logger.info(f"使用主源 {primary_mirror} 和备用源 {backup_mirror} 安装依赖")
        else:
            logger.info(f"使用主源 {primary_mirror} 安装依赖")

        if _run_pip_command(cmd, f"从 {req_path.name} 安装依赖"):
            return True
        else:
            logger.error("在线安装失败")
            return False
    else:
        # 如果没有配置主镜像源，使用pip的本地全局配置
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-U",
            "-r",
            str(req_path),
            "--no-warn-script-location",
            "--break-system-packages",
        ]

        if _run_pip_command(cmd, f"从 {req_path.name} 安装依赖 (本地全局配置)"):
            return True
        else:
            logger.error("使用pip本地全局配置安装失败")
            return False


def check_and_install_dependencies():
    """检查并安装项目依赖"""
    pip_config = read_pip_config()
    enable_pip_install = pip_config.get("enable_pip_install", True)

    logger.info(f"启用 pip 安装依赖: {enable_pip_install}")

    if enable_pip_install:
        logger.info("开始安装/更新依赖")
        if install_requirements(pip_config=pip_config):
            logger.info("依赖检查和安装完成")
        else:
            logger.warning("依赖安装失败，程序可能无法正常运行")
    else:
        logger.info("Pip 依赖安装已禁用，跳过依赖安装")


### 核心业务 ###


def agent(is_dev_mode=False):
    try:
        # 清理模块缓存
        utils_modules = [
            name for name in list(sys.modules.keys()) if name.startswith("utils")
        ]
        for module_name in utils_modules:
            del sys.modules[module_name]

        # 动态导入 utils 的所有内容
        import utils
        import importlib

        importlib.reload(utils)

        # 将 utils 的所有公共属性导入到当前命名空间
        for attr_name in dir(utils):
            if not attr_name.startswith("_"):
                globals()[attr_name] = getattr(utils, attr_name)

        if is_dev_mode:
            from utils.logger import change_console_level

            change_console_level("DEBUG")
            logger.info("开发模式：日志等级已设置为DEBUG")

        from maa.agent.agent_server import AgentServer
        from maa.toolkit import Toolkit

        import custom

        Toolkit.init_option("./")

        if len(sys.argv) < 2:
            logger.error("缺少必要的 socket_id 参数")
            return

        socket_id = sys.argv[-1]
        logger.info(f"socket_id: {socket_id}")

        AgentServer.start_up(socket_id)
        logger.info("AgentServer启动")
        AgentServer.join()
        AgentServer.shut_down()
        logger.info("AgentServer关闭")
    except ImportError as e:
        logger.error(f"导入模块失败: {e}")
        logger.error("考虑重新配置环境")
        sys.exit(1)
    except Exception as e:
        logger.exception("agent运行过程中发生异常")
        raise

# 调整窗口大小等功能

def list_all_windows():
    import win32gui
    import win32con
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

        import win32gui
        import win32con
 
        win32gui.SetWindowPos(
            hwnd, None,
            left, top,  # 保持位置不变
            target_width + border_width, target_height + border_height,  # 设置新宽度，保持原高度
            win32con.SWP_NOMOVE | win32con.SWP_NOZORDER
        )


### 程序入口 ###


def main():
    is_dev_mode = os.path.exists(".vscode") or os.path.exists(".github")
    # # 如果是Linux系统，启动虚拟环境
    # if sys.platform.startswith("linux"):
    #     ensure_venv_and_relaunch_if_needed()
    check_and_install_dependencies()

    if is_dev_mode:
        logger.info(f"set cwd: {os.getcwd()}")

    logger.info("已经将以下窗口调整至合适大小")

    # 执行公告的转换  
    try:
        from utils import RESOURCE_DIR
        folder_path = os.path.join(RESOURCE_DIR, "Announcement")
        batch_convert_directory(folder_path)
    except:
        pass

    # 执行窗口大小调整
    try:
        resize_notepad_width()
    except:
        logger.error("调整窗口大小失败，可能是权限不足，请以管理员身份运行！")
        return 0
    


    agent(is_dev_mode=is_dev_mode)


if __name__ == "__main__":
    main()
    
