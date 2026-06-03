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

    def answer(self, question, subject=None):
        if not question or not question.strip():
            return {"answer": "Vui lòng nhập câu hỏi!", "source": "system"}
        
        normalized = question.lower().strip()
        
        # 1. Kiểm tra bộ nhớ
        if normalized in self.memory["qa_pairs"]:
            self.stats["from_memory"] += 1
            self.save_stats()
            return {"answer": self.memory["qa_pairs"][normalized], "source": "memory"}
        
        # 2. Tìm trong bài học
        lessons = db.get_lessons(subject=subject)
        for lesson in lessons:
            if any(word in question.lower() for word in lesson["title"].lower().split()):
                answer = f"📖 **{lesson['title']}**\n\n{lesson['theory'][:800]}"
                self.memory["qa_pairs"][normalized] = answer
                self.save_memory()
                return {"answer": answer, "source": "database"}
        
        # 3. Gọi Gemini
        if self.gemini_available:
            gemini_answer = self.call_gemini(f"Học sinh hỏi: {question}\n\nHãy trả lời bằng tiếng Việt, ngắn gọn, dễ hiểu, có ví dụ cụ thể.")
            if gemini_answer:
                self.memory["qa_pairs"][normalized] = gemini_answer
                self.save_memory()
                self.stats["from_gemini"] = self.stats.get("from_gemini", 0) + 1
                self.save_stats()
                return {"answer": gemini_answer, "source": "gemini"}
        
        # 4. Fallback
        return {"answer": "🤔 Tôi chưa có câu trả lời cho câu hỏi này. Hãy thử hỏi cách khác hoặc yêu cầu giáo viên thêm bài học!", "source": "fallback"}

    def generate_exercise_with_gemini(self, topic, level):
        """Sinh bài tập mới bằng Gemini"""
        if not self.gemini_available:
            return self.get_fallback_exercise(topic, level)
        
        prompt = f"""
        Hãy tạo MỘT câu hỏi trắc nghiệm {level} về chủ đề "{topic}" trong lập trình Python.
        
        YÊU CẦU:
        - Câu hỏi phải rõ ràng, dễ hiểu
        - Có 4 lựa chọn A, B, C, D
        - Đáp án đúng là một trong 4 lựa chọn
        
        TRẢ VỀ DUY NHẤT JSON (không có text khác, không có markdown):
        {{
            "type": "multiple_choice",
            "question": "nội dung câu hỏi",
            "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
            "answer": "A",
            "explanation": "giải thích ngắn gọn tại sao đáp án này đúng"
        }}
        """
        
        result = self.call_gemini(prompt)
        if result:
            try:
                result = result.strip()
                if result.startswith("```json"):
                    result = result[7:]
                if result.startswith("```"):
                    result = result[3:]
                if result.endswith("```"):
                    result = result[:-3]
                result = result.strip()
                
                data = json.loads(result)
                
                if not data.get("question") or not data.get("options") or len(data["options"]) != 4:
                    return self.get_fallback_exercise(topic, level)
                if not data.get("answer") or data["answer"] not in ["A", "B", "C", "D"]:
                    return self.get_fallback_exercise(topic, level)
                
                return data
            except:
                return self.get_fallback_exercise(topic, level)
        
        return self.get_fallback_exercise(topic, level)

    def get_fallback_exercise(self, topic, level):
        """Bài tập dự phòng khi Gemini không hoạt động"""
        topic_lower = topic.lower() if topic else "python"
        
        templates = {
            "biến": {
                "type": "multiple_choice",
                "question": "Biến trong Python được dùng để làm gì?",
                "options": [
                    "A. Lưu trữ dữ liệu",
                    "B. Định nghĩa hàm",
                    "C. Tạo vòng lặp",
                    "D. In ra màn hình"
                ],
                "answer": "A",
                "explanation": "Biến dùng để lưu trữ dữ liệu trong bộ nhớ."
            },
            "hàm": {
                "type": "multiple_choice",
                "question": "Từ khóa nào dùng để định nghĩa hàm trong Python?",
                "options": [
                    "A. function",
                    "B. def",
                    "C. define",
                    "D. func"
                ],
                "answer": "B",
                "explanation": "Trong Python, hàm được định nghĩa bằng từ khóa 'def'."
            },
            "vòng lặp": {
                "type": "multiple_choice",
                "question": "Vòng lặp nào sau đây dùng để lặp với số lần xác định?",
                "options": [
                    "A. while",
                    "B. for",
                    "C. do-while",
                    "D. loop"
                ],
                "answer": "B",
                "explanation": "Vòng lặp 'for' thường dùng khi biết trước số lần lặp."
            },
            "list": {
                "type": "multiple_choice",
                "question": "Kiểu dữ liệu nào dùng để lưu trữ danh sách các phần tử có thể thay đổi?",
                "options": [
                    "A. Tuple",
                    "B. List",
                    "C. Dictionary",
                    "D. Set"
                ],
                "answer": "B",
                "explanation": "List là kiểu dữ liệu có thể thay đổi, lưu trữ nhiều phần tử."
            }
        }
        
        for key, template in templates.items():
            if key in topic_lower:
                return template
        
        return {
            "type": "multiple_choice",
            "question": f"Khái niệm '{topic}' trong lập trình Python là gì?",
            "options": [
                "A. Một khái niệm cơ bản trong lập trình",
                "B. Một thư viện Python",
                "C. Một hàm dựng sẵn",
                "D. Một lỗi thường gặp"
            ],
            "answer": "A",
            "explanation": f"'{topic}' là một khái niệm quan trọng trong lập trình."
        }

    def get_stats(self):
        return {
            "total_learned": len(self.memory["qa_pairs"]),
            "from_memory": self.stats["from_memory"],
            "from_db": self.stats["from_db"],
            "from_gemini": self.stats.get("from_gemini", 0),
            "gemini_available": self.gemini_available
        }