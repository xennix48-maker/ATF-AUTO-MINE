import requests
import json
import time
import os
import sys
import asyncio
import urllib.parse
import uuid
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from telethon import TelegramClient, functions

# ANSI color codes
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

# Configuration
API_ID = 28752231
API_HASH = 'ec1c1f2c30e2f1855c3edee7e348480b'
SESSION_NAME = "atf_miner"
BASE_URL = "https://atfminers.asloni.online/miner/index.php"
BOT_USERNAME = '@ATF_AIRDROP_bot'

TASKS = [
    {"name": "instagram_like_comment", "display": "Instagram Like & Comment", "icon": "📸"},
    {"name": "twitter_retweet", "display": "Twitter Retweet", "icon": "🐦"},
    {"name": "youtube_like_comment", "display": "YouTube Like & Comment", "icon": "📺"},
    {"name": "website_visit", "display": "Website Visit", "icon": "🌐"}
]

class ATFMinerBot:
    """Professional ATF Miner Automation Bot"""
    
    def __init__(self):
        self.client: Optional[TelegramClient] = None
        self.session_data: Dict[str, Any] = {}
        self.headers: Dict[str, str] = self._initialize_headers()
        self.stats: Dict[str, Any] = {
            "total_claimed": 0,
            "boost_count": 0,
            "tasks_completed": 0,
            "start_time": datetime.now()
        }
        self.last_task_cycle: float = 0
        self.last_session_refresh: float = 0
        
    def _initialize_headers(self) -> Dict[str, str]:
        """Initialize default request headers"""
        return {
            'User-Agent': "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.193 Mobile Safari/537.36",
            'Content-Type': "application/json",
            'x-requested-with': "XMLHttpRequest",
            'origin': "https://atfminers.asloni.online",
            'referer': "https://atfminers.asloni.online/miner/index.html?v=100",
        }
    
    def _get_timestamp(self) -> str:
        """Generate current timestamp in milliseconds"""
        return str(int(time.time() * 1000))
    
    def _clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration for display"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
    
    def display_banner(self):
        """Display professional banner"""
        self._clear_screen()
        banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════╗
║                                                                  ║
║  {Colors.WHITE}█████╗ ████████╗███████╗    ███╗   ███╗██╗███╗   ██╗███████╗██████╗ {Colors.CYAN}║
║  {Colors.WHITE}██╔══██╗╚══██╔══╝██╔════╝    ████╗ ████║██║████╗  ██║██╔════╝██╔══██╗{Colors.CYAN}║
║  {Colors.WHITE}███████║   ██║   █████╗      ██╔████╔██║██║██╔██╗ ██║█████╗  ██████╔╝{Colors.CYAN}║
║  {Colors.WHITE}██╔══██║   ██║   ██╔══╝      ██║╚██╔╝██║██║██║╚██╗██║██╔══╝  ██╔══██╗{Colors.CYAN}║
║  {Colors.WHITE}██║  ██║   ██║   ██║         ██║ ╚═╝ ██║██║██║ ╚████║███████╗██║  ██║{Colors.CYAN}║
║  {Colors.WHITE}╚═╝  ╚═╝   ╚═╝   ╚═╝         ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝{Colors.CYAN}║
║                                                                  ║
║                    {Colors.GREEN}AUTOMATED MINING SYSTEM{Colors.CYAN}                     ║
║                    {Colors.YELLOW}Version 2.0 | Created by MICK{Colors.CYAN}                  ║
╚══════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
        print(banner)
    
    async def authenticate_telegram(self) -> bool:
        """Authenticate with Telegram API"""
        self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        
        try:
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                print(f"{Colors.YELLOW}[•] First-time authentication required{Colors.RESET}")
                phone = input(f"{Colors.WHITE}[?] Enter phone number: {Colors.RESET}")
                await self.client.send_code_request(phone)
                code = input(f"{Colors.WHITE}[?] Enter verification code: {Colors.RESET}")
                await self.client.sign_in(phone, code)
                print(f"{Colors.GREEN}[✓] Authentication successful{Colors.RESET}")
            else:
                print(f"{Colors.GREEN}[✓] Session loaded successfully{Colors.RESET}")
            
            return True
            
        except Exception as e:
            print(f"{Colors.RED}[✗] Authentication failed: {str(e)}{Colors.RESET}")
            return False
    
    async def fetch_session_data(self) -> Tuple[Optional[str], Optional[int], Optional[str]]:
        """Fetch fresh session data from bot"""
        try:
            bot = await self.client.get_entity(BOT_USERNAME)
            await self.client.send_message(bot, '/start')
            await asyncio.sleep(2)
            
            web_view = await self.client(functions.messages.RequestWebViewRequest(
                peer=bot,
                bot=bot,
                platform='android',
                from_bot_menu=True,
                url='https://atfminers.asloni.online'
            ))
            
            raw_url = web_view.url
            init_data = raw_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]
            init_data = urllib.parse.unquote(init_data)
            
            # Parse user information
            user_encoded = init_data.split('user=')[1].split('&')[0]
            user_data = json.loads(urllib.parse.unquote(user_encoded))
            tg_id = int(user_data['id'])
            username = user_data.get('username', '')
            
            return init_data, tg_id, username
            
        except Exception as e:
            print(f"{Colors.RED}[✗] Failed to fetch session: {str(e)}{Colors.RESET}")
            return None, None, None
    
    def authenticate_session(self, init_data: str, tg_id: int, username: str) -> bool:
        """Authenticate with backend API"""
        params = {'action': "login", 't': self._get_timestamp()}
        payload = {
            "initData": init_data,
            "request_id": str(uuid.uuid4()),
            "tg_id": tg_id,
            "username": username
        }
        
        try:
            response = requests.post(BASE_URL, params=params, json=payload, headers=self.headers)
            data = response.json()
            
            session_token = data.get("tma_session_token")
            if session_token:
                self.headers['x-atf-tma-session'] = session_token
                self.headers['cookie'] = f"atf_tma_session={session_token}"
            
            user_info = data.get("user", {})
            self.session_data = {
                "tg_id": tg_id,
                "username": username,
                "display_name": username or user_info.get("first_name", "User"),
                "init_data": init_data
            }
            
            return True
            
        except Exception as e:
            print(f"{Colors.RED}[✗] API authentication failed: {str(e)}{Colors.RESET}")
            return False
    
    def execute_tasks(self) -> int:
        """Start all available tasks"""
        print(f"\n{Colors.CYAN}{'─' * 50}{Colors.RESET}")
        print(f"{Colors.GREEN}[→] INITIATING TASK EXECUTION{Colors.RESET}")
        print(f"{Colors.CYAN}{'─' * 50}{Colors.RESET}")
        
        successful = 0
        
        for idx, task in enumerate(TASKS, 1):
            print(f"\n{Colors.YELLOW}[{idx}/{len(TASKS)}] {task['icon']} {task['display']}{Colors.RESET}")
            
            try:
                params = {'action': "start_task", 't': self._get_timestamp()}
                payload = {
                    "initData": self.session_data['init_data'],
                    "task_id": task['name'],
                    "tg_id": self.session_data['tg_id'],
                    "request_id": str(uuid.uuid4())
                }
                
                response = requests.post(BASE_URL, params=params, json=payload, headers=self.headers)
                result = response.json()
                
                if result.get("status") == "success":
                    print(f"{Colors.GREEN}[✓] Task initiated successfully{Colors.RESET}")
                    successful += 1
                else:
                    print(f"{Colors.YELLOW}[!] Status: {result.get('message', 'Unknown')}{Colors.RESET}")
                    
            except Exception as e:
                print(f"{Colors.RED}[✗] Failed: {str(e)}{Colors.RESET}")
            
            time.sleep(1)
        
        self.stats['tasks_completed'] += successful
        print(f"\n{Colors.GREEN}[✓] Completed {successful}/{len(TASKS)} tasks{Colors.RESET}")
        return successful
    
    def claim_task_rewards(self) -> int:
        """Claim rewards from completed tasks"""
        print(f"\n{Colors.CYAN}{'─' * 50}{Colors.RESET}")
        print(f"{Colors.GREEN}[→] CLAIMING TASK REWARDS{Colors.RESET}")
        print(f"{Colors.CYAN}{'─' * 50}{Colors.RESET}")
        
        total = 0
        
        for idx, task in enumerate(TASKS, 1):
            print(f"\n{Colors.YELLOW}[{idx}/{len(TASKS)}] {task['icon']} {task['display']}{Colors.RESET}")
            
            try:
                params = {'action': "claim_task", 't': self._get_timestamp()}
                payload = {
                    "initData": self.session_data['init_data'],
                    "task_id": task['name'],
                    "tg_id": self.session_data['tg_id'],
                    "request_id": str(uuid.uuid4())
                }
                
                response = requests.post(BASE_URL, params=params, json=payload, headers=self.headers)
                result = response.json()
                
                if result.get("status") == "success":
                    amount = result.get("claimed_amount", 0)
                    total += amount
                    print(f"{Colors.GREEN}[✓] Claimed {amount} ATF{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}[!] {result.get('message', 'Claim failed')}{Colors.RESET}")
                    
            except Exception as e:
                print(f"{Colors.RED}[✗] Error: {str(e)}{Colors.RESET}")
            
            time.sleep(1)
        
        self.stats['total_claimed'] += total
        print(f"\n{Colors.CYAN}{'─' * 50}{Colors.RESET}")
        print(f"{Colors.GREEN}[✓] Total claimed: {total} ATF{Colors.RESET}")
        print(f"{Colors.CYAN}{'─' * 50}{Colors.RESET}")
        
        return total
    
    def process_boost(self) -> bool:
        """Execute boost cycle"""
        try:
            params = {'action': "activate_boost", 't': self._get_timestamp()}
            payload = {
                "initData": self.session_data['init_data'],
                "request_id": str(uuid.uuid4()),
                "tg_id": self.session_data['tg_id'],
                "display_preview": 100.188
            }
            
            response = requests.post(BASE_URL, params=params, json=payload, headers=self.headers)
            result = response.json()
            status = result.get("status")
            
            if status == "success":
                self.stats['boost_count'] += 1
                pending = result.get("pending_reward", "0")
                
                print(f"\n{Colors.CYAN}{'─' * 50}{Colors.RESET}")
                print(f"{Colors.GREEN}[⚡] BOOST #{self.stats['boost_count']}{Colors.RESET}")
                print(f"{Colors.CYAN}{'─' * 50}{Colors.RESET}")
                print(f"{Colors.GREEN}[✓] Pending: {Colors.WHITE}{pending} ATF{Colors.RESET}")
                return True
                
            elif status == "cooldown":
                print(f"\n{Colors.YELLOW}[!] Cooldown active, waiting 10s...{Colors.RESET}")
                time.sleep(10)
                return False
                
            elif status == "penalty":
                remaining = int(result.get("remaining", 0))
                for i in range(remaining, 0, -1):
                    sys.stdout.write(f"\r{Colors.RED}[!] Penalty: {i}s remaining{Colors.RESET}")
                    sys.stdout.flush()
                    time.sleep(1)
                print()
                return False
                
            elif status == "rate_limited":
                print(f"\n{Colors.RED}[!] Rate limited, waiting 60s...{Colors.RESET}")
                time.sleep(60)
                return False
                
            else:
                print(f"\n{Colors.RED}[✗] Boost failed | Status: {status}{Colors.RESET}")
                return False
                
        except Exception as e:
            print(f"\n{Colors.RED}[✗] Boost error: {str(e)}{Colors.RESET}")
            return False
    
    def display_status(self):
        """Display current mining status"""
        runtime = (datetime.now() - self.stats['start_time']).total_seconds()
        
        print(f"\n{Colors.CYAN}{'═' * 50}{Colors.RESET}")
        print(f"{Colors.WHITE}📊 MINING STATUS{Colors.RESET}")
        print(f"{Colors.CYAN}{'─' * 50}{Colors.RESET}")
        print(f"{Colors.WHITE}User:     {Colors.GREEN}{self.session_data.get('display_name', 'Unknown')}{Colors.RESET}")
        print(f"{Colors.WHITE}Runtime:  {Colors.GREEN}{self._format_duration(runtime)}{Colors.RESET}")
        print(f"{Colors.WHITE}Boosts:   {Colors.GREEN}{self.stats['boost_count']}{Colors.RESET}")
        print(f"{Colors.WHITE}Total ATF:{Colors.GREEN} {self.stats['total_claimed']}{Colors.RESET}")
        print(f"{Colors.CYAN}{'═' * 50}{Colors.RESET}")
    
    async def run_task_cycle(self):
        """Execute full task cycle"""
        print(f"\n{Colors.CYAN}{'═' * 50}{Colors.RESET}")
        print(f"{Colors.GREEN}[→] TASK CYCLE INITIATED{Colors.RESET}")
        print(f"{Colors.CYAN}{'═' * 50}{Colors.RESET}")
        
        started = self.execute_tasks()
        
        if started > 0:
            print(f"\n{Colors.YELLOW}[•] Waiting 60 seconds for task completion...{Colors.RESET}")
            for remaining in range(60, 0, -1):
                sys.stdout.write(f"\r{Colors.YELLOW}[•] Time remaining: {remaining:02d}s{Colors.RESET}")
                sys.stdout.flush()
                time.sleep(1)
            print()
            
            self.claim_task_rewards()
        
        self.last_task_cycle = time.time()
    
    async def run(self):
        """Main execution loop"""
        self.display_banner()
        
        # Telegram authentication
        print(f"{Colors.YELLOW}[•] Establishing Telegram connection...{Colors.RESET}")
        if not await self.authenticate_telegram():
            sys.exit(1)
        
        # Fetch session data
        print(f"{Colors.YELLOW}[•] Fetching session data...{Colors.RESET}")
        init_data, tg_id, username = await self.fetch_session_data()
        if not init_data:
            sys.exit(1)
        
        # API authentication
        print(f"{Colors.YELLOW}[•] Authenticating with API...{Colors.RESET}")
        if not self.authenticate_session(init_data, tg_id, username):
            sys.exit(1)
        
        self.display_banner()
        self.display_status()
        
        # Initial task execution
        await self.run_task_cycle()
        
        print(f"\n{Colors.YELLOW}[•] Next task cycle: 4 hours{Colors.RESET}")
        
        # Initialize timers
        self.last_task_cycle = time.time()
        self.last_session_refresh = time.time()
        
        # Main loop
        try:
            while True:
                current_time = time.time()
                
                # Refresh session every 30 minutes
                if current_time - self.last_session_refresh >= 1800:
                    print(f"\n{Colors.YELLOW}[•] Refreshing session...{Colors.RESET}")
                    init_data, tg_id, username = await self.fetch_session_data()
                    if init_data:
                        self.authenticate_session(init_data, tg_id, username)
                        print(f"{Colors.GREEN}[✓] Session refreshed{Colors.RESET}")
                    self.last_session_refresh = current_time
                
                # Execute task cycle every 4 hours
                if current_time - self.last_task_cycle >= 14400:
                    await self.run_task_cycle()
                    print(f"\n{Colors.YELLOW}[•] Next task cycle: 4 hours{Colors.RESET}")
                
                # Process boost
                self.process_boost()
                
                # Countdown to next boost
                for remaining in range(15, 0, -1):
                    sys.stdout.write(f"\r{Colors.YELLOW}[•] Next boost: {remaining:02d}s{Colors.RESET}")
                    sys.stdout.flush()
                    time.sleep(1)
                print()
                
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}[!] Shutting down miner...{Colors.RESET}")
            self.display_status()
            print(f"\n{Colors.GREEN}[✓] Session terminated gracefully{Colors.RESET}")

async def main():
    bot = ATFMinerBot()
    await bot.run()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}[✗] Fatal error: {str(e)}{Colors.RESET}")
        sys.exit(1)