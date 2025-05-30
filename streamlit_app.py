import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import datetime

# 1. إعداد الاتصال بـ Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_info, scope)
client = gspread.authorize(creds)

# 2. حدد اسم الشيت
SHEET_ID = "1gin23ojAkaWviu7zy5wVqMqR2kX1xQDTz2EkQsepdQo"
spreadsheet = client.open_by_key(SHEET_ID)

# 3. واجهة Streamlit
st.title("📲 تطبيق إرسال الرسائل على واتساب")

# 3.1 اختيار المادة (اسم الورقة)
sheet_names = [s.title for s in spreadsheet.worksheets() if s.title != "send_log"]
subject = st.selectbox("اختر المادة:", sheet_names)

# 3.2 إدخال الرسالة
default_message = "مرحبًا {name}، تم رفع المحاضرة الجديدة ✅"
message_template = st.text_area("✉️ الرسالة (استخدم {name} داخل النص):", value=default_message)

# 3.3 عرض الطلاب
worksheet = spreadsheet.worksheet(subject)
data = worksheet.get_all_records()
df = pd.DataFrame(data)

st.subheader("👥 قائمة الطلاب:")
st.dataframe(df)

# 3.4 زر الإرسال (سيتم التفعيل لاحقًا)
if st.button("🚀 إرسال الرسائل"):
    st.success("✨ تم تحضير الرسائل (الخطوة التالية: إرسال واتساب سيتم برمجته)")

