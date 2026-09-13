BASE_RESUME = """
Melody Qiu
AI Research & Technology Intelligence Analyst | LLM Applications & Product Strategy
Email: melody7448@outlook.com

[PROFESSIONAL SUMMARY]
5+ years of cross-industry global tech intelligence & commercial strategy research experience, with 3 years of hands-on LLM and AI product evaluation practice. Specialize in designing production-grade ReAct Agent architectures with dynamic execution security (AST inspection, container sandboxing), building automated intelligence pipelines, and horizontal LLM evaluations.

[CORE SKILLS]
- AI Ecosystem & Commercial Strategy: Global Tech Trend Tracking, AI Product Competitive Analysis, Partner Ecosystem Growth, GTM Strategy.
- AI Solution Architecture & Client Success: Enterprise AI Implementation, Agentic Workflow Design, RAG Solution Mapping, Multi-Model Evaluation.
- Technical Stack: OpenAI API, Claude API, DeepSeek API, Dify, Coze, n8n, OpenClaw, Python, SQLite, Docker, Telegram.

[PROFESSIONAL EXPERIENCE]
1. LBank Exchange | Business Development Specialist (Jun 2025-Mar 2026)
   - Engineered an automated intelligence pipeline (OpenAI API, OpenClaw, Telegram) to track global Web3/AI dynamics, cutting manual screening workload by 60%.
   - Built and managed a pipeline of 40+ potential listing projects across DeFi, GameFi, and AI/Infrastructure sectors.
   - Conducted due diligence on project fundamentals, tokenomics, technical architecture, and on-chain traction.

2. Shenzhen Lixin Technology Trading Co., Ltd | Social Media Marketing Lead & Overseas Marketing Specialist (Jul 2021-Sep 2023)
   - Grew a North America Amazon store to $100K monthly sales, improved product ranking from #200 to Top 40.
   - Managed 200+ KOL relationships, generated 107+ marketing leads with a 4:1 ROI.

[INDEPENDENT AI RESEARCH PROJECT]
Frontier LLM Research & AI Workflow Evaluation (2025-Present)
- Production-Grade ReAct Architecture: Designed and deployed a resilient ReAct agent engine featuring automated self-healing retry logic.
- Static AST Security Barrier: Engineered a pre-runtime security gate using Python AST inspection to block unauthorized system imports.
- Dual-Sandbox Isolation Execution: Built fault-tolerant execution prioritizing network-disabled Docker and restricted subprocess sandbox.
- State Resilience & Persistence: Integrated SQLite session checkpointing for long-running agentic workflows.

[EDUCATION]
- Bachelor's in Business Administration, Shenzhen University (2021-2024)
- Associate's in Business English, Jiangxi Biotechnology Vocational College (2016-2019)
"""


import json
import logging
import sqlite3
import os
from typing import Dict, Any, Optional, Callable, List
from openai import OpenAI

logger = logging.getLogger("job_agent")

# ==================== SQLite 状态机与持久化管理 ====================
class JobHunterDatabase:
    def __init__(self, db_path="job_hunter_state.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT,
                company TEXT,
                description TEXT,
                score REAL,
                status TEXT DEFAULT 'Discovered',
                tailored_resume TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def save_job(self, job_id: str, title: str, company: str, description: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO jobs (id, title, company, description, status)
            VALUES (?, ?, ?, ?, 'Discovered')
        ''', (job_id, title, company, description))
        conn.commit()
        conn.close()

    def update_status(self, job_id: str, status: str, score: float = None, tailored_resume: str = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if score is not None and tailored_resume is not None:
            cursor.execute('UPDATE jobs SET status = ?, score = ?, tailored_resume = ? WHERE id = ?', (status, score, tailored_resume, job_id))
        elif score is not None:
            cursor.execute('UPDATE jobs SET status = ?, score = ? WHERE id = ?', (status, score, job_id))
        else:
            cursor.execute('UPDATE jobs SET status = ? WHERE id = ?', (status, job_id))
        conn.commit()
        conn.close()

# ==================== 智能求职核心流水线扩展 ====================
class JobHunterPipeline:
    def __init__(self, client: OpenAI, model_name: str = "gpt-4o-mini"):
        self.client = client
        self.model_name = model_name
        self.db = JobHunterDatabase()

    def evaluate_job_redteam(self, jd_text: str) -> dict:
        """红蓝对抗评分器：大模型扮演挑剔的招聘经理"""
        prompt = (
            f"你是一个严厉的求职红队评审。请根据以下岗位描述 (JD) 和候选人背景（AI Agent 自动化、GTM、Web3 投研与商业化），进行红蓝对抗打分。\n"
            f"岗位描述：\n{jd_text}\n\n"
            "请严格以 JSON 格式输出评估结果，包含以下字段：\n"
            "- score: 0到10的浮点数评分\n"
            "- pros: 匹配亮点（数组）\n"
            "- cons_or_risks: 潜在风险或不匹配点（数组）\n"
            "- verdict: 'PASS'（>=7分）或 'REJECT'（<7分）"
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "system", "content": "You are a strict technical and business recruiter."},
                          {"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"[RedTeam Error] 评分失败: {str(e)}")
            return {"score": 0.0, "verdict": "REJECT", "cons_or_risks": [str(e)]}

    def tailor_resume(self, jd_text: str, base_resume: str) -> str:
        """防幻觉简历动态优化器：基于真实底稿简历，绝不虚构，针对岗位JD精准重组"""
        prompt = (
            f"你是一个顶级的求职简历策略专家。请根据以下【岗位 JD】和候选人的【真实底稿简历】，为候选人量身定制一份高度匹配的简历内容。\n\n"
            f"【严厉铁律】：\n"
            f"1. 绝不允许虚构、伪造任何未在底稿中出现过的工作经历、公司名称、项目或技术栈。\n"
            f"2. 只能使用【真实底稿简历】中提供的事实，通过重新组织语言、加权核心亮点、对齐 JD 关键词来提升匹配度。\n"
            f"3. 保持专业、精炼、结果导向的商业与技术表达。\n\n"
            f"【岗位 JD】：\n{jd_text}\n\n"
            f"【真实底稿简历】：\n{base_resume}\n\n"
            "请输出针对该岗位的定制化简历优化版本（包含核心摘要与匹配亮点）："
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a professional, anti-hallucination resume strategist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"[Tailor Error] 简历定制失败: {str(e)}")
            return "Error generating tailored resume from base."

    def process_job(self, job_id: str, title: str, company: str, description: str) -> dict:
        """执行完整自动化闭环"""
        self.db.save_job(job_id, title, company, description)
        logger.info(f"[Pipeline] 新岗位入库: {company} - {title}")

        eval_result = self.evaluate_job_redteam(description)
        score = eval_result.get("score", 0.0)
        verdict = eval_result.get("verdict", "REJECT")
        
        logger.info(f"[RedTeam] 评分: {score} | 结论: {verdict}")

        if verdict == "PASS" or score >= 7.0:
            tailored_resume = self.tailor_resume(description, BASE_RESUME)
            self.db.update_status(job_id, status="Tailored", score=score, tailored_resume=tailored_resume)
            return {
                "status": "PASS",
                "score": score,
                "tailored_resume": tailored_resume,
                "message": "红队通过，简历定制完成！"
            }
        else:
            self.db.update_status(job_id, status="Rejected", score=score)
            return {
                "status": "REJECT",
                "score": score,
                "message": "未达标或存在风险，已被红队拦截。"
            }