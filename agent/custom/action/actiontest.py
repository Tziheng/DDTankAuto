from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

from utils import logger,time


@AgentServer.custom_action("MyCustomAction")
class MyCustomAction(CustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        logger.info("MyCustomAction is running!")
        logger.info(argv.custom_action_param)
        for i in range(1000):
            logger.debug(f"Debug message {i}")
            if context.tasker.stopping:
                logger.info("MyCustomAction is stopping!")
                return CustomAction.RunResult(success=False)
            time.sleep(1)
        

        return CustomAction.RunResult(success=True)
