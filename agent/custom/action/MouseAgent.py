from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from utils import logger,time
import json 
import threading
from pynput import mouse, keyboard
import pyautogui




@AgentServer.custom_action("MouseAgent")
class MouseAgent(CustomAction):

    clicking = threading.Event()  # 控制连点线程的“运行/停止”标志

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:
        logger.info("连点器脚本开始运行！")
        args = {     
            "period": 100,
            "key":"`"
        }
        if argv.custom_action_param is not None:
            args.update(json.loads(argv.custom_action_param))
        logger.debug(f"args：{args}")
        self.clickPeriod = args["period"] / 1000.0  # 转换为秒
        self.key = args["key"]
        
        logger.info(f"开始连点（按住 {self.key} 持续点击，松开停止）")

        # 监听全局键盘事件
        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()

        while not context.tasker.stopping:
            time.sleep(1)

        self.clicking.clear()
        listener.stop()
        listener.join()

        logger.info("连点器脚本结束运行！")

        return CustomAction.RunResult(success=True)
    
    def get_click_position(self):
        SAFE_MARGIN = 10         # 屏幕边缘安全边距（像素）
        """返回当前鼠标位置，并确保坐标在屏幕内"""
        x, y = pyautogui.position()
        screen_w, screen_h = pyautogui.size()
        x = max(SAFE_MARGIN, min(x, screen_w - SAFE_MARGIN))
        y = max(SAFE_MARGIN, min(y, screen_h - SAFE_MARGIN))
        return x, y

    def click_loop(self):
        """在全局鼠标位置循环点击，直到 clicking 被清除"""
        while self.clicking.is_set():
            x, y = self.get_click_position()
            mouse.Controller().click(mouse.Button.left, 1)
            time.sleep(self.clickPeriod)

    def on_press(self,key):
        """键盘按下事件回调"""
        try:
            if key == keyboard.KeyCode.from_char(self.key):
                if not self.clicking.is_set():
                    self.clicking.set()
                    # 在新线程中执行点击，避免阻塞键盘监听
                    threading.Thread(target=self.click_loop, daemon=True).start()
                    
        except AttributeError:
            pass  # 忽略非字符键

    def on_release(self,key):
        """键盘释放事件回调"""
        try:
            if key == keyboard.KeyCode.from_char(self.key):
                if self.clicking.is_set():
                    self.clicking.clear()
                     
        except AttributeError:
            pass