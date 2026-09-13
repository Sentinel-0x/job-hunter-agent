import os
from openai import OpenAI
from job_agent import JobHunterPipeline

from dotenv import load_dotenv
load_dotenv()

def _load_base_resume():
    resume_path = os.path.join(os.path.dirname(__file__), "data", "base_resume.md")
    if os.path.exists(resume_path):
        with open(resume_path, "r", encoding="utf-8") as f:
            return f.read()
    return f"{os.environ.get('FULL_NAME', 'Candidate')} | Resume data not found, please add data/base_resume.md"

BASE_RESUME = _load_base_resume()


if __name__ == "__main__":
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url=os.environ.get("OPENAI_BASE_URL")
    )
    pipeline = JobHunterPipeline(client, model_name="gpt-4o-mini")
    
    jd_sample = "Looking for a global AI Product & GTM Specialist with hands-on Python/Agent development experience, cross-border business development background, and strong technical evaluation skills."
    
    print("正在执行红队评估与基于底稿的简历定制...")
    result = pipeline.process_job("test_base_01", "AI GTM Lead", "Global AI Corp", jd_sample)
    print("=== 最终输出结果 ===")
    print(result)