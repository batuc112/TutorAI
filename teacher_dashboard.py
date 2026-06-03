import streamlit as st
import database as db
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUBJECT = "programming"

def show_dashboard(user):
    st.title(f"👨‍🏫 Trang quản lý - {user['full_name']}")
    
    # Thêm tab mới cho Đúng/Sai
    tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📚 Bài giảng", 
        "✅ Trắc nghiệm", 
        "✓/✗ Đúng/Sai", 
        "📝 Tự luận", 
        "📊 Xem tất cả", 
        "📝 Đề thi", 
        "🧠 AI Học tập", 
        "🏷️ Tag/Chủ đề"
    ])
    
    # ========== LẤY DANH SÁCH TAG ==========
    all_tags = db.get_all_topics(SUBJECT)
    
    # ========== TAB 0: BÀI GIẢNG (LÝ THUYẾT) ==========
    with tab0:
        st.subheader(f"📚 Thêm bài giảng (Lý thuyết)")
        col1, col2 = st.columns(2)
        with col1:
            lesson_level = st.selectbox("Trình độ", ["beginner", "intermediate", "advanced"], key="ls_lvl")
            lesson_title = st.text_input("Tiêu đề bài học", key="ls_title")
        with col2:
            selected_tags = st.multiselect("Chọn tag (chủ đề)", all_tags, key="ls_tags_select")
            new_tag = st.text_input("Hoặc thêm tag mới (cách nhau bằng dấu phẩy)", key="ls_new_tag")
            if new_tag:
                new_tags = [t.strip() for t in new_tag.split(',') if t.strip()]
                for tag in new_tags:
                    db.add_topic(tag, SUBJECT, user["id"])
                selected_tags.extend(new_tags)
        
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
    
    # ========== TAB 1: TRẮC NGHIỆM (A, B, C, D) ==========
    with tab1:
        st.subheader(f"✅ Thêm câu hỏi trắc nghiệm (4 lựa chọn)")
        col1, col2 = st.columns(2)
        with col1:
            mcq_level = st.selectbox("Trình độ", ["beginner", "intermediate", "advanced"], key="mcq_lvl")
        with col2:
            selected_tags = st.multiselect("Chọn tag (chủ đề)", all_tags, key="mcq_tags_select")
            new_tag = st.text_input("Hoặc thêm tag mới", key="mcq_new_tag")
            if new_tag:
                new_tags = [t.strip() for t in new_tag.split(',') if t.strip()]
                for tag in new_tags:
                    db.add_topic(tag, SUBJECT, user["id"])
                selected_tags.extend(new_tags)
        
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
    
    # ========== TAB 2: ĐÚNG/SAI (MỚI) ==========
    with tab2:
        st.subheader(f"✓/✗ Thêm câu hỏi Đúng/Sai")
        col1, col2 = st.columns(2)
        with col1:
            tf_level = st.selectbox("Trình độ", ["beginner", "intermediate", "advanced"], key="tf_lvl")
        with col2:
            selected_tags = st.multiselect("Chọn tag (chủ đề)", all_tags, key="tf_tags_select")
            new_tag = st.text_input("Hoặc thêm tag mới", key="tf_new_tag")
            if new_tag:
                new_tags = [t.strip() for t in new_tag.split(',') if t.strip()]
                for tag in new_tags:
                    db.add_topic(tag, SUBJECT, user["id"])
                selected_tags.extend(new_tags)
        
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
    
    # ========== TAB 3: TỰ LUẬN ==========
    with tab3:
        st.subheader(f"📝 Thêm câu hỏi tự luận")
        col1, col2 = st.columns(2)
        with col1:
            essay_level = st.selectbox("Trình độ", ["beginner", "intermediate", "advanced"], key="es_lvl")
        with col2:
            selected_tags = st.multiselect("Chọn tag (chủ đề)", all_tags, key="es_tags_select")
            new_tag = st.text_input("Hoặc thêm tag mới", key="es_new_tag")
            if new_tag:
                new_tags = [t.strip() for t in new_tag.split(',') if t.strip()]
                for tag in new_tags:
                    db.add_topic(tag, SUBJECT, user["id"])
                selected_tags.extend(new_tags)
        
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
    
    # ========== TAB 4: XEM TẤT CẢ ==========
    with tab4:
        st.subheader("📊 Tất cả bài tập")
        exercises = db.get_exercises()
        if exercises:
            # Bộ lọc theo loại
            filter_type = st.selectbox("Lọc theo loại", ["Tất cả", "multiple_choice", "true_false", "essay"])
            filtered = [ex for ex in exercises if filter_type == "Tất cả" or ex["type"] == filter_type]
            
            for ex in filtered[:30]:
                type_icon = "✅" if ex["type"] == "multiple_choice" else ("✓/✗" if ex["type"] == "true_false" else "📝")
                with st.expander(f"{type_icon} {ex['question'][:80]}..."):
                    st.markdown(f"**Câu hỏi:** {ex['question']}")
                    if ex.get("options"):
                        st.markdown(f"**Lựa chọn:** {', '.join(ex['options'])}")
                    st.markdown(f"**Đáp án:** `{ex['answer']}`")
                    st.markdown(f"**Tags:** {', '.join(ex['tags']) if ex['tags'] else 'Chưa có tag'}")
        else:
            st.info("Chưa có bài tập nào")
    
    # ========== TAB 5: ĐỀ THI ==========
    with tab5:
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
            # Lấy tất cả bài tập để chọn
            all_exercises = db.get_exercises()
            exercise_options = {f"{ex['type']}: {ex['question'][:60]}...": ex for ex in all_exercises}
            
            for i in range(num_questions):
                with st.expander(f"Câu {i+1}"):
                    selected_key = st.selectbox("Chọn câu hỏi", list(exercise_options.keys()), key=f"ex_select_{i}")
                    if selected_key:
                        q = exercise_options[selected_key]
                        questions.append(q)
            
            if st.button("💾 Lưu đề thi", key="save_exam"):
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
    
    # ========== TAB 6: AI HỌC TẬP ==========
    with tab6:
        st.subheader("🧠 Dữ liệu huấn luyện AI")
        training_data = db.get_all_training_data()
        st.metric("Số câu hỏi mẫu", len(training_data))
        
        if training_data:
            st.subheader("Danh sách câu hỏi mẫu")
            for i, (q, c) in enumerate(training_data[-50:]):
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
    
    # ========== TAB 7: QUẢN LÝ TAG ==========
    with tab7:
        st.subheader("🏷️ Quản lý Tag/Chủ đề")
        
        # Danh sách tag hiện có
        all_tags = db.get_all_topics(SUBJECT)
        st.write(f"**Tổng số tag:** {len(all_tags)}")
        
        if all_tags:
            st.subheader("📋 Danh sách tag")
            col1, col2 = st.columns(2)
            for i, tag in enumerate(all_tags):
                with col1 if i % 2 == 0 else col2:
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
        
        # Xóa tag (cẩn thận)
        st.divider()
        st.subheader("🗑️ Xóa tag")
        st.warning("⚠️ Xóa tag sẽ không xóa bài tập, chỉ xóa tag khỏi danh sách quản lý.")
        tag_to_delete = st.selectbox("Chọn tag cần xóa", ["-- Chọn --"] + all_tags)
        if tag_to_delete != "-- Chọn --" and st.button("Xóa tag", key="delete_tag_btn"):
            db.delete_topic(tag_to_delete)
            st.success(f"✅ Đã xóa tag: {tag_to_delete}")
            st.rerun()