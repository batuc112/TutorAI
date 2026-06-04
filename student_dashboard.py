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


def save_exercise_to_db(question_data, level, topic_name=None):
    """Lưu bài tập vào database - ĐẢM BẢO ĐỊNH DẠNG ĐÚNG"""
    
    exercise_id = f"GEN{random.randint(10000, 99999)}"
    tags = [SUBJECT]
    if topic_name:
        tags.append(topic_name)
        db.get_or_create_topic(topic_name, SUBJECT)
    
    # ===== LẤY VÀ XỬ LÝ CÂU HỎI =====
    question = question_data.get("question", "")
    if isinstance(question, list):
        question = ''.join(question)
    elif not isinstance(question, str):
        question = str(question)
    
    # ===== LẤY VÀ XỬ LÝ OPTIONS =====
    options = question_data.get("options", [])
    
    # Nếu options là chuỗi, thử parse JSON
    if isinstance(options, str):
        try:
            options = json.loads(options)
        except:
            options = []
    
    # Nếu options là list, xử lý từng phần tử
    clean_options = []
    if isinstance(options, list):
        for opt in options:
            if isinstance(opt, list):
                # Ghép mảng ký tự thành chuỗi
                clean_options.append(''.join(opt))
            elif isinstance(opt, str):
                clean_options.append(opt)
            else:
                clean_options.append(str(opt))
    
    # Đảm bảo có đúng 4 options
    if len(clean_options) != 4:
        clean_options = [
            "A. Đáp án A",
            "B. Đáp án B",
            "C. Đáp án C",
            "D. Đáp án D"
        ]
    
    # Đảm bảo mỗi option bắt đầu đúng prefix
    for i, opt in enumerate(clean_options):
        prefix = ["A. ", "B. ", "C. ", "D. "][i]
        # Nếu chưa có prefix, thêm vào
        if not opt.startswith(prefix[:2]):
            # Bỏ prefix cũ nếu có
            opt = re.sub(r'^[A-D]\.\s*', '', opt)
            clean_options[i] = prefix + opt
    
    # ===== LẤY ĐÁP ÁN =====
    answer = question_data.get("answer", "A")
    if isinstance(answer, list):
        answer = ''.join(answer)
    else:
        answer = str(answer).upper().strip()
    # Chỉ lấy chữ cái đầu
    if len(answer) > 1:
        answer = answer[0]
    if answer not in ["A", "B", "C", "D"]:
        answer = "A"
    
    # ===== LẤY GIẢI THÍCH =====
    explanation = question_data.get("explanation", "")
    if isinstance(explanation, list):
        explanation = ''.join(explanation)
    elif not isinstance(explanation, str):
        explanation = str(explanation)
    
    # ===== TẠO DỮ LIỆU JSON ĐỂ LƯU =====
    # Dùng json.dumps với ensure_ascii=False để giữ tiếng Việt
    options_json = json.dumps(clean_options, ensure_ascii=False)
    tags_json = json.dumps(tags, ensure_ascii=False)
    
    exercise_data = {
        "exercise_id": exercise_id,
        "question": question,
        "type": "multiple_choice",
        "options": options_json,  # Đã là JSON string
        "answer": answer,
        "subject": SUBJECT,
        "level": level,
        "tags": tags_json,
        "teacher_id": 1,
        "auto_generated": 1,
        "correct_explanation": explanation,
        "created_at": datetime.now().isoformat()
    }
    
    # Debug: in ra để kiểm tra
    print(f"📝 Lưu bài tập:")
    print(f"   ID: {exercise_id}")
    print(f"   Question: {question[:50]}...")
    print(f"   Options: {clean_options}")
    print(f"   Answer: {answer}")
    
    db.add_exercise(exercise_data)
    return exercise_id


def show_dashboard(user):
    # Khởi tạo hybrid_tutor
    if 'hybrid_tutor' not in st.session_state:
        st.session_state.hybrid_tutor = HybridTutor(api_key=os.getenv("GEMINI_API_KEY"))
    
    profile = db.get_student_profile(user["id"])
    student_level = profile["level"]
    gemini_available = st.session_state.hybrid_tutor.gemini_available
    
    if "user_id" not in st.session_state:
        st.session_state.user_id = user["id"]
    
    # Chat history
    chat_key = f"chat_messages_{SUBJECT}"
    if chat_key not in st.session_state:
        history = db.get_chat_history(user["id"], SUBJECT, limit=100)
        if history:
            st.session_state[chat_key] = history
        else:
            welcome_msg = f"👋 Chào bạn {user['full_name']}! Trình độ: **{student_level.upper()}**\n\n💻 **Gia sư Lập trình**\n\n• **'bài tập'** - Bài ngẫu nhiên\n• **'bài tập về biến'** - Bài theo chủ đề\n• **'làm đề'** - Thi thử\n• **'hàm là gì?'** - Hỏi lý thuyết"
            st.session_state[chat_key] = [{"role": "assistant", "content": welcome_msg}]
            db.save_chat_message(user["id"], SUBJECT, "assistant", welcome_msg)
    
    # Exam state
    if "is_doing_exam" not in st.session_state:
        st.session_state.is_doing_exam = False
    if "current_exam" not in st.session_state:
        st.session_state.current_exam = None
    if "exam_current_index" not in st.session_state:
        st.session_state.exam_current_index = 0
    if "exam_start_time" not in st.session_state:
        st.session_state.exam_start_time = None
    
    # Practice state
    if "waiting_for_answer" not in st.session_state:
        st.session_state.waiting_for_answer = False
    if "current_question" not in st.session_state:
        st.session_state.current_question = None
    
    # Nút xóa lịch sử
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🗑️ Xóa lịch sử", key="clear_history"):
            db.clear_chat_history(user["id"], SUBJECT)
            st.session_state[chat_key] = []
            st.rerun()
    
    # ========== LÀM ĐỀ THI ==========
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
        
        c1, c2 = st.columns([1, 3])
        with c1:
            if remaining <= 0:
                st.error("⏰ HẾT GIỜ!")
            else:
                st.info(f"⏰ {minutes}:{seconds:02d}")
        with c2:
            st.progress(current / total, text=f"Câu {current + 1}/{total}")
        
        st.subheader(f"📝 {exam['title']}")
        q = questions[current]
        st.markdown(f"**{q['question']}**")
        
        answer = None
        if q["type"] == "multiple_choice" and q.get("options"):
            answer = st.radio("Chọn đáp án:", q["options"], key=f"exam_q_{current}")
            answer = answer[0] if answer else None
        elif q["type"] == "true_false":
            answer = st.radio("Chọn đáp án:", ["A. Đúng", "B. Sai"], key=f"exam_q_{current}")
            answer = answer[0] if answer else None
        else:
            answer = st.text_input("Câu trả lời:", key=f"exam_q_{current}")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⏩ Nộp câu", key="submit_exam"):
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
                        st.rerun()
                else:
                    st.warning("Vui lòng chọn/nhập câu trả lời!")
        with c2:
            if st.button("❌ Hủy", key="cancel_exam"):
                st.session_state.is_doing_exam = False
                st.session_state.current_exam = None
                st.session_state.exam_current_index = 0
                st.session_state.exam_start_time = None
                st.rerun()
        return
    
    # ========== HIỂN THỊ CHAT ==========
    for msg in st.session_state[chat_key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # ========== XỬ LÝ BÀI TẬP ĐANG CHỜ TRẢ LỜI ==========
    if st.session_state.waiting_for_answer and st.session_state.current_question:
        with st.chat_message("assistant"):
            st.markdown(f"**📝 {st.session_state.current_question['question']}**")
            if st.session_state.current_question.get("options"):
                for opt in st.session_state.current_question["options"]:
                    st.markdown(f"  {opt}")
        
        with st.form(key="answer_form"):
            answer_input = None
            if st.session_state.current_question.get("type") == "multiple_choice" and st.session_state.current_question.get("options"):
                answer_input = st.radio("Chọn đáp án:", st.session_state.current_question["options"])
                answer_input = answer_input[0] if answer_input else None
            elif st.session_state.current_question.get("type") == "true_false":
                answer_input = st.radio("Chọn đáp án:", ["A. Đúng", "B. Sai"])
                answer_input = answer_input[0] if answer_input else None
            else:
                answer_input = st.text_input("Câu trả lời:")
            
            submitted = st.form_submit_button("✅ Nộp bài")
            
            if submitted:
                if answer_input:
                    ex = st.session_state.current_question
                    is_correct = answer_input.upper() == ex["answer"].upper() if ex["type"] not in ["essay", "fill_blank"] else answer_input.strip().lower() == ex["answer"].lower()
                    score = 100 if is_correct else 0
                    
                    if gemini_available:
                        with st.spinner("🤖 Đang phân tích câu trả lời..."):
                            explanation = st.session_state.hybrid_tutor.call_gemini(
                                f"Học sinh trả lời câu hỏi: {ex['question']}\nĐáp án học sinh: {answer_input}\nĐáp án đúng: {ex['answer']}\nHãy giải thích ngắn gọn, tối đa 2 câu, bằng tiếng Việt."
                            )
                            if not explanation:
                                explanation = f"✅ Đúng!" if is_correct else f"❌ Sai. Đáp án đúng là: {ex['answer']}"
                    else:
                        explanation = f"✅ Đúng!" if is_correct else f"❌ Sai. Đáp án đúng là: {ex['answer']}"
                    
                    db.add_practice_result(user["id"], ex["exercise_id"], score, answer_input, explanation)
                    db.mark_exercise_done(user["id"], ex["exercise_id"], is_exam=0)
                    
                    result_msg = f"**📝 Câu hỏi:** {ex['question']}\n\n"
                    result_msg += f"**💬 Câu trả lời của bạn:** {answer_input}\n\n"
                    result_msg += f"**📊 Kết quả:** {'✅ Chính xác!' if is_correct else '❌ Chưa đúng'}\n\n"
                    result_msg += f"**📖 Giải thích:** {explanation}"
                    
                    st.session_state[chat_key].append({"role": "assistant", "content": result_msg})
                    db.save_chat_message(user["id"], SUBJECT, "assistant", result_msg)
                    
                    st.session_state.waiting_for_answer = False
                    st.session_state.current_question = None
                    st.rerun()
                else:
                    st.warning("Vui lòng nhập câu trả lời!")
        return
    
    # ========== NHẬP TIN NHẮN ==========
    if prompt := st.chat_input("Nhập yêu cầu..."):
        # Lưu tin nhắn user
        db.save_chat_message(user["id"], SUBJECT, "user", prompt)
        st.session_state[chat_key].append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            msg_lower = prompt.lower()
            response = None
            
            # ===== BÀI TẬP =====
            if "bài tập" in msg_lower:
                topic = extract_topic_from_question(prompt)
                gemini_working = st.session_state.hybrid_tutor.gemini_available
                
                # 1. TÌM BÀI TẬP TRONG DATABASE TRƯỚC
                if topic:
                    st.info(f"🔍 Đang tìm bài tập về **{topic}** trong kho...")
                    # Lấy bài tập theo chủ đề, chưa làm
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
                    # CÓ BÀI TẬP TRONG DATABASE -> LẤY RA DÙNG
                    ex = random.choice(exercises)
                    st.session_state.waiting_for_answer = True
                    st.session_state.current_question = ex
                    st.markdown(f"**📝 Bài tập từ kho (đã lưu):**\n\n{ex['question']}")
                    if ex.get("options"):
                        for opt in ex["options"]:
                            st.markdown(f"  {opt}")
                    st.rerun()
                
                elif gemini_working:
                    # KHÔNG CÒN BÀI TẬP TRONG DATABASE -> GỌI GEMINI TẠO MỚI
                    with st.spinner(f"🤖 Đã làm hết bài về '{topic if topic else 'chủ đề này'}', Gemini đang tạo bài tập mới..."):
                        new_ex = st.session_state.hybrid_tutor.generate_exercise_with_gemini(
                            topic if topic else "Python", 
                            student_level
                        )
                        
                        if new_ex and new_ex.get("question"):
                            # Lưu bài tập mới vào database
                            exercise_id = save_exercise_to_db(new_ex, student_level, topic)
                            new_ex["exercise_id"] = exercise_id
                            st.session_state.waiting_for_answer = True
                            st.session_state.current_question = new_ex
                            
                            st.markdown(f"**✨ Bài tập mới (Gemini tạo - đã lưu vào kho):**\n\n{new_ex['question']}")
                            if new_ex.get("options"):
                                for opt in new_ex["options"]:
                                    st.markdown(f"  {opt}")
                            st.markdown("---")
                            st.info("💡 Bài tập này sẽ được dùng cho lần sau!")
                            st.rerun()
                        else:
                            st.error("❌ **Không thể tạo bài tập mới!** Vui lòng thử lại sau.")
                else:
                    # KHÔNG CÓ BÀI TẬP VÀ KHÔNG CÓ GEMINI
                    if topic:
                        st.warning(f"📚 **Chưa có bài tập nào về '{topic}' trong kho!**")
                    else:
                        st.warning("📚 **Chưa có bài tập nào trong kho!**")
                    
                    if st.button("🔄 Làm lại bài tập cũ"):
                        db.reset_exercise_history(user["id"])
                        st.rerun()
            # ===== LÀM ĐỀ =====
            elif "làm đề" in msg_lower or "đề thi" in msg_lower or "thi thử" in msg_lower:
                exams = db.get_exams(subject=SUBJECT, level=student_level)
                
                if exams:
                    exam = random.choice(exams)
                    st.session_state.is_doing_exam = True
                    st.session_state.current_exam = {
                        "exam_id": f"EXAM_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "title": exam["title"],
                        "questions": exam["questions"],
                        "total": len(exam["questions"]),
                        "time_limit": exam.get("time_limit", 30),
                        "answers": []
                    }
                    st.session_state.exam_current_index = 0
                    st.session_state.exam_start_time = None
                    response = f"📝 **{exam['title']}**\n✨ Gồm {len(exam['questions'])} câu\n⏰ Thời gian: {exam.get('time_limit', 30)} phút\n\n👉 Trả lời từng câu bên dưới!"
                    st.markdown(response)
                    st.session_state[chat_key].append({"role": "assistant", "content": response})
                    db.save_chat_message(user["id"], SUBJECT, "assistant", response)
                    st.rerun()
                else:
                    error_msg = "📚 **Chưa có đề thi nào trong hệ thống!**\n\n🔧 **Hướng dẫn:**\n- Yêu cầu giáo viên tạo đề thi\n- Giáo viên vào tab '📝 Đề thi' → 'Tạo đề mới'"
                    st.markdown(error_msg)
                    st.session_state[chat_key].append({"role": "assistant", "content": error_msg})
                    db.save_chat_message(user["id"], SUBJECT, "assistant", error_msg)
            
            # ===== HỎI LÝ THUYẾT =====
            else:
                with st.spinner("🤔 Đang suy nghĩ..."):
                    result = st.session_state.hybrid_tutor.answer(prompt, subject=SUBJECT)
                    response = result["answer"]
                    st.markdown(response)
                    st.session_state[chat_key].append({"role": "assistant", "content": response})
                    db.save_chat_message(user["id"], SUBJECT, "assistant", response)
        
        # Lưu phản hồi AI (nếu chưa được lưu)
        if response and not st.session_state.get("waiting_for_answer", False) and not st.session_state.get("is_doing_exam", False):
            db.save_chat_message(user["id"], SUBJECT, "assistant", response)