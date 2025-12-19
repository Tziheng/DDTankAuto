from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from utils import logger
import json

@AgentServer.custom_action("SpireAgent")
class SpireAgent(CustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:
        logger.debug("SpireAgent is running!")
        logger.debug(argv.custom_action_param)
        
       

        return CustomAction.RunResult(success=True)
