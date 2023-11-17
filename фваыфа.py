from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QPolygon
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from UI import Ui_MainWindow

from sys import argv, exit
from random import randint


class Suprematism(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.click)

    def draw(self):
        self.repaint()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setBrush(QColor(randint(0, 250), randint(0, 250), randint(0, 250)))

        leigt = randint(1, 20)
        qp.drawEllipse(QPoint(50, 50), leigt, leigt)
        qp.end()

    def click(self):
        self.draw()


app = QApplication(argv)
ex = Suprematism()
ex.show()
exit(app.exec())
