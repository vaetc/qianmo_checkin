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
    
    def check_task_status(self):
        """检查任务状态"""
        try:
            # 检查新任务
            response = self.session.get(f"{self.base_url}/home.php?mod=task&item=new")
            new_tasks = self._extract_tasks(response.text, "新任务")
            
            # 检查进行中的任务
            response = self.session.get(f"{self.base_url}/home.php?mod=task&item=doing")
            doing_tasks = self._extract_tasks(response.text, "进行中")
            
            # 检查已完成的任务
            response = self.session.get(f"{self.base_url}/home.php?mod=task&item=done")
            done_tasks = self._extract_tasks(response.text, "已完成")
            
            return {
                'new': new_tasks,
                'doing': doing_tasks,
                'done': done_tasks
            }
            
        except Exception as e:
            print(f"❌ 检查任务状态异常: {e}")
            return None
    
    def _extract_tasks(self, html, status):
        """从HTML中提取任务信息"""
        tasks = []
        
        # 检查是否有"暂无新任务"提示
        if '暂无新任务' in html or '周期性任务完成后可以再次申请' in html:
            return tasks
        
        # 匹配任务表格中的任务
        # <a href="home.php?mod=task&amp;do=view&amp;id=1">每日威望红包</a>
        pattern = r'<a\s+href="home\.php\?mod=task&(?:amp;)?do=(?:view|apply|draw)&(?:amp;)?id=(\d+)"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html)
        
        seen_ids = set()
        for task_id, task_name in matches:
            if task_id in seen_ids:
                continue
            seen_ids.add(task_id)
            
            task_name = task_name.strip()
            if task_name and len(task_name) < 50:
                tasks.append({
                    'id': task_id,
                    'name': task_name,
                    'status': status
                })
        
        return tasks
    
    def apply_task(self, task_id, task_name):
        """申请任务"""
        try:
            apply_url = f"{self.base_url}/home.php?mod=task&do=apply&id={task_id}"
            response = self.session.get(apply_url)
            response_text = response.text
            
            # 检查是否需要确认
            if '确认' in response_text or 'confirm' in response_text.lower():
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
        
        # 检查所有任务状态
        task_status = self.check_task_status()
        
        if not task_status:
            print("  ⚠️  无法获取任务状态")
            return False
        
        # 显示任务状态
        if task_status['new']:
            print(f"  📋 新任务: {len(task_status['new'])} 个")
            for task in task_status['new']:
                print(f"    - {task['name']} (ID: {task['id']})")
        
        if task_status['doing']:
            print(f"  ⏳ 进行中: {len(task_status['doing'])} 个")
            for task in task_status['doing']:
                print(f"    - {task['name']} (ID: {task['id']})")
        
        if task_status['done']:
            print(f"  ✅ 已完成: {len(task_status['done'])} 个")
            for task in task_status['done']:
                print(f"    - {task['name']} (ID: {task['id']})")
        
        print()
        
        # 处理新任务和进行中的任务
        success_count = 0
        all_tasks = task_status['new'] + task_status['doing']
        
        if not all_tasks:
            if task_status['done']:
                print("  ✅ 所有任务已完成")
                return True
            else:
                print("  ⚠️  未找到可处理的任务")
                return False
        
        for task in all_tasks:
            task_id = task['id']
            task_name = task['name']
            
            print(f"  处理任务: {task_name} (ID: {task_id})")
            
            # 如果是新任务,先申请
            if task['status'] == '新任务':
                if not self.apply_task(task_id, task_name):
                    print()
                    continue
                time.sleep(2)
            
            # 尝试领取奖励
            if self.draw_task(task_id, task_name):
                success_count += 1
            
            time.sleep(1)
            print()
        
        print(f"  ✅ 成功完成 {success_count}/{len(all_tasks)} 个任务")
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
                print("⚠️  无法获取威望信息")
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
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
