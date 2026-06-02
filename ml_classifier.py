import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import database as db

class MLQuestionClassifier:
    def __init__(self, model_path="ml_model.joblib"):
        self.model_path = model_path
        self.pipeline = None
        self.load_or_train()
    
    def get_training_data(self):
        return db.get_all_training_data()
    
    def get_default_data(self):
        return [
            ("biến trong python là gì", "definition"),
            ("thế nào là hàm", "definition"),
            ("khái niệm vòng lặp", "definition"),
            ("cho tôi ví dụ về biến", "example"),
            ("lấy ví dụ về hàm", "example"),
            ("cách khai báo biến", "how_to"),
            ("làm thế nào để tạo hàm", "how_to"),
            ("cho tôi bài tập về biến", "exercise"),
            ("gửi bài tập hàm", "exercise"),
        ]
    
    def train(self):
        print("🤖 Đang huấn luyện AI học máy...")
        data = self.get_training_data()
        
        if not data:
            data = self.get_default_data()
        
        questions = [item[0] for item in data]
        labels = [item[1] for item in data]
        
        self.pipeline = make_pipeline(
            TfidfVectorizer(ngram_range=(1, 2), max_features=5000),
            MultinomialNB()
        )
        
        self.pipeline.fit(questions, labels)
        joblib.dump(self.pipeline, self.model_path)
        
        accuracy = self.pipeline.score(questions, labels)
        print(f"✅ Huấn luyện thành công! Độ chính xác: {accuracy:.2%}")
    
    def load_or_train(self):
        if os.path.exists(self.model_path):
            try:
                self.pipeline = joblib.load(self.model_path)
                print("✅ Đã tải mô hình AI có sẵn")
            except:
                self.train()
        else:
            self.train()
    
    def predict(self, question):
        if not self.pipeline:
            return "general", 0.5
        try:
            predicted = self.pipeline.predict([question])[0]
            probs = self.pipeline.predict_proba([question])[0]
            return predicted, max(probs)
        except:
            return "general", 0.5
    
    def learn_new(self, question, category):
        db.add_training_data(question, category)
        all_data = self.get_training_data()
        if len(all_data) % 10 == 0:
            self.train()