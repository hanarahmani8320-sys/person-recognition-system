# تنظیمات پروژه
import os

# مسیرهای فایل‌ها
DB_PATH = "data/users.db"
MODELS_PATH = "models"
UPLOADS_PATH = "uploads"
FACES_PATH = "uploads/faces"

# مدل‌های YOLO
YOLO_PERSON_MODEL = "models/yolov8n.pt"  # یا yolov8s.pt
LICENSE_PLATE_MODEL = "models/license_plate.pt"
BEST_MODEL = "models/best.pt"

# تنظیمات تشخیص چهره
CONFIDENCE_THRESHOLD = 0.5
FACE_RECOGNITION_THRESHOLD = 0.6

# تنظیمات Streamlit
PAGE_TITLE = "🔐 سیستم تشخیص و شناسایی افراد"
PAGE_ICON = "👤"

# دسته‌بندی احساسات
EMOTIONS = {
    "happy": "😊 خوشحال",
    "sad": "😔 غمگین",
    "angry": "😠 ناراحت",
    "neutral": "😐 جدی",
    "surprised": "😮 متفاجئ",
    "disgust": "🤢 انزجار",
    "fear": "😨 ترسیده"
}

# رنگ‌های UI
COLORS = {
    "authorized": "#00D084",  # سبز
    "unauthorized": "#FF6B6B",  # قرمز
    "processing": "#4ECDC4",  # فیروزه‌ای
    "info": "#45B7D1"  # آبی
}

# ایجاد دایرکتوری‌های لازم
os.makedirs(UPLOADS_PATH, exist_ok=True)
os.makedirs(FACES_PATH, exist_ok=True)
os.makedirs(MODELS_PATH, exist_ok=True)
os.makedirs("data", exist_ok=True)
