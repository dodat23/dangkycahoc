import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials
import traceback

SHEET_NAME = "QL_Thanh_Nhac"

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Hệ Thống Đăng Ký Lớp Thanh Nhạc",
    page_icon="🎵",
    layout="centered"
)

@st.cache_resource
def ket_noi_google_sheets():
    try:
        scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Đọc trực tiếp từ st.secrets của Streamlit Cloud
        secrets_dict = dict(st.secrets["gpex"]) # Hoặc tên bảng mật khẩu bạn đặt trong Streamlit
        creds = Credentials.from_service_account_info(secrets_dict, scopes=scopes)
        
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        return sheet
    except Exception as e:
        st.error(f"Lỗi kết nối Google Sheets chi tiết: {str(e)}")
        st.code(traceback.format_exc())
        return None

sheet = ket_noi_google_sheets()

# CSS giao diện
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    .stApp {
        background: linear-gradient(135deg, #fdf2f8 0%, #fff1f2 50%, #fae8ff 100%);
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #1f2937;
    }
    @keyframes floatNotes {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-6px) rotate(5deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }
    .music-header {
        text-align: center;
        animation: floatNotes 4s ease-in-out infinite;
    }
    .stTextInput > div > div > input {
        background-color: #ffffff;
        color: #1f2937;
        border: 1.5px solid #f472b6;
        border-radius: 14px;
        padding: 12px 16px;
        box-shadow: 0 4px 10px rgba(244, 114, 182, 0.08);
        font-size: 16px;
    }
    div.stButton > button {
        border-radius: 14px;
        font-weight: 700;
        background: linear-gradient(135deg, #ec4899 0%, #be185d 100%);
        color: white;
        border: none;
        width: 100%;
        padding: 12px 20px;
        box-shadow: 0 8px 20px rgba(236, 72, 153, 0.4);
        cursor: pointer;
    }
    div.stButton > button:hover {
        transform: translateY(-3px);
        background: linear-gradient(135deg, #db2777 0%, #9d174d 100%);
    }
    .card {
        padding: 24px;
        border-radius: 22px;
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(12px);
        border: 1.5px solid rgba(244, 114, 182, 0.4);
        box-shadow: 0 12px 30px -6px rgba(244, 114, 182, 0.15);
        margin-bottom: 18px;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #f472b6 0%, #be185d 100%);
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

def lay_ngay_thu_7_gan_nhat():
    ngay_hien_tai = datetime.now()
    so_ngay_den_thu_7 = (5 - ngay_hien_tai.weekday()) % 7
    thu_7 = ngay_hien_tai + timedelta(days=so_ngay_den_thu_7)
    return thu_7.strftime("%d/%m/%Y")

def tai_du_lieu_sheets():
    if sheet is None:
        return {"Ca 1 (8:00 - 9:45)": [], "Ca 2 (9:45 - 11:30)": []}
    try:
        data_rows = sheet.get_all_records()
        ca1 = []
        ca2 = []
        for row in data_rows:
            ten = str(row.get("HoVaTen", "")).strip()
            ca = str(row.get("CaHoc", "")).strip()
            if ten:
                if "Ca 1" in ca:
                    ca1.append(ten)
                elif "Ca 2" in ca:
                    ca2.append(ten)
        return {
            "Ca 1 (8:00 - 9:45)": ca1,
            "Ca 2 (9:45 - 11:30)": ca2
        }
    except Exception:
        sheet.clear()
        sheet.append_row(["HoVaTen", "CaHoc"])
        return {"Ca 1 (8:00 - 9:45)": [], "Ca 2 (9:45 - 11:30)": []}

def cap_nhat_len_sheets(dang_ky_dict):
    if sheet is None:
        return
    sheet.clear()
    sheet.append_row(["HoVaTen", "CaHoc"])
    rows_to_add = []
    for hv in dang_ky_dict["Ca 1 (8:00 - 9:45)"]:
        rows_to_add.append([hv, "Ca 1 (8:00 - 9:45)"])
    for hv in dang_ky_dict["Ca 2 (9:45 - 11:30)"]:
        rows_to_add.append([hv, "Ca 2 (9:45 - 11:30)"])
    if rows_to_add:
        sheet.append_rows(rows_to_add)

danh_sach_dang_ky = tai_du_lieu_sheets()
ngay_thu_7 = lay_ngay_thu_7_gan_nhat()

st.markdown("""
    <div class="music-header">
        <h1 style='color: #be185d; font-weight: 800; margin-bottom: 0;'>
            🎶 Đăng ký ca học thanh nhạc 🎤
        </h1>
        <p style='color: #6b7280; font-size: 17px; margin-top: 5px;'>
            🎵 <i>Luyện thanh thăng hoa cùng Ms Gemma</i> 🎵
        </p>
    </div>
""", unsafe_allow_html=True)

st.info(f"📅 **Lịch hòa ca Thứ 7 tuần này:** `{ngay_thu_7}` (Thời gian: **8:00 - 11:30**)")

tong_so_hoc_vien = len(danh_sach_dang_ky["Ca 1 (8:00 - 9:45)"]) + len(danh_sach_dang_ky["Ca 2 (9:45 - 11:30)"])
st.markdown(f"🎧 **Tổng số giọng ca đã đăng ký tuần này:** `{tong_so_hoc_vien}/10 chỗ`")
st.progress(tong_so_hoc_vien / 10)

st.write("")

col1, col2 = st.columns(2)

with col1:
    siso_1 = len(danh_sach_dang_ky["Ca 1 (8:00 - 9:45)"])
    st.markdown(f"""
        <div class="card">
            <h4>🎼 Ca 1 (8:00 - 9:45)</h4>
            <p style="color: #4b5563; font-size: 14px;">Trạng thái: <b style="color: #be185d;">{siso_1}/5</b> giọng ca đã nhận</p>
            <hr style="border-color: #fbcfe8; margin: 8px 0 12px 0;">
    """, unsafe_allow_html=True)
    if siso_1 == 0:
        st.caption("Chưa có học viên đăng ký")
    else:
        for idx, hv in enumerate(danh_sach_dang_ky["Ca 1 (8:00 - 9:45)"], 1):
            st.write(f"**{idx}.** 🎤 {hv}")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    siso_2 = len(danh_sach_dang_ky["Ca 2 (9:45 - 11:30)"])
    st.markdown(f"""
        <div class="card">
            <h4>🎹 Ca 2 (9:45 - 11:30)</h4>
            <p style="color: #4b5563; font-size: 14px;">Trạng thái: <b style="color: #be185d;">{siso_2}/5</b> giọng ca đã nhận</p>
            <hr style="border-color: #fbcfe8; margin: 8px 0 12px 0;">
    """, unsafe_allow_html=True)
    if siso_2 == 0:
        st.caption("Chưa có học viên đăng ký")
    else:
        for idx, hv in enumerate(danh_sach_dang_ky["Ca 2 (9:45 - 11:30)"], 1):
            st.write(f"**{idx}.** 🎶 {hv}")
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()
st.subheader("✍️ Đăng Ký Luyện Thanh")

if tong_so_hoc_vien < 10:
    with st.container():
        if 'clear_input' in st.session_state and st.session_state['clear_input']:
            st.session_state['ten_input'] = ""
            st.session_state['clear_input'] = False

        ten_hoc_vien = st.text_input("Nhập tên", key="ten_input", label_visibility="collapsed", autocomplete="off")
        
        cac_ca = list(danh_sach_dang_ky.keys())
        if len(danh_sach_dang_ky[cac_ca[0]]) >= 5:
            st.session_state["ca_dang_ky"] = cac_ca[1]

        ca_duoc_chon = st.selectbox(
            "Chọn ca học",
            options=cac_ca,
            format_func=lambda ca: f"{ca} - {len(danh_sach_dang_ky[ca])}/5 học viên",
            key="ca_dang_ky"
        )

        if st.button("🎶 Xác Nhận Đăng Ký Ca Học"):
            ten_chuan_hoa = ten_hoc_vien.strip()
            if not ten_chuan_hoa:
                st.caption("Vui lòng nhập họ và tên của bạn trước khi đăng ký.")
            else:
                da_dang_ky = False
                ca_cu = ""
                for ca, ds in danh_sach_dang_ky.items():
                    if ten_chuan_hoa in ds:
                        da_dang_ky = True
                        ca_cu = ca
                        break
                
                if da_dang_ky:
                    st.caption(f"Bạn {ten_chuan_hoa} đã đăng ký ca {ca_cu} rồi. Mỗi người chỉ được chọn một ca.")
                else:
                    if len(danh_sach_dang_ky[ca_duoc_chon]) >= 5:
                        st.caption(f"Ca {ca_duoc_chon} đã đủ 5/5 học viên. Vui lòng chọn ca còn chỗ.")
                    else:
                        danh_sach_dang_ky[ca_duoc_chon].append(ten_chuan_hoa)
                        cap_nhat_len_sheets(danh_sach_dang_ky)
                        st.session_state['clear_input'] = True
                        st.rerun()

st.divider()
st.subheader("🔍 Tra Cứu Ca Học")
with st.container():
    if 'clear_check' in st.session_state and st.session_state['clear_check']:
        st.session_state['input_check'] = ""
        st.session_state['clear_check'] = False

    ten_kiem_tra = st.text_input("Tra cứu", key="input_check", label_visibility="collapsed", autocomplete="off")
    
    if st.button("🎵 Tra Cứu Ca Học"):
        st.session_state['search_name'] = ten_kiem_tra.strip()

if 'search_name' in st.session_state and st.session_state['search_name']:
    name_to_find = st.session_state['search_name']
    tim_thay = False
    for ca, ds in danh_sach_dang_ky.items():
        if name_to_find in ds:
            tim_thay = True
            st.markdown(f"Giọng ca **{name_to_find}** hiện đang luyện tập ở **{ca}**.")
            
            if st.button(f"❌ Xác nhận HỦY lịch của {name_to_find}", key="btn_huy_lich_action"):
                danh_sach_dang_ky[ca].remove(name_to_find)
                cap_nhat_len_sheets(danh_sach_dang_ky)
                del st.session_state['search_name']
                st.session_state['clear_check'] = True
                st.rerun()
            break
            
    if not tim_thay:
        st.caption(f"Không tìm thấy dữ liệu đăng ký cho tên {name_to_find} trong tuần này.")

if tong_so_hoc_vien == 10:
    st.divider()
    st.success("📊 **Bảng Sheet tổng hợp hòa ca chính thức được mở:**")
    st.subheader("📋 Danh Sách Học Từng Ca")
    
    sheet_col1, sheet_col2 = st.columns(2)

    with sheet_col1:
        st.markdown("#### **🎼 Ca 1 (8:00 - 9:45)**")
        ds_ca1 = danh_sach_dang_ky["Ca 1 (8:00 - 9:45)"]
        df_ca1 = pd.DataFrame({
            "STT": range(1, len(ds_ca1) + 1),
            "Họ và Tên": ds_ca1,
            "Trạng thái": ["Đã xác nhận🎤"] * len(ds_ca1)
        })
        st.dataframe(df_ca1, use_container_width=True, hide_index=True)

    with sheet_col2:
        st.markdown("#### **🎹 Ca 2 (9:45 - 11:30)**")
        ds_ca2 = danh_sach_dang_ky["Ca 2 (9:45 - 11:30)"]
        df_ca2 = pd.DataFrame({
            "STT": range(1, len(ds_ca2) + 1),
            "Họ và Tên": ds_ca2,
            "Trạng thái": ["Đã xác nhận🎶"] * len(ds_ca2)
        })
        st.dataframe(df_ca2, use_container_width=True, hide_index=True)

    danh_sach_tong_hop = []
    for ca, ds_hv in danh_sach_dang_ky.items():
        for hv in ds_hv:
            danh_sach_tong_hop.append({
                "Họ và Tên": hv,
                "Ca Học": ca,
                "Ngày Học": ngay_thu_7
            })

    df_tong = pd.DataFrame(danh_sach_tong_hop)
    csv_data = df_tong.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Tải xuống file danh sách ca sĩ toàn lớp (CSV)",
        data=csv_data,
        file_name=f"Danh_sach_thanh_nhac_{ngay_thu_7.replace('/', '_')}.csv",
        mime="text/csv"
    )
