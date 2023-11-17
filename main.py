import sys
from PyQt6 import QtWidgets, QtCore, QtGui, uic
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel, QSqlRecord, QSqlQuery
import os


class FilterDialog(QtWidgets.QDialog):
    def __init__(self, headers):
        super().__init__()

        self.setWindowTitle("Filter Data")

        self.layout = QtWidgets.QVBoxLayout(self)

        self.header_list = QtWidgets.QComboBox()
        self.header_list.addItems(headers)
        self.layout.addWidget(self.header_list)

        self.value_input = QtWidgets.QLineEdit()
        self.layout.addWidget(self.value_input)

        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_values(self):
        return self.header_list.currentText(), self.value_input.text()


class DbViewer(QtWidgets.QMainWindow):
    def __init__(self, db):
        super().__init__()
        uic.loadUi('main.ui', self)

        self.db = db
        self.table_model = QSqlTableModel(db=self.db)
        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.table_model)

        query = QSqlQuery()
        query.exec('SELECT name FROM sqlite_master WHERE type="table"')
        self.tables = []
        self.next_index = 1
        while query.next():
            self.tables.append(query.value(0))

        # Создание модели файловой системы
        self.file_model = QtGui.QFileSystemModel()
        self.file_model.setRootPath(QtCore.QDir.rootPath())

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Database Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.initialize_db()
        self.tree_view = QtWidgets.QTreeView()

        self.tree_view.setModel(self.file_model)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.table_combo_box = QtWidgets.QComboBox()
        self.layout.addWidget(self.table_combo_box)


        self.table_combo_box.currentTextChanged.connect(self.update_table)

        # Add a toolbar with "Add", "Update", "Filter" and "Switch View" buttons
        toolbar = QtWidgets.QToolBar()
        self.addToolBar(toolbar)

        add_action = QtGui.QAction("Add", self)
        add_action.triggered.connect(self.add_user)
        toolbar.addAction(add_action)

        update_action = QtGui.QAction("Update", self)
        update_action.triggered.connect(self.update_user)
        toolbar.addAction(update_action)

        filter_action = QtGui.QAction("Filter", self)
        filter_action.triggered.connect(self.filter_data)
        toolbar.addAction(filter_action)

        switch_view_action = QtGui.QAction("Switch View", self)
        switch_view_action.triggered.connect(self.switch_view)
        toolbar.addAction(switch_view_action)

    def initialize_db(self):
        self.table_view = QtWidgets.QTableView()

        # Disable direct editing of the table
        self.table_view.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setCentralWidget(self.table_view)

        print(self.table_model.tableName())
        self.table_model.setTable(self.tables[self.next_index])
        self.table_model.select()
        self.table_view.setModel(self.proxy_model)

        # Enable sorting
        self.table_view.setSortingEnabled(True)

    def add_user(self):
        dialog = [self.table_model.headerData(i, QtCore.Qt.Orientation.Horizontal) for i in
                  range(self.table_model.columnCount())]
        print(dialog)
        query = QSqlQuery()
        query.exec(f'SELECT  FROM {self.tables[self.next_index]} WHERE type="table"')
        self.tables = []
        self.next_index = 1
        while query.next():
            self.tables.append(query.value(0))


        # Add a new record to the end of the model
        record = QSqlRecord()

        # Set default values for the new record here
        # For example:
        record.setValue("id", self.table_model.rowCount() + 1)
        data = []
        # For each column in the model, open an input dialog and add the input value to the record
        for i in range(1, self.table_model.columnCount()):
            input_dialog = QtWidgets.QInputDialog()
            input_dialog.setInputMode(QtWidgets.QInputDialog.InputMode.TextInput)
            input_dialog.setLabelText(dialog[i])
            ok = input_dialog.exec()
            if ok:
                value = input_dialog.textValue()
                data.append(value)
        print(data)

        print(self.table_model.insertRow(-1))

        print(self.table_model.insertRecord(-1, record))
        print(self.table_model.select())
        self.table_model.submitAll()

    def update_user(self):
        # Show an input dialog to get the user id
        id, ok = QtWidgets.QInputDialog.getInt(self, "Update User", "Enter id:")

        if ok and id != 0:
            index = None

            # Find the row with the given user id
            for row in range(self.proxy_model.rowCount()):
                index = self.proxy_model.index(row, 0)
                source_index = self.proxy_model.mapToSource(index)
                self.table_view.hideRow(index.row())
                record = self.table_model.record(source_index.row())
                if record.value("id") == id:
                    # Enable editing for this row
                    self.table_view.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.AllEditTriggers)
                    self.table_view.setCurrentIndex(index)
                    self.table_view.showRow(index.row())
        elif id == -1:
            self.table_view.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.AllEditTriggers)
        else:
            for row in range(self.proxy_model.rowCount()):
                self.table_view.showRow(row)
            # If the user id was not found, disable editing
            self.table_view.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
            self.table_model.submitAll()

    def filter_data(self):
        # Show a dialog to select the header and filter text
        dialog = FilterDialog([self.table_model.headerData(i, QtCore.Qt.Orientation.Horizontal) for i in
                               range(self.table_model.columnCount())])
        result = dialog.exec()
        print(result)
        if 1:  # result == QtWidgets.QDialog.accepted:
            header, filter_text = dialog.get_values()

            column_index = [self.table_model.headerData(i, QtCore.Qt.Orientation.Horizontal) for i in
                            range(self.table_model.columnCount())].index(header)
            if column_index >= 0:
                # Apply the filter to the proxy model
                self.proxy_model.setFilterKeyColumn(column_index)
                self.proxy_model.setFilterFixedString(filter_text)

    def switch_view(self):
        self.update_table()

    def update_table(self):
        self.next_index = (self.next_index + 1) % len(self.tables)
        table_name = self.tables[int(self.next_index)]
        self.table_model.setTable(table_name)
        self.table_model.select()


def main():
    app = QtWidgets.QApplication(sys.argv)

    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('coffee.sqlite')

    if not db.open():
        print(f"Cannot open database: {db.lastError().text()}")
        return

    viewer = DbViewer(db)
    viewer.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
