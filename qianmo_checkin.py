# qianmo_checkin.py
import requests
import os
import re
from datetime import datetime
import time
import smtplib
import ssl
from email.mime.text import MIMEText
from email.header import Header


def send_email(subject, content):
    """
    发送邮件通知
    需要配置以下环境变量：
    SMTP_HOST
    SMTP_PORT
    SMTP_USER
    SMTP_PASS
    MAIL_TO
    """

    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = os.environ.get("SMTP_PORT", "465")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    mail_to = os.environ.get("MAIL_TO")

    if not all([smtp_host, smtp_port, smtp_user, smtp_pass, mail_to]):
        print("⚠️ 邮件配置不完整，跳过邮件发送")
        return False

    try:
        smtp_port = int(smtp_port)
    except ValueError:
        print("❌ SMTP_PORT 必须是数字")
        return False

    msg = MIMEText(content, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = smtp_user
    msg["To"] = mail_to

    recipients = [item.strip() for item in mail_to.split(",") if item.strip()]

    try:
        if smtp_port == 465:
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=30)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
            server.starttls()

        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, recipients, msg.as_string())
        server.quit()

        print("📧 邮件发送成功")
        return True

    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False


class QianMoCheckin:
    def __init__(self, cookie):
        self.base_url = "https://www.1000qm.vip"
        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": f"{self.base_url}/forum.php"
        })

        self._set_cookies(cookie)

    def _set_cookies(self, cookie_string):
        """设置 Cookie 到 session"""
        for item in cookie_string.split(";"):
            item = item.strip()
            if "=" in item:
                key, value = item.split("=", 1)
                self.session.cookies.set(key, value, domain=".1000qm.vip")

    def get_formhash(self):
        """获取 formhash"""
        try:
            response = self.session.get(f"{self.base_url}/forum.php", timeout=30)

            match = re.search(r"formhash=([a-z0-9]+)", response.text)
            if match:
                return match.group(1)

            match = re.search(r'name="formhash"\s+value="([a-z0-9]+)"', response.text)
            if match:
                return match.group(1)

            return None

        except Exception as e:
            print(f"获取 formhash 失败: {e}")
            return None

    def checkin(self):
        """执行签到"""
        formhash = self.get_formhash()

        if not formhash:
            msg = "无法获取 formhash，签到失败"
            print(f"❌ {msg}")
            return False, msg

        try:
            checkin_url = (
                f"{self.base_url}/plugin.php?"
                f"id=dsu_paulsign:sign&operation=qiandao&infloat=1&inajax=1"
            )

            data = {
                "formhash": formhash,
                "qdxq": "kx",
                "qdmode": "1",
                "todaysay": "开心是一种选择，快乐融入日常，感受每一个美好的瞬间！"
            }

            response = self.session.post(checkin_url, data=data, timeout=30)
            response_text = response.text

            if "签到成功" in response_text:
                msg = "签到成功"
                print(f"✅ {msg}")
                return True, msg

            elif "已经签到" in response_text or "您今天已经签到过了" in response_text:
                msg = "今天已经签到过了"
                print(f"ℹ️ {msg}")
                return True, msg

            else:
                error_match = re.search(r"<root><!\[CDATA\[(.*?)\]\]></root>", response_text)
                if error_match:
                    error_msg = re.sub(r"<.*?>", "", error_match.group(1)).strip()
                    msg = f"签到失败: {error_msg}"
                else:
                    msg = "签到失败，未识别到具体原因"

                print(f"❌ {msg}")
                return False, msg

        except Exception as e:
            msg = f"签到异常: {e}"
            print(f"❌ {msg}")
            return False, msg

    def check_task_status(self):
        """检查任务状态 - 返回 new, doing, done, no_new, unknown"""
        try:
            response = self.session.get(f"{self.base_url}/home.php?mod=task&item=new", timeout=30)
            html = response.text

            if re.search(
                r'<a href="home\.php\?mod=task&amp;do=apply&amp;id=1"[^>]*>立即申请</a>',
                html
            ):
                return "new"

            response = self.session.get(f"{self.base_url}/home.php?mod=task&item=doing", timeout=30)
            html = response.text

            if re.search(
                r'<a href="home\.php\?mod=task&amp;do=view&amp;id=1">每日威望红包</a>',
                html
            ):
                return "doing"

            response = self.session.get(f"{self.base_url}/home.php?mod=task&item=done", timeout=30)
            html = response.text

            pattern = (
                r'<a href="home\.php\?mod=task&amp;do=view&amp;id=1">'
                r'每日威望红包</a>.*?完成于 (\d{4}-\d{1,2}-\d{1,2} \d{2}:\d{2})'
            )

            match = re.search(pattern, html, re.DOTALL)

            if match:
                complete_time_str = match.group(1)
                complete_time = datetime.strptime(complete_time_str, "%Y-%m-%d %H:%M")
                today = datetime.now().date()

                if complete_time.date() == today:
                    return "done"
                else:
                    return "no_new"

            return "no_new"

        except Exception as e:
            print(f"  检查任务状态异常: {e}")
            return "unknown"

    def process_tasks(self):
        """处理每日任务"""
        try:
            status = self.check_task_status()

            if status == "done":
                msg = "每日威望红包任务今天已完成"
                print(f"  ✅ {msg}")
                return True, msg

            if status == "no_new":
                msg = "暂无新任务，可能今天已完成或任务未刷新"
                print(f"  ℹ️ {msg}")
                return True, msg

            if status == "unknown":
                msg = "无法确定任务状态"
                print(f"  ⚠️ {msg}")
                return False, msg

            task_id = "1"
            task_name = "每日威望红包"

            if status == "new":
                print(f"  📋 发现新任务: {task_name}")

                apply_url = f"{self.base_url}/home.php?mod=task&do=apply&id={task_id}"
                apply_response = self.session.get(apply_url, timeout=30)
                apply_text = apply_response.text

                if "成功接受任务" in apply_text or "成功" in apply_text:
                    print("  ✅ 申请任务成功")
                elif "您已经申请过" in apply_text or "进行中" in apply_text:
                    print("  ℹ️ 任务已申请")
                elif "已完成" in apply_text:
                    msg = "任务已完成"
                    print(f"  ✅ {msg}")
                    return True, msg

                time.sleep(1)

            elif status == "doing":
                print(f"  📋 任务进行中: {task_name}")

            draw_url = f"{self.base_url}/home.php?mod=task&do=draw&id={task_id}"
            draw_response = self.session.get(draw_url, timeout=30)
            draw_text = draw_response.text

            success_keywords = [
                "恭喜",
                "成功完成任务",
                "任务已完成",
                "领取成功",
                "奖励已发放"
            ]

            error_keywords = [
                "您还没有申请",
                "任务不存在",
                "操作失败"
            ]

            is_success = any(keyword in draw_text for keyword in success_keywords)
            has_error = any(keyword in draw_text for keyword in error_keywords)

            if is_success and not has_error:
                reward_match = re.search(r"威望.*?(\d+)", draw_text)
                if reward_match:
                    reward = reward_match.group(1)
                    msg = f"完成任务成功，获得 {reward} 威望"
                else:
                    msg = "完成任务成功"

                print(f"  🎁 {msg}")
                return True, msg

            time.sleep(1)
            new_status = self.check_task_status()

            if new_status == "done":
                msg = "任务完成成功"
                print(f"  ✅ {msg}")
                return True, msg

            elif new_status == "no_new":
                msg = "任务完成成功"
                print(f"  ✅ {msg}")
                return True, msg

            else:
                msg = "任务完成失败"
                print(f"  ⚠️ {msg}")
                return False, msg

        except Exception as e:
            msg = f"处理任务异常: {e}"
            print(f"❌ {msg}")
            return False, msg

    def get_prestige(self):
        """获取威望、铜币、积分信息"""
        try:
            response = self.session.get(
                f"{self.base_url}/home.php?mod=spacecp&ac=credit&showcredit=1",
                timeout=30
            )
            html = response.text

            prestige_match = re.search(r"<em>\s*威望:\s*</em>(\d+)", html)
            copper_match = re.search(r"<em>\s*铜币:\s*</em>(\d+)", html)
            credits_match = re.search(r"<em>积分:\s*</em>(\d+)", html)

            result = []

            if prestige_match:
                result.append(f"威望: {prestige_match.group(1)}")

            if copper_match:
                result.append(f"铜币: {copper_match.group(1)}")

            if credits_match:
                result.append(f"积分: {credits_match.group(1)}")

            if result:
                msg = " | ".join(result)
                print(f"📊 {msg}")
                return True, msg

            else:
                msg = "无法获取积分信息"
                print(f"⚠️ {msg}")
                return False, msg

        except Exception as e:
            msg = f"获取积分异常: {e}"
            print(f"❌ {msg}")
            return False, msg

    def verify_login(self):
        """验证登录状态"""
        try:
            response = self.session.get(f"{self.base_url}/forum.php", timeout=30)

            if "member.php?mod=logging&action=login" in response.text:
                msg = "Cookie 已失效，请重新获取"
                print(f"❌ {msg}")
                return False, msg

            username_match = re.search(
                r'<a[^>]*title="访问我的空间"[^>]*>([^<]+)</a>',
                response.text
            )

            if username_match:
                username = username_match.group(1).strip()
                msg = f"登录验证成功，用户: {username}"
                print(f"✅ {msg}")
                return True, msg

            msg = "登录验证成功"
            print(f"✅ {msg}")
            return True, msg

        except Exception as e:
            msg = f"验证登录异常: {e}"
            print(f"❌ {msg}")
            return False, msg


def main():
    start_time = datetime.now()

    print(f"{'=' * 50}")
    print("阡陌居自动签到脚本")
    print(f"运行时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 50}\n")

    cookie = os.environ.get("QIANMO_COOKIE")

    login_ok = False
    checkin_success = False
    task_success = False
    prestige_ok = False

    login_msg = "未执行"
    checkin_msg = "未执行"
    task_msg = "未执行"
    prestige_msg = "未执行"
    final_status = "未知"

    try:
        if not cookie:
            final_status = "失败"
            login_msg = "未设置 QIANMO_COOKIE 环境变量"
            print(f"❌ 错误: {login_msg}")

        else:
            checker = QianMoCheckin(cookie)

            print("🔄 验证登录状态...")
            login_ok, login_msg = checker.verify_login()
            print()

            if not login_ok:
                final_status = "登录失败"
                print("请重新获取 Cookie 并更新 GitHub Secrets")

            else:
                time.sleep(1)

                print("🔄 开始签到...")
                checkin_success, checkin_msg = checker.checkin()
                print()

                time.sleep(2)

                print("🔄 开始处理每日任务...")
                task_success, task_msg = checker.process_tasks()
                print()

                time.sleep(2)

                print("🔄 获取威望信息...")
                prestige_ok, prestige_msg = checker.get_prestige()
                print()

                if checkin_success and task_success:
                    final_status = "全部完成"
                elif checkin_success or task_success:
                    final_status = "部分完成"
                else:
                    final_status = "执行失败"

    except Exception as e:
        final_status = "运行异常"
        error_msg = str(e)
        print(f"❌ 运行异常: {error_msg}")

    end_time = datetime.now()
    duration = int((end_time - start_time).total_seconds())

    print(f"\n{'=' * 50}")
    if final_status == "全部完成":
        print("✅ 所有任务完成")
    elif final_status == "部分完成":
        print("⚠️ 部分任务完成")
    else:
        print(f"❌ {final_status}")
    print(f"{'=' * 50}")

    subject = f"阡陌居签到结果：{final_status}"

    body = f"""阡陌居自动签到结果

运行时间：{start_time.strftime('%Y-%m-%d %H:%M:%S')}
结束时间：{end_time.strftime('%Y-%m-%d %H:%M:%S')}
耗时：{duration} 秒

登录状态：{"成功" if login_ok else "失败"}
登录信息：{login_msg}

签到状态：{"成功" if checkin_success else "失败"}
签到信息：{checkin_msg}

每日任务状态：{"成功" if task_success else "失败"}
每日任务信息：{task_msg}

积分信息状态：{"成功" if prestige_ok else "失败"}
积分信息：{prestige_msg}

最终结果：{final_status}
"""

    send_email(subject, body)


if __name__ == "__main__":
    main()
