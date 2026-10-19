# Student Performance Prediction System

[![Live on Render](https://img.shields.io/badge/Render-Live_App-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://student-performance-prediction-system-4pkl.onrender.com/)
[![Live on GitHub Pages](https://img.shields.io/badge/GitHub_Pages-Interactive_Demo-222222?style=for-the-badge&logo=github&logoColor=white)](https://03dxd12.github.io/Student-Performance-Prediction-System/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Web_Framework-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Machine_Learning-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)

A full-stack Machine Learning web application built with **Flask**, **Scikit-Learn**, and **MySQL / SQLite** to predict student academic outcomes based on study habits, attendance percentage, and prior grades.

---

### 🌐 Live Deployments

- 🚀 **Full Cloud Web Application (Render)**: [https://student-performance-prediction-system-4pkl.onrender.com/](https://student-performance-prediction-system-4pkl.onrender.com/)  
  *(Full CRUD, database persistence, ML prediction logging, and analytics dashboard)*
- ⚡ **Interactive Client Demo (GitHub Pages)**: [https://03dxd12.github.io/Student-Performance-Prediction-System/](https://03dxd12.github.io/Student-Performance-Prediction-System/)  
  *(Instant real-time slider inference with formula & weight visualization)*

---

## 📌 Features

- **Student Management (CRUD)**: Register new students, update records, and view enrolled student profiles.
- **Performance Prediction**: Predict student results (Pass / Fail) using a trained Logistic Regression model based on:
  - Study Hours
  - Attendance Rate (%)
  - Previous Grade
- **Interactive Dashboard**: View prediction histories, student analytics, and overall performance metrics.
- **MySQL Database Integration**: Persistent storage for student profiles and prediction logs.

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Flask
- **Machine Learning**: Scikit-Learn (`LogisticRegression`), Pandas
- **Database**: MySQL (`mysql-connector-python`)
- **Frontend**: HTML5, CSS3, Jinja2 Templates

---

## 🗄️ Database Setup

1. Start your MySQL service (e.g., via XAMPP, WampServer, or native MySQL service).
2. Import the schema file `flask_db.sql` or let Flask initialize it automatically:
   ```sql
   CREATE DATABASE IF NOT EXISTS flask_db;
   USE flask_db;

   CREATE TABLE students (
       id INT AUTO_INCREMENT PRIMARY KEY,
       name VARCHAR(100),
       course VARCHAR(100)
   );

   CREATE TABLE predictions (
       id INT AUTO_INCREMENT PRIMARY KEY,
       student_id INT,
       study_hours FLOAT,
       attendance FLOAT,
       previous_grade FLOAT,
       result VARCHAR(50),
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (student_id) REFERENCES students(id)
   );
   ```

---

## 🚀 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/03DxD12/Student-Performance-Prediction-System.git
   cd Student-Performance-Prediction-System
   ```

2. **Create and activate a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install flask mysql-connector-python pandas scikit-learn
   ```

4. **Train the ML model** (generates `model.pkl`):
   ```bash
   python train_model.py
   ```

5. **Run the Flask application**:
   ```bash
   python app.py
   ```
   Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 📂 Project Structure

```text
├── app.py               # Main Flask application & routing
├── train_model.py       # Script to train logistic regression model
├── model.pkl            # Serialized trained model
├── student_data.csv     # Training dataset
├── flask_db.sql         # MySQL database schema
├── templates/           # HTML templates (Jinja2)
│   ├── index.html
│   ├── dashboard.html
│   ├── students.html
│   ├── add_student.html
│   ├── edit_student.html
│   └── predict.html
└── static/              # CSS, JavaScript, and static assets
```
