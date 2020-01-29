from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = QUiLoader().load("mainwindow.ui")
        self.ui.show()
        self.ui.setWindowTitle("RoboAide")
        self.setMinimumHeight(100)
        self.setMinimumWidth(250)
        # self.setMaximumHeight(200)
        # self.setMaximumWidth(800)
        self.setIcon()

        self.initializeSliderPositions()

        # Connect the slider signals
        self.ui.slider_mot1.valueChanged.connect(lambda: self.changeMotorPosition(self.ui.slider_mot1, 1))
        self.ui.slider_mot2.valueChanged.connect(lambda: self.changeMotorPosition(self.ui.slider_mot2, 2))
        self.ui.slider_mot3.valueChanged.connect(lambda: self.changeMotorPosition(self.ui.slider_mot3, 3))
        self.ui.slider_mot4.valueChanged.connect(lambda: self.changeMotorPosition(self.ui.slider_mot4, 4))
        self.ui.slider_mot5.valueChanged.connect(lambda: self.changeMotorPosition(self.ui.slider_mot5, 5))
        self.ui.slider_mot6.valueChanged.connect(lambda: self.changeMotorPosition(self.ui.slider_mot6, 6))

    def setIcon(self):
        appIcon = QIcon("icon.jpg")
        self.ui.setWindowIcon(appIcon)

    # Sets the slider position to the each motors initial position
    def initializeSliderPositions(self):
        # TODO: get the position value for each motor
        mot1 = 0
        mot2 = 0
        mot3 = 0
        mot4 = 0
        mot5 = 0
        mot6 = 0
        self.ui.slider_mot1.setValue(mot1)
        self.ui.slider_mot2.setValue(mot2)
        self.ui.slider_mot3.setValue(mot3)
        self.ui.slider_mot4.setValue(mot4)
        self.ui.slider_mot5.setValue(mot5)
        self.ui.slider_mot6.setValue(mot6)

    # Slot to change a motor's position when the slider's value is changed
    def changeMotorPosition(self, slider, num):
        value = slider.value()
        print("Motor #%d: %d" % (num, value))
        # TODO: make this into a sentence and send it to the controller


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec_()
    sys.exit()
