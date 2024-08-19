import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QCheckBox, QPushButton, QWidget, QLineEdit, \
    QListWidget, QListWidgetItem, QLabel, QMessageBox, QToolButton, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QIcon, QMouseEvent


class StickyNoteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sticky Note")
        self.setGeometry(100, 100, 400, 400)
        self.setStyleSheet("background-color: #2c2c2c; color: white;")
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.tasks = []
        self.is_pinned = False

        # Main layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        # Top bar layout for pin and close buttons
        self.top_bar_layout = QHBoxLayout()
        self.layout.addLayout(self.top_bar_layout)

        # Close button
        self.close_button = QToolButton(self)
        self.close_button.setIcon(QIcon('icons/close.png'))  # Ensure you have a 'close_icon.png' file or replace with a suitable path
        self.close_button.setToolTip("Close")
        self.close_button.clicked.connect(self.close)
        self.close_button.setStyleSheet("background-color: #444; border: none;")
        self.close_button.setFixedSize(30, 30)
        self.top_bar_layout.addWidget(self.close_button)

        # Pin button
        self.pin_button = QToolButton(self)
        self.pin_button.setIcon(
            QIcon('icons/pin.png'))  # Ensure you have a 'pin.png' file or replace with a suitable path
        self.pin_button.setToolTip("Pin to top")
        self.pin_button.clicked.connect(self.toggle_pin)
        self.pin_button.setStyleSheet("background-color: #444; border: none;")
        self.pin_button.setFixedSize(30, 30)
        self.top_bar_layout.addWidget(self.pin_button)

        self.top_bar_layout.addStretch()

        # Date and time display
        self.datetime_label = QLabel()
        self.datetime_label.setAlignment(Qt.AlignCenter)
        self.datetime_label.setStyleSheet("font-size: 18px; padding: 10px;")
        self.layout.addWidget(self.datetime_label)

        # Start the timer to update date and time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)  # Update every second

        # Task list
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("background-color: #3c3c3c; border: none;")
        self.layout.addWidget(self.task_list)

        # Add new task input
        self.new_task_input = QLineEdit()
        self.new_task_input.setPlaceholderText("Add a new task...")
        self.new_task_input.setStyleSheet("background-color: #444; color: white; padding: 5px;")
        self.layout.addWidget(self.new_task_input)

        # Add task button
        self.add_task_btn = QPushButton("Add Task")
        self.add_task_btn.setStyleSheet("background-color: #5c5c5c;")
        self.add_task_btn.clicked.connect(self.add_task)
        self.layout.addWidget(self.add_task_btn)

        # Delete task button
        self.delete_task_btn = QPushButton("Delete Selected Task")
        self.delete_task_btn.setStyleSheet("background-color: #5c5c5c;")
        self.delete_task_btn.clicked.connect(self.delete_task)
        self.layout.addWidget(self.delete_task_btn)

        # Save button
        self.save_btn = QPushButton("Save Tasks")
        self.save_btn.setStyleSheet("background-color: #5c5c5c;")
        self.save_btn.clicked.connect(self.save_tasks)
        self.layout.addWidget(self.save_btn)

        # Load tasks on startup
        self.load_tasks()

    def update_datetime(self):
        current_datetime = QDateTime.currentDateTime().toString("dddd, MMMM d yyyy - hh:mm:ss ap")
        self.datetime_label.setText(current_datetime)

    def add_task(self):
        task_text = self.new_task_input.text().strip()
        if task_text:
            checkbox = QCheckBox(task_text)
            checkbox.setStyleSheet("padding: 5px;")
            item = QListWidgetItem()
            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, checkbox)
            self.new_task_input.clear()
            self.tasks.append({'text': task_text, 'checked': False})

    def delete_task(self):
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Delete Task", "Please select a task to delete.")
            return

        for item in selected_items:
            row = self.task_list.row(item)
            self.task_list.takeItem(row)
            del self.tasks[row]

    def save_tasks(self):
        tasks_to_save = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            widget = self.task_list.itemWidget(item)
            task_text = widget.text()
            task_checked = widget.isChecked()
            tasks_to_save.append({'text': task_text, 'checked': task_checked})

        with open('tasks.json', 'w') as file:
            json.dump(tasks_to_save, file, indent=4)

        QMessageBox.information(self, "Saved", "Tasks have been saved successfully!")

    def load_tasks(self):
        try:
            with open('tasks.json', 'r') as file:
                self.tasks = json.load(file)

            for task in self.tasks:
                checkbox = QCheckBox(task['text'])
                checkbox.setChecked(task['checked'])
                checkbox.setStyleSheet("padding: 5px;")
                item = QListWidgetItem()
                self.task_list.addItem(item)
                self.task_list.setItemWidget(item, checkbox)
        except FileNotFoundError:
            pass

    def toggle_pin(self):
        if self.is_pinned:
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setWindowOpacity(1.0)  # Full opacity when unpinned
        else:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            self.setWindowOpacity(0.85)

        self.show()
        self.is_pinned = not self.is_pinned

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and not self.is_pinned:
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton and not self.is_pinned:
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = StickyNoteApp()
    main_window.show()
    sys.exit(app.exec_())