import cv2
import numpy as np
from ultralytics import YOLO
from deepface import DeepFace
from config import *
import os

class YOLODetector:
    """کلاس برای تشخیص اشیاء با YOLO"""
    
    def __init__(self, model_path=YOLO_PERSON_MODEL):
        """بارگذاری مدل YOLO"""
        try:
            if os.path.exists(model_path):
                self.model = YOLO(model_path)
            else:
                print(f"مدل در {model_path} پیدا نشد، مدل پیش‌فرض بارگذاری می‌شود...")
                self.model = YOLO('yolov8n.pt')
        except Exception as e:
            print(f"خطا در بارگذاری مدل: {e}")
            self.model = None
    
    def detect_persons(self, image, conf=CONFIDENCE_THRESHOLD):
        """تشخیص افراد در تصویر"""
        if self.model is None:
            return []
        
        results = self.model(image, conf=conf)
        detections = []
        
        for r in results:
            for box in r.boxes:
                if int(box.cls) == 0:  # کلاس شخص
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    confidence = float(box.conf[0])
                    detections.append({
                        'bbox': (x1, y1, x2, y2),
                        'confidence': confidence
                    })
        
        return detections
    
    def detect_license_plates(self, image, model_path=LICENSE_PLATE_MODEL):
        """تشخیص پلاک خودرو"""
        if not os.path.exists(model_path):
            return []
        
        try:
            model = YOLO(model_path)
            results = model(image)
            detections = []
            
            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    confidence = float(box.conf[0])
                    detections.append({
                        'bbox': (x1, y1, x2, y2),
                        'confidence': confidence
                    })
            
            return detections
        except Exception as e:
            print(f"خطا در تشخیص پلاک: {e}")
            return []


class FaceRecognizer:
    """کلاس برای تشخیص چهره و احساسات"""
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def detect_faces(self, image):
        """تشخیص چهره‌ها در تصویر"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        detections = []
        for (x, y, w, h) in faces:
            detections.append({
                'bbox': (x, y, x+w, y+h),
                'area': w * h
            })
        
        return detections
    
    def detect_emotion(self, image):
        """تشخیص احساسات در تصویر"""
        try:
            # تجزیه تصویر
            result = DeepFace.analyze(
                image,
                actions=['emotion'],
                enforce_detection=False
            )
            
            if isinstance(result, list) and len(result) > 0:
                emotions = result[0]['emotion']
                dominant_emotion = result[0]['dominant_emotion']
                
                # تبدیل به فارسی
                emotion_fa = EMOTIONS.get(dominant_emotion, dominant_emotion)
                
                return {
                    'emotion': emotion_fa,
                    'dominant_emotion': dominant_emotion,
                    'scores': emotions,
                    'confidence': max(emotions.values()) / 100
                }
            return None
        except Exception as e:
            print(f"خطا در تشخیص احساسات: {e}")
            return None
    
    def compare_faces(self, face1, face2):
        """مقایسه دو چهره"""
        try:
            result = DeepFace.verify(
                face1,
                face2,
                model_name='Facenet',
                enforce_detection=False
            )
            
            return {
                'verified': result['verified'],
                'distance': result['distance'],
                'threshold': result['threshold']
            }
        except Exception as e:
            print(f"خطا در مقایسه چهره: {e}")
            return {'verified': False, 'distance': 1.0}


class ImageProcessor:
    """کلاس برای پردازش تصاویر"""
    
    @staticmethod
    def draw_box(image, bbox, label, color=(0, 255, 0), thickness=2):
        """رسم جعبه‌ای دور شناسایی‌ها"""
        x1, y1, x2, y2 = bbox
        cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
        
        # رسم متن
        cv2.putText(
            image,
            label,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            color,
            2
        )
        
        return image
    
    @staticmethod
    def crop_face(image, bbox):
        """برش چهره از تصویر"""
        x1, y1, x2, y2 = bbox
        return image[y1:y2, x1:x2]
    
    @staticmethod
    def resize_image(image, width=640):
        """تغییر سایز تصویر"""
        h, w = image.shape[:2]
        ratio = width / w
        new_height = int(h * ratio)
        
        return cv2.resize(image, (width, new_height))
    
    @staticmethod
    def add_watermark(image, text, position=(10, 30), color=(0, 255, 0)):
        """اضافه کردن واترمارک"""
        cv2.putText(
            image,
            text,
            position,
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2
        )
        return image


# نمونه استفاده
if __name__ == "__main__":
    # تست تشخیص فرد
    detector = YOLODetector()
    recognizer = FaceRecognizer()
    
    print("مدل‌ها آماده هستند!")
