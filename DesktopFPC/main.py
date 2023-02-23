from PyQt5 import QtWidgets
from GUI import exam
import sys
from Containers import *


class Window(QtWidgets.QMainWindow, exam.Ui_exam_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.start_ex.clicked.connect(self.start_exam)
        self.over_ex.clicked.connect(self.over_exam)

    def start_exam(self):
        inside_start(int(self.lineEdit.text()))

    def over_exam(self):
        exit_exam()
        sys.exit()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
