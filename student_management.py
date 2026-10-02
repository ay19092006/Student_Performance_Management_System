import csv
import os
import re
import mysql.connector
from mysql.connector import Error

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = "Student@123"
DB_NAME = "student_db"
PASS_MARK = 40.0
EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
    )

def run_query(sql, params=(), fetch=False):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, params)
        if fetch:
            return cur.fetchall()
        conn.commit()
        return cur.rowcount
    except Error as e:
        print(f"\n[Database error] {e}")
        return None
    finally:
        if conn is not None and conn.is_connected():
            conn.close()

def read_text(prompt, max_len=100):
    while True:
        value = input(prompt).strip()
        if value and len(value) <= max_len:
            return value
        print(f"  Enter a non-empty value (max {max_len} characters).")

def read_int(prompt, low, high):
    while True:
        try:
            value = int(input(prompt).strip())
            if low <= value <= high:
                return value
            print(f"  Value must be between {low} and {high}.")
        except ValueError:
            print("  Please enter a whole number.")

def read_marks(prompt):
    while True:
        try:
            value = float(input(prompt).strip())
            if 0 <= value <= 100:
                return round(value, 2)
            print("  Marks must be between 0 and 100.")
        except ValueError:
            print("  Please enter a valid number.")

def read_email(prompt):
    while True:
        value = input(prompt).strip()
        if EMAIL_PATTERN.match(value) and len(value) <= 120:
            return value
        print("  Please enter a valid email address.")

def print_students(rows):
    if not rows:
        print("\nNo records found.")
        return
    header = f"{'ID':<5}{'Name':<22}{'Age':<5}{'Course':<20}{'Marks':<8}{'Email'}"
    print("\n" + header)
    print("-" * len(header) + "-" * 20)
    for sid, name, age, course, marks, email in rows:
        print(f"{sid:<5}{name:<22}{age:<5}{course:<20}{float(marks):<8.2f}{email}")
    print(f"\nTotal: {len(rows)} record(s)")

def add_student():
    print("\n--- Add Student ---")
    name = read_text("Name: ")
    age = read_int("Age: ", 5, 100)
    course = read_text("Course: ")
    marks = read_marks("Marks (0-100): ")
    email = read_email("Email: ")
    result = run_query(
        "INSERT INTO students (name, age, course, marks, email) "
        "VALUES (%s, %s, %s, %s, %s)",
        (name, age, course, marks, email),
    )
    if result:
        print("\nStudent added successfully.")

def view_students():
    print("\n--- All Students ---")
    rows = run_query(
        "SELECT student_id, name, age, course, marks, email "
        "FROM students ORDER BY student_id",
        fetch=True,
    )
    if rows is not None:
        print_students(rows)

def search_student():
    print("\n--- Search ---")
    print("1. By ID\n2. By Name\n3. By Course")
    choice = input("Choose: ").strip()
    base = "SELECT student_id, name, age, course, marks, email FROM students WHERE "
    if choice == "1":
        sid = read_int("Student ID: ", 1, 10**9)
        rows = run_query(base + "student_id = %s", (sid,), fetch=True)
    elif choice == "2":
        term = read_text("Name (partial allowed): ")
        rows = run_query(base + "name LIKE %s", (f"%{term}%",), fetch=True)
    elif choice == "3":
        term = read_text("Course (partial allowed): ")
        rows = run_query(base + "course LIKE %s", (f"%{term}%",), fetch=True)
    else:
        print("Invalid choice.")
        return
    if rows is not None:
        print_students(rows)

def student_exists(sid):
    rows = run_query("SELECT 1 FROM students WHERE student_id = %s", (sid,), fetch=True)
    return bool(rows)

def update_student():
    print("\n--- Update Student ---")
    sid = read_int("Student ID to update: ", 1, 10**9)
    if not student_exists(sid):
        print("No student with that ID.")
        return
    print("1. Marks\n2. Email\n3. Course")
    choice = input("What to update: ").strip()
    if choice == "1":
        sql, value = "UPDATE students SET marks = %s WHERE student_id = %s", read_marks("New marks: ")
    elif choice == "2":
        sql, value = "UPDATE students SET email = %s WHERE student_id = %s", read_email("New email: ")
    elif choice == "3":
        sql, value = "UPDATE students SET course = %s WHERE student_id = %s", read_text("New course: ")
    else:
        print("Invalid choice.")
        return
    if run_query(sql, (value, sid)) is not None:
        print("Record updated.")

def delete_student():
    print("\n--- Delete Student ---")
    sid = read_int("Student ID to delete: ", 1, 10**9)
    rows = run_query(
        "SELECT student_id, name, age, course, marks, email "
        "FROM students WHERE student_id = %s",
        (sid,), fetch=True,
    )
    if not rows:
        print("No student with that ID.")
        return
    print_students(rows)
    if input("Delete this record? (yes/no): ").strip().lower() == "yes":
        if run_query("DELETE FROM students WHERE student_id = %s", (sid,)):
            print("Record deleted.")
    else:
        print("Deletion cancelled.")

def performance_report():
    print("\n--- Performance Report ---")
    rows = run_query(
        "SELECT COUNT(*), AVG(marks), MAX(marks), MIN(marks), "
        "SUM(marks >= %s), SUM(marks < %s) FROM students",
        (PASS_MARK, PASS_MARK), fetch=True,
    )
    if not rows or rows[0][0] == 0:
        print("No data available.")
        return
    total, avg, high, low, passed, failed = rows[0]
    print(f"Total students : {total}")
    print(f"Average marks  : {float(avg):.2f}")
    print(f"Highest marks  : {float(high):.2f}")
    print(f"Lowest marks   : {float(low):.2f}")
    print(f"Pass (>= {PASS_MARK:.0f}) : {int(passed)}")
    print(f"Fail (<  {PASS_MARK:.0f}) : {int(failed)}")

    top = run_query(
        "SELECT name, marks FROM students ORDER BY marks DESC LIMIT 3", fetch=True
    )
    if top:
        print("\nTop performers:")
        for i, (name, marks) in enumerate(top, 1):
            print(f"  {i}. {name} - {float(marks):.2f}")

    by_course = run_query(
        "SELECT course, COUNT(*), AVG(marks) FROM students "
        "GROUP BY course ORDER BY AVG(marks) DESC",
        fetch=True,
    )
    if by_course:
        print("\nCourse-wise average:")
        for course, count, avg_c in by_course:
            print(f"  {course:<20} students: {count:<3} avg: {float(avg_c):.2f}")

def export_csv():
    """Optional feature: export all records to CSV."""
    rows = run_query(
        "SELECT student_id, name, age, course, marks, email FROM students", fetch=True
    )
    if not rows:
        print("Nothing to export.")
        return
    try:
        with open("students_export.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["student_id", "name", "age", "course", "marks", "email"])
            writer.writerows(rows)
        print("Exported to students_export.csv")
    except OSError as e:
        print(f"[File error] {e}")

MENU = """
Student Performance Management System
1. Add Student
2. View All Students
3. Search Student
4. Update Student
5. Delete Student
6. Performance Report
7. Export to CSV
0. Exit
"""

ACTIONS = {
    "1": add_student,
    "2": view_students,
    "3": search_student,
    "4": update_student,
    "5": delete_student,
    "6": performance_report,
    "7": export_csv,
}

def main():
    try:
        get_connection().close()
        print("Connected to MySQL successfully.")
    except Error as e:
        print(f"Could not connect to the database: {e}")
        return
    while True:
        print(MENU)
        choice = input("Enter choice: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        action = ACTIONS.get(choice)
        if action:
            action()
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()