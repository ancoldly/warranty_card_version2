import streamlit as st
from docxtpl import DocxTemplate
from jinja2 import Environment
import pytz
from datetime import datetime
import tempfile
from docx2pdf import convert
import base64
import os
import pythoncom

st.set_page_config(page_title="Phiếu bảo hành - Tuấn Anh", layout="centered")

st.title("📄 Phiếu Bảo Hành - Cửa hàng điện thoại Tuấn Anh")

# Khởi tạo session_state để lưu file
if "docx_file" not in st.session_state:
    st.session_state.docx_file = None
if "pdf_file" not in st.session_state:
    st.session_state.pdf_file = None

# Nhập thông tin khách hàng
st.subheader("Thông tin khách hàng")
customer = st.text_input("👤 Tên khách hàng")
phone = st.text_input("📞 Số điện thoại")
address = st.text_input("🏠 Địa chỉ")

# Ngày giờ
tz = pytz.timezone('Asia/Ho_Chi_Minh')
now = datetime.now(tz)
date = now.strftime("%d/%m/%Y %H:%M:%S")

# Thông tin sản phẩm
st.subheader("Thông tin sản phẩm")
info_product = st.text_area("📱 Tên hàng hóa (có thể xuống dòng)", height=150)
quantity = st.number_input("Số lượng", min_value=1, step=1)
price = st.number_input("Đơn giá", min_value=0.0, step=1000.0, format="%.0f")
discount = st.number_input("Chiết khấu", min_value=0.0, step=1000.0, format="%.0f")
vat = st.number_input("VAT", min_value=0.0, step=1000.0, format="%.0f")

# Tính tổng
subtotal = price * quantity
total = subtotal - discount + vat

# Filter nl2br (nếu dùng trong template)
def nl2br(value):
    if not value:
        return ""
    return value.replace('\n', '\n')

jinja_env = Environment()
jinja_env.filters['nl2br'] = nl2br

# Nút tạo phiếu
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
        st.session_state.docx_file = tmp_docx.name  # Lưu vào session_state

    # Chuyển sang PDF
    pdf_path = tmp_docx.name.replace(".docx", ".pdf")
    try:
        pythoncom.CoInitialize()
        convert(tmp_docx.name, pdf_path)
        pythoncom.CoUninitialize()
        st.session_state.pdf_file = pdf_path  # Lưu PDF vào session_state
        pdf_available = True
    except Exception as e:
        st.error(f"Lỗi khi chuyển sang PDF: {e}")
        pdf_available = False

    st.success("✅ Tạo phiếu thành công!")

# --- Hiển thị nút tải và PDF dựa trên session_state ---

# Tải DOCX
if st.session_state.docx_file and os.path.exists(st.session_state.docx_file):
    with open(st.session_state.docx_file, "rb") as file_docx:
        st.download_button(
            label="⬇️ Tải xuống phiếu (DOCX)",
            data=file_docx,
            file_name=f"{phone}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

# Tải PDF + hiển thị PDF
if st.session_state.pdf_file and os.path.exists(st.session_state.pdf_file):
    with open(st.session_state.pdf_file, "rb") as file_pdf:
        st.download_button(
            label="⬇️ Tải xuống phiếu (PDF)",
            data=file_pdf,
            file_name=f"{phone}.pdf",
            mime="application/pdf"
        )

    # Hiển thị PDF trong iframe
    with open(st.session_state.pdf_file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
