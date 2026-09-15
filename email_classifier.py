class EmailClassifier:
    """判断求职邮件回复类型：拒信 / 积极信号 / 中性，用于 job-hunter-agent 自动分类收到的招聘方回复邮件"""

    def smart_filter_email(self, email_subject: str, email_body: str) -> bool:
        rejection_keywords = ["unfortunately", "regret", "not moving forward", "closed", "other candidates"]
        body_lower = f"{email_subject} {email_body}".lower()

        for kw in rejection_keywords:
            if kw in body_lower:
                return False

        positive_keywords = ["interview", "schedule", "call", "discussion", "chat", "next steps"]
        for kw in positive_keywords:
            if kw in body_lower:
                return True

        return False

