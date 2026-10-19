from pathlib import Path
import pickle

import mysql.connector
from mysql.connector import errorcode
import pandas as pd
from flask import Flask, flash, redirect, render_template, request, url_for
from sklearn.linear_model import LogisticRegression


app = Flask(__name__)
app.secret_key = "student-performance-secret"

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model.pkl"
DATASET_PATH = BASE_DIR / "student_data.csv"

def create_database_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="flask_db",
        )
    except mysql.connector.Error as err:
        if err.errno != errorcode.ER_BAD_DB_ERROR:
            raise

        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS flask_db")
        cursor.close()
        connection.database = "flask_db"

    return connection


db = create_database_connection()


def get_cursor():
    return db.cursor()


def ensure_tables():
    cursor = get_cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            course VARCHAR(100)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT,
            study_hours FLOAT,
            attendance FLOAT,
            previous_grade FLOAT,
            result VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
        """
    )
    db.commit()
    cursor.close()


def train_and_save_model():
    df = pd.read_csv(DATASET_PATH)
    x_data = df[["study_hours", "attendance", "previous_grade"]]
    y_data = df["result"]

    trained_model = LogisticRegression()
    trained_model.fit(x_data, y_data)

    with MODEL_PATH.open("wb") as model_file:
        pickle.dump(trained_model, model_file)

    return trained_model


def load_model():
    if not MODEL_PATH.exists():
        return train_and_save_model()

    with MODEL_PATH.open("rb") as model_file:
        return pickle.load(model_file)


ensure_tables()
model = load_model()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"].strip()
        course = request.form["course"].strip()

        if not name or not course:
            flash("Name and course are required.", "danger")
            return redirect(url_for("add_student"))

        cursor = get_cursor()
        cursor.execute(
            "INSERT INTO students (name, course) VALUES (%s, %s)",
            (name, course),
        )
        db.commit()
        cursor.close()

        flash("Student record saved successfully.", "success")
        return redirect(url_for("view_students"))

    return render_template("add_student.html")


@app.route("/students")
def view_students():
    cursor = get_cursor()
    cursor.execute("SELECT * FROM students ORDER BY id DESC")
    data = cursor.fetchall()
    cursor.close()
    return render_template("students.html", students=data)


@app.route("/delete/<int:id>")
def delete(id):
    cursor = get_cursor()
    cursor.execute("DELETE FROM predictions WHERE student_id=%s", (id,))
    cursor.execute("DELETE FROM students WHERE id=%s", (id,))
    db.commit()
    cursor.close()

    flash("Student and related predictions deleted.", "warning")
    return redirect(url_for("view_students"))


@app.route("/edit/<int:id>")
def edit_student(id):
    cursor = get_cursor()
    cursor.execute("SELECT * FROM students WHERE id=%s", (id,))
    student = cursor.fetchone()
    cursor.close()

    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("view_students"))

    return render_template("edit_student.html", student=student)


@app.route("/update/<int:id>", methods=["POST"])
def update_student(id):
    name = request.form["name"].strip()
    course = request.form["course"].strip()

    if not name or not course:
        flash("Name and course are required.", "danger")
        return redirect(url_for("edit_student", id=id))

    cursor = get_cursor()
    cursor.execute(
        "UPDATE students SET name=%s, course=%s WHERE id=%s",
        (name, course, id),
    )
    db.commit()
    cursor.close()

    flash("Student record updated.", "success")
    return redirect(url_for("view_students"))


@app.route("/predict", methods=["GET", "POST"])
def predict():
    cursor = get_cursor()
    cursor.execute("SELECT * FROM students ORDER BY name ASC")
    students = cursor.fetchall()

    if request.method == "POST":
        if not students:
            cursor.close()
            flash("Add a student record before making a prediction.", "danger")
            return redirect(url_for("add_student"))

        student_id = request.form["student_id"]
        hours = float(request.form["hours"])
        attendance = float(request.form["attendance"])
        prev_grade = float(request.form["grade"])

        prediction = model.predict([[hours, attendance, prev_grade]])
        result = "Pass" if prediction[0] == 1 else "Fail"

        cursor.execute(
            """
            INSERT INTO predictions (student_id, study_hours, attendance, previous_grade, result)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (student_id, hours, attendance, prev_grade, result),
        )
        db.commit()

        cursor.execute(
            """
            SELECT p.id, s.name, p.study_hours, p.attendance, p.previous_grade, p.result, p.created_at
            FROM predictions p
            JOIN students s ON p.student_id = s.id
            ORDER BY p.created_at DESC
            LIMIT 10
            """
        )
        history = cursor.fetchall()
        cursor.close()
        return render_template(
            "predict.html",
            result=result,
            students=students,
            history=history,
        )

    cursor.execute(
        """
        SELECT p.id, s.name, p.study_hours, p.attendance, p.previous_grade, p.result, p.created_at
        FROM predictions p
        JOIN students s ON p.student_id = s.id
        ORDER BY p.created_at DESC
        LIMIT 10
        """
    )
    history = cursor.fetchall()
    cursor.close()
    return render_template("predict.html", students=students, history=history)


@app.route("/dashboard")
def dashboard():
    cursor = get_cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = cursor.fetchone()[0]

    cursor.execute("SELECT result, COUNT(*) FROM predictions GROUP BY result")
    stats = cursor.fetchall()

    cursor.execute(
        """
        SELECT s.name, p.result, p.study_hours, p.attendance, p.previous_grade, p.created_at
        FROM predictions p
        JOIN students s ON p.student_id = s.id
        ORDER BY p.created_at DESC
        LIMIT 8
        """
    )
    recent_predictions = cursor.fetchall()
    cursor.close()

    return render_template(
        "dashboard.html",
        students=total_students,
        predictions=total_predictions,
        stats=stats,
        recent_predictions=recent_predictions,
    )


if __name__ == "__main__":
    app.run(debug=True)
