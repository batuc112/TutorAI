import json
import re
import os
import random
from datetime import datetime
from ml_classifier import MLQuestionClassifier
import database as db
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class HybridTutor:
    def __init__(self, api_key=None):
        self.memory = self.load_memory()
        self.stats = self.load_stats()
        
        self.ml_classifier = MLQuestionClassifier()
        
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.gemini_available = False
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
                self.gemini_available = True
                print("✅ Gemini API đã sẵn sàng")
            except Exception as e:
                print(f"⚠️ Lỗi Gemini: {e}")
                self.gemini_available = False
        else:
            print("⚠️ Chưa có Gemini API key")
        
        print("🤖 AI Tutor đã sẵn sàng!")

    def load_memory(self):
        try:
            with open("ai_memory.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"qa_pairs": {}, "explanations": {}}

    def save_memory(self):
        with open("ai_memory.json", "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)

    def load_stats(self):
        try:
            with open("ai_stats.json", "r") as f:
                return json.load(f)
        except:
            return {"from_memory": 0, "from_db": 0, "from_gemini": 0}

    def save_stats(self):
        with open("ai_stats.json", "w") as f:
            json.dump(self.stats, f)

    def call_gemini(self, prompt):
        if not self.gemini_available:
            return None
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini lỗi: {e}")
            return None

    def explain_answer_with_gemini(self, question, user_answer, correct_answer, topic):
        memory_key = f"{question}_{user_answer}".lower()
        
        if memory_key in self.memory.get("explanations", {}):
            return self.memory["explanations"][memory_key]
        
        if not self.gemini_available:
            return self.fallback_explanation(question, user_answer, correct_answer, topic)
        
        prompt = f"""
        Bạn là gia sư AI. Hãy giải thích đáp án cho câu hỏi sau.

        CÂU HỎI: {question}
        HỌC SINH TRẢ LỜI: {user_answer}
        ĐÁP ÁN ĐÚNG: {correct_answer}
        CHỦ ĐỀ: {topic}

        Yêu cầu: Giải thích ngắn gọn, tối đa 3 câu, dễ hiểu.
        Trả lời bằng tiếng Việt.
        """
        
        explanation = self.call_gemini(prompt)
        
        if explanation:
            if "explanations" not in self.memory:
                self.memory["explanations"] = {}
            self.memory["explanations"][memory_key] = explanation
            self.save_memory()
            self.stats["from_gemini"] = self.stats.get("from_gemini", 0) + 1
            self.save_stats()
            return explanation
        
        return self.fallback_explanation(question, user_answer, correct_answer, topic)

    def fallback_explanation(self, question, user_answer, correct_answer, topic):
        if user_answer.lower() == correct_answer.lower():
            return f"✅ Chính xác! Đáp án đúng là {correct_answer}.\n\n📖 {topic} là một khái niệm quan trọng."
        else:
            return f"❌ Chưa đúng. Đáp án đúng là: {correct_answer}\n\n📖 Hãy xem lại kiến thức về '{topic}'."

    def generate_exercise_with_gemini(self, topic, level):
        if not self.gemini_available:
            return self.generate_exercise_from_template(topic, level)
        
        prompt = f"""
        Hãy tạo một câu hỏi {level} về chủ đề "{topic}" trong lập trình Python.
        
        Yêu cầu:
        - Nếu là trắc nghiệm: có 4 lựa chọn A, B, C, D
        - Nếu là điền khuyết: có chỗ trống _____
        
        Trả về JSON:
        {{
            "type": "multiple_choice",
            "question": "nội dung câu hỏi",
            "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
            "answer": "A",
            "explanation": "giải thích ngắn"
        }}
        """
        
        result = self.call_gemini(prompt)
        if result:
            try:
                result = re.sub(r'^```json\s*', '', result)
                result = re.sub(r'\s*```$', '', result)
                data = json.loads(result)
                return data
            except:
                pass
        return self.generate_exercise_from_template(topic, level)

    def generate_exercise_from_template(self, topic, level):
        topic_cap = topic.capitalize() if topic else "Chủ đề"
        return {
            "type": "essay",
            "question": f"{topic_cap} là gì? Hãy giải thích ngắn gọn.",
            "options": [],
            "answer": f"Đáp án tham khảo: {topic_cap} là một khái niệm quan trọng.",
            "explanation": f"Đây là câu hỏi về {topic}."
        }

    def answer(self, question, subject=None):
        if not question or not question.strip():
            return {"answer": "Vui lòng nhập câu hỏi!", "source": "system"}
        
        normalized = question.lower().strip()
        
        if normalized in self.memory["qa_pairs"]:
            self.stats["from_memory"] += 1
            self.save_stats()
            return {"answer": self.memory["qa_pairs"][normalized], "source": "memory"}
        
        lessons = db.get_lessons(subject=subject)
        for lesson in lessons:
            if any(word in question.lower() for word in lesson["title"].lower().split()):
                answer = f"📖 **{lesson['title']}**\n\n{lesson['theory'][:500]}"
                self.learn_new_question(question, answer, subject)
                return {"answer": answer, "source": "database"}
        
        if self.gemini_available:
            subject_hint = f"Môn học: {subject}" if subject else ""
            gemini_answer = self.call_gemini(f"Học sinh hỏi: {question}\n{subject_hint}\nHãy trả lời bằng tiếng Việt, ngắn gọn, dễ hiểu.")
            if gemini_answer:
                self.learn_new_question(question, gemini_answer, subject)
                self.stats["from_gemini"] = self.stats.get("from_gemini", 0) + 1
                self.save_stats()
                return {"answer": gemini_answer, "source": "gemini"}
        
        return {"answer": "Tôi chưa có câu trả lời. Hãy yêu cầu giáo viên thêm bài học!", "source": "fallback"}

    def learn_new_question(self, question, answer, subject=None):
        normalized = question.lower().strip()
        key = f"{subject}_{normalized}" if subject else normalized
        self.memory["qa_pairs"][key] = answer
        self.save_memory()
        return True

    def get_stats(self):
        return {
            "total_learned": len(self.memory["qa_pairs"]),
            "from_memory": self.stats["from_memory"],
            "from_db": self.stats["from_db"],
            "from_gemini": self.stats.get("from_gemini", 0),
            "gemini_available": self.gemini_available
        }