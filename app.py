import streamlit as st
import database as db
from dotenv import load_dotenv
import os

load_dotenv()
db.init_database()

st.set_page_config(page_title="AI Tutor - Lập trình", page_icon="💻", layout="wide")

st.markdown("""
<style>
    .stApp header {
        background-color: #f0f2f6;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .auth-container {
        max-width: 450px;
        margin: 0 auto;
        padding: 2rem;
        background-color: #ffffff;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .auth-title {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .product-name {
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        color: #4CAF50;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .product-slogan {
        text-align: center;
        font-size: 14px;
        color: #666;
        margin-top: 0px;
        margin-bottom: 20px;
        padding-top: 0px;
    }
    /* Thu gọn khoảng cách giữa các nút */
    .stButton button {
        margin-top: 5px;
        margin-bottom: 5px;
    }
    div[data-testid="stForm"] {
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
</style>
""", unsafe_allow_html=True)

# Xử lý logout
if st.query_params.get("logout") == "true":
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.query_params.clear()
    st.rerun()

# Khởi tạo session state
if "user" not in st.session_state:
    st.session_state.user = None
if "show_register" not in st.session_state:
    st.session_state.show_register = False

# ========== FORM ĐĂNG NHẬP / ĐĂNG KÝ ==========
if st.session_state.user is None:
    # Tên sản phẩm
    st.markdown('<div class="product-name">💻 AI Tutor</div>', unsafe_allow_html=True)
    st.markdown('<div class="product-slogan">Gia sư lập trình thông minh với AI</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    
    if not st.session_state.show_register:
        # ===== FORM ĐĂNG NHẬP =====
        st.markdown('<div class="auth-title"><h2>🔐 Đăng nhập</h2></div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập", placeholder="Nhập tên đăng nhập")
            password = st.text_input("Mật khẩu", type="password", placeholder="Nhập mật khẩu")
            submitted = st.form_submit_button("Đăng nhập", use_container_width=True)
            
            if submitted:
                user = db.authenticate(username, password)
                if user:
                    st.session_state.user = user
                    st.success(f"Chào mừng {user['full_name']}!")
                    st.rerun()
                else:
                    st.error("Sai tên đăng nhập hoặc mật khẩu")
        
        # Nút đăng ký (cách nút đăng nhập 1 khoảng nhỏ)
        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
        if st.button("📝 Đăng ký", use_container_width=True):
            st.session_state.show_register = True
            st.rerun()
        
    else:
        # ===== FORM ĐĂNG KÝ =====
        st.markdown('<div class="auth-title"><h2>📝 Đăng ký</h2></div>', unsafe_allow_html=True)
        
        with st.form("register_form"):
            new_username = st.text_input("Tên đăng nhập *", placeholder="Chọn tên đăng nhập")
            new_password = st.text_input("Mật khẩu *", type="password", placeholder="Mật khẩu (ít nhất 4 ký tự)")
            confirm_password = st.text_input("Xác nhận mật khẩu *", type="password", placeholder="Nhập lại mật khẩu")
            new_fullname = st.text_input("Họ và tên *", placeholder="Nhập họ tên của bạn")
            
            submitted = st.form_submit_button("Đăng ký", use_container_width=True)
            
            if submitted:
                if not new_username or not new_password or not new_fullname:
                    st.error("Vui lòng điền đầy đủ thông tin!")
                elif new_password != confirm_password:
                    st.error("Mật khẩu xác nhận không khớp!")
                elif len(new_password) < 4:
                    st.error("Mật khẩu phải có ít nhất 4 ký tự!")
                else:
                    success, message = db.register_user(new_username, new_password, new_fullname)
                    if success:
                        st.success(message)
                        st.info("✅ Đăng ký thành công! Vui lòng đăng nhập.")
                        st.session_state.show_register = False
                        st.rerun()
                    else:
                        st.error(message)
        
        # Nút quay lại đăng nhập
        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
        if st.button("🔐 Đăng nhập", use_container_width=True):
            st.session_state.show_register = False
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== SAU KHI ĐĂNG NHẬP ==========
else:
    user = st.session_state.user
    
    # Header với nút đăng xuất
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(f"💻 AI Tutor - Gia sư Lập trình")
        st.caption(f"Xin chào, **{user['full_name']}** | Vai trò: {user['role']}")
    with col2:
        if st.button("🚪 Đăng xuất", key="logout_btn", use_container_width=True):
            st.query_params["logout"] = "true"
            st.rerun()
    
    st.divider()
    
    # Lấy profile và hiển thị thông tin nhanh
    profile = db.get_student_profile(user["id"]) if user["role"] == "student" else None
    
    if profile:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Trình độ", profile["level"].upper())
        with col2:
            exam_scores = profile.get("exam_scores", [])
            last_score = exam_scores[-1] if exam_scores else "Chưa có"
            st.metric("📝 Điểm gần nhất", last_score)
        with col3:
            from hybrid_tutor import HybridTutor
            if 'hybrid_tutor' not in st.session_state:
                st.session_state.hybrid_tutor = HybridTutor(api_key=os.getenv("GEMINI_API_KEY"))
            stats = st.session_state.hybrid_tutor.get_stats()
            gemini_status = "✅ Đã kết nối" if stats.get("gemini_available") else "⚠️ Chưa kết nối"
            st.metric("🤖 Gemini", gemini_status)
    
    # Điều hướng theo role
    if user["role"] == "student":
        import student_dashboard as student
        student.show_dashboard(user)
    else:
        import teacher_dashboard as teacher
        teacher.show_dashboard(user)