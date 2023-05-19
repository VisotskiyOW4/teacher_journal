from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, \
    QPushButton, QDialog, QLabel, QLineEdit, QMessageBox, QComboBox, QHBoxLayout, QFormLayout
from PyQt5.QtCore import Qt
import mysql.connector

# З'єднання з базою даних
mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="teacher_journal"
)

# Створення курсора
cursor = mydb.cursor()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Задаємо заголовок вікна
        self.setWindowTitle("Електронний журнал вчителя")

        # Задаємо розміри вікна
        self.setGeometry(100, 100, 800, 600)

        # Створюємо головний контейнер для вміщення вмісту
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Створюємо вертикальний макет для вміщення елементів у контейнері
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Створюємо таблицю для відображення оцінок
        self.grades_table = QTableWidget()
        self.grades_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Вимикаємо редагування таблиці
        self.grades_table.setSelectionBehavior(QTableWidget.SelectRows)  # Виділяти цілі рядки
        self.grades_table.verticalHeader().setVisible(False)  # Приховуємо вертикальні заголовки
        self.grades_table.setAlternatingRowColors(True)  # Використовувати альтернативні кольори для рядків
        self.grades_table.setStyleSheet("QTableView { selection-background-color: #86c1e8; }")  # Колір виділення
        self.grades_table.setFont(QFont("Arial", 10))  # Задаємо шрифт для тексту в таблиці

        # Створюємо кнопки для додавання, редагування та видалення оцінок
        self.add_grade_button = QPushButton("Додати оцінку")
        self.edit_grade_button = QPushButton("Редагувати оцінку")
        self.delete_grade_button = QPushButton("Видалити оцінку")

        # Додавання таблиці, випадаючого списку та кнопок до головного контейнера
        main_layout.addWidget(self.grades_table)
        main_layout.addWidget(self.add_grade_button)
        main_layout.addWidget(self.edit_grade_button)
        main_layout.addWidget(self.delete_grade_button)

        # Встановлюємо стиль за замовчуванням для додатку
        self.setStyleSheet(
            "QMainWindow { background-color: #ffffff; }"
            "QTableWidget { background-color: #ffffff; color: #000000; border: none; }"
            "QHeaderView::section { background-color: #86c1e8; color: #ffffff; border: none; }"
        )

        # Підключаємо функціонал до кнопок
        self.add_grade_button.clicked.connect(self.add_grade)
        self.edit_grade_button.clicked.connect(self.edit_grade)
        self.delete_grade_button.clicked.connect(self.delete_grade)

        # Відображення оцінок при запуску програми
        self.display_grades()

    def display_grades(self):
        # Очистити таблицю
        self.grades_table.clear()
        self.grades_table.setRowCount(0)
        self.grades_table.setColumnCount(4)
        self.grades_table.setHorizontalHeaderLabels(["ID", "Учень", "Предмет", "Оцінка"])

        # Отримати дані з бази даних
        sql = "SELECT grades.grade_id, students.name, subjects.subject_name, grades.grade FROM grades " \
              "INNER JOIN students ON grades.student_id = students.student_id " \
              "INNER JOIN subjects ON grades.subject_id = subjects.subject_id"
        cursor.execute(sql)
        grades = cursor.fetchall()

        # Відображення даних у таблиці
        for row_number, row_data in enumerate(grades):
            self.grades_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.grades_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        # Автоматичне налаштування ширини стовпців
        self.grades_table.resizeColumnsToContents()

    def add_grade(self):
        dialog = AddGradeDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.display_grades()

    def edit_grade(self):
        selected_row = self.grades_table.currentRow()
        if selected_row != -1:
            grade_id = self.grades_table.item(selected_row, 0).text()
            dialog = EditGradeDialog(grade_id, self)
            if dialog.exec_() == QDialog.Accepted:
                self.display_grades()
        else:
            QMessageBox.warning(self, "Помилка", "Будь ласка, виберіть оцінку для редагування.")

    def delete_grade(self):
        selected_row = self.grades_table.currentRow()
        if selected_row != -1:
            grade_id = self.grades_table.item(selected_row, 0).text()
            reply = QMessageBox.question(self, "Підтвердження видалення",
                                         "Ви впевнені, що хочете видалити цю оцінку?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                # Видалення оцінки з бази даних
                # ...
                self.display_grades()
        else:
            QMessageBox.warning(self, "Помилка", "Будь ласка, виберіть оцінку для видалення.")

    def add_grade(self):
        dialog = AddGradeDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.display_grades()


class AddGradeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Додати оцінку")

        layout = QFormLayout()

        self.student_combo = QComboBox()
        self.student_combo.addItems(get_student_names())
        layout.addRow("Учень:", self.student_combo)

        self.subject_combo = QComboBox()
        self.subject_combo.addItems(get_subject_names())
        layout.addRow("Предмет:", self.subject_combo)

        self.grade_input = QLineEdit()
        layout.addRow("Оцінка:", self.grade_input)

        button_layout = QHBoxLayout()
        layout.addRow(button_layout)

        add_button = QPushButton("Додати")
        add_button.clicked.connect(self.add_grade)
        button_layout.addWidget(add_button)

        cancel_button = QPushButton("Скасувати")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        self.setLayout(layout)

    def add_grade(self):
        student = self.student_input.text()
        subject = self.subject_input.text()
        grade = self.grade_input.text()

        if student and subject and grade:
            # Отримати student_id за допомогою запиту до students таблиці
            sql = "SELECT student_id FROM students WHERE name = %s"
            val = (student,)
            cursor.execute(sql, val)
            student_result = cursor.fetchone()

            # Отримати subject_id за допомогою запиту до subjects таблиці
            sql = "SELECT subject_id FROM subjects WHERE subject_name = %s"
            val = (subject,)
            cursor.execute(sql, val)
            subject_result = cursor.fetchone()

            if student_result and subject_result:
                student_id = student_result[0]
                subject_id = subject_result[0]

                # Додати оцінку до grades таблиці
                sql = "INSERT INTO grades (student_id, subject_id, grade) VALUES (%s, %s, %s)"
                val = (student_id, subject_id, grade)
                cursor.execute(sql, val)
                mydb.commit()
                self.accept()
            else:
                QMessageBox.warning(self, "Помилка", "Невірне ім'я учня або предмета.")
        else:
            QMessageBox.warning(self, "Помилка", "Будь ласка, заповніть всі поля.")


class EditGradeDialog(QDialog):
    def __init__(self, grade_id, parent=None):

        super().__init__(parent)
        self.setWindowTitle("Редагувати оцінку")
        self.grade_id = grade_id

        layout = QVBoxLayout()

        self.grade_label = QLabel("Оцінка:")
        layout.addWidget(self.grade_label)

        self.grade_input = QLineEdit()
        layout.addWidget(self.grade_input)

        self.save_button = QPushButton("Зберегти")
        self.save_button.clicked.connect(self.save_grade)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        self.load_grade()

    def load_grade(self):
        sql = "SELECT grade FROM grades WHERE grade_id = %s"
        val = (self.grade_id,)
        cursor.execute(sql, val)
        result = cursor.fetchone()

        if result:
            grade = result[0]
            self.grade_input.setText(str(grade))

    def save_grade(self):
        grade = self.grade_input.text()

        if grade:
            sql = "UPDATE grades SET grade = %s WHERE grade_id = %s"
            val = (grade, self.grade_id)
            cursor.execute(sql, val)
            mydb.commit()
            self.accept()
        else:
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть оцінку.")


class DeleteGradeDialog(QDialog):
    def __init__(self, grade_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Видалити оцінку")
        self.grade_id = grade_id

        layout = QVBoxLayout()

        label = QLabel("Ви впевнені, що хочете видалити цю оцінку?")
        layout.addWidget(label)

        delete_button = QPushButton("Видалити")
        delete_button.clicked.connect(self.delete_grade)
        layout.addWidget(delete_button)

        cancel_button = QPushButton("Скасувати")
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)

        self.setLayout(layout)

    def delete_grade(self):
        sql = "DELETE FROM grades WHERE grade_id = %s"
        val = (self.grade_id,)
        cursor.execute(sql, val)
        mydb.commit()
        self.accept()


class AddGradeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Додати оцінку")

        layout = QVBoxLayout()

        self.student_label = QLabel("Учень:")
        layout.addWidget(self.student_label)

        self.student_combo = QComboBox()
        self.student_combo.addItems(get_student_names())
        layout.addWidget(self.student_combo)

        self.subject_label = QLabel("Предмет:")
        layout.addWidget(self.subject_label)

        self.subject_combo = QComboBox()
        self.subject_combo.addItems(get_subject_names())
        layout.addWidget(self.subject_combo)

        self.grade_label = QLabel("Оцінка:")
        layout.addWidget(self.grade_label)

        self.grade_input = QLineEdit()
        layout.addWidget(self.grade_input)

        self.add_button = QPushButton("Додати")
        self.add_button.clicked.connect(self.add_grade)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def add_grade(self):
        student = self.student_combo.currentText()
        subject = self.subject_combo.currentText()
        grade = self.grade_input.text()

        if student and subject and grade:
            # Отримати student_id за допомогою запиту до students таблиці
            sql = "SELECT student_id FROM students WHERE name = %s"
            val = (student,)
            cursor.execute(sql, val)
            student_result = cursor.fetchone()

            # Отримати subject_id за допомогою запиту до subjects таблиці
            sql = "SELECT subject_id FROM subjects WHERE subject_name = %s"
            val = (subject,)
            cursor.execute(sql, val)
            subject_result = cursor.fetchone()

            if student_result and subject_result:
                student_id = student_result[0]
                subject_id = subject_result[0]

                # Додати оцінку до grades таблиці
                sql = "INSERT INTO grades (student_id, subject_id, grade) VALUES (%s, %s, %s)"
                val = (student_id, subject_id, grade)
                cursor.execute(sql, val)
                mydb.commit()
                self.accept()
            else:
                QMessageBox.warning(self, "Помилка", "Невірне ім'я учня або предмета.")
        else:
            QMessageBox.warning(self, "Помилка", "Будь ласка, заповніть всі поля.")


def get_student_names():
    sql = "SELECT name FROM students"
    cursor.execute(sql)
    students = cursor.fetchall()
    return [student[0] for student in students]


def get_subject_names():
    sql = "SELECT subject_name FROM subjects"
    cursor.execute(sql)
    subjects = cursor.fetchall()
    return [subject[0] for subject in subjects]


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
