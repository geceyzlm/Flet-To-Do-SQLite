import flet as ft
import sqlite3

class TodoApp(ft.Stack):
    def __init__(self):
        super().__init__()
        self.new_task = ft.TextField(hint_text="yaz..", expand=True)
        self.tasks = ft.Column()
        self.data = 0  # Her eklenen liste ve tuşlarına sayısal değer atıyoruz
        self.conn = sqlite3.connect("todo.db")  # SQLite veritabanına bağlanma
        self.cursor = self.conn.cursor()
        
        # Görevler tablosunu oluştur
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL
            )
        ''')
        self.conn.commit()

        self.controls = [
            ft.Column(
                width=600,
                controls=[
                    # 1
                    ft.Row(
                        controls=[
                            self.new_task,
                            ft.FloatingActionButton(icon=ft.icons.ADD, on_click=self.add_clicked),
                            ft.FloatingActionButton(icon="highlight_off", on_click=self.deleteall, bgcolor="#D55E27")
                        ],
                    ),
                    # 2
                    self.tasks
                ],
            )
        ]
        self.load_tasks()  # Veritabanından görevleri yükle ve ekrana yansıt

    def load_tasks(self):
        # Veritabanındaki tüm görevleri yükleyip ekrana ekle
        self.cursor.execute("SELECT * FROM tasks")
        for row in self.cursor.fetchall():
            task_id, task_text = row
            self.add_task_ui(task_text, task_id)

    def add_task_ui(self, task_text, task_id):
        # Bir görevi UI'ya ekler, task_id ile bağlantılı
        self.edt = ft.IconButton(icon=ft.icons.CREATE_OUTLINED, tooltip="Edit To-Do", data=task_id, on_click=self.edit)
        self.dlt = ft.IconButton(icon=ft.icons.DELETE_OUTLINE, tooltip="Delete To-Do", data=task_id, on_click=self.delete)
        self.lt = ft.ListTile(leading=self.edt, title=ft.Text(task_text), trailing=self.dlt, data=task_id)
        self.tasks.controls.append(self.lt)
        self.tasks.update()

    def add_clicked(self, e):
        task_text = self.new_task.value
        if task_text.strip():
            # Yeni görevi veritabanına ekle
            self.cursor.execute("INSERT INTO tasks (task) VALUES (?)", (task_text,))
            task_id = self.cursor.lastrowid
            self.conn.commit()

            # UI'ya ekle
            self.add_task_ui(task_text, task_id)
            self.new_task.value = ""  # TextField'ı sıfırla
            self.update()

    def deleteall(self, e):
        # Tüm görevleri veritabanından ve ekrandan sil
        self.cursor.execute("DELETE FROM tasks")
        self.conn.commit()

        self.tasks.controls.clear()  # UI'daki tüm görevleri temizle
        self.update()

    def delete(self, e):
        task_id = e.control.data
        # Veritabanından sil
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()

        # UI'dan sil
        for task in self.tasks.controls[:]:
            if task.data == task_id:
                self.tasks.controls.remove(task)
                self.update()

    def kapat(self, e):
        self.msj.open = False
        self.update()

    def save(self, e):
        task_id = e.control.data
        new_value = self.gncl.value

        # Veritabanında güncelle
        self.cursor.execute("UPDATE tasks SET task = ? WHERE id = ?", (new_value, task_id))
        self.conn.commit()

        # UI'da güncelle
        for task in self.tasks.controls[:]:
            if task.data == task_id:
                task.title = ft.Text(new_value)
                self.update()
        self.msj.open = False

    def edit(self, e):
        task_id = e.control.data

        self.gncl = ft.TextField(hint_text="yeni değer yaz", expand=True)
        self.msj = ft.AlertDialog(
            open=False, modal=True, title=ft.Text("Please confirm"),
            actions=[
                ft.TextButton("kaydet", on_click=self.save, data=task_id),
                ft.TextButton("kapat", on_click=self.kapat)
            ],
            content=self.gncl
        )

        self.tasks.controls.append(self.msj)
        self.msj.open = True
        self.update()


def main(page: ft.Page):
    page.title = "ToDo App"
    page.window.width = 600
    page.window.height = 700

    todo_app = TodoApp()

    page.add(todo_app)
    page.update()


ft.app(target=main)
