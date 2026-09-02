# bot/secrets_manager.py
import json
import os
import getpass
import base64
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SECRETS_FILE = "data/secrets.json"
CONFIG_FILE = "data/config.json"
KEY_FILE = "data/key.key"

class SecretsManager:
    def __init__(self):
        self.ensure_data_dir()
        self.key = self.load_or_create_key()
        self.cipher = Fernet(self.key)
        self.secrets = self.load_secrets()
    
    def ensure_data_dir(self):
        if not os.path.exists("data"):
            os.makedirs("data")
    
    def load_or_create_key(self):
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(KEY_FILE, 'wb') as f:
                f.write(key)
            return key
    
    def load_secrets(self):
        if os.path.exists(SECRETS_FILE):
            with open(SECRETS_FILE, 'rb') as f:
                encrypted = f.read()
                decrypted = self.cipher.decrypt(encrypted)
                return json.loads(decrypted)
        return {}
    
    def save_secrets(self):
        encrypted = self.cipher.encrypt(json.dumps(self.secrets).encode())
        with open(SECRETS_FILE, 'wb') as f:
            f.write(encrypted)
    
    def get_secret(self, key, default=None):
        return self.secrets.get(key, default)
    
    def set_secret(self, key, value):
        self.secrets[key] = value
        self.save_secrets()
    
    def get_discord_token(self):
        token = self.get_secret('discord_token')
        if not token:
            token = self.prompt_for_token()
        return token
    
    def prompt_for_token(self):
        print("\n" + "="*50)
        print("🔐 NHẬP DISCORD TOKEN")
        print("="*50)
        print("⚠️ Token sẽ được mã hóa và lưu an toàn")
        print("📌 Bạn có thể lấy token tại: https://discord.com/developers/applications")
        print("="*50)
        
        while True:
            token = getpass.getpass("🎯 Nhập Discord Token: ").strip()
            if token:
                confirm = getpass.getpass("🔄 Xác nhận lại Token: ").strip()
                if token == confirm:
                    self.set_secret('discord_token', token)
                    print("\n✅ Token đã được lưu an toàn!\n")
                    return token
                else:
                    print("❌ Token không khớp! Vui lòng nhập lại.\n")
            else:
                print("❌ Token không được để trống!\n")
    
    def get_admin_password(self):
        password = self.get_secret('admin_password')
        if not password:
            password = self.prompt_for_admin_password()
        return password
    
    def prompt_for_admin_password(self):
        print("\n" + "="*50)
        print("🔑 CÀI ĐẶT MẬT KHẨU ADMIN")
        print("="*50)
        
        while True:
            password = getpass.getpass("👤 Nhập mật khẩu admin: ").strip()
            if len(password) < 6:
                print("❌ Mật khẩu phải có ít nhất 6 ký tự!\n")
                continue
            confirm = getpass.getpass("🔄 Xác nhận mật khẩu: ").strip()
            if password == confirm:
                self.set_secret('admin_password', password)
                print("\n✅ Mật khẩu admin đã được lưu!\n")
                return password
            else:
                print("❌ Mật khẩu không khớp!\n")
    
    def get_web_key(self):
        """Lấy key truy cập web"""
        key = self.get_secret('web_access_key')
        if not key:
            key = self.prompt_for_web_key()
        return key
    
    def prompt_for_web_key(self):
        """Tạo hoặc nhập key truy cập web"""
        print("\n" + "="*50)
        print("🔑 CÀI ĐẶT KEY TRUY CẬP WEB")
        print("="*50)
        print("Key này sẽ được dùng để truy cập vào Web Admin")
        print("Bạn có thể tự nhập hoặc để hệ thống tạo tự động")
        print("="*50)
        
        choice = input("Bạn muốn (1) Tự nhập key, (2) Tạo tự động? (1/2): ").strip()
        
        if choice == "1":
            while True:
                key = getpass.getpass("🔑 Nhập key truy cập (tối thiểu 8 ký tự): ").strip()
                if len(key) >= 8:
                    confirm = getpass.getpass("🔄 Xác nhận lại key: ").strip()
                    if key == confirm:
                        self.set_secret('web_access_key', key)
                        print("\n✅ Key truy cập đã được lưu!\n")
                        return key
                    else:
                        print("❌ Key không khớp!\n")
                else:
                    print("❌ Key phải có ít nhất 8 ký tự!\n")
        else:
            # Tạo key tự động
            key = secrets.token_urlsafe(16)
            print(f"\n🔑 Key truy cập của bạn: {key}")
            print("📌 Vui lòng lưu lại key này để sử dụng sau!")
            confirm = input("Đã lưu key? (yes để tiếp tục): ").strip()
            if confirm.lower() == 'yes':
                self.set_secret('web_access_key', key)
                print("\n✅ Key truy cập đã được lưu!\n")
                return key
            else:
                return self.prompt_for_web_key()
    
    def reset_secrets(self):
        confirm = input("⚠️ Bạn có chắc muốn xóa tất cả secrets? (yes/no): ")
        if confirm.lower() == 'yes':
            if os.path.exists(SECRETS_FILE):
                os.remove(SECRETS_FILE)
            if os.path.exists(KEY_FILE):
                os.remove(KEY_FILE)
            print("✅ Đã xóa secrets. Khởi động lại để nhập lại.")
            return True
        return False

# Singleton
secrets_manager = SecretsManager()
