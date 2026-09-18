import os
import logging
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential
import requests

from fetcher import fetch_jobs_from_sources
from target_roles import is_target_role
from pipeline.tailor import ResumeTailor
from llm_matcher import evaluate_match
from tailor_llm import generate_tailored_summary
from pipeline.auto_submitter import JobAutoSubmitter
from pipeline.database import JobHunterDatabase

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("daily_pipeline")

SCORE_THRESHOLD = 7  # 满分10分，达到7分才算通过


@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(3))
def send_telegram_message(text: str):
    """发送 Telegram 消息，带自动重试"""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        logger.error("Telegram 配置缺失，无法发送消息")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    max_length = 4000
    chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
    for chunk in chunks:
        payload = {"chat_id": chat_id, "text": chunk, "parse_mode": "Markdown"}
        res = requests.post(url, json=payload, timeout=15)
        res.raise_for_status()


def run_daily_pipeline():
    logger.info("=== 每日岗位流水线启动 ===")

    db = JobHunterDatabase()
    tailor = ResumeTailor("data/base_resume.pdf")
    submitter = JobAutoSubmitter(headless=True)

    jobs = fetch_jobs_from_sources()
    logger.info(f"抓取到 {len(jobs)} 条真实岗位")

    candidates = [j for j in jobs if is_target_role(j["title"])]
    logger.info(f"粗筛通过 {len(candidates)} 条")

    candidates = [j for j in candidates if not db.is_job_already_processed(j["url"])]
    logger.info(f"排除已处理过的岗位后，剩余 {len(candidates)} 条新岗位")

    candidates = [j for j in candidates if len(j.get("description", "")) >= 200]
    logger.info(f"排除描述信息不足的岗位后，剩余 {len(candidates)} 条可评估岗位")

    qualified = []
    for job in candidates:
        # 数据库去重：已经处理过的岗位不再重复评估
        result = evaluate_match(tailor.master_content, job["title"], job.get("description", ""))
        if result["score"] >= SCORE_THRESHOLD and result["is_eligible_location"] and result["is_ai_tech_related"]:
            job["match_result"] = result
            qualified.append(job)

    logger.info(f"精筛达标 {len(qualified)} 条（评分>={SCORE_THRESHOLD}/10）")

    if not qualified:
        send_telegram_message(f"📋 *今日岗位流水线运行完毕*\n共抓取 {len(jobs)} 条，粗筛 {len(candidates)} 条，今日没有达标岗位（>={SCORE_THRESHOLD}/10分）。")
        return

    report_lines = [f"📋 *今日达标岗位汇总（{len(qualified)}条）*\n"]

    for idx, job in enumerate(qualified, 1):
        # 检查数据库中是否已投递过
        applicant_info = {"full_name": os.environ.get("FULL_NAME"), "email": os.environ.get("EMAIL")}
        summary = generate_tailored_summary(tailor.master_content, job["title"], job.get("description", ""))
        prep_result = submitter.prepare_application(
            job_url=job["url"],
            applicant_info=applicant_info,
            resume_path="data/base_resume.pdf",
            tailored_summary=summary
        )

        db.add_job(title=job["title"], company=job["company"], url=job["url"], status="Qualified")

        if prep_result.get("captcha_detected"):
            status_line = "⚠️ 需要人工处理（遇到人机验证）"
        elif prep_result.get("success") and prep_result.get("submit_button_found"):
            confirm_number = db.add_pending_confirmation(
                job_url=job["url"], company=job["company"],
                title=job["title"], tailored_summary=summary
            )
            status_line = f"✅ 可自动提交，回复 `确认 {confirm_number}` 来真正提交"
        else:
            status_line = "⚠️ 需要人工检查（未找到标准提交按钮）"

        report_lines.append(
            f"{idx}. *{job['title']}*\n"
            f"公司: {job['company']} | 来源: {job['source']}\n"
            f"评分: {job['match_result']['score']}/10 | {job['match_result']['reason']}\n"
            f"链接: {job['url']}\n"
            f"状态: {status_line}\n"
        )

    full_report = "\n".join(report_lines)
    send_telegram_message(full_report)
    logger.info("每日汇总已推送至 Telegram")


if __name__ == "__main__":
    run_daily_pipeline()
