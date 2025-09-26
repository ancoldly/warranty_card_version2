import streamlit as st
from docxtpl import DocxTemplate
from jinja2 import Environment
import pytz
from datetime import datetime
import tempfile
import os

st.set_page_config(page_title="Phiếu bảo hành - Tuấn Anh", layout="centered")

st.title("📄 Phiếu Bảo Hành - Cửa hàng điện thoại Tuấn Anh")

# Khởi tạo session_state để lưu file
if "docx_file" not in st.session_state:
    st.session_state.docx_file = None

# --- Nhập thông tin khách hàng ---
st.subheader("Thông tin khách hàng")
customer = st.text_input("👤 Tên khách hàng")
phone = st.text_input("📞 Số điện thoại")
address = st.text_input("🏠 Địa chỉ")

# --- Ngày giờ ---
tz = pytz.timezone('Asia/Ho_Chi_Minh')
now = datetime.now(tz)
date = now.strftime("%d/%m/%Y %H:%M:%S")

# --- Thông tin sản phẩm ---
st.subheader("Thông tin sản phẩm")
info_product = st.text_area("📱 Tên hàng hóa (có thể xuống dòng)", height=150)
quantity = st.number_input("Số lượng", min_value=1, step=1)
price = st.number_input("Đơn giá", min_value=0.0, step=1000.0, format="%.0f")
discount = st.number_input("Chiết khấu", min_value=0.0, step=1000.0, format="%.0f")
vat = st.number_input("VAT", min_value=0.0, step=1000.0, format="%.0f")

# --- Tính tổng ---
subtotal = price * quantity
total = subtotal - discount + vat

# --- Filter nl2br (dùng trong template nếu cần xuống dòng) ---
def nl2br(value):
    if not value:
        return ""
    return value.replace('\n', '\n')

jinja_env = Environment()
jinja_env.filters['nl2br'] = nl2br

# --- Nút tạo phiếu ---
if st.button("📄 Tạo phiếu bảo hành"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx:
        doc = DocxTemplate("template_with_placeholders.docx")  # file template
        context = {
            "date": date,
            "customer": customer,
            "phone": phone,
            "address": address,
            "info_product": info_product,
            "quantity": quantity,
            "price": f"{price:,.0f} VNĐ",
            "discount": f"{discount:,.0f} VNĐ",
            "vat": f"{vat:,.0f} VNĐ",
            "total": f"{total:,.0f} VNĐ",
            "stt": 1
        }
        doc.render(context, jinja_env=jinja_env)
        doc.save(tmp_docx.name)
        st.session_state.docx_file = tmp_docx.name  # lưu file DOCX vào session_state

    st.success("✅ Tạo phiếu thành công!")

# --- Hiển thị nút tải DOCX ---
if st.session_state.docx_file and os.path.exists(st.session_state.docx_file):
    with open(st.session_state.docx_file, "rb") as file_docx:
        st.download_button(
            label="⬇️ Tải xuống phiếu (DOCX)",
            data=file_docx,
            file_name=f"{phone if phone else 'phieu_bao_hanh'}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
