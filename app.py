import streamlit as st
import database as db
from dotenv import load_dotenv
import os

load_dotenv()
db.init_database()

st.set_page_config(page_title="AI Tutor - Lập trình", page_icon="💻", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 1rem;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .logout-btn {
        background-color: #ff4b4b;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 8px;
        cursor: pointer;
    }
    .logout-btn:hover {
        background-color: #ff0000;
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

# ========== FORM ĐĂNG NHẬP ==========
if st.session_state.user is None:
    st.title("💻 Hệ thống Gia sư AI Lập trình")
    st.markdown("### Đăng nhập để tiếp tục")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập")
            password = st.text_input("Mật khẩu", type="password")
            submitted = st.form_submit_button("🔐 Đăng nhập", use_container_width=True)
            
            if submitted:
                user = db.authenticate(username, password)
                if user:
                    st.session_state.user = user
                    st.success(f"Chào mừng {user['full_name']}!")
                    st.rerun()
                else:
                    st.error("Sai tên đăng nhập hoặc mật khẩu")
        
        st.markdown("---")
        st.caption("📌 **Tài khoản mặc định:**")
        st.caption("👨‍🎓 Học sinh: student1 / 123456")
        st.caption("👨‍🏫 Giáo viên: teacher1 / 123456")

# ========== SAU KHI ĐĂNG NHẬP ==========
else:
    user = st.session_state.user
    
    # Header với nút đăng xuất
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(f"💻 Gia sư AI Lập trình")
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
        try:
            import student_dashboard as student
            student.show_dashboard(user)
        except Exception as e:
            st.error(f"Lỗi tải giao diện học sinh: {str(e)}")
            st.info("Vui lòng kiểm tra file student_dashboard.py")
    else:
        try:
            import teacher_dashboard as teacher
            teacher.show_dashboard(user)
        except Exception as e:
            st.error(f"Lỗi tải giao diện giáo viên: {str(e)}")
            st.info("Vui lòng kiểm tra file teacher_dashboard.py")