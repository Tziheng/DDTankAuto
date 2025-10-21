from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from utils import logger,time,RESOURCE_DIR
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
            "n":3,
        }
        args.update(json.loads(argv.custom_action_param))
        duration = args["duration"]
        n = args["n"]
        logger.debug(f"args：{args}")

        # 读取题库
        filepath = os.path.join(RESOURCE_DIR,"text/flyquestion.csv")
        questionbank = dict(pd.read_csv(filepath).values.tolist())

        logger.debug(f"题库：{questionbank}")
        
        # 最长持续时间
        cnt = 0
        while cnt < duration:
            # 截屏读取实时题目
            img = context.tasker.controller.post_screencap().wait().get()
            recodetail = context.run_recognition(
                entry="OCR",
                pipeline_override={"OCR":{"roi" : [250,180,750,300]}},
                image=img,
                )
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
                output += f"\n当前题目为：（置信度：{score:.0f}％）\n{question}\n"+f"该题答案：\n{answer}\n"
            logger.info("\n"+"="*15+output+"="*15)
            time.sleep(3)
            cnt += 3
         
        logger.info("飞飞乐脚本运行结束！")

        return CustomAction.RunResult(success=True)
