from math import log
from .logger import *
from .config import PROJECT_DIR, RESOURCE_DIR
from .time import *

try:
    from .setWindows import *
except ImportError:
    logger.warning("some utils model import failed")



