from .logger import *

try:
    from .time import *
except ImportError:
    logger.warning("utils moudule import failed")



current_file_path = os.path.abspath(__file__)
utils_dir = os.path.dirname(current_file_path)  # 包含此脚本的目录
agent_dir = os.path.dirname(utils_dir)  #  
project_dir = os.path.dirname(agent_dir)  # 项目根目录

PROJECT_DIR = project_dir
RESOURCE_DIR  = os.path.join(PROJECT_DIR, "resource")
