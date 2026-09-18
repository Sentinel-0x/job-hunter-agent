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

        # 3. 待确认提交表：存放已准备好表单、等待用户在Telegram确认后才真正提交的岗位
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_confirmation (
                confirm_number INTEGER PRIMARY KEY AUTOINCREMENT,
                job_url TEXT,
                company TEXT,
                title TEXT,
                tailored_summary TEXT,
                status TEXT DEFAULT "waiting",
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

    def add_pending_confirmation(self, job_url: str, company: str, title: str, tailored_summary: str) -> int:
        """添加一条待确认提交的岗位，返回该条记录的编号（用于Telegram里对应"确认1"这种指令）"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO pending_confirmation (job_url, company, title, tailored_summary) VALUES (?, ?, ?, ?)",
                (job_url, company, title, tailored_summary)
            )
            conn.commit()
            return cursor.lastrowid

    def get_pending_confirmation(self, confirm_number: int):
        """根据编号取出一条待确认的岗位信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT job_url, company, title, tailored_summary, status FROM pending_confirmation WHERE confirm_number = ?",
                (confirm_number,)
            )
            row = cursor.fetchone()
            if row:
                return {"job_url": row[0], "company": row[1], "title": row[2], "tailored_summary": row[3], "status": row[4]}
            return None

    def update_confirmation_status(self, confirm_number: int, status: str):
        """更新待确认岗位的状态（如 confirmed / submitted / rejected）"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE pending_confirmation SET status = ? WHERE confirm_number = ?",
                (status, confirm_number)
            )
            conn.commit()

    def is_job_already_processed(self, url: str) -> bool:
        """检查这条岗位链接是否已经出现在岗位池里（避免重复推送/重复评估）"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT 1 FROM jobs WHERE url = ?", (url,))
            return cursor.fetchone() is not None

    def list_waiting_confirmations(self):
        """列出所有还在等待确认的岗位"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT confirm_number, company, title FROM pending_confirmation WHERE status = 'waiting'"
            )
            return cursor.fetchall()
