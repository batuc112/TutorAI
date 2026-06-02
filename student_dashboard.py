import streamlit as st
import database as db
import random
import time
import json
import re
from datetime import datetime
from hybrid_tutor import HybridTutor
from dotenv import load_dotenv
import os

load_dotenv()

# Subject cố định
SUBJECT = "programming"


def extract_topic_from_question(question):
    question_lower = question.lower()
    patterns = [
        (r'bài tập (?:về|với) (\w+)', 1),
        (r'bài (?:tập|thực hành) (\w+)', 1),
        (r'làm bài (\w+)', 1),
        (r'cho tôi bài tập (\w+)', 1),
    ]
    
    for pattern, group in patterns:
        match = re.search(pattern, question_lower)
        if match:
            topic = match.group(group)
            stop_words = ["về", "với", "của", "một", "cho", "tôi"]
            if topic not in stop_words:
                return topic
    
    words = question_lower.split()
    for i, word in enumerate(words):
        if word in ["về", "với", "của"] and i + 1 < len(words):
            return words[i + 1]
    return None


def save_exercise_to_db(question_data, level):
    exercise_id = f"GEN{random.randint(10000, 99999)}"
    exercise_data = {
        "exercise_id": exercise_id,
        "question": question_data["question"],
        "type": question_data.get("type", "essay"),
        "options": json.dumps(question_data.get("options", [])),
        "answer": question_data["answer"],
        "subject": SUBJECT,
        "level": level,
        "tags": json.dumps([SUBJECT]),
        "teacher_id": 1,
        "auto_generated": 1,
        "correct_explanation": question_data.get("explanation", ""),
        "created_at": datetime.now().isoformat()
    }
    db.add_exercise(exercise_data)
    return exercise_id


def generate_exam(student_level):
    exams = db.get_exams(subject=SUBJECT, level=student_level)
    if not exams:
        return None, "📚 Chưa có đề thi nào."
    selected = random.choice(exams)
    return {
        "exam_id": f"EXAM_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "title": selected["title"],
        "questions": selected["questions"],
        "total": len(selected["questions"]),
        "time_limit": selected.get("time_limit", 30),
        "answers": []
    }, None


def show_dashboard(user):
    if 'hybrid_tutor' not in st.session_state:
        st.session_state.hybrid_tutor = HybridTutor(api_key=os.getenv("GEMINI_API_KEY"))
    
    profile = db.get_student_profile(user["id"])
    student_level = profile["level"]
    gemini_available = st.session_state.hybrid_tutor.gemini_available
    
    # Session state
    if "user_id" not in st.session_state:
        st.session_state.user_id = user["id"]
    
    chat_key = f"chat_messages_{SUBJECT}"
    if chat_key not in st.session_state:
        history = db.get_chat_history(user["id"], SUBJECT, limit=50)
        if history:
            st.session_state[chat_key] = history
        else:
            welcome_msg = f"👋 Chào bạn {user['full_name']}! Trình độ hiện tại: **{student_level.upper()}**\n\n💬 Tôi là gia sư AI Lập trình. Bạn có thể:\n• **'Bài tập về biến'** - Nhận bài theo chủ đề\n• **'Bài tập'** - Nhận bài ngẫu nhiên\n• **'Làm đề'** - Thi thử\n• **'Hàm là gì?'** - Hỏi lý thuyết\n\nHãy bắt đầu nào! 🚀"
            st.session_state[chat_key] = [{"role": "assistant", "content": welcome_msg}]
            db.save_chat_message(user["id"], SUBJECT, "assistant", welcome_msg)
    
    if "is_doing_exam" not in st.session_state:
        st.session_state.is_doing_exam = False
    if "current_exam" not in st.session_state:
        st.session_state.current_exam = None
    if "exam_current_index" not in st.session_state:
        st.session_state.exam_current_index = 0
    if "exam_start_time" not in st.session_state:
        st.session_state.exam_start_time = None
    if "show_explanation" not in st.session_state:
        st.session_state.show_explanation = False
    if "last_answer_result" not in st.session_state:
        st.session_state.last_answer_result = None
    
    # Nút xóa lịch sử chat (nhỏ gọn)
    col_clear, col_spacer = st.columns([1, 10])
    with col_clear:
        if st.button("🗑️ Xóa lịch sử", key="clear_history", help="Xóa toàn bộ lịch sử chat"):
            db.clear_chat_history(user["id"], SUBJECT)
            st.session_state[chat_key] = []
            st.rerun()
    
    # Làm đề thi
    if st.session_state.is_doing_exam and st.session_state.current_exam:
        exam = st.session_state.current_exam
        questions = exam["questions"]
        total = exam["total"]
        current = st.session_state.exam_current_index
        time_limit = exam.get("time_limit", 30)
        
        if st.session_state.exam_start_time is None:
            st.session_state.exam_start_time = time.time()
        
        elapsed = time.time() - st.session_state.exam_start_time
        remaining = max(0, time_limit * 60 - elapsed)
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if remaining <= 0:
                st.error("⏰ HẾT GIỜ!")
            else:
                st.info(f"⏰ {minutes}:{seconds:02d}")
        with col2:
            st.progress(current / total, text=f"Câu {current + 1}/{total}")
        
        st.subheader(f"📝 {exam['title']}")
        q = questions[current]
        st.markdown(f"**{q['question']}**")
        
        answer = None
        if q["type"] == "multiple_choice" and q.get("options"):
            answer = st.radio("Chọn đáp án:", q["options"], key=f"q_{current}")
            answer = answer[0] if answer else None
        elif q["type"] == "true_false":
            answer = st.radio("Chọn đáp án:", ["A. Đúng", "B. Sai"], key=f"q_{current}")
            answer = answer[0] if answer else None
        else:
            answer = st.text_input("Câu trả lời:", key=f"q_{current}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⏩ Nộp câu", key="submit_btn", use_container_width=True):
                if answer:
                    is_correct = answer.upper() == q["answer"].upper() if q["type"] != "essay" else True
                    score = 100 if is_correct else 0
                    exam["answers"].append({"correct": is_correct, "score": score})
                    
                    if current + 1 < total:
                        st.session_state.exam_current_index = current + 1
                        st.rerun()
                    else:
                        total_score = sum(a["score"] for a in exam["answers"])
                        avg_score = total_score / total
                        new_level = db.add_exam_result(user["id"], exam["exam_id"], avg_score, exam["answers"])
                        st.success(f"🎉 KẾT QUẢ: {avg_score:.1f}/100")
                        if new_level != student_level:
                            st.balloons()
                            st.success(f"🚀 NÂNG TRÌNH ĐỘ LÊN {new_level.upper()}!")
                        st.session_state.is_doing_exam = False
                        st.session_state.current_exam = None
                        st.session_state.exam_current_index = 0
                        st.session_state.exam_start_time = None
                        if st.button("🏠 Về trang chính"):
                            st.rerun()
                else:
                    st.warning("Vui lòng chọn/nhập câu trả lời!")
        with col2:
            if st.button("❌ Hủy", key="cancel_exam", use_container_width=True):
                st.session_state.is_doing_exam = False
                st.session_state.current_exam = None
                st.session_state.exam_current_index = 0
                st.session_state.exam_start_time = None
                st.rerun()
        return
    
    # Hiển thị chat history
    for msg in st.session_state[chat_key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if st.session_state.get("show_explanation") and st.session_state.get("last_answer_result"):
        with st.chat_message("assistant"):
            st.markdown(st.session_state.last_answer_result)
        st.session_state.show_explanation = False
    
    # Xử lý nhập liệu
    if prompt := st.chat_input("Nhập yêu cầu..."):
        db.save_chat_message(user["id"], SUBJECT, "user", prompt)
        st.session_state[chat_key].append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            msg_lower = prompt.lower()
            response = None
            
            if "bài tập" in msg_lower or "bài mới" in msg_lower:
                topic = extract_topic_from_question(prompt)
                
                if topic:
                    with st.chat_message("assistant"):
                        st.info(f"🔍 Đang tìm bài tập về **{topic}**...")
                    exercises = db.get_exercises_by_topic(
                        topic=topic,
                        subject=SUBJECT,
                        level=student_level,
                        student_id=user["id"]
                    )
                else:
                    exercises = db.get_unsolved_exercises(
                        student_id=user["id"],
                        subject=SUBJECT,
                        level=student_level
                    )
                
                if exercises:
                    ex = random.choice(exercises)
                    st.session_state.current_exercise = ex
                    
                    st.markdown(f"**📝 {ex['question']}**")
                    
                    with st.form(key=f"practice_form_{ex['exercise_id']}"):
                        answer_input = None
                        
                        if ex["type"] == "multiple_choice" and ex.get("options"):
                            answer_input = st.radio("Chọn đáp án:", ex["options"])
                            answer_input = answer_input[0] if answer_input else None
                        elif ex["type"] == "true_false":
                            answer_input = st.radio("Chọn đáp án:", ["A. Đúng", "B. Sai"])
                            answer_input = answer_input[0] if answer_input else None
                        elif ex["type"] == "fill_blank":
                            answer_input = st.text_input("Điền câu trả lời vào ô trống:")
                        else:
                            answer_input = st.text_area("Câu trả lời:")
                        
                        submitted = st.form_submit_button("✅ Nộp bài")
                        
                        if submitted:
                            if answer_input:
                                is_correct = answer_input.upper() == ex["answer"].upper() if ex["type"] not in ["essay", "fill_blank"] else answer_input.strip().lower() == ex["answer"].lower()
                                score = 100 if is_correct else 0
                                
                                if gemini_available:
                                    with st.spinner("🤖 Đang phân tích câu trả lời..."):
                                        explanation = st.session_state.hybrid_tutor.explain_answer_with_gemini(
                                            ex["question"], answer_input, ex["answer"], topic if topic else "chủ đề này"
                                        )
                                else:
                                    explanation = f"✅ Đáp án đúng là: {ex['answer']}" if is_correct else f"❌ Đáp án đúng là: {ex['answer']}"
                                
                                db.add_practice_result(user["id"], ex["exercise_id"], score, answer_input, explanation)
                                db.mark_exercise_done(user["id"], ex["exercise_id"], is_exam=0)
                                
                                if is_correct:
                                    st.success("🎉 Chính xác!")
                                else:
                                    st.error(f"❌ Chưa đúng. Đáp án đúng là: {ex['answer']}")
                                
                                with st.expander("📖 Xem giải thích chi tiết"):
                                    st.markdown(explanation)
                                
                                st.rerun()
                            else:
                                st.warning("Vui lòng chọn/nhập câu trả lời!")
                
                elif gemini_available:
                    with st.spinner(f"🤖 Đang tạo bài tập mới về '{topic if topic else 'chủ đề này'}'..."):
                        new_exercise = st.session_state.hybrid_tutor.generate_exercise_with_gemini(
                            topic if topic else "Python", 
                            student_level
                        )
                        
                        if new_exercise:
                            exercise_id = save_exercise_to_db(new_exercise, student_level)
                            new_exercise["exercise_id"] = exercise_id
                            st.session_state.current_exercise = new_exercise
                            
                            st.markdown(f"**✨ Bài tập mới (do AI tạo, đã lưu):**\n\n{new_exercise['question']}")
                            
                            with st.form(key=f"practice_form_new_{exercise_id}"):
                                answer_input = None
                                
                                if new_exercise.get("type") == "multiple_choice" and new_exercise.get("options"):
                                    answer_input = st.radio("Chọn đáp án:", new_exercise["options"])
                                    answer_input = answer_input[0] if answer_input else None
                                elif new_exercise.get("type") == "true_false":
                                    answer_input = st.radio("Chọn đáp án:", ["A. Đúng", "B. Sai"])
                                    answer_input = answer_input[0] if answer_input else None
                                else:
                                    answer_input = st.text_input("Câu trả lời:")
                                
                                submitted = st.form_submit_button("✅ Nộp bài")
                                
                                if submitted:
                                    if answer_input:
                                        is_correct = answer_input.upper() == new_exercise["answer"].upper() if new_exercise.get("type") not in ["essay", "fill_blank"] else answer_input.strip().lower() == new_exercise["answer"].lower()
                                        score = 100 if is_correct else 0
                                        
                                        with st.spinner("🤖 Đang phân tích câu trả lời..."):
                                            explanation = st.session_state.hybrid_tutor.explain_answer_with_gemini(
                                                new_exercise["question"], answer_input, new_exercise["answer"], topic if topic else "Python"
                                            )
                                        
                                        db.add_practice_result(user["id"], exercise_id, score, answer_input, explanation)
                                        db.mark_exercise_done(user["id"], exercise_id, is_exam=0)
                                        
                                        if is_correct:
                                            st.success("🎉 Chính xác!")
                                        else:
                                            st.error(f"❌ Chưa đúng. Đáp án đúng là: {new_exercise['answer']}")
                                        
                                        with st.expander("📖 Xem giải thích chi tiết"):
                                            st.markdown(explanation)
                                        
                                        st.rerun()
                                    else:
                                        st.warning("Vui lòng chọn/nhập câu trả lời!")
                            
                            st.caption("💡 *Bài tập này đã được lưu vào database để dùng cho lần sau!*")
                        else:
                            st.markdown("⚠️ Không thể tạo bài tập mới. Vui lòng thử lại sau!")
                else:
                    if topic:
                        st.warning(f"📚 Chưa có bài tập về '{topic}' và chưa kết nối Gemini để tạo mới.")
                    else:
                        st.warning("📚 Chưa có bài tập nào trong kho!")
                    
                    if st.button("🔄 Làm lại bài tập cũ"):
                        db.reset_exercise_history(user["id"])
                        st.rerun()
            
            elif "làm đề" in msg_lower or "đề thi" in msg_lower:
                exam, error = generate_exam(student_level)
                if exam:
                    st.session_state.is_doing_exam = True
                    st.session_state.current_exam = exam
                    st.session_state.exam_current_index = 0
                    st.session_state.exam_start_time = None
                    st.markdown(f"📝 **{exam['title']}**\n✨ Gồm {exam['total']} câu\n⏰ Thời gian: {exam['time_limit']} phút\n\n👉 Trả lời từng câu bên dưới!")
                    st.rerun()
                else:
                    st.markdown(error)
            
            else:
                with st.spinner("🤔 Đang suy nghĩ..."):
                    result = st.session_state.hybrid_tutor.answer(prompt, subject=SUBJECT)
                    response = result["answer"]
                    st.markdown(response)
        
        if response:
            db.save_chat_message(user["id"], SUBJECT, "assistant", response)
            st.session_state[chat_key].append({"role": "assistant", "content": response})
        else:
            db.save_chat_message(user["id"], SUBJECT, "assistant", st.session_state[chat_key][-1]["content"])
        
        st.rerun()