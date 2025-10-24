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
        if argv.custom_action_param is not None:
            args.update(json.loads(argv.custom_action_param))
        logger.debug(args)

        times = args["times"]
        mode = args["mode"]

        
        for i in range(times):
            if context.tasker.stopping:
                logger.info("FightAgent is stopping!")
                return CustomAction.RunResult(success=False)
            if mode == 0:
                logger.info(f"开始执行第{i+1}次竞技场自埋任务！")
                context.run_task("竞技场")
            else:
                logger.info(f"开始执行第{i+1}关多人副本任务！")
                context.run_task("多人副本")
        context.run_task("房间页面-结束任务")

        return CustomAction.RunResult(success=True)
