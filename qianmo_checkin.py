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
            'Cookie': cookie,
            'Referer': f'{self.base_url}/forum.php'
        })
    
    def get_formhash(self):
        """获取 formhash 用于签到和任务"""
        try:
            response = self.session.get(f"{self.base_url}/forum.php")
            match = re.search(r'formhash=([a-z0-9]+)', response.text)
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
            # Discuz 签到接口
            checkin_url = f"{self.base_url}/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&inajax=1"
            data = {
                'formhash': formhash,
                'qdxq': 'kx',  # 签到心情：开心
                'qdmode': '1',
                'todaysay': '每日自动签到'
            }
            
            response = self.session.post(checkin_url, data=data)
            
            if '签到成功' in response.text or '已经签到' in response.text:
                print("✅ 签到成功")
                return True
            elif '已经签到' in response.text:
                print("ℹ️  今天已经签到过了")
                return True
            else:
                print(f"❌ 签到失败: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ 签到异常: {e}")
            return False
    
    def get_daily_tasks(self):
        """获取每日任务列表"""
        try:
            response = self.session.get(f"{self.base_url}/home.php?mod=task")
            
            # 查找所有可用任务
            # 匹配任务ID和任务名称
            task_pattern = r'home\.php\?mod=task&do=apply&id=(\d+).*?class="xi2">(.*?)</a>'
            tasks = re.findall(task_pattern, response.text, re.DOTALL)
            
            available_tasks = []
            for task_id, task_name in tasks:
                task_name = re.sub(r'<.*?>', '', task_name).strip()
                if task_name:
                    available_tasks.append({
                        'id': task_id,
                        'name': task_name
                    })
            
            return available_tasks
            
        except Exception as e:
            print(f"❌ 获取任务列表异常: {e}")
            return []
    
    def apply_task(self, task_id, task_name):
        """申请任务"""
        try:
            formhash = self.get_formhash()
            if not formhash:
                return False
            
            apply_url = f"{self.base_url}/home.php?mod=task&do=apply&id={task_id}"
            response = self.session.get(apply_url)
            
            if '成功' in response.text or '已申请' in response.text:
                print(f"  ✅ 申请任务成功: {task_name}")
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
            formhash = self.get_formhash()
            if not formhash:
                return False
            
            draw_url = f"{self.base_url}/home.php?mod=task&do=draw&id={task_id}"
            response = self.session.get(draw_url)
            
            if '成功' in response.text or '恭喜' in response.text:
                # 尝试提取奖励信息
                reward_match = re.search(r'威望.*?(\d+)', response.text)
                if reward_match:
                    reward = reward_match.group(1)
                    print(f"  🎁 领取奖励成功: {task_name} (+{reward} 威望)")
                else:
                    print(f"  🎁 领取奖励成功: {task_name}")
                return True
            elif '已完成' in response.text or '已领取' in response.text:
                print(f"  ℹ️  任务已完成: {task_name}")
                return True
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
            return False
        
        print(f"  📋 找到 {len(tasks)} 个任务\n")
        
        success_count = 0
        
        for task in tasks:
            task_id = task['id']
            task_name = task['name']
            
            print(f"  处理任务: {task_name} (ID: {task_id})")
            
            # 申请任务
            if self.apply_task(task_id, task_name):
                time.sleep(1)  # 等待1秒
                
                # 领取奖励
                if self.draw_task(task_id, task_name):
                    success_count += 1
            
            time.sleep(1)  # 任务间隔
            print()
        
        print(f"  ✅ 成功完成 {success_count}/{len(tasks)} 个任务")
        return success_count > 0
    
    def get_prestige(self):
        """获取威望信息"""
        try:
            response = self.session.get(f"{self.base_url}/home.php?mod=space&do=home")
            
            # 提取威望信息
            prestige_match = re.search(r'威望[：:]\s*(\d+)', response.text)
            credits_match = re.search(r'积分[：:]\s*(\d+)', response.text)
            
            if prestige_match:
                prestige = prestige_match.group(1)
                credits = credits_match.group(1) if credits_match else "未知"
                print(f"📊 当前威望: {prestige} | 积分: {credits}")
                return True
            else:
                print("⚠️  无法获取威望信息")
                return False
                
        except Exception as e:
            print(f"❌ 获取威望异常: {e}")
            return False

def main():
    print(f"{'='*50}")
    print(f"阡陌居自动签到脚本")
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    
    # 从环境变量获取 Cookie
    cookie = os.environ.get('QIANMO_COOKIE')
    
    if not cookie:
        print("❌ 错误: 未设置 QIANMO_COOKIE 环境变量")
        print("请在 GitHub Secrets 中添加 QIANMO_COOKIE")
        return
    
    checker = QianMoCheckin(cookie)
    
    # 1. 执行签到
    print("🔄 开始签到...")
    checkin_success = checker.checkin()
    print()
    
    time.sleep(2)
    
    # 2. 完成每日任务
    task_success = checker.complete_daily_tasks()
    print()
    
    time.sleep(2)
    
    # 3. 获取威望
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
