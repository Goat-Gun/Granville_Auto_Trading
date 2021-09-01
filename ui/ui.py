import sys

from kiwoom.kiwoom import *
from PyQt5.QtWidgets import *
class Ui_class():
    def __init__(self):
        print("Ui_class입니다")

        self.app = QApplication(sys.argv)

        self.kiwoom = Kiwoom()

        self.app.exec_()

