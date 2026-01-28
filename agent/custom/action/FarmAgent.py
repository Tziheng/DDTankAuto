from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from maa.define import OCRResult
from utils import logger,time
import json
from datetime import datetime


@AgentServer.custom_action("FarmAgent")
class FarmAgent(CustomAction):
    def run(
            self,
            context: Context,
            argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:
        logger.debug("FarmAgent is running!")
        logger.debug(argv.custom_action_param)
        args = {
            "duration":3600,
        }
        if argv.custom_action_param is not None:
            args.update(json.loads(argv.custom_action_param))
        logger.debug(args)

        duration = args["duration"]

        # 记录已偷过菜的好友
        stolen_friends = set()

        # 在持续事件内
        start = datetime.now()
        friend_name = ""
        while (datetime.now() - start).total_seconds() < duration and not context.tasker.stopping:
            
            # 识别列表好友
            taskdetail = context.run_task("农场-识别列表好友")
            if taskdetail is not None:
                recodetail = taskdetail.nodes[0].recognition
                for result in recodetail.all_results:
                    result_pos = result.box.x, result.box.y
                   # 通过偏移量获取好友名称所在位置
                   # name_box框的大小位置计算一下
                    name_box = [result_pos[0]+1, result_pos[1]+2, 1,2]
                    name_taskdetail = context.run_task("农场-识别好友名称",pipeline_override={"农场-识别好友名称":{"roi": name_box}})
                    if name_taskdetail is not None:
                        name_recodetail = name_taskdetail.nodes[0].recognition
                        friend_name = "".join([_.text for _ in name_recodetail.all_results if isinstance(_, OCRResult)])
                    # 如果好友不在已偷过菜的好友列表中，则偷菜
                    if friend_name not in stolen_friends:
                        # 点击访问家园按钮
                        button_pos = [result_pos[0]+1, result_pos[1]+2, 1,2]
                        context.run_task("农场-点击好友农场",pipeline_override={"农场-点击好友农场":{"target": button_pos}})
                    else:
                        # 如果列表里全部偷过菜
                        # 则下滑
                        # 如果下滑后依旧没有新好友，则上滑持续一分钟，stolen_friends清空
                        pass
            time.sleep(1)

        logger.info("偷菜脚本运行结束！")

        return CustomAction.RunResult(success=True)
    
    def get_target_vegetables(self,context:Context) -> list[list]:
        # 获得目标菜的坐标
        context.run_task("农场-识别目标菜")
        return [[1,2,3,4],[5,6,7,8]]
    
    def steal_vegetables(self,context:Context):
        """偷菜逻辑"""
        logger.info("开始偷菜...")
        target_vegetables = self.get_target_vegetables(context)
        for pos in target_vegetables:
            context.run_task("农场-点击菜",pipeline_override={"农场-点击菜":{"target": pos}})
           
        logger.info("偷菜完成！")
        
        