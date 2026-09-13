import os
from openai import OpenAI
from job_agent import JobHunterPipeline

# 你的真实底稿简历常量
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