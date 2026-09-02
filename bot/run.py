# bot/run.py
import subprocess
import sys
import os
import threading
import time
import signal
import logging
from secrets_manager import secrets_manager
from config_manager import config_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_first_run():
    """Kiểm tra lần đầu chạy"""
    if not os.path.exists("data/secrets.json"):
        print("\n" + "="*60)
        print("   🎮 CHÀO MỪNG ĐẾN VỚI GAME MQ SYSTEM")
        print("="*60)
        print("Đây là lần đầu tiên bạn chạy hệ thống!")
        print("Chúng tôi sẽ thiết lập cấu hình bảo mật...")
        print("="*60 + "\n")
        return True
    return False

def run_bot():
    """Chạy Bot Discord"""
    logger.info("🤖 Khởi động Bot Discord...")
    try:
        from bot import run_bot
        run_bot()
    except Exception as e:
        logger.error(f"Lỗi Bot: {e}")
        sys.exit(1)

def run_web():
    """Chạy Web Server"""
    logger.info("🌐 Khởi động Web Server...")
    try:
        from web_server import run_web_server
        run_web_server()
    except Exception as e:
        logger.error(f"Lỗi Web Server: {e}")
        sys.exit(1)

def main():
    logger.info("="*60)
    logger.info("   🚀 KHỞI ĐỘNG HỆ THỐNG GAME MQ")
    logger.info("="*60)
    
    # Kiểm tra lần đầu chạy
    if check_first_run():
        secrets_manager.get_discord_token()
        secrets_manager.get_admin_password()
        secrets_manager.get_web_key()
        print("\n✅ Thiết lập hoàn tất! Khởi động hệ thống...\n")
    
    # Kiểm tra token
    token = secrets_manager.get_secret('discord_token')
    if not token:
        logger.error("❌ Không tìm thấy Discord Token!")
        secrets_manager.prompt_for_token()
    
    # Lấy thông tin
    web_key = secrets_manager.get_web_key()
    host = config_manager.get('api_host', '0.0.0.0')
    port = config_manager.get('api_port', 5000)
    
    # Hiển thị thông tin
    print("\n" + "="*60)
    print("   ✅ HỆ THỐNG ĐÃ SẴN SÀNG")
    print("="*60)
    print(f"🌐 Web Admin: http://{host}:{port}")
    print(f"🔑 Key truy cập: {web_key}")
    print(f"📌 Bot Discord: Đang chạy...")
    print("="*60)
    print("🛑 Nhấn Ctrl+C để dừng")
    print("="*60 + "\n")
    
    # Chạy Web Server trong thread riêng
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    
    # Chạy Bot trong thread chính
    try:
        run_bot()
    except KeyboardInterrupt:
        logger.info("\n🛑 Đã dừng hệ thống!")
        sys.exit(0)

if __name__ == "__main__":
    main()
