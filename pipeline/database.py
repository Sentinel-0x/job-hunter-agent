import sqlite3
import os
import hashlib

class JobHunterDatabase:
    """
    Unified SQLite persistent storage for job-hunter-agent.
    Manages both the candidate job pool ('jobs') and application tracking ('applied_jobs').
    """
    def __init__(self, db_path: str = "data/job_hunter.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. 抓取到的岗位池表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                company TEXT,
                url TEXT UNIQUE,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. 已投递状态追踪表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applied_jobs (
                id TEXT PRIMARY KEY,
                company TEXT,
                title TEXT,
                url TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()

    def add_job(self, title: str, company: str, url: str, status: str = "New"):
        """向候选池添加抓取到的岗位"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO jobs (title, company, url, status) VALUES (?, ?, ?, ?)",
                    (title, company, url, status)
                )
        except sqlite3.IntegrityError:
            pass

    def save_applied_job(self, url: str, company: str, title: str, status: str = "APPLIED"):
        """记录已投递的岗位状态"""
        job_id = hashlib.sha256(f"{url}{company}{title}".encode('utf-8')).hexdigest()[:16]
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO applied_jobs (id, company, title, url, status) VALUES (?, ?, ?, ?, ?)",
                (job_id, company, title, url, status)
            )
            conn.commit()
