import numpy as np
import pandas as pd
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS
from pyngrok import ngrok, conf
import threading

# --- 1. إعداد التوكن الخاص بـ ngrok ---
# (يفضل متشاركش التوكن ده مع حد غريب، بس لصاحبك تمام)
conf.get_default().auth_token = "36M1S8Xv3ugMVxy3pNK1ZTmSc4Q_Lb2V8MNgHDHk5fq7xP44"

# --- 2. إعداد تطبيق Flask ---
app = Flask(__name__) # تصحيح الاسم
CORS(app) # للسماح للموقع الخارجي بالاتصال بالسيرفر

# --- 3. تحميل الموديل والـ Scaler (أهم خطوة) ---
try:
    print("⏳ جاري تحميل الموديل والملفات...")
    model = joblib.load('heart_disease_model.pkl')
    scaler = joblib.load('scaler.pkl')
    print("✅ تم تحميل الموديل والـ Scaler بنجاح!")
except Exception as e:
    print(f"❌ مصيبة! مش لاقي الملفات. تأكد إن ملفات .pkl جنب ملف الكود.\nالخطأ: {e}")
    # هنا بنوقف الكود عشان ميكملش غلط
    exit()

# أسماء الأعمدة (عشان الـ Scaler يفهم الترتيب)
columns = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 
           'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']

@app.route('/')
def home():
    return "<h1>Server is Running! 🚀</h1><p>Send POST request to /diagnose</p>"

@app.route('/diagnose', methods=['POST'])
def diagnose():
    try:
        # 1. استقبال البيانات
        data = request.json
        features_list = data.get('features', [])
        
        print(f"📩 استلمت بيانات: {features_list}")

        # التأكد من عدد المدخلات
        if len(features_list) != 13:
            return jsonify({"status": "error", "message": "يجب إدخال 13 قيمة بالضبط"}), 400

        # 2. تحويل البيانات وتجهيزها (Scaling)
        # لازم نحولها لـ DataFrame بنفس أسماء الأعمدة عشان الـ Scaler يشتغل صح
        input_df = pd.DataFrame([features_list], columns=columns)
        
        # 🔥 الخطوة السحرية: توحيد المقاييس
        final_features = scaler.transform(input_df)

        # 3. التنبؤ (Prediction)
        prediction = model.predict(final_features)
        probability = model.predict_proba(final_features)

        # تجهيز النتيجة
        # (في داتاسيت Kaggle: 0=مريض، 1=سليم - حسب ما اكتشفنا سابقاً)
        # سنقوم بعكس الشرط ليتوافق مع المنطق الطبي (Risk vs Healthy)
        if prediction[0] == 0: 
            diagnosis_text = "مريض (High Risk)"
            confidence = probability[0][0] * 100 # نسبة احتمال المرض
            is_sick = True
        else:
            diagnosis_text = "سليم (Healthy)"
            confidence = probability[0][1] * 100 # نسبة احتمال السلامة
            is_sick = False

        # 4. الرد على صاحبك
        response = {
            "status": "success",
            "diagnosis": diagnosis_text,
            "certainty_percentage": round(confidence, 2),
            "is_heart_disease_detected": is_sick
        }
        
        print(f"📤 النتيجة المرسلة: {diagnosis_text} ({confidence:.2f}%)")
        return jsonify(response)

    except Exception as e:
        print(f"❌ خطأ أثناء المعالجة: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- تشغيل السيرفر ---
if __name__ == "__main__":
    # إغلاق أي اتصال قديم لـ ngrok عشان ميحصلش تعارض
    ngrok.kill()
    
    # فتح نفق جديد
    public_url = ngrok.connect(5000).public_url
    print(f"\n🚀 ===================================================")
    print(f"🔗 ابعت اللينك ده لصاحبك: {public_url}")
    print(f"🔗 واللينك الكامل للـ API هو: {public_url}/diagnose")
    print(f"===================================================\n")
    
    app.run(port=5000)