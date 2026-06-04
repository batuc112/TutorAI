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
    
    # ========== TẠO CÁC BẢNG ==========
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
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS training_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        category TEXT,
        created_at TEXT
    )
    ''')
    
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
    
    # ========== THÊM TÀI KHOẢN MẶC ĐỊNH ==========
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
    
    # ========== THÊM TOPICS MẶC ĐỊNH ==========
    cursor.execute("SELECT COUNT(*) FROM topics")
    if cursor.fetchone()[0] == 0:
        default_topics = ["biến", "hàm", "vòng lặp", "list", "tuple", "dictionary", "set", "class", "đệ quy", "file"]
        for topic in default_topics:
            cursor.execute('''
            INSERT INTO topics (name, subject, usage_count, created_at, teacher_id)
            VALUES (?, ?, 0, ?, 1)
            ''', (topic, "programming", datetime.now().isoformat()))
    
    # ========== CÂU HỎI HUẤN LUYỆN ==========
    cursor.execute("SELECT COUNT(*) FROM training_data")
    if cursor.fetchone()[0] == 0:
        
        # ===== 1. DEFINITION =====
        definition_data = [
            # Biến
            ("biến trong python là gì", "definition"),
            ("thế nào là biến", "definition"),
            ("khái niệm biến trong lập trình", "definition"),
            ("định nghĩa biến", "definition"),
            ("biến được hiểu như thế nào", "definition"),
            ("hãy giải thích biến", "definition"),
            ("biến trong code là gì", "definition"),
            ("biến có nghĩa là gì", "definition"),
            ("biến là gì trong python", "definition"),
            ("biến dùng để làm gì", "definition"),
            
            # Hàm 
            ("hàm trong python là gì", "definition"),
            ("thế nào là hàm", "definition"),
            ("khái niệm hàm trong lập trình", "definition"),
            ("định nghĩa hàm", "definition"),
            ("hàm được hiểu như thế nào", "definition"),
            ("hãy giải thích hàm", "definition"),
            ("function trong python là gì", "definition"),
            ("hàm có nghĩa là gì", "definition"),
            ("thế nào là function", "definition"),
            ("hàm là gì trong code", "definition"),
            
            # Vòng lặp 
            ("vòng lặp trong python là gì", "definition"),
            ("thế nào là vòng lặp", "definition"),
            ("khái niệm vòng lặp", "definition"),
            ("định nghĩa vòng lặp", "definition"),
            ("vòng lặp được hiểu như thế nào", "definition"),
            ("hãy giải thích vòng lặp", "definition"),
            ("loop trong python là gì", "definition"),
            ("vòng lặp for là gì", "definition"),
            ("vòng lặp while là gì", "definition"),
            ("thế nào là loop", "definition"),
            
            # List 
            ("list trong python là gì", "definition"),
            ("thế nào là list", "definition"),
            ("khái niệm list trong lập trình", "definition"),
            ("định nghĩa list", "definition"),
            ("list được hiểu như thế nào", "definition"),
            ("hãy giải thích list", "definition"),
            ("mảng trong python là gì", "definition"),
            ("list có nghĩa là gì", "definition"),
            ("thế nào là danh sách trong python", "definition"),
            ("list là gì trong code", "definition"),
            
            # Tuple 
            ("tuple trong python là gì", "definition"),
            ("thế nào là tuple", "definition"),
            ("khái niệm tuple", "definition"),
            ("tuple khác list thế nào", "definition"),
            ("tuple là gì", "definition"),
            
            # Dictionary 
            ("dictionary trong python là gì", "definition"),
            ("thế nào là dict", "definition"),
            ("khái niệm dictionary", "definition"),
            ("dict là gì trong python", "definition"),
            ("dictionary dùng để làm gì", "definition"),
            
            # Set 
            ("set trong python là gì", "definition"),
            ("thế nào là set", "definition"),
            ("khái niệm set", "definition"),
            ("set khác list thế nào", "definition"),
            ("set là gì", "definition"),
            
            # Class/OOP 
            ("class trong python là gì", "definition"),
            ("thế nào là class", "definition"),
            ("khái niệm class trong oop", "definition"),
            ("định nghĩa class", "definition"),
            ("oop là gì", "definition"),
            ("hướng đối tượng là gì", "definition"),
            ("object là gì trong python", "definition"),
            ("thế nào là lập trình hướng đối tượng", "definition"),
            ("class và object là gì", "definition"),
            ("đối tượng trong oop là gì", "definition"),
            
            # Đệ quy 
            ("đệ quy trong python là gì", "definition"),
            ("thế nào là đệ quy", "definition"),
            ("khái niệm đệ quy", "definition"),
            ("recursion là gì", "definition"),
            ("hàm đệ quy là gì", "definition"),
            
            # File handling 
            ("file handling trong python là gì", "definition"),
            ("thế nào là đọc ghi file", "definition"),
            ("cách đọc file trong python", "definition"),
            ("file trong python là gì", "definition"),
            ("xử lý file là gì", "definition"),
            
            # Exception 
            ("exception trong python là gì", "definition"),
            ("thế nào là ngoại lệ", "definition"),
            ("try except là gì", "definition"),
            ("lỗi trong python là gì", "definition"),
            ("xử lý lỗi là gì", "definition"),
            
            # Module 
            ("module trong python là gì", "definition"),
            ("thế nào là module", "definition"),
            ("import trong python là gì", "definition"),
            ("thư viện python là gì", "definition"),
            ("pip là gì", "definition"),
            
            # Decorator 
            ("decorator trong python là gì", "definition"),
            ("thế nào là decorator", "definition"),
            ("decorator dùng để làm gì", "definition"),
            ("wrapper là gì", "definition"),
            ("decorator là gì", "definition"),
            
            # Generator 
            ("generator trong python là gì", "definition"),
            ("thế nào là generator", "definition"),
            ("yield trong python là gì", "definition"),
            ("generator khác list thế nào", "definition"),
            ("generator là gì", "definition"),
            
            # Context Manager 
            ("context manager trong python là gì", "definition"),
            ("thế nào là context manager", "definition"),
            ("with trong python là gì", "definition"),
            ("context manager dùng để làm gì", "definition"),
            ("enter exit là gì", "definition"),
            
            # Async/Await 
            ("async trong python là gì", "definition"),
            ("await trong python là gì", "definition"),
            ("thế nào là asynchronous", "definition"),
            ("coroutine trong python là gì", "definition"),
            ("async function là gì", "definition"),
        ]
        
        # ===== 2. EXAMPLE  =====
        example_data = [
            # Biến (10 câu)
            ("cho tôi ví dụ về biến", "example"),
            ("lấy ví dụ về biến trong python", "example"),
            ("ví dụ minh họa biến", "example"),
            ("hãy cho ví dụ về biến", "example"),
            ("ví dụ thực tế về biến", "example"),
            ("cho ví dụ cách khai báo biến", "example"),
            ("lấy ví dụ biến số", "example"),
            ("ví dụ về biến trong code", "example"),
            ("minh họa biến bằng ví dụ", "example"),
            ("cho tôi xem ví dụ biến", "example"),
            
            # Hàm (10 câu)
            ("cho tôi ví dụ về hàm", "example"),
            ("lấy ví dụ về hàm trong python", "example"),
            ("ví dụ minh họa hàm", "example"),
            ("hãy cho ví dụ về hàm", "example"),
            ("ví dụ thực tế về hàm", "example"),
            ("cho ví dụ cách định nghĩa hàm", "example"),
            ("lấy ví dụ hàm có tham số", "example"),
            ("ví dụ về hàm trả về giá trị", "example"),
            ("minh họa hàm bằng ví dụ", "example"),
            ("cho tôi xem ví dụ hàm", "example"),
            
            # Vòng lặp (10 câu)
            ("cho tôi ví dụ về vòng lặp", "example"),
            ("lấy ví dụ về vòng lặp for", "example"),
            ("ví dụ minh họa vòng lặp while", "example"),
            ("hãy cho ví dụ về loop", "example"),
            ("ví dụ thực tế về vòng lặp", "example"),
            ("cho ví dụ vòng lặp for range", "example"),
            ("lấy ví dụ vòng lặp lồng nhau", "example"),
            ("ví dụ về vòng lặp vô hạn", "example"),
            ("minh họa vòng lặp bằng ví dụ", "example"),
            ("cho tôi xem ví dụ vòng lặp", "example"),
            
            # List (10 câu)
            ("cho tôi ví dụ về list", "example"),
            ("lấy ví dụ về list trong python", "example"),
            ("ví dụ minh họa list", "example"),
            ("hãy cho ví dụ về mảng", "example"),
            ("ví dụ thực tế về danh sách", "example"),
            ("cho ví dụ cách tạo list", "example"),
            ("lấy ví dụ list comprehension", "example"),
            ("ví dụ về thao tác list", "example"),
            ("minh họa list bằng ví dụ", "example"),
            ("cho tôi xem ví dụ list", "example"),
            
            # Dictionary (10 câu)
            ("cho tôi ví dụ về dictionary", "example"),
            ("lấy ví dụ về dict", "example"),
            ("ví dụ minh họa dictionary", "example"),
            ("hãy cho ví dụ về từ điển", "example"),
            ("cho ví dụ dict trong python", "example"),
            ("lấy ví dụ duyệt dict", "example"),
            ("ví dụ về thêm key dict", "example"),
            ("minh họa dictionary bằng ví dụ", "example"),
            ("cho tôi xem ví dụ dict", "example"),
            ("ví dụ về dictionary comprehension", "example"),
            
            # Class (10 câu)
            ("cho tôi ví dụ về class", "example"),
            ("lấy ví dụ về class trong python", "example"),
            ("ví dụ minh họa oop", "example"),
            ("hãy cho ví dụ về đối tượng", "example"),
            ("ví dụ thực tế về class", "example"),
            ("cho ví dụ class và object", "example"),
            ("lấy ví dụ về inheritance", "example"),
            ("ví dụ về phương thức trong class", "example"),
            ("minh họa class bằng ví dụ", "example"),
            ("cho tôi xem ví dụ class", "example"),
            
            # Đệ quy (5 câu)
            ("cho tôi ví dụ về đệ quy", "example"),
            ("lấy ví dụ về hàm đệ quy", "example"),
            ("ví dụ minh họa recursion", "example"),
            ("hãy cho ví dụ đệ quy tính giai thừa", "example"),
            ("cho ví dụ đệ quy fibonacci", "example"),
            
            # File (10 câu)
            ("cho tôi ví dụ về đọc file", "example"),
            ("lấy ví dụ về ghi file", "example"),
            ("ví dụ minh họa file handling", "example"),
            ("hãy cho ví dụ mở file", "example"),
            ("ví dụ về đọc file txt", "example"),
            ("cho ví dụ ghi file csv", "example"),
            ("lấy ví dụ đọc file json", "example"),
            ("ví dụ về with open", "example"),
            ("minh họa đọc ghi file", "example"),
            ("cho tôi xem ví dụ file", "example"),
            
            # Exception (5 câu)
            ("cho tôi ví dụ về try except", "example"),
            ("lấy ví dụ về xử lý lỗi", "example"),
            ("ví dụ minh họa exception", "example"),
            ("hãy cho ví dụ bắt lỗi", "example"),
            ("cho ví dụ try except finally", "example"),
            
            # Module (5 câu)
            ("cho tôi ví dụ về import", "example"),
            ("lấy ví dụ về module", "example"),
            ("ví dụ minh họa import math", "example"),
            ("hãy cho ví dụ dùng random", "example"),
            ("cho ví dụ import datetime", "example"),
            
            # Decorator (5 câu)
            ("cho tôi ví dụ về decorator", "example"),
            ("lấy ví dụ về decorator trong python", "example"),
            ("ví dụ minh họa decorator", "example"),
            ("hãy cho ví dụ @staticmethod", "example"),
            ("cho ví dụ decorator có tham số", "example"),
            
            # Generator (5 câu)
            ("cho tôi ví dụ về generator", "example"),
            ("lấy ví dụ về yield", "example"),
            ("ví dụ minh họa generator", "example"),
            ("hãy cho ví dụ generator function", "example"),
            ("cho ví dụ generator comprehension", "example"),
            
            # Context Manager (5 câu)
            ("cho tôi ví dụ về context manager", "example"),
            ("lấy ví dụ về with open", "example"),
            ("ví dụ minh họa context manager", "example"),
            ("hãy cho ví dụ tự tạo context manager", "example"),
            ("cho ví dụ context manager với class", "example"),
        ]
        
        # ===== 3. HOW_TO (100 câu) =====
        howto_data = [
            # Biến (5 câu)
            ("cách khai báo biến trong python", "how_to"),
            ("làm thế nào để tạo biến", "how_to"),
            ("hướng dẫn đặt tên biến", "how_to"),
            ("cách gán giá trị cho biến", "how_to"),
            ("làm sao để khai báo biến", "how_to"),
            
            # Hàm (10 câu)
            ("cách tạo hàm trong python", "how_to"),
            ("làm thế nào để định nghĩa hàm", "how_to"),
            ("hướng dẫn viết hàm", "how_to"),
            ("cách truyền tham số cho hàm", "how_to"),
            ("làm sao để hàm trả về giá trị", "how_to"),
            ("cách dùng return trong hàm", "how_to"),
            ("hướng dẫn tạo hàm có tham số mặc định", "how_to"),
            ("cách viết lambda function", "how_to"),
            ("làm thế nào để gọi hàm", "how_to"),
            ("cách dùng hàm ẩn danh", "how_to"),
            
            # Vòng lặp (10 câu)
            ("cách viết vòng lặp for", "how_to"),
            ("làm thế nào để dùng vòng lặp while", "how_to"),
            ("hướng dẫn tạo vòng lặp", "how_to"),
            ("cách dùng range trong for", "how_to"),
            ("làm sao để thoát vòng lặp", "how_to"),
            ("cách dùng break trong vòng lặp", "how_to"),
            ("hướng dẫn dùng continue", "how_to"),
            ("cách tạo vòng lặp lồng nhau", "how_to"),
            ("làm thế nào để lặp qua list", "how_to"),
            ("cách dùng enumerate trong vòng lặp", "how_to"),
            
            # List (10 câu)
            ("cách tạo list trong python", "how_to"),
            ("làm thế nào để thêm phần tử vào list", "how_to"),
            ("hướng dẫn xóa phần tử khỏi list", "how_to"),
            ("cách truy cập phần tử trong list", "how_to"),
            ("làm sao để sắp xếp list", "how_to"),
            ("cách đảo ngược list", "how_to"),
            ("hướng dẫn cắt list", "how_to"),
            ("cách gộp hai list", "how_to"),
            ("làm thế nào để tìm phần tử trong list", "how_to"),
            ("cách dùng list comprehension", "how_to"),
            
            # Dictionary (10 câu)
            ("cách tạo dictionary", "how_to"),
            ("làm thế nào để thêm key vào dict", "how_to"),
            ("hướng dẫn xóa key khỏi dictionary", "how_to"),
            ("cách lấy value từ dict", "how_to"),
            ("làm sao để duyệt dictionary", "how_to"),
            ("cách kiểm tra key tồn tại", "how_to"),
            ("hướng dẫn dùng get()", "how_to"),
            ("cách lấy tất cả key", "how_to"),
            ("làm thế nào để lấy tất cả value", "how_to"),
            ("cách dùng dictionary comprehension", "how_to"),
            
            # Class (10 câu)
            ("cách tạo class trong python", "how_to"),
            ("làm thế nào để định nghĩa class", "how_to"),
            ("hướng dẫn tạo đối tượng từ class", "how_to"),
            ("cách viết phương thức trong class", "how_to"),
            ("làm sao để dùng constructor", "how_to"),
            ("cách tạo inheritance", "how_to"),
            ("hướng dẫn override method", "how_to"),
            ("cách dùng super()", "how_to"),
            ("làm thế nào để tạo property", "how_to"),
            ("cách dùng static method", "how_to"),
            
            # Đệ quy (5 câu)
            ("cách viết hàm đệ quy", "how_to"),
            ("làm thế nào để dùng đệ quy", "how_to"),
            ("hướng dẫn tạo đệ quy", "how_to"),
            ("cách viết đệ quy tính giai thừa", "how_to"),
            ("làm sao để tránh stack overflow", "how_to"),
            
            # File (10 câu)
            ("cách đọc file trong python", "how_to"),
            ("làm thế nào để ghi file", "how_to"),
            ("hướng dẫn mở file với with", "how_to"),
            ("cách đọc file csv", "how_to"),
            ("làm sao để ghi file csv", "how_to"),
            ("cách đọc file json", "how_to"),
            ("hướng dẫn ghi file json", "how_to"),
            ("cách đọc từng dòng trong file", "how_to"),
            ("làm thế nào để kiểm tra file tồn tại", "how_to"),
            ("cách xóa file trong python", "how_to"),
            
            # Exception (5 câu)
            ("cách bắt lỗi trong python", "how_to"),
            ("làm thế nào để dùng try except", "how_to"),
            ("hướng dẫn xử lý ngoại lệ", "how_to"),
            ("cách dùng finally", "how_to"),
            ("làm sao để raise exception", "how_to"),
            
            # Module (10 câu)
            ("cách import module trong python", "how_to"),
            ("làm thế nào để cài đặt thư viện", "how_to"),
            ("hướng dẫn dùng pip", "how_to"),
            ("cách import từ file khác", "how_to"),
            ("làm sao để import as", "how_to"),
            ("cách dùng from import", "how_to"),
            ("hướng dẫn tạo module riêng", "how_to"),
            ("cách cài đặt package", "how_to"),
            ("làm thế nào để dùng virtual environment", "how_to"),
            ("cách dùng requirements.txt", "how_to"),
            
            # Decorator (5 câu)
            ("cách tạo decorator trong python", "how_to"),
            ("làm thế nào để dùng decorator", "how_to"),
            ("hướng dẫn viết decorator", "how_to"),
            ("cách dùng @staticmethod", "how_to"),
            ("làm sao để dùng @classmethod", "how_to"),
            
            # Generator (5 câu)
            ("cách tạo generator trong python", "how_to"),
            ("làm thế nào để dùng yield", "how_to"),
            ("hướng dẫn tạo generator function", "how_to"),
            ("cách dùng generator comprehension", "how_to"),
            ("làm sao để lặp qua generator", "how_to"),
            
            # Context Manager (5 câu)
            ("cách tạo context manager", "how_to"),
            ("làm thế nào để dùng with", "how_to"),
            ("hướng dẫn tạo context manager bằng class", "how_to"),
            ("cách dùng contextlib", "how_to"),
            ("làm sao để tạo context manager bằng decorator", "how_to"),
        ]
        
        # ===== 4. EXERCISE (100 câu) =====
        exercise_data = [
            # Biến (10 câu)
            ("cho tôi bài tập về biến", "exercise"),
            ("gửi bài tập về biến", "exercise"),
            ("làm bài tập biến", "exercise"),
            ("bài tập thực hành biến", "exercise"),
            ("cho bài tập khai báo biến", "exercise"),
            ("bài tập về kiểu dữ liệu biến", "exercise"),
            ("thực hành biến", "exercise"),
            ("bài tập biến số", "exercise"),
            ("luyện tập biến", "exercise"),
            ("bài tập về đặt tên biến", "exercise"),
            
            # Hàm (10 câu)
            ("cho tôi bài tập về hàm", "exercise"),
            ("gửi bài tập hàm", "exercise"),
            ("làm bài tập về function", "exercise"),
            ("bài tập thực hành hàm", "exercise"),
            ("cho bài tập viết hàm", "exercise"),
            ("bài tập về tham số hàm", "exercise"),
            ("thực hành hàm có return", "exercise"),
            ("bài tập lambda function", "exercise"),
            ("luyện tập viết hàm", "exercise"),
            ("bài tập về đệ quy", "exercise"),
            
            # Vòng lặp (10 câu)
            ("cho tôi bài tập về vòng lặp", "exercise"),
            ("gửi bài tập vòng lặp for", "exercise"),
            ("làm bài tập vòng lặp while", "exercise"),
            ("bài tập thực hành loop", "exercise"),
            ("cho bài tập về range", "exercise"),
            ("bài tập vòng lặp lồng nhau", "exercise"),
            ("thực hành break continue", "exercise"),
            ("bài tập in số bằng vòng lặp", "exercise"),
            ("luyện tập vòng lặp", "exercise"),
            ("bài tập về enumerate", "exercise"),
            
            # List (10 câu)
            ("cho tôi bài tập về list", "exercise"),
            ("gửi bài tập list", "exercise"),
            ("làm bài tập về mảng", "exercise"),
            ("bài tập thực hành list", "exercise"),
            ("cho bài tập list comprehension", "exercise"),
            ("bài tập về thao tác list", "exercise"),
            ("thực hành thêm xóa list", "exercise"),
            ("bài tập sắp xếp list", "exercise"),
            ("luyện tập list", "exercise"),
            ("bài tập về cắt list", "exercise"),
            
            # Dictionary (10 câu)
            ("cho tôi bài tập về dictionary", "exercise"),
            ("gửi bài tập dict", "exercise"),
            ("làm bài tập dictionary", "exercise"),
            ("bài tập thực hành dict", "exercise"),
            ("cho bài tập về từ điển", "exercise"),
            ("bài tập duyệt dict", "exercise"),
            ("thực hành thêm key dict", "exercise"),
            ("bài tập dictionary comprehension", "exercise"),
            ("luyện tập dictionary", "exercise"),
            ("bài tập về get và setdefault", "exercise"),
            
            # Class (10 câu)
            ("cho tôi bài tập về class", "exercise"),
            ("gửi bài tập oop", "exercise"),
            ("làm bài tập class", "exercise"),
            ("bài tập thực hành class", "exercise"),
            ("cho bài tập về đối tượng", "exercise"),
            ("bài tập về inheritance", "exercise"),
            ("thực hành tạo class", "exercise"),
            ("bài tập về phương thức", "exercise"),
            ("luyện tập oop", "exercise"),
            ("bài tập về constructor", "exercise"),
            
            # File (10 câu)
            ("cho tôi bài tập về file", "exercise"),
            ("gửi bài tập đọc file", "exercise"),
            ("làm bài tập ghi file", "exercise"),
            ("bài tập thực hành file", "exercise"),
            ("cho bài tập đọc csv", "exercise"),
            ("bài tập về json", "exercise"),
            ("thực hành đọc ghi file", "exercise"),
            ("bài tập xử lý file", "exercise"),
            ("luyện tập file handling", "exercise"),
            ("bài tập về with open", "exercise"),
            
            # Exception (5 câu)
            ("cho tôi bài tập về try except", "exercise"),
            ("gửi bài tập xử lý lỗi", "exercise"),
            ("làm bài tập exception", "exercise"),
            ("bài tập thực hành try except", "exercise"),
            ("cho bài tập bắt lỗi", "exercise"),
            
            # Module (5 câu)
            ("cho tôi bài tập về module", "exercise"),
            ("gửi bài tập import", "exercise"),
            ("làm bài tập về thư viện", "exercise"),
            ("bài tập thực hành module", "exercise"),
            ("cho bài tập dùng math", "exercise"),
            
            # Decorator (5 câu)
            ("cho tôi bài tập về decorator", "exercise"),
            ("gửi bài tập decorator", "exercise"),
            ("làm bài tập về decorator", "exercise"),
            ("bài tập thực hành decorator", "exercise"),
            ("cho bài tập tạo decorator", "exercise"),
            
            # Generator (5 câu)
            ("cho tôi bài tập về generator", "exercise"),
            ("gửi bài tập generator", "exercise"),
            ("làm bài tập về yield", "exercise"),
            ("bài tập thực hành generator", "exercise"),
            ("cho bài tập generator function", "exercise"),
            
            # Tổng hợp (10 câu)
            ("cho tôi bài tập python cơ bản", "exercise"),
            ("gửi bài tập lập trình", "exercise"),
            ("làm bài tập thực hành", "exercise"),
            ("bài tập tổng hợp python", "exercise"),
            ("cho bài tập code", "exercise"),
            ("bài tập về giải thuật", "exercise"),
            ("thực hành lập trình", "exercise"),
            ("bài tập python nâng cao", "exercise"),
            ("luyện tập code", "exercise"),
            ("bài tập về cấu trúc dữ liệu", "exercise"),
        ]
        
        # ===== 5. COMPARE (100 câu) =====
        compare_data = [
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
            ("so sánh python 2 và python 3", "compare"),
            ("khác nhau giữa py2 và py3", "compare"),
            ("phân biệt pip và conda", "compare"),
            ("so sánh anaconda và miniconda", "compare"),
            ("khác nhau giữa jupyter notebook và python script", "compare"),
            ("phân biệt flask và django", "compare"),
            ("so sánh numpy array và list", "compare"),
            ("khác nhau giữa pandas series và dataframe", "compare"),
            ("phân biệt matplotlib và seaborn", "compare"),
            ("so sánh tensorflow và pytorch", "compare"),
            ("khác nhau giữa cpu và gpu", "compare"),
            ("phân biệt ram và rom", "compare"),
            ("so sánh ssd và hdd", "compare"),
            ("khác nhau giữa windows và linux", "compare"),
            ("phân biệt macos và windows", "compare"),
            ("so sánh chrome và firefox", "compare"),
            ("khác nhau giữa tcp và udp", "compare"),
            ("phân biệt ipv4 và ipv6", "compare"),
            ("so sánh mysql và postgresql", "compare"),
            ("khác nhau giữa mongodb và mysql", "compare"),
            ("phân biệt redis và memcached", "compare"),
            ("so sánh rabbitmq và kafka", "compare"),
            ("khác nhau giữa api và sdk", "compare"),
            ("phân biệt rest và graphql", "compare"),
            ("so sánh jwt và session", "compare"),
            ("khác nhau giữa oauth1 và oauth2", "compare"),
            ("phân biệt vertical scaling và horizontal scaling", "compare"),
            ("so sánh monolithic và microservices", "compare"),
            ("khác nhau giữa dev và ops", "compare"),
            ("phân biệt agile và waterfall", "compare"),
            ("so sánh scrum và kanban", "compare"),
            ("khác nhau giữa unit test và integration test", "compare"),
            ("phân biệt tdd và bdd", "compare"),
            ("so sánh ci và cd", "compare"),
            ("khác nhau giữa git và svn", "compare"),
            ("phân biệt github và gitlab", "compare"),
            ("so sánh bitbucket và github", "compare"),
            ("khác nhau giữa fork và clone", "compare"),
            ("phân biệt pull request và merge request", "compare"),
            ("so sánh issue và bug", "compare"),
            ("khác nhau giữa hotfix và bugfix", "compare"),
            ("phân biệt refactor và rewrite", "compare"),
            ("so sánh interpreter và compiler", "compare"),
            ("khác nhau giữa jit và aot", "compare"),
            ("phân biệt bytecode và machine code", "compare"),
            ("so sánh static typing và dynamic typing", "compare"),
            ("khác nhau giữa strong typing và weak typing", "compare"),
            ("phân biệt functional programming và oop", "compare"),
            ("so sánh declarative và imperative", "compare"),
            ("khác nhau giữa recursion và iteration", "compare"),
            ("phân biệt memoization và tabulation", "compare"),
            ("so sánh binary search và linear search", "compare"),
            ("khác nhau giữa bubble sort và quick sort", "compare"),
            ("phân biệt merge sort và heap sort", "compare"),
            ("so sánh hashmap và treemap", "compare"),
            ("khác nhau giữa hashset và treeset", "compare"),
            ("phân biệt priority queue và queue", "compare"),
            ("so sánh adjacency matrix và adjacency list", "compare"),
            ("khác nhau giữa dfs và bfs", "compare"),
            ("phân biệt dijkstra và bellman-ford", "compare"),
            ("so sánh kruskal và prim", "compare"),
            ("khác nhau giữa knapsack và subset sum", "compare"),
            ("phân biệt lru cache và fifo cache", "compare"),
            ("so sánh optimistic locking và pessimistic locking", "compare"),
            ("khác nhau giữa acid và base", "compare"),
            ("phân biệt sharding và partitioning", "compare"),
            ("so sánh replication và clustering", "compare"),
            ("khác nhau giữa load balancer và reverse proxy", "compare"),
            ("phân biệt ssl và tls", "compare"),
        ]
        
        # Gộp tất cả dữ liệu
        all_training_data = definition_data + example_data + howto_data + exercise_data + compare_data
        
        for question, category in all_training_data:
            cursor.execute('''
            INSERT INTO training_data (question, category, created_at)
            VALUES (?, ?, ?)
            ''', (question, category, datetime.now().isoformat()))
        
        print(f"✅ Đã thêm {len(all_training_data)} câu hỏi mẫu vào dữ liệu huấn luyện")
        print(f"   - Definition: {len(definition_data)} câu")
        print(f"   - Example: {len(example_data)} câu")
        print(f"   - How_to: {len(howto_data)} câu")
        print(f"   - Exercise: {len(exercise_data)} câu")
        print(f"   - Compare: {len(compare_data)} câu")
    
    conn.commit()
    conn.close()
    print("✅ Database khởi tạo thành công!")


# ========== TOPICS MANAGEMENT ==========
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
    """Lấy tất cả topics"""
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
    """Lấy hoặc tạo topic mới"""
    topic_name = topic_name.lower()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM topics WHERE name = ?", (topic_name,))
    exists = cursor.fetchone()
    
    if exists:
        conn.close()
        increment_topic_usage(topic_name)
        return True
    
    cursor.execute('''
    INSERT INTO topics (name, subject, usage_count, created_at, teacher_id)
    VALUES (?, ?, 1, ?, 1)
    ''', (topic_name, subject, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return False


def delete_topic(topic_name):
    """Xóa topic"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM topics WHERE name = ?", (topic_name.lower(),))
    conn.commit()
    conn.close()


def get_exercises_by_tag(tag_name, subject, level, student_id):
    """Lấy bài tập theo tag"""
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
    conn = get_connection()
    cursor = conn.cursor()
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
    """Thêm bài tập vào database - NHẬN JSON STRING"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO exercises (exercise_id, question, type, options, answer, subject, level, tags, teacher_id, auto_generated, correct_explanation, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        exercise_data["exercise_id"],
        exercise_data["question"],
        exercise_data["type"],
        exercise_data["options"],  
        exercise_data["answer"],
        exercise_data["subject"],
        exercise_data["level"],
        exercise_data["tags"],      
        exercise_data["teacher_id"],
        exercise_data.get("auto_generated", 0),
        exercise_data.get("correct_explanation", ""),
        exercise_data["created_at"]
    ))
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
        
        try:
            options = json.loads(row[4]) if row[4] else []
        except:
            options = []
        
        try:
            tags = json.loads(row[8]) if row[8] else []
        except:
            tags = []
        
        exercises.append({
            "id": row[0],
            "exercise_id": row[1],
            "question": row[2],
            "type": row[3],
            "options": options,
            "answer": row[5],
            "subject": row[6],
            "level": row[7],
            "tags": tags,
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
    """Lấy bài tập theo chủ đề"""
    all_exercises = get_exercises(subject=subject, level=level)
    
    topic_exercises = []
    for ex in all_exercises:
        ex_tags = ex.get("tags", [])
        if isinstance(ex_tags, str):
            try:
                ex_tags = json.loads(ex_tags)
            except:
                ex_tags = []
        
        if (topic in ex["question"].lower() or 
            any(topic in tag.lower() for tag in ex_tags)):
            topic_exercises.append(ex)
    
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