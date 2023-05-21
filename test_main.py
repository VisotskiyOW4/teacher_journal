import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, \
    QPushButton, QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem, QDialog, QDialogButtonBox
import mysql.connector


class AddDataTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.teacher_name_label = QLabel("Teacher Name:")
        self.teacher_name_input = QLineEdit()

        self.subject_name_label = QLabel("Subject Name:")
        self.subject_name_input = QLineEdit()

        self.student_name_label = QLabel("Student Name:")
        self.student_name_input = QLineEdit()

        self.class_name_label = QLabel("Class Name:")
        self.class_name_input = QLineEdit()

        self.grade_label = QLabel("Grade:")
        self.grade_input = QLineEdit()

        self.add_data_button = QPushButton("Add Data")
        self.add_data_button.clicked.connect(self.add_data)

        self.layout.addWidget(self.teacher_name_label)
        self.layout.addWidget(self.teacher_name_input)
        self.layout.addWidget(self.subject_name_label)
        self.layout.addWidget(self.subject_name_input)
        self.layout.addWidget(self.student_name_label)
        self.layout.addWidget(self.student_name_input)
        self.layout.addWidget(self.class_name_label)
        self.layout.addWidget(self.class_name_input)
        self.layout.addWidget(self.grade_label)
        self.layout.addWidget(self.grade_input)
        self.layout.addWidget(self.add_data_button)

        self.setLayout(self.layout)

    def add_data(self):
        teacher_name = self.teacher_name_input.text()
        subject_name = self.subject_name_input.text()
        student_name = self.student_name_input.text()
        class_name = self.class_name_input.text()
        grade = self.grade_input.text()

        if not teacher_name or not subject_name or not student_name or not class_name or not grade:
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")
            return

        try:
            connection = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="",
                database="journal"
            )
            cursor = connection.cursor()

            # Отримання teacher_id за допомогою teacher_name
            cursor.execute("SELECT teacher_id FROM teachers WHERE teacher_name = %s", (teacher_name,))
            teacher_id = cursor.fetchone()
            if teacher_id is None:
                # Додавання нового вчителя
                cursor.execute("INSERT INTO teachers (teacher_name) VALUES (%s)", (teacher_name,))
                teacher_id = cursor.lastrowid

            # Отримання subject_id за допомогою subject_name
            cursor.execute("SELECT subject_id FROM subjects WHERE subject_name = %s", (subject_name,))
            subject_id = cursor.fetchone()
            if subject_id is None:
                # Додавання нового предмету
                cursor.execute("INSERT INTO subjects (subject_name) VALUES (%s)", (subject_name,))
                subject_id = cursor.lastrowid

            # Отримання student_id за допомогою student_name і class_name
            cursor.execute("SELECT student_id FROM students WHERE student_name = %s AND class_name = %s",
                           (student_name, class_name))
            student_id = cursor.fetchone()
            if student_id is None:
                # Додавання нового учня
                cursor.execute("INSERT INTO students (student_name, class_name) VALUES (%s, %s)",
                               (student_name, class_name))
                student_id = cursor.lastrowid

            # Додавання оцінки
            cursor.execute("INSERT INTO grades (teacher_id, subject_id, student_id, grade) "
                           "VALUES (%s, %s, %s, %s)", (teacher_id, subject_id, student_id, grade))

            connection.commit()

            QMessageBox.information(self, "Success", "Data added successfully.")

            # Очищення полів вводу
            self.teacher_name_input.clear()
            self.subject_name_input.clear()
            self.student_name_input.clear()
            self.class_name_input.clear()
            self.grade_input.clear()

        except mysql.connector.Error as error:
            QMessageBox.critical(self, "Error", f"Failed to add data to database: {error}")

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


class DisplayDataTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.button_refresh = QPushButton("Refresh Data")
        self.layout.addWidget(self.button_refresh)

        self.button_edit = QPushButton("Edit Data")
        self.layout.addWidget(self.button_edit)

        self.button_delete = QPushButton("Delete")
        self.layout.addWidget(self.button_delete)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.button_refresh.clicked.connect(self.refresh_data)
        self.button_edit.clicked.connect(self.edit_data)
        self.button_delete.clicked.connect(self.delete_data)

        self.load_data()

    def load_data(self):
        try:
            connection = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="",
                database="journal"
            )
            cursor = connection.cursor()

            query = ("SELECT grades.id, teachers.teacher_name, subjects.subject_name, students.student_name, "
                     "students.class_name, grades.grade "
                     "FROM grades "
                     "JOIN teachers ON grades.teacher_id = teachers.teacher_id "
                     "JOIN subjects ON grades.subject_id = subjects.subject_id "
                     "JOIN students ON grades.student_id = students.student_id")
            cursor.execute(query)
            data = cursor.fetchall()

            # Clear the table
            self.table.clear()

            # Set the column headers
            column_headers = ["ID", "Teacher Name", "Subject Name", "Student Name", "Class Name", "Grade"]
            self.table.setColumnCount(len(column_headers))
            self.table.setHorizontalHeaderLabels(column_headers)

            # Set the row count
            self.table.setRowCount(len(data))

            # Populate the table with data
            for row in range(len(data)):
                for col in range(len(data[row])):
                    item = QTableWidgetItem(str(data[row][col]))
                    self.table.setItem(row, col, item)

            self.table.resizeColumnsToContents()
        except mysql.connector.Error as error:
            QMessageBox.critical(self, "Error", f"An error occurred while loading data: {str(error)}")
        finally:
            cursor.close()
            connection.close()

    def refresh_data(self):
        self.load_data()

    def edit_data(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if len(selected_rows) == 0:
            QMessageBox.warning(self, "No Rows Selected", "Please select a row to edit.")
            return

        selected_row = selected_rows[0]
        id_index = 0  # Index of the ID column in the table
        id_value = int(self.table.item(selected_row.row(), id_index).text())

        dialog = EditDataDialog(id_value, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_edited_data()

            try:
                connection = mysql.connector.connect(
                    host="127.0.0.1",
                    user="root",
                    password="",
                    database="journal"
                )
                cursor = connection.cursor()

                # Verify if the new teacher_id exists in the teachers table
                teacher_id = new_data[0]
                select_teacher_query = "SELECT teacher_id FROM teachers WHERE teacher_id = %s"
                cursor.execute(select_teacher_query, (teacher_id,))
                result = cursor.fetchone()
                if not result:
                    QMessageBox.warning(self, "Invalid Teacher ID", "The specified teacher ID does not exist.")
                    return

                update_query = ("UPDATE grades "
                                "SET teacher_id = %s, subject_id = %s, student_id = %s, grade = %s "
                                "WHERE id = %s")
                cursor.execute(update_query, (*new_data, id_value))
                connection.commit()

                QMessageBox.information(self, "Data Updated", "Data has been updated successfully.")
                self.load_data()
            except mysql.connector.Error as error:
                QMessageBox.critical(self, "Error", f"An error occurred while updating data: {str(error)}")
            finally:
                cursor.close()
                connection.close()

    def delete_data(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if len(selected_rows) == 0:
            QMessageBox.warning(self, "No Rows Selected", "Please select a row to delete.")
            return

        selected_row = selected_rows[0]
        id_index = 0  # Index of the ID column in the table
        id_value = self.table.item(selected_row.row(), id_index).text()

        reply = QMessageBox.question(self, "Confirm Deletion",
                                     "Are you sure you want to delete this data?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                connection = mysql.connector.connect(
                    host="127.0.0.1",
                    user="root",
                    password="",
                    database="journal"
                )
                cursor = connection.cursor()

                delete_query = "DELETE FROM grades WHERE id = %s"
                cursor.execute(delete_query, (id_value,))
                connection.commit()

                QMessageBox.information(self, "Data Deleted", "Data has been deleted successfully.")
                self.load_data()
            except mysql.connector.Error as error:
                QMessageBox.critical(self, "Error", f"An error occurred while deleting data: {str(error)}")
            finally:
                cursor.close()
                connection.close()


class EditDataDialog(QDialog):
    def __init__(self, id_value, parent=None):
        super().__init__(parent)

        self.id_value = id_value

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.teacher_label = QLabel("Teacher:")
        self.teacher_input = QLineEdit()

        self.subject_label = QLabel("Subject:")
        self.subject_input = QLineEdit()

        self.student_label = QLabel("Student:")
        self.student_input = QLineEdit()

        self.grade_label = QLabel("Grade:")
        self.grade_input = QLineEdit()

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addWidget(self.teacher_label)
        self.layout.addWidget(self.teacher_input)
        self.layout.addWidget(self.subject_label)
        self.layout.addWidget(self.subject_input)
        self.layout.addWidget(self.student_label)
        self.layout.addWidget(self.student_input)
        self.layout.addWidget(self.grade_label)
        self.layout.addWidget(self.grade_input)
        self.layout.addWidget(self.button_box)

        self.setWindowTitle("Edit Data")

        self.load_data()

    def load_data(self):
        try:
            connection = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="",
                database="journal"
            )
            cursor = connection.cursor()

            query = ("SELECT teachers.teacher_name, subjects.subject_name, students.student_name, grades.grade "
                     "FROM grades "
                     "JOIN teachers ON grades.teacher_id = teachers.teacher_id "
                     "JOIN subjects ON grades.subject_id = subjects.subject_id "
                     "JOIN students ON grades.student_id = students.student_id "
                     "WHERE grades.id = %s")
            cursor.execute(query, (self.id_value,))
            data = cursor.fetchone()

            if data:
                self.teacher_input.setText(data[0])
                self.subject_input.setText(data[1])
                self.student_input.setText(data[2])
                self.grade_input.setText(str(data[3]))
        except mysql.connector.Error as error:
            QMessageBox.critical(self, "Error", f"An error occurred while loading data: {str(error)}")
        finally:
            cursor.close()
            connection.close()

    def get_edited_data(self):
        teacher = self.teacher_input.text()
        subject = self.subject_input.text()
        student = self.student_input.text()
        grade = self.grade_input.text()

        return teacher, subject, student, grade


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Journal")
        self.setGeometry(200, 200, 800, 600)

        self.tabs = QTabWidget()
        self.add_data_tab = AddDataTab()
        self.display_data_tab = DisplayDataTab()
        self.tabs.addTab(self.add_data_tab, "Add Data")
        self.tabs.addTab(self.display_data_tab, "Display Data")

        self.setCentralWidget(self.tabs)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
