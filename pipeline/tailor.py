import os
import pypdf

class ResumeTailor:
    def __init__(self, master_resume_path: str):
        self.master_resume_path = master_resume_path
        self.master_content = self._load_master_resume()

    def _load_master_resume(self) -> str:
        if not os.path.exists(self.master_resume_path):
            print(f"[!] 警告: 未找到母简历路径: {self.master_resume_path}")
            return "Melody Qiu | AI Agent Architecture & Cross-Border GTM Specialist"
        
        try:
            reader = pypdf.PdfReader(self.master_resume_path)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            print(f"[*] 成功加载母简历，字符数: {len(text)}")
            return text
        except Exception as e:
            print(f"[!] 解析母简历 PDF 异常: {e}")
            return "Melody Qiu | AI Agent Architecture & Cross-Border GTM Specialist"

    def generate_tailored_summary(self, job_title: str, jd_text: str = "") -> str:
        base_profile = "Melody Qiu (melodymiller828@gmail.com | Telegram: @Melody0x_8)\n" \
                       "Core Background: Business English, Cross-Border GTM, AI Agent & Automation Workflows."
        
        tailored_block = f"\n[Target Position Tailoring]\n" \
                         f"Target Role: {job_title}\n" \
                         f"Customized Highlights: Optimized based on Master Resume and JD requirements, emphasizing Python, ReAct Agent architectures, and automated pipeline execution."
        
        return base_profile + tailored_block