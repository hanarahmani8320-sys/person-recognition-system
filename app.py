import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
from datetime import datetime
import time

# استفاده از مدل‌ها و پایگاه داده
from database import Database
from models import YOLODetector, FaceRecognizer, ImageProcessor
from config import *

# تنظیمات صفحه
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# استایل‌های CSS سفارشی
st.markdown("""
<style>
    :root {
        --primary-color: #1f77e8;
        --success-color: #00D084;
        --danger-color: #FF6B6B;
        --warning-color: #FFB81C;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    h1, h2, h3 {
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .info-box {
        background: rgba(255,255,255,0.1);
        border-left: 4px solid #00D084;
        padding: 15px;
        border-radius: 8px;
        backdrop-filter: blur(10px);
    }
    
    .warning-box {
        background: rgba(255,107,107,0.2);
        border-left: 4px solid #FF6B6B;
        padding: 15px;
        border-radius: 8px;
        backdrop-filter: blur(10px);
    }
    
    .success-box {
        background: rgba(0,208,132,0.2);
        border-left: 4px solid #00D084;
        padding: 15px;
        border-radius: 8px;
        backdrop-filter: blur(10px);
    }
    
    .user-card {
        background: rgba(255,255,255,0.95);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        color: #333;
    }
    
    .emotion-badge {
        display: inline-block;
        padding: 8px 16px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        font-weight: bold;
        margin: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'detector' not in st.session_state:
    st.session_state.detector = YOLODetector()
if 'recognizer' not in st.session_state:
    st.session_state.recognizer = FaceRecognizer()
if 'processor' not in st.session_state:
    st.session_state.processor = ImageProcessor()
if 'db' not in st.session_state:
    st.session_state.db = Database()

# تنظیمات Sidebar
st.sidebar.markdown("# 🎛️ منو")

page = st.sidebar.radio(
    "صفحه را انتخاب کنید:",
    ["🏠 صفحه اصلی", "🔍 تشخیص فرد", "👤 ثبت کاربر جدید", "📊 لاگ دسترسی‌ها", "⚙️ تنظیمات"],
    key="page_selector"
)

# صفحه اصلی
if page == "🏠 صفحه اصلی":
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("# 🔐 سیستم تشخیص و شناسایی افراد")
        st.markdown("""
        ### خوش آمدید!
        
        این سیستم از فناوری‌های پیشرفته هوش مصنوعی استفاده می‌کند:
        
        ✅ **تشخیص فرد** با استفاده از YOLOv8  
        ✅ **تشخیص چهره** با الگوریتم‌های پیشرفته  
        ✅ **تشخیص احساسات** با Deep Learning  
        ✅ **پایگاه داده امن** برای ذخیره اطلاعات  
        """)
    
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3556/3556098.png", width=200)
    
    st.markdown("---")
    
    # آمار
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        users = st.session_state.db.get_all_users()
        st.metric("👥 کاربران ثبت‌شده", len(users))
    
    with col2:
        logs = st.session_state.db.get_access_logs(1)
        st.metric("📋 دسترسی امروز", len(logs))
    
    with col3:
        st.metric("🟢 وضعیت سیستم", "فعال")
    
    with col4:
        st.metric("⚡ سرعت", "بسیار خوب")
    
    st.markdown("---")
    st.markdown("""
    ### 🚀 شروع کنید:
    1. **ثبت کاربر جدید**: برای اضافه کردن شخص جدید
    2. **تشخیص فرد**: برای شناسایی و دسترسی
    3. **مشاهده لاگ**: برای بررسی تاریخچه دسترسی‌ها
    """)

# صفحه تشخیص فرد
elif page == "🔍 تشخیص فرد":
    st.markdown("# 🔍 تشخیص و شناسایی فرد")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📸 بارگذاری تصویر")
        uploaded_file = st.file_uploader(
            "عکس را بارگذاری کنید:",
            type=['jpg', 'jpeg', 'png', 'bmp'],
            key="detection_upload"
        )
    
    with col2:
        st.subheader("⚙️ تنظیمات")
        confidence = st.slider("حداقل اطمینان", 0.0, 1.0, CONFIDENCE_THRESHOLD)
        detect_emotion = st.checkbox("تشخیص احساسات", value=True)
    
    if uploaded_file is not None:
        # بارگذاری تصویر
        image = Image.open(uploaded_file)
        image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # تشخیص افراد
        with st.spinner("🔄 در حال تشخیص..."):
            persons = st.session_state.detector.detect_persons(image_np, conf=confidence)
            
            if len(persons) > 0:
                st.success(f"✅ {len(persons)} نفر شناسایی شد!")
                
                # رسم جعبه‌ها
                result_image = image_np.copy()
                
                for i, person in enumerate(persons):
                    bbox = person['bbox']
                    result_image = st.session_state.processor.draw_box(
                        result_image,
                        bbox,
                        f"Person {i+1}",
                        color=(0, 255, 0)
                    )
                    
                    # برش چهره
                    face = st.session_state.processor.crop_face(image_np, bbox)
                    
                    # تشخیص احساسات
                    if detect_emotion and face.shape[0] > 0 and face.shape[1] > 0:
                        emotion_result = st.session_state.recognizer.detect_emotion(face)
                        
                        if emotion_result:
                            emotion_text = emotion_result['emotion']
                            result_image = st.session_state.processor.add_watermark(
                                result_image,
                                emotion_text,
                                position=(bbox[0], bbox[1]-30),
                                color=(0, 255, 0)
                            )
                
                # نمایش نتیجه
                st.image(cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB))
                
                # سعی برای تطابق با کاربران
                st.markdown("---")
                st.subheader("🔎 نتایج تطابق")
                
                users = st.session_state.db.get_all_users()
                
                if len(users) > 0:
                    for i, person in enumerate(persons):
                        st.markdown(f"### 👤 فرد {i+1}")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        # نمایش احساسات
                        bbox = person['bbox']
                        face = st.session_state.processor.crop_face(image_np, bbox)
                        
                        if detect_emotion and face.shape[0] > 0 and face.shape[1] > 0:
                            emotion_result = st.session_state.recognizer.detect_emotion(face)
                            
                            if emotion_result:
                                with col1:
                                    st.metric("😊 احساس", emotion_result['emotion'])
                                with col2:
                                    st.metric("💯 اطمینان", f"{emotion_result['confidence']:.1%}")
                        
                        # جستجو در کاربران
                        st.write("**کاربران ممکن:**")
                        for user in users[:3]:  # نمایش 3 مورد برتر
                            with st.container():
                                col1, col2, col3 = st.columns([1, 2, 1])
                                
                                with col1:
                                    if os.path.exists(user['image_path']):
                                        st.image(user['image_path'], width=80)
                                
                                with col2:
                                    st.markdown(f"""
                                    **نام:** {user['name']} {user['family_name']}  
                                    **سن:** {user['age']} سال  
                                    **شغل:** {user['job']}  
                                    **شماره تماس:** {user['phone']}
                                    """)
                                
                                with col3:
                                    if st.button(f"✅ تایید {user['name']}", key=f"confirm_{i}_{user['id']}"):
                                        # ثبت دسترسی
                                        emotion_text = ""
                                        if detect_emotion and face.shape[0] > 0 and face.shape[1] > 0:
                                            emotion_result = st.session_state.recognizer.detect_emotion(face)
                                            emotion_text = emotion_result['dominant_emotion'] if emotion_result else ""
                                        
                                        st.session_state.db.log_access(
                                            user['id'],
                                            "✅ مجاز",
                                            emotion_text,
                                            uploaded_file.name,
                                            person['confidence']
                                        )
                                        st.success(f"✅ دسترسی {user['name']} ثبت شد")
                        
                        st.markdown("---")
                else:
                    st.warning("⚠️ هیچ کاربری ثبت نشده است. ابتدا کاربران را ثبت کنید.")
            else:
                st.warning("⚠️ هیچ فردی در تصویر تشخیص داده نشد!")


# صفحه ثبت کاربر جدید
elif page == "👤 ثبت کاربر جدید":
    st.markdown("# 👤 ثبت کاربر جدید")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📸 تصویر کاربر")
        user_image = st.file_uploader(
            "عکس پروفایل را بارگذاری کنید:",
            type=['jpg', 'jpeg', 'png'],
            key="user_image_upload"
        )
        
        if user_image is not None:
            image = Image.open(user_image)
            st.image(image, use_column_width=True)
    
    with col2:
        st.subheader("📝 اطلاعات کاربر")
        
        name = st.text_input("نام:", placeholder="مثال: علی")
        family_name = st.text_input("نام خانوادگی:", placeholder="مثال: رحمانی")
        age = st.number_input("سن:", min_value=1, max_value=120, value=25)
        job = st.text_input("شغل:", placeholder="مثال: مهندس")
        phone = st.text_input("شماره تماس:", placeholder="09XXXXXXXXX")
        email = st.text_input("ایمیل:", placeholder="example@gmail.com")
    
    st.markdown("---")
    
    if st.button("✅ ثبت کاربر", use_container_width=True, key="submit_user"):
        if not all([name, family_name, job, phone, email, user_image]):
            st.error("❌ لطفاً تمام فیلدها را پر کنید!")
        else:
            # ذخیره تصویر
            image_path = f"{FACES_PATH}/{name.strip()}.jpg"
            image.save(image_path)
            
            # اضافه کردن به پایگاه داده
            user_id, success, message = st.session_state.db.add_user(
                name.strip(),
                family_name.strip(),
                age,
                job.strip(),
                phone.strip(),
                email.strip(),
                image_path
            )
            
            if success:
                st.success(f"✅ {message}")
                st.balloons()
                time.sleep(2)
                st.rerun()
            else:
                st.error(f"❌ {message}")


# صفحة لاگ دسترسی‌ها
elif page == "📊 لاگ دسترسی‌ها":
    st.markdown("# 📊 لاگ دسترسی‌ها")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        days = st.selectbox("نمایش آخرین:", [1, 7, 30], format_func=lambda x: f"{x} روز")
    
    with col2:
        filter_status = st.selectbox("فیلتر وضعیت:", ["همه", "✅ مجاز", "❌ غیرمجاز"])
    
    with col3:
        st.metric("لاگ‌های کل", len(st.session_state.db.get_access_logs(days)))
    
    st.markdown("---")
    
    logs = st.session_state.db.get_access_logs(days)
    
    if logs:
        # فیلتر کردن
        if filter_status != "همه":
            logs = [log for log in logs if log['status'] == filter_status]
        
        # نمایش به صورت جدول
        for log in logs:
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                if log['user_id']:
                    user = st.session_state.db.get_user_by_name(
                        [u['name'] for u in st.session_state.db.get_all_users() if u['id'] == log['user_id']][0]
                    )
                    st.write(f"👤 {user['name']} {user['family_name']}")
                else:
                    st.write("👤 مجهول")
            
            with col2:
                status_emoji = "✅" if "مجاز" in log['status'] else "❌"
                st.write(f"{status_emoji} {log['status']}")
            
            with col3:
                if log['emotion']:
                    st.write(f"{EMOTIONS.get(log['emotion'], log['emotion'])}")
            
            with col4:
                st.write(f"💯 {log['confidence']:.1%}")
            
            with col5:
                st.write(f"🕐 {log['timestamp']}")
            
            st.divider()
    else:
        st.info("ℹ️ هیچ لاگی برای دوره‌ی انتخاب‌شده وجود ندارد.")


# صفحة تنظیمات
elif page == "⚙️ تنظیمات":
    st.markdown("# ⚙️ تنظیمات سیستم")
    
    tab1, tab2, tab3 = st.tabs(["👥 مدیریت کاربران", "🔧 تنظیمات فنی", "ℹ️ درباره"])
    
    with tab1:
        st.subheader("👥 لیست کاربران")
        
        users = st.session_state.db.get_all_users()
        
        if users:
            for user in users:
                with st.container():
                    col1, col2, col3 = st.columns([1, 3, 1])
                    
                    with col1:
                        if os.path.exists(user['image_path']):
                            st.image(user['image_path'], width=80)
                    
                    with col2:
                        st.markdown(f"""
                        **{user['name']} {user['family_name']}**  
                        🎂 سن: {user['age']} | 💼 شغل: {user['job']}  
                        📞 {user['phone']} | 📧 {user['email']}
                        """)
                    
                    with col3:
                        if st.button("🗑️ حذف", key=f"delete_{user['id']}"):
                            success, message = st.session_state.db.delete_user(user['id'])
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    
                    st.divider()
        else:
            st.info("ℹ️ هیچ کاربری ثبت نشده است.")
    
    with tab2:
        st.subheader("🔧 تنظیمات فنی")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            📁 مسیر پایگاه داده: {DB_PATH}  
            📁 مسیر مدل‌ها: {MODELS_PATH}  
            📁 مسیر تصاویر: {FACES_PATH}  
            """)
        
        with col2:
            st.warning(f"""
            ⚙️ حداقل اطمینان: {CONFIDENCE_THRESHOLD}  
            📊 حد مقایسه چهره: {FACE_RECOGNITION_THRESHOLD}  
            """)
    
    with tab3:
        st.markdown("""
        # درباره این سیستم
        
        **سیستم تشخیص و شناسایی افراد**
        
        فناوری‌های استفاده‌شده:
        - 🤖 YOLOv8 برای تشخیص افراد
        - 👁️ DeepFace برای تشخیص احساسات
        - 💾 SQLite برای مدیریت داده‌ها
        - 🎨 Streamlit برای رابط کاربری
        
        **نسخه:** 1.0.0  
        **توسعه‌دهنده:** تیم توسعه  
        **آخرین بروزرسانی:** 2024
        """)

# فوتر
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: white; padding: 20px;'>
<p>🔐 سیستم تشخیص و شناسایی افراد | طراحی و توسعه‌یافته با ❤️</p>
<p>© 2024 | تمام حقوق محفوظ است</p>
</div>
""", unsafe_allow_html=True)
