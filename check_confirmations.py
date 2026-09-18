import os
import re
import logging
import requests
from dotenv import load_dotenv

from pipeline.database import JobHunterDatabase
from pipeline.auto_submitter import JobAutoSubmitter

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("check_confirmations")


def get_telegram_updates():
    """获取最新的 Telegram 消息（用户发给bot的回复）"""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json().get("result", [])


def send_telegram_message(text: str):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=15)


def process_confirmations():
    """扫描最新消息，找出'确认 N'指令，真正执行提交"""
    db = JobHunterDatabase()
    submitter = JobAutoSubmitter(headless=True)

    updates = get_telegram_updates()
    logger.info(f"获取到 {len(updates)} 条最新消息")

    for update in updates:
        message = update.get("message", {})
        text = message.get("text", "")
        match = re.match(r"确认\s*(\d+)", text)
        if not match:
            continue

        confirm_number = int(match.group(1))
        record = db.get_pending_confirmation(confirm_number)

        if not record:
            send_telegram_message(f"❌ 未找到编号 {confirm_number} 对应的待确认岗位")
            continue

        if record["status"] != "waiting":
            send_telegram_message(f"⚠️ 编号 {confirm_number} 已经处理过（当前状态: {record['status']}），不再重复提交")
            continue

        logger.info(f"正在真实提交: {record['title']}")
        applicant_info = {"full_name": os.environ.get("FULL_NAME"), "email": os.environ.get("EMAIL")}
        success = submitter.confirm_submit(
            job_url=record["job_url"],
            applicant_info=applicant_info,
            resume_path="data/base_resume.pdf",
            tailored_summary=record["tailored_summary"]
        )

        if success:
            db.update_confirmation_status(confirm_number, "submitted")
            db.save_applied_job(url=record["job_url"], company=record["company"], title=record["title"], status="APPLIED")
            send_telegram_message(f"✅ 已成功提交: *{record['title']}* @ {record['company']}")
        else:
            db.update_confirmation_status(confirm_number, "failed")
            send_telegram_message(f"❌ 提交失败: *{record['title']}*，请手动处理: {record['job_url']}")


if __name__ == "__main__":
    process_confirmations()
