from datetime import datetime
from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from utils import logger,RESOURCE_DIR,time
import os
import json
import pandas as pd
from rapidfuzz import process


@AgentServer.custom_action("FlyAnswer")
class FlyAnswer(CustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        logger.info("飞飞乐脚本开始运行！")
        args = {     
            "duration": 3600,
            "n":1,
            "speed":0.5
        }
        if argv.custom_action_param is not None:
            args.update(json.loads(argv.custom_action_param))
        duration = args["duration"]
        n = args["n"]
        speed = args["speed"]
        logger.debug(f"args：{args}")

        # 读取题库
        filepath = os.path.join(RESOURCE_DIR,"text/flyquestion.csv")
        questionbank = dict(pd.read_csv(filepath).values.tolist())

        
        # 最长持续时间
        lastoutput = ""
        start = datetime.now()
        while (datetime.now() - start).total_seconds() < duration and not context.tasker.stopping:
            try:
                # 截屏读取实时题目
                img = context.tasker.controller.post_screencap().wait().get()
                taskdetail = context.run_task(
                    entry="OCR",
                    pipeline_override={"OCR":{"roi" : [250,180,750,300]}},
                    )
                recodetail = taskdetail.nodes[0].recognition
                all_results = recodetail.all_results
                alltext = "".join([_.text for _ in all_results])
                
                # 匹配题目
                best_match = process.extract(alltext, questionbank.keys(),limit=n)
                
                # 回答题目
                output = ""
                for i in range(n-1,-1,-1):
                    question = best_match[i][0]
                    answer = questionbank[question]    
                    score = best_match[i][1]
                    output += f"当前题目为：（相似度：{score:.0f}％） {question} "+f"该题答案： {answer}"
                if output != lastoutput:
                    time.sleep(speed)
                    logger.info(f"当前题目为：（相似度：{score:.0f}％）")
                    time.sleep(speed)
                    logger.info(f"{question}")
                    time.sleep(speed)
                    logger.info(f"该题答案：")
                    time.sleep(speed)
                    logger.info(f"{answer}")
                    time.sleep(speed)
                    logger.info("")
                    lastoutput = output
            except:
                pass
            time.sleep(speed)
         
        logger.info("飞飞乐脚本运行结束！")

        return CustomAction.RunResult(success=True)
