import requests
import json
import time
import os
import sys
import random
import asyncio
import urllib.parse
import uuid
import threading
from datetime import datetime
from telethon import TelegramClient, functions

R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
B = '\033[94m'
C = '\033[96m'
W = '\033[97m'
RESET = '\033[0m'

API_ID = 28752231
API_HASH = 'ec1c1f2c30e2f1855c3edee7e348480b'
SESSION_NAME = "atf_miner"

TASKS = [
    {"name": "instagram_like_comment", "display": "📸 Instagram Like & Comment"},
    {"name": "twitter_retweet", "display": "🐦 Twitter Retweet"},
    {"name": "youtube_like_comment", "display": "📺 YouTube Like & Comment"},
    {"name": "website_visit", "display": "🌐 Website Visit"}
]

def get_timestamp():
    return str(int(time.time() * 1000))

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

async def refresh_session(client, bot_ent):
    """Refresh the webview to get new init data"""
    web_view = await client(functions.messages.RequestWebViewRequest(
        peer=bot_ent, 
        bot=bot_ent, 
        platform='android', 
        from_bot_menu=True,
        url='https://atfminers.asloni.online'
    ))
    
    raw_url = web_view.url
    raw_data = raw_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]
    init_data = urllib.parse.unquote(raw_data)
    
    try:
        user_encoded = init_data.split('user=')[1].split('&')[0]
        user_json = json.loads(urllib.parse.unquote(user_encoded))
        tg_id = int(user_json['id'])
        username = user_json.get('username', '')
    except Exception as e:
        print(f"{R}[!] Failed to parse user data. Error: {e}{RESET}")
        return None, None, None
    
    return init_data, tg_id, username

def start_tasks(url, headers, tg_id, init_data):
    """Start all 4 tasks"""
    print(f"\n{C}{'='*50}{RESET}")
    print(f"{G}🚀 STARTING TASKS{RESET}")
    print(f"{C}{'='*50}{RESET}")
    
    success_count = 0
    # Start all 4 tasks
    for idx, task in enumerate(TASKS, 1):
        print(f"\n{Y}[{idx}/4] Starting: {task['display']}{RESET}")
        
        try:
            params_start = {'action': "start_task", 't': get_timestamp()}
            payload_start = {
                "initData": init_data,
                "task_id": task['name'],
                "tg_id": tg_id,
                "request_id": str(uuid.uuid4())
            }
            
            resp_start = requests.post(url, params=params_start, data=json.dumps(payload_start), headers=headers)
            data_start = resp_start.json()
            
            if data_start.get("status") == "success":
                print(f"{G}[+] Started successfully{RESET}")
                success_count += 1
            else:
                print(f"{Y}[!] Status: {data_start.get('message', 'Unknown')}{RESET}")
                
        except Exception as e:
            print(f"{R}[-] Failed: {e}{RESET}")
        
        time.sleep(1)
    
    print(f"\n{G}[+] Started {success_count}/{len(TASKS)} tasks!{RESET}")
    print(f"{C}{'='*50}{RESET}")
    return success_count

def claim_tasks(url, headers, tg_id, init_data):
    """Claim rewards from all tasks"""
    print(f"\n{C}{'='*50}{RESET}")
    print(f"{G}💰 CLAIMING TASK REWARDS{RESET}")
    print(f"{C}{'='*50}{RESET}")
    
    total_claimed = 0
    for idx, task in enumerate(TASKS, 1):
        print(f"\n{Y}[{idx}/4] Claiming: {task['display']}{RESET}")
        
        try:
            params_claim = {'action': "claim_task", 't': get_timestamp()}
            payload_claim = {
                "initData": init_data,
                "task_id": task['name'],
                "tg_id": tg_id,
                "request_id": str(uuid.uuid4())
            }
            
            resp_claim = requests.post(url, params=params_claim, data=json.dumps(payload_claim), headers=headers)
            data_claim = resp_claim.json()
            
            if data_claim.get("status") == "success":
                claimed = data_claim.get("claimed_amount", 0)
                total_claimed += claimed
                print(f"{G}[+] Claimed {claimed} ATF{RESET}")
            else:
                print(f"{Y}[!] Claim failed: {data_claim.get('message', 'Unknown')}{RESET}")
                
        except Exception as e:
            print(f"{R}[-] Error: {e}{RESET}")
        
        time.sleep(1)
    
    print(f"\n{C}{'='*50}{RESET}")
    print(f"{G}🎉 TOTAL CLAIMED: {total_claimed} ATF{RESET}")
    print(f"{C}{'='*50}{RESET}")
    
    return total_claimed

def boost_cycle(url, headers, tg_id, init_data, boost_count):
    """Single boost cycle - 15 seconds"""
    try:
        params_boost = {'action': "activate_boost", 't': get_timestamp()}
        payload_boost = {
            "initData": init_data,
            "request_id": str(uuid.uuid4()),
            "tg_id": tg_id,
            "display_preview": 100.188
        }
        resp_boost = requests.post(url, params=params_boost, data=json.dumps(payload_boost), headers=headers)
        data_boost = resp_boost.json()

        if data_boost.get("status") == "success":
            pending_reward = data_boost.get("pending_reward", "0")
            print(f"\n{C}{'='*50}{RESET}")
            print(f"{G}⚡ BOOST #{boost_count}{RESET}")
            print(f"{C}{'='*50}{RESET}")
            print(f"{G}[+] Pending Reward: {W}{pending_reward} ATF{RESET}")
            return True
        elif data_boost.get("status") == "cooldown":
            print(f"\n{Y}[!] Cooldown, waiting 10s...{RESET}")
            time.sleep(10)
            return False
        elif data_boost.get("status") == "penalty":
            remaining = int(data_boost.get("remaining", 0))
            for s in range(remaining, 0, -1):
                sys.stdout.write(f"\r{R}[!] Penalty | waiting: {s}s   {RESET}")
                sys.stdout.flush()
                time.sleep(1)
            print()
            return False
        elif data_boost.get("status") == "rate_limited":
            print(f"\n{R}[!] Rate limited, waiting 60s...{RESET}")
            time.sleep(60)
            return False
        else:
            print(f"\n{R}[-] Failed | Status: {data_boost.get('status', 'error')}{RESET}")
            return False
        
    except Exception as e:
        print(f"\n{R}[!] Error: {e}{RESET}")
        return False

async def main():
    clear_terminal()
    print(f"{C}========================================{RESET}")
    print(f"{G}⛏️  ATF MINER AUTO MINING & BOOST ⛏️{RESET}")
    print(f"{C}========================================{RESET}")
    print(f"{W}Created By : {Y}Kelvin{RESET}")
    print(f"{C}========================================{RESET}\n")
    
    # Connect to Telegram
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            phone_number = input(f"{W}Enter Your Telegram Number => {RESET}")
            await client.send_code_request(phone_number)
            otp_code = input(f"{W}Enter Telegram OTP => {RESET}")
            await client.sign_in(phone_number, otp_code)
            print(f"{G}[+] Session saved!{RESET}")
        else:
            print(f"{G}[+] Session loaded!{RESET}")
            
    except Exception as e:
        print(f"{R}[!] Error: {e}{RESET}")
        sys.exit(1)
    
    # Get bot entity and initial data
    bot_ent = await client.get_entity('@ATF_AIRDROP_bot')
    await client.send_message(bot_ent, '/start')
    await asyncio.sleep(2)
    
    init_data, tg_id, username = await refresh_session(client, bot_ent)
    if not init_data:
        sys.exit(1)
    
    # Login to get token
    url = "https://atfminers.asloni.online/miner/index.php"
    login_params = {'action': "login", 't': get_timestamp()}
    login_payload = {
        "initData": init_data, 
        "request_id": str(uuid.uuid4()),
        "tg_id": tg_id,
        "username": username
    }
    
    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.193 Mobile Safari/537.36",
        'Content-Type': "application/json",
        'x-requested-with': "XMLHttpRequest",
        'origin': "https://atfminers.asloni.online",
        'referer': "https://atfminers.asloni.online/miner/index.html?v=100",
    }
    
    resp_login = requests.post(url, params=login_params, data=json.dumps(login_payload), headers=headers)
    data_login = resp_login.json()
    
    tma_token = data_login.get("tma_session_token")
    if tma_token:
        headers['x-atf-tma-session'] = tma_token
        headers['cookie'] = f"atf_tma_session={tma_token}"
    
    user_data = data_login.get("user", {})
    first_name = user_data.get("first_name", "")
    display_name = username if username else first_name
    
    clear_terminal()
    print(f"{C}========================================{RESET}")
    print(f"{G}⛏️  ATF MINER AUTO MINING & BOOST ⛏️{RESET}")
    print(f"{C}========================================{RESET}")
    print(f"{W}Created By : {Y}Kelvin{RESET}")
    print(f"{C}========================================{RESET}")
    print(f"\n{G}🎉 Welcome {C}{display_name} {G}! 🎉{RESET}")
    print(f"{C}========================================{RESET}\n")
    
    # On first run, do full task cycle
    print(f"\n{C}{'='*50}{RESET}")
    print(f"{G}📋 FIRST CYCLE - STARTING TASKS{RESET}")
    print(f"{C}{'='*50}{RESET}")
    
    # Start tasks
    started = start_tasks(url, headers, tg_id, init_data)
    
    if started > 0:
        # Wait 1 minute
        print(f"\n{Y}[*] Waiting 1 minute for tasks to complete...{RESET}")
        for remaining in range(60, 0, -1):
            sys.stdout.write(f"\r{Y}[*] Time remaining: {remaining:02d} seconds {RESET}")
            sys.stdout.flush()
            time.sleep(1)
        print(f"\n{G}[+] Wait completed!{RESET}")
        
        # Claim tasks
        claim_tasks(url, headers, tg_id, init_data)
    
    print(f"\n{Y}[*] Next tasks cycle in: 4 hours 0 minutes{RESET}")
    print(f"{C}{'='*50}{RESET}\n")
    
    # Start boost counter
    boost_count = 0
    
    # Main loop - runs boost every 15 seconds and tasks every 4 hours
    last_task_time = time.time()
    last_refresh_time = time.time()
    
    while True:
        current_time = time.time()
        
        # Refresh session every 30 minutes
        if current_time - last_refresh_time >= 1800:
            print(f"\n{Y}[*] Refreshing session...{RESET}")
            new_init_data, new_tg_id, new_username = await refresh_session(client, bot_ent)
            if new_init_data:
                init_data = new_init_data
                tg_id = new_tg_id
                
                login_payload = {
                    "initData": init_data, 
                    "request_id": str(uuid.uuid4()),
                    "tg_id": tg_id,
                    "username": username
                }
                resp_login = requests.post(url, params=login_params, data=json.dumps(login_payload), headers=headers)
                data_login = resp_login.json()
                
                tma_token = data_login.get("tma_session_token")
                if tma_token:
                    headers['x-atf-tma-session'] = tma_token
                    headers['cookie'] = f"atf_tma_session={tma_token}"
                
                print(f"{G}[+] Session refreshed!{RESET}")
                last_refresh_time = current_time
        
        # Check if 4 hours passed for tasks
        if current_time - last_task_time >= 4 * 3600:
            print(f"\n{C}{'='*50}{RESET}")
            print(f"{G}📋 4 HOUR TASK CYCLE{RESET}")
            print(f"{C}{'='*50}{RESET}")
            
            # Start tasks
            started = start_tasks(url, headers, tg_id, init_data)
            
            if started > 0:
                # Wait 1 minute
                print(f"\n{Y}[*] Waiting 1 minute for tasks to complete...{RESET}")
                for remaining in range(60, 0, -1):
                    sys.stdout.write(f"\r{Y}[*] Time remaining: {remaining:02d} seconds {RESET}")
                    sys.stdout.flush()
                    time.sleep(1)
                print(f"\n{G}[+] Wait completed!{RESET}")
                
                # Claim tasks
                claim_tasks(url, headers, tg_id, init_data)
            
            last_task_time = current_time
            print(f"\n{Y}[*] Next tasks cycle in: 4 hours 0 minutes{RESET}")
            print(f"{C}{'='*50}{RESET}\n")
        
        # Boost every 15 seconds
        boost_count += 1
        boost_cycle(url, headers, tg_id, init_data, boost_count)
        
        # Wait 15 seconds
        for remaining in range(15, 0, -1):
            sys.stdout.write(f"\r{Y}[*] Next boost in: {remaining:02d} seconds {RESET}")
            sys.stdout.flush()
            time.sleep(1)
        print()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Y}[!] Stopping miner...{RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{R}[!] Error: {e}{RESET}")
        sys.exit(1)