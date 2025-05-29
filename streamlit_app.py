import streamlit as st
import pandas as pd
import gspread
import json
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# إعداد الوصول لـ Google Sheets باستخدام Streamlit Secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_info, scope)
client = gspread.authorize(creds)

# تحميل الشيت الرئيسي
SHEET_ID = "1gin23ojAkaWviu7zy5wVqMqR2kX1xQDTz2EkQsepdQo"
spreadsheet = client.open_by_key(SHEET_ID)
sheet_names = [sheet.title for sheet in spreadsheet.worksheets() if sheet.title != "send_log"]

st.title("📬 منصة إرسال رسائل واتساب للطلاب")

# اختيار الشيت (المادة)
selected_sheet = st.selectbox("اختر الشيت (المادة):", sheet_names)
students_df = pd.DataFrame(spreadsheet.worksheet(selected_sheet).get_all_records())

# عرض الطلاب
with st.expander("👥 عرض أسماء الطلاب"):
    st.dataframe(students_df)

# كتابة الرسالة
message_template = st.text_area("✉️ نص الرسالة:", "مرحبًا {الاسم}، تم رفع المحاضرة الجديدة على المنصة 🎓")

# إرسال الطلبات للبوت
if st.button("🚀 إرسال الرسالة"):
    log_ws = spreadsheet.worksheet("send_log")
    for _, row in students_df.iterrows():
        message = message_template.replace("{الاسم}", row["الاسم"])
        log_ws.append_row([
            selected_sheet,
            message,
            "pending",
            str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ])
    st.success("✅ تم إرسال الطلبات للبوت بنجاح! سيتم الإرسال تلقائيًا ✨")
