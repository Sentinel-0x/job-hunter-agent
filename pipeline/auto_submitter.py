import os
import logging
from playwright.sync_api import sync_playwright

logger = logging.getLogger("auto_submitter")


class JobAutoSubmitter:
    def __init__(self, headless: bool = True):
        self.headless = headless

    def prepare_application(self, job_url: str, applicant_info: dict, resume_path: str, tailored_summary: str = "") -> dict:
        """
        打开岗位页面，填写表单，挂载简历，截图保存供人工确认。
        不点击提交，返回准备状态供上层决定是否真正提交。
        """
        result = {
            "success": False,
            "screenshot_path": None,
            "submit_button_found": False,
            "captcha_detected": False,
            "error": None
        }
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()
                page.goto(job_url, timeout=30000)

                if page.locator("input[name*='name'], input[id*='name']").count() > 0:
                    page.fill("input[name*='name'], input[id*='name']", applicant_info.get("full_name", ""))

                if page.locator("input[type='email'], input[name*='email']").count() > 0:
                    page.fill("input[type='email'], input[name*='email']", applicant_info.get("email", ""))

                if tailored_summary:
                    for selector in ["textarea[name*='cover']", "textarea[name*='summary']", "textarea[name*='message']"]:
                        if page.locator(selector).count() > 0:
                            page.fill(selector, tailored_summary)
                            break

                if os.path.exists(resume_path):
                    file_input = page.locator("input[type='file']")
                    if file_input.count() > 0:
                        file_input.set_input_files(resume_path)
                        logger.info(f"成功挂载母简历: {resume_path}")

                page_text = page.content().lower()
                captcha_signals = ["cloudflare", "security verification", "performing security",
                                    "verifying you are not a bot", "captcha", "recaptcha"]
                if any(signal in page_text for signal in captcha_signals):
                    result["captcha_detected"] = True
                    result["error"] = "检测到人机验证，无法自动化，需要人工处理"
                    browser.close()
                    logger.warning(f"检测到人机验证，跳过此岗位: {job_url}")
                    return result

                submit_selectors = [
                    "button[type='submit']", "input[type='submit']",
                    "button:has-text('Apply')", "button:has-text('Submit')"
                ]
                submit_found = any(page.locator(sel).count() > 0 for sel in submit_selectors)
                result["submit_button_found"] = submit_found

                screenshot_dir = "data/screenshots"
                os.makedirs(screenshot_dir, exist_ok=True)
                safe_name = "".join(c if c.isalnum() else "_" for c in job_url)[-50:]
                screenshot_path = f"{screenshot_dir}/{safe_name}.png"
                page.screenshot(path=screenshot_path)
                result["screenshot_path"] = screenshot_path

                browser.close()
                result["success"] = True
                logger.info(f"表单准备完毕，等待人工确认后提交。截图: {screenshot_path}")
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"表单准备失败: {e}")
        return result

    def confirm_submit(self, job_url: str, applicant_info: dict, resume_path: str, tailored_summary: str = "") -> bool:
        """
        重新打开页面，填表，真正点击提交按钮。
        只应在用户通过 Telegram 确认后调用。
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()
                page.goto(job_url, timeout=30000)

                if page.locator("input[name*='name'], input[id*='name']").count() > 0:
                    page.fill("input[name*='name'], input[id*='name']", applicant_info.get("full_name", ""))

                if page.locator("input[type='email'], input[name*='email']").count() > 0:
                    page.fill("input[type='email'], input[name*='email']", applicant_info.get("email", ""))

                if tailored_summary:
                    for selector in ["textarea[name*='cover']", "textarea[name*='summary']", "textarea[name*='message']"]:
                        if page.locator(selector).count() > 0:
                            page.fill(selector, tailored_summary)
                            break

                if os.path.exists(resume_path):
                    file_input = page.locator("input[type='file']")
                    if file_input.count() > 0:
                        file_input.set_input_files(resume_path)

                submit_selectors = [
                    "button[type='submit']", "input[type='submit']",
                    "button:has-text('Apply')", "button:has-text('Submit')"
                ]
                clicked = False
                for sel in submit_selectors:
                    if page.locator(sel).count() > 0:
                        page.locator(sel).first.click()
                        clicked = True
                        break

                page.wait_for_timeout(2000)
                browser.close()

                if clicked:
                    logger.info(f"真实提交完成: {job_url}")
                else:
                    logger.warning(f"未找到提交按钮，未能真实提交: {job_url}")
                return clicked
        except Exception as e:
            logger.error(f"提交过程异常: {e}")
            return False
