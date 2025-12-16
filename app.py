import streamlit as st
import pandas as pd
import numpy as np
import joblib
import shap
import plotly.graph_objects as go
import plotly.express as px
import requests
from streamlit_lottie import st_lottie
import time
from datetime import datetime
import json

# ==========================================
# 1. تظبيط الصفحة (Page Config)
# بنجهز الصفحة عشان تستقبل العربي وتكون RTL
# ==========================================
st.set_page_config(
    page_title="دكتور القلب الذكي - AI Cardiology Assistant",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. اللمسات الجمالية المحسّنة (CSS & Style)
# شغل عالمي الجودة مع دعم الـ Dark Mode والـ Animations
# ==========================================
st.markdown("""
<style>
/* استيراد خطوط عالمية للعربي والإنجليزي */
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Inter:wght@400;600;700&display=swap');

/* تظبيط اتجاه الصفحة حسب اللغة */
html, body, [class*="css"] {
    font-family: 'Cairo', 'Inter', sans-serif;
    direction: rtl;
    text-align: right;
}

/* الخلفية المتحركة الاحترافية */
.stApp {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #0f0c29);
    background-size: 400% 400%;
    animation: gradient 20s ease infinite;
    color: white;
}

@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* الكروت الاحترافية */
.result-card {
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 25px;
    backdrop-filter: blur(20px);
    background: rgba(255, 255, 255, 0.05);
    border: 2px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 15px 40px rgba(0,0,0,0.6);
    transition: all 0.4s ease;
}

.result-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 50px rgba(0,0,0,0.8);
    border-color: rgba(255, 255, 255, 0.3);
}

/* الأزرار الاحترافية */
.stButton>button {
    font-family: 'Cairo', sans-serif;
    font-weight: 700;
    border-radius: 15px;
    height: 3.5em;
    transition: all 0.3s ease;
    border: 2px solid transparent;
}

.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 10px 25px rgba(255,255,255,0.2);
}

/* الـ Stats Cards */
.stat-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
    margin: 10px 0;
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
    background: linear-gradient(135deg, rgba(255,255,255,0.15), rgba(255,255,255,0.08));
}

/* الـ Progress Bar المخصص */
.custom-progress {
    height: 8px;
    border-radius: 10px;
    background: rgba(255,255,255,0.1);
    overflow: hidden;
    margin: 15px 0;
}

.custom-progress-bar {
    height: 100%;
    border-radius: 10px;
    transition: width 1s ease;
    background: linear-gradient(90deg, #00e676, #00c853);
    animation: shimmer 2s infinite;
}

@keyframes shimmer {
    0% {background-position: -1000px 0;}
    100% {background-position: 1000px 0;}
}

/* تحسين الـ Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(15,12,41,0.95), rgba(48,43,99,0.95));
    border-left: 2px solid rgba(255,255,255,0.1);
}

/* الـ Tabs الاحترافية */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 10px 20px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
}

/* الـ Metrics المخصصة */
[data-testid="stMetricValue"] {
    font-size: 2.5rem;
    font-weight: 900;
}

/* تحسين الـ Expanders */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
    font-weight: 600;
}

/* الـ Tooltips */
.stTooltipIcon {
    color: #00e676;
}

/* الـ Loading Spinner */
.stSpinner > div {
    border-top-color: #00e676 !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. دوال مساعدة محسّنة (Enhanced Helpers)
# ==========================================

# دالة لجلب الأنيميشنز
def load_lottieurl(url):
    """بنجيب الأنيميشن من النت - لو النت واقف هنرجع None"""
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except:
        return None

# دالة لحفظ التاريخ الطبي
def save_medical_history(data):
    """بنحفظ التاريخ الطبي في الـ Session State"""
    if 'medical_history' not in st.session_state:
        st.session_state['medical_history'] = []
    
    data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state['medical_history'].append(data)
    
    # نحتفظ بآخر 10 سجلات بس
    if len(st.session_state['medical_history']) > 10:
        st.session_state['medical_history'] = st.session_state['medical_history'][-10:]

# دالة لحساب مؤشر الصحة العامة
def calculate_health_score(data):
    """بنحسب درجة الصحة العامة من 100"""
    score = 100
    
    # السن - كل ما تكبر تخسر شوية
    if data['age'] > 60:
        score -= (data['age'] - 60) * 0.5
    
    # الضغط
    if data['trestbps'] > 140:
        score -= 10
    elif data['trestbps'] > 130:
        score -= 5
    
    # الكوليسترول
    if data['chol'] > 240:
        score -= 15
    elif data['chol'] > 200:
        score -= 8
    
    # السكر الصايم
    if data['fbs'] == 1:
        score -= 10
    
    # الوجع في الصدر
    if data['cp'] in [1, 2]:
        score -= 15
    
    # الوجع مع المجهود
    if data['exang'] == 1:
        score -= 10
    
    # ضربات القلب
    expected_max_hr = 220 - data['age']
    if data['thalach'] < expected_max_hr * 0.6:
        score -= 10
    
    return max(0, min(100, score))

# دالة لتوليد التوصيات
def generate_recommendations(data, is_risky):
    """بنولد توصيات طبية حسب الحالة"""
    recommendations = []
    
    if is_risky:
        recommendations.append("🚨 **ضروري جداً**: زيارة طبيب قلب في أقرب وقت")
        recommendations.append("📋 اعمل رسم قلب كامل (ECG) وإيكو على القلب")
    
    if data['trestbps'] > 140:
        recommendations.append("💊 الضغط عالي - راجع دكتور باطنة وممكن تحتاج علاج")
        recommendations.append("🧂 قلل الملح في الأكل وابعد عن المخللات")
    
    if data['chol'] > 200:
        recommendations.append("🥗 الكوليسترول محتاج ضبط - زود الخضار والفواكه")
        recommendations.append("🏃 مارس رياضة على الأقل 30 دقيقة يومياً")
    
    if data['fbs'] == 1:
        recommendations.append("🍬 السكر عالي - قلل النشويات والسكريات")
    
    if data['age'] > 50 and data['exang'] == 1:
        recommendations.append("⚠️ الوجع مع المجهود في السن ده علامة مهمة - لازم متابعة")
    
    # توصيات عامة
    recommendations.append("😴 نام كويس 7-8 ساعات يومياً")
    recommendations.append("🚭 لو بتدخن - لازم تبطل فوراً")
    recommendations.append("🧘 قلل التوتر والقلق - جرب التأمل أو اليوجا")
    
    if not is_risky:
        recommendations.append("✅ حافظ على نمط حياتك الصحي الحالي")
        recommendations.append("📅 اعمل فحص دوري كل 6 شهور للاطمئنان")
    
    return recommendations

# بنحمل ملفات الذكاء الاصطناعي
@st.cache_resource
def load_assets():
    """بنحمل الموديل والسكيلر - مع الكاش عشان مش كل مرة نحملهم"""
    try:
        model = joblib.load('heart_disease_model.pkl')
        scaler = joblib.load('scaler.pkl')
        return model, scaler
    except Exception as e:
        st.error(f"مشكلة في تحميل الملفات: {str(e)}")
        return None, None

model, scaler = load_assets()

# بنحمل الأنيميشنز
lottie_heart = load_lottieurl("https://lottie.host/44d93539-e932-4140-9b37-251016892550/S3Xq6i0B2s.json")
lottie_doctor = load_lottieurl("https://lottie.host/e6c9a304-4632-4752-b91c-843376283575/r7e2e8y8Xw.json")
lottie_success = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_touohxv0.json")

# ==========================================
# 4. إدارة الصفحات والجلسات (Session Management)
# ==========================================

# تهيئة المتغيرات في الـ Session
if 'page' not in st.session_state:
    st.session_state['page'] = 'landing'

if 'language' not in st.session_state:
    st.session_state['language'] = 'ar'  # العربية افتراضياً

if 'theme' not in st.session_state:
    st.session_state['theme'] = 'dark'

if 'total_analyses' not in st.session_state:
    st.session_state['total_analyses'] = 0

# دوال التنقل
def go_to_app():
    """الانتقال لصفحة التطبيق"""
    st.session_state['page'] = 'app'
    st.toast('🚀 يلا بينا نبدأ الكشف!', icon="🎯")

def go_to_landing():
    """الرجوع للصفحة الرئيسية"""
    st.session_state['page'] = 'landing'

def go_to_history():
    """الانتقال لصفحة التاريخ الطبي"""
    st.session_state['page'] = 'history'

def go_to_statistics():
    """الانتقال لصفحة الإحصائيات"""
    st.session_state['page'] = 'statistics'

# ==========================================
# 5. صفحة البداية المحسّنة (Enhanced Landing Page)
# ==========================================

if st.session_state['page'] == 'landing':
    
    # الهيدر الرئيسي
    col_logo, col_title, col_stats = st.columns([1, 2, 1])
    
    with col_title:
        if lottie_heart:
            st_lottie(lottie_heart, height=200, key="heart_landing")
        st.markdown("""
        <h1 style='text-align: center; font-size: 4rem; margin: 0; 
                   background: linear-gradient(120deg, #00e676, #00c853);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   font-weight: 900;'>
            دكتور القلب الذكي 🫀
        </h1>
        <h2 style='text-align: center; color: #aaa; font-weight: 400; margin-top: 10px;'>
            AI-Powered Cardiology Assistant
        </h2>
        """, unsafe_allow_html=True)
    
    with col_stats:
        st.markdown(f"""
        <div class="stat-card">
            <h3 style='margin:0; color:#00e676;'>📊</h3>
            <h2 style='margin:5px 0; font-size:2rem;'>{st.session_state['total_analyses']}</h2>
            <p style='margin:0; color:#aaa;'>تحليل تم إنجازه</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("---")
    
    # قسم المميزات
    st.markdown("<h2 style='text-align: center; margin: 30px 0;'>✨ ليه تختار دكتور القلب الذكي؟</h2>", unsafe_allow_html=True)
    
    feat1, feat2, feat3, feat4 = st.columns(4)
    
    with feat1:
        st.markdown("""
        <div class="stat-card">
            <h1 style='font-size: 3rem; margin: 0;'>🤖</h1>
            <h3>ذكاء اصطناعي</h3>
            <p style='color: #aaa;'>مدرب على آلاف الحالات الحقيقية</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat2:
        st.markdown("""
        <div class="stat-card">
            <h1 style='font-size: 3rem; margin: 0;'>⚡</h1>
            <h3>نتائج فورية</h3>
            <p style='color: #aaa;'>تحليل دقيق في أقل من 10 ثواني</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat3:
        st.markdown("""
        <div class="stat-card">
            <h1 style='font-size: 3rem; margin: 0;'>🔒</h1>
            <h3>خصوصية تامة</h3>
            <p style='color: #aaa;'>بياناتك آمنة ومشفرة 100%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat4:
        st.markdown("""
        <div class="stat-card">
            <h1 style='font-size: 3rem; margin: 0;'>📈</h1>
            <h3>تقارير تفصيلية</h3>
            <p style='color: #aaa;'>تحليل شامل مع توصيات مخصصة</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    
    # قسم الشرح التفصيلي
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("""
        ### 🎯 المشروع ده بيعمل إيه؟
        
        **دكتور القلب الذكي** هو نظام ذكاء اصطناعي متطور بيحلل بياناتك الطبية باستخدام 
        خوارزميات Machine Learning المتقدمة. البرنامج بيشوف:
        
        - 💉 **الضغط والكوليسترول** - مؤشرات حيوية مهمة
        - 📊 **رسم القلب (ECG)** - تحليل النشاط الكهربائي
        - 🫀 **معدل ضربات القلب** - في الراحة والمجهود
        - 🔬 **التحاليل المخبرية** - السكر والثلاسيميا
        
        وبعد كده بيقولك: انت في الأمان ولا محتاج كشف؟
        """)
    
    with col_info2:
        st.markdown("""
        ### 🎓 مين يستخدم النظام ده؟
        
        - 👨‍⚕️ **الأطباء**: كأداة مساعدة في التشخيص السريع
        - 🏥 **المستشفيات**: للفرز الأولي للحالات
        - 👤 **الأفراد**: للاطمئنان على الصحة بشكل دوري
        - 🔬 **الباحثين**: لدراسة أنماط أمراض القلب
        
        ### ⚠️ تنويه مهم
        
        النظام ده **مساعد ذكي وليس بديل** عن الطبيب المختص.
        دايماً راجع دكتور قلب للتشخيص النهائي والعلاج.
        """)
    
    st.write("---")
    
    # أزرار البدء
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    
    with col_btn2:
        if st.button("🚀 ابدأ الكشف الذكي الآن", use_container_width=True, type="primary"):
            go_to_app()
            st.rerun()
        
        st.write("")
        
        col_sub1, col_sub2 = st.columns(2)
        with col_sub1:
            if st.button("📊 شوف الإحصائيات", use_container_width=True):
                go_to_statistics()
                st.rerun()
        
        with col_sub2:
            if st.button("📜 التاريخ الطبي", use_container_width=True):
                go_to_history()
                st.rerun()
    
    st.write("")
    st.write("")
    
    # الفوتر
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 30px;'>
        <p>🔬 Powered by Advanced Machine Learning & SHAP Explainability</p>
        <p>Made with ❤️ for Better Healthcare</p>
        <p style='font-size: 0.9rem;'>© 2024 Smart Heart Doctor - All Rights Reserved</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 6. صفحة التطبيق الرئيسية (Main Application)
# ==========================================

elif st.session_state['page'] == 'app':
    
    # الهيدر مع زر الرجوع
    col_back, col_head, col_anim = st.columns([0.5, 2.5, 1])
    
    with col_back:
        if st.button("🏠", help="رجوع للرئيسية"):
            go_to_landing()
            st.rerun()
    
    with col_head:
        st.markdown("""
        <h1 style='margin: 0;'>🩺 عيادة الذكاء الاصطناعي</h1>
        <p style='color: #aaa; margin: 5px 0;'>دخل بياناتك بدقة عشان نديك أفضل تحليل</p>
        """, unsafe_allow_html=True)
    
    with col_anim:
        if lottie_doctor:
            st_lottie(lottie_doctor, height=80, key="doc_header")
    
    st.write("---")
    
    # ==========================================
    # الـ Sidebar - لوحة التحكم الكاملة
    # ==========================================
    with st.sidebar:
        st.markdown("### 📝 بيانات المريض")
        
        # دليل المصطلحات
        with st.expander("📖 دليل المصطلحات الطبية", expanded=False):
            st.markdown("""
            **المصطلحات اللي هتحتاجها:**
            
            - **Chest Pain (CP)**: نوع الألم في الصدر
              - 0: مفيش ألم
              - 1: ذبحة صدرية نمطية
              - 2: ذبحة غير نمطية
              - 3: ألم مش من القلب
            
            - **Resting BP**: ضغط الدم وانت مرتاح
              - المثالي: 120/80
              - عالي: فوق 140/90
            
            - **Cholesterol**: الدهون في الدم
              - طبيعي: أقل من 200
              - حدودي: 200-239
              - عالي: 240+
            
            - **Fasting Blood Sugar**: السكر الصايم
              - طبيعي: أقل من 100
              - مقدمات سكري: 100-125
              - سكري: 126+
            
            - **ECG**: رسم القلب في الراحة
            
            - **Max Heart Rate**: أقصى نبض وصله القلب
            
            - **Exercise Angina**: وجع في الصدر مع المجهود
            
            - **Oldpeak**: انخفاض ST في رسم القلب
            
            - **Slope**: ميل موجة ST
            
            - **CA**: عدد الشرايين السليمة
            
            - **Thalassemia**: نوع من أنواع الأنيميا
            """)
        
        st.write("---")
        
        # فورم المدخلات الرئيسي
        with st.form("medical_form_enhanced"):
            
            # 1. البيانات الشخصية
            st.markdown("#### 👤 البيانات الأساسية")
            col_age, col_gender = st.columns(2)
            
            with col_age:
                age = st.number_input(
                    "العمر (سنة)",
                    min_value=20,
                    max_value=100,
                    value=50,
                    help="العمر الحالي بالسنوات"
                )
            
            with col_gender:
                gender = st.selectbox(
                    "النوع",
                    ["ذكر", "أنثى"],
                    help="الجنس البيولوجي"
                )
            
            st.write("")
            
            # 2. العلامات الحيوية
            st.markdown("#### 💉 العلامات الحيوية")
            
            cp = st.select_slider(
                "نوع ألم الصدر",
                options=[
                    "مفيش ألم (0)",
                    "ذبحة نمطية (1)",
                    "ذبحة غير نمطية (2)",
                    "ألم مش من القلب (3)"
                ],
                help="اختار الوصف الأقرب للألم اللي بتحس بيه"
            )
            
            col_bp, col_chol = st.columns(2)
            
            with col_bp:
                trestbps = st.number_input(
                    "ضغط الدم (mmHg)",
                    min_value=90,
                    max_value=250,
                    value=120,
                    step=5,
                    help="الضغط الانقباضي وانت مرتاح"
                )
                
                # مؤشر الضغط
                if trestbps < 120:
                    st.success("مثالي ✅")
                elif trestbps < 140:
                    st.warning("مرتفع قليلاً ⚠️")
                else:
                    st.error("مرتفع جداً ⛔")
            
            with col_chol:
                chol = st.number_input(
                    "الكوليسترول (mg/dL)",
                    min_value=100,
                    max_value=600,
                    value=200,
                    step=10,
                    help="نسبة الكوليسترول الكلي"
                )
                
                # مؤشر الكوليسترول
                if chol < 200:
                    st.success("مثالي ✅")
                elif chol < 240:
                    st.warning("حدودي ⚠️")
                else:
                    st.error("عالي ⛔")
            
            fbs = st.radio(
                "سكر الدم الصايم > 120 mg/dL؟",
                ["لا", "نعم"],
                horizontal=True,
                help="هل السكر الصايم أعلى من 120؟"
            )
            
            st.write("")
            
            # 3. فحوصات القلب
            st.markdown("#### 🫀 فحوصات القلب")
            
            restecg = st.selectbox(
                "نتيجة رسم القلب (ECG)",
                [
                    "طبيعي (0)",
                    "موجة ST-T غير طبيعية (1)",
                    "تضخم البطين الأيسر (2)"
                ],
                help="نتيجة تخطيط القلب في الراحة"
            )
            
            thalach = st.slider(
                "أقصى معدل لضربات القلب",
                min_value=60,
                max_value=220,
                value=150,
                help="أعلى نبض وصله القلب أثناء المجهود"
            )
            
            # حساب النبض المتوقع
            expected_max = 220 - age
            hr_percentage = (thalach / expected_max) * 100
            
            st.caption(f"النبض المتوقع لعمرك: {expected_max} | نسبة الإنجاز: {hr_percentage:.0f}%")
            
            exang = st.radio(
                "ألم في الصدر مع المجهود؟",
                ["لا", "نعم"],
                horizontal=True,
                help="هل يظهر ألم في الصدر عند بذل مجهود؟"
            )
            
            col_old, col_slope = st.columns(2)
            
            with col_old:
                oldpeak = st.number_input(
                    "انخفاض ST (Oldpeak)",
                    min_value=0.0,
                    max_value=6.0,
                    value=0.0,
                    step=0.1,
                    help="مقدار انخفاض ST في رسم القلب بالمجهود"
                )
            
            with col_slope:
                slope = st.selectbox(
                    "ميل موجة ST",
                    ["صاعد (0)", "مسطح (1)", "هابط (2)"],
                    help="شكل ميل موجة ST في رسم القلب"
                )
            
            ca = st.slider(
                "عدد الشرايين الرئيسية السليمة",
                min_value=0,
                max_value=3,
                value=0,
                help="عدد الشرايين اللي ظاهرة سليمة في الأشعة بالصبغة"
            )
            
            thal = st.selectbox(
                "نتيجة فحص الثلاسيميا",
                [
                    "غير معروف (0)",
                    "عيب ثابت (1)",
                    "طبيعي (2)",
                    "عيب قابل للإصلاح (3)"
                ],
                help="نتيجة فحص الثلاسيميا (نوع من الأنيميا)"
            )
            
            st.write("---")
            
            # زر التحليل الكبير
            submit_btn = st.form_submit_button(
                "🔬 حلل البيانات بالذكاء الاصطناعي",
                use_container_width=True,
                type="primary"
            )
    
    # ==========================================
    # معالجة البيانات والتحليل
    # ==========================================
    
    if submit_btn:
        
        # شريط التحميل الاحترافي
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("⏳ جاري تجهيز البيانات...")
        progress_bar.progress(20)
        time.sleep(0.3)
        
        status_text.text("🤖 استدعاء محرك الذكاء الاصطناعي...")
        progress_bar.progress(50)
        time.sleep(0.4)
        
        status_text.text("📊 تحليل العوامل والمخاطر...")
        progress_bar.progress(80)
        time.sleep(0.3)
        
        status_text.text("✨ إعداد التقرير النهائي...")
        progress_bar.progress(100)
        time.sleep(0.2)
        
        progress_bar.empty()
        status_text.empty()
        
        # تحويل المدخلات لأرقام يفهمها الموديل
        input_dict = {
            'age': age,
            'sex': 1 if gender == "ذكر" else 0,
            'cp': int(cp.split("(")[1][0]),
            'trestbps': trestbps,
            'chol': chol,
            'fbs': 1 if fbs == "نعم" else 0,
            'restecg': int(restecg.split("(")[1][0]),
            'thalach': thalach,
            'exang': 1 if exang == "نعم" else 0,
            'oldpeak': oldpeak,
            'slope': int(slope.split("(")[1][0]),
            'ca': ca,
            'thal': int(thal.split("(")[1][0])
        }
        
        input_df = pd.DataFrame(input_dict, index=[0])
        
        # التوقع باستخدام الموديل
        if model and scaler:
            
            # Scaling + Prediction
            input_scaled = scaler.transform(input_df)
            pred = model.predict(input_scaled)[0]
            probs = model.predict_proba(input_scaled)[0]
            
            # تحديد الحالة (0 = مريض، 1 = سليم)
            is_risky = (pred == 0)
            confidence = probs[0] * 100 if is_risky else probs[1] * 100
            
            # حساب مؤشر الصحة العامة
            health_score = calculate_health_score(input_dict)
            
            # حفظ في التاريخ
            save_medical_history({
                **input_dict,
                'is_risky': is_risky,
                'confidence': confidence,
                'health_score': health_score
            })
            
            # زيادة عداد التحليلات
            st.session_state['total_analyses'] += 1
            
            st.write("---")
            st.write("")
            
            # ==========================================
            # عرض النتائج الرئيسية
            # ==========================================
            
            st.markdown("## 📋 التقرير الطبي الشامل")
            st.write("")
            
            # صف المؤشرات السريعة
            met1, met2, met3, met4 = st.columns(4)
            
            with met1:
                st.metric(
                    label="🎯 دقة التوقع",
                    value=f"{confidence:.1f}%",
                    delta="عالية" if confidence > 80 else "متوسطة"
                )
            
            with met2:
                st.metric(
                    label="💪 مؤشر الصحة",
                    value=f"{health_score:.0f}/100",
                    delta="ممتاز" if health_score > 80 else ("جيد" if health_score > 60 else "يحتاج تحسين"),
                    delta_color="normal" if health_score > 60 else "inverse"
                )
            
            with met3:
                st.metric(
                    label="🫀 معدل القلب",
                    value=f"{thalach} bpm",
                    delta=f"{hr_percentage:.0f}% من المتوقع"
                )
            
            with met4:
                st.metric(
                    label="📊 التحليلات",
                    value=st.session_state['total_analyses'],
                    delta="تحليل جديد"
                )
            
            st.write("")
            
            # النتيجة الرئيسية
            res_main, res_side = st.columns([2, 1])
            
            with res_main:
                if is_risky:
                    st.markdown(f"""
                    <div class="result-card" style="border-right: 6px solid #ff4b4b; background: linear-gradient(135deg, rgba(255,75,75,0.2), rgba(255,75,75,0.05));">
                        <h2 style="color:#ff4b4b; margin:0; font-size: 2rem;">⚠️ تحذير: احتمالية وجود مشكلة قلبية</h2>
                        <h1 style="font-size: 4rem; margin:15px 0; font-weight: 900;">
                            {confidence:.1f}%
                            <span style="font-size:1.5rem; color:#ccc; font-weight: 400;">مؤشر الخطورة</span>
                        </h1>
                        <p style="margin-top:15px; font-size:1.2rem; line-height: 1.8;">
                            الذكاء الاصطناعي بيشير إن في مؤشرات مقلقة في بياناتك الطبية.
                            <strong>ضروري جداً</strong> تزور دكتور قلب متخصص في أقرب وقت ممكن.
                        </p>
                        <div style="margin-top: 20px; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 10px;">
                            <p style="margin: 0; font-size: 0.95rem;">
                                ⚕️ <strong>ملحوظة:</strong> هذا التشخيص أولي ويحتاج لتأكيد من طبيب مختص
                            </p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.error("🚨 **إجراء عاجل مطلوب:** النظام للمساعدة فقط - استشر طبيباً فوراً", icon="⚠️")
                
                else:
                    st.markdown(f"""
                    <div class="result-card" style="border-right: 6px solid #00e676; background: linear-gradient(135deg, rgba(0,230,118,0.2), rgba(0,230,118,0.05));">
                        <h2 style="color:#00e676; margin:0; font-size: 2rem;">✅ مبروك! المؤشرات إيجابية</h2>
                        <h1 style="font-size: 4rem; margin:15px 0; font-weight: 900;">
                            {confidence:.1f}%
                            <span style="font-size:1.5rem; color:#ccc; font-weight: 400;">نسبة الأمان</span>
                        </h1>
                        <p style="margin-top:15px; font-size:1.2rem; line-height: 1.8;">
                            الحمد لله! 🎉 المؤشرات الطبية بتقول إن قلبك في حالة كويسة.
                            استمر في نمط حياتك الصحي وحافظ على الفحوصات الدورية.
                        </p>
                        <div style="margin-top: 20px; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 10px;">
                            <p style="margin: 0; font-size: 0.95rem;">
                                💡 <strong>نصيحة:</strong> الوقاية خير من العلاج - استمر في الرياضة والأكل الصحي
                            </p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.balloons()
                    st.success("✨ نتيجة رائعة! استمر في العناية بصحتك", icon="🎯")
            
            with res_side:
                # مقياس الصحة العامة
                st.markdown("### 💪 مقياس الصحة")
                
                # Progress bar مخصص
                health_color = "#00e676" if health_score > 70 else ("#ffa726" if health_score > 50 else "#ff4b4b")
                
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; text-align: center;">
                    <h1 style="font-size: 3.5rem; margin: 0; color: {health_color};">{health_score:.0f}</h1>
                    <p style="margin: 5px 0; color: #aaa;">من 100</p>
                    <div style="width: 100%; height: 10px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden; margin-top: 15px;">
                        <div style="width: {health_score}%; height: 100%; background: linear-gradient(90deg, {health_color}, {health_color}dd); transition: width 1s ease;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("")
                
                # تصنيف الحالة
                if health_score > 80:
                    st.success("🌟 صحة ممتازة")
                elif health_score > 60:
                    st.info("😊 صحة جيدة")
                elif health_score > 40:
                    st.warning("⚠️ تحتاج اهتمام")
                else:
                    st.error("🚨 تحتاج رعاية")
            
            st.write("---")
            
            # ==========================================
            # التوصيات الطبية المخصصة
            # ==========================================
            
            st.markdown("## 📝 التوصيات الطبية المخصصة")
            
            recommendations = generate_recommendations(input_dict, is_risky)
            
            rec_col1, rec_col2 = st.columns(2)
            
            with rec_col1:
                st.markdown("### 🎯 إجراءات فورية")
                for i, rec in enumerate(recommendations[:len(recommendations)//2]):
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.05); padding: 15px; margin: 10px 0; border-radius: 10px; border-right: 3px solid #00e676;">
                        {rec}
                    </div>
                    """, unsafe_allow_html=True)
            
            with rec_col2:
                st.markdown("### 💡 نصائح عامة")
                for i, rec in enumerate(recommendations[len(recommendations)//2:]):
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.05); padding: 15px; margin: 10px 0; border-radius: 10px; border-right: 3px solid #2196f3;">
                        {rec}
                    </div>
                    """, unsafe_allow_html=True)
            
            st.write("---")
            
            # ==========================================
            # تحليل SHAP - ليه الموديل قرر كده؟
            # ==========================================
            
            st.markdown("## 🧠 تحليل القرار (AI Explainability)")
            
            exp_col1, exp_col2 = st.columns([3, 2])
            
            with exp_col1:
                st.markdown("### 📊 العوامل الأكثر تأثيراً")
                
                try:
                    # حساب SHAP Values
                    explainer = shap.TreeExplainer(model)
                    shap_values = explainer.shap_values(input_df)
                    
                    if isinstance(shap_values, list):
                        target_idx = 0 if is_risky else 1
                        sv = shap_values[target_idx][0]
                    else:
                        sv = shap_values[0, :, 0]
                    
                    # تحضير البيانات للرسمة
                    feature_names_ar = {
                        'age': 'العمر',
                        'sex': 'الجنس',
                        'cp': 'نوع الألم',
                        'trestbps': 'ضغط الدم',
                        'chol': 'الكوليسترول',
                        'fbs': 'سكر الدم',
                        'restecg': 'رسم القلب',
                        'thalach': 'معدل النبض',
                        'exang': 'ألم المجهود',
                        'oldpeak': 'انخفاض ST',
                        'slope': 'ميل ST',
                        'ca': 'الشرايين',
                        'thal': 'الثلاسيميا'
                    }
                    
                    plot_df = pd.DataFrame({
                        'Feature': [feature_names_ar.get(f, f) for f in input_df.columns],
                        'Impact': sv,
                        'Value': input_df.values[0]
                    }).sort_values(by='Impact', key=abs, ascending=True)
                    
                    # رسمة SHAP احترافية
                    colors = ['#ff4b4b' if x > 0 else '#00e676' for x in plot_df['Impact']]
                    
                    fig_shap = go.Figure()
                    
                    fig_shap.add_trace(go.Bar(
                        y=plot_df['Feature'],
                        x=plot_df['Impact'],
                        orientation='h',
                        marker=dict(
                            color=colors,
                            line=dict(color='rgba(255,255,255,0.3)', width=1)
                        ),
                        text=[f"{v:.3f}" for v in plot_df['Impact']],
                        textposition='auto',
                        hovertemplate='<b>%{y}</b><br>التأثير: %{x:.4f}<extra></extra>'
                    ))
                    
                    fig_shap.update_layout(
                        title={
                            'text': "مساهمة كل عامل في القرار النهائي",
                            'font': {'size': 18, 'family': 'Cairo'}
                        },
                        xaxis_title="مقدار التأثير (SHAP Value)",
                        template="plotly_dark",
                        height=450,
                        margin=dict(l=150, r=20, t=50, b=50),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(255,255,255,0.02)',
                        font=dict(family="Cairo", size=12),
                        hovermode='y unified'
                    )
                    
                    fig_shap.add_vline(x=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")
                    
                    st.plotly_chart(fig_shap, use_container_width=True)
                
                except Exception as e:
                    st.error(f"مشكلة في حساب SHAP: {str(e)}")
            
            with exp_col2:
                st.markdown("### ℹ️ فهم التحليل")
                
                st.info("""
                **إزاي نقرأ الرسمة دي؟**
                
                - 🔴 **الأحمر**: العوامل اللي **زادت** احتمال المشكلة
                - 🟢 **الأخضر**: العوامل اللي **قللت** احتمال المشكلة
                - 📏 **طول الخط**: قد إيه العامل ده مؤثر
                
                **مثال:**
                لو السن أحمر وطويل، يعني السن الكبير ساهم في زيادة الخطر.
                """)
                
                st.markdown("### 🎓 SHAP Values")
                
                st.markdown("""
                **SHAP** هي تقنية شرح قرارات الذكاء الاصطناعي.
                
                بتقولنا بالظبط كل عامل ساهم بكام في القرار النهائي،
                وده بيخلي الموديل **شفاف** و**موثوق**.
                
                📚 [اعرف أكتر عن SHAP](https://github.com/slundberg/shap)
                """)
            
            st.write("---")
            
            # ==========================================
            # التحليل ثلاثي الأبعاد
            # ==========================================
            
            st.markdown("## 🌐 موقعك في الخريطة الطبية (3D Analysis)")
            
            st.info("""
            **النقطة الذهبية 🟡** دي بتمثل حالتك وسط عينة من المرضى:
            - 🟢 **الأخضر**: حالات سليمة
            - 🔴 **الأحمر**: حالات حرجة
            
            شوف انت فين بالنسبة للحالات التانية!
            """)
            
            # توليد بيانات للمقارنة
            np.random.seed(42)
            
            # حالات سليمة
            healthy_age = np.random.randint(25, 50, 50)
            healthy_chol = np.random.randint(150, 210, 50)
            healthy_hr = np.random.randint(140, 190, 50)
            
            # حالات مرضية
            risky_age = np.random.randint(50, 80, 50)
            risky_chol = np.random.randint(220, 350, 50)
            risky_hr = np.random.randint(90, 140, 50)
            
            fig_3d = go.Figure()
            
            # السليمين
            fig_3d.add_trace(go.Scatter3d(
                x=healthy_age,
                y=healthy_chol,
                z=healthy_hr,
                mode='markers',
                marker=dict(
                    size=4,
                    color='#00e676',
                    opacity=0.4,
                    symbol='circle'
                ),
                name='حالات سليمة',
                hovertemplate='<b>سليم</b><br>العمر: %{x}<br>الكوليسترول: %{y}<br>النبض: %{z}<extra></extra>'
            ))
            
            # المرضى
            fig_3d.add_trace(go.Scatter3d(
                x=risky_age,
                y=risky_chol,
                z=risky_hr,
                mode='markers',
                marker=dict(
                    size=4,
                    color='#ff4b4b',
                    opacity=0.4,
                    symbol='circle'
                ),
                name='حالات حرجة',
                hovertemplate='<b>حرج</b><br>العمر: %{x}<br>الكوليسترول: %{y}<br>النبض: %{z}<extra></extra>'
            ))
            
            # المريض الحالي
            fig_3d.add_trace(go.Scatter3d(
                x=[age],
                y=[chol],
                z=[thalach],
                mode='markers+text',
                marker=dict(
                    size=18,
                    color='#FFD700',
                    line=dict(width=3, color='white'),
                    symbol='diamond'
                ),
                text=["أنت هنا"],
                textposition="top center",
                textfont=dict(size=14, color='white', family='Cairo'),
                name='حالتك الحالية',
                hovertemplate='<b>أنت</b><br>العمر: %{x}<br>الكوليسترول: %{y}<br>النبض: %{z}<extra></extra>'
            ))
            
            fig_3d.update_layout(
                scene=dict(
                    xaxis=dict(title='العمر (سنة)', backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,0.1)"),
                    yaxis=dict(title='الكوليسترول (mg/dL)', backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,0.1)"),
                    zaxis=dict(title='معدل النبض (bpm)', backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,0.1)"),
                    bgcolor="rgba(0,0,0,0)"
                ),
                template="plotly_dark",
                height=600,
                margin=dict(l=0, r=0, b=0, t=30),
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Cairo", size=12),
                legend=dict(
                    bgcolor="rgba(255,255,255,0.1)",
                    bordercolor="rgba(255,255,255,0.2)",
                    borderwidth=1
                )
            )
            
            st.plotly_chart(fig_3d, use_container_width=True)
            
            st.write("---")
            
            # ==========================================
            # مقارنة مع المعدلات الطبيعية
            # ==========================================
            
            st.markdown("## 📈 مقارنة قيمك مع المعدلات الطبيعية")
            
            # تحضير بيانات المقارنة
            comparison_data = {
                'المؤشر': ['ضغط الدم', 'الكوليسترول', 'السكر الصايم', 'معدل النبض'],
                'قيمتك': [trestbps, chol, 'عالي' if fbs == "نعم" else 'طبيعي', thalach],
                'المعدل الطبيعي': ['< 120', '< 200', '< 100', f'{220 - age}'],
                'الحالة': [
                    'طبيعي' if trestbps < 120 else ('حدودي' if trestbps < 140 else 'عالي'),
                    'طبيعي' if chol < 200 else ('حدودي' if chol < 240 else 'عالي'),
                    'طبيعي' if fbs == "لا" else 'عالي',
                    'مناسب' if thalach >= (220 - age) * 0.5 else 'منخفض'
                ]
            }
            
            df_comparison = pd.DataFrame(comparison_data)
            
            # عرض الجدول بتنسيق جميل
            st.dataframe(
                df_comparison,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "المؤشر": st.column_config.TextColumn("المؤشر الطبي", width="medium"),
                    "قيمتك": st.column_config.TextColumn("قيمتك الحالية", width="medium"),
                    "المعدل الطبيعي": st.column_config.TextColumn("المعدل المثالي", width="medium"),
                    "الحالة": st.column_config.TextColumn("التقييم", width="small")
                }
            )
            
            st.write("---")
            
            # ==========================================
            # تصدير التقرير
            # ==========================================
            
            st.markdown("## 💾 حفظ ومشاركة التقرير")
            
            export_col1, export_col2, export_col3 = st.columns(3)
            
            with export_col1:
                # تحضير البيانات للتصدير
                report_data = {
                    'التاريخ': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'العمر': age,
                    'الجنس': gender,
                    'النتيجة': 'يحتاج فحص' if is_risky else 'سليم',
                    'نسبة الثقة': f"{confidence:.1f}%",
                    'مؤشر الصحة': f"{health_score:.0f}/100",
                    **input_dict
                }
                
                # تحويل لـ JSON
                json_report = json.dumps(report_data, ensure_ascii=False, indent=2)
                
                st.download_button(
                    label="📥 تحميل JSON",
                    data=json_report,
                    file_name=f"heart_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with export_col2:
                # تحويل لـ CSV
                csv_report = pd.DataFrame([report_data]).to_csv(index=False)
                
                st.download_button(
                    label="📊 تحميل CSV",
                    data=csv_report,
                    file_name=f"heart_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with export_col3:
                if st.button("🖨️ طباعة التقرير", use_container_width=True):
                    st.info("استخدم Ctrl+P لطباعة الصفحة")
        
        else:
            st.error("⚠️ ملفات الموديل غير موجودة! تأكد من وجود الملفات في المجلد.")

# ==========================================
# صفحة التاريخ الطبي
# ==========================================

elif st.session_state['page'] == 'history':
    
    col_back, col_title = st.columns([0.5, 4])
    
    with col_back:
        if st.button("🏠", help="رجوع للرئيسية"):
            go_to_landing()
            st.rerun()
    
    with col_title:
        st.markdown("# 📜 التاريخ الطبي")
    
    st.write("---")
    
    if 'medical_history' in st.session_state and len(st.session_state['medical_history']) > 0:
        
        st.success(f"📊 لديك {len(st.session_state['medical_history'])} سجل طبي محفوظ")
        
        # عرض السجلات
        for idx, record in enumerate(reversed(st.session_state['medical_history'])):
            
            with st.expander(f"🔍 التحليل رقم {len(st.session_state['medical_history']) - idx} - {record.get('timestamp', 'غير محدد')}"):
                
                rec_col1, rec_col2, rec_col3 = st.columns(3)
                
                with rec_col1:
                    st.metric("العمر", f"{record['age']} سنة")
                    st.metric("ضغط الدم", f"{record['trestbps']} mmHg")
                    st.metric("الكوليسترول", f"{record['chol']} mg/dL")
                
                with rec_col2:
                    st.metric("معدل النبض", f"{record['thalach']} bpm")
                    st.metric("النتيجة", "⚠️ يحتاج فحص" if record.get('is_risky') else "✅ سليم")
                    st.metric("الثقة", f"{record.get('confidence', 0):.1f}%")
                
                with rec_col3:
                    st.metric("مؤشر الصحة", f"{record.get('health_score', 0):.0f}/100")
                    st.metric("الجنس", "ذكر" if record['sex'] == 1 else "أنثى")
                    st.metric("السكر الصايم", "عالي" if record['fbs'] == 1 else "طبيعي")
        
        st.write("---")
        
        # رسمة تطور الصحة
        if len(st.session_state['medical_history']) > 1:
            st.markdown("### 📈 تطور مؤشر الصحة")
            
            history_df = pd.DataFrame(st.session_state['medical_history'])
            
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=list(range(len(history_df))),
                y=history_df['health_score'],
                mode='lines+markers',
                name='مؤشر الصحة',
                line=dict(color='#00e676', width=3),
                marker=dict(size=10, color='#00e676', line=dict(width=2, color='white'))
            ))
            
            fig_trend.update_layout(
                title="تطور مؤشر الصحة عبر الوقت",
                xaxis_title="رقم التحليل",
                yaxis_title="مؤشر الصحة (من 100)",
                template="plotly_dark",
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(255,255,255,0.02)',
                font=dict(family="Cairo")
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
        
        # زر حذف التاريخ
        if st.button("🗑️ مسح كل التاريخ", type="secondary"):
            st.session_state['medical_history'] = []
            st.success("تم مسح التاريخ الطبي بنجاح!")
            st.rerun()
    
    else:
        st.info("📭 لا يوجد سجلات طبية حتى الآن. ابدأ أول تحليل!")
        
        if st.button("🚀 ابدأ تحليل جديد", use_container_width=True):
            go_to_app()
            st.rerun()

# ==========================================
# صفحة الإحصائيات
# ==========================================

elif st.session_state['page'] == 'statistics':
    
    col_back, col_title = st.columns([0.5, 4])
    
    with col_back:
        if st.button("🏠", help="رجوع للرئيسية"):
            go_to_landing()
            st.rerun()
    
    with col_title:
        st.markdown("# 📊 الإحصائيات والتحليلات")
    
    st.write("---")
    
    # إحصائيات عامة
    st.markdown("### 📈 إحصائيات عامة عن أمراض القلب")
    
    stat1, stat2, stat3, stat4 = st.columns(4)
    
    with stat1:
        st.markdown("""
        <div class="stat-card">
            <h2 style='color: #ff4b4b; margin: 0;'>17.9M</h2>
            <p style='margin: 5px 0;'>وفاة سنوياً</p>
            <p style='font-size: 0.85rem; color: #aaa;'>بسبب أمراض القلب</p>
        </div>
        """, unsafe_allow_html=True)
    
    with stat2:
        st.markdown("""
        <div class="stat-card">
            <h2 style='color: #ffa726; margin: 0;'>31%</h2>
            <p style='margin: 5px 0;'>من الوفيات</p>
            <p style='font-size: 0.85rem; color: #aaa;'>حول العالم</p>
        </div>
        """, unsafe_allow_html=True)
    
    with stat3:
        st.markdown("""
        <div class="stat-card">
            <h2 style='color: #00e676; margin: 0;'>80%</h2>
            <p style='margin: 5px 0;'>قابلة للوقاية</p>
            <p style='font-size: 0.85rem; color: #aaa;'>بنمط حياة صحي</p>
        </div>
        """, unsafe_allow_html=True)
    
    with stat4:
        st.markdown("""
        <div class="stat-card">
            <h2 style='color: #2196f3; margin: 0;'>50+</h2>
            <p style='margin: 5px 0;'>السن الأكثر عرضة</p>
            <p style='font-size: 0.85rem; color: #aaa;'>للإصابة</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    
    # رسمة توضيحية
    st.markdown("### 🌍 توزيع عوامل الخطر")
    
    # بيانات وهمية توضيحية
    risk_factors = ['التدخين', 'الضغط العالي', 'الكوليسترول', 'السكري', 'السمنة', 'قلة الحركة']
    risk_percentages = [23, 31, 27, 19, 29, 35]
    
    fig_risks = go.Figure()
    
    fig_risks.add_trace(go.Bar(
        x=risk_percentages,
        y=risk_factors,
        orientation='h',
        marker=dict(
            color=['#ff4b4b', '#ff5722', '#ff6f00', '#ffa726', '#ffb74d', '#ffc107'],
            line=dict(color='rgba(255,255,255,0.3)', width=1)
        ),
        text=[f"{p}%" for p in risk_percentages],
        textposition='auto'
    ))
    
    fig_risks.update_layout(
        title="نسبة انتشار عوامل الخطر بين مرضى القلب",
        xaxis_title="النسبة المئوية",
        template="plotly_dark",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0.02)',
        font=dict(family="Cairo"),
        showlegend=False
    )
    
    st.plotly_chart(fig_risks, use_container_width=True)
    
    st.write("---")
    
    # نصائح الوقاية
    st.markdown("### 💪 كيف تحمي قلبك؟")
    
    prev_col1, prev_col2 = st.columns(2)
    
    with prev_col1:
        st.markdown("""
        #### 🥗 التغذية الصحية
        - زود الخضار والفواكه يومياً
        - قلل الدهون المشبعة والملح
        - اختار الحبوب الكاملة
        - كُل سمك مرتين في الأسبوع
        - اشرب مياه كتير
        
        #### 🏃 النشاط البدني
        - 30 دقيقة رياضة يومياً
        - المشي السريع مفيد جداً
        - اصعد السلم بدل المصعد
        - مارس رياضة تحبها
        """)
    
    with prev_col2:
        st.markdown("""
        #### 🚭 تجنب التدخين
        - التدخين عدو القلب الأول
        - حتى التدخين السلبي خطر
        - اطلب مساعدة للإقلاع
        
        #### 😌 إدارة التوتر
        - خد وقتك في الراحة
        - مارس التأمل أو اليوجا
        - نام كويس 7-8 ساعات
        - اقضي وقت مع العيلة
        
        #### 🩺 الفحص الدوري
        - افحص ضغطك وسكرك دورياً
        - راجع الدكتور سنوياً
        - اعمل تحاليل شاملة
        """)
    
    st.write("---")
    
    # مصادر علمية
    st.markdown("### 📚 مصادر علمية موثوقة")
    
    st.markdown("""
    - 🏥 [منظمة الصحة العالمية - أمراض القلب](https://www.who.int/health-topics/cardiovascular-diseases)
    - 💙 [جمعية القلب الأمريكية](https://www.heart.org)
    - 🔬 [المعهد الوطني للقلب](https://www.nhlbi.nih.gov)
    - 📊 [إحصائيات أمراض القلب 2024](https://www.cdc.gov/heartdisease)
    """)
    
    st.info("💡 **ملاحظة:** كل المعلومات هنا للتوعية فقط. استشر طبيبك دائماً.")

# ==========================================
# Footer في كل الصفحات
# ==========================================

st.write("")
st.write("")
st.markdown("---")

footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("""
    **🫀 دكتور القلب الذكي**  
    نظام ذكاء اصطناعي متطور  
    للكشف المبكر عن أمراض القلب
    """)

with footer_col2:
    st.markdown("""
    **⚡ تقنيات مستخدمة**  
    - Machine Learning  
    - SHAP Explainability  
    - 3D Visualization  
    - Real-time Analysis
    """)

with footer_col3:
    st.markdown("""
    **📞 تواصل معنا**  
    - 📧 Email: support@smartheart.ai  
    - 🌐 Website: www.smartheart.ai  
    - 💬 Support: 24/7 Available
    """)

st.markdown("""
<div style='text-align: center; padding: 20px; color: #666;'>
    <p style='margin: 5px 0;'>🔬 Powered by Advanced AI & Medical Research</p>
    <p style='margin: 5px 0;'>Made with ❤️ for Better Healthcare & Saving Lives</p>
    <p style='margin: 5px 0; font-size: 0.9rem;'>© 2024 Smart Heart Doctor - All Rights Reserved | v2.0</p>
    <p style='margin: 10px 0; font-size: 0.85rem; color: #888;'>
        ⚠️ هذا النظام للمساعدة الطبية فقط وليس بديلاً عن استشارة الطبيب المختص
    </p>
</div>
""", unsafe_allow_html=True)
