"""
Task Manager with GUI using Kivy / Python
Features:
- Add, edit, delete tasks
- Mark tasks complete/incomplete
- Save/load tasks to JSON (tasks.json)
- Task categories added
- Uses RecycleView for task list
- Single-file app (kv language embedded)

Run: pip install kivy  
Then: python kivy_task_manager.py

"""
import json
import os
from datetime import datetime
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.core.window import Window

Window.size = (640, 500)

KV = r'''
#:import dp kivy.metrics.dp

<TaskRow>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(56)
    padding: dp(8)
    spacing: dp(8)

    CheckBox:
        id: checkbox
        size_hint_x: None
        width: dp(40)
        active: root.completed
        on_active: root.on_toggle_complete(self.active)

    Label:
        id: title
        markup: True
        text: ('[s]' + root.title + '[/s]') if root.completed else root.title
        halign: 'left'
        valign: 'middle'
        text_size: self.size
        shorten: True
        color: (0.5,0.5,0.5,1) if root.completed else (1,1,1,1)

    Label:
        id: category
        text: root.category
        size_hint_x: None
        width: dp(100)
        halign: 'center'
        valign: 'middle'
        text_size: self.size
        color: (0.7,0.7,0.7,1)

    Label:
        id: due
        text: root.due
        size_hint_x: None
        width: dp(120)
        halign: 'right'
        valign: 'middle'
        text_size: self.size
        color: (0.6,0.6,0.6,1)

    BoxLayout:
        size_hint_x: None
        width: dp(120)
        spacing: dp(4)
        Button:
            text: 'Edit'
            on_release: app.open_edit_task(root.index)
        Button:
            text: 'Delete'
            on_release: app.confirm_delete(root.index)

<MainScreen>:
    orientation: 'vertical'
    padding: dp(8)
    spacing: dp(8)

    BoxLayout:
        size_hint_y: None
        height: dp(48)
        spacing: dp(8)

        Label:
            text: 'Task Manager'
            font_size: '18sp'
            halign: 'left'
            valign: 'middle'
            text_size: self.size

        Button:
            text: 'Add Task'
            size_hint_x: None
            width: dp(120)
            on_release: app.open_add_task()

    RecycleView:
        id: rv
        viewclass: 'TaskRow'
        data: root.rv_data
        RecycleBoxLayout:
            default_size: None, dp(56)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'

    BoxLayout:
        size_hint_y: None
        height: dp(36)
        spacing: dp(8)
        Label:
            text: root.status_text
            halign: 'left'
            valign: 'middle'
            text_size: self.size
        Button:
            text: 'Save Now'
            size_hint_x: None
            width: dp(120)
            on_release: app.save_tasks(); app.show_save_confirmation()

<AddEditPopup>:
    title: root.window_title
    size_hint: 0.9, 0.7
    auto_dismiss: False
    BoxLayout:
        orientation: 'vertical'
        padding: dp(12)
        spacing: dp(8)
        BoxLayout:
            orientation: 'vertical'
            spacing: dp(6)
            Label:
                text: 'Title:'
                size_hint_y: None
                height: dp(20)
            TextInput:
                id: inp_title
                text: root.title_text
                multiline: False
                size_hint_y: None
                height: dp(40)

            Label:
                text: 'Category:'
                size_hint_y: None
                height: dp(20)
            TextInput:
                id: inp_category
                text: root.category_text
                multiline: False
                size_hint_y: None
                height: dp(40)

            Label:
                text: 'Description (optional):'
                size_hint_y: None
                height: dp(20)
            TextInput:
                id: inp_desc
                text: root.desc_text
                multiline: True
                size_hint_y: None
                height: dp(100)

            Label:
                text: 'Due date (YYYY-MM-DD) (optional):'
                size_hint_y: None
                height: dp(20)
            TextInput:
                id: inp_due
                text: root.due_text
                multiline: False
                size_hint_y: None
                height: dp(40)

        BoxLayout:
            size_hint_y: None
            height: dp(42)
            spacing: dp(8)
            Button:
                text: 'Cancel'
                on_release: root.dismiss()
            Button:
                text: 'Save'
                on_release: root.on_save(inp_title.text, inp_category.text, inp_desc.text, inp_due.text)
'''

class TaskRow(RecycleDataViewBehavior, BoxLayout):
    title = StringProperty('')
    desc = StringProperty('')
    due = StringProperty('')
    category = StringProperty('')
    completed = BooleanProperty(False)
    index = NumericProperty(0)

    def refresh_view_attrs(self, rv, index, data):
        self.index = data.get('index', 0)
        self.category = data.get('category', '')
        return super().refresh_view_attrs(rv, index, data)

    def on_toggle_complete(self, active):
        app = App.get_running_app()
        app.toggle_task_complete(self.index, active)

class AddEditPopup(Popup):
    window_title = StringProperty('Add Task')
    title_text = StringProperty('')
    desc_text = StringProperty('')
    due_text = StringProperty('')
    category_text = StringProperty('')
    edit_index = NumericProperty(-1)

    def on_save(self, title, category, desc, due):
        app = App.get_running_app()
        title = title.strip()
        category = category.strip()
        due = due.strip()
        if not title:
            from kivy.uix.label import Label
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.button import Button
            w = Popup(title='Validation', size_hint=(0.6, 0.3))
            box = BoxLayout(orientation='vertical', padding=8)
            box.add_widget(Label(text='Title cannot be empty'))
            btn = Button(text='OK', size_hint_y=None, height=40)
            box.add_widget(btn)
            w.add_widget(box)
            btn.bind(on_release=w.dismiss)
            w.open()
            return
        if self.edit_index >= 0:
            app.save_edited_task(self.edit_index, title, desc, due, category)
        else:
            app.add_task(title, desc, due, category)
        self.dismiss()

class MainScreen(BoxLayout):
    rv_data = ListProperty([])
    status_text = StringProperty('')

class TaskManagerApp(App):
    data_file = 'tasks.json'

    def build(self):
        self.title = 'Task Manager with GUI Kivy/Python'
        Builder.load_string(KV)
        self.root = MainScreen()
        self.tasks = []
        self.load_tasks()
        self.refresh_view()
        return self.root

    def load_tasks(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
            except Exception as e:
                print('Failed to load tasks:', e)
                self.tasks = []
        else:
            self.tasks = []

    def save_tasks(self, *args):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, indent=2, ensure_ascii=False)
            self.root.status_text = f'Saved {len(self.tasks)} tasks at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        except Exception as e:
            self.root.status_text = f'Error saving: {e}'

    def show_save_confirmation(self):
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        p = Popup(title='Save Confirmation', size_hint=(0.6,0.3))
        p.add_widget(Label(text='Tasks have been saved successfully.'))
        p.open()

    def refresh_view(self):
        data = []
        for idx, t in enumerate(self.tasks):
            due = t.get('due', '') or ''
            category = t.get('category','')
            data.append({
                'title': t.get('title', ''),
                'desc': t.get('desc', ''),
                'due': due,
                'category': category,
                'completed': t.get('completed', False),
                'index': idx,
            })
        self.root.rv_data = data
        self.root.status_text = f'{len(self.tasks)} tasks loaded'

    def open_add_task(self):
        p = AddEditPopup()
        p.window_title = 'Add Task'
        p.edit_index = -1
        p.open()

    def open_edit_task(self, index):
        if 0 <= index < len(self.tasks):
            t = self.tasks[index]
            p = AddEditPopup()
            p.window_title = 'Edit Task'
            p.title_text = t.get('title', '')
            p.desc_text = t.get('desc', '')
            p.due_text = t.get('due', '')
            p.category_text = t.get('category','')
            p.edit_index = index
            p.open()

    def add_task(self, title, desc, due, category):
        self.tasks.append({'title': title, 'desc': desc, 'due': due, 'category': category, 'completed': False})
        self.refresh_view()
        self.save_tasks()

    def save_edited_task(self, index, title, desc, due, category):
        if 0 <= index < len(self.tasks):
            self.tasks[index].update({'title': title, 'desc': desc, 'due': due, 'category': category})
            self.refresh_view()
            self.save_tasks()

    def confirm_delete(self, index):
        if 0 <= index < len(self.tasks):
            def do_delete(instance=None):
                self.delete_task(index)
                popup.dismiss()

            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.label import Label
            from kivy.uix.button import Button
            popup = Popup(title='Confirm Delete', size_hint=(0.8, 0.4), auto_dismiss=False)
            box = BoxLayout(orientation='vertical', padding=12, spacing=8)
            box.add_widget(Label(text=f"Delete task: {self.tasks[index].get('title','')}?"))
            btns = BoxLayout(size_hint_y=None, height=40, spacing=8)
            b1 = Button(text='Cancel')
            b2 = Button(text='Delete')
            btns.add_widget(b1)
            btns.add_widget(b2)
            box.add_widget(btns)
            popup.add_widget(box)
            b1.bind(on_release=popup.dismiss)
            b2.bind(on_release=do_delete)
            popup.open()

    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks.pop(index)
            self.refresh_view()
            self.save_tasks()

    def toggle_task_complete(self, index, completed):
        if 0 <= index < len(self.tasks):
            self.tasks[index]['completed'] = bool(completed)
            self.refresh_view()
            self.save_tasks()

    def on_stop(self):
        self.save_tasks()


if __name__ == '__main__':
    TaskManagerApp().run()