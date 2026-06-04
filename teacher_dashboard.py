import streamlit as st
import database as db
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUBJECT = "programming"

# Tag mặc định
DEFAULT_TAGS = ["biến", "hàm", "vòng lặp", "list", "tuple", "dictionary", "set", "class", "đệ quy", "file", 
                "exception", "module", "decorator", "generator", "OOP", "cơ bản", "nâng cao"]

def show_dashboard(user):
    st.title(f"👨‍🏫 Trang quản lý - {user['full_name']}")
    
    # Đảm bảo tag mặc định có trong database
    for tag in DEFAULT_TAGS:
        db.add_topic(tag, SUBJECT, user["id"])
    
    # Lấy danh sách tag
    all_tags = db.get_all_topics(SUBJECT)
    
    # Tạo các tab
    tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📚 Bài giảng",
        "✅ Trắc nghiệm",
        "✓/✗ Đúng/Sai",
        "📝 Tự luận",
        "📝 Đề thi",
        "📖 Xem bài giảng",
        "📝 Xem bài tập",
        "📄 Xem đề thi",
        "🏷️ Quản lý Tag"
    ])
    
    # ========== TAB 0: BÀI GIẢNG (THÊM MỚI) ==========
    with tab0:
        st.subheader("📚 Thêm bài giảng (Lý thuyết)")
        
        col1, col2 = st.columns(2)
        with col1:
            lesson_level = st.selectbox("Trình độ", ["beginner", "intermediate", "advanced"], key="ls_lvl")
            lesson_title = st.text_input("Tiêu đề bài học", key="ls_title")
        with col2:
            selected_tags = st.multiselect("Chọn tag (chủ đề)", all_tags, key="ls_tags")
        
        lesson_theory = st.text_area("📖 Lý thuyết", height=200, key="ls_theory")
        lesson_examples = st.text_area("💡 Ví dụ (mỗi dòng 1 ví dụ)", height=100, key="ls_ex")
        
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
                    "tags": json.dumps(selected_tags),
                    "teacher_id": user["id"],
                    "created_at": datetime.now().isoformat()
                }
                db.add_lesson(lesson_data)
                st.success(f"✅ Đã thêm bài giảng: {lesson_title}")
                st.balloons()
    
    # ========== TAB 1: TRẮC NGHIỆM (THÊM MỚI) ==========
    with tab1:
        st.subheader("✅ Thêm câu hỏi trắc nghiệm (4 lựa chọn)")
        
        col1, col2 = st.columns(2)
        with col1:
            mcq_level = st.selectbox("Trình độ", ["beginner", "intermediate", "advanced"], key="mcq_lvl")
        with col2:
            selected_tags = st.multiselect("Chọn tag (chủ đề)", all_tags, key="mcq_tags")
        
        mcq_question = st.text_area("📌 Câu hỏi", height=100, key="mcq_q")
        
        st.markdown("**Các lựa chọn:**")
        col_a, col_b = st.columns(2)
        with col_a:
            opt_a = st.text_input("A.", key="opt_a")
            opt_c = st.text_input("C.", key="opt_c")
        with col_b:
            opt_b = st.text_input("B.", key="opt_b")
            opt_d = st.text_input("D.", key="opt_d")
        
        answer = st.selectbox("Đáp án đúng", ["A", "B", "C", "D"], key="mcq_ans")
        explanation = st.text_area("📖 Giải thích (tùy chọn)", height=80, key="mcq_exp")
        
        if st.button("💾 Lưu câu hỏi trắc nghiệm", key="save_mcq"):
            if mcq_question and opt_a and opt_b and opt_c and opt_d:
                exercise_data = {
                    "exercise_id": f"MCQ{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "question": mcq_question,
                    "type": "multiple_choice",
                    "options": [opt_a, opt_b, opt_c, opt_d],
                    "answer": answer,
                    "subject": SUBJECT,
                    "level": mcq_level,
                    "tags": json.dumps(selected_tags),
                    "teacher_id": user["id"],
                    "auto_generated": 0,
                    "correct_explanation": explanation,
                    "created_at": datetime.now().isoformat()
                }
                db.add_exercise(exercise_data)
                st.success("✅ Đã thêm câu hỏi trắc nghiệm!")
                st.balloons()
    
    # ========== TAB 2: ĐÚNG/SAI (THÊM MỚI) ==========
    with tab2:
        st.subheader("✓/✗ Thêm câu hỏi Đúng/Sai")
        
        col1, col2 = st.columns(2)
        with col1:
            tf_level = st.selectbox("Trình độ", ["beginner", "intermediate", "advanced"], key="tf_lvl")
        with col2:
            selected_tags = st.multiselect("Chọn tag (chủ đề)", all_tags, key="tf_tags")
        
        tf_question = st.text_area("📌 Câu hỏi (nhận định)", height=100, key="tf_q")
        tf_answer = st.selectbox("Câu này đúng hay sai?", ["A. Đúng", "B. Sai"], key="tf_ans")
        tf_explanation = st.text_area("📖 Giải thích (tùy chọn)", height=80, key="tf_exp")
        
        if st.button("💾 Lưu câu hỏi Đúng/Sai", key="save_tf"):
            if tf_question:
                exercise_data = {
                    "exercise_id": f"TF{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "question": tf_question,
                    "type": "true_false",
                    "options": ["A. Đúng", "B. Sai"],
                    "answer": "A" if "A" in tf_answer else "B",
                    "subject": SUBJECT,
                    "level": tf_level,
                    "tags": json.dumps(selected_tags),
                    "teacher_id": user["id"],
                    "auto_generated": 0,
                    "correct_explanation": tf_explanation,
                    "created_at": datetime.now().isoformat()
                }
                db.add_exercise(exercise_data)
                st.success("✅ Đã thêm câu hỏi Đúng/Sai!")
                st.balloons()
    
    # ========== TAB 3: TỰ LUẬN (THÊM MỚI) ==========
    with tab3:
        st.subheader("📝 Thêm câu hỏi tự luận")
        
        col1, col2 = st.columns(2)
        with col1:
            essay_level = st.selectbox("Trình độ", ["beginner", "intermediate", "advanced"], key="es_lvl")
        with col2:
            selected_tags = st.multiselect("Chọn tag (chủ đề)", all_tags, key="es_tags")
        
        essay_question = st.text_area("📌 Câu hỏi tự luận", height=150, key="es_q")
        essay_answer = st.text_area("✅ Đáp án tham khảo", height=150, key="es_ans")
        
        if st.button("💾 Lưu câu hỏi tự luận", key="save_essay"):
            if essay_question and essay_answer:
                exercise_data = {
                    "exercise_id": f"ESSAY{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "question": essay_question,
                    "type": "essay",
                    "options": [],
                    "answer": essay_answer,
                    "subject": SUBJECT,
                    "level": essay_level,
                    "tags": json.dumps(selected_tags),
                    "teacher_id": user["id"],
                    "auto_generated": 0,
                    "correct_explanation": "",
                    "created_at": datetime.now().isoformat()
                }
                db.add_exercise(exercise_data)
                st.success("✅ Đã thêm câu hỏi tự luận!")
                st.balloons()
    
    # ========== TAB 4: ĐỀ THI (TẠO MỚI) ==========
    with tab4:
        st.subheader("📝 Tạo đề thi mới")
        
        col1, col2 = st.columns(2)
        with col1:
            exam_level = st.selectbox("Trình độ", ["beginner", "intermediate", "advanced"], key="ex_lvl")
            exam_title = st.text_input("Tiêu đề", key="ex_title")
        with col2:
            num_questions = st.number_input("Số câu (3-20)", min_value=3, max_value=20, value=5, key="num_q")
            time_limit = st.number_input("Thời gian (phút)", min_value=5, max_value=180, value=30, key="time_lim")
        
        all_exercises = db.get_exercises()
        if all_exercises:
            exercise_options = {f"{ex['type']}: {ex['question'][:60]}...": ex for ex in all_exercises}
            
            selected_questions = []
            for i in range(num_questions):
                with st.expander(f"Câu {i+1}"):
                    selected_key = st.selectbox("Chọn câu hỏi", list(exercise_options.keys()), key=f"ex_select_{i}")
                    if selected_key:
                        selected_questions.append(exercise_options[selected_key])
            
            if st.button("💾 Lưu đề thi", key="save_exam"):
                if exam_title and selected_questions:
                    exam_data = {
                        "exam_id": f"EXAM{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "title": exam_title,
                        "subject": SUBJECT,
                        "level": exam_level,
                        "questions": selected_questions,
                        "time_limit": time_limit,
                        "created_at": datetime.now().isoformat(),
                        "teacher_id": user["id"]
                    }
                    db.add_exam(exam_data)
                    st.success(f"✅ Đã tạo đề: {exam_title}")
                    st.balloons()
        else:
            st.warning("Chưa có bài tập nào! Hãy thêm bài tập trước khi tạo đề thi.")
    
    # ========== TAB 5: XEM BÀI GIẢNG ==========
    with tab5:
        st.subheader("📖 Danh sách bài giảng")
        
        lessons = db.get_lessons()
        if lessons:
            for lesson in lessons:
                with st.expander(f"📚 [{lesson['level']}] {lesson['title']}", expanded=False):
                    st.markdown(f"**ID:** `{lesson['lesson_id']}`")
                    st.markdown(f"**Tags:** {', '.join(lesson['tags']) if lesson['tags'] else 'Chưa có tag'}")
                    st.markdown("---")
                    st.markdown("**📖 Lý thuyết:**")
                    st.markdown(lesson['theory'])
                    if lesson.get('examples'):
                        st.markdown("---")
                        st.markdown("**💡 Ví dụ:**")
                        for ex in lesson['examples']:
                            st.markdown(f"- {ex}")
                    
                    # Nút xóa
                    if st.button("🗑️ Xóa bài giảng này", key=f"del_lesson_{lesson['lesson_id']}"):
                        conn = db.get_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM lessons WHERE lesson_id = ?", (lesson['lesson_id'],))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Đã xóa bài giảng: {lesson['title']}")
                        st.rerun()
        else:
            st.info("Chưa có bài giảng nào")
    
    # ========== TAB 6: XEM BÀI TẬP ==========
    with tab6:
        st.subheader("📝 Danh sách bài tập")
        
        # Bộ lọc
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filter_type = st.selectbox("Lọc theo loại", ["Tất cả", "multiple_choice", "true_false", "essay"])
        with col_f2:
            filter_level = st.selectbox("Lọc theo trình độ", ["Tất cả", "beginner", "intermediate", "advanced"])
        with col_f3:
            search = st.text_input("🔍 Tìm kiếm", placeholder="Nhập từ khóa...")
        
        exercises = db.get_exercises()
        
        # Lọc
        filtered = []
        for ex in exercises:
            if filter_type != "Tất cả" and ex["type"] != filter_type:
                continue
            if filter_level != "Tất cả" and ex["level"] != filter_level:
                continue
            if search and search.lower() not in ex["question"].lower():
                continue
            filtered.append(ex)
        
        if filtered:
            for ex in filtered:
                type_icon = "✅" if ex["type"] == "multiple_choice" else ("✓/✗" if ex["type"] == "true_false" else "📝")
                with st.expander(f"{type_icon} [{ex['level']}] {ex['question'][:100]}...", expanded=False):
                    st.markdown(f"**ID:** `{ex['exercise_id']}`")
                    st.markdown(f"**Tags:** {', '.join(ex['tags']) if ex['tags'] else 'Chưa có tag'}")
                    st.markdown("---")
                    st.markdown(f"**📌 Câu hỏi:** {ex['question']}")
                    if ex.get('options'):
                        st.markdown("**Lựa chọn:**")
                        for opt in ex['options']:
                            st.markdown(f"  {opt}")
                    st.markdown(f"**✅ Đáp án:** `{ex['answer']}`")
                    if ex.get('correct_explanation'):
                        st.markdown(f"**📖 Giải thích:** {ex['correct_explanation']}")
                    
                    # Nút xóa
                    if st.button("🗑️ Xóa bài tập này", key=f"del_ex_{ex['exercise_id']}"):
                        conn = db.get_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM exercises WHERE exercise_id = ?", (ex['exercise_id'],))
                        cursor.execute("DELETE FROM student_exercise_history WHERE exercise_id = ?", (ex['exercise_id'],))
                        cursor.execute("DELETE FROM quiz_history WHERE exercise_id = ?", (ex['exercise_id'],))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Đã xóa bài tập")
                        st.rerun()
        else:
            st.info("Không có bài tập nào phù hợp")
    
    # ========== TAB 7: XEM ĐỀ THI ==========
    with tab7:
        st.subheader("📄 Danh sách đề thi")
        
        exams = db.get_exams()
        if exams:
            for ex in exams:
                with st.expander(f"📄 [{ex['level']}] {ex['title']} - {len(ex['questions'])} câu - {ex['time_limit']} phút", expanded=False):
                    st.markdown(f"**ID:** `{ex['exam_id']}`")
                    st.markdown("---")
                    for i, q in enumerate(ex['questions']):
                        st.markdown(f"**Câu {i+1}:** {q['question']}")
                        st.markdown(f"   *Đáp án: {q['answer']}*")
                        if q.get('options'):
                            st.markdown(f"   *Lựa chọn:* {', '.join(q['options'])}")
                        st.markdown("---")
                    
                    # Nút xóa
                    if st.button("🗑️ Xóa đề thi này", key=f"del_exam_{ex['exam_id']}"):
                        conn = db.get_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM exams WHERE exam_id = ?", (ex['exam_id'],))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Đã xóa đề thi: {ex['title']}")
                        st.rerun()
        else:
            st.info("Chưa có đề thi nào")
    
    # ========== TAB 8: QUẢN LÝ TAG ==========
    with tab8:
        st.subheader("🏷️ Quản lý Tag/Chủ đề")
        
        # Danh sách tag mặc định
        st.markdown("### 📋 Tag mặc định")
        cols = st.columns(4)
        for i, tag in enumerate(DEFAULT_TAGS):
            with cols[i % 4]:
                st.caption(f"• {tag}")
        
        st.divider()
        
        # Danh sách tag hiện có
        all_tags = db.get_all_topics(SUBJECT)
        st.write(f"**Tổng số tag:** {len(all_tags)}")
        
        if all_tags:
            st.subheader("📋 Danh sách tag hiện có")
            cols = st.columns(4)
            for i, tag in enumerate(all_tags):
                with cols[i % 4]:
                    st.caption(f"• {tag}")
        
        st.divider()
        
        # Thêm tag mới
        st.subheader("➕ Thêm tag mới")
        new_tag_name = st.text_input("Tên tag mới", key="new_tag_input")
        if st.button("Thêm tag", key="add_tag_btn"):
            if new_tag_name:
                db.add_topic(new_tag_name, SUBJECT, user["id"])
                st.success(f"✅ Đã thêm tag: {new_tag_name}")
                st.rerun()
        
        # Xóa tag
        if all_tags:
            st.divider()
            st.subheader("🗑️ Xóa tag")
            st.warning("⚠️ Xóa tag sẽ không xóa bài tập, chỉ xóa tag khỏi danh sách quản lý.")
            
            tag_to_delete = st.selectbox("Chọn tag cần xóa", ["-- Chọn --"] + all_tags, key="delete_tag_select")
            if tag_to_delete != "-- Chọn --" and st.button("Xóa tag", key="delete_tag_btn"):
                db.delete_topic(tag_to_delete)
                st.success(f"✅ Đã xóa tag: {tag_to_delete}")
                st.rerun()