import os
import requests
import feedparser
import logging
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential

load_dotenv()
logger = logging.getLogger("fetcher")

WWR_CATEGORIES = [
    "remote-sales-and-marketing-jobs",
    "remote-product-jobs",
    "remote-management-and-finance-jobs",
]

RETRY_CONFIG = dict(
    wait=wait_random_exponential(min=1, max=10),
    stop=stop_after_attempt(3)
)


@retry(**RETRY_CONFIG)
def _get_with_retry(url, **kwargs):
    """带自动重试的网络请求，应对偶发DNS/网络波动"""
    response = requests.get(url, timeout=10, **kwargs)
    response.raise_for_status()
    return response


def fetch_from_weworkremotely():
    """从 We Work Remotely 多个相关分类抓取真实岗位（带重试）"""
    jobs = []
    for category in WWR_CATEGORIES:
        url = f"https://weworkremotely.com/categories/{category}.rss"
        try:
            response = _get_with_retry(url)
            feed = feedparser.parse(response.content)
            for entry in feed.entries:
                jobs.append({
                    "title": entry.title,
                    "company": entry.title.split(":")[0].strip() if ":" in entry.title else "Unknown",
                    "url": entry.link,
                    "source": "We Work Remotely",
                    "posted_at": entry.get("published", ""),
                    "description": entry.get("summary", ""),
                    "country": entry.get("country", ""),
                    "region": entry.get("region", ""),
                    "expires_at": entry.get("expires_at", "")
                })
            logger.info(f"[We Work Remotely - {category}] 成功抓取 {len(feed.entries)} 条")
        except Exception as e:
            logger.error(f"[We Work Remotely - {category}] 抓取失败（已重试3次）: {e}")
    return jobs


def fetch_from_himalayas(max_pages=5, per_page=20):
    """从 Himalayas.app 官方公开 JSON API 分页抓取真实岗位（带重试）"""
    jobs = []
    url = "https://himalayas.app/jobs/api"
    cursor = None

    for page in range(max_pages):
        try:
            params = {"limit": per_page}
            if cursor:
                params["cursor"] = cursor
            response = _get_with_retry(url, params=params)
            data = response.json()

            page_jobs = data.get("jobs", [])
            if not page_jobs:
                break

            for job in page_jobs:
                jobs.append({
                    "title": job.get("title", ""),
                    "company": job.get("companyName", "Unknown"),
                    "url": job.get("applicationLink", ""),
                    "source": "Himalayas",
                    "employment_type": job.get("employmentType", ""),
                    "min_salary": job.get("minSalary"),
                    "max_salary": job.get("maxSalary"),
                    "currency": job.get("currency", ""),
                    "location_restrictions": job.get("locationRestrictions", []),
                    "description": job.get("description", ""),
                    "expires_at": job.get("expiryDate", "")
                })

            cursor = data.get("nextCursor")
            if not cursor:
                break
        except Exception as e:
            logger.error(f"[Himalayas] 第{page+1}页抓取失败（已重试3次）: {e}")
            break

    logger.info(f"[Himalayas] 成功抓取 {len(jobs)} 条真实岗位")
    return jobs


def fetch_from_web3career(tags=None, remote=True, limit=100):
    """从 Web3.career 官方 API 抓取真实岗位（带重试）"""
    jobs = []
    token = os.environ.get("WEB3CAREER_API_TOKEN")
    if not token:
        logger.error("[Web3.career] 未配置 WEB3CAREER_API_TOKEN，跳过此数据源")
        return jobs

    url = "https://web3.career/api/v1"
    params = {"token": token, "limit": limit}
    if remote:
        params["remote"] = "true"
    if tags:
        params["tag"] = tags

    try:
        response = _get_with_retry(url, params=params)
        data = response.json()

        job_list = []
        if isinstance(data, list) and len(data) > 2 and isinstance(data[2], list):
            job_list = data[2]

        for job in job_list:
            if not isinstance(job, dict):
                continue
            jobs.append({
                "title": job.get("title", ""),
                "company": job.get("company", "Unknown"),
                "url": job.get("apply_url", ""),
                "source": "Web3.career",
                "posted_at": job.get("date", ""),
                "tags": job.get("tags", []),
                "min_salary": job.get("salary_min_value"),
                "max_salary": job.get("salary_max_value"),
                "is_remote": job.get("is_remote", False),
                "description": job.get("description", "")
            })
        logger.info(f"[Web3.career] 成功抓取 {len(jobs)} 条真实岗位")
    except Exception as e:
        logger.error(f"[Web3.career] 抓取失败（已重试3次）: {e}")
    return jobs


def fetch_from_remoteok(limit=100):
    """从 Remote OK 官方公开 JSON API 抓取真实岗位（带重试）"""
    jobs = []
    url = "https://remoteok.com/api"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = _get_with_retry(url, headers=headers)
        data = response.json()

        job_list = data[1:] if isinstance(data, list) and len(data) > 1 else []

        for job in job_list[:limit]:
            if not isinstance(job, dict):
                continue
            jobs.append({
                "title": job.get("position", ""),
                "company": job.get("company", "Unknown"),
                "url": f"https://remoteok.com/remote-jobs/{job.get('id', '')}",
                "source": "Remote OK",
                "posted_at": job.get("date", ""),
                "tags": job.get("tags", []),
                "description": job.get("description", "")
            })
        logger.info(f"[Remote OK] 成功抓取 {len(jobs)} 条真实岗位")
    except Exception as e:
        logger.error(f"[Remote OK] 抓取失败（已重试3次）: {e}")
    return jobs


def fetch_jobs_from_sources():
    """
    多源真实岗位聚合抓取，每个数据源均带自动重试（3次，指数退避）。
    当前接入：We Work Remotely、Himalayas.app、Web3.career、Remote OK
    """
    all_jobs = []
    all_jobs.extend(fetch_from_weworkremotely())
    all_jobs.extend(fetch_from_himalayas())
    all_jobs.extend(fetch_from_web3career())
    all_jobs.extend(fetch_from_remoteok())
    logger.info(f"[聚合完成] 共抓取到 {len(all_jobs)} 条真实岗位")
    return all_jobs
