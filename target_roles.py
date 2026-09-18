"""
第一层过滤：岗位标题/方向粗筛。
逻辑：标题命中目标职能词即可通过（不要求必须带AI字样，
因为公司是否AI相关往往体现在公司背景/岗位描述里，不是标题字面）。
真正的AI相关性和匹配度判断交给下一层的LLM语义评估。
"""

TARGET_FUNCTION_WORDS = [
    "gtm", "go-to-market", "partnership", "partnerships", "alliance",
    "customer success", "csm", "solutions consultant", "solutions architect",
    "implementation", "commercialization", "ecosystem", "strategy",
    "strategic", "research ops", "research operations", "advisory",
    "research", "program manager", "head of partnerships", "head of sales",
]

EXCLUDE_WORDS = [
    "account executive", "sales development representative",
    "business development representative", "content marketing",
    "seo", "inside sales", "sdr", "bdr",
    "performance marketing", "demand generation", "affiliate",
]


def is_target_role(job_title: str) -> bool:
    title_lower = job_title.lower()

    if any(ex in title_lower for ex in EXCLUDE_WORDS):
        return False

    return any(func in title_lower for func in TARGET_FUNCTION_WORDS)
