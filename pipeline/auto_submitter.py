import os
from playwright.sync_api import sync_playwright

class JobAutoSubmitter:
    def __init__(self, headless: bool = True):
        self.headless = headless

    def submit_application(self, job_url: str, applicant_info: dict, resume_path: str) -> bool:
        print(f"[*] [安全投递引擎] 目标网址: {job_url} | 申请人: {applicant_info.get('full_name')} ({applicant_info.get('email')})")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()
                page.goto(job_url, timeout=30000)
                
                # 智能寻找并填写表单
                if page.locator("input[name*='name'], input[id*='name']").count() > 0:
                    page.fill("input[name*='name'], input[id*='name']", applicant_info.get("full_name", ""))
                
                if page.locator("input[type='email'], input[name*='email']").count() > 0:
                    page.fill("input[type='email'], input[name*='email']", applicant_info.get("email", ""))
                
                # 挂载真实母简历路径
                if os.path.exists(resume_path):
                    file_input = page.locator("input[type='file']")
                    if file_input.count() > 0:
                        file_input.set_input_files(resume_path)
                        print(f"[*] 成功绑定并挂载母简历: {resume_path}")
                
                print("[*] 表单数据与母简历已成功挂载，模拟外部投递执行完毕。")
                browser.close()
                return True
        except Exception as e:
            print(f"[!] 投递过程异常 (已安全拦截): {e}")
            return False
