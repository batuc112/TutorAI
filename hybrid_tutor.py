import json
import re
import os
import random
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import database as db
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

class HybridTutor:
    def __init__(self, api_key=None):

        self.memory = self.load_memory()
        self.stats = self.load_stats()
        
        # ========== KHỞI TẠO EMBEDDING MODEL ==========
        print("🔄 Đang tải mô hình Embedding tiếng Việt...")
        self.embedding_model = SentenceTransformer('bkai-foundation-models/vietnamese-bi-encoder')
        print("✅ Đã tải xong mô hình Embedding!")
        
        # ========== DANH SÁCH CHỦ ĐỀ ==========
        self.topics = ["biến", "hàm", "vòng lặp", "list", "tuple", "dictionary", "class", "đệ quy", "file", "module"]
        self.topic_embeddings = self.embedding_model.encode(self.topics)
        
        # ========== RULE-BASED PATTERNS ==========
        self.question_patterns = {
            "definition": ["gì", "là gì", "thế nào", "khái niệm", "định nghĩa", "giải thích"],
            "example": ["ví dụ", "lấy ví dụ", "cho ví dụ", "minh họa"],
            "how_to": ["cách", "làm thế nào", "hướng dẫn", "các bước"],
            "exercise": ["bài tập", "làm bài", "thực hành", "bài thực hành"],
            "compare": ["so sánh", "khác nhau", "phân biệt", "giống nhau"],
        }
        
        # Tải dữ liệu huấn luyện
        self.training_questions = []
        self.training_labels = []
        self.training_embeddings = None
        self.load_training_data()
        
        # ========== KHỞI TẠO GEMINI ==========
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.gemini_available = False
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                self.gemini_available = True
                print("✅ Gemini API đã sẵn sàng")
            except Exception as e:
                print(f"⚠️ Lỗi Gemini: {e}")
                self.gemini_available = False
        else:
            print("⚠️ Chưa có Gemini API key")
        
        print("🤖 AI Tutor đã sẵn sàng (Embedding tìm chủ đề + Rule-based phân loại)!")
    
    def load_training_data(self):
        """Load dữ liệu huấn luyện và tạo vector embedding"""
        data = db.get_all_training_data()
        
        if not data or len(data) == 0:
            print("⚠️ Chưa có dữ liệu huấn luyện!")
            self.training_embeddings = None
            return
        
        self.training_questions = [item[0] for item in data]
        self.training_labels = [item[1] for item in data]
        
        print(f"🔄 Đang tạo vector embedding cho {len(self.training_questions)} câu hỏi...")
        self.training_embeddings = self.embedding_model.encode(self.training_questions, show_progress_bar=True)
        print(f"✅ Đã tạo xong {len(self.training_embeddings)} vector embedding!")
    
    def normalize_question(self, question):
        q_lower = question.lower().strip()

        patterns = [
            r"(.+?)\s+là gì",
            r"thế nào là\s+(.+)",
            r"khái niệm\s+(.+)",
            r"định nghĩa\s+(.+)",
            r"giải thích\s+(.+)",
            r"hãy giải thích\s+(.+)",
            r"cho tôi biết\s+(.+)",
            r"(.+?)\s+được hiểu như thế nào",
            r"(.+?)\s+nghĩa là gì",
        ]

        for pattern in patterns:
            match = re.search(pattern, q_lower)

            if match:
                topic = match.group(1).strip()

                # chuẩn hóa về cùng 1 dạng
                normalized = f"{topic} là gì"

                print(f"🔄 Chuẩn hóa: '{question}' → '{normalized}'")

                return normalized

        return q_lower
    def load_training_data(self):
        """Load dữ liệu huấn luyện và tạo vector embedding"""
        data = db.get_all_training_data()
            
        if not data or len(data) == 0:
            print("⚠️ Chưa có dữ liệu huấn luyện!")
            self.training_embeddings = None
            return
            
        self.training_questions = [item[0] for item in data]
        self.training_labels = [item[1] for item in data]
            
        print(f"🔄 Đang tạo vector embedding cho {len(self.training_questions)} câu hỏi...")
        self.training_embeddings = self.embedding_model.encode(self.training_questions, show_progress_bar=True)
        print(f"✅ Đã tạo xong {len(self.training_embeddings)} vector embedding!")

    def extract_topic_by_embedding(self, question):
        """Dùng Embedding để tìm chủ đề chính trong câu hỏi"""
        if not question or not isinstance(question, str):
            return None, 0
        
        try:
            question_embedding = self.embedding_model.encode([question])
            similarities = cosine_similarity(question_embedding, self.topic_embeddings)[0]
            
            best_idx = similarities.argmax()
            best_score = similarities[best_idx]
            
            if best_score > 0.5:
                return self.topics[best_idx], best_score
            return None, best_score
        except:
            return None, 0

    def classify_by_rule(self, question):
        """Phân loại câu hỏi bằng Rule-based"""
        q_lower = question.lower()
        
        definition_keywords = [
            "gì", "là gì", "thế nào", "khái niệm", "định nghĩa", 
            "giải thích", "thế nào là", "được hiểu", "nghĩa là"
        ]
        example_keywords = ["ví dụ", "lấy ví dụ", "cho ví dụ", "minh họa"]
        howto_keywords = ["cách", "làm thế nào", "hướng dẫn", "các bước"]
        exercise_keywords = ["bài tập", "làm bài", "thực hành", "bài thực hành", "đề"]
        compare_keywords = ["so sánh", "khác nhau", "phân biệt", "giống nhau"]
        
        if any(kw in q_lower for kw in definition_keywords):
            return "definition"
        if any(kw in q_lower for kw in example_keywords):
            return "example"
        if any(kw in q_lower for kw in howto_keywords):
            return "how_to"
        if any(kw in q_lower for kw in exercise_keywords):
            return "exercise"
        if any(kw in q_lower for kw in compare_keywords):
            return "compare"
        
        return "general"

    def classify_question(self, question):
        """Kết hợp: Embedding tìm chủ đề + Rule-based phân loại"""
        
        # Bước 1: Embedding tìm chủ đề
        topic, topic_score = self.extract_topic_by_embedding(question)
        
        # Bước 2: Rule-based phân loại câu hỏi
        q_type = self.classify_by_rule(question)
        
        print(f"📝 Câu hỏi: {question}")
        print(f"   → Chủ đề (Embedding): {topic} (độ tin cậy: {topic_score:.2%})")
        print(f"   → Loại (Rule-based): {q_type}")
        
        # Bước 3: Lưu topic vào session state
        if topic:
            st.session_state.current_topic = topic
        
        return q_type, 0.8

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
        
        normalized_q = self.normalize_question(question)
        
        if normalized_q in self.memory["qa_pairs"]:
            self.stats["from_memory"] += 1
            self.save_stats()
            return {"answer": self.memory["qa_pairs"][normalized_q], "source": "memory"}
        
        category, confidence = self.classify_question(question)
        
        if category == "definition":
            answer = self.get_definition_answer(None, question, subject)
        elif category == "example":
            answer = self.get_example_answer(None, question, subject)
        elif category == "how_to":
            answer = self.get_howto_answer(None, question, subject)
        elif category == "exercise":
            answer = self.get_exercise_answer(None, question, subject)
        else:
            answer = None
        
        if answer:

            self.memory["qa_pairs"][normalized_q] = answer
            self.save_memory()
            return {"answer": answer, "source": "database"}
        
        if self.gemini_available:
            gemini_answer = self.call_gemini(f"Học sinh hỏi: {question}\nHãy trả lời bằng tiếng Việt, ngắn gọn, dễ hiểu.")
            if gemini_answer:
                # LƯU VÀO BỘ NHỚ
                self.memory["qa_pairs"][normalized_q] = gemini_answer
                self.save_memory()
                return {"answer": gemini_answer, "source": "gemini"}
        
        return {"answer": "🤔 Tôi chưa hiểu câu hỏi. Hãy thử hỏi cách khác!", "source": "fallback"}

    def get_definition_answer(self, topic, question, subject):
        """Trả lời câu hỏi định nghĩa"""
        normalized_q = self.normalize_question(question)
        print(f"🔄 Câu hỏi gốc: {question}")
        print(f"🔄 Câu hỏi chuẩn hóa: {normalized_q}")
        
        lessons = db.get_lessons(subject=subject)
        for lesson in lessons:
            # So sánh với câu đã chuẩn hóa
            if any(word in normalized_q for word in lesson["title"].lower().split()):
                return f"📖 **{lesson['title']}**\n\n{lesson['theory'][:800]}"
        # So sánh với câu gốc
            if any(word in question.lower() for word in lesson["title"].lower().split()):
                return f"📖 **{lesson['title']}**\n\n{lesson['theory'][:800]}"
        if not topic:
            topic = self.extract_topic_by_embedding(question)[0]
        
        if topic:
            lessons = db.get_lessons(subject=subject)
            for lesson in lessons:
                if topic in lesson["title"].lower():
                    return f"📖 **{lesson['title']}**\n\n{lesson['theory'][:800]}"
        
        if self.gemini_available:
            return self.call_gemini(f"Hãy định nghĩa '{topic if topic else 'khái niệm'}' trong Python một cách ngắn gọn.")
        return f"📖 **{topic.capitalize() if topic else 'Chủ đề'}**\n\nĐang cập nhật nội dung."

    def get_example_answer(self, topic, question, subject):
        """Trả lời yêu cầu ví dụ"""
        if topic:
            lessons = db.get_lessons(subject=subject)
            for lesson in lessons:
                if topic in lesson["title"].lower() and lesson.get("examples"):
                    return f"📖 **{lesson['title']}**\n\n💡 **Ví dụ:**\n- " + "\n- ".join(lesson["examples"][:3])
        
        if self.gemini_available:
            return self.call_gemini(f"Hãy cho 2-3 ví dụ về '{topic if topic else 'chủ đề này'}' trong Python.")
        return "💡 Chưa có ví dụ. Hãy yêu cầu giáo viên thêm!"

    def get_howto_answer(self, topic, question, subject):
        """Trả lời câu hỏi cách làm"""
        if topic:
            lessons = db.get_lessons(subject=subject)
            for lesson in lessons:
                if topic in lesson["title"].lower():
                    return f"🔧 **Hướng dẫn về {topic}:**\n{lesson['theory'][:500]}"
        
        if self.gemini_available:
            return self.call_gemini(f"Hãy hướng dẫn cách sử dụng '{topic if topic else 'chủ đề này'}' trong Python.")
        return f"🔧 Chưa có hướng dẫn về '{topic if topic else 'chủ đề này'}'."

    def get_exercise_answer(self, topic, question, subject):
        """Trả lời yêu cầu bài tập"""
        exercises = db.get_exercises(subject=subject)
        if exercises:
            ex = random.choice(exercises)
            return f"📝 **Bài tập:**\n{ex['question']}\n\n💡 Hãy trả lời và tôi sẽ chấm điểm!"
        
        if self.gemini_available and topic:
            return self.call_gemini(f"Hãy tạo một bài tập về '{topic}' cho người mới học Python.")
        return "📚 Chưa có bài tập. Hãy yêu cầu giáo viên thêm!"

    def get_compare_answer(self, topic, question, subject):
        """Trả lời câu hỏi so sánh"""
        if self.gemini_available:
            return self.call_gemini(f"Hãy so sánh các khái niệm trong câu hỏi sau: {question}")
        return "📊 Chưa có dữ liệu so sánh."

    def generate_exercise_with_gemini(self, topic, level):
        """Sinh bài tập mới bằng Gemini"""
        if not self.gemini_available:
            return self.get_fallback_exercise(topic, level)
        
        prompt = f"""
        Hãy tạo MỘT câu hỏi trắc nghiệm {level} về chủ đề "{topic}" trong lập trình Python.
        
        TRẢ VỀ JSON:
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
                result = result.strip()
                if result.startswith("```json"):
                    result = result[7:]
                if result.startswith("```"):
                    result = result[3:]
                if result.endswith("```"):
                    result = result[:-3]
                result = result.strip()
                data = json.loads(result)
                return data
            except:
                return self.get_fallback_exercise(topic, level)
        return self.get_fallback_exercise(topic, level)

    def get_fallback_exercise(self, topic, level):
        """Bài tập dự phòng"""
        return {
            "type": "multiple_choice",
            "question": f"Khái niệm '{topic}' trong Python là gì?",
            "options": [
                "A. Một khái niệm cơ bản",
                "B. Một thư viện Python",
                "C. Một hàm dựng sẵn",
                "D. Một lỗi thường gặp"
            ],
            "answer": "A",
            "explanation": f"'{topic}' là một khái niệm quan trọng."
        }

    def get_stats(self):
        return {
            "total_learned": len(self.memory["qa_pairs"]),
            "from_memory": self.stats["from_memory"],
            "from_db": self.stats["from_db"],
            "from_gemini": self.stats.get("from_gemini", 0),
            "gemini_available": self.gemini_available
        }