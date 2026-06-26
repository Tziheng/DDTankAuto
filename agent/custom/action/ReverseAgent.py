from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from utils import logger, time
import json
import keyboard


_KEY_MAP = {
    "w": "s", "s": "w", "a": "d", "d": "a",
    "up": "down", "down": "up", "left": "right", "right": "left",
}


@AgentServer.custom_action("ReverseAgent")
class ReverseAgent(CustomAction):

    def __init__(self):
        super().__init__()
        self.reverse_flag = False
        self.on_button = "-"
        self.off_button = "="
        self._pressed = set()

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:
        logger.info("翻转代理脚本开始运行！")
        args = {"on_button": "-", "off_button": "="}
        if argv.custom_action_param is not None:
            args.update(json.loads(argv.custom_action_param))
        self.on_button = args["on_button"]
        self.off_button = args["off_button"]
        logger.debug(f"args：{args}")

        def hook_handler(event):
            key_name = event.name
            is_keyup = event.event_type == keyboard.KEY_UP

            # 开关按键（只处理按下）
            if not is_keyup:
                if key_name == self.on_button:
                    self.reverse_flag = True
                    logger.info(f"翻转已开启（按下 {self.on_button}）")
                    return False  # suppress，拦截
                if key_name == self.off_button:
                    self.reverse_flag = False
                    logger.info(f"翻转已关闭（按下 {self.off_button}）")
                    return False

            if self.reverse_flag and key_name in _KEY_MAP:
                rev_key = _KEY_MAP[key_name]
                if not is_keyup:
                    logger.debug(f"翻转: {key_name} → {rev_key}")
                    keyboard.send(rev_key, do_press=True, do_release=False)
                    self._pressed.add(rev_key)
                else:
                    if rev_key in self._pressed:
                        logger.debug(f"翻转释放: {rev_key}")
                        keyboard.send(rev_key, do_press=False, do_release=True)
                        self._pressed.discard(rev_key)
                return False  # suppress，拦截原键

            return True  # 不拦截

        hook = keyboard.hook(hook_handler, suppress=True)

        while not context.tasker.stopping:
            time.sleep(1)

        keyboard.unhook(hook)
        logger.info("翻转代理脚本运行结束！")
        return CustomAction.RunResult(success=True)
