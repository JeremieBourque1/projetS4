# Description: GUI application for the control of the robotic arm
#
# Authors: Jeremie Bourque <Jeremie.Bourque@USherbrooke.ca>
#          Jacob Kealey <Jacob.Kealey@USherbrooke.ca>
#
# Date created: 22-01-2020


from PySide2.QtWidgets import QApplication, QMainWindow, QLineEdit, QVBoxLayout, QMenu, QListWidgetItem,\
    QDialog, QDialogButtonBox, QLabel, QPushButton
from PySide2.QtGui import QIcon
from PySide2.QtCore import QRect
from PySide2.QtUiTools import QUiLoader
import sys
import warnings

# To remove the following warning: DeprecationWarning: an integer is required
# (got type PySide2.QtWidgets.QDialogButtonBox.StandardButton).
# Implicit conversion to integers using __int__ is deprecated, and may be removed in a future version of Python.
# self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
warnings.filterwarnings("ignore","an integer is required", DeprecationWarning)

class ListOfSequencesHandler:
    def __init__(self, ui, motors = {}):
        self.__motors = motors
        self.mListOfSequences = ui.listOfSequences
        self.mCreateSequenceButton = ui.newSequence
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
        self.w = CreateSequenceWindow(self.__motors, self)
        # 2 first number QPoint and 2 last QSize
        self.w.setGeometry(QRect(150, 150, 600, 400))
        self.w.show()

    def showMenu(self, event):
        menu = QMenu()
        # TODO: implement the Modify Sequence functionality (show the characteristics and modify them)
        menu.addAction("Modify Sequence")
        menu.addAction("Delete Sequence", self.removeSelectedItem)
        menu.exec_(self.mListOfSequences.mapToGlobal(event))


# Window for creating a new sequence
class CreateSequenceWindow(QDialog):
    # TODO: get the motors
    def __init__(self, motors = {}, listOfSequenceHandler = None):
        QDialog.__init__(self)
        appIcon = QIcon("icon.jpg")
        self.setWindowIcon(appIcon)

        self.__listOfSequenceHandler = listOfSequenceHandler
        self.__motors = motors
        self.__sequence = Sequence(motors)
        self.__wantedPositions = {}

        self.layout = QVBoxLayout(self)
        self.mNameEntry = QLineEdit()
        self.mNameLabel = QLabel("Sequence Name")
        # TODO: mettre des sliders pour les moteurs
        self.mMotor1Entry = QLineEdit()
        self.mMotor1Label = QLabel("Motor1 Position")
        self.mMotor2Entry = QLineEdit()
        self.mMotor2Label = QLabel("Motor2 Position")
        self.nextMoveButton = QPushButton("Next Move")
        self.buttonBox = QDialogButtonBox()

        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.accepted.connect(self.addItem)
        self.buttonBox.rejected.connect(self.reject)

        self.mNameEntry.textEdited.connect(self.setName)
        self.mMotor1Entry.textEdited.connect(self.setMotor1Position)
        self.mMotor2Entry.textEdited.connect(self.setMotor2Position)

        self.nextMoveButton.clicked.connect(self.addMovetoSequence)

        self.layout.addWidget(self.mNameLabel)
        self.layout.addWidget(self.mNameEntry)
        self.layout.addWidget(self.mMotor1Label)
        self.layout.addWidget(self.mMotor1Entry)
        self.layout.addWidget(self.mMotor2Label)
        self.layout.addWidget(self.mMotor2Entry)
        self.layout.addWidget(self.nextMoveButton)
        self.layout.addWidget(self.buttonBox)

    def setName(self, name):
        self.__sequence.setName(name)

    def addItem(self):
        if self.__sequence.getName() != "name":
            self.__listOfSequenceHandler.addItem(self.__sequence)

    def setMotor1Position(self, pos):
        self.__wantedPositions["motor1"] = pos

    def setMotor2Position(self, pos):
        self.__wantedPositions["motor2"] = pos

    def addMovetoSequence(self):
        self.__sequence.addMove(self.__motors, self.__wantedPositions)


# unfinished class
class Sequence(QListWidgetItem):
    def __init__(self,motors = {}, name="name"):
        QListWidgetItem.__init__(self)
        # QListWidgetItem method for setting the text of the item
        self.setText(name)
        self.__moves = []
        self.__name = name
        self.__motors = motors

    def setName(self, name):
        self.setText(name)
        self.__name = name

    def getName(self):
        return self.__name

    # motorName: list of names of the motors (the keys to the positions dictionary)
    # positions: dictionary of positions for a motor
    def addMove(self, motors, positions):
        newMove = Move(self.__motors)
        for motorName in motors:
            newMove.setMotorPosition(motorName, positions[motorName])
        self.__moves.append(newMove)


# Class for a move of a sequence
class Move:
    def __init__(self, motors = {}):
        self.__motors = motors
        # to store the different positions of the move
        self.__movePositions = {}

    def setMotorPosition(self, motorName, position):
        if motorName in self.__motors:
            # TODO: verify that it is an int/float
            self.__motors[motorName].setPosition(position)
            self.__movePositions[motorName] = position
        else:
            return "There's no motor named that way"

    def getMotorPosition(self, motorName):
        if motorName in self.__motors:
            return self.__movePositions[motorName]
        else:
            return "There's no motor named that way"



# Class for a motor and its characteristics
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

        # ---------------
        mot1 = Motor("motor1")
        mot2 = Motor("motor2")
        dictMot = dict()
        dictMot[mot1.getName()] = mot1
        dictMot[mot2.getName()] = mot2
        # sequence1 = Sequence("testSequence", dictMot)
        # ---------------

        self.listItem = ListOfSequencesHandler(self.ui, dictMot)
        #self.listItem.addItem(sequence1)

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
