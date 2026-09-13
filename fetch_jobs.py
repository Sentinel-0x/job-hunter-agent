import json
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def get_robust_session(retries=3, backoff_factor=1):
    """🛠️ 生产级 Session 构造器：具备指数退避重试能力"""
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,                      # 最多重试 3 次
        backoff_factor=backoff_factor,      # 指数等待间隔：1s, 2s, 4s...
        status_forcelist=[429, 500, 502, 503, 504], # 遇到此类 HTTP 状态码时重试
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def fetch_data():
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    session = get_robust_session()

    # 1. Jobicy
    try:
        logging.info("📡 正在抓取 Jobicy 岗位（已启用自动重试）...")
        res = session.get("https://jobicy.com/api/v2/remote-jobs?count=30", headers=headers, timeout=10)
        if res.status_code == 200:
            for item in res.json().get("jobs", []):
                jobs.append({
                    "title": item.get("jobTitle"),
                    "company": item.get("companyName"),
                    "location": item.get("jobGeo", "Worldwide"),
                    "type": item.get("jobType", "N/A"),
                    "url": item.get("url"),
                    "desc": item.get("jobExcerpt", "")[:300],
                    "source": "Jobicy"
                })
    except Exception as e:
        logging.error(f"❌ Jobicy 经过 3 次重试后依然失败: {e}")

    # 2. Remotive
    try:
        logging.info("📡 正在抓取 Remotive 岗位（已启用自动重试）...")
        res = session.get("https://remotive.com/api/remote-jobs?limit=30", headers=headers, timeout=10)
        if res.status_code == 200:
            for item in res.json().get("jobs", []):
                jobs.append({
                    "title": item.get("title"),
                    "company": item.get("company_name"),
                    "location": item.get("candidate_required_location", "Worldwide"),
                    "type": item.get("job_type", "N/A"),
                    "url": item.get("url"),
                    "desc": item.get("description", "")[:300],
                    "source": "Remotive"
                })
    except Exception as e:
        logging.error(f"❌ Remotive 经过 3 次重试后依然失败: {e}")

    # 3. Himalayas
    try:
        logging.info("📡 正在抓取 Himalayas 岗位（已启用自动重试）...")
        res = session.get("https://himalayas.app/jobs/api?limit=30", headers=headers, timeout=10)
        if res.status_code == 200:
            for item in res.json().get("jobs", []):
                jobs.append({
                    "title": item.get("title"),
                    "company": item.get("companyName"),
                    "location": "Worldwide" if item.get("worldwide") else "Restricted",
                    "type": item.get("employmentType", "N/A"),
                    "url": item.get("applicationLink"),
                    "desc": item.get("excerpt", "")[:300],
                    "source": "Himalayas"
                })
    except Exception as e:
        logging.error(f"❌ Himalayas 经过 3 次重试后依然失败: {e}")

    # 4. RemoteOK
    try:
        logging.info("📡 正在抓取 Remote OK 岗位（已启用自动重试）...")
        res = session.get("https://remoteok.com/api", headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            for item in data[1:30]:
                jobs.append({
                    "title": item.get("position"),
                    "company": item.get("company"),
                    "location": item.get("location", "Worldwide"),
                    "type": "Remote",
                    "url": item.get("url"),
                    "desc": item.get("description", "")[:300],
                    "source": "Remote OK"
                })
    except Exception as e:
        logging.error(f"❌ Remote OK 经过 3 次重试后依然失败: {e}")

    with open("jobs_data.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    
    logging.info(f"✅ 抓取完成！共收集 {len(jobs)} 条原始岗位数据。")

if __name__ == "__main__":
    fetch_data()
