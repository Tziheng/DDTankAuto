from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from PIL import Image
from utils import logger,time,RESOURCE_DIR
import os
import json

@AgentServer.custom_action("ShowLike")
class ShowLike(CustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        logger.debug(f"ShowLike run !") 
        logger.debug(argv.custom_action_param)
        
        args = {
            "target": [475, 565],
            "path": f"{RESOURCE_DIR}/image/show_output/",
            "msg": "save show img"
        }       
        args.update(json.loads(argv.custom_action_param))
        target = args["target"]
        path = args["path"].format(**globals())
        logger.debug(args)
        
        if target == [475, 565]:
            logger.info("正在执行点赞操作")
            # 点赞，长按0.2秒
            context.tasker.controller.post_touch_down(x=target[0], y=target[1]).wait()
            time.sleep(0.2)
            context.tasker.controller.post_touch_up().wait()


        # 截图并保存
        # 获得上次识别结果的相似度
        node = context.tasker.get_latest_node("弹弹选秀-识别到自己装扮")
        reco = node.recognition
        source = reco.best_result.score
        logger.info(f"识别结果相似度为{source*100:.2f}％")

        if path[-1] == "/" or path[-1] == "\\":
            path = os.path.join(path, f"time_{time.get_current_time()}_similarity_{source}.png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        

        screen_array = context.tasker.controller.cached_image
        logger.debug(f"screen_array shape: {screen_array.shape}")

        height, width = screen_array.shape[:2]

        x, y, w, h = 0, 0, width, height
        # BGR2RGB
        if len(screen_array.shape) == 3 and screen_array.shape[2] == 3:
            rgb_array = screen_array[y:y+h, x:x+w, ::-1]
        else:
            rgb_array = screen_array[y:y+h, x:x+w]
            logger.warning("当前截图并非三通道")

        img = Image.fromarray(rgb_array)
        img.save(path)

        logger.info(f"保存点赞图片至{path}")
        

        return True
