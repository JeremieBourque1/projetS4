from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtGui import QIcon
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setMinimumHeight(100)
        self.setMinimumWidth(250)
        # self.setMaximumHeight(200)
        # self.setMaximumWidth(800)
        self.setIcon()

    def setIcon(self):
        appIcon = QIcon("icon.jpg")
        self.setWindowIcon(appIcon)



if __name__ == "__main__":
    app = QApplication(sys.argv)

    ui_file = QFile("mainwindow.ui")
    ui_file.open(QFile.ReadOnly)

    window = MainWindow()
    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()
    window.show()


    sys.exit(app.exec_())
