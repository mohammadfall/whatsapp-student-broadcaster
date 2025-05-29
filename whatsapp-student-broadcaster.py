import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# إعداد الاتصال بـ Google Sheets باستخدام secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_info, scope)
client = gspread.authorize(creds)

# معلومات الشيت
sheet_name = "whatsapp-student-broadcaster"  # اسم Google Sheet

# الربط بين المادة واسم الشيت الداخلي (worksheet)
worksheet_map = {
    "فسيولوجي": "physiology_students",
    "فارما 1": "pharma one_students",
    "فارما 3": "pharma three_students",
    "باثولوجي": "patho_students"
}

# واجهة Streamlit
st.set_page_config(page_title="إرسال رسالة واتساب للطلاب", layout="centered")
st.title("📖 إرسال رسالة واتساب للطلاب")
st.markdown("اختر المادة، اكتب الرسالة، واضغط إرسال 🔔")

# اختيار المادة
selected_subject = st.selectbox("اختر المادة", list(worksheet_map.keys()))

# قراءة البيانات من الشيت
worksheet = client.open(sheet_name).worksheet(worksheet_map[selected_subject])
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# إدخال الرسالة
message = st.text_area("✏️ اكتب نص الرسالة:", "نزلت المحاضرة الجديدة! شغّلها على المنصة 💻")

# عرض عدد الطلاب وجدولهم
st.markdown(f"عدد الطلاب: {len(df)}")
st.dataframe(df[["الاسم", "الرقم"]], use_container_width=True)

# زر إرسال (محاكاة فقط)
if st.button("🚀 إرسال الرسالة"):
    for _, row in df.iterrows():
        name = row["الاسم"]
        phone = row["الرقم"]
        st.success(f"📤 تم تجهيز الرسالة لـ {name} ({phone})")
