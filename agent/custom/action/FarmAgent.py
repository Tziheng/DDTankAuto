from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from maa.define import OCRResult
from utils import logger,time
import json
import os

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

        # 记录已偷过菜的好友
        stolen_friends = set()

        # 主循环
        while True:
            # 检查爱心值
            if not self.check_heart_value(context):
                logger.info("爱心值不足，停止偷菜")
                break

            # 查找未偷过的好友
            friend_found = False

            # 尝试点击好友
            task_detail = context.run_task("农场-点击好友")
            if task_detail and task_detail.success:
                logger.info("找到好友，准备进入农场")
                friend_found = True

                # 进入好友家园
                home_detail = context.run_task("农场-进入好友家园")
                if home_detail and home_detail.success:
                    # 进入农场
                    farm_detail = context.run_task("农场-进入农场")
                    if farm_detail and farm_detail.success:
                        # 进入菜园
                        garden_detail = context.run_task("农场-进入菜园")
                        if garden_detail and garden_detail.success:
                            # 偷菜
                            self.steal_vegetables(context)
                        else:
                            logger.warning("无法进入菜园")
                    else:
                        logger.warning("无法进入农场")
                else:
                    logger.warning("无法进入好友家园")

                # 返回好友列表
                context.run_task("农场-返回好友列表")
            else:
                logger.info("未找到好友，尝试下滑列表")
                # 下滑好友列表
                scroll_detail = context.run_task("农场-好友列表下滑")
                if not scroll_detail or not scroll_detail.success:
                    logger.info("好友列表已到底，停止偷菜")
                    break

            if not friend_found:
                logger.info("没有可偷菜的好友，停止偷菜")
                break

            time.sleep(1)

        return CustomAction.RunResult(success=True)

    def check_heart_value(self, context):
        """检查爱心值是否足够"""
        try:
            # 截屏读取爱心值
            img = context.tasker.controller.post_screencap().wait().get()
            task_detail = context.run_task(
                entry="OCR",
                pipeline_override={"OCR":{"roi" : [10, 100, 100, 50]}},
            )
            if task_detail is not None:
                recodetail = task_detail.nodes[0].recognition
                all_results = recodetail.all_results
                alltext = "".join([_.text for _ in all_results if isinstance(_, OCRResult)])

                # 查找爱心值信息，例如 "50/50"
                if "/" in alltext:
                    heart_info = alltext.split("/")[0]
                    heart_value = int(heart_info)
                    logger.info(f"当前爱心值: {heart_value}")
                    return heart_value > 0
        except Exception as e:
            logger.debug(f"检查爱心值时出错: {e}")
        # 如果无法识别，默认继续
        return True

    def steal_vegetables(self, context):
        """偷取成熟的蔬菜"""
        try:
            # 寻找可偷取的蔬菜
            while True:
                # 查找收割符号
                harvest_detail = context.run_task("农场-查找收割符号")
                if harvest_detail and harvest_detail.success:
                    logger.info("找到可偷取的蔬菜")
                    # 点击镰刀偷取
                    sickle_detail = context.run_task("农场-点击镰刀")
                    if sickle_detail and sickle_detail.success:
                        logger.info("偷取蔬菜成功")
                    time.sleep(0.5)
                else:
                    logger.info("没有可偷取的蔬菜")
                    break
        except Exception as e:
            logger.debug(f"偷菜时出错: {e}")
