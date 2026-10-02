CREATE DATABASE IF NOT EXISTS student_db;
USE student_db;
DROP TABLE IF EXISTS students;

CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    age        INT NOT NULL,
    course     VARCHAR(100) NOT NULL,
    marks      DECIMAL(5,2) NOT NULL,
    email      VARCHAR(120) UNIQUE,
    CONSTRAINT chk_age   CHECK (age BETWEEN 5 AND 100),
    CONSTRAINT chk_marks CHECK (marks BETWEEN 0 AND 100)
);

INSERT INTO students (name, age, course, marks, email) VALUES
('Anurag Yadav',  20, 'Computer Science', 78.50, 'anurag@gmail.com'),
('Priya Verma',   21, 'Electronics',      65.25, 'priya@gmail.com'),
('Rohan Singh',   19, 'Mechanical',       38.00, 'rohan@gmail.com'),
('Simran Kaur',   20, 'Computer Science', 91.75, 'simran@gmail.com'),
('Karan Mehta',   22, 'Civil',            55.00, 'karan@gmail.com'),
('Neha Gupta',    21, 'Electronics',      34.50, 'neha@gmail.com'),
('Arjun Patel',   20, 'Mechanical',       72.00, 'arjun@gmail.com'),
('Anjali Rao',    19, 'Computer Science', 84.00, 'anjali@gmail.com'),
('Manpreet Singh',22, 'Civil',            47.50, 'manpreet@gmail.com'),
('Divya Nair',    20, 'Electronics',      88.25, 'divya@gmail.com');