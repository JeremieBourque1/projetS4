# Description: GUI application for the control of the robotic arm
#
# Authors: Jeremie Bourque <Jeremie.Bourque@USherbrooke.ca>
#          Jacob Kealey <Jacob.Kealey@USherbrooke.ca>
#
# Date created: 22-01-2020


from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QMenu, QListWidgetItem
from PySide2.QtGui import QIcon
from PySide2.QtCore import QRect
from PySide2.QtUiTools import QUiLoader
import sys


class ListOfSequencesHandler:
    def __init__(self, ui):
        self.mListOfSequences = ui.listOfSequences
        self.mCreateSequenceButton = ui.newSequence
        listofnames = ["Vincent","Amelie","Jeremie", "Olivier", "Jacob"]
        for i in listofnames:
            sequence = Sequence(i)
            self.mListOfSequences.addItem(sequence)
        # TODO: maybe move the connect elsewhere so there's no need for a private delete button
        # connect the create button to the addWindow function which creates a new window
        self.mCreateSequenceButton.clicked.connect(self.addWindow)
        # connect the qwidgetlist to the custom right click menu
        self.mListOfSequences.customContextMenuRequested.connect(self.showMenu)

    def addItem(self, item):
        self.mListOfSequences.addItem(item)

    def removeItem(self, row):
        self.mListOfSequences.takeItem(row)

    def removeSelectedItem(self):
        listItems = self.mListOfSequences.selectedItems()
        if not listItems: return
        for item in listItems:
            self.mListOfSequences.takeItem(self.mListOfSequences.row(item))

    def addWindow(self):
        self.w = CreateSequenceWindow()
        # 2 first number QPoint and 2 last QSize
        self.w.setGeometry(QRect(100, 100, 400, 200))
        self.w.show()

    def showMenu(self, event):
        menu = QMenu()
        # TODO: implement the More Information functionality (show the characteristics and modify them)
        menu.addAction("Modify Sequence")
        menu.addAction("Delete Sequence", self.removeSelectedItem)
        menu.exec_(self.mListOfSequences.mapToGlobal(event))


# Window for creating a new sequence
class CreateSequenceWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.cancelButton = QPushButton('Cancel', self)
        # close is a function of QWidget
        self.cancelButton.clicked.connect(self.close)
        layout = QVBoxLayout(self)
        layout.addWidget(self.cancelButton)

# unfinished class
class Sequence(QListWidgetItem):
    def __init__(self, name="name",motors = {}, status = False):
        QListWidgetItem.__init__(self)
        self.setText(name)
        self.mMotors = {}
        self.mStatus = status

    # def addMotor(self, motor):

# class for a motor and its characteristics
class Motor:
    def __init__(self, name="name", pos = 0, status = False):
        self.__name = name
        self.__position = pos
        self.__status = status

    def setPosition(self, pos):
        self.__position=pos

    def getPosition(self):
        return self.__position

    def setName(self, name):
        self.__name = name

    def getName(self):
        return self.__name

    def setStatus(self, status):
        self.__status = status

    def getStatus(self):
        return self.__status


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

        self.listItem = ListOfSequencesHandler(self.ui)

        self.initializeSliderPositions()

        # Connect the slider signals
        self.ui.slider_mot1.valueChanged.connect(lambda: changeMotorPosition(self.ui.slider_mot1, 1))
        self.ui.slider_mot2.valueChanged.connect(lambda: changeMotorPosition(self.ui.slider_mot2, 2))
        self.ui.slider_mot3.valueChanged.connect(lambda: changeMotorPosition(self.ui.slider_mot3, 3))
        self.ui.slider_mot4.valueChanged.connect(lambda: changeMotorPosition(self.ui.slider_mot4, 4))
        self.ui.slider_mot5.valueChanged.connect(lambda: changeMotorPosition(self.ui.slider_mot5, 5))
        self.ui.slider_mot6.valueChanged.connect(lambda: changeMotorPosition(self.ui.slider_mot6, 6))

        # Connect button signals
        self.ui.calibrateVerticalAxisButton.clicked.connect(calibrateVerticalAxis)

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
def changeMotorPosition(slider, num):
    value = slider.value()
    print("Motor #%d: %d" % (num, value))
    # TODO: make this into a sentence and send it to the controller


def calibrateVerticalAxis():
    print("Calibrating vertical axis")
    # TODO: launch calibration process on controller


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec_()
    sys.exit()
