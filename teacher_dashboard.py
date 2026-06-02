import streamlit as st
import database as db
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Subject cố định
SUBJECT = "programming"
SUBJECT_DISPLAY = "Lập trình"

def show_dashboard(user):
    st.title(f"👨‍🏫 Trang quản lý - {user['full_name']}")
    
    tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📚 Bài giảng", "✅ Trắc nghiệm", "📝 Tự luận", "📊 Xem tất cả", "📝 Đề thi", "🧠 AI Học tập"
    ])
    
    # ========== TAB 0: BÀI GIẢNG ==========
    with tab0:
        st.subheader(f"📚 Thêm bài giảng ({SUBJECT_DISPLAY})")
        col1, col2 = st.columns(2)
        with col1:
            lesson_level = st.selectbox("Trình độ", ["beginner", "intermediate", "advanced"], key="ls_lvl")
            lesson_title = st.text_input("Tiêu đề", key="ls_title")
        with col2:
            lesson_tags = st.text_input("Tags", key="ls_tags")
        
        lesson_theory = st.text_area("Lý thuyết", height=200, key="ls_theory")
        lesson_examples = st.text_area("Ví dụ (mỗi dòng 1 ví dụ)", height=100, key="ls_ex")
        
        if st.button("💾 Lưu bài giảng", key="save_lesson"):
            if lesson_title and lesson_theory:
                examples = [ex.strip() for ex in lesson_examples.split('\n') if ex.strip()]
                lesson_data = {
                    "lesson_id": f"L{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "title": lesson_title,
                    "theory": lesson_theory,
                    "examples": examples,
                    "exercises": [],
                    "subject": SUBJECT,
                    "level": lesson_level,
                    "tags": [t.strip() for t in lesson_tags.split(',') if t.strip()],
                    "teacher_id": user["id"],
                    "created_at": datetime.now().isoformat()
                }
                db.add_lesson(lesson_data)
                st.success(f"✅ Đã thêm bài giảng: {lesson_title}")
                st.balloons()
    
    # ========== TAB 1: TRẮC NGHIỆM ==========
    with tab1:
        st.subheader(f"✅ Thêm câu hỏi trắc nghiệm ({SUBJECT_DISPLAY})")
        col1, col2 = st.columns(2)
        with col1:
            mcq_level = st.selectbox("Trình độ", ["beginner", "intermediate", "advanced"], key="mcq_lvl")
        with col2:
            mcq_tags = st.text_input("Tags", key="mcq_tags")
        
        mcq_question = st.text_area("Câu hỏi", height=100, key="mcq_q")
        
        col_a, col_b = st.columns(2)
        with col_a:
            opt_a = st.text_input("A.", key="opt_a")
            opt_c = st.text_input("C.", key="opt_c")
        with col_b:
            opt_b = st.text_input("B.", key="opt_b")
            opt_d = st.text_input("D.", key="opt_d")
        
        answer = st.selectbox("Đáp án đúng", ["A", "B", "C", "D"], key="mcq_ans")
        
        if st.button("💾 Lưu", key="save_mcq"):
            if mcq_question and opt_a and opt_b and opt_c and opt_d:
                exercise_data = {
                    "exercise_id": f"MCQ{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "question": mcq_question,
                    "type": "multiple_choice",
                    "options": [opt_a, opt_b, opt_c, opt_d],
                    "answer": answer,
                    "subject": SUBJECT,
                    "level": mcq_level,
                    "tags": [t.strip() for t in mcq_tags.split(',') if t.strip()],
                    "teacher_id": user["id"],
                    "auto_generated": 0,
                    "correct_explanation": "",
                    "created_at": datetime.now().isoformat()
                }
                db.add_exercise(exercise_data)
                st.success("✅ Đã thêm câu hỏi!")
                st.balloons()
    
    # ========== TAB 2: TỰ LUẬN ==========
    with tab2:
        st.subheader(f"📝 Thêm câu hỏi tự luận ({SUBJECT_DISPLAY})")
        col1, col2 = st.columns(2)
        with col1:
            essay_level = st.selectbox("Trình độ", ["beginner", "intermediate", "advanced"], key="es_lvl")
        with col2:
            essay_tags = st.text_input("Tags", key="es_tags")
        
        essay_question = st.text_area("Câu hỏi", height=150, key="es_q")
        essay_answer = st.text_area("Đáp án tham khảo", height=150, key="es_ans")
        
        if st.button("💾 Lưu", key="save_essay"):
            if essay_question and essay_answer:
                exercise_data = {
                    "exercise_id": f"ESSAY{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "question": essay_question,
                    "type": "essay",
                    "options": [],
                    "answer": essay_answer,
                    "subject": SUBJECT,
                    "level": essay_level,
                    "tags": [t.strip() for t in essay_tags.split(',') if t.strip()],
                    "teacher_id": user["id"],
                    "auto_generated": 0,
                    "correct_explanation": "",
                    "created_at": datetime.now().isoformat()
                }
                db.add_exercise(exercise_data)
                st.success("✅ Đã thêm câu hỏi tự luận!")
                st.balloons()
    
    # ========== TAB 3: XEM TẤT CẢ ==========
    with tab3:
        st.subheader("📊 Tất cả bài tập")
        exercises = db.get_exercises()
        if exercises:
            for ex in exercises[:20]:
                with st.expander(f"{ex['type']}: {ex['question'][:80]}..."):
                    st.markdown(f"**Câu hỏi:** {ex['question']}")
                    st.markdown(f"**Đáp án:** `{ex['answer']}`")
        else:
            st.info("Chưa có bài tập nào")
    
    # ========== TAB 4: ĐỀ THI ==========
    with tab4:
        st.subheader("📝 Quản lý đề thi")
        tab_create, tab_list = st.tabs(["Tạo đề mới", "Danh sách đề"])
        
        with tab_create:
            col1, col2 = st.columns(2)
            with col1:
                exam_level = st.selectbox("Trình độ", ["beginner", "intermediate", "advanced"], key="ex_lvl")
                exam_title = st.text_input("Tiêu đề", key="ex_title")
            with col2:
                num_questions = st.number_input("Số câu (3-20)", min_value=3, max_value=20, value=5, key="num_q")
                time_limit = st.number_input("Thời gian (phút)", min_value=5, max_value=180, value=30, key="time_lim")
            
            questions = []
            for i in range(num_questions):
                with st.expander(f"Câu {i+1}"):
                    q_type = st.selectbox("Loại", ["multiple_choice", "true_false", "fill_blank"], key=f"type_{i}")
                    q_text = st.text_area("Nội dung", key=f"text_{i}")
                    if q_type == "multiple_choice":
                        col_a, col_b = st.columns(2)
                        with col_a:
                            opt_a = st.text_input("A.", key=f"a_{i}")
                            opt_c = st.text_input("C.", key=f"c_{i}")
                        with col_b:
                            opt_b = st.text_input("B.", key=f"b_{i}")
                            opt_d = st.text_input("D.", key=f"d_{i}")
                        options = [opt_a, opt_b, opt_c, opt_d]
                        answer = st.selectbox("Đáp án", ["A", "B", "C", "D"], key=f"ans_{i}")
                    elif q_type == "true_false":
                        options = ["A. Đúng", "B. Sai"]
                        answer = st.selectbox("Đáp án", ["A", "B"], key=f"ans_{i}")
                    else:
                        options = []
                        answer = st.text_input("Đáp án", key=f"ans_{i}")
                    if q_text:
                        questions.append({"question": q_text, "type": q_type, "options": options, "answer": answer})
            
            if st.button("💾 Lưu đề", key="save_exam"):
                if exam_title and questions:
                    exam_data = {
                        "exam_id": f"EXAM{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "title": exam_title,
                        "subject": SUBJECT,
                        "level": exam_level,
                        "questions": questions,
                        "time_limit": time_limit,
                        "created_at": datetime.now().isoformat(),
                        "teacher_id": user["id"]
                    }
                    db.add_exam(exam_data)
                    st.success(f"✅ Đã tạo đề: {exam_title}")
                    st.balloons()
        
        with tab_list:
            exams = db.get_exams()
            if exams:
                for ex in exams:
                    with st.expander(f"📄 {ex['title']} ({ex['level']}) - {len(ex['questions'])} câu"):
                        for i, q in enumerate(ex['questions'][:3]):
                            st.markdown(f"**{i+1}.** {q['question'][:100]}...")
            else:
                st.info("Chưa có đề thi nào")
    
    # ========== TAB 5: AI HỌC TẬP ==========
    with tab5:
        st.subheader("🧠 Dữ liệu huấn luyện AI")
        
        training_data = db.get_all_training_data()
        st.metric("Số câu hỏi mẫu", len(training_data))
        
        if training_data:
            st.subheader("Danh sách câu hỏi mẫu")
            for i, (q, c) in enumerate(training_data[-30:]):
                st.caption(f"{i+1}. [{c}] {q[:100]}")
        
        st.divider()
        st.subheader("Thêm câu hỏi mới")
        new_question = st.text_input("Câu hỏi mẫu")
        new_category = st.selectbox("Nhãn", ["definition", "example", "how_to", "exercise", "compare"])
        
        if st.button("➕ Thêm"):
            if new_question:
                db.add_training_data(new_question, new_category)
                st.success("✅ Đã thêm! Hãy nhấn 'Huấn luyện lại AI' để cập nhật.")
                st.rerun()
        
        if st.button("🔄 Huấn luyện lại AI", key="retrain_btn"):
            from ml_classifier import MLQuestionClassifier
            classifier = MLQuestionClassifier()
            classifier.train()
            st.success("✅ Đã huấn luyện AI thành công!")