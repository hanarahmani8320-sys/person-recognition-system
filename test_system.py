"""
سیستم تشخیص و شناسایی افراد
Person Recognition System

این اسکریپت برای تست و بررسی مدل‌ها استفاده می‌شود.
"""

from models import YOLODetector, FaceRecognizer, ImageProcessor
from database import Database
import cv2
from config import *

def test_system():
    """تست مدل‌های سیستم"""
    
    print("=" * 50)
    print("🧪 تست سیستم تشخیص و شناسایی افراد")
    print("=" * 50)
    
    # تست پایگاه داده
    print("\n1️⃣ تست پایگاه داده...")
    db = Database()
    
    # اضافه کردن کاربر تست
    user_id, success, msg = db.add_user(
        name="علی",
        family_name="رحمانی",
        age=28,
        job="مهندس",
        phone="09123456789",
        email="ali@example.com",
        image_path="uploads/faces/ali.jpg"
    )
    
    if success:
        print(f"✅ {msg}")
    else:
        print(f"⚠️ {msg}")
    
    # دریافت کاربران
    users = db.get_all_users()
    print(f"✅ تعداد کاربران: {len(users)}")
    
    # تست مدل‌های AI
    print("\n2️⃣ تست مدل‌های AI...")
    try:
        detector = YOLODetector()
        print("✅ مدل YOLO بارگذاری شد")
    except Exception as e:
        print(f"❌ خطا در بارگذاری YOLO: {e}")
    
    try:
        recognizer = FaceRecognizer()
        print("✅ مدل Face Recognizer بارگذاری شد")
    except Exception as e:
        print(f"❌ خطا در بارگذاری Face Recognizer: {e}")
    
    try:
        processor = ImageProcessor()
        print("✅ Image Processor بارگذاری شد")
    except Exception as e:
        print(f"❌ خطا در بارگذاری Image Processor: {e}")
    
    # تست دایرکتوری‌ها
    print("\n3️⃣ بررسی دایرکتوری‌ها...")
    directories = [UPLOADS_PATH, FACES_PATH, MODELS_PATH]
    
    for dir_path in directories:
        import os
        if os.path.exists(dir_path):
            print(f"✅ {dir_path} وجود دارد")
        else:
            print(f"❌ {dir_path} وجود ندارد")
    
    print("\n" + "=" * 50)
    print("✅ تمام تست‌ها اتمام یافت!")
    print("=" * 50)

if __name__ == "__main__":
    test_system()
