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
    ) -> bool:
        logger.debug("FightAgent is running!")
        logger.debug(argv.custom_action_param)
        
        args = {
            "mode":0,
            "times":1
        }       
        args.update(json.loads(argv.custom_action_param))
        logger.debug(args)

        times = args["times"]
        mode = args["mode"]

        if mode == 0:
            for i in range(times):
                logger.info(f"开始执行第{i+1}次竞技场自埋任务！")
                context.run_task("竞技场")

            context.run_task("房间页面-结束任务")
        if mode == 1:
            for i in range(times):
                logger.info(f"开始执行第{i+1}次多人副本任务！")
                context.run_task("多人副本")

            context.run_task("房间页面-结束任务")

        return CustomAction.RunResult(success=True)
