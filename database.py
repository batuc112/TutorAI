import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "data/tutor.db"

def get_connection():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Bảng users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT,
        created_at TEXT
    )
    ''')
    
    # Bảng student_profiles
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS student_profiles (
        user_id INTEGER PRIMARY KEY,
        level TEXT DEFAULT 'beginner',
        topics_learned TEXT,
        quiz_scores TEXT,
        weak_topics TEXT,
        score_history TEXT,
        exam_scores TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # Bảng lessons
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lesson_id TEXT UNIQUE,
        title TEXT,
        theory TEXT,
        examples TEXT,
        exercises TEXT,
        subject TEXT,
        level TEXT,
        tags TEXT,
        teacher_id INTEGER,
        created_at TEXT,
        FOREIGN KEY (teacher_id) REFERENCES users(id)
    )
    ''')
    
    # Bảng exercises
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exercise_id TEXT UNIQUE,
        question TEXT,
        type TEXT,
        options TEXT,
        answer TEXT,
        subject TEXT,
        level TEXT,
        tags TEXT,
        teacher_id INTEGER,
        auto_generated INTEGER DEFAULT 0,
        correct_explanation TEXT,
        created_at TEXT,
        FOREIGN KEY (teacher_id) REFERENCES users(id)
    )
    ''')
    
    # Bảng exams
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id TEXT UNIQUE,
        title TEXT,
        subject TEXT,
        level TEXT,
        questions TEXT,
        time_limit INTEGER DEFAULT 30,
        created_at TEXT,
        teacher_id INTEGER,
        is_active INTEGER DEFAULT 1,
        FOREIGN KEY (teacher_id) REFERENCES users(id)
    )
    ''')
    
    # Bảng quiz_history
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quiz_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        exercise_id TEXT,
        score INTEGER,
        answer TEXT,
        explanation TEXT,
        is_exam INTEGER DEFAULT 0,
        completed_at TEXT,
        FOREIGN KEY (student_id) REFERENCES users(id)
    )
    ''')
    # Thêm vào hàm init_database()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        subject TEXT,
        usage_count INTEGER DEFAULT 0,
        created_at TEXT,
        teacher_id INTEGER,
        FOREIGN KEY (teacher_id) REFERENCES users(id)
    )
    ''')
    # Bảng training_data
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS training_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        category TEXT,
        created_at TEXT
    )
    ''')
    
    # Bảng student_exercise_history
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS student_exercise_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        exercise_id TEXT,
        is_exam INTEGER DEFAULT 0,
        completed_at TEXT,
        FOREIGN KEY (student_id) REFERENCES users(id)
    )
    ''')
    
    # Bảng chat_history
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject TEXT,
        role TEXT,
        content TEXT,
        created_at TEXT,
        FOREIGN KEY (student_id) REFERENCES users(id)
    )
    ''')
    
    # Thêm tài khoản mặc định
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        default_users = [
            ("student1", "123456", "student", "Nguyễn Văn An"),
            ("student2", "123456", "student", "Trần Thị Bình"),
            ("teacher1", "123456", "teacher", "Cô giáo Mai"),
        ]
        for user in default_users:
            cursor.execute('''
            INSERT INTO users (username, password, role, full_name, created_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (user[0], user[1], user[2], user[3], datetime.now().isoformat()))
            
            if user[2] == "student":
                user_id = cursor.lastrowid
                cursor.execute('''
                INSERT INTO student_profiles (user_id, level, topics_learned, quiz_scores, weak_topics, score_history, exam_scores)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, "beginner", "[]", "{}", "[]", "[]", "[]"))
    
    # ========== DỮ LIỆU HUẤN LUYỆN (230 CÂU) ==========
    cursor.execute("SELECT COUNT(*) FROM training_data")
    if cursor.fetchone()[0] == 0:
        training_data = [
            # ===== DEFINITION (50 câu) =====
            ("biến trong python là gì", "definition"),
            ("thế nào là hàm trong lập trình", "definition"),
            ("khái niệm vòng lặp là gì", "definition"),
            ("class trong oop là gì", "definition"),
            ("đệ quy là gì", "definition"),
            ("list trong python là gì", "definition"),
            ("tuple là gì", "definition"),
            ("dictionary là gì", "definition"),
            ("set là gì", "definition"),
            ("module là gì", "definition"),
            ("thư viện là gì", "definition"),
            ("exception là gì", "definition"),
            ("file handling là gì", "definition"),
            ("lambda function là gì", "definition"),
            ("decorator là gì", "definition"),
            ("generator là gì", "definition"),
            ("iterator là gì", "definition"),
            ("polymorphism là gì", "definition"),
            ("inheritance là gì", "definition"),
            ("encapsulation là gì", "definition"),
            ("abstraction là gì", "definition"),
            ("magic method là gì", "definition"),
            ("context manager là gì", "definition"),
            ("namespace là gì", "definition"),
            ("scope là gì", "definition"),
            ("closure là gì", "definition"),
            ("coroutine là gì", "definition"),
            ("async function là gì", "definition"),
            ("await là gì", "definition"),
            ("threading là gì", "definition"),
            ("multiprocessing là gì", "definition"),
            ("socket là gì", "definition"),
            ("api là gì", "definition"),
            ("rest api là gì", "definition"),
            ("json là gì", "definition"),
            ("xml là gì", "definition"),
            ("sql là gì", "definition"),
            ("database là gì", "definition"),
            ("orm là gì", "definition"),
            ("git là gì", "definition"),
            ("github là gì", "definition"),
            ("pip là gì", "definition"),
            ("virtual environment là gì", "definition"),
            ("debug là gì", "definition"),
            ("unit test là gì", "definition"),
            ("ci cd là gì", "definition"),
            ("docker là gì", "definition"),
            ("kubernetes là gì", "definition"),
            ("cloud computing là gì", "definition"),
            ("machine learning là gì", "definition"),
            
            # ===== EXAMPLE (50 câu) =====
            ("cho tôi ví dụ về biến", "example"),
            ("lấy ví dụ về hàm trong python", "example"),
            ("ví dụ về vòng lặp for", "example"),
            ("cho ví dụ về câu lệnh if", "example"),
            ("ví dụ về list comprehension", "example"),
            ("minh họa cách dùng dictionary", "example"),
            ("ví dụ về đệ quy tính giai thừa", "example"),
            ("lấy ví dụ về xử lý file", "example"),
            ("cho ví dụ về try except", "example"),
            ("ví dụ về class và object", "example"),
            ("ví dụ về lambda function", "example"),
            ("cho ví dụ về decorator", "example"),
            ("ví dụ về generator", "example"),
            ("lấy ví dụ về map và filter", "example"),
            ("ví dụ về cách dùng enumerate", "example"),
            ("cho ví dụ về zip function", "example"),
            ("ví dụ về split và join", "example"),
            ("lấy ví dụ về list slicing", "example"),
            ("ví dụ về string formatting", "example"),
            ("cho ví dụ về f-string", "example"),
            ("ví dụ về regular expression", "example"),
            ("lấy ví dụ về datetime", "example"),
            ("ví dụ về random module", "example"),
            ("cho ví dụ về math module", "example"),
            ("ví dụ về os module", "example"),
            ("lấy ví dụ về sys module", "example"),
            ("ví dụ về json module", "example"),
            ("cho ví dụ về requests module", "example"),
            ("ví dụ về threading", "example"),
            ("lấy ví dụ về multiprocessing", "example"),
            ("ví dụ về socket programming", "example"),
            ("cho ví dụ về api call", "example"),
            ("ví dụ về sqlite3", "example"),
            ("lấy ví dụ về list append", "example"),
            ("ví dụ về dict update", "example"),
            ("cho ví dụ về set operations", "example"),
            ("ví dụ về tuple unpacking", "example"),
            ("lấy ví dụ về args và kwargs", "example"),
            ("ví dụ về static method", "example"),
            ("cho ví dụ về class method", "example"),
            ("ví dụ về property decorator", "example"),
            ("lấy ví dụ về super function", "example"),
            ("ví dụ về multiple inheritance", "example"),
            ("cho ví dụ về method overriding", "example"),
            ("ví dụ về abstract class", "example"),
            ("lấy ví dụ về context manager", "example"),
            ("ví dụ về async await", "example"),
            ("cho ví dụ về aiohttp", "example"),
            ("ví dụ về type hints", "example"),
            ("lấy ví dụ về dataclass", "example"),
            
            # ===== HOW_TO (50 câu) =====
            ("cách khai báo biến trong python", "how_to"),
            ("làm thế nào để tạo một hàm", "how_to"),
            ("hướng dẫn viết vòng lặp while", "how_to"),
            ("cách sử dụng câu lệnh if else", "how_to"),
            ("làm sao để thêm phần tử vào list", "how_to"),
            ("cách xóa phần tử khỏi dictionary", "how_to"),
            ("hướng dẫn đọc file trong python", "how_to"),
            ("làm thế nào để bắt lỗi ngoại lệ", "how_to"),
            ("cách viết hàm đệ quy", "how_to"),
            ("làm sao để import module", "how_to"),
            ("cách tạo class trong python", "how_to"),
            ("hướng dẫn cài đặt thư viện pip", "how_to"),
            ("cách chạy file .py từ terminal", "how_to"),
            ("làm thế nào để sắp xếp list", "how_to"),
            ("cách tạo virtual environment", "how_to"),
            ("hướng dẫn sử dụng git", "how_to"),
            ("làm thế nào để push code lên github", "how_to"),
            ("cách viết unit test", "how_to"),
            ("hướng dẫn debug python", "how_to"),
            ("làm sao để tạo API với flask", "how_to"),
            ("cách kết nối database", "how_to"),
            ("hướng dẫn sử dụng sqlite3", "how_to"),
            ("làm thế nào để đọc file csv", "how_to"),
            ("cách xử lý json trong python", "how_to"),
            ("hướng dẫn gửi request http", "how_to"),
            ("làm sao để tạo decorator", "how_to"),
            ("cách sử dụng generator", "how_to"),
            ("hướng dẫn dùng lambda function", "how_to"),
            ("làm thế nào để sử dụng map filter", "how_to"),
            ("cách dùng list comprehension", "how_to"),
            ("hướng dẫn dùng dict comprehension", "how_to"),
            ("làm sao để set comprehension", "how_to"),
            ("cách sử dụng enumerate", "how_to"),
            ("hướng dẫn dùng zip function", "how_to"),
            ("làm thế nào để dùng args kwargs", "how_to"),
            ("cách tạo static method", "how_to"),
            ("hướng dẫn dùng class method", "how_to"),
            ("làm sao để dùng property decorator", "how_to"),
            ("cách dùng super function", "how_to"),
            ("hướng dẫn multiple inheritance", "how_to"),
            ("làm thế nào để override method", "how_to"),
            ("cách tạo abstract class", "how_to"),
            ("hướng dẫn context manager", "how_to"),
            ("làm sao để dùng async await", "how_to"),
            ("cách tạo coroutine", "how_to"),
            ("hướng dẫn dùng asyncio", "how_to"),
            ("làm thế nào để dùng threading", "how_to"),
            ("cách dùng multiprocessing", "how_to"),
            ("hướng dẫn dùng socket", "how_to"),
            ("làm sao để tạo cli app", "how_to"),
            
            # ===== EXERCISE (50 câu) =====
            ("cho tôi bài tập về biến", "exercise"),
            ("gửi bài tập về hàm trong python", "exercise"),
            ("làm bài tập về vòng lặp", "exercise"),
            ("bài tập về list trong python", "exercise"),
            ("cho bài tập về dictionary", "exercise"),
            ("bài tập về xử lý chuỗi", "exercise"),
            ("gửi bài tập về đệ quy", "exercise"),
            ("bài tập về sắp xếp mảng", "exercise"),
            ("cho bài tập về class oop", "exercise"),
            ("bài tập về đọc ghi file", "exercise"),
            ("bài tập về câu lệnh if else", "exercise"),
            ("bài tập tổng hợp python", "exercise"),
            ("bài tập về list comprehension", "exercise"),
            ("cho bài tập về dict comprehension", "exercise"),
            ("bài tập về lambda function", "exercise"),
            ("gửi bài tập về map filter reduce", "exercise"),
            ("bài tập về decorator", "exercise"),
            ("cho bài tập về generator", "exercise"),
            ("bài tập về exception handling", "exercise"),
            ("gửi bài tập về module", "exercise"),
            ("bài tập về datetime", "exercise"),
            ("cho bài tập về random", "exercise"),
            ("bài tập về json", "exercise"),
            ("gửi bài tập về api request", "exercise"),
            ("bài tập về threading", "exercise"),
            ("cho bài tập về multiprocessing", "exercise"),
            ("bài tập về socket", "exercise"),
            ("gửi bài tập về database", "exercise"),
            ("bài tập về sqlite3", "exercise"),
            ("cho bài tập về regex", "exercise"),
            ("bài tập về web scraping", "exercise"),
            ("gửi bài tập về flask", "exercise"),
            ("bài tập về tkinter", "exercise"),
            ("cho bài tập về numpy", "exercise"),
            ("bài tập về pandas", "exercise"),
            ("gửi bài tập về matplotlib", "exercise"),
            ("bài tập về seaborn", "exercise"),
            ("cho bài tập về scikit learn", "exercise"),
            ("bài tập về machine learning", "exercise"),
            ("gửi bài tập về deep learning", "exercise"),
            ("bài tập về binary search", "exercise"),
            ("cho bài tập về bubble sort", "exercise"),
            ("bài tập về quick sort", "exercise"),
            ("gửi bài tập về merge sort", "exercise"),
            ("bài tập về linked list", "exercise"),
            ("cho bài tập về stack", "exercise"),
            ("bài tập về queue", "exercise"),
            ("gửi bài tập về tree", "exercise"),
            ("bài tập về graph", "exercise"),
            ("cho bài tập về dynamic programming", "exercise"),
            
            # ===== COMPARE (30 câu) =====
            ("so sánh list và tuple", "compare"),
            ("sự khác nhau giữa for và while", "compare"),
            ("phân biệt hàm và thủ tục", "compare"),
            ("khác nhau giữa mảng và danh sách", "compare"),
            ("so sánh đệ quy và vòng lặp", "compare"),
            ("phân biệt break và continue", "compare"),
            ("so sánh stack và queue", "compare"),
            ("khác nhau giữa biến cục bộ và toàn cục", "compare"),
            ("phân biệt sort và sorted", "compare"),
            ("so sánh dict và list khi nào dùng", "compare"),
            ("khác nhau giữa == và is", "compare"),
            ("phân biệt deep copy và shallow copy", "compare"),
            ("so sánh class và struct", "compare"),
            ("khác nhau giữa inheritance và composition", "compare"),
            ("phân biệt overloading và overriding", "compare"),
            ("so sánh abstract class và interface", "compare"),
            ("khác nhau giữa multithreading và multiprocessing", "compare"),
            ("phân biệt synchronous và asynchronous", "compare"),
            ("so sánh http và https", "compare"),
            ("khác nhau giữa json và xml", "compare"),
            ("phân biệt sql và nosql", "compare"),
            ("so sánh git merge và rebase", "compare"),
            ("khác nhau giữa docker và vm", "compare"),
            ("phân biệt array và linked list", "compare"),
            ("so sánh binary tree và binary search tree", "compare"),
            ("khác nhau giữa bfs và dfs", "compare"),
            ("phân biệt regression và classification", "compare"),
            ("so sánh supervised và unsupervised learning", "compare"),
            ("khác nhau giữa train test split và cross validation", "compare"),
            ("phân biệt precision và recall", "compare"),
        ]
        
        for question, category in training_data:
            cursor.execute('''
            INSERT INTO training_data (question, category, created_at)
            VALUES (?, ?, ?)
            ''', (question, category, datetime.now().isoformat()))
        
        print(f"✅ Đã thêm {len(training_data)} câu hỏi mẫu vào dữ liệu huấn luyện")
    
    conn.commit()
    conn.close()
    print("✅ Database khởi tạo thành công!")

# ========== TOPICS MANAGEMENT (QUẢN LÝ TAG) ==========
def add_topic(name, subject, teacher_id=1):
    """Thêm topic mới nếu chưa có"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR IGNORE INTO topics (name, subject, usage_count, created_at, teacher_id)
    VALUES (?, ?, 0, ?, ?)
    ''', (name.lower(), subject, datetime.now().isoformat(), teacher_id))
    conn.commit()
    conn.close()


def get_all_topics(subject=None):
    """Lấy tất cả topics (tag)"""
    conn = get_connection()
    cursor = conn.cursor()
    if subject:
        cursor.execute("SELECT name FROM topics WHERE subject = ? ORDER BY name", (subject,))
    else:
        cursor.execute("SELECT name FROM topics ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


def increment_topic_usage(topic_name):
    """Tăng số lần sử dụng topic"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE topics SET usage_count = usage_count + 1
    WHERE name = ?
    ''', (topic_name.lower(),))
    conn.commit()
    conn.close()


def get_or_create_topic(topic_name, subject):
    """Lấy hoặc tạo topic mới, trả về True nếu đã tồn tại, False nếu vừa tạo"""
    topic_name = topic_name.lower()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM topics WHERE name = ?", (topic_name,))
    exists = cursor.fetchone()
    
    if exists:
        conn.close()
        increment_topic_usage(topic_name)
        return True
    
    # Tạo mới
    cursor.execute('''
    INSERT INTO topics (name, subject, usage_count, created_at, teacher_id)
    VALUES (?, ?, 1, ?, 1)
    ''', (topic_name, subject, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return False


def delete_topic(topic_name):
    """Xóa topic (cẩn thận khi xóa)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM topics WHERE name = ?", (topic_name.lower(),))
    conn.commit()
    conn.close()


def get_exercises_by_tag(tag_name, subject, level, student_id):
    """Lấy bài tập theo tag (chủ đề) - dùng cho student_dashboard"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT e.* FROM exercises e
    WHERE e.subject = ? AND e.level = ? 
    AND e.tags LIKE ?
    AND e.exercise_id NOT IN (
        SELECT exercise_id FROM student_exercise_history 
        WHERE student_id = ? AND is_exam = 0
    )
    ''', (subject, level, f'%"{tag_name}"%', student_id))
    rows = cursor.fetchall()
    conn.close()
    
    exercises = []
    for row in rows:
        exercises.append({
            "id": row[0],
            "exercise_id": row[1],
            "question": row[2],
            "type": row[3],
            "options": json.loads(row[4]) if row[4] else [],
            "answer": row[5],
            "subject": row[6],
            "level": row[7],
            "tags": json.loads(row[8]) if row[8] else []
        })
    return exercises
# ========== AUTH ==========
def authenticate(username, password):
    """Đăng nhập - không phân biệt chữ hoa/thường ở username"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, full_name FROM users WHERE LOWER(username) = LOWER(?) AND password = ?", 
                   (username, password))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "role": row[2], "full_name": row[3]}
    return None


def register_user(username, password, full_name):
    """Đăng ký tài khoản học sinh mới"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Kiểm tra username đã tồn tại (không phân biệt hoa thường)
    cursor.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?)", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Tên đăng nhập đã tồn tại!"
    
    cursor.execute('''
    INSERT INTO users (username, password, role, full_name, created_at)
    VALUES (?, ?, ?, ?, ?)
    ''', (username, password, 'student', full_name, datetime.now().isoformat()))
    
    user_id = cursor.lastrowid
    
    cursor.execute('''
    INSERT INTO student_profiles (user_id, level, topics_learned, quiz_scores, weak_topics, score_history, exam_scores)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, "beginner", "[]", "{}", "[]", "[]", "[]"))
    
    conn.commit()
    conn.close()
    return True, "Đăng ký thành công!"


# ========== STUDENT PROFILES ==========
def get_student_profile(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT level, topics_learned, quiz_scores, weak_topics, score_history, exam_scores FROM student_profiles WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "level": row[0],
            "topics_learned": json.loads(row[1]),
            "quiz_scores": json.loads(row[2]),
            "weak_topics": json.loads(row[3]),
            "score_history": json.loads(row[4]) if row[4] else [],
            "exam_scores": json.loads(row[5]) if row[5] else []
        }
    return {"level": "beginner", "topics_learned": [], "quiz_scores": {}, "weak_topics": [], "score_history": [], "exam_scores": []}


def update_student_profile(user_id, profile_data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE student_profiles 
    SET level = ?, topics_learned = ?, quiz_scores = ?, weak_topics = ?, score_history = ?, exam_scores = ?
    WHERE user_id = ?
    ''', (profile_data["level"], json.dumps(profile_data["topics_learned"]),
          json.dumps(profile_data["quiz_scores"]), json.dumps(profile_data["weak_topics"]),
          json.dumps(profile_data.get("score_history", [])),
          json.dumps(profile_data.get("exam_scores", [])), user_id))
    conn.commit()
    conn.close()


def update_level_by_exams(user_id, profile):
    exam_scores = profile.get("exam_scores", [])
    if len(exam_scores) < 2:
        return profile["level"]
    if exam_scores[-2] >= 80 and exam_scores[-1] >= 80:
        current = profile["level"]
        if current == "beginner":
            new_level = "intermediate"
        elif current == "intermediate":
            new_level = "advanced"
        else:
            new_level = "advanced"
        if new_level != current:
            profile["level"] = new_level
            update_student_profile(user_id, profile)
            return new_level
    return profile["level"]


def add_exam_result(user_id, exam_id, score, answers):
    profile = get_student_profile(user_id)
    exam_scores = profile.get("exam_scores", [])
    exam_scores.append(score)
    profile["exam_scores"] = exam_scores[-5:]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO quiz_history (student_id, exercise_id, score, answer, explanation, is_exam, completed_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, exam_id, score, json.dumps(answers), "", 1, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    update_student_profile(user_id, profile)
    return update_level_by_exams(user_id, profile)


def add_practice_result(user_id, exercise_id, score, answer, explanation=""):
    profile = get_student_profile(user_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO quiz_history (student_id, exercise_id, score, answer, explanation, is_exam, completed_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, exercise_id, score, answer, explanation, 0, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    mark_exercise_done(user_id, exercise_id, is_exam=0)
    
    if score < 60 and exercise_id not in profile["weak_topics"]:
        profile["weak_topics"].append(exercise_id)
        update_student_profile(user_id, profile)
    return profile["level"]


def get_average_score_last_5(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT score FROM quiz_history 
    WHERE student_id = ? AND is_exam = 0
    ORDER BY completed_at DESC LIMIT 5
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return 0
    scores = [row[0] for row in rows]
    return sum(scores) / len(scores)


# ========== EXERCISES ==========
def add_exercise(exercise_data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO exercises (exercise_id, question, type, options, answer, subject, level, tags, teacher_id, auto_generated, correct_explanation, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (exercise_data["exercise_id"], exercise_data["question"], exercise_data["type"],
          json.dumps(exercise_data.get("options", [])), exercise_data["answer"],
          exercise_data["subject"], exercise_data["level"], json.dumps(exercise_data["tags"]),
          exercise_data["teacher_id"], exercise_data.get("auto_generated", 0),
          exercise_data.get("correct_explanation", ""), exercise_data["created_at"]))
    conn.commit()
    conn.close()


def get_exercises(subject=None, level=None, exercise_type=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM exercises WHERE 1=1"
    params = []
    if subject:
        query += " AND subject = ?"
        params.append(subject)
    if level:
        query += " AND level = ?"
        params.append(level)
    if exercise_type:
        query += " AND type = ?"
        params.append(exercise_type)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    exercises = []
    for row in rows:
        exercises.append({
            "id": row[0],
            "exercise_id": row[1],
            "question": row[2],
            "type": row[3],
            "options": json.loads(row[4]) if row[4] else [],
            "answer": row[5],
            "subject": row[6],
            "level": row[7],
            "tags": json.loads(row[8]),
            "teacher_id": row[9],
            "auto_generated": row[10],
            "correct_explanation": row[11] if len(row) > 11 else "",
            "created_at": row[12] if len(row) > 12 else ""
        })
    return exercises


def get_unsolved_exercises(student_id, subject=None, level=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = '''
    SELECT e.* FROM exercises e
    WHERE e.exercise_id NOT IN (
        SELECT exercise_id FROM student_exercise_history 
        WHERE student_id = ? AND is_exam = 0
    )
    '''
    params = [student_id]
    
    if subject:
        query += " AND e.subject = ?"
        params.append(subject)
    if level:
        query += " AND e.level = ?"
        params.append(level)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    exercises = []
    for row in rows:
        exercises.append({
            "id": row[0],
            "exercise_id": row[1],
            "question": row[2],
            "type": row[3],
            "options": json.loads(row[4]) if row[4] else [],
            "answer": row[5],
            "subject": row[6],
            "level": row[7]
        })
    return exercises


def get_exercises_by_topic(topic, subject, level, student_id):
    """Lấy bài tập theo chủ đề (dùng tags)"""
    all_exercises = get_exercises(subject=subject, level=level)
    
    topic_exercises = []
    for ex in all_exercises:
        # Kiểm tra trong tags của bài tập
        ex_tags = ex.get("tags", [])
        if isinstance(ex_tags, str):
            try:
                ex_tags = json.loads(ex_tags)
            except:
                ex_tags = []
        
        # Kiểm tra trong câu hỏi hoặc tags
        if (topic in ex["question"].lower() or 
            any(topic in tag.lower() for tag in ex_tags)):
            topic_exercises.append(ex)
    
    # Lọc bài chưa làm
    unsolved = []
    for ex in topic_exercises:
        if not get_exercise_history(student_id, ex["exercise_id"]):
            unsolved.append(ex)
    
    return unsolved


def get_exercise_history(student_id, exercise_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id FROM student_exercise_history 
    WHERE student_id = ? AND exercise_id = ?
    ''', (student_id, exercise_id))
    row = cursor.fetchone()
    conn.close()
    return row is not None


def mark_exercise_done(student_id, exercise_id, is_exam=0):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id FROM student_exercise_history 
    WHERE student_id = ? AND exercise_id = ?
    ''', (student_id, exercise_id))
    
    if not cursor.fetchone():
        cursor.execute('''
        INSERT INTO student_exercise_history (student_id, exercise_id, is_exam, completed_at)
        VALUES (?, ?, ?, ?)
        ''', (student_id, exercise_id, is_exam, datetime.now().isoformat()))
        conn.commit()
    
    conn.close()


def reset_exercise_history(student_id, exercise_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    if exercise_id:
        cursor.execute('''
        DELETE FROM student_exercise_history 
        WHERE student_id = ? AND exercise_id = ?
        ''', (student_id, exercise_id))
    else:
        cursor.execute('''
        DELETE FROM student_exercise_history 
        WHERE student_id = ?
        ''', (student_id,))
    
    conn.commit()
    conn.close()


# ========== CHAT HISTORY ==========
def save_chat_message(student_id, subject, role, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO chat_history (student_id, subject, role, content, created_at)
    VALUES (?, ?, ?, ?, ?)
    ''', (student_id, subject, role, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_chat_history(student_id, subject, limit=100):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT role, content FROM chat_history 
    WHERE student_id = ? AND subject = ?
    ORDER BY created_at ASC LIMIT ?
    ''', (student_id, subject, limit))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in rows]


def clear_chat_history(student_id, subject=None):
    conn = get_connection()
    cursor = conn.cursor()
    if subject:
        cursor.execute('''
        DELETE FROM chat_history WHERE student_id = ? AND subject = ?
        ''', (student_id, subject))
    else:
        cursor.execute('''
        DELETE FROM chat_history WHERE student_id = ?
        ''', (student_id,))
    conn.commit()
    conn.close()


# ========== LESSONS ==========
def add_lesson(lesson_data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO lessons (lesson_id, title, theory, examples, exercises, subject, level, tags, teacher_id, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (lesson_data["lesson_id"], lesson_data["title"], lesson_data["theory"],
          json.dumps(lesson_data["examples"]), json.dumps(lesson_data["exercises"]),
          lesson_data["subject"], lesson_data["level"], json.dumps(lesson_data["tags"]),
          lesson_data["teacher_id"], lesson_data["created_at"]))
    conn.commit()
    conn.close()


def get_lessons(subject=None, level=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM lessons WHERE 1=1"
    params = []
    if subject:
        query += " AND subject = ?"
        params.append(subject)
    if level:
        query += " AND level = ?"
        params.append(level)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    lessons = []
    for row in rows:
        lessons.append({
            "id": row[0],
            "lesson_id": row[1],
            "title": row[2],
            "theory": row[3],
            "examples": json.loads(row[4]),
            "exercises": json.loads(row[5]),
            "subject": row[6],
            "level": row[7],
            "tags": json.loads(row[8]),
            "teacher_id": row[9],
            "created_at": row[10]
        })
    return lessons


def search_lessons_by_keyword(keyword, subject=None):
    conn = get_connection()
    cursor = conn.cursor()
    if subject:
        cursor.execute("SELECT * FROM lessons WHERE subject = ? AND (title LIKE ? OR theory LIKE ?)", 
                       (subject, f"%{keyword}%", f"%{keyword}%"))
    else:
        cursor.execute("SELECT * FROM lessons WHERE title LIKE ? OR theory LIKE ?", 
                       (f"%{keyword}%", f"%{keyword}%"))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for row in rows:
        results.append({
            "title": row[2],
            "theory": row[3],
            "examples": json.loads(row[4]),
            "tags": json.loads(row[8]),
            "subject": row[6]
        })
    return results


# ========== EXAMS ==========
def add_exam(exam_data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO exams (exam_id, title, subject, level, questions, time_limit, created_at, teacher_id, is_active)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (exam_data["exam_id"], exam_data["title"], exam_data["subject"],
          exam_data["level"], json.dumps(exam_data["questions"]),
          exam_data.get("time_limit", 30), exam_data["created_at"],
          exam_data["teacher_id"], 1))
    conn.commit()
    conn.close()


def get_exams(subject=None, level=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM exams WHERE is_active = 1"
    params = []
    if subject:
        query += " AND subject = ?"
        params.append(subject)
    if level:
        query += " AND level = ?"
        params.append(level)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    exams = []
    for row in rows:
        exams.append({
            "id": row[0],
            "exam_id": row[1],
            "title": row[2],
            "subject": row[3],
            "level": row[4],
            "questions": json.loads(row[5]),
            "time_limit": row[6],
            "created_at": row[7],
            "teacher_id": row[8]
        })
    return exams


# ========== TRAINING DATA ==========
def add_training_data(question, category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO training_data (question, category, created_at)
    VALUES (?, ?, ?)
    ''', (question, category, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_all_training_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT question, category FROM training_data")
    rows = cursor.fetchall()
    conn.close()
    return [(row[0], row[1]) for row in rows]


# Khởi tạo database
init_database()