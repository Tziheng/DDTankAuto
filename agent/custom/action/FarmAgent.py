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
    ) -> bool:
        logger.debug("FarmAgent is running!")
        logger.debug(argv.custom_action_param)
        args = {
            "time":3600,
        }       
        if argv.custom_action_param is not None:
            args.update(json.loads(argv.custom_action_param))
        logger.debug(args)

        start_time = time.get_current_time()

        while time.get_current_time() - start_time < args["time"]:

            if context.tasker.stopping:
                logger.info("FarmAgent is stopping!")
                return CustomAction.RunResult(success=False)

            






        return CustomAction.RunResult(success=True)