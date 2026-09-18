import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("llm_matcher")

client = OpenAI(
    api_key=os.environ.get("SILICONFLOW_API_KEY"),
    base_url=os.environ.get("SILICONFLOW_BASE_URL")
)

SCORE_THRESHOLD = 7  # 满分10分，达到7分才算通过（对应之前75%的门槛）


def evaluate_match(resume_text: str, job_title: str, job_description: str) -> dict:
    """
    用 LLM 评估岗位与母简历的真实匹配度，采用 1-10 分制（参考成熟开源项目的评分设计）。
    分数越离散、越真实，比0-100百分比更不容易出现"卡在中间不敢下判断"的问题。
    """
    prompt = (
        "你是一个极其严格、诚实的招聘匹配评估专家。\n\n"
        "请按以下两步评估：\n\n"
        "【第一步 - 行业前置检查（严格）】\n"
        "判断这家公司是否以AI/机器学习为核心业务，而不是仅仅是一家使用了一些科技工具的普通公司。\n"
        "判断标准：这家公司的核心产品/服务本身就是AI技术（如AI模型、AI Agent、AI基础设施、LLM应用），"
        "或者这个具体岗位的核心职责直接围绕AI产品/AI技术展开。\n\n"
        "以下情况【不算】通过（即使公司用了一些科技手段，也不算AI核心业务）：\n"
        "- 保险科技公司（如InsurTech），核心业务是保险，不是AI\n"
        "- 支付科技公司（如FinTech支付），核心业务是支付，不是AI\n"
        "- 一般的Web3/区块链公司，如果核心业务是交易所/钱包/DeFi协议本身，不是AI\n"
        "- 任何公司里，岗位职责是客服/销售/运营，但没有明确围绕AI产品或AI技术的岗位\n\n"
        "以下情况才【算】通过：\n"
        "- 公司核心产品是AI模型、AI Agent、AI SaaS工具、AI基础设施\n"
        "- 岗位职责明确是围绕AI产品的GTM、AI产品的客户成功、AI技术的解决方案咨询等\n\n"
        "如果不通过第一步，无论候选人的商业技能多匹配，最终分数不得超过3分。\n\n"
        "【第二步 - 实际匹配度评估】\n"
        "如果第一步通过，再用 1-10 分给出候选人与岗位的真实匹配度：\n"
        "- 1-3分：明显不匹配，缺乏核心资质\n"
        "- 4-6分：部分相关，但有明显差距\n"
        "- 7-8分：较好匹配，核心能力对得上\n"
        "- 9-10分：高度匹配，几乎完全符合\n\n"
        "打分必须真实、离散，不要因为不确定就无脑打7分敷衍了事。"
        "如果候选人明显缺乏岗位的核心资质（如要求'7年以上XX经验'而候选人完全没有），必须打3分以下。\n\n"
        f"【候选人简历】：\n{resume_text}\n\n"
        f"【岗位标题】：{job_title}\n"
        f"【岗位描述】：\n{job_description[:3000]}\n\n"
        "请以严格的 JSON 格式输出，不要有任何其他文字：\n"
        '{"is_ai_tech_related": true或false, "score": 1到10的整数, '
        '"reason": "一句话说明打这个分的核心原因", "is_eligible_location": true或false}'
    )

    try:
        response = client.chat.completions.create(
            model=os.environ.get("SILICONFLOW_MODEL"),
            messages=[
                {"role": "system", "content": "You are an extremely strict, honest recruiting match evaluator. You give real, discrete scores, never lazy middle-ground numbers. Always respond in valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.3
        )
        raw = response.choices[0].message.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        result = json.loads(raw)
        score = result.get("score", 0)
        return {
            "score": score,
            "match_percentage": score * 10,
            "reason": result.get("reason", ""),
            "is_eligible_location": result.get("is_eligible_location", True),
            "is_ai_tech_related": result.get("is_ai_tech_related", False)
        }
    except Exception as e:
        logger.error(f"[LLM匹配评估] 失败: {e}")
        return {"score": 0, "match_percentage": 0, "reason": f"评估失败: {e}", "is_eligible_location": True, "is_ai_tech_related": False}
