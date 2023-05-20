from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, \
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox
from PyQt5.QtCore import Qt
import mysql.connector


class ElectronicJournal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Електронний журнал вчителя")
        self.setGeometry(100, 100, 800, 600)

        self.setup_ui()
        self.connect_db()
        self.synchronize_data()

    def setup_ui(self):
        # Віджети для введення даних
        self.student_name_combo = QComboBox()
        self.subject_combo = QComboBox()
        self.grade_input = QLineEdit()
        self.teacher_combo = QComboBox()

        # Кнопки
        self.filter_button = QPushButton("Фільтрувати за учнем")
        self.add_grade_button = QPushButton("Додати оцінку")
        self.edit_grade_button = QPushButton("Редагувати оцінку")
        self.delete_grade_button = QPushButton("Видалити оцінку")

        self.filter_button.clicked.connect(self.apply_student_filter)
        self.add_grade_button.clicked.connect(self.add_grade)
        self.edit_grade_button.clicked.connect(self.edit_grade)
        self.delete_grade_button.clicked.connect(self.delete_grade)

        # Таблиця для відображення оцінок
        self.grades_table = QTableWidget()
        self.grades_table.setColumnCount(4)
        self.grades_table.setHorizontalHeaderLabels(["Учень", "Предмет", "Оцінка", "Вчитель"])

        # Головний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Розміщення віджетів
        main_layout = QVBoxLayout(central_widget)
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Учень:"))
        input_layout.addWidget(self.student_name_combo)
        input_layout.addWidget(QLabel("Предмет:"))
        input_layout.addWidget(self.subject_combo)
        input_layout.addWidget(QLabel("Оцінка:"))
        input_layout.addWidget(self.grade_input)
        input_layout.addWidget(QLabel("Вчитель:"))
        input_layout.addWidget(self.teacher_combo)
        input_layout.addWidget(self.filter_button)
        input_layout.addWidget(self.add_grade_button)
        input_layout.addWidget(self.edit_grade_button)
        input_layout.addWidget(self.delete_grade_button)
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.grades_table)

    def connect_db(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="teacher_journal"
        )
        self.cursor = self.db.cursor()

    def apply_student_filter(self):
        student_name = self.student_name_combo.currentText()
        self.filter_grades_by_student(student_name)

    def add_grade(self):
        student_name = self.student_name_combo.currentText()
        subject = self.subject_combo.currentText()
        grade = self.grade_input.text()
        teacher = self.teacher_combo.currentText()

        # Отримання ID учня за іменем
        query = "SELECT id FROM students WHERE name = %s"
        self.cursor.execute(query, (student_name,))
        student_id = self.cursor.fetchone()[0]

        # Отримання ID предмета за назвою
        query = "SELECT id FROM subjects WHERE name = %s"
        self.cursor.execute(query, (subject,))
        subject_id = self.cursor.fetchone()[0]

        # Отримання ID вчителя за іменем
        query = "SELECT id FROM teachers WHERE name = %s"
        self.cursor.execute(query, (teacher,))
        teacher_id = self.cursor.fetchone()[0]

        # Додавання оцінки до бази даних
        query = "INSERT INTO grades (student_id, subject_id, grade, teacher_id) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(query, (student_id, subject_id, grade, teacher_id))
        self.db.commit()

        # Очищення полів вводу
        self.grade_input.clear()
        self.synchronize_data()

    def edit_grade(self):
        print("Edit button clicked")
        current_row = self.grades_table.currentRow()
        if current_row >= 0:
            student_name = self.grades_table.item(current_row, 0).text()
            subject = self.grades_table.item(current_row, 1).text()
            grade = self.grade_input.text()
            teacher = self.grades_table.item(current_row, 3).text()

            # Отримання ID учня за іменем
            query = "SELECT id FROM students WHERE name = %s"
            self.cursor.execute(query, (student_name,))
            student_id = self.cursor.fetchone()[0]

            # Отримання ID предмета за назвою
            query = "SELECT id FROM subjects WHERE name = %s"
            self.cursor.execute(query, (subject,))
            subject_id = self.cursor.fetchone()[0]

            # Отримання ID вчителя за іменем
            query = "SELECT id FROM teachers WHERE name = %s"
            self.cursor.execute(query, (teacher,))
            teacher_id = self.cursor.fetchone()[0]

            # Оновлення оцінки у базі даних
            query = "UPDATE grades SET grade = %s WHERE student_id = %s AND subject_id = %s AND teacher_id = %s"
            self.cursor.execute(query, (grade, student_id, subject_id, teacher_id))
            self.db.commit()
            self.synchronize_data()

    def delete_grade(self):
        print("Delete button click")
        current_row = self.grades_table.currentRow()
        if current_row >= 0:
            student_name = self.grades_table.item(current_row, 0).text()
            subject = self.grades_table.item(current_row, 1).text()
            teacher = self.grades_table.item(current_row, 3).text()

            # Отримання ID учня за іменем
            query = "SELECT id FROM students WHERE name = %s"
            self.cursor.execute(query, (student_name,))
            student_id = self.cursor.fetchone()[0]

            # Отримання ID предмета за назвою
            query = "SELECT id FROM subjects WHERE name = %s"
            self.cursor.execute(query, (subject,))
            subject_id = self.cursor.fetchone()[0]

            # Отримання ID вчителя за іменем
            query = "SELECT id FROM teachers WHERE name = %s"
            self.cursor.execute(query, (teacher,))
            teacher_id = self.cursor.fetchone()[0]

            # Видалення оцінки з бази даних
            query = "DELETE FROM grades WHERE student_id = %s AND subject_id = %s AND teacher_id = %s"
            self.cursor.execute(query, (student_id, subject_id, teacher_id))
            self.db.commit()
            self.synchronize_data()

    def load_data(self):
        self.grades_table.setRowCount(0)

        # Отримання даних про оцінки з бази даних
        query = """
            SELECT students.name, subjects.name, grades.grade, teachers.name
        FROM grades
        JOIN students ON grades.student_id = students.id
        JOIN subjects ON grades.subject_id = subjects.id
        JOIN classes ON students.class_id = classes.id
        JOIN teachers ON classes.teacher_id = teachers.id
        """
        self.cursor.execute(query)
        grades = self.cursor.fetchall()

        # Відображення даних у таблиці
        for row_num, (student_name, subject, grade, teacher) in enumerate(grades):
            self.grades_table.insertRow(row_num)
            self.grades_table.setItem(row_num, 0, QTableWidgetItem(student_name))
            self.grades_table.setItem(row_num, 1, QTableWidgetItem(subject))
            self.grades_table.setItem(row_num, 2, QTableWidgetItem(str(grade)))
            self.grades_table.setItem(row_num, 3, QTableWidgetItem(teacher))

    def filter_grades_by_student(self, student_name):
        self.grades_table.setRowCount(0)

        # Отримання даних про оцінки за учнем з бази даних
        query = """
            SELECT students.name, subjects.name, grades.grade, teachers.name
            FROM grades
            JOIN students ON grades.student_id = students.id
            JOIN subjects ON grades.subject_id = subjects.id
            JOIN classes ON students.class_id = classes.id
            JOIN teachers ON classes.teacher_id = teachers.id
            WHERE students.name = %s
        """
        self.cursor.execute(query, (student_name,))
        grades = self.cursor.fetchall()

        # Відображення даних у таблиці
        for row_num, (student_name, subject, grade, teacher) in enumerate(grades):
            self.grades_table.insertRow(row_num)
            self.grades_table.setItem(row_num, 0, QTableWidgetItem(student_name))
            self.grades_table.setItem(row_num, 1, QTableWidgetItem(subject))
            self.grades_table.setItem(row_num, 2, QTableWidgetItem(str(grade)))
            self.grades_table.setItem(row_num, 3, QTableWidgetItem(teacher))

    def synchronize_data(self):
        self.load_students()
        self.load_subjects()
        self.load_teachers()
        self.load_data()

    def load_students(self):
        self.student_name_combo.clear()

        query = "SELECT name FROM students"
        self.cursor.execute(query)
        students = self.cursor.fetchall()

        for student in students:
            self.student_name_combo.addItem(student[0])

    def load_subjects(self):
        self.subject_combo.clear()

        query = "SELECT name FROM subjects"
        self.cursor.execute(query)
        subjects = self.cursor.fetchall()

        for subject in subjects:
            self.subject_combo.addItem(subject[0])

    def load_teachers(self):
        self.teacher_combo.clear()

        query = "SELECT name FROM teachers"
        self.cursor.execute(query)
        teachers = self.cursor.fetchall()

        for teacher in teachers:
            self.teacher_combo.addItem(teacher[0])

    def closeEvent(self, event):
        # Закриття з'єднання з базою даних при закритті програми
        self.db.close()


if __name__ == '__main__':
    app = QApplication([])
    window = ElectronicJournal()
    window.show()
    app.exec()
