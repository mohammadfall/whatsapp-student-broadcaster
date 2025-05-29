import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# إعداد الاتصال بـ Google Sheets باستخدام secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_info, scope)
client = gspread.authorize(creds)

# ID الخاص بملف Google Sheet
sheet_id = "1gin23ojAkaWviu7zy5wVqMqR2kX1xQDTz2EkQsepdQo"

# الربط بين المادة واسم الشيت الداخلي
worksheet_map = {
    "فسيولوجي": "physiology_students",
    "فارما 1": "pharma one_students",
    "فارما 3": "pharma three_students",
    "باثولوجي": "patho_students"
}

# واجهة Streamlit
st.set_page_config(page_title="إرسال رسالة واتساب للطلاب", layout="centered")
st.title("📖 إرسال رسالة واتساب للطلاب")
st.markdown("اختر المادة، اكتب الرسالة، وسيتم توليد الطلب تلقائيًا 🔔")

# اختيار المادة
selected_subject = st.selectbox("اختر المادة", list(worksheet_map.keys()))

# قراءة بيانات الطلاب
worksheet = client.open_by_key(sheet_id).worksheet(worksheet_map[selected_subject])
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# إدخال الرسالة
message = st.text_area("✏️ اكتب نص الرسالة (يمكنك استخدام {name} لتخصيص الرسالة):", "مرحبًا {name}، نزلت المحاضرة الجديدة على المنصة 🎓")

# عرض عدد الطلاب
st.markdown(f"### 👥 عدد الطلاب: {len(df)}")
st.dataframe(df[["الاسم", "الرقم"]], use_container_width=True)

# زر إرسال فعلي (يكتب في شيت send_log)
if st.button("🚀 إرسال الرسالة"):
    try:
        log_sheet = client.open_by_key(sheet_id).worksheet("send_log")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_sheet.append_row([worksheet_map[selected_subject], message, "pending", now])
        st.success("📤 تم تسجيل الطلب في الشيت بنجاح، البوت سيبدأ الإرسال تلقائيًا")
    except Exception as e:
        st.error(f"❌ فشل تسجيل الطلب: {e}")
