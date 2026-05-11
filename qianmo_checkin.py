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
        
        self.core_cookies = self._extract_core_cookies(cookie)
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': f'{self.base_url}/forum.php'
        })
        
        self._set_cookies(cookie)
    
    def _extract_core_cookies(self, cookie_string):
        """提取核心认证 Cookie"""
        core_keys = ['auth', 'saltkey']
        core_cookies = {}
        
        for item in cookie_string.split(';'):
            item = item.strip()
            if '=' in item:
                key, value = item.split('=', 1)
                for core_key in core_keys:
                    if core_key in key:
                        core_cookies[key] = value
        
        return core_cookies
    
    def _set_cookies(self, cookie_string):
        """设置 Cookie 到 session"""
        for item in cookie_string.split(';'):
            item = item.strip()
            if '=' in item:
                key, value = item.split('=', 1)
                self.session.cookies.set(key, value, domain='.1000qm.vip')
    
    def _update_session_cookies(self, response):
        """从响应中更新 session cookies"""
        pass
    
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
            print("❌ 无法获取 formhash，签到失败")
            return False
        
        try:
            checkin_url = f"{self.base_url}/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&inajax=1"
            data = {
                'formhash': formhash,
                'qdxq': 'kx',
                'qdmode': '1',
                'todaysay': '每日自动签到'
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
    
    def get_daily_tasks(self):
        """获取每日任务列表"""
        try:
            # 先访问任务主页
            response = self.session.get(f"{self.base_url}/home.php?mod=task")
            print(f"  [调试] 任务页面响应长度: {len(response.text)}")
            
            # 尝试多种模式匹配任务
            patterns = [
                # 模式1: 标准链接
                r'<a\s+href="home\.php\?mod=task&(?:amp;)?do=(?:view|apply)&(?:amp;)?id=(\d+)"[^>]*>([^<]+)</a>',
                # 模式2: 任务表格
                r'<h3[^>]*>\s*<a[^>]*id=(\d+)[^>]*>([^<]+)</a>',
                # 模式3: 简化版
                r'do=apply&(?:amp;)?id=(\d+)[^>]*>([^<]+)<',
            ]
            
            all_tasks = []
            
            for pattern in patterns:
                tasks = re.findall(pattern, response.text)
                if tasks:
                    print(f"  [调试] 使用模式匹配到 {len(tasks)} 个任务")
                    all_tasks.extend(tasks)
            
            # 去重
            available_tasks = []
            seen_ids = set()
            
            for task_id, task_name in all_tasks:
                if task_id in seen_ids:
                    continue
                seen_ids.add(task_id)
                
                task_name = task_name.strip()
                # 过滤掉明显不是任务名的内容
                if task_name and len(task_name) < 50 and '搜索' not in task_name:
                    available_tasks.append({
                        'id': task_id,
                        'name': task_name
                    })
                    print(f"  发现任务: {task_name} (ID: {task_id})")
            
            # 如果没找到任务,保存页面用于调试
            if not available_tasks:
                with open('/tmp/task_page.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"  [调试] 任务页面已保存到 /tmp/task_page.html")
            
            return available_tasks
            
        except Exception as e:
            print(f"❌ 获取任务列表异常: {e}")
            return []
    
    def apply_task(self, task_id, task_name):
        """申请任务"""
        try:
            apply_url = f"{self.base_url}/home.php?mod=task&do=apply&id={task_id}"
            response = self.session.get(apply_url)
            response_text = response.text
            
            # 检查是否需要确认
            if '确认' in response_text or 'confirm' in response_text.lower():
                # 尝试直接确认
                confirm_url = f"{self.base_url}/home.php?mod=task&do=apply&id={task_id}&confirm=1"
                response = self.session.get(confirm_url)
                response_text = response.text
            
            if '成功接受任务' in response_text or '申请成功' in response_text:
                print(f"  ✅ 申请任务成功: {task_name}")
                return True
            elif '已申请过' in response_text or '您已经申请过' in response_text or '进行中' in response_text:
                print(f"  ℹ️  任务已申请: {task_name}")
                return True
            else:
                # 提取可能的错误信息
                error_patterns = [
                    r'<div[^>]*class="[^"]*alert[^"]*"[^>]*>(.*?)</div>',
                    r'<p[^>]*class="[^"]*error[^"]*"[^>]*>(.*?)</p>',
                    r'showDialog\([\'"]([^\'"]+)[\'"]\)',
                ]
                
                for pattern in error_patterns:
                    error_match = re.search(pattern, response_text, re.DOTALL)
                    if error_match:
                        error_msg = re.sub(r'<[^>]+>', '', error_match.group(1)).strip()
                        if error_msg:
                            print(f"  ⚠️  申请失败: {error_msg}")
                            return False
                
                print(f"  ⚠️  申请任务失败: {task_name}")
                return False
                
        except Exception as e:
            print(f"  ❌ 申请任务异常: {e}")
            return False
    
    def draw_task(self, task_id, task_name):
        """领取任务奖励"""
        try:
            draw_url = f"{self.base_url}/home.php?mod=task&do=draw&id={task_id}"
            response = self.session.get(draw_url)
            response_text = response.text
            
            if '恭喜' in response_text or '成功' in response_text:
                reward_match = re.search(r'威望.*?(\d+)', response_text)
                if reward_match:
                    reward = reward_match.group(1)
                    print(f"  🎁 领取奖励成功: {task_name} (+{reward} 威望)")
                else:
                    print(f"  🎁 领取奖励成功: {task_name}")
                return True
            elif '已完成' in response_text or '已领取' in response_text:
                print(f"  ℹ️  任务已完成: {task_name}")
                return True
            elif '还未完成' in response_text or '未完成' in response_text:
                print(f"  ⏳ 任务未完成: {task_name}")
                return False
            else:
                print(f"  ⚠️  领取奖励失败: {task_name}")
                return False
                
        except Exception as e:
            print(f"  ❌ 领取奖励异常: {e}")
            return False
    
    def complete_daily_tasks(self):
        """完成每日威望任务"""
        print("🔄 开始处理每日任务...")
        
        tasks = self.get_daily_tasks()
        
        if not tasks:
            print("  ⚠️  未找到可用任务")
            print("  💡 提示: 请访问 https://www.1000qm.vip/home.php?mod=task 查看任务状态")
            return False
        
        print(f"  📋 找到 {len(tasks)} 个任务\n")
        
        success_count = 0
        
        for task in tasks:
            task_id = task['id']
            task_name = task['name']
            
            print(f"  处理任务: {task_name} (ID: {task_id})")
            
            if self.apply_task(task_id, task_name):
                time.sleep(2)
                
                if self.draw_task(task_id, task_name):
                    success_count += 1
            
            time.sleep(1)
            print()
        
        print(f"  ✅ 成功完成 {success_count}/{len(tasks)} 个任务")
        return success_count > 0
    
    def get_prestige(self):
        """获取威望信息"""
        try:
            response = self.session.get(f"{self.base_url}/home.php?mod=spacecp&ac=credit&showcredit=1")
            
            prestige = None
            credits = None
            
            # 尝试多种模式匹配威望
            patterns = [
                r'威望[：:]\s*(\d+)',
                r'<em>威望</em>\s*<span[^>]*>(\d+)</span>',
                r'威望.*?(\d+)',
            ]
            
            for pattern in patterns:
                prestige_match = re.search(pattern, response.text)
                if prestige_match:
                    prestige = prestige_match.group(1)
                    break
            
            credits_match = re.search(r'积分[：:]\s*(\d+)', response.text)
            if credits_match:
                credits = credits_match.group(1)
            
            if prestige:
                credits_str = credits if credits else "未知"
                print(f"📊 当前威望: {prestige} | 积分: {credits_str}")
                return True
            else:
                print("⚠️  无法获取威望信息,可能需要更新 Cookie")
                return False
                
        except Exception as e:
            print(f"❌ 获取威望异常: {e}")
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
    
    task_success = checker.complete_daily_tasks()
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
    
    print(f"提示: https://www.1000qm.vip/home.php?mod=task 或 https://www.1000qm.vip/home.php?mod=task&item=new 有每日威望红包任务")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
