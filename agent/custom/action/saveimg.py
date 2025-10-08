from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from datetime import datetime
from PIL import Image
import sys
from utils import logger,time,RESOURCE_DIR
import os
import json

@AgentServer.custom_action("SaveImg")
class SaveImg(CustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        logger.debug("SaveImg is running!")
        logger.debug(argv.custom_action_param)
        
        args = {
            "roi": [0, 0, 0, 0],
            "path": f"{RESOURCE_DIR}/tmp/",
            "msg": "save img"
        }       
        args.update(json.loads(argv.custom_action_param))
        path = args["path"].format(**globals())
        if path[-1] == "/" or path[-1] == "\\":
            path = os.path.join(path, f"{time.get_current_time()}.png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        logger.debug(args)

        screen_array =  context.tasker.controller.post_screencap().wait().get()
        logger.debug(f"screen_array shape: {screen_array.shape}")

        height, width = screen_array.shape[:2]

        if  args["roi"] != [0, 0, 0, 0]:
            x, y, w, h = args["roi"]
            if w<=0 or h<=0 or x<0 or y<0 or x+w > width or y+h > height:
                logger.warning(f"roi超出屏幕范围,实际窗口范围为({width},{height})")
                return False
        else:
            x, y, w, h = 0, 0, width, height
        # BGR2RGB
        if len(screen_array.shape) == 3 and screen_array.shape[2] == 3:
            rgb_array = screen_array[y:y+h, x:x+w, ::-1]
        else:
            rgb_array = screen_array[y:y+h, x:x+w]
            logger.warning("当前截图并非三通道")

        img = Image.fromarray(rgb_array)
        img.save(path)

        logger.logo(f"保存图片至{path}")
        

        return True
