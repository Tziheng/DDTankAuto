from .logger import *

try:
    from .time import *
except ImportError:
    logger.warning("utils moudule import failed")




PROJECT_DIR = sys.path[0]
RESOURCE_DIR = os.path.join(sys.path[0], "resource")
