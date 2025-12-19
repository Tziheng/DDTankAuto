from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from utils import logger,time
import json

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
            "time":3600,
        }       
        if argv.custom_action_param is not None:
            args.update(json.loads(argv.custom_action_param))
        logger.debug(args)

  
        return CustomAction.RunResult(success=True)