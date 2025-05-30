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
worksheet = spreadsheet.worksheet(selected_sheet)
students_data = worksheet.get_all_records()

# تصفية الطلاب (فقط اللي ما تم الإرسال إلهم)
students_df = pd.DataFrame(students_data)
students_df = students_df[students_df["تم الارسال؟"] != "✅"].reset_index(drop=True)

# عرض الطلاب
with st.expander("👥 عرض الطلاب المستهدفين (فقط اللي ما تم الإرسال لهم)"):
    st.dataframe(students_df)

# كتابة الرسالة
message_template = st.text_area("✉️ نص الرسالة:", "مرحبًا {الاسم}، تم رفع المحاضرة الجديدة على المنصة 🎓")

# معاينة الرسائل
st.subheader("📋 معاينة الرسائل:")
preview = []
for _, row in students_df.iterrows():
    preview_message = message_template.replace("{الاسم}", row["الاسم"])
    preview.append(f"{row['الاسم']} ➤ {preview_message}")
st.code("\n".join(preview), language="markdown")

# زر الإرسال
if st.button("🚀 إرسال الطلبات للبوت"):
    log_ws = spreadsheet.worksheet("send_log")
    for i, row in students_df.iterrows():
        name = row["الاسم"]
        phone = str(row["الرقم"])
        if not phone.startswith("962"):
            phone = "962" + phone.lstrip("0")

        message = message_template.replace("{الاسم}", name)

        # حفظ في سجل send_log
        log_ws.append_row([
            selected_sheet,
            name,
            phone,
            message,
            "pending",
            str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ])

        # تحديث خانة "تم الارسال؟" لحالة مؤقتة
        worksheet.update_cell(i + 2, 3, "🚀 جاري الإرسال")  # +2 لأن أول صف header و +1 للتحويل من index إلى row

    st.success("✅ تم إرسال الطلبات للبوت بنجاح! سيتم الإرسال تلقائيًا ✨")
