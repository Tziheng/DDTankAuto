from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from utils import logger
import json

@AgentServer.custom_action("FightAgent")
class FightAgent(CustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:
        logger.debug("FightAgent is running!")
        logger.debug(argv.custom_action_param)
        
        args = {
            "mode":0,
            "times":1
        }       
        if argv.custom_action_param is not None:
            args.update(json.loads(argv.custom_action_param))
        logger.debug(args)

        times = args["times"]
        mode = args["mode"]

        if mode == 0:
            logger.info(f"开始执行竞技场自埋任务，共计{times}次！")
        else:
            logger.info(f"开始执行多人副本任务，共计{times}次！")
        logger.info("注意停止任务时，需要完整的完成当前关卡后，该任务才会停止！")
        
        for i in range(times):
            if context.tasker.stopping:
                logger.info("任务已停止")
                return CustomAction.RunResult(success=False)
            if mode == 0:
                logger.info(f"开始执行第{i+1}次竞技场自埋任务！")
                context.run_task("竞技场")
            else:
                logger.info(f"开始执行第{i+1}关多人副本任务！")
                context.run_task("多人副本")
        context.run_task("房间页面-结束任务")

        return CustomAction.RunResult(success=True)
