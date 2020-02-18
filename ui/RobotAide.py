# Description: GUI application for the control of the robotic arm
#
# Authors: Jeremie Bourque <Jeremie.Bourque@USherbrooke.ca>
#          Jacob Kealey <Jacob.Kealey@USherbrooke.ca>
#
# Date created: 22-01-2020


from PySide2.QtWidgets import QApplication, QMainWindow, QLineEdit, QVBoxLayout, QMenu, QListWidgetItem,\
    QDialog, QDialogButtonBox, QLabel, QPushButton, QSlider, QListWidget, QMessageBox
from PySide2.QtGui import QIcon
from PySide2.QtCore import QRect, Qt
from PySide2.QtUiTools import QUiLoader
import sys
import warnings
import struct
import serial

# To remove the following warning: DeprecationWarning: an integer is required
# (got type PySide2.QtWidgets.QDialogButtonBox.StandardButton).
# Implicit conversion to integers using __int__ is deprecated, and may be removed in a future version of Python.
# self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
warnings.filterwarnings("ignore","an integer is required", DeprecationWarning)

# App icon
icon = 'icon.png'

# Reference for the documentation https://www.youtube.com/watch?v=yUe46581x58

# Define struct format for communicating messages
# H (short, 2 bytes) : motor position
# message size = 12 bytes
s = struct.Struct('6H')

# Establish serial connection
# TODO: refactor as function
port = 'COM4'
try:
    ser = serial.Serial(port, 9600)
    print("Connected to %s" % port)
except serial.serialutil.SerialException:
    print("Failed to connect to %s." % port)
# TODO: port should be chosen in the gui

# Handler for the list of sequences
class ListOfSequencesHandler:
    """
    test for documentation
    """
    def __init__(self, ui, motors = {}):
        self.__motors = motors
        self.mListOfSequences = ui.listOfSequences
        self.mCreateSequenceButton = ui.newSequence
        self.__ui = ui

        # Connect the create button to the addWindow function which creates a new window
        self.mCreateSequenceButton.clicked.connect(self.addWindow)

        # Connect the qwidgetlist to the custom right click menu
        self.mListOfSequences.customContextMenuRequested.connect(self.showMenu)

        # Put the sliders in a list
        self.listOfSliders = []
        for motor in motors:
            slider = QSlider()
            slider.setOrientation(Qt.Horizontal)
            self.listOfSliders.append(slider)


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
        self.__ui.setEnabled(False)
        # 2 first number QPoint and 2 last QSize
        self.w.setGeometry(QRect(150, 150, 600, 400))
        self.w.show()

    def showMenu(self, event):
        menu = QMenu()
        # TODO: implement the Modify Sequence functionality (show the characteristics and modify them)
        menu.addAction("Modify Sequence")
        menu.addAction("Delete Sequence", self.removeSelectedItem)
        menu.exec_(self.mListOfSequences.mapToGlobal(event))

    def enableUi(self):
        self.__ui.setEnabled(True)


# Window for creating a new sequence
class CreateSequenceWindow(QDialog):
    def __init__(self, motors={}, listOfSequenceHandler=None):
        QDialog.__init__(self)
        appIcon = QIcon(icon)
        self.setWindowIcon(appIcon)

        self.__listOfSequenceHandler = listOfSequenceHandler
        self.__motors = motors
        self.__sequence = Sequence(motors)
        self.__wantedPositions = {}
        self.layout = QVBoxLayout(self)
        self.__nameEntry = QLineEdit()
        self.__nameLabel = QLabel("Sequence Name")
        self.__listOfMoves = QListWidget()

        # Message to make the user put a name to the sequence
        self.__noNameMessage = QMessageBox()
        self.__noNameMessage.setText("Your sequence doesn't have a name by clicking the ok button "
                                     "it will not be saved")
        self.__noNameMessage.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        # Close the create sequence window and the message
        self.__noNameMessage.accepted.connect(self.reject)
        # Renable the create sequence window and closes the message
        self.__noNameMessage.rejected.connect(self.enableWindow)


        # Set the text for the labels
        self.mMotorLabels = []
        for motorNumber in range(0,len(motors)):
            self.mMotorLabels.append(QLabel("Motor " + str(motorNumber+1) + " position"))

        self.nextMoveButton = QPushButton("Next Move")

        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        # If ok pressed add the sequence to the list
        self.buttonBox.accepted.connect(self.addItem)
        # If cancel pressed close the create sequence window
        self.buttonBox.rejected.connect(self.reject)

        # Renable the main window when the create sequence closes
        self.rejected.connect(self.__listOfSequenceHandler.enableUi)
        self.accepted.connect(self.__listOfSequenceHandler.enableUi)

        self.__nameEntry.textEdited.connect(self.setName)
        self.nextMoveButton.clicked.connect(self.addMovetoSequence)

        self.__listOfMoves.itemDoubleClicked.connect(self.moveDoubleClicked)

        # Build the vertical layout with the different widgets
        self.layout.addWidget(self.__nameLabel)
        self.layout.addWidget(self.__nameEntry)
        self.layout.addWidget(self.__listOfMoves)
        for motorNumber in range(len(self.__motors)):
            self.layout.addWidget(self.mMotorLabels[motorNumber])
            self.layout.addWidget(self.__listOfSequenceHandler.listOfSliders[motorNumber])
        self.layout.addWidget(self.nextMoveButton)
        self.layout.addWidget(self.buttonBox)

    def setName(self, name):
        self.__sequence.setName(name)

    def addItem(self):
        if self.__sequence.getName() != "":
            self.__listOfSequenceHandler.addItem(self.__sequence)
            self.accept()
        else:
            self.setEnabled(False)
            self.__noNameMessage.exec_()


    def addMovetoSequence(self):
        # Create the new move and set his positions
        move = Move(self.__motors)
        i = 0
        for motorName in self.__motors:
            move.setMotorPosition(motorName, self.__listOfSequenceHandler.listOfSliders[i].value())
            i += 1
        self.__sequence.addMove(move)

        # Set text for the move label
        labelText = "move " + self.__sequence.getNumberofMoves() +": "
        i = 0
        for motor in self.__motors:
            labelText += self.__motors[motor].getName() + " " +\
                         str(self.__listOfSequenceHandler.listOfSliders[i].value()) + ", "
            i += 1
        label = moveLabel(move,labelText,self.__motors)

        # insert label to the head of the list
        self.__listOfMoves.insertItem(0, label)

    # Access the move positions when double clicked on
    def moveDoubleClicked(self, moveItem):
        moveItem.doubleClickEvent()

    def enableWindow(self):
        self.setEnabled(True)

# Class for the labels that are stored in the move list in the sequence creator
class moveLabel(QListWidgetItem):
    def __init__(self, move = None, text = None, motors = {}, parent=None):
        QListWidgetItem.__init__(self, parent)
        self.__move = move
        self.__motors = motors
        self.setText(text)

    def doubleClickEvent(self):
        # TODO: make the motors move to their respective positions
        for motor in self.__motors:
            print(motor + " "+ str(self.__move.getMotorPosition(motor)))


# Class for a sequence of moves
class Sequence(QListWidgetItem):
    def __init__(self,motors = {}, name=""):
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

    def addMove(self, newMove):
        self.__moves.append(newMove)

    def getNumberofMoves(self):
        return str(len(self.__moves))

# Class for a move of a sequence
class Move:
    def __init__(self, motors = {}):
        self.__motors = motors

        # To store the different positions of the move
        self.__movePositions = dict()
        # Initialize move positions to an invalid position (-1)
        for motor in self.__motors:
            self.__movePositions[motor] = -1

    def setMotorPosition(self, motorName, position):
        if motorName in self.__motors:
            self.__motors[motorName].setPosition(position)
            self.__movePositions[motorName] = position
        else:
            return "There's no motor named that way"

    def getMotorPosition(self, motorName):
        if motorName in self.__movePositions:
            return self.__movePositions[motorName]
        else:
            return "There's no motor named that way"



# Class for a motor and its characteristics
class Motor:
    def __init__(self, mainWindow = None, name="", pos = 0, status = False):
        self.__name = name
        self.__position = pos
        self.__status = status
        self.__window = mainWindow

    def setPosition(self, pos):
        self.__position=pos
        # print("%s: %d" % (self.__name, pos))
        sendMessage(self.__window)

    def getPosition(self):
        return self.__position

    def setName(self, name):
        self.__name = name

    def getName(self):
        return self.__name

    def setStatus(self, status):
        self.__status = status

    def isEnabled(self):
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
        self.dictMot = dict()
        for i in range(1, 7):
            mot = Motor(self,"motor" + str(i))
            self.dictMot[mot.getName()] = mot
        # ---------------

        self.__listOfSenquenceHandler = ListOfSequencesHandler(self.ui, self.dictMot)

        self.initializeSliderPositions()

        # Connect the slider signals
        self.ui.slider_mot1.valueChanged.connect(lambda: self.dictMot["motor1"].setPosition(self.ui.slider_mot1.value()))
        self.ui.slider_mot2.valueChanged.connect(lambda: self.dictMot["motor2"].setPosition(self.ui.slider_mot2.value()))
        self.ui.slider_mot3.valueChanged.connect(lambda: self.dictMot["motor3"].setPosition(self.ui.slider_mot3.value()))
        self.ui.slider_mot4.valueChanged.connect(lambda: self.dictMot["motor4"].setPosition(self.ui.slider_mot4.value()))
        self.ui.slider_mot5.valueChanged.connect(lambda: self.dictMot["motor5"].setPosition(self.ui.slider_mot5.value()))
        self.ui.slider_mot6.valueChanged.connect(lambda: self.dictMot["motor6"].setPosition(self.ui.slider_mot6.value()))

        # Connect button signals
        self.ui.calibrateVerticalAxisButton.clicked.connect(calibrateVerticalAxis)

    def setIcon(self):
        appIcon = QIcon(icon)
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


# Send message to Arduino containing all motor values
def sendMessage(mainWindow):
    values = (mainWindow.dictMot["motor1"].getPosition(),
              mainWindow.dictMot["motor2"].getPosition(),
              mainWindow.dictMot["motor3"].getPosition(),
              mainWindow.dictMot["motor4"].getPosition(),
              mainWindow.dictMot["motor5"].getPosition(),
              mainWindow.dictMot["motor6"].getPosition())
    packed_data = s.pack(*values)
    ser.write(packed_data)


def calibrateVerticalAxis():
    print("Calibrating vertical axis")
    # TODO: launch calibration process on controller


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec_()
    sys.exit()
