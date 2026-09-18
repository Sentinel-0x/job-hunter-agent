"""
简历关键词权重配置。
高权重：核心目标方向（GTM、AI、商务开发）
中权重：技术能力背书
低权重：早期经历，非当前主打方向
"""

HIGH_WEIGHT = {
    "gtm": 3, "go-to-market": 3, "business development": 3,
    "deal sourcing": 3, "partnership": 3, "partner ecosystem": 3,
    "client success": 3, "founder negotiation": 3, "due diligence": 3,
    "ecosystem": 3, "competitive intelligence": 3, "ai agent": 3,
    "solutions consulting": 3, "technical onboarding": 3,
}

MID_WEIGHT = {
    "python": 2, "docker": 2, "llm": 2, "ai product": 2,
    "reAct": 2, "agentic workflow": 2, "rag": 2,
    "multi-model evaluation": 2, "gpt": 2, "claude": 2, "deepseek": 2,
    "openai api": 2, "sandbox": 2, "benchmarking": 2,
    "cross-border": 2, "listing": 2,
}

LOW_WEIGHT = {
    "marketing": 1, "kol": 1, "influencer": 1, "tiktok": 1,
    "facebook": 1, "google analytics": 1, "amazon": 1,
    "e-commerce": 1, "freight": 1,
}

ALL_KEYWORDS = {**HIGH_WEIGHT, **MID_WEIGHT, **LOW_WEIGHT}
MAX_POSSIBLE_SCORE = sum(ALL_KEYWORDS.values())


def calculate_match_score(job_description: str) -> dict:
    """
    计算岗位描述与母简历关键词的加权匹配度。
    返回 0-100 的百分比分数，以及命中的关键词列表。
    """
    text_lower = job_description.lower()
    matched = []
    score = 0

    for keyword, weight in ALL_KEYWORDS.items():
        if keyword in text_lower:
            matched.append(keyword)
            score += weight

    percentage = round((score / MAX_POSSIBLE_SCORE) * 100, 1)

    return {
        "match_percentage": percentage,
        "matched_keywords": matched,
        "raw_score": score,
        "max_score": MAX_POSSIBLE_SCORE
    }

