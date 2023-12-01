import sqlite3
import sys
from Planner_ui import Ui_MainWindow
from add_or_change_tasks_ui import Ui_MainWindow1
from categories_ui import Ui_MainWindow2
from random import randint, choice
from datetime import date, datetime
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QInputDialog, QCheckBox, QColorDialog, QMainWindow, QTableWidgetItem, \
    QMessageBox

NAMES_COLUMNS = ['Id', '✓', 'Задача', 'Дата', 'Время', 'Категория', 'Заметки',
                 'Приоритет']  # Названия колонок таблиц с задачами
SOOT = {'Id': 'task_id', '✓': 'is_checked', 'Задача': 'name', 'Дата': 'date', 'Время': 'time',
        'Категория': 'category_id', 'Заметки': 'notes',
        'Приоритет': 'priority'}  # Соответствие названий колонок с названиями в базе данных


class Planner(QMainWindow, Ui_MainWindow):  # Основной класс, отвечает за главное окно
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connection = sqlite3.connect('Database_planner.sqlite')  # Подключение к базе данных
        self.initUI()

    def initUI(self):
        self.label_tasks_after_srok.setText(f'Просроченные задачи к {self.date_today()}')
        # Подключение кнопок
        self.calendar.selectionChanged.connect(self.calendar_changed)
        self.add_tasks_date.clicked.connect(self.add_or_change_task)
        self.add_tasks_all.clicked.connect(self.add_or_change_task)
        self.change_tasks_date.clicked.connect(self.add_or_change_task)
        self.change_tasks_after_srok.clicked.connect(self.add_or_change_task)
        self.save_tasks_date.clicked.connect(self.save_usual_for_save_all)
        self.save_tasks_after_srok.clicked.connect(self.save_prosrok_for_save_all)
        self.save_tasks_all.clicked.connect(self.save_all_for_save_all)
        self.delete_tasks_date.clicked.connect(self.delete_usual_for_delete_all)
        self.delete_tasks_after_srok.clicked.connect(self.delete_prosrok_for_delete_all)
        self.delete_tasks_all.clicked.connect(self.delete_all_for_delete_all)
        self.sort_tasks_all.clicked.connect(self.sortirovka)
        self.save_notes.clicked.connect(self.save_notes_to_data)
        self.save_quotes.clicked.connect(self.save_quotes_to_data)
        self.save_goals.clicked.connect(self.save_goals_to_data)
        self.change_category.clicked.connect(self.add_or_change_category)
        self.add_category.clicked.connect(self.add_or_change_category)
        self.delete_category.clicked.connect(self.delete_category_from_data)
        self.Planner_tab.currentChanged.connect(self.quotes)
        # При открытии приложения
        self.selects()
        self.select_data_category()
        self.calendar_changed()
        self.combo_sort()
        self.set_notes()
        self.set_goals()
        self.quotes()
        self.set_quotes()

    # Методы для отображения цитат, заметок, целей (следующие 4)

    def save_quotes_to_data(self):  # Для цитат
        self.save_for_quotes_notes_goals(self.text_quotes, 'quote', 'Quotes')

    def save_notes_to_data(self):  # Для заметок
        self.save_for_quotes_notes_goals(self.text_notes, 'note', 'OtherNotes')

    def save_goals_to_data(self):  # Для целей
        self.save_for_quotes_notes_goals(self.text_goals, 'goal', 'Goals')

    def save_for_quotes_notes_goals(self, pole, elem_in_data, data):  # Сохраняем заметки/цитаты/цели в базу данных
        one = pole.toPlainText().split('\n')
        all_ones = list(self.connection.cursor().execute(
            f"""SELECT {elem_in_data}, id From {data}""").fetchall())  # Выбираем все нужные данные
        names = [a[0] for a in all_ones]
        for elem in one:
            if elem not in names:  # Если записи нет в базе данных, добавить ее
                self.connection.cursor().execute(f"""INSERT INTO {data} ({elem_in_data})
                VALUES (?);""", (elem,))
        for elem in all_ones:  # Проверка на удаленные
            if elem[0] not in one:
                self.connection.cursor().execute(f"""DELETE FROM {data} WHERE id=({elem[1]});""")
        self.connection.commit()

    # Методы для отображения цитат, заметок, целей (следующие 4)

    def set_quotes(self):  # Для цитат
        self.set_for_quotes_notes_goals(self.text_quotes, 'quote', 'Quotes')

    def set_notes(self):  # Для заметок
        self.set_for_quotes_notes_goals(self.text_notes, 'note', 'OtherNotes')

    def set_goals(self):  # Для целей
        self.set_for_quotes_notes_goals(self.text_goals, 'goal', 'Goals')

    def set_for_quotes_notes_goals(self, pole, elem_in_data, data):  # Отображаем в pole заметки/цитаты/цели
        zn = [a[0] for a in
              list(self.connection.cursor().execute(
                  f"""SELECT {elem_in_data} FROM {data} ORDER BY id"""))]  # Выбираем нужные данные
        pole.setText('\n'.join(zn))
        self.connection.commit()

    def quotes(self):  # Отображение цитат в self.label_quote
        self.statusbar.showMessage('')
        quote = choice(list(self.connection.cursor().execute("""SELECT quote FROM Quotes""")))[0]
        self.label_quote.setText(quote)

    # Методы для сортировки таблицы (следующие 3)        

    def sortirovka(self):  # Выбор сортировки
        zn = self.choice_sort_tasks_all.currentText()
        if zn in ['✓', 'Приоритет']:
            self.yes_or_not_dialog(zn)
        elif zn in ['Дата', 'Категория']:
            self.choice_dialog(zn)
        else:
            for_sorted = lambda x: (x[NAMES_COLUMNS.index(zn)], -x[-1], x[1])  # Сортировка по алфавиту/числам
            self.preporation_all_for_select_data(for_sort=for_sorted)

    def choice_dialog(self, text):  # Сортировка по нескольким значениям
        if text == 'Дата':
            all_texts = self.connection.cursor().execute(
                """SELECT DISTINCT date from Tasks""").fetchall()  # Выбираем нужные данные
            f = 0
        else:
            all_texts = self.connection.cursor().execute(
                """SELECT name from Categories""").fetchall()  # Выбираем нужные данные
            f = 1
        all_texts = ['Все'] + [elem[0] for elem in all_texts]
        ask, ok_pressed = QInputDialog.getItem(self, text, "Выберите один из вариантов", (all_texts), 0,
                                               False)  # Открываем диалоговое окно
        if ok_pressed:
            if ask == 'Все':  # Выводим все в определенном порядке
                for_sorted = lambda x: (x[NAMES_COLUMNS.index(text)], -x[-1], x[1])
                self.preporation_all_for_select_data(for_sort=for_sorted)
            elif f == 0:
                condit = f"WHERE {SOOT[text]} = '{ask}'"
                self.preporation_all_for_select_data(condition=condit)
            else:
                ask = self.connection.cursor().execute(
                    f"""SELECT category_id from Categories WHERE Name = '{ask}'""").fetchone()  # Ищем category_id
                condit = f"WHERE {SOOT[text]} = '{ask[0]}'"
                self.preporation_all_for_select_data(condition=condit)
        self.connection.commit()

    def yes_or_not_dialog(self, text):  # Сортировка по трем значениям
        ask, ok_pressed = QInputDialog.getItem(self, text, "Выберите один из вариантов", ("Все", "Да", "Нет"), 0,
                                               False)  # Открываем диалоговое окно
        if ok_pressed:
            if ask == 'Все':
                if text == '✓':
                    for_sorted = lambda x: (x[1], -x[-1])  # Сортировка по сделанным/несделанным
                else:
                    for_sorted = lambda x: (-x[-1], x[1])  # Сортировка по приоритету
                self.preporation_all_for_select_data(for_sort=for_sorted)
            else:
                if ask == 'Да':
                    if text == '✓':
                        number = 2  # Чтобы QCheckBox был с галочкой
                    else:
                        number = 1
                else:
                    number = 0
                condit = f"WHERE {SOOT[text]} = {number}"
                self.preporation_all_for_select_data(condition=condit)

    def calendar_changed(self):  # Реакция на изменение даты в self.calendar
        self.label_tasks_date.setText(f'Задачи на {str(self.calendar.selectedDate().toString("dd-MM-yyyy"))}')
        self.preporation_usual_for_select_data()

    def date_today(self):  # Сегодняшняя дата
        return date.today().strftime("%d-%m-%Y")

    # Методы для отображения таблиц (следующие 6)

    def preporation_usual_for_select_data(self):  # Для таблицы table_tasks_date
        data = self.calendar.selectedDate().toString("dd-MM-yyyy")
        condition = f"WHERE date = '{data}'"  # Условие для отображения задач
        for_sort = lambda x: (x[1], -x[-1], x[4])  # Как сортировать
        unvisible = [0, 3, 7]  # Номера невидимых столбцов
        self.select_data_all(self.table_tasks_date, condition, for_sort, unvisible)
        self.progress()  # Прогресс для таблицы table_tasks_date

    def preporation_prosrok_for_select_data(self):  # Для таблицы table_tasks_after_srok
        data = self.date_today()
        condition = f"WHERE date < '{data}' AND is_checked = 0"
        for_sort = lambda x: (x[1])
        unvisible = [0, 3, 4, 7]
        self.select_data_all(self.table_tasks_after_srok, condition, for_sort, unvisible)

    def preporation_all_for_select_data(self, condition='',
                                        for_sort=lambda x: (-x[0], -x[-1], x[1])):  # Для таблицы table_tasks_all
        unvisible = [0]
        self.select_data_all(self.table_tasks_all, condition, for_sort, unvisible)

    def select_data_all(self, table, condition, for_sort, unvisible):  # Отображение таблиц задач
        self.statusbar.showMessage('')
        res = self.connection.cursor().execute(
            f'SELECT * FROM Tasks {condition}').fetchall()  # Выбираем подходящие задачи
        res = sorted(res, key=for_sort)
        table.setColumnCount(8)
        table.setRowCount(0)
        table.setHorizontalHeaderLabels(NAMES_COLUMNS)
        # Выводим данные в формате таблицы
        for i, row in enumerate(res):
            table.setRowCount(
                table.rowCount() + 1)
            for j, elem in enumerate(row):
                if j == 1:
                    check = QCheckBox(self)
                    check.setCheckState(elem)
                    table.setCellWidget(i, j, check)
                elif j == 5:
                    cat = self.connection.cursor().execute(
                        f"""SELECT name, color from Categories WHERE category_id = {elem}""").fetchone()
                    color = cat[1]
                    table.setItem(i, j, QTableWidgetItem(cat[0]))
                else:
                    if elem is None:
                        elem = ''
                    table.setItem(i, j, QTableWidgetItem(str(elem)))
            self.color_row(table, i, QColor(color))  # Красим строку в цвет категории
        for column in unvisible:  # Прячем столбцы
            table.setColumnHidden(column, True)
        table.resizeColumnsToContents()
        self.connection.commit()

    def color_row(self, table, row, color):  # Красим row в color
        for i in range(table.columnCount()):
            item = table.item(row, i)
            if not (item is None):
                item.setBackground(color)

    def select_data_category(self):  # Отображение таблиц категорий
        self.statusbar.showMessage('')
        res = self.connection.cursor().execute(
            f'SELECT * FROM Categories').fetchall()  # Выбираем всю информацию о категориях
        self.table_categories.setColumnCount(3)
        self.table_categories.setRowCount(0)
        self.table_categories.setHorizontalHeaderLabels(['Номер', 'Название', 'Цвет'])
        # Выводим данные в формате таблицы
        for i, row in enumerate(res):
            self.table_categories.setRowCount(
                self.table_categories.rowCount() + 1)
            for j, elem in enumerate(row):
                if j == 2:
                    color = self.connection.cursor().execute(
                        f"""SELECT color from Categories WHERE category_id = {row[0]}""").fetchone()
                    self.table_categories.setItem(i, j, QTableWidgetItem(''))
                    self.table_categories.item(i, 2).setBackground(QColor(color[0]))
                else:
                    self.table_categories.setItem(i, j, QTableWidgetItem(str(elem)))
        self.table_categories.setColumnHidden(0, True)  # Прячем столбец
        self.table_categories.resizeColumnsToContents()
        self.connection.commit()

    def selects(self):  # Обновление таблиц
        self.preporation_prosrok_for_select_data()
        self.preporation_usual_for_select_data()
        self.preporation_all_for_select_data()

    # Методы для удаления задач в таблицах (следующие 6)

    def delete_usual_for_delete_all(self):  # Для таблицы table_tasks_date
        self.for_delete_all(self.table_tasks_date)

    def delete_prosrok_for_delete_all(self):  # Для таблицы table_tasks_after_srok
        self.for_delete_all(self.table_tasks_after_srok)

    def delete_all_for_delete_all(self):  # Для таблицы table_tasks_all
        self.for_delete_all(self.table_tasks_all)

    def for_delete_all(self, table):  # Проверка выделенной строки в table и подготовка для self.delete_all(id_task)
        row = table.currentRow()
        if self.status_bar(row, 'задачу', 'удалить'):
            id_task = table.item(row, 0).text()
            self.delete_all(id_task)

    def delete_all(self, id_task):  # Удаление из таблиц с задачами
        if self.message_box_delete:
            query = f"""DELETE from Tasks WHERE task_id = {id_task};"""
            self.connection.cursor().execute(query)  # Удаление по id
            self.connection.commit()
            self.selects()

    def delete_category_from_data(self):  # Удаление из таблицы с категориями
        row = self.table_categories.currentRow()
        if row == 0:
            self.statusbar.showMessage(f'Эту категорию нельзя удалить!')  # Категорию "Без категории" удалить нельзя
        elif self.status_bar(row, 'задачу', 'удалить'):
            category_id = self.table_categories.item(row, 0).text()
            if self.message_box_delete:  # Подтверждение удаления
                self.connection.cursor().execute(f"""UPDATE Tasks 
                SET category_id = 1
                WHERE category_id = {category_id};""")  # Меняем все задачи с category_id на "Без категории"
                query = f"""DELETE from categories WHERE category_id = {category_id};"""
                self.connection.cursor().execute(query)  # Удаляем категорию
                self.connection.commit()
                self.select_data_category()
                self.selects()

    # Методы для сохранения изменений в таблицах (следующие 4)

    def save_usual_for_save_all(self):  # Для таблицы table_tasks_date
        self.save_all(self.table_tasks_date)

    def save_prosrok_for_save_all(self):  # Для таблицы table_tasks_after_srok
        self.save_all(self.table_tasks_after_srok)

    def save_all_for_save_all(self):  # Для таблицы table_tasks_all
        self.save_all(self.table_tasks_all)

    def save_all(self, table):  # Сохранение изменений в таблице table (в предыдущих 3 методах)
        rows = table.rowCount()
        for i in range(rows):
            line = []
            for j in range(8):
                if j == 1:
                    line.append(table.cellWidget(i, 1).isChecked())
                else:
                    line.append(table.item(i, j).text())
            # В line все текущие значения
            if self.check(line[2], line[4], line[5], line[3], line[-1]):  # Проверка на соответствие формата
                if line[1] == True:
                    line[1] = 2  # Чтобы QCheckBox был с галочкой
                category_id = self.connection.cursor().execute(
                    f"""SELECT category_id from Categories WHERE name = '{line[5]}'""").fetchone()  # Ищем category_id
                query = f"""UPDATE Tasks 
                SET name = ?, category_id = ?, is_checked = ?, notes = ?, time = ?, priority = ?, date = ?
                WHERE task_id = {line[0]};"""
                sp = (line[2], category_id[0], line[1], line[6], line[4], line[-1], line[3])
                self.connection.cursor().execute(query, sp)  # Изменение данных в базе данных
            else:
                break  # Если не прошло проверки, ничего меняться не будет
        self.connection.commit()
        self.selects()  # Обновление отображающихся таблиц

    def status_bar(self, row, what, act):  # Cообщение об ошибки в self.statusbar
        if row != -1:  # Проверка на выделенную строку
            return True
        self.statusbar.showMessage(
            f'Выделите {what}, которую хотите {act}!')  # what = задачу/категорию, act = изменить/удалить
        return False

    def check_two(self, task, time):  # Проверка на соответствие формата task, time
        if task == '':
            return Exception('Введите задачу')  # Задача должна быть введена
        if time != '':
            if len(time) != 5 or time[2] != ':':  # Время должно иметь формат "часы:минуты"
                return Exception('Неверный формат времени')
            if not (int(time[:2]) <= 23 and int(time[:2]) >= 0):
                return Exception('Неверный указаны часы')
            if not (int(time[3:]) <= 59 and int(time[3:]) >= 0):
                return Exception('Неверный указаны минуты')
        return True

    def check(self, task, time, category, dates,
              priority):  # Проверка на соответствие формата task, time, category, dates, priority
        try:
            otvet = self.check_two(task, time)  # Проверка на соответствие формата task, time
            if type(otvet) == Exception:
                raise otvet
            cater = self.connection.cursor().execute(f"""SELECT name from Categories""").fetchall()
            all_cat = [x[0] for x in cater]
            if category not in all_cat:  # Проверка существует ли категория
                raise Exception('Нет данной категории')
            datetime.strptime(dates, '%d-%m-%Y')  # Проверка существует ли дата
            if not (priority == '0' or priority == '1'):
                raise Exception(
                    'Есть приоритет - 1, нет - 0')  # Проверка существует ли приоритет (у него только два значения)
            return True
        except ValueError:
            self.message_box('Неверный формат даты')
        except Exception as e:
            self.message_box(e)
        finally:
            self.connection.commit()

    def message_box_delete(self):  # Подтверждение удаления через QMessageBox 
        msg = QMessageBox()
        msg.setWindowTitle('Удаление')
        msg.setText('Вы уверенны?')
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = msg.exec_()
        return result == QMessageBox.Yes

    def message_box(self, mess):  # Сообщение об ошибке через QMessageBox с текстом mess
        msg = QMessageBox()
        msg.setWindowTitle('Ошибка')
        msg.setText(str(mess))
        msg.setIcon(QMessageBox.Warning)
        msg.exec_()

    def combo_sort(self):  # Критерии для сортировки в self.choice_sort_tasks_all
        self.choice_sort_tasks_all.addItems(NAMES_COLUMNS[1:])

    def progress(self):  # Изменение прогресса
        rows = self.table_tasks_date.rowCount()
        if rows != 0:
            count = 0
            for i in range(rows):  # Считается кол-во выполненных задач
                count += self.table_tasks_date.cellWidget(i, 1).isChecked()
            percent = int(count * 100 / rows)  # Кол-во выполненных задач / кол-во всех задач
        else:
            percent = 100  # Если задач нет, прогресс = 100 %
        self.progress_of_tasks_date.setValue(percent)  # Устанавливается значение на шкалу прогресса

    def add_or_change_task(self):  # Открытие окна, позволяющего добавить/изменить задачу
        self.statusbar.showMessage('')
        self.add_or_change_task_widget = AddOrChangeTask(self.sender(), self)
        if self.statusbar.currentMessage() == '':  # Проверка на ошибки
            self.add_or_change_task_widget.show()

    def add_or_change_category(self):  # Открытие окна, позволяющего добавить/изменить категорию
        self.statusbar.showMessage('')
        self.add_or_change_category_window = CategoryWindow(self.sender(), self)
        if self.statusbar.currentMessage() == '':  # Проверка на ошибки
            self.add_or_change_category_window.show()

    def closeEvent(self, event):
        self.connection.close()  # Pазрывает связь с базой данных при закрытии приложения


class AddOrChangeTask(QMainWindow, Ui_MainWindow1):
    def __init__(self, action, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.parent = parent  # Класс-родитель
        self.action = action  # Что делать? Изменить или добавить?
        self.setWindowTitle(self.action.text())
        self.combo()
        if self.action.text() == 'Изменить задачу':
            self.initUI_for_change()
        else:
            self.initUI_for_add()

    def initUI_for_add(self):  # initUI для добавления
        self.checkBox_task.setChecked(False)  # Задача изначально не сделана
        self.checkBox_task.hide()  # Прячем номер и сделана ли задача
        self.label_id_task.hide()
        self.label_number_task.hide()
        self.date_task.setDate(self.parent.calendar.selectedDate())
        self.save_task.clicked.connect(self.save_for_add)

    def initUI_for_change(self):  # initUI для изменения
        self.save_task.clicked.connect(self.save_for_change)
        if self.action == self.parent.change_tasks_date:  # Выбор таблицы, с которой работаем
            table = self.parent.table_tasks_date
        else:
            table = self.parent.table_tasks_after_srok
        row = table.currentRow()
        if self.parent.status_bar(row, 'задачу', 'изменить'):  # Проверка на выделенную строку
            # Устанавливаем данные в поля 
            self.label_id_task.setText(table.item(row, 0).text())
            query = """SELECT name, category_id, time, notes, priority, is_checked, date from Tasks Where task_id = ?;"""
            sp = (table.item(row, 0).text(),)
            info = self.parent.connection.cursor().execute(query, sp).fetchone()
            self.name_task.setText(info[0])
            date_obj = datetime.strptime(info[6], '%d-%m-%Y').date()
            self.date_task.setDate(date_obj)
            self.combo_categories_task.setCurrentText(self.parent.connection.cursor().execute(
                f"""SELECT name FROM Categories WHERE category_id = {info[1]}""").fetchone()[0])
            self.time_task.setText(info[2])
            self.text_notes_task.setPlainText(info[3])
            if info[4]:
                self.priorty_yes_task.setChecked(info[4])
            self.checkBox_task.setChecked(info[5])
        self.parent.connection.commit()

    def check(self):  # Проверка на соответствие формата
        try:
            otvet = self.parent.check_two(self.name_task.text(),
                                          self.time_task.text())  # Используем метод из родительского класса
            if type(otvet) == Exception:
                raise otvet
            return True
        except Exception as e:
            self.parent.message_box(e)
        finally:
            self.parent.connection.commit()

    # Методы для сохранения задачи (следующие 3)

    def save_for_add(self):  # Для добавления
        query = """INSERT INTO Tasks (name, category_id, is_checked, date, time, notes, priority) 
                           VALUES (?, ?, ?, ?, ?, ?, ?);"""
        self.save_all(query)

    def save_for_change(self):  # Для изменения
        query = f"""UPDATE Tasks 
        SET name = ?, category_id = ?, is_checked = ?, date = ?, time = ?, notes = ? , priority = ? 
        WHERE task_id = {self.label_id_task.text()};"""
        self.save_all(query)

    def save_all(self, query):  # Сохранение задачи в базу данных
        self.label_save.setText('')
        name = self.name_task.text()
        name_category = self.combo_categories_task.currentText()
        id_category = self.parent.connection.cursor().execute(f"""SELECT category_id FROM Categories WHERE name = ?""",
                                                              (name_category,)).fetchone()[0]
        data = self.date_task.date().toString('dd-MM-yyyy')
        notes = self.text_notes_task.toPlainText()
        time = self.time_task.text()
        notes = self.text_notes_task.toPlainText()
        radio = self.priorty_not_task.isChecked()
        checked = self.checkBox_task.isChecked()
        if radio:
            priorty = 0
        else:
            priorty = 1
        if checked:
            checked = 2
        if self.check():
            sp = (name, id_category, checked, data, time, notes, priorty)
            self.parent.connection.cursor().execute(query, sp)
            self.label_save.setText('Сохранено')
        self.parent.connection.commit()

    def combo(self):  # Установка категорий в self.combo_categories_task
        category_in_task = self.parent.connection.cursor().execute("""SELECT name FROM Categories""").fetchall()
        category_in_task = sorted(category_in_task, key=lambda x: x[0])
        for category in category_in_task:
            self.combo_categories_task.addItem(category[0])

    def closeEvent(self, event):
        self.parent.selects()
        self.parent.connection.close()  # Pазрывает связь с базой данных при закрытии окна
        self.close()


class CategoryWindow(QMainWindow, Ui_MainWindow2):
    def __init__(self, action, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.parent = parent  # Класс-родитель
        self.action = action  # Что делать? Изменить или добавить?
        self.setWindowTitle(self.action.text())
        self.parent.statusbar.showMessage('')
        self.choice_color.clicked.connect(self.run)
        self.random_color.clicked.connect(self.random_colorr)
        if self.action.text() == 'Изменить категорию':
            self.initUI_for_change()
        else:
            self.initUI_for_add()

    def initUI_for_add(self):  # initUI для добавления
        self.save_category.clicked.connect(self.save_for_add)

    def initUI_for_change(self):  # initUI для изменения
        row = self.parent.table_categories.currentRow()
        if self.parent.status_bar(row, 'категорию', 'изменить'):  # Проверка на выделенную строку
            # Устанавливаем данные в поля 
            self.text_name_category.setText(str(self.parent.table_categories.item(row, 1).text()))
            color = self.parent.connection.cursor().execute(
                f"""SELECT color from Categories WHERE category_id = {self.parent.table_categories.item(row, 0).text()}""").fetchone()
            self.set_color(color[0])
        self.save_category.clicked.connect(self.save_for_change)
        self.parent.connection.commit()

    def random_colorr(self):  # Рандомный выбор цвета
        r = randint(0, 255)
        g = randint(0, 255)
        b = randint(0, 255)
        color = '#%02X%02X%02X' % (r, g, b)
        self.set_color(color)

    def set_color(self, color):  # Установка color
        self.random_color.setStyleSheet(
            "background-color: {}".format(color))
        self.choice_color.setStyleSheet(
            "background-color: {}".format(color))

    def run(self):  # Открытие окна с цветами
        color = QColorDialog.getColor()
        if color.isValid():
            self.set_color(color.name())

    def check(self):  # Проверка на соответствие формата
        try:
            names = [a[0] for a in
                     self.parent.connection.cursor().execute(f"""SELECT name from Categories""").fetchall()]
            if self.text_name_category.text() == '':
                raise Exception('Введите название категории!')
            if self.text_name_category.text() in names and self.action.text() != 'Изменить категорию':
                raise Exception('Такая категория уже есть')  # Нельзя повторять названия категорий
            return True
        except Exception as e:
            self.statusbar.showMessage(str(e))

    # Методы для сохранения категории (следующие 3)

    def save_for_add(self):  # Для добавления
        query = """INSERT INTO Categories (name, color) 
                           VALUES (?, ?);"""
        self.save_all(query)

    def save_for_change(self):  # Для изменения
        row = self.parent.table_categories.currentRow()
        query = f"""UPDATE Categories 
        SET name = ?, color = ?
        WHERE category_id = {self.parent.table_categories.item(row, 0).text()};"""
        self.save_all(query)

    def save_all(self, query):  # Сохранение категории в базу данных
        self.label_save.setText('')
        self.statusbar.showMessage('')
        name = self.text_name_category.text()
        color = self.choice_color.palette().button().color()
        if self.check():
            sp = (name, str(color.name()),)
            self.parent.connection.cursor().execute(query, sp)
            self.label_save.setText('Сохранено!')
        self.parent.connection.commit()

    def closeEvent(self, event):
        self.parent.selects()
        self.parent.select_data_category()
        self.parent.connecion.close()  # Pазрывает связь с базой данных при закрытии окна
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Planner()
    ex.show()
    sys.exit(app.exec())
