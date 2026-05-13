# qianmo_checkin.py
import requests
import os
import re
from datetime import datetime
import time

class QianMoCheckin:
    def __init__(self, cookie):
        self.base_url = "https://www.1000qm.vip"
        self.session = requests.Session()
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': f'{self.base_url}/forum.php'
        })
        
        self._set_cookies(cookie)
    
    def _set_cookies(self, cookie_string):
        """设置 Cookie 到 session"""
        for item in cookie_string.split(';'):
            item = item.strip()
            if '=' in item:
                key, value = item.split('=', 1)
                self.session.cookies.set(key, value, domain='.1000qm.vip')
    
    def get_formhash(self):
        """获取 formhash"""
        try:
            response = self.session.get(f"{self.base_url}/forum.php")
            
            match = re.search(r'formhash=([a-z0-9]+)', response.text)
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
            print("❌ 无法获取 formhash,签到失败")
            return False
        
        try:
            checkin_url = f"{self.base_url}/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&inajax=1"
            data = {
                'formhash': formhash,
                'qdxq': 'kx',
                'qdmode': '1',
                'todaysay': '开心是一种选择，快乐融入日常，感受每一个美好的瞬间！'
            }
            
            response = self.session.post(checkin_url, data=data)
            response_text = response.text
            
            if '签到成功' in response_text:
                print("✅ 签到成功")
                return True
            elif '已经签到' in response_text or '您今天已经签到过了' in response_text:
                print("ℹ️  今天已经签到过了")
                return True
            else:
                error_match = re.search(r'<root><!\[CDATA\[(.*?)\]\]></root>', response_text)
                if error_match:
                    error_msg = error_match.group(1)
                    print(f"❌ 签到失败: {error_msg}")
                else:
                    print(f"❌ 签到失败")
                return False
                
        except Exception as e:
            print(f"❌ 签到异常: {e}")
            return False
    
    def check_task_status(self):
        """检查任务状态 - 返回 'new', 'doing', 'done', 'unknown'"""
        try:
            # 先检查新任务页面
            response = self.session.get(f"{self.base_url}/home.php?mod=task&item=new")
            html = response.text
            
            # 如果在新任务页面找到，说明可以申请
            if re.search(r'<a href="home\.php\?mod=task&amp;do=apply&amp;id=1"[^>]*>立即申请</a>', html):
                return 'new'
            
            # 检查进行中的任务
            response = self.session.get(f"{self.base_url}/home.php?mod=task&item=doing")
            html = response.text
            
            # 如果在进行中页面找到
            if re.search(r'<a href="home\.php\?mod=task&amp;do=view&amp;id=1">每日威望红包</a>', html):
                return 'doing'
            
            # 检查已完成的任务，并验证是否是今天完成的
            response = self.session.get(f"{self.base_url}/home.php?mod=task&item=done")
            html = response.text
            
            # 查找任务和完成时间
            pattern = r'<a href="home\.php\?mod=task&amp;do=view&amp;id=1">每日威望红包</a>.*?完成于 (\d{4}-\d{1,2}-\d{1,2} \d{2}:\d{2})'
            match = re.search(pattern, html, re.DOTALL)
            
            if match:
                complete_time_str = match.group(1)
                # 解析完成时间
                complete_time = datetime.strptime(complete_time_str, '%Y-%m-%d %H:%M')
                today = datetime.now().date()
                
                # 如果是今天完成的，返回 done
                if complete_time.date() == today:
                    return 'done'
                else:
                    # 昨天或更早完成的，应该可以重新申请
                    return 'new'
            
            return 'unknown'
            
        except Exception as e:
            print(f"  检查任务状态异常: {e}")
            return 'unknown'
    
    def process_tasks(self):
        """处理每日任务"""
        try:
            # 检查任务状态
            status = self.check_task_status()
            
            if status == 'done':
                print(f"  ✅ 每日威望红包任务今天已完成")
                return True
            
            if status == 'unknown':
                print(f"  ⚠️  无法确定任务状态")
                return False
            
            task_id = '1'
            task_name = '每日威望红包'
            
            # 如果任务是新的，需要先申请
            if status == 'new':
                print(f"  📋 发现新任务: {task_name}")
                
                # 申请任务
                apply_url = f"{self.base_url}/home.php?mod=task&do=apply&id={task_id}"
                apply_response = self.session.get(apply_url)
                apply_text = apply_response.text
                
                # 检查申请结果
                apply_success = False
                if '成功接受任务' in apply_text or '成功' in apply_text:
                    print(f"  ✅ 申请任务成功")
                    apply_success = True
                elif '您已经申请过' in apply_text or '进行中' in apply_text:
                    print(f"  ℹ️  任务已申请")
                    apply_success = True
                elif '已完成' in apply_text:
                    print(f"  ✅ 任务已完成")
                    return True
                
                time.sleep(1)
            
            elif status == 'doing':
                print(f"  📋 任务进行中: {task_name}")
                apply_success = True
            else:
                apply_success = False
            
            # 尝试完成任务
            draw_url = f"{self.base_url}/home.php?mod=task&do=draw&id={task_id}"
            draw_response = self.session.get(draw_url)
            draw_text = draw_response.text
            
            # 多种成功判断条件
            success_keywords = [
                '恭喜',
                '成功完成任务',
                '任务已完成',
                '领取成功',
                '奖励已发放'
            ]
            
            is_success = any(keyword in draw_text for keyword in success_keywords)
            
            # 也检查是否有错误提示
            error_keywords = [
                '您还没有申请',
                '任务不存在',
                '操作失败'
            ]
            
            has_error = any(keyword in draw_text for keyword in error_keywords)
            
            if is_success and not has_error:
                # 提取奖励信息
                reward_match = re.search(r'威望.*?(\d+)', draw_text)
                if reward_match:
                    reward = reward_match.group(1)
                    print(f"  🎁 完成任务成功 (+{reward} 威望)")
                else:
                    print(f"  ✅ 完成任务成功")
                return True
            
            # 如果没有明确的成功或失败信息，检查任务状态来确认
            time.sleep(1)
            new_status = self.check_task_status()
            
            if new_status == 'done':
                print(f"  ✅ 任务完成成功")
                return True
            elif new_status == 'new':
                # 任务又变成新的了，说明完成成功
                print(f"  ✅ 任务完成成功")
                return True
            else:
                print(f"  ⚠️  任务完成失败")
                return False
                
        except Exception as e:
            print(f"❌ 处理任务异常: {e}")
            return False
    
    def get_prestige(self):
        """获取威望和铜币信息"""
        try:
            response = self.session.get(f"{self.base_url}/home.php?mod=spacecp&ac=credit&showcredit=1")
            html = response.text
            
            # 匹配威望
            prestige_match = re.search(r'<em>\s*威望:\s*</em>(\d+)', html)
            # 匹配铜币
            copper_match = re.search(r'<em>\s*铜币:\s*</em>(\d+)', html)
            # 匹配积分
            credits_match = re.search(r'<em>积分:\s*</em>(\d+)', html)
            
            result = []
            if prestige_match:
                result.append(f"威望: {prestige_match.group(1)}")
            if copper_match:
                result.append(f"铜币: {copper_match.group(1)}")
            if credits_match:
                result.append(f"积分: {credits_match.group(1)}")
            
            if result:
                print(f"📊 {' | '.join(result)}")
                return True
            else:
                print("⚠️  无法获取积分信息")
                return False
                
        except Exception as e:
            print(f"❌ 获取积分异常: {e}")
            return False
    
    def verify_login(self):
        """验证登录状态"""
        try:
            response = self.session.get(f"{self.base_url}/forum.php")
            
            if 'member.php?mod=logging&action=login' in response.text:
                print("❌ Cookie 已失效,请重新获取")
                return False
            
            username_match = re.search(r'<a[^>]*title="访问我的空间"[^>]*>([^<]+)</a>', response.text)
            if username_match:
                username = username_match.group(1).strip()
                print(f"✅ 登录验证成功,用户: {username}")
                return True
            
            print("✅ 登录验证成功")
            return True
            
        except Exception as e:
            print(f"❌ 验证登录异常: {e}")
            return False

def main():
    print(f"{'='*50}")
    print(f"阡陌居自动签到脚本")
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    
    cookie = os.environ.get('QIANMO_COOKIE')
    
    if not cookie:
        print("❌ 错误: 未设置 QIANMO_COOKIE 环境变量")
        return
    
    checker = QianMoCheckin(cookie)
    
    print("🔄 验证登录状态...")
    if not checker.verify_login():
        print("\n请重新获取 Cookie 并更新 GitHub Secrets")
        return
    print()
    
    time.sleep(1)
    
    print("🔄 开始签到...")
    checkin_success = checker.checkin()
    print()
    
    time.sleep(2)
    
    print("🔄 开始处理每日任务...")
    task_success = checker.process_tasks()
    print()
    
    time.sleep(2)
    
    print("🔄 获取威望信息...")
    checker.get_prestige()
    
    print(f"\n{'='*50}")
    if checkin_success and task_success:
        print("✅ 所有任务完成")
    elif checkin_success or task_success:
        print("⚠️  部分任务完成")
    else:
        print("❌ 任务执行失败")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
