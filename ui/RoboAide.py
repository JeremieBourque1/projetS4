# Description: GUI application for the control of the robotic arm
#
# Authors: Jeremie Bourque <Jeremie.Bourque@USherbrooke.ca>
#          Jacob Kealey <Jacob.Kealey@USherbrooke.ca>
#
# Date created: 22-01-2020


from PySide2.QtWidgets import QApplication, QMainWindow, QLineEdit, QVBoxLayout, QMenu, QListWidgetItem,\
    QDialog, QDialogButtonBox, QLabel, QPushButton, QSlider, QListWidget, QMessageBox
from PySide2.QtGui import QIcon
from PySide2.QtCore import QRect, Qt, QThread, Signal
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

## App icon
icon = 'icon.png'

## Serial communication port
commPort = 'COM3'
# TODO: port should be chosen in the gui

# Reference for the documentation https://www.youtube.com/watch?v=yUe46581x58
# Ignore the part with the py_filter.py!!
# To see the doc go to docs->html->index.html

## Define struct format for communicating messages
# H (short, 2 bytes) : motor position
# message size = 12 bytes
s = struct.Struct('6H')

def initSerialConnection(port):
    """
    Initialize the serial connection with the device connected on the port
    :param port: The serial port which the Arduino is connected on
    :return: Serial object which is used to communicate with the Arduino
    """
    try:
        ser = serial.Serial(port, 9600)
        print("Connected to %s" % port)
        return ser
    except serial.serialutil.SerialException:
        print("Failed to connect to %s." % port)

class MessageReception(QThread):
    """
    Class for a thread that handles incoming serial messages
    """
    # TODO: We need to receive logs (lines of text) and motor data than can be unpacked into the struct.
    def run(self):
        print("Message Reception thread started")
        while True:
            try:
                print(comm.readline())
            except (AttributeError, NameError) as e:
                pass

class ListOfSequencesHandler:
    """
    Handler for the list of sequences
    """
    def __init__(self, ui, motors = {}):
        """
        Initializtion of the handler for the list of sequences
        :param ui: The ui in which the list of sequence is in
        :param motors: The dictionary of all the motors
        """
        ## The dictionary of all the motors
        self.__motors = motors
        ## The list of sequence
        self.__listOfSequences = ui.listOfSequences
        ## The create a new sequence button
        self.__createSequenceButton = ui.createSequenceButton
        ## The ui in which the list of sequence is in
        self.__ui = ui
        ## The window in which the new sequence will be created
        self.__window = None

        # Create a new window when the create sequence button is clicked
        self.__createSequenceButton.clicked.connect(self.createWindow)

        # Connect the qwidgetlist to the custom right click menu
        self.__listOfSequences.customContextMenuRequested.connect(self.showMenu)

        # Put the sliders of the create sequence window in a list
        ## List of sliders in the create sequence window
        self.listOfSliders = []
        for motor in motors:
            slider = QSlider()
            slider.setOrientation(Qt.Horizontal)
            self.listOfSliders.append(slider)

    def addItem(self, item):
        """
        Add an item to the list of sequence
        :param item: The item to add
        :return: No return
        """
        self.__listOfSequences.addItem(item)

    def removeSelectedItem(self):
        """
        Removes the selected item in the list
        :return: No return
        """
        listItems = self.__listOfSequences.selectedItems()
        if not listItems: return
        for item in listItems:
            self.__listOfSequences.takeItem(self.__listOfSequences.row(item))

    def createWindow(self):
        """
        Create the window for to create a new sequence
        :return: No return
        """
        self.__window = CreateSequenceWindow(self.__motors, self)
        self.__ui.setEnabled(False)
        # 2 first number QPoint where the window is created and 2 last QSize(the size of the window)
        self.__window.setGeometry(QRect(150, 150, 600, 400))
        self.__window.show()

    def showMenu(self, event):
        """
        The right click menu of the sequence of the list
        :param event: The event (here right click) that makes the menu come up
        :return: No return
        """
        menu = QMenu()
        # TODO: implement the Modify Sequence functionality (show the characteristics and modify them)
        menu.addAction("Modify Sequence")
        # Add a button in the menu that when clicked, it deletes the sequence in the list
        menu.addAction("Delete Sequence", self.removeSelectedItem)
        menu.exec_(self.__listOfSequences.mapToGlobal(event))

    def enableUi(self):
        """
        Enable the ui
        :return: No return
        """
        self.__ui.setEnabled(True)

class CreateSequenceWindow(QDialog):
    """
    Window for creating a new sequence
    """
    def __init__(self, motors={}, listOfSequenceHandler=None):
        """
        Initializtion of the window for creating a new sequence
        :param motors: The dictionary of all the motors
        :param listOfSequenceHandler: The handler of the list of sequence
        """
        QDialog.__init__(self)
        # Set the window icon
        appIcon = QIcon(icon)
        self.setWindowIcon(appIcon)

        ## The handler of the list of sequence
        self.__listOfSequenceHandler = listOfSequenceHandler
        ## The dictionary of all the motors
        self.__motors = motors
        ## The new sequence
        self.__sequence = Sequence(motors)
        ## A dictionary of the positions of the new sequence
        self.__wantedPositions = {}
        ## The layout of the create sequence window
        self.__layout = QVBoxLayout(self)
        ## The widget for the name of the sequence
        self.__nameEntry = QLineEdit()
        ## The label for the widget in which the name of the sequence is written
        self.__nameLabel = QLabel("Sequence Name")
        ## The list of the different moves that forms the sequence
        self.__listOfMoves = QListWidget()

        ## Message to make the user put a name to the sequence
        self.__noNameMessage = QMessageBox()
        self.__noNameMessage.setText("Your sequence doesn't have a name by clicking the ok button "
                                     "it will not be saved")
        self.__noNameMessage.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        # Close the create sequence window and the message
        self.__noNameMessage.accepted.connect(self.reject)
        # Renable the create sequence window and closes the message
        self.__noNameMessage.rejected.connect(self.enableWindow)

        # Set the text for the labels
        ## Labels for the motors in the UI
        self.__motorLabels = []
        for motorNumber in range(0,len(motors)):
            self.__motorLabels.append(QLabel("Motor " + str(motorNumber+1) + " position"))

        ## Button to add a move to the sequence and procede to the next move
        self.nextMoveButton = QPushButton("Next Move")

        ## Buttons to accept or cancel the creation of a sequence
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
        self.__layout.addWidget(self.__nameLabel)
        self.__layout.addWidget(self.__nameEntry)
        self.__layout.addWidget(self.__listOfMoves)
        for motorNumber in range(len(self.__motors)):
            self.__layout.addWidget(self.__motorLabels[motorNumber])
            self.__layout.addWidget(self.__listOfSequenceHandler.listOfSliders[motorNumber])
        self.__layout.addWidget(self.nextMoveButton)
        self.__layout.addWidget(self.buttonBox)

    def setName(self, name):
        """
        Sets the name of the sequence with the user input
        :param name: The name of the sequence
        :return: No return
        """
        self.__sequence.setName(name)

    def addItem(self):
        """
        Add the sequence to the list of sequence
        :return:
        """
        if self.__sequence.getName() != "":
            self.__listOfSequenceHandler.addItem(self.__sequence)
            self.accept()
        else:
            self.setEnabled(False)
            self.__noNameMessage.exec_()

    def addMovetoSequence(self):
        """
        Add the last move to the sequence
        :return:
        """

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
        """
        Called when a move in the sequence is double clicked
        :param moveItem: the move that was double clicked
        :return: No return
        """
        moveItem.doubleClickEvent()

    def enableWindow(self):
        """
        Enable the create sequence window
        :return:
        """
        self.setEnabled(True)

class moveLabel(QListWidgetItem):
    """
    Class for the custom labels that are stored in the move list in the sequence creator
    """
    def __init__(self, move = None, text = None, motors = {}, parent=None):
        """
        Initialization of the move label
        :param move: The move
        :param text: The text in the label
        :param motors: Dictionary of all the motors
        :param parent: The Qt parent
        """
        QListWidgetItem.__init__(self, parent)
        self.__move = move
        self.__motors = motors
        self.setText(text)

    def doubleClickEvent(self):
        """
        Handles the event when the move lable is double clicked
        :return:
        """
        # TODO: make the motors move to their respective positions
        for motor in self.__motors:
            print(motor + " "+ str(self.__move.getMotorPosition(motor)))


# Class for a sequence of moves
class Sequence(QListWidgetItem):
    """

    """
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
        print("%s: %d" % (self.__name, pos))
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

        # Serial communication
        self.msgReception = MessageReception()
        self.msgReception.start()

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
    try:
        comm.write(packed_data)
    except (AttributeError, NameError) as e:
        print("Error sending message")


def calibrateVerticalAxis():
    print("Calibrating vertical axis")
    # TODO: launch calibration process on controller


if __name__ == "__main__":
    comm = initSerialConnection(commPort)
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec_()
    sys.exit()
