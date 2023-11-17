from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QPolygon
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog

from sys import argv, exit
from random import randint


class Suprematism(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI.ui', self)
        self.pushButton.clicked.connect(self.click)

    def draw(self):
        self.repaint()

    def paintEvent(self, event):
        print(1)
        qp = QPainter()
        qp.begin(self)
        qp.setBrush(QColor('yellow'))

        leigt = randint(1, 20)
        qp.drawEllipse(QPoint(50, 50), leigt, leigt)
        qp.end()

    def click(self):
        self.draw()


app = QApplication(argv)
ex = Suprematism()
ex.show()
exit(app.exec())
