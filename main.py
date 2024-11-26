from gemini import generate
import csv, json

first_generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0,
    "top_p": 0.95,
    "response_mime_type": "application/json",
    "response_schema": {"type":"OBJECT","properties":{"label":{"type":"STRING"},"reason":{"type":"STRING"}}},
}

second_generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
    "response_mime_type": "application/json",
    "response_schema": {"type":"OBJECT","properties":{"first_level_sub_category":{"type":"STRING"},"second_level_sub_category":{"type":"STRING"},"reason":{"type":"STRING"}}},
}

subcategories = []
contents = []

with open('data/label_rules.json', 'r') as file:
    label_rules = json.load(file)


file =  open('data/cs_qadata_fortest1.csv',encoding='utf-8')
line = csv.reader(file)
next(line)
for row in line:
    id = row[0]
    user_result = row[1]
    user_comment = row[2]
    user_label = row[3]
    content = row[4]
    contents.append(content)
    prompt1 = """
你是一位经验丰富的游戏客服对话分类专家。你的任务是将用户与客服的对话准确分类到预定义类别中。请仔细分析问题内容,考虑关键词和上下文,然后输出符合要求的JSON格式回复。

<输入对话>
""" + content + """
</输入对话>

<候选类别>
充值问题: 包括各种支付平台未到账、充值失败、退款申请、恶意退款、商品信息获取问题、充值限制、第三方充值渠道相关问题等（通常表现为有“支付”或者“充值”这些关键词）。
特殊问题: 包括游戏建议反馈、兑换码使用、预约奖励领取、道具兑换错误(如星轨专票/通票兑换错误)等非常规问题。
法务相关问题: 涉及举报(如侵权、泄露、账号交易等)、数据披露等法律相关问题。
HoYoLAB问题: 涉及HoYoLAB社区和工具(如崩坏：星穹铁道地图)使用的相关问题。
账号问题: 包括账号安全(如被盗)、登录异常、信息修改(如改生日)、账号绑定解绑、忘记密码、验证码问题、账号注销、PSN相关问题等。
活动问题: 主要涉及游戏内版本活动的相关问题,如活动奖励、活动任务、活动规则等（通常表现为有“活动/事件/event/quest"这些关键词）。
游戏问题: 包括游戏系统(如跃迁、成就、模拟宇宙、背包、道具、商店、合成、养成功能等)、战斗及角色/怪物表现、任务流程(开拓、冒险、日常、活动任务等)、迷宫关卡(解密玩法、地图场景、物件表现等)、客户端问题(闪退、崩溃、显示异常、性能/卡顿、声音异常、手柄问题等)、游戏内本地化相关(文本翻译、配音等)、启动器问题等游戏内容和技术相关问题。
</候选类别>

<注意事项>
- 活动问题优先级高于游戏问题，如果同时符合两者，则为活动问题。
- 理由应简洁明了,引用原文关键词或短语
- 如果无法确定分类,选择最相关的类别并详细说明原因
- 结合整个问题的上下文来判断类别,不要仅依赖单个词语
- 如果问题涉及多个方面,优先选择最主要或最核心的问题类别
- 注意识别用户的具体诉求,而不仅仅是问题中提到的表面内容
</注意事项>

"""
    try:
        response = generate(prompt=prompt1,generation_config=first_generation_config)
        first_label = response['label']
        first_label = first_label.replace("\"","").replace(r"\n","").strip()
        # reason = response['reason']
        # reason = reason.replace("\"","").replace(r"\n","").strip()
        # with open('data/first_label.txt','a') as f:
        #     f.write(id + "|" + first_label + "|" + user_label + "|" + reason + "\n")
    except Exception as e:
        print(e)

    subcategories = json.dumps(label_rules[first_label],ensure_ascii=False)

    prompt2 = """
你是一位精通游戏行业的AI助手，专门负责分析和分类游戏客服对话。你的任务是将给定的对话准确分类到预定义的一级和二级子类别中。请遵循以下步骤：

1. 仔细阅读整个对话，理解玩家的问题和客服的回应。
2. 识别对话中的关键词、短语和主题。
3. 考虑游戏相关的上下文和常见问题类型。
4. 从候选类别中选择最匹配的一级和二级子类别。
5. 提供简洁但有力的理由，引用对话中的具体内容。

<输入对话>
""" + content + """
</输入对话>

<候选子类别格式说明>
候选子类别是一个嵌套的JSON对象，结构如下：
{
    "一级子分类1": {
    "二级子分类1": "二级子分类1的描述",
    "二级子分类2": "二级子分类2的描述",
    ...
    },
    "一级子分类2": {
    "二级子分类1": "二级子分类1的描述",
    "二级子分类2": "二级子分类2的描述",
    ...
    },
    ...
}

每个一级子分类包含多个二级子分类，每个二级类别下都有其描述。
在分类时，你只需要选择一级子分类和二级子分类。
</候选子类别格式说明>

<候选子类别>
""" + subcategories + """
</候选子类别>

注意事项：
- 二级分类必须在一级分类下选择。
- 确保选择的类别与对话内容高度相关。
- 理由应当简洁明了，直接引用对话中的关键内容。
- 如果对话涉及多个主题，请选择最主要或最重要的一个进行分类。
    """
    try:    
        response = generate(prompt=prompt2, generation_config=second_generation_config)
        print(response)
        second_label = response['first_level_sub_category']
        second_label = second_label.replace("\"","").replace(r"\n","").strip()
        third_label = response['second_level_sub_category']
        third_label = third_label.replace("\"","").replace(r"\n","").strip()
        reason = response['reason']
        reason = reason.replace("\"","").replace(r"\n","").strip()
        with open('data/compare_result.txt','a') as f:
            f.write(id + "|" + user_label + "|" + first_label + "|" + second_label + "|" + third_label + "|" + reason + "\n")
    except Exception as e:
        print(e)
    finally:
        f.close()