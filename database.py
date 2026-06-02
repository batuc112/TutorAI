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
    
    cursor.execute("SELECT COUNT(*) FROM training_data")
    if cursor.fetchone()[0] == 0:
        training_data = [
            ("biến trong python là gì", "definition"),
            ("thế nào là hàm", "definition"),
            ("khái niệm vòng lặp", "definition"),
            ("cho tôi ví dụ về biến", "example"),
            ("lấy ví dụ về hàm", "example"),
            ("cách khai báo biến", "how_to"),
            ("làm thế nào để tạo hàm", "how_to"),
            ("cho tôi bài tập về biến", "exercise"),
            ("gửi bài tập hàm", "exercise"),
            ("so sánh list và tuple", "compare"),
            ("sự khác nhau giữa for và while", "compare"),
        ]
        for q, c in training_data:
            cursor.execute('''
            INSERT INTO training_data (question, category, created_at)
            VALUES (?, ?, ?)
            ''', (q, c, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    print("✅ Database khởi tạo thành công!")


def authenticate(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, full_name FROM users WHERE username = ? AND password = ?", 
                   (username, password))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "role": row[2], "full_name": row[3]}
    return None


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

def search_exercises_by_keyword(keyword):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM exercises WHERE question LIKE ?", (f"%{keyword}%",))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for row in rows:
        results.append({
            "exercise_id": row[1],
            "question": row[2],
            "answer": row[5],
            "type": row[3],
            "subject": row[6]
        })
    return results


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
            "level": row[7],
            "tags": json.loads(row[8])
        })
    return exercises

def get_exercises_by_topic(topic, subject, level, student_id):
    all_exercises = get_exercises(subject=subject, level=level)
    
    topic_exercises = []
    for ex in all_exercises:
        if topic in ex["question"].lower() or any(topic in tag.lower() for tag in ex.get("tags", [])):
            topic_exercises.append(ex)
    
    unsolved = []
    for ex in topic_exercises:
        if not get_exercise_history(student_id, ex["exercise_id"]):
            unsolved.append(ex)
    
    return unsolved

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


def save_chat_message(student_id, subject, role, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO chat_history (student_id, subject, role, content, created_at)
    VALUES (?, ?, ?, ?, ?)
    ''', (student_id, subject, role, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_chat_history(student_id, subject, limit=50):
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


init_database()