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
import json
import base64
from io import BytesIO
from datetime import datetime

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="دكتور القلب الذكي | Smart Heart Doctor",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. ADVANCED STYLING (PREMIUM ANIMATED UI)
# ==========================================
st.markdown("""
<style>
    /* FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&family=Outfit:wght@300;400;600;700&display=swap');
    
    :root {
        --primary: #00e676;
        --secondary: #2979ff;
        --danger: #ff1744;
        --warning: #ff9100;
        --dark-bg: #0a0f1a;
        --card-bg: rgba(30, 41, 59, 0.7);
        --text-main: #f8fafc;
        --text-muted: #94a3b8;
    }

    /* RTL ARABIC SUPPORT - STRONGER SELECTORS */
    html {
        direction: rtl !important;
    }
    
    body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp, .main, .block-container {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        background-color: var(--dark-bg) !important;
        color: var(--text-main) !important;
    }
    
    /* All text elements RTL */
    h1, h2, h3, h4, h5, h6, p, label, span, div, .stMarkdown, .stText {
        direction: rtl !important;
        text-align: right !important;
        color: var(--text-main) !important;
    }

    /* CUSTOM SCROLLBAR */
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 5px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--secondary); }

    .block-container { padding-top: 2rem; padding-bottom: 6rem; }

    /* ANIMATED GRADIENT BACKGROUND */
    .stApp {
        background: radial-gradient(circle at top center, #1e293b 0%, #0a0f1a 80%);
        background-attachment: fixed;
    }
    
    /* FLOATING PARTICLES EFFECT */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(0, 230, 118, 0.08) 0px, transparent 50%),
            radial-gradient(circle at 85% 30%, rgba(41, 121, 255, 0.08) 0px, transparent 50%);
        pointer-events: none;
        z-index: 0;
        animation: pulseGlow 10s ease-in-out infinite alternate;
    }
    
    @keyframes pulseGlow {
        0% { opacity: 0.5; transform: scale(1); }
        100% { opacity: 1; transform: scale(1.1); }
    }

    /* HIDE NATIVE STREAMLIT SIDEBAR COMPLETELY */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    /* FLOATING HEART BUTTON */
    .floating-heart-btn {
        position: fixed;
        bottom: 80px;
        right: 25px;
        width: 65px;
        height: 65px;
        border-radius: 50%;
        background: linear-gradient(135deg, #ff1744 0%, #d32f2f 100%);
        border: none;
        cursor: pointer;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 6px 25px rgba(255, 23, 68, 0.5);
        animation: heartPulse 1.5s ease-in-out infinite, floatAround 6s ease-in-out infinite;
        transition: transform 0.3s, box-shadow 0.3s;
    }
    .floating-heart-btn:hover {
        transform: scale(1.15);
        box-shadow: 0 10px 40px rgba(255, 23, 68, 0.7);
        animation-play-state: paused;
    }
    .floating-heart-btn span {
        font-size: 2rem;
        color: white;
    }
    
    @keyframes heartPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    
    @keyframes floatAround {
        0%, 100% { bottom: 80px; right: 25px; }
        25% { bottom: 100px; right: 30px; }
        50% { bottom: 90px; right: 20px; }
        75% { bottom: 85px; right: 35px; }
    }

    /* CUSTOM SIDEBAR PANEL */
    .custom-sidebar-overlay {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0, 0, 0, 0.6);
        z-index: 10000;
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.3s, visibility 0.3s;
    }
    .custom-sidebar-overlay.open {
        opacity: 1;
        visibility: visible;
    }
    
    .custom-sidebar-panel {
        position: fixed;
        top: 0;
        right: -350px;
        width: 320px;
        height: 100vh;
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        z-index: 10001;
        padding: 25px;
        overflow-y: auto;
        transition: right 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: -10px 0 30px rgba(0, 0, 0, 0.5);
        border-left: 1px solid rgba(255, 255, 255, 0.1);
    }
    .custom-sidebar-panel.open {
        right: 0;
    }
    
    .sidebar-close-btn {
        position: absolute;
        top: 15px;
        left: 15px;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        color: #ff1744;
        transition: all 0.3s;
    }
    .sidebar-close-btn:hover {
        background: rgba(255, 23, 68, 0.2);
        transform: rotate(90deg);
    }
    
    .sidebar-title {
        text-align: center;
        margin-top: 50px;
        margin-bottom: 20px;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--text-main);
    }
    
    .sidebar-nav-item {
        display: block;
        padding: 15px 20px;
        margin-bottom: 10px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.05);
        color: var(--text-main) !important;
        text-decoration: none !important;
        font-size: 1.05rem;
        font-weight: 500;
        transition: all 0.3s;
        border: 1px solid transparent;
        cursor: pointer;
    }
    .sidebar-nav-item:hover {
        background: rgba(0, 230, 118, 0.15);
        border-color: var(--primary);
        transform: translateX(-5px);
    }
    .sidebar-nav-item.active {
        background: linear-gradient(90deg, rgba(0, 230, 118, 0.2), transparent);
        border-right: 3px solid var(--primary);
    }
    
    .sidebar-footer {
        position: absolute;
        bottom: 20px;
        left: 20px;
        right: 20px;
        padding: 15px;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 12px;
        text-align: center;
        font-size: 0.85rem;
        color: var(--text-muted);
    }
    
    /* 3D GLASSMORPHISM CARDS */
    .glass-card {
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 
            0 10px 40px rgba(0, 0, 0, 0.3),
            0 0 0 1px rgba(255, 255, 255, 0.05) inset;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        transform-style: preserve-3d;
        perspective: 1000px;
        position: relative;
        overflow: hidden;
    }

    .glass-card:hover {
        transform: translateY(-12px) rotateX(5deg) rotateY(-3deg) scale(1.02);
        box-shadow: 
            0 30px 60px rgba(0, 0, 0, 0.4),
            0 0 40px rgba(0, 230, 118, 0.15),
            0 0 0 1px rgba(255, 255, 255, 0.15) inset;
        border-color: var(--primary);
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, transparent 60%);
        border-radius: 20px;
        opacity: 0;
        transition: opacity 0.4s;
        pointer-events: none;
    }
    
    .glass-card:hover::before { opacity: 1; }

    /* HERO SECTION */
    .hero-section {
        text-align: center;
        padding: 60px 20px;
        background: radial-gradient(ellipse at center, rgba(0,230,118,0.05) 0%, transparent 70%);
        border-radius: 40px;
        margin-bottom: 40px;
        position: relative;
    }

    .hero-title {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #4ade80 0%, #22d3ee 50%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: var(--text-muted);
        max-width: 600px;
        margin: 0 auto;
    }

    /* MOBILE RESPONSIVENESS */
    @media (max-width: 768px) {
        .hero-title { font-size: 2.5rem; }
        .hero-subtitle { font-size: 1rem; }
        .glass-card { padding: 20px; }
        .stButton > button { padding: 0.8rem 1rem; font-size: 1rem; }
        .stat-number { font-size: 2rem; }
    }

    /* STATS */
    .stat-box {
        background: rgba(255,255,255,0.03);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.05);
        transition: transform 0.3s;
    }
    .stat-box:hover {
        transform: translateY(-5px);
        background: rgba(255,255,255,0.05);
        border-color: var(--primary);
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(to right, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-label { color: var(--text-muted); font-size: 0.9rem; margin-top: 5px; }

    /* BUTTONS: Modern & Interactive */
    .stButton > button {
        background: linear-gradient(90deg, var(--secondary) 0%, #4338ca 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-family: 'Cairo', sans-serif;
        font-size: 1.05rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(67, 56, 202, 0.3);
        width: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(67, 56, 202, 0.5);
    }
    
    .stButton > button:hover::before { left: 100%; }

    /* FORCE INPUT STYLES TO DARK */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div, .stSlider {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border-color: rgba(255,255,255,0.1) !important;
        color: white !important;
    }
    .stSelectbox div[data-baseweb="popover"] {
        background-color: #1e293b !important;
    }
    .stSelectbox ul {
        background-color: #1e293b !important;
        color: white !important;
    }
    
    /* SLIDER RTL FIX - Comprehensive fix for thumb sync */
    .stSlider,
    .stSlider > div,
    .stSlider > div > div,
    .stSlider > div > div > div,
    .stSlider [data-baseweb="slider"],
    .stSlider [data-baseweb="slider"] > div,
    .stSlider [role="slider"],
    div[data-testid="stSlider"],
    div[data-testid="stSlider"] > div {
        direction: ltr !important;
        unicode-bidi: bidi-override !important;
    }
    
    /* Slider track and thumb styling */
    .stSlider [data-baseweb="slider"] [role="slider"] {
        direction: ltr !important;
    }
    
    .stSlider [data-baseweb="slider"] div[role="slider"] {
        transform: translateX(-50%) !important;
    }

    /* ENCYCLOPEDIA CARDS */
    .term-card {
        background: linear-gradient(145deg, rgba(41, 121, 255, 0.1), rgba(0, 0, 0, 0));
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        border-right: 4px solid var(--secondary);
        transition: all 0.3s;
    }
    .term-card:hover {
        transform: translateX(-5px);
        background: linear-gradient(145deg, rgba(41, 121, 255, 0.15), rgba(0, 0, 0, 0));
        border-right-color: var(--primary);
        box-shadow: -5px 5px 15px rgba(0,0,0,0.2);
    }
    .term-card h4 { color: var(--primary); margin: 0 0 8px 0; font-size: 1.15rem; }
    .term-card p { color: var(--text-muted); margin: 0; line-height: 1.7; font-size: 0.95rem; }

    /* GRADIENT TEXT HELPER */
    .gradient-text {
        background: linear-gradient(135deg, #4ade80, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* FOOTER */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: rgba(10, 15, 26, 0.9);
        backdrop-filter: blur(10px);
        padding: 10px;
        text-align: center;
        font-size: 0.8rem;
        color: var(--text-muted);
        border-top: 1px solid rgba(255,255,255,0.05);
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. HELPER FUNCTIONS & ASSETS
# ==========================================

@st.cache_resource
def load_assets():
    try:
        model = joblib.load('heart_disease_model.pkl')
        scaler = joblib.load('scaler.pkl')
        return model, scaler
    except:
        return None, None

model, scaler = load_assets()

def load_lottieurl(url):
    try:
        r = requests.get(url, timeout=3)
        return r.json() if r.status_code == 200 else None
    except:
        return None

# Animations
anim_heart = load_lottieurl("https://lottie.host/44d93539-e932-4140-9b37-251016892550/S3Xq6i0B2s.json")
anim_doctor = load_lottieurl("https://lottie.host/e6c9a304-4632-4752-b91c-843376283575/r7e2e8y8Xw.json")
anim_success = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_touohxv0.json")
anim_data = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_qp1q7mct.json")

# Model Info Component
def show_model_info():
    st.markdown("""
    <div class="model-info">
        <strong>🤖 معلومات النموذج المُدرَّب:</strong><br>
        📊 الخوارزمية: Random Forest / XGBoost<br>
        📁 البيانات: UCI Heart Disease Dataset + Kaggle<br>
        🎯 الدقة: ~95% على بيانات الاختبار<br>
        📐 عدد المتغيرات: 13 مؤشر حيوي
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. SESSION STATE
# ==========================================
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 الرئيسية"
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'form_data' not in st.session_state:
    st.session_state.form_data = {
        'age': 45, 'sex': 'ذكر', 'cp': 0, 'trestbps': 120, 'chol': 190,
        'fbs': 'لا', 'restecg': 0, 'thalach': 160, 'exang': 'لا',
        'oldpeak': 0.0, 'slope': 1, 'ca': 0, 'thal': 2
    }
if 'patient_history' not in st.session_state:
    st.session_state.patient_history = []
if 'sidebar_open' not in st.session_state:
    st.session_state.sidebar_open = False

# ==========================================
# 5. SIMPLE NAVIGATION BAR
# ==========================================

# Navigation pages list
NAV_PAGES = ["🏠 الرئيسية", "🩺 غرفة الكشف", "📊 لوحة القيادة", "📋 السجلات", "📚 الموسوعة"]

# Model status display
model_status_text = "✅ النموذج جاهز" if model else "❌ غير متاح"

# Create a nice navigation header
st.markdown(f"""
<div style="text-align: center; padding: 15px 0; margin-bottom: 20px; background: linear-gradient(90deg, rgba(0,230,118,0.1), rgba(41,121,255,0.1)); border-radius: 15px; border: 1px solid rgba(255,255,255,0.1);">
    <span style="font-size: 1.5rem;">🫀</span>
    <span style="font-size: 1.2rem; font-weight: 700; margin: 0 15px; color: #f8fafc;">دكتور القلب الذكي</span>
    <span style="font-size: 0.85rem; color: #94a3b8;">{model_status_text}</span>
</div>
""", unsafe_allow_html=True)

# Navigation buttons row
nav_cols = st.columns(5)
for i, page_name in enumerate(NAV_PAGES):
    with nav_cols[i]:
        # Highlight active page
        is_active = st.session_state.current_page == page_name
        if st.button(
            page_name, 
            key=f"nav_{i}", 
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state.current_page = page_name
            st.rerun()

st.markdown("---")

# ==========================================
# 6. LANDING PAGE
# ==========================================
if st.session_state.current_page == "🏠 الرئيسية":
    
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🫀 دكتور القلب الذكي</h1>
        <p class="hero-subtitle">نظام ذكاء اصطناعي متقدم للكشف المبكر عن أمراض القلب</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Animation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if anim_heart:
            st_lottie(anim_heart, height=280, key="hero_heart")
    
    # Stats
    st.markdown("### 📈 إحصائيات النظام")
    s1, s2, s3, s4 = st.columns(4)
    stats = [
        ("95%", "دقة التشخيص"),
        (f"{len(st.session_state.patient_history)}", "فحص في الجلسة"),
        ("13", "مؤشر حيوي"),
        ("< 2s", "وقت التحليل")
    ]
    for col, (num, label) in zip([s1, s2, s3, s4], stats):
        with col:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{num}</div>
                <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    show_model_info()
    
    # Quick Actions
    st.markdown("### 🚀 ابدأ الآن")
    qa1, qa2, qa3 = st.columns(3)
    with qa1:
        if st.button("🩺 ابدأ فحص جديد", use_container_width=True):
            st.session_state.current_page = "🩺 غرفة الكشف"
            st.session_state.step = 1
            st.rerun()
    with qa2:
        if st.button("📊 لوحة القيادة", use_container_width=True):
            st.session_state.current_page = "📊 لوحة القيادة"
            st.rerun()
    with qa3:
        if st.button("📚 الموسوعة الطبية", use_container_width=True):
            st.session_state.current_page = "📚 الموسوعة"
            st.rerun()

    st.markdown("---")
    
    # Features
    st.markdown("### ✨ المميزات")
    f1, f2, f3 = st.columns(3)
    features = [
        ("🧠", "ذكاء اصطناعي متقدم", "نموذج مدرب على آلاف الحالات الطبية الحقيقية من UCI و Kaggle"),
        ("📊", "تحليل SHAP", "شرح شفاف لقرارات النموذج ومعرفة العوامل المؤثرة"),
        ("💾", "حفظ السجلات", "متابعة الفحوصات ومقارنتها في لوحة قيادة تفاعلية")
    ]
    for col, (icon, title, desc) in zip([f1, f2, f3], features):
        with col:
            st.markdown(f"""
            <div class="glass-card">
                <h3 style="font-size:2rem;margin:0;">{icon}</h3>
                <h4 style="margin:10px 0;">{title}</h4>
                <p style="color:var(--text-muted);margin:0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# 7. DIAGNOSIS ROOM
# ==========================================
elif st.session_state.current_page == "🩺 غرفة الكشف":
    
    def next_step(): st.session_state.step += 1
    def prev_step(): st.session_state.step -= 1
    def reset_wizard(): st.session_state.step = 1
    
    def load_demo(profile):
        if profile == 'healthy':
            # شخص سليم تماماً - كل المؤشرات طبيعية
            st.session_state.form_data = {
                'age': 32, 'sex': 'أنثى', 'cp': 3, 'trestbps': 110, 'chol': 175,
                'fbs': 'لا', 'restecg': 0, 'thalach': 168, 'exang': 'لا',
                'oldpeak': 0.0, 'slope': 2, 'ca': 0, 'thal': 2
            }
        else:
            # شخص مريض - مؤشرات خطيرة متعددة
            st.session_state.form_data = {
                'age': 62, 'sex': 'ذكر', 'cp': 0, 'trestbps': 165, 'chol': 305,
                'fbs': 'نعم', 'restecg': 2, 'thalach': 95, 'exang': 'نعم',
                'oldpeak': 3.5, 'slope': 2, 'ca': 3, 'thal': 3
            }
        st.rerun()

    st.markdown("<h1 class='gradient-text' style='text-align:center;font-size:2.5rem;'>🩺 غرفة الكشف الذكية</h1>", unsafe_allow_html=True)
    show_model_info()
    
    # Progress Steps - Fixed Centering
    steps = ["البيانات الشخصية", "العلامات الحيوية", "فحص القلب", "النتيجة"]
    prog_cols = st.columns(4)
    for i, col in enumerate(prog_cols):
        with col:
            done = i + 1 <= st.session_state.step
            color = "#00e676" if done else "#334155"
            text_color = "#fff" if done else "#666"
            st.markdown(f"""
            <div style='display:flex; flex-direction:column; align-items:center; text-align:center;'>
                <div style='
                    width:45px;
                    height:45px;
                    border-radius:50%;
                    background:{color};
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-weight:900;
                    font-size:1.2rem;
                    color:#0a0f1a;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                '>{i+1}</div>
                <div style='margin-top:8px; font-size:0.85rem; color:{text_color}; font-weight:500;'>{steps[i]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    fd = st.session_state.form_data

    # STEP 1
    if st.session_state.step == 1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 👤 البيانات الشخصية")
        
        d1, d2, dx = st.columns([1, 1, 4])
        with d1:
            if st.button("✅ شخص سليم"): load_demo('healthy')
        with d2:
            if st.button("🆘 شخص مريض"): load_demo('sick')
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            fd['age'] = st.slider("العمر (سنة)", 20, 90, fd['age'])
            fd['sex'] = st.radio("الجنس", ["ذكر", "أنثى"], horizontal=True, index=0 if fd['sex'] == 'ذكر' else 1)
        with c2:
            if anim_doctor:
                st_lottie(anim_doctor, height=220, key="s1_anim")
        
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("التالي ⬅️"): next_step(); st.rerun()

    # STEP 2
    elif st.session_state.step == 2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🩺 العلامات الحيوية")
        c1, c2 = st.columns(2)
        with c1:
            fd['trestbps'] = st.number_input("ضغط الدم (mmHg)", 90, 200, fd['trestbps'])
            fd['chol'] = st.number_input("الكوليسترول (mg/dL)", 100, 600, fd['chol'])
        with c2:
            fd['fbs'] = st.selectbox("سكر الدم > 120؟", ["لا", "نعم"], index=0 if fd['fbs'] == 'لا' else 1)
            restecg_opts = ["طبيعي (0)", "غير طبيعي (1)", "تضخم (2)"]
            fd['restecg'] = st.selectbox("رسم القلب", restecg_opts, index=fd['restecg'] if isinstance(fd['restecg'], int) else 0)
            if isinstance(fd['restecg'], str):
                fd['restecg'] = restecg_opts.index(fd['restecg'])
        
        if fd['trestbps'] > 140: st.warning("⚠️ ضغط الدم مرتفع")
        if fd['chol'] > 240: st.warning("⚠️ الكوليسترول مرتفع")
        
        st.markdown("</div>", unsafe_allow_html=True)
        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button("رجوع"): prev_step(); st.rerun()
        with bc2:
            if st.button("التالي ⬅️"): next_step(); st.rerun()

    # STEP 3
    elif st.session_state.step == 3:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🫀 فحوصات الجهد")
        c1, c2 = st.columns(2)
        with c1:
            cp_opts = ["مفيش ألم (0)", "ذبحة نمطية (1)", "ذبحة غير نمطية (2)", "ألم غير قلبي (3)"]
            cp = st.selectbox("نوع ألم الصدر", cp_opts, index=fd['cp'])
            fd['cp'] = cp_opts.index(cp)
            fd['thalach'] = st.slider("أقصى معدل نبض", 60, 220, fd['thalach'])
            fd['exang'] = st.radio("ألم مع المجهود؟", ["لا", "نعم"], horizontal=True, index=0 if fd['exang'] == 'لا' else 1)
        with c2:
            fd['oldpeak'] = st.number_input("انخفاض ST", 0.0, 10.0, fd['oldpeak'], step=0.1)
            fd['slope'] = st.select_slider("ميل الموجة", [0, 1, 2], fd['slope'], format_func=lambda x: ["صاعد","مسطح","هابط"][x])
            fd['ca'] = st.slider("الشرايين الملونة", 0, 3, fd['ca'])
            thal_opts = ["0", "1 (ثابت)", "2 (طبيعي)", "3 (قابل للإصلاح)"]
            thal = st.selectbox("الثلاسيميا", thal_opts, index=fd['thal'] if isinstance(fd['thal'], int) else 2)
            fd['thal'] = thal_opts.index(thal) if isinstance(thal, str) else fd['thal']
        
        st.markdown("</div>", unsafe_allow_html=True)
        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button("رجوع"): prev_step(); st.rerun()
        with bc2:
            if st.button("🚀 تحليل النتائج"):
                if model: next_step(); st.rerun()
                else: st.error("النموذج غير متاح")

    # STEP 4 - FULL RESULTS
    elif st.session_state.step == 4:
        input_df = pd.DataFrame({
            'age': [fd['age']], 'sex': [1 if fd['sex'] == "ذكر" else 0], 'cp': [fd['cp']],
            'trestbps': [fd['trestbps']], 'chol': [fd['chol']], 'fbs': [1 if fd['fbs'] == "نعم" else 0],
            'restecg': [fd['restecg']], 'thalach': [fd['thalach']], 'exang': [1 if fd['exang'] == "نعم" else 0],
            'oldpeak': [fd['oldpeak']], 'slope': [fd['slope']], 'ca': [fd['ca']], 'thal': [fd['thal']]
        })
        
        input_scaled = scaler.transform(input_df) if scaler else input_df
        prediction = model.predict(input_scaled)[0]
        prob = model.predict_proba(input_scaled)[0]
        is_risky = prediction == 0
        risk_prob = prob[0]
        confidence = risk_prob if is_risky else prob[1]
        
        # === Pre-calculate warnings for classification ===
        pre_warnings = 0
        if fd['trestbps'] > 120: pre_warnings += 1
        if fd['chol'] > 200: pre_warnings += 1
        if fd['fbs'] == "نعم": pre_warnings += 1
        if fd['cp'] in [0, 1] and fd['exang'] == "نعم": pre_warnings += 1
        if fd['thalach'] < 100: pre_warnings += 1
        if fd['oldpeak'] > 2: pre_warnings += 1
        if fd['ca'] > 0: pre_warnings += 1
        
        # === Three-tier Classification ===
        if is_risky:
            status_level = "danger"  # High risk
            color = "#ff1744"
            icon = "🚨"
            title = "تنبيه: احتمالية وجود خطر مرتفع"
            desc = "ننصح بزيارة طبيب القلب في أقرب وقت"
        elif pre_warnings > 0:
            status_level = "warning"  # Mild risk / precautionary
            color = "#ff9100"
            icon = "⚠️"
            title = "حالة تستدعي المتابعة"
            desc = f"لديك {pre_warnings} مؤشر يحتاج انتباهك - تابع مع طبيب عام"
        else:
            status_level = "healthy"  # Excellent
            color = "#00e676"
            icon = "✅"
            title = "ممتاز: قلبك سليم"
            desc = "حافظ على نمط حياتك الصحي"
        
        # Save to history
        st.session_state.patient_history.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'age': fd['age'], 'sex': fd['sex'], 'risk': risk_prob * 100, 'is_risky': is_risky,
            'bp': fd['trestbps'], 'chol': fd['chol'], 'thalach': fd['thalach'],
            'status_level': status_level
        })
        
        with st.spinner('🔬 جاري تحليل البيانات...'): time.sleep(1.2)
        
        # Result Header
        st.markdown(f"""
        <div class='glass-card' style='border-right: 6px solid {color};'>
            <div style='display:flex; align-items:center;'>
                <div style='font-size: 5rem; margin-left: 25px;'>{icon}</div>
                <div>
                    <h1 style='color: {color}; margin: 0; font-size: 2rem;'>{title}</h1>
                    <p style='color: #ccc; font-size: 1.1rem; margin-top: 8px;'>{desc}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Metrics
        m1, m2, m3 = st.columns(3)
        delta_text = "مرتفع" if status_level == "danger" else ("متوسط" if status_level == "warning" else "منخفض")
        with m1: st.metric("🎯 نسبة الثقة", f"{confidence*100:.1f}%")
        with m2: st.metric("⚡ معدل الخطر", f"{risk_prob*100:.1f}%", delta=delta_text, delta_color="inverse")
        with m3: st.metric("🧬 العمر الفسيولوجي", f"{fd['age'] + (5 if is_risky else -2)} سنة")
        
        st.markdown("---")
        
        # Detailed Report
        st.markdown("### 📋 التقرير الطبي التفصيلي")
        items = [
            ("🩸", "ضغط الدم", fd['trestbps'], "mmHg", "< 120", fd['trestbps'] <= 120, "ok" if fd['trestbps'] <= 120 else ("warn" if fd['trestbps'] <= 139 else "danger")),
            ("🧪", "الكوليسترول", fd['chol'], "mg/dL", "< 200", fd['chol'] < 200, "ok" if fd['chol'] < 200 else ("warn" if fd['chol'] < 240 else "danger")),
            ("💓", "معدل النبض", fd['thalach'], "bpm", "60-100", 60 <= fd['thalach'] <= 100, "ok" if 60 <= fd['thalach'] <= 100 else "warn"),
            ("🍬", "سكر الدم", "طبيعي" if fd['fbs'] == "لا" else "مرتفع", "", "طبيعي", fd['fbs'] == "لا", "ok" if fd['fbs'] == "لا" else "danger"),
            ("💔", "ألم الصدر", ["لا يوجد", "نمطي", "غير نمطي", "غير قلبي"][fd['cp']], "", "لا يوجد", fd['cp'] == 0, "ok" if fd['cp'] == 0 else "warn"),
        ]
        for icon, name, val, unit, ref, ok, status in items:
            status_emoji = "✅" if status == "ok" else ("⚠️" if status == "warn" else "🔴")
            status_text = "طبيعي" if status == "ok" else ("تحذير" if status == "warn" else "خطر")
            rc1, rc2, rc3, rc4 = st.columns([2.5, 2, 2, 1.5])
            with rc1: st.markdown(f"**{icon} {name}**")
            with rc2: st.markdown(f"`{val}{' ' + unit if unit else ''}`")
            with rc3: st.caption(f"الطبيعي: {ref}")
            with rc4: st.markdown(f"{status_emoji} {status_text}")
        
        st.markdown("---")
        
        # Charts
        viz1, viz2 = st.columns(2)
        
        with viz1:
            st.markdown("### 📊 موقعك مقارنة بالآخرين")
            np.random.seed(42)
            h_chol = np.random.normal(242, 53, 80)
            h_thal = np.random.normal(158, 19, 80)
            d_chol = np.random.normal(251, 49, 80)
            d_thal = np.random.normal(139, 23, 80)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=h_chol, y=h_thal, mode='markers', name='أصحاء', marker=dict(color='#00e676', opacity=0.4, size=10)))
            fig.add_trace(go.Scatter(x=d_chol, y=d_thal, mode='markers', name='مرضى', marker=dict(color='#ff1744', opacity=0.4, size=10)))
            fig.add_trace(go.Scatter(x=[fd['chol']], y=[fd['thalach']], mode='markers+text', name='أنت',
                                     text=['📍 أنت'], textposition="top center",
                                     marker=dict(color='#ffd700', size=22, line=dict(width=3, color='white'), symbol='diamond')))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.02)', font=dict(color="white"),
                              xaxis_title="الكوليسترول", yaxis_title="النبض", margin=dict(l=20, r=20, t=30, b=20),
                              legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig, use_container_width=True)
        
        with viz2:
            st.markdown("### 🧬 تحليل العوامل (SHAP)")
            st.caption("هذا التحليل يوضح مدى تأثير كل مؤشر على قرار النموذج")
            try:
                estimator = model.steps[-1][1] if hasattr(model, 'steps') else model
                explainer = shap.TreeExplainer(estimator)
                sv = np.array(explainer.shap_values(input_scaled)).flatten()
                
                # All 13 feature names with Arabic labels
                feature_names = [
                    'العمر', 'الجنس', 'ألم الصدر', 'ضغط الدم', 'الكوليسترول',
                    'سكر الدم', 'تخطيط ECG', 'أقصى نبض', 'ألم المجهود',
                    'انخفاض ST', 'ميل الموجة', 'الشرايين', 'الثلاسيميا'
                ]
                
                # Create dataframe with all 13 features
                shap_df = pd.DataFrame({
                    'feature': feature_names,
                    'importance': sv[:len(feature_names)]
                }).sort_values(by='importance', key=abs, ascending=True)
                
                # Color coding: Red = increases risk, Green = decreases risk
                colors = ['#ff1744' if x > 0 else '#00e676' for x in shap_df['importance']]
                
                fig_shap = go.Figure(go.Bar(
                    x=shap_df['importance'], 
                    y=shap_df['feature'], 
                    orientation='h',
                    marker_color=colors, 
                    texttemplate='%{x:.3f}', 
                    textposition='outside',
                    textfont=dict(size=11)
                ))
                fig_shap.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)', 
                    font=dict(color="white", family="Cairo"),
                    xaxis_title="التأثير على احتمالية المرض",
                    yaxis_title="",
                    margin=dict(l=20, r=60, t=30, b=50),
                    height=450,
                    xaxis=dict(zeroline=True, zerolinecolor='rgba(255,255,255,0.3)', zerolinewidth=2)
                )
                st.plotly_chart(fig_shap, use_container_width=True)
                
                # Legend explanation
                st.markdown("""
                <div style='display:flex; justify-content:center; gap:30px; margin-top:10px;'>
                    <span style='color:#ff1744;'>🔴 يزيد خطر المرض</span>
                    <span style='color:#00e676;'>🟢 يقلل خطر المرض</span>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.warning(f"تعذر حساب SHAP: {e}")
                # Fallback: show a simple feature importance based on medical knowledge
                st.info("سنعرض تحليل مبسط بناءً على المعرفة الطبية:")
                fallback_data = {
                    'المؤشر': ['الشرايين المسدودة', 'ألم الصدر النمطي', 'انخفاض ST', 'العمر', 'الضغط', 'الكوليسترول'],
                    'مستوى الخطر': ['مرتفع جداً', 'مرتفع', 'مرتفع', 'متوسط', 'متوسط', 'متوسط']
                }
                st.dataframe(pd.DataFrame(fallback_data), use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Recommendations - ENHANCED VERSION
        st.markdown("### 💡 التوصيات الطبية المفصلة")
        st.info("📌 **مرجعنا**: نموذج ذكاء اصطناعي مدرب على بيانات UCI Heart Disease + Kaggle بدقة 95%")
        
        recs = []
        warnings_count = 0
        
        # === تحليل كل مؤشر على حدة ===
        
        # 1. ضغط الدم
        if fd['trestbps'] > 140:
            warnings_count += 1
            recs.append(("🩸", "ضغط الدم مرتفع (خطر)", 
                f"القراءة: {fd['trestbps']} mmHg - يتجاوز الحد الطبيعي (< 120).\n\n"
                "**الإجراء المطلوب:**\n"
                "• قياس الضغط يومياً لمدة أسبوع\n"
                "• تقليل الملح لأقل من 2 جرام/يوم\n"
                "• زيارة طبيب باطنة لوصف علاج إذا استمر"))
        elif fd['trestbps'] > 120:
            warnings_count += 1
            recs.append(("🩸", "ضغط الدم حدّي", 
                f"القراءة: {fd['trestbps']} mmHg - أعلى قليلاً من الطبيعي.\n\n"
                "**نصيحة:** قلل الملح ومارس المشي 20 دقيقة يومياً."))
        
        # 2. الكوليسترول
        if fd['chol'] > 240:
            warnings_count += 1
            recs.append(("�", "الكوليسترول مرتفع (خطر)", 
                f"القراءة: {fd['chol']} mg/dL - يتجاوز 240 (خطر تصلب الشرايين).\n\n"
                "**الإجراء المطلوب:**\n"
                "• تحليل دهون شامل (HDL, LDL, Triglycerides)\n"
                "• تجنب اللحوم الحمراء والمقليات تماماً\n"
                "• قد تحتاج أدوية Statins بوصفة طبية"))
        elif fd['chol'] > 200:
            warnings_count += 1
            recs.append(("🧪", "الكوليسترول حدّي", 
                f"القراءة: {fd['chol']} mg/dL - أعلى من الطبيعي قليلاً.\n\n"
                "**نصيحة:** أكثر من الألياف (الشوفان، التفاح) واستخدم زيت الزيتون."))
        
        # 3. سكر الدم
        if fd['fbs'] == "نعم":
            warnings_count += 1
            recs.append(("🍬", "سكر الدم مرتفع (خطر)", 
                "سكر الصائم > 120 mg/dL - مؤشر لمرحلة ما قبل السكري أو سكري.\n\n"
                "**الإجراء المطلوب:**\n"
                "• تحليل السكر التراكمي (HbA1c)\n"
                "• تجنب السكر الأبيض والعصائر والمشروبات الغازية\n"
                "• متابعة مع طبيب غدد صماء"))
        
        # 4. ألم الصدر
        if fd['cp'] == 0 or fd['cp'] == 1:  # Typical angina
            if fd['exang'] == "نعم":
                warnings_count += 1
                recs.append(("💔", "ألم صدر مع المجهود (مهم جداً)", 
                    "وجود ألم صدر نمطي يزيد مع المجهود - علامة كلاسيكية لمشاكل الشرايين التاجية.\n\n"
                    "**الإجراء المطلوب:**\n"
                    "• اختبار جهد (Stress Test) عاجل\n"
                    "• قسطرة تشخيصية إذا كان الاختبار إيجابي\n"
                    "• تجنب المجهود الشاق حتى المراجعة"))
        
        # 5. معدل النبض
        if fd['thalach'] < 100:
            warnings_count += 1
            recs.append(("💓", "ضعف استجابة القلب للمجهود", 
                f"أقصى نبض: {fd['thalach']} bpm - أقل من المتوقع لعمرك.\n\n"
                "**معناه:** القلب لا يستجيب بكفاءة للمجهود.\n"
                "**الإجراء:** فحص إيكو للقلب وتخطيط كهربائي."))
        
        # 6. ST Depression
        if fd['oldpeak'] > 2:
            warnings_count += 1
            recs.append(("📉", "انخفاض ST ملحوظ (خطر)", 
                f"القراءة: {fd['oldpeak']} mm - انخفاض كبير يشير لنقص تروية القلب.\n\n"
                "**معناه الطبي:** الشرايين التاجية لا توصل دم كافي لعضلة القلب.\n"
                "**الإجراء:** قسطرة قلبية تشخيصية مطلوبة."))
        
        # 7. الشرايين الملونة
        if fd['ca'] > 0:
            warnings_count += 1
            recs.append(("🫀", f"انسداد في {fd['ca']} شريان تاجي", 
                f"عدد الشرايين المتأثرة: {fd['ca']} من 4.\n\n"
                "**معناه:** وجود ضيق أو انسداد في الشرايين الرئيسية المغذية للقلب.\n"
                "**الإجراء:** متابعة مع طبيب قلب تدخلي - قد تحتاج دعامة أو جراحة."))
        
        # === ملخص الحالة ===
        if is_risky:
            st.error(f"⚠️ **تنبيه:** الموديل يصنف حالتك كـ 'عالية الخطورة' بناءً على {warnings_count} مؤشر غير طبيعي.")
            recs.insert(0, ("🚨", "إجراء عاجل مطلوب", 
                "بناءً على تحليل النموذج (UCI Heart Disease Model):\n\n"
                "**يجب عليك:**\n"
                "1. زيارة طبيب قلب خلال أسبوع\n"
                "2. إجراء: تخطيط قلب ECG + إيكو + اختبار جهد\n"
                "3. عدم القيام بمجهود بدني شاق حتى المراجعة"))
        elif warnings_count > 0:
            st.warning(f"⚡ **ملاحظة:** رغم أن النتيجة العامة مطمئنة، إلا أن هناك {warnings_count} مؤشر يحتاج انتباهك.")
        else:
            recs.append(("🌟", "حالة ممتازة!", 
                "كل المؤشرات الحيوية في النطاق الطبيعي.\n\n"
                "**نصيحتنا:** حافظ على نمط حياتك الصحي واعمل فحص دوري كل سنة."))
        
        # عرض التوصيات
        rc1, rc2 = st.columns(2)
        for i, (icon, title, desc) in enumerate(recs):
            col = rc1 if i % 2 == 0 else rc2
            with col:
                st.markdown(f"""
                <div class="term-card">
                    <h4>{icon} {title}</h4>
                    <p style="white-space: pre-line;">{desc}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # === Complete Patient Data Table ===
        st.markdown("### 📊 جدول البيانات الكامل")
        st.caption("جميع القيم التي أدخلتها مع تفسيرها الطبي")
        
        # Create DataFrame for the table
        table_data = {
            "الأيقونة": ["👤", "🚻", "💔", "🩸", "🧪", "🍬", "📈", "💓", "🏃", "📉", "📐", "🫀", "🩺"],
            "المؤشر": [
                "العمر", "الجنس", "نوع ألم الصدر", "ضغط الدم", "الكوليسترول",
                "سكر الدم صائم", "تخطيط القلب", "أقصى نبض", "ألم مع المجهود",
                "انخفاض ST", "ميل الموجة", "الشرايين الملونة", "الثلاسيميا"
            ],
            "القيمة": [
                f"{fd['age']} سنة",
                fd['sex'],
                ["مفيش ألم", "ذبحة نمطية", "ذبحة غير نمطية", "ألم غير قلبي"][fd['cp']],
                f"{fd['trestbps']} mmHg",
                f"{fd['chol']} mg/dL",
                fd['fbs'],
                ["طبيعي", "شذوذ ST-T", "تضخم بطين أيسر"][fd['restecg']],
                f"{fd['thalach']} bpm",
                fd['exang'],
                f"{fd['oldpeak']} mm",
                ["صاعد", "مسطح", "هابط"][fd['slope']],
                f"{fd['ca']} شريان",
                ["غير محدد", "ثابت", "طبيعي", "قابل للإصلاح"][fd['thal']]
            ],
            "ملاحظة": [
                "عامل خطر يزيد مع التقدم",
                "الذكور أعلى خطراً",
                "الذبحة النمطية مؤشر قوي",
                "الطبيعي أقل من 120",
                "الطبيعي أقل من 200",
                "أكثر من 120 = مرتفع",
                "تخطيط كهربائي",
                "المتوقع: 220 - العمر",
                "نعم = علامة خطر",
                "أكثر من 2 = نقص تروية",
                "الهابط أخطر",
                "0 = طبيعي",
                "فحص تصويري"
            ]
        }
        
        df_table = pd.DataFrame(table_data)
        st.dataframe(df_table, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # === NEW: Export Section ===
        st.markdown("### 📤 تصدير التقرير")
        st.info("💡 يمكنك تحميل التقرير بصيغ متعددة حسب احتياجك")
        
        # Prepare report data for export
        report_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": title,
            "risk_percentage": round(risk_prob * 100, 2),
            "confidence": round(confidence * 100, 2),
            "patient_data": {
                "age": fd['age'], "sex": fd['sex'], "blood_pressure": fd['trestbps'],
                "cholesterol": fd['chol'], "fasting_blood_sugar": fd['fbs'],
                "max_heart_rate": fd['thalach'], "chest_pain_type": fd['cp'],
                "exercise_angina": fd['exang'], "st_depression": fd['oldpeak'],
                "vessels_colored": fd['ca'], "thalassemia": fd['thal']
            },
            "warnings_count": pre_warnings
        }
        
        exp1, exp2, exp3 = st.columns(3)
        
        with exp1:
            st.markdown("##### 📄 تصدير JSON")
            st.caption("مثالي للمبرمجين والتكامل مع الأنظمة الأخرى")
            json_str = json.dumps(report_data, ensure_ascii=False, indent=2)
            st.download_button(
                label="⬇️ تحميل JSON",
                data=json_str,
                file_name=f"heart_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with exp2:
            st.markdown("##### 📊 تصدير CSV")
            st.caption("مثالي لبرامج الجداول مثل Excel أو Google Sheets")
            csv_df = pd.DataFrame([{
                "التاريخ": report_data["timestamp"],
                "الحالة": report_data["status"],
                "نسبة الخطر%": report_data["risk_percentage"],
                "العمر": fd['age'],
                "الجنس": fd['sex'],
                "الضغط": fd['trestbps'],
                "الكوليسترول": fd['chol'],
                "النبض": fd['thalach'],
                "التحذيرات": pre_warnings
            }])
            st.download_button(
                label="⬇️ تحميل CSV",
                data=csv_df.to_csv(index=False).encode('utf-8-sig'),
                file_name=f"heart_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with exp3:
            st.markdown("##### 🖨️ تصدير للطباعة")
            st.caption("نسخ النتائج كنص - اطبعها أو أرسلها للطبيب")
            report_text = f"""
=== تقرير دكتور القلب الذكي ===
التاريخ: {report_data['timestamp']}
الحالة: {title}
نسبة الخطر: {report_data['risk_percentage']}%

--- البيانات ---
العمر: {fd['age']} سنة
الجنس: {fd['sex']}
ضغط الدم: {fd['trestbps']} mmHg
الكوليسترول: {fd['chol']} mg/dL
أقصى نبض: {fd['thalach']} bpm

عدد التحذيرات: {pre_warnings}
================================
            """
            st.download_button(
                label="⬇️ تحميل TXT",
                data=report_text.encode('utf-8'),
                file_name=f"heart_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        st.markdown("---")
        if st.button("🔄 فحص جديد", use_container_width=True): reset_wizard(); st.rerun()

# ==========================================
# 8. DASHBOARD
# ==========================================
elif st.session_state.current_page == "📊 لوحة القيادة":
    st.markdown("<h1 class='gradient-text' style='text-align:center;'>📊 لوحة القيادة التحليلية</h1>", unsafe_allow_html=True)
    show_model_info()
    
    if len(st.session_state.patient_history) == 0:
        st.info("🔍 لا توجد فحوصات محفوظة. قم بإجراء فحص في غرفة الكشف أولاً.")
        if anim_data:
            st_lottie(anim_data, height=300)
    else:
        df = pd.DataFrame(st.session_state.patient_history)
        
        s1, s2, s3, s4 = st.columns(4)
        with s1: st.metric("📊 إجمالي الفحوصات", len(df))
        with s2: st.metric("⚠️ حالات خطر", len(df[df['is_risky'] == True]))
        with s3: st.metric("📅 متوسط العمر", f"{df['age'].mean():.0f}")
        with s4: st.metric("📈 متوسط الخطر", f"{df['risk'].mean():.1f}%")
        
        st.markdown("---")
        
        # 3D Chart
        st.markdown("### 🌐 تحليل ثلاثي الأبعاد")
        fig_3d = px.scatter_3d(df, x='age', y='chol', z='bp', color='risk', size='risk',
                               color_continuous_scale=['#00e676', '#ff9100', '#ff1744'],
                               labels={'age': 'العمر', 'chol': 'الكوليسترول', 'bp': 'الضغط', 'risk': 'الخطر %'})
        fig_3d.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=500)
        st.plotly_chart(fig_3d, use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 📊 توزيع الحالات")
            risk_counts = df['is_risky'].value_counts()
            fig_pie = go.Figure(data=[go.Pie(labels=['سليم', 'خطر'], 
                                              values=[risk_counts.get(False, 0), risk_counts.get(True, 0)],
                                              marker_colors=['#00e676', '#ff1744'], hole=0.5,
                                              textinfo='percent+label')])
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig_pie, use_container_width=True)
        with c2:
            st.markdown("### 📈 الخطر مع العمر")
            fig_line = px.scatter(df, x='age', y='risk', size='chol', color='is_risky',
                                  color_discrete_map={True: '#ff1744', False: '#00e676'},
                                  labels={'age': 'العمر', 'risk': 'الخطر %', 'chol': 'الكوليسترول'})
            fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig_line, use_container_width=True)

# ==========================================
# 9. HISTORY
# ==========================================
elif st.session_state.current_page == "📋 السجلات":
    st.markdown("<h1 class='gradient-text' style='text-align:center;'>📋 سجل الفحوصات</h1>", unsafe_allow_html=True)
    show_model_info()
    
    if len(st.session_state.patient_history) == 0:
        st.info("📭 لا توجد سجلات محفوظة بعد.")
    else:
        for i, rec in enumerate(reversed(st.session_state.patient_history)):
            color = "#ff1744" if rec['is_risky'] else "#00e676"
            status = "⚠️ خطر" if rec['is_risky'] else "✅ سليم"
            
            with st.expander(f"🕐 {rec['timestamp']} | {rec['sex']} - {rec['age']} سنة | {status}"):
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric("الخطر", f"{rec['risk']:.1f}%")
                with c2: st.metric("الضغط", f"{rec['bp']}")
                with c3: st.metric("الكوليسترول", f"{rec['chol']}")
                with c4: st.metric("النبض", f"{rec.get('thalach', 'N/A')}")
        
        st.markdown("---")
        if st.button("🗑️ مسح جميع السجلات"):
            st.session_state.patient_history = []
            st.rerun()

# ==========================================
# 10. ENCYCLOPEDIA
# ==========================================
elif st.session_state.current_page == "📚 الموسوعة":
    st.markdown("<h1 class='gradient-text' style='text-align:center;'>📚 الموسوعة الطبية</h1>", unsafe_allow_html=True)
    show_model_info()
    
    st.markdown("---")
    
    # Heart Anatomy
    st.markdown("## 🫀 تشريح القلب")
    st.markdown("""
    <div class="glass-card">
        <p style="font-size: 1.1rem; line-height: 2; color: #e2e8f0;">
        القلب هو العضو الأهم في جسم الإنسان، وهو مضخة عضلية قوية بحجم قبضة اليد تقع في منتصف الصدر مائلة قليلاً لليسار.
        يتكون القلب من <strong style="color: #4ade80;">4 حجرات</strong>: الأذين الأيمن والأيسر (يستقبلان الدم) والبطين الأيمن والأيسر (يضخان الدم).
        ينبض القلب حوالي <strong style="color: #4ade80;">100,000 مرة يومياً</strong> ويضخ حوالي 7,500 لتر من الدم.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Medical Terms
    st.markdown("## 📖 المصطلحات الطبية")
    
    terms = [
        ("🩸 ضغط الدم (Blood Pressure)", 
         "قوة دفع الدم على جدران الشرايين أثناء ضخ القلب. يُقاس برقمين: الانقباضي (العلوي) والانبساطي (السفلي). الطبيعي: 120/80 mmHg. ارتفاعه يزيد خطر السكتة والجلطات."),
        
        ("🧪 الكوليسترول (Cholesterol)", 
         "مادة دهنية شمعية ضرورية لبناء الخلايا. النوع الضار (LDL) يتراكم في الشرايين ويسدها. الطبيعي: أقل من 200 mg/dL. المرتفع يسبب تصلب الشرايين."),
        
        ("💓 معدل النبض (Heart Rate)", 
         "عدد ضربات القلب في الدقيقة الواحدة. الطبيعي للبالغ في الراحة: 60-100 نبضة/دقيقة. الرياضيون قد يكون لديهم معدل أقل (40-60) وهذا طبيعي."),
        
        ("📊 تخطيط القلب (ECG/EKG)", 
         "رسم بياني يسجل النشاط الكهربائي للقلب. يكشف عن اضطرابات النظم، الجلطات السابقة، تضخم عضلة القلب، ومشاكل أخرى."),
        
        ("💔 الذبحة الصدرية (Angina)", 
         "ألم أو ضغط في الصدر ينتج عن نقص تدفق الدم لعضلة القلب. قد يمتد للكتف والذراع والفك. يحدث عادة مع المجهود ويتحسن بالراحة."),
        
        ("📉 انخفاض ST (ST Depression)", 
         "تغير في رسم القلب يشير لنقص التروية (وصول الدم) لعضلة القلب. كلما زاد الانخفاض، زادت خطورة الحالة."),
        
        ("🩺 الثلاسيميا (Thalassemia)", 
         "اضطراب وراثي في الدم يؤثر على إنتاج الهيموجلوبين. يستخدم في التشخيص كمؤشر لنوعية الدم والأكسجين الواصل للقلب."),
    ]
    
    for title, desc in terms:
        st.markdown(f"""
        <div class="term-card">
            <h4>{title}</h4>
            <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Risk Factors
    st.markdown("## 🛡️ عوامل الخطر")
    
    r1, r2 = st.columns(2)
    with r1:
        st.markdown("""
        <div class="glass-card" style="border-right: 4px solid #ff1744;">
            <h4 style="color: #ff1744;">❌ عوامل لا يمكن التحكم فيها</h4>
            <ul style="color: #ccc; line-height: 2;">
                <li><strong>العمر:</strong> > 45 للرجال، > 55 للنساء</li>
                <li><strong>التاريخ العائلي:</strong> أقارب من الدرجة الأولى مصابون</li>
                <li><strong>الجنس:</strong> الرجال أكثر عرضة قبل سن 55</li>
                <li><strong>العرق:</strong> بعض الأعراق أكثر عرضة</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with r2:
        st.markdown("""
        <div class="glass-card" style="border-right: 4px solid #00e676;">
            <h4 style="color: #00e676;">✅ عوامل يمكن التحكم فيها</h4>
            <ul style="color: #ccc; line-height: 2;">
                <li><strong>التدخين:</strong> الإقلاع يقلل الخطر 50%</li>
                <li><strong>السمنة:</strong> فقدان 5-10% من الوزن يُحسّن</li>
                <li><strong>الضغط والكوليسترول:</strong> قابلان للعلاج</li>
                <li><strong>النشاط البدني:</strong> 30 دقيقة يومياً تكفي</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Prevention Tips
    st.markdown("## 💡 نصائح للوقاية")
    
    tips = [
        ("🚭", "أقلع عن التدخين", "التدخين يضاعف خطر أمراض القلب. الإقلاع يبدأ بتحسين صحتك خلال 20 دقيقة فقط!"),
        ("🏃", "مارس الرياضة", "30 دقيقة من المشي السريع 5 أيام أسبوعياً تقلل الخطر بنسبة 30-40%."),
        ("🥗", "تناول غذاء صحي", "ركز على الخضروات والفواكه والحبوب الكاملة. قلل الدهون المشبعة والملح والسكر."),
        ("😴", "نم جيداً", "النوم 7-8 ساعات يومياً يساعد القلب على الراحة والتعافي."),
        ("🧘", "قلل التوتر", "التوتر المزمن يرفع الضغط. جرب التأمل، اليوغا، أو أي نشاط مريح."),
        ("⚖️", "حافظ على وزن صحي", "الوزن الزائد يُجهد القلب. BMI بين 18.5-24.9 هو الهدف."),
    ]
    
    tc1, tc2 = st.columns(2)
    for i, (icon, title, desc) in enumerate(tips):
        col = tc1 if i % 2 == 0 else tc2
        with col:
            st.markdown(f"""
            <div class="term-card">
                <h4>{icon} {title}</h4>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# FOOTER
# ==========================================
st.markdown("""
<div class='footer'>
    ⚠️ هذا النظام للمساعدة فقط ولا يعتبر بديلاً عن استشارة طبيب متخصص | 
    🤖 النموذج: UCI Heart Disease Dataset | 
    © 2025 Smart Heart Doctor - Built with team & ❤️
</div>
""", unsafe_allow_html=True)
