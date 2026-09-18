import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("tailor_llm")

client = OpenAI(
    api_key=os.environ.get("SILICONFLOW_API_KEY"),
    base_url=os.environ.get("SILICONFLOW_BASE_URL")
)


def generate_tailored_summary(resume_text: str, job_title: str, job_description: str) -> str:
    """
    根据真实母简历和目标岗位描述，用 LLM 生成一段针对性的简历摘要。
    严格约束：只能使用母简历中已有的真实经历，不允许编造。
    """
    prompt = (
        "你是一位专业的求职简历顾问。请根据候选人的【真实母简历】，"
        "为以下【目标岗位】撰写一段针对性的简历摘要（3-4句话，英文）。\n\n"
        "【严格铁律】：\n"
        "1. 绝不允许虚构任何未在母简历中出现过的经历、公司、项目或技术。\n"
        "2. 只能重新组织母简历中已有的真实内容，突出与该岗位最相关的经历。\n"
        "3. 语言专业、精炼、结果导向。\n\n"
        f"【真实母简历】：\n{resume_text}\n\n"
        f"【目标岗位】：{job_title}\n"
        f"【岗位描述】：\n{job_description[:2000]}\n\n"
        "请直接输出这段定制化摘要，不要有任何其他说明文字："
    )

    try:
        response = client.chat.completions.create(
            model=os.environ.get("SILICONFLOW_MODEL"),
            messages=[
                {"role": "system", "content": "You are a professional, anti-hallucination resume consultant. Never invent facts not present in the source resume."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"[简历定制] 生成失败: {e}")
        return f"生成失败: {e}"
