from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from maa.define import OCRResult,Rect
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
            logger.debug("农场-识别列表好友")
            if taskdetail is not None:
                recodetail = taskdetail.nodes[0].recognition
                for result in recodetail.filtered_results:
                    name_box = [result.box[0] + 80, result.box[1],result.box[2] - 80, 30]
                    name_taskdetail = context.run_task("农场-识别好友名称",pipeline_override={"农场-识别好友名称":{"roi": name_box}})
                    if name_taskdetail is not None:
                        name_recodetail = name_taskdetail.nodes[0].recognition
                        friend_name = "".join([_.text for _ in name_recodetail.all_results if isinstance(_, OCRResult)])
                        logger.info(f"好友名称={friend_name}")
                    # 如果好友不在已偷过菜的好友列表中，则偷菜
                    if friend_name not in stolen_friends:
                        stolen_friends.add(friend_name)
                        button_pos = [result.box[0]+300, result.box[1]+35, 1,1]
                        context.run_task("农场-点击好友农场",pipeline_override={"农场-点击好友农场":{"target": button_pos}})
                        self.steal_vegetables(context)
                    else:
                        context.run_task("农场-下滑好友列表")
            time.sleep(1)

        logger.info("偷菜脚本运行结束！")

        return CustomAction.RunResult(success=True)
    
    def get_target_vegetables(self,context:Context) -> list[list]:
        # 获得目标菜的坐标
        logger.info("识别目标菜中...")
        taskdetail = context.run_task("农场-识别目标菜")
        if taskdetail is not None and taskdetail.nodes:
            recognition = taskdetail.nodes[0].recognition
            if recognition is not None:
                return [[_.box[0]+_.box[2]/2,_.box[1] + _.box[3],0,0] for _ in recognition.filtered_results]
        logger.info("未识别到目标菜")
        return []
    
    def steal_vegetables(self,context:Context):
        """偷菜逻辑"""
        logger.info("开始偷菜...")
        context.run_task("农场-一键浇水")
        target_vegetables = self.get_target_vegetables(context)
        for pos in target_vegetables:
            context.run_task("农场-点击菜",pipeline_override={"农场-点击菜":{"target": pos}})
           
        logger.info("偷菜完成！")
        context.run_task("农场-点击退出")
        
        