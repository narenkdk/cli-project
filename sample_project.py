import sys
import sqlite3
import json
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QLineEdit,
    QMessageBox,
    QFileDialog,
)
from PyQt5.QtCore import Qt


class TodoList:
    def __init__(self, db_name="todo_list.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            completed BOOLEAN NOT NULL CHECK (completed IN (0, 1))
        )
        """
        )
        self.conn.commit()

    def add_task(self, description):
        self.cursor.execute(
            "INSERT INTO tasks (description, completed) VALUES (?, ?)",
            (description, False),
        )
        self.conn.commit()

    def remove_task(self, task_id):
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()

    def mark_task_completed(self, task_id):
        self.cursor.execute(
            "UPDATE tasks SET completed = ? WHERE id = ?", (True, task_id)
        )
        self.conn.commit()

    def update_task_description(self, task_id, new_description):
        self.cursor.execute(
            "UPDATE tasks SET description = ? WHERE id = ?", (new_description, task_id)
        )
        self.conn.commit()

    def list_tasks(self):
        self.cursor.execute("SELECT * FROM tasks")
        return self.cursor.fetchall()

    def import_tasks_from_json(self, file_path):
        with open(file_path, "r") as file:
            tasks = json.load(file)
            for task in tasks:
                self.add_task(task["description"])
                if task["completed"]:
                    self.mark_task_completed(self.cursor.lastrowid)


class TodoListApp(QWidget):
    def __init__(self):
        super().__init__()
        self.todo_list = TodoList()  # Initialize todo_list before calling initUI
        self.initUI()

    def initUI(self):
        self.setWindowTitle("To-Do List Application")

        self.layout = QVBoxLayout()

        self.task_list = QListWidget()
        self.layout.addWidget(self.task_list)

        self.task_input = QLineEdit(self)
        self.task_input.setPlaceholderText("Enter a new task")
        self.layout.addWidget(self.task_input)

        self.button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Task", self)
        self.add_button.clicked.connect(self.add_task)
        self.button_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Remove Task", self)
        self.remove_button.clicked.connect(self.remove_task)
        self.button_layout.addWidget(self.remove_button)

        self.complete_button = QPushButton("Mark Completed", self)
        self.complete_button.clicked.connect(self.mark_task_completed)
        self.button_layout.addWidget(self.complete_button)

        self.update_button = QPushButton("Update Description", self)
        self.update_button.clicked.connect(self.update_task_description)
        self.button_layout.addWidget(self.update_button)

        self.import_button = QPushButton("Import from JSON", self)
        self.import_button.clicked.connect(self.import_tasks_from_json)
        self.button_layout.addWidget(self.import_button)

        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)
        self.refresh_list()

    def add_task(self):
        description = self.task_input.text()
        if description:
            self.todo_list.add_task(description)
            self.task_input.clear()
            self.refresh_list()
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a task description.")

    def remove_task(self):
        selected_task = self.task_list.currentRow()
        if selected_task >= 0:
            task_id = self.task_list.item(selected_task).data(Qt.UserRole)
            self.todo_list.remove_task(task_id)
            self.refresh_list()
        else:
            QMessageBox.warning(
                self, "Selection Error", "Please select a task to remove."
            )

    def mark_task_completed(self):
        selected_task = self.task_list.currentRow()
        if selected_task >= 0:
            task_id = self.task_list.item(selected_task).data(Qt.UserRole)
            self.todo_list.mark_task_completed(task_id)
            self.refresh_list()
        else:
            QMessageBox.warning(
                self, "Selection Error", "Please select a task to mark as completed."
            )

    def update_task_description(self):
        selected_task = self.task_list.currentRow()
        new_description = self.task_input.text()
        if selected_task >= 0 and new_description:
            task_id = self.task_list.item(selected_task).data(Qt.UserRole)
            self.todo_list.update_task_description(task_id, new_description)
            self.task_input.clear()
            self.refresh_list()
        else:
            if selected_task < 0:
                QMessageBox.warning(
                    self, "Selection Error", "Please select a task to update."
                )
            if not new_description:
                QMessageBox.warning(
                    self, "Input Error", "Please enter a new task description."
                )

    def import_tasks_from_json(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open JSON File", "", "JSON Files (*.json)"
        )
        if file_path:
            self.todo_list.import_tasks_from_json(file_path)
            self.refresh_list()
        else:
            QMessageBox.warning(self, "File Error", "Please select a JSON file.")

    def refresh_list(self):
        self.task_list.clear()
        tasks = self.todo_list.list_tasks()
        for task in tasks:
            item = f"{task[1]} - {'Completed' if task[2] else 'Pending'}"
            list_item = self.task_list.addItem(item)
            self.task_list.item(self.task_list.count() - 1).setData(
                Qt.UserRole, task[0]
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = TodoListApp()
    ex.show()
    sys.exit(app.exec_())