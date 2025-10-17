from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

from utils import logger


@AgentServer.custom_action("MyCustomAction")
class MyCustomAction(CustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        logger.info("MyCustomAction is running!")
        logger.info(argv.custom_action_param)
        # argv.custom_action_param 是一个 str,用eval()解析
        logger.info(eval(argv.custom_action_param)[1])

        return CustomAction.RunResult(success=True)
