import streamlit as st
import pandas as pd

# إعداد صفحة التطبيق
st.set_page_config(page_title="إرسال رسالة واتساب للطلاب", layout="centered")

# العنوان الرئيسي
st.title("📖 إرسال رسالة واتساب للطلاب")
st.markdown("اختر المادة، اكتب الرسالة، واضغط إرسال 🔔")

# بيانات الطلاب - مثال (تقدر تغيرها بربط خارجي)
data = {
    "الاسم": ["محمد", "سارة", "أحمد"],
    "الرقم": ["0791111111", "0782222222", "0773333333"],
    "المادة": ["فسيولوجي", "فارما", "فسيولوجي"]
}
df = pd.DataFrame(data)

# اختيار المادة
materials = df["المادة"].unique().tolist()
selected_material = st.selectbox("اختر المادة", materials)

# إدخال نص الرسالة
message = st.text_area("اكتب نص الرسالة", "نزلت المحاضرة الجديدة! شغفها على المنصة")

# عرض الطلاب المستهدفين حسب المادة
target_students = df[df["المادة"] == selected_material]
st.markdown(f"عدد الطلاب: {len(target_students)}")

# عرض جدول الطلاب
st.dataframe(
    target_students[["الاسم", "الرقم"]].reset_index(drop=True),
    use_container_width=True
)

# زر الإرسال
if st.button("🚀 إرسال الرسالة"):
    for _, row in target_students.iterrows():
        name = row["الاسم"]
        phone = row["الرقم"]
        # مكان تنفيذ عملية الإرسال لاحقًا
        st.success(f"✅ تم تجهيز رسالة لـ {name} على الرقم {phone}")
