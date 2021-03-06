# Description: GUI application for the control of the robotic arm
#
# Authors: Jeremie Bourque <Jeremie.Bourque@USherbrooke.ca>
#          Jacob Kealey <Jacob.Kealey@USherbrooke.ca>
#
# Date created: 22-01-2020

import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__))) # import error fix


from PySide2.QtWidgets import QApplication, QMainWindow, QLineEdit, QVBoxLayout, QMenu, QListWidgetItem,\
    QDialog, QDialogButtonBox, QLabel, QPushButton, QSlider, QListWidget, QMessageBox
from PySide2.QtGui import QIcon, QBrush
from PySide2.QtCore import QRect, Qt, QMutex, QThread, Signal
from PySide2.QtUiTools import QUiLoader
from Communication import MessageReception, MessageTransmission, initSerialConnection, scanAvailablePorts
from Drawer import Drawer
from collections import deque

import warnings
import struct

import json
import time


# To remove the following warning: DeprecationWarning: an integer is required
# (got type PySide2.QtWidgets.QDialogButtonBox.StandardButton).
# Implicit conversion to integers using __int__ is deprecated, and may be removed in a future version of Python.
# self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
warnings.filterwarnings("ignore","an integer is required", DeprecationWarning)

# Change working directory to this script's directory to easily access mainwindow.ui
os.chdir(os.path.dirname(os.path.realpath(__file__)))

## App icon
icon = 'icon.png'

class playSequence(QThread):
    """
    Tread to send the different positions to the motors during a sequence
    """
    def __init__(self,moves,motors, listOfSequencesHandler, mainWindow):
        """
        Initialization of the play sequence thread
        :param moves: the moves of the sequence containing the different positions to reach
        :param motors: the motors of the robot
        :param listOfSequencesHandler: the handler of the different sequences
        :param mainWindow: the main window of the UI
        """
        super(playSequence, self).__init__()
        ## The moves of the sequence containing the different positions to reach
        self.__moves=moves
        ## The motors of the robot
        self.__motors=motors
        ## The handler of the different sequences
        self.__listOfSequencesHandler = listOfSequencesHandler
        ## The main window of the UI
        self.__mainWindow = mainWindow

        # Make sure the thread close properly even if the app is closed
        self.__mainWindow.app.aboutToQuit.connect(self.close)

        # connect a custom function to handle the different events when the thread is closed
        self.finished.connect(self.stop)

    def run(self):
        for move in self.__moves:
            for motor in self.__motors:
                self.__motors[motor].setGoalPosition(move.getMotorPosition(motor))
            for motor in self.__motors:
                while self.__motors[motor].getCurrentPosition() < self.__motors[motor].getGoalPosition() - 10 \
                        or self.__motors[motor].getCurrentPosition() > self.__motors[motor].getGoalPosition() + 10:
                    if not self.__mainWindow.shouldStop:
                        # print("current position:" + str(self.__motors[motor].getCurrentPosition()))
                        # print("goal position:" + str(self.__motors[motor].getGoalPosition()))
                        self.__motors[motor].setGoalPosition(move.getMotorPosition(motor))
                        self.msleep(250)
                    else:
                        break


    def stop(self):
        """
        Handles the different events when the thread is closed
        :return: None
        """
        self.__listOfSequencesHandler.robotInMotionMessage.accept()
        self.__listOfSequencesHandler.enableUi()
        self.__mainWindow.shouldStop = False

    def close(self):
        """
        To get out of the while loop
        :return: None
        """
        self.__mainWindow.shouldStop = True


def loadSequences(listOfSequenceHandler,motors):
    """
    To load the saved sequence in the SaveSequence.json file and put them in the list of sequence
    :param listOfSequenceHandler: To add the sequences to the list
    :param motors: the motors of the robotic arm
    :return: No return
    """
    try:
        with open('SaveSequence.json') as save:
            savedListOfSequences = json.load(save)
        for sequence in savedListOfSequences:
            for sequenceName in sequence:
                savedSequence = Sequence(motors,sequenceName)
                for move in sequence[sequenceName]:
                    savedMove = Move(motors)
                    for motor in move:
                        savedMove.setMotorPosition(motor, move[motor])
                    savedSequence.addMove(savedMove)
                listOfSequenceHandler.addItem(savedSequence)
    except FileNotFoundError:
        print("Save file not found")

class ListOfSequencesHandler:
    """
    Handler for the list of sequences
    """
    def __init__(self, mainWindow, motors):
        """
        Initializtion of the handler for the list of sequences
        :param ui: The ui in which the list of sequence is in
        :param motors: The dictionary of all the motors
        """
        ## The dictionary of all the motors
        self.__motors = motors
        ## The list of sequence
        self.__listOfSequences = mainWindow.ui.listOfSequences
        self.__listOfSequences.itemDoubleClicked.connect(self.playSequence)
        ## The create a new sequence button
        self.__createSequenceButton = mainWindow.ui.createSequenceButton
        ## The ui in which the list of sequence is in
        self.__ui = mainWindow.ui
        ## The main window of the ui
        self.__mainWindow = mainWindow
        ## The window in which the new sequence will be created
        self.__window = None
        ## Thread to send the sequence to the motors
        self.playSequenceThread = None
        ## Message to make the user put a name to the sequence
        # TODO: Set the size of the message to something appropriate
        self.robotInMotionMessage = QMessageBox()
        self.robotInMotionMessage.setIcon(QMessageBox.Information)
        self.robotInMotionMessage.setWindowIcon(QIcon(icon))
        self.robotInMotionMessage.setText("Robot is in motion")
        self.robotInMotionMessage.addButton(QMessageBox.Abort)
        self.robotInMotionMessage.rejected.connect(self.__mainWindow.stopMotors)
        self.robotInMotionMessage.rejected.connect(self.enableUi)

        # Create a new window when the create sequence button is clicked
        self.__createSequenceButton.clicked.connect(self.createWindow)

        # Connect the qwidgetlist to the custom right click menu
        self.__listOfSequences.customContextMenuRequested.connect(self.showMenu)

    def addItem(self, item):
        """
        Add an item to the list of sequence
        :param item: The QListWidgetItem sequence to add
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
            # Load the save file
            with open('SaveSequence.json', 'r') as save_file:
                savedListOfSequences = json.load(save_file)
            # Search for the sequence that needs to be deleted
            indexSequence = -1
            for sequence in range(len(savedListOfSequences)):
                for sequenceName in savedListOfSequences[sequence]:
                    if sequenceName == item.getName():
                        # Delete the sequence
                        indexSequence = sequence
            if indexSequence != -1:
                savedListOfSequences.pop(indexSequence)

            # Rewrite the save file without the deleted sequence
            with open('SaveSequence.json', 'w') as save_file:
                json.dump(savedListOfSequences, save_file)

    def createWindow(self, modifySequence = False):
        """
                Create the window to create a new sequence
        :param modifySequence: bool, if true there's a selected sequence that needs to be modified if false
        it's a new sequence
        :return: No return
        """
        if modifySequence:
            self.__window = CreateSequenceWindow(self.__motors, self, self.getSelectedItems()[0], True)
        else:
            self.__window = CreateSequenceWindow(self.__motors, self, Sequence(self.__motors))
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
        menu.addAction("Modify Sequence",lambda: self.createWindow(True))
        # Add a button in the menu that when clicked, it deletes the sequence in the list
        menu.addAction("Delete Sequence", self.removeSelectedItem)
        menu.exec_(self.__listOfSequences.mapToGlobal(event))

    def enableUi(self):
        """
        Enable the ui
        :return: No return
        """
        self.__ui.setEnabled(True)

    def getSelectedItems(self):
        """
        Accessor to the selected items of the list
        :return: the selected items
        """
        # Returns the only item in the list because the list is set to be
        return self.__listOfSequences.selectedItems()

    def playSequence(self):
        self.playSequenceThread = playSequence(self.getSelectedItems()[0].getMoves(), self.__motors,self,self.__mainWindow)
        self.__ui.setEnabled(False)
        # self.robotInMotionMessage.rejected.connect(self.playSequenceThread.quit)
        self.playSequenceThread.start()
        self.robotInMotionMessage.exec_()

class CreateSequenceWindow(QDialog):
    """
    Window for creating a new sequence
    """
    def __init__(self, motors={}, listOfSequenceHandler = None, sequence = None, modifySequence = False):
        """
        Initializtion of the window for creating a new sequence
        :param motors: The dictionary of all the motors
        :param listOfSequenceHandler: The handler of the list of sequence
        """
        QDialog.__init__(self)
        # Set the window icon
        appIcon = QIcon(icon)
        self.setWindowIcon(appIcon)

        ## Flag if the sequence is a modified one or a new one
        self.__modifySequence = modifySequence
        ## The handler of the list of sequence
        self.__listOfSequenceHandler = listOfSequenceHandler
        ## The dictionary of all the motors
        self.__motors = motors
        ## The new sequence
        self.__sequence = sequence
        ## A dictionary of the positions of the new sequence
        self.__wantedPositions = {}
        ## The layout of the create sequence window
        self.__layout = QVBoxLayout(self)
        ## The widget for the name of the sequenc
        self.nameEntry = QLineEdit()
        self.nameEntry.setText(self.__sequence.getName())
        ## The label for the widget in which the name of the sequence is written
        self.__nameLabel = QLabel("Sequence Name")
        ## The list of the different moves that forms the sequence
        self.__listOfMoveLabels = QListWidget()
        moveNumber = 1
        for move in self.__sequence.getMoves():
            # Set text for the move label
            labelText = "move " + str(moveNumber) + ": "
            moveNumber += 1
            for motor in self.__motors:
                labelText += self.__motors[motor].getName() + " " + \
                             str(move.getMotorPosition(self.__motors[motor].getName())) + ", "
            label = moveLabel(move, labelText, self.__motors)

            # insert label to the head of the list
            self.__listOfMoveLabels.insertItem(0, label)

        # Put the sliders of the create sequence window in a list
        ## List of sliders in the create sequence window
        self.listOfSliders = []
        dictOfSlider = dict()

        for motor in self.__motors:
            dictOfSlider[motor] = QSlider(Qt.Horizontal)
            dictOfSlider[motor].setMaximum(4095)
            dictOfSlider[motor].setValue(self.__motors[motor].getCurrentPosition())
            dictOfSlider[motor].sliderMoved.connect(self.__motors[motor].setGoalPosition)
            self.listOfSliders.append(dictOfSlider[motor])

        ## Message to make the user put a name to the sequence
        self.__noNameMessage = QMessageBox()
        self.__noNameMessage.setIcon(QMessageBox.Warning)
        self.__noNameMessage.setWindowIcon(appIcon)
        self.__noNameMessage.setText("Please name your sequence before saving it")
        self.__noNameMessage.setStandardButtons(QMessageBox.Ok)
        # Renable the create sequence window and closes the message
        self.__noNameMessage.accepted.connect(self.enableWindow)

        ## Warning message to make sure the user doen't want to save the sequence
        self.__warningMessage = QMessageBox()
        self.__warningMessage.setIcon(QMessageBox.Warning)
        self.__warningMessage.setWindowIcon(appIcon)
        self.__warningMessage.setText("Are you sure you want to close this window? Your sequence will not be saved")
        self.__warningMessage.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        # Close the create sequence window and the message
        self.__warningMessage.accepted.connect(self.reject)
        # Renable the create sequence window and closes the message
        self.__warningMessage.rejected.connect(self.enableWindow)

        # Set the text for the labels
        ## Labels for the motors in the UI
        self.__motorLabels = []
        for motorNumber in range(0,len(motors)):
            self.__motorLabels.append(QLabel("Motor " + str(motorNumber+1) + " position"))

        ## Button to add a move to the sequence and procede to the next move
        self.nextMoveButton = QPushButton("Save Move")

        ## Buttons to accept or cancel the creation of a sequence
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        # If ok pressed add the sequence to the list
        self.buttonBox.accepted.connect(lambda: self.addSequenceToList(self.__modifySequence))
        # If cancel pressed close the create sequence window
        self.buttonBox.rejected.connect(self.__warningMessage.exec)

        # Renable the main window when the create sequence closes
        self.rejected.connect(self.__listOfSequenceHandler.enableUi)
        self.accepted.connect(self.__listOfSequenceHandler.enableUi)

        self.nextMoveButton.clicked.connect(self.addMovetoSequence)

        self.__listOfMoveLabels.itemDoubleClicked.connect(self.moveDoubleClicked)

        # Build the vertical layout with the different widgets
        self.__layout.addWidget(self.__nameLabel)
        self.__layout.addWidget(self.nameEntry)
        self.__layout.addWidget(self.__listOfMoveLabels)
        for motorNumber in range(len(self.__motors)):
            self.__layout.addWidget(self.__motorLabels[motorNumber])
            self.__layout.addWidget(self.listOfSliders[motorNumber])
        self.__layout.addWidget(self.nextMoveButton)
        self.__layout.addWidget(self.buttonBox)

        # Connect the qwidgetlist to the custom right click menu
        self.__listOfMoveLabels.setContextMenuPolicy(Qt.CustomContextMenu)
        self.__listOfMoveLabels.customContextMenuRequested.connect(self.rightClickMenu)

    def setName(self, name):
        """
        Sets the name of the sequence with the user input
        :param name: The name of the sequence
        :return: No return
        """
        self.__sequence.setName(name)

    def getSequence(self):
        """
        Accessor of the sequence (for tests)
        :return: the sequence
        """
        return self.__sequence

    def getListofMoveLabels(self):
        """
        Accessor of the list of move labels (for tests)
        :return: the list of move labels
        """
        return self.__listOfMoveLabels

    def addSequenceToList(self, modifySequence = False):
        """
        Add the sequence to the list of sequence
        :param modifySequence: bool, if true there's a selected sequence that needs to be modified if false
        it's a new sequence
        :return: No return
        """
        # TODO: look to move this method to the list of sequence handler
        # TODO: don't let the user enter a sequence that has the same name as an old one
        self.setName(self.nameEntry.text())
        if self.__sequence.getName() != "":
            # Load previously saved sequences
            try:
                with open('SaveSequence.json') as save:
                    savedListOfSequences = json.load(save)
            except FileNotFoundError:
                savedListOfSequences = []

            if modifySequence:
                # Get the item that needs to be modified
                # selectedSequence = self.__listOfSequenceHandler.getSelectedItems()
                # Find the selected sequence in the list of saved ones
                for sequence in savedListOfSequences:
                    if self.__sequence.getName() in sequence:
                        indexOfTheSequence = savedListOfSequences.index(sequence)
                        # remove the unmodified sequence to insert the modified sequence
                        savedListOfSequences.remove(sequence)
                        self.__listOfSequenceHandler.addItem(self.__sequence)
                        # Make the sequence json seriable
                        newSequence = dict()
                        newSequence[self.__sequence.getName()] = []
                        for moveNumber in range(len(self.__sequence.getMoves())):
                            newSequence[self.__sequence.getName()].append(
                                self.__sequence.getMoves()[moveNumber].getMovePositions())

                        # Append new sequence to the old ones
                        savedListOfSequences.insert(indexOfTheSequence,newSequence)

                        # Write the sequences to the file
                        with open('SaveSequence.json', 'w') as outfile:
                            json.dump(savedListOfSequences, outfile)

                        self.accept()
            else:
                self.__listOfSequenceHandler.addItem(self.__sequence)
                # Make the sequence json seriable
                newSequence = dict()
                newSequence[self.__sequence.getName()] = []
                for moveNumber in range(len(self.__sequence.getMoves())):
                    newSequence[self.__sequence.getName()].append(
                        self.__sequence.getMoves()[moveNumber].getMovePositions())

                # Append new sequence to the old ones
                savedListOfSequences.append(newSequence)

                # Write the sequences to the file
                with open('SaveSequence.json', 'w') as outfile:
                    json.dump(savedListOfSequences, outfile)

                self.accept()
        else:
            self.setEnabled(False)
            self.__noNameMessage.exec_()

    def addMovetoSequence(self):
        """
        Add the last move to the sequence
        :return: No return
        """
        move = None
        labelToModify = None
        # Check if there's a move in modifying state
        for row in range(self.__listOfMoveLabels.count()):
            if not self.__listOfMoveLabels.item(row).getMove().isNew:
                move = self.__listOfMoveLabels.item(row).getMove()
                labelToModify = self.__listOfMoveLabels.item(row)
                break
        # verify if the move is a new one
        if move is None:
            # Create the new move and set his positions
            move = Move(self.__motors)
            i = 0
            for motorName in self.__motors:
                move.setMotorPosition(motorName, self.listOfSliders[i].value())
                i += 1
            self.__sequence.addMove(move)

            # Set text for the move label
            labelText = "move " + str(self.__sequence.getNumberofMoves()) +": "
            i = 0
            for motor in self.__motors:
                labelText += self.__motors[motor].getName() + " " +\
                             str(self.listOfSliders[i].value()) + ", "
                i += 1
            label = moveLabel(move,labelText,self.__motors)

            # insert label to the head of the list
            self.__listOfMoveLabels.insertItem(0, label)
        else:
            # modify the move
            i = 0
            for motorName in self.__motors:
                move.setMotorPosition(motorName, self.listOfSliders[i].value())
                i += 1

            # modify the label of the move
            textToEdit = labelToModify.text()
            listOfTextToEdit = textToEdit.split(' ')
            labelText = listOfTextToEdit[0] + " " + listOfTextToEdit[1] + " "
            i = 0
            for motor in self.__motors:
                labelText += self.__motors[motor].getName() + " " + \
                             str(self.listOfSliders[i].value()) + ", "
                i += 1
            labelToModify.setText(labelText)
            labelToModify.setSelected(False)
            labelToModify.setBackground(Qt.white)

            # reset the state of the move
            move.isNew = True


    # Access the move positions when double clicked on
    def moveDoubleClicked(self, moveItem):
        """
        Called when a move in the sequence is double clicked
        :param moveItem: the move that was double clicked
        :return: No return
        """
        moveItem.goToMoveOfTheLabel()
        self.updateSlidersPositions()

    def updateSlidersPositions(self):
        counterMotors = 0
        for motor in self.__motors:
            self.listOfSliders[counterMotors].setValue(self.__motors[motor].getGoalPosition())
            counterMotors += 1

    def enableWindow(self):
        """
        Enable the create sequence window
        :return:
        """
        self.setEnabled(True)

    def rightClickMenu(self, event):
        """
        The right click menu of the move list
        :param event: The event (here right click) that makes the menu come up
        :return: No return
        """
        menu = QMenu()
        # Add a button in the menu that when clicked, it puts a move in modifying state
        menu.addAction("Modify Move",lambda: self.modifyMove(self.__listOfMoveLabels.selectedItems()[0]))
        # Add a button in the menu that when clicked, it deletes a move in the list
        menu.addAction("Delete Move",lambda: self.deleteMove(self.__listOfMoveLabels.selectedItems()[0]))
        menu.exec_(self.__listOfMoveLabels.mapToGlobal(event))

    def deleteMove(self,label):
        """
        Delete a move and its label of the sequence
        :param label: label of the move
        :return: No return
        """
        # remove the label from the list
        self.__listOfMoveLabels.takeItem(self.__listOfMoveLabels.row(label))
        # remove the move from the sequence
        self.__sequence.deleteMove(label.getMove())

        # rename the labels in the list of moves
        for index in range(self.__sequence.getNumberofMoves()-1,-1,-1):
            labelToModify = self.__listOfMoveLabels.item(index)
            textToEdit = labelToModify.text()
            listOfTextToEdit = textToEdit.split(' ')
            listOfTextToEdit[1] = str(self.__sequence.getNumberofMoves()-index) + ':'
            textToEdit = ' '.join(listOfTextToEdit)
            self.__listOfMoveLabels.item(index).setText(textToEdit)

    def modifyMove(self,label):
        """
        Put a move to a modified state
        :param label: label of the move
        :return: No return
        """
        # Check if there's a move in modifying state
        for row in range(self.__listOfMoveLabels.count()):
            if not self.__listOfMoveLabels.item(row).getMove().isNew:
                self.__listOfMoveLabels.item(row).getMove().isNew = True
                self.__listOfMoveLabels.item(row).setBackground(QBrush(Qt.white))

        moveToModify = label.getMove()
        moveToModify.isNew = False
        label.setBackground(QBrush(Qt.darkCyan))
        label.goToMoveOfTheLabel()
        self.updateSlidersPositions()

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
        ## The move for the label
        self.__move = move
        ## The dictionary of all the motors
        self.__motors = motors
        self.setText(text)

    def goToMoveOfTheLabel(self):
        """
        Handles the event when the move lable is double clicked
        :return: No return1
        """
        self.__move.goToMove()


    def getMove(self):
        """
        Accessor of the move of the label
        :return: the move object
        """
        return self.__move

# Class for a sequence of moves
class Sequence(QListWidgetItem):
    """
    Sequence is a series of moves that will be executed in a specific order
    """
    def __init__(self,motors = {}, name=""):
        QListWidgetItem.__init__(self)
        # QListWidgetItem method for setting the text of the item
        self.setText(name)
        ## A list of moves
        self.__moves = []
        ## The name of the sequence
        self.__name = name
        ## A dictionary of all the motors
        self.__motors = motors

    def setName(self, name):
        """
        Sets the name of the sequence
        :param name: The name
        :return: No return
        """
        self.setText(name)
        self.__name = name

    def getName(self):
        """
        Accesor for the sequence name
        :return: The name of the sequence
        """
        return self.__name

    def addMove(self, newMove):
        """
        Adds a move to the list in the sequence
        :param newMove: The move to add to the list
        :return: No return
        """
        self.__moves.append(newMove)

    def getNumberofMoves(self):
        """
        :return: The number of moves in the sequence
        """
        return len(self.__moves)

    def getMoves(self):
        """
        Acessor of the moves of the sequence
        :return: The moves of the sequence
        """
        return self.__moves

    def deleteMove(self, move):
        """
        Delete a specific move of the sequence
        :param move: the move to be deleted
        :return: No return
        """
        self.__moves.remove(move)

# Class for a move of a sequence
class Move:
    """
    A move contains all the position of all the motors for a specific point in space
    """
    def __init__(self, motors = {}):
        ## A dictionary of all motors
        self.__motors = motors
        ## To store the different positions of the move
        self.__movePositions = dict()
        ## State of the move (modified or new)
        self.isNew = True
        # Initialize move positions to an invalid position (-1)
        for motor in self.__motors:
            self.__movePositions[motor] = -1

    def setMotorPosition(self, motorName, position):
        """
        Setter of the position of a motor in the move
        :param motorName: The name of the motor we want to set the positio
        :param position: The position of the motor
        :return: Return None if succesful and an error string if not
        """
        if motorName in self.__motors:
            self.__movePositions[motorName] = position
            return None
        else:
            return "There's no motor named that way"

    def getMotorPosition(self, motorName):
        """
        Accessor for the positions in the move
        :param motorName: The name of the motor
        :return: Return the position if succesful and an error string if not
        """
        if motorName in self.__movePositions:
            return self.__movePositions[motorName]
        else:
            return "There's no motor named that way"

    def getMovePositions(self):
        return self.__movePositions

    def goToMove(self):
        for motor in self.__motors:
            self.__motors[motor].setGoalPosition(self.getMotorPosition(motor))

class Motor:
    """
    Class for a motor which has a position, a name and a status
    """
    def __init__(self, mainWindow=None, name="", goalPosition=0, status=False):
        """
        Initialization
        :param mainWindow: The main window of the ui
        :param name: The name of the motor
        :param pos: The position of the motor
        :param status: the status of the motor
        """
        ## The main window of the ui
        self.__name = name
        ## The goal position of the motor
        self.__goalPosition = goalPosition
        ## The current position of the motor
        self.__currentPosition = 0
        ## The status of the motor
        self.__status = status
        ## The main window of the ui
        self.__window = mainWindow
        self.mu = QMutex()

    def setGoalPosition(self, pos):
        """
        Setter of the goal positon
        :param pos: the position
        :return: No return
        """
        self.mu.lock()
        self.__goalPosition=pos
        self.mu.unlock()
        print("%s: %d" % (self.__name, pos))
        self.__window.sendMessage('a')

    def getGoalPosition(self):
        """
        Accessor of the goal position
        :return: The goal position of the motor
        """
        self.mu.lock()
        pos = self.__goalPosition
        self.mu.unlock()
        return pos

    def setCurrentPosition(self, pos):
        """
        Setter of the current position
        :return: No return
        """
        self.mu.lock()
        self.__currentPosition = pos
        self.mu.unlock()

    def getCurrentPosition(self):
        """
        Accessor of the current position
        :return: The current position of the motor
        """
        self.mu.lock()
        pos = self.__currentPosition
        self.mu.unlock()
        return pos

    def setName(self, name):
        """
        Setter of the name of the motor
        :param name: The name of the motor
        :return: No return
        """
        self.__name = name

    def getName(self):
        """
        Accessor of the name
        :return: The name of the motor
        """
        return self.__name

    def setStatus(self, status):
        """
        Setter of the status of the motor
        :param status: The status
        :return: No return
        """
        self.__status = status

    def isEnabled(self):
        """
        Accessor of the status
        :return: The status
        """
        return self.__status


class MainWindow(QMainWindow):
    """
    Main window class
    """
    def __init__(self, app):
        """
        MainWindow initialization
        """
        super(MainWindow, self).__init__()
        ## app
        self.app = app
        ## ui object
        self.ui = QUiLoader().load("mainwindow.ui")
        self.ui.show()
        self.ui.setWindowTitle("RoboAide")
        self.setMinimumHeight(100)
        self.setMinimumWidth(250)
        # self.setMaximumHeight(200)
        # self.setMaximumWidth(800)
        self.setIcon()
        self.msgMu = QMutex()

        self.numberOfMotors = 6
        self.s, self.messageSize = makeStruct()

        # Connect button signals
        self.ui.calibrateVerticalAxisButton.clicked.connect(self.calibrateVerticalAxis)

        self.ports_list = scanAvailablePorts()
        self.populatePortsList()

        # ---------------
        ## Dictionnary of all motor objects
        self.dictMot = dict()
        for i in range(1, self.numberOfMotors+1):
            mot = Motor(self, "motor" + str(i))
            self.dictMot[mot.getName()] = mot
        # ---------------

        ## List of drawers
        self.drawersList = []
        for i in range(3):
            self.drawersList.append(Drawer(self, "drawer" + str(i+1)))

        self.updateSliderPositions()

        ## ListOfSequencesHandler object
        self.listOfSequencesHandler = ListOfSequencesHandler(self, self.dictMot)

        # load the last save
        loadSequences(self.listOfSequencesHandler,self.dictMot)

        # Connect the slider signals
        self.ui.slider_mot1.sliderMoved.connect(
            lambda: self.dictMot["motor1"].setGoalPosition(self.ui.slider_mot1.value()))
        self.ui.slider_mot2.sliderMoved.connect(
            lambda: self.dictMot["motor2"].setGoalPosition(self.ui.slider_mot2.value()))
        self.ui.slider_mot3.sliderMoved.connect(
            lambda: self.dictMot["motor3"].setGoalPosition(self.ui.slider_mot3.value()))
        self.ui.slider_mot4.sliderMoved.connect(
            lambda: self.dictMot["motor4"].setGoalPosition(self.ui.slider_mot4.value()))
        self.ui.slider_mot5.sliderMoved.connect(
            lambda: self.dictMot["motor5"].setGoalPosition(self.ui.slider_mot5.value()))
        self.ui.slider_mot6.sliderMoved.connect(
            lambda: self.dictMot["motor6"].setGoalPosition(self.ui.slider_mot6.value()))

        # Connect button signals
        self.ui.calibrateVerticalAxisButton.clicked.connect(self.calibrateVerticalAxis)

        # Connect drawer buttons signals
        self.ui.drawer1Open.clicked.connect(self.drawersList[0].open)
        self.ui.drawer2Open.clicked.connect(self.drawersList[1].open)
        self.ui.drawer3Open.clicked.connect(self.drawersList[2].open)
        self.ui.drawer1Close.clicked.connect(self.drawersList[0].close)
        self.ui.drawer2Close.clicked.connect(self.drawersList[1].close)
        self.ui.drawer3Close.clicked.connect(self.drawersList[2].close)

        # Connect the tab changed with updating the sliders
        self.ui.tabWidget.currentChanged.connect(self.updateSliderPositions)

        # Serial communication
        ## Outgoing message deque
        self.msgDeque = deque(maxlen=3)
        ## Stop indicator for the motors
        self.shouldStop = False
        ## Message reception QThread object
        self.msgReception = MessageReception(self)
        ## Message transmission QThread object
        self.msgTransmission = MessageTransmission(self)
        self.app.aboutToQuit.connect(self.msgReception.stop)
        self.app.aboutToQuit.connect(self.msgTransmission.stop)
        self.comm = None
        self.serialConnected = None
        try:
            with open('SavePort.json') as save:
                savedPort = json.load(save)
                for index in range(1,len(self.ports_list)):
                    if self.ports_list[index].device==savedPort:
                        self.ui.portselection.setCurrentIndex(index)
                        self.connect_port(savedPort)
                    else:
                        print("The last port is not available")
        except FileNotFoundError:
            print("SavePort file not found")
        self.ui.portselection.currentIndexChanged.connect(self.connect_port)

    def connect_port(self, lastPort=None):
        """
        Connect the selected port of the controller
        :param: lastPort: name of the port that was last used
        :return: None
        """
        if isinstance(lastPort, str):
            commPort = lastPort
        else:
            commPort = self.ui.portselection.currentText()
        self.comm, self.serialConnected = initSerialConnection(commPort)
        if self.comm is not None:
            self.app.aboutToQuit.connect(self.comm.close)
            self.msgReception.start()
            self.msgTransmission.start()
            self.sendMessage('s')

    def setIcon(self):
        """
        Set main window icon
        :return: None
        """
        appIcon = QIcon(icon)
        self.ui.setWindowIcon(appIcon)

    def updateSliderPositions(self, index = 0):
        """
        Update motor slider positions
        :return: None
        """
        if index == 0:
            print("Updating motor slider positions")
            self.ui.slider_mot1.setValue(self.dictMot["motor1"].getCurrentPosition())
            self.ui.slider_mot2.setValue(self.dictMot["motor2"].getCurrentPosition())
            self.ui.slider_mot3.setValue(self.dictMot["motor3"].getCurrentPosition())
            self.ui.slider_mot4.setValue(self.dictMot["motor4"].getCurrentPosition())
            self.ui.slider_mot5.setValue(self.dictMot["motor5"].getCurrentPosition())
            self.ui.slider_mot6.setValue(self.dictMot["motor6"].getCurrentPosition())
            print("Finished initializing slider positions")

    def populatePortsList(self):
        """
        Populate the available serial ports in the drop down menu
        :return: None
        """
        print("Scanning and populating list of available serial ports")
        for index in range(len(self.ports_list)):
            result = isinstance(self.ports_list[index], str)
            if not result:
                self.ui.portselection.addItem(self.ports_list[index].device)
            else:
                self.ui.portselection.addItem(self.ports_list[index])

    def sendMessage(self, mode):
        """
        Package message and send on communication port
        :param mode: mode in which the message should be interpreted by the controller
        :return: None
        """
        if self.serialConnected:
            values = (mode.encode(),
                      self.dictMot["motor1"].getGoalPosition(),
                      self.dictMot["motor2"].getGoalPosition(),
                      self.dictMot["motor3"].getGoalPosition(),
                      self.dictMot["motor4"].getGoalPosition(),
                      self.dictMot["motor5"].getGoalPosition(),
                      self.dictMot["motor6"].getGoalPosition(),
                      self.shouldStop,
                      self.drawersList[0].getState(),
                      self.drawersList[1].getState(),
                      self.drawersList[2].getState(),
                      b'\0')
            print("Outgoing: ", end='')
            print(values)
            packed_data = self.s.pack(*values)
            self.msgMu.lock()
            self.msgDeque.append(packed_data)
            self.msgMu.unlock()
        else:
            print("Error sending message, serial not connected")

    def calibrateVerticalAxis(self):
        """
        Trigger vertical axis calibration
        :return: None
        """
        print("Calibrating vertical axis")
        self.sendMessage('c')

    def stopMotors(self):
        """
        Signal all motors to stop and empty message deque
        """
        self.shouldStop = True
        self.msgDeque.clear()
        self.sendMessage('a')


def makeStruct():
    """
    Make the struct and return it along with it's size in bytes
    :return: struct object, byte size of the struct
    """
    ## Define struct format for communicating messages
    # c: mode
    #       'a' -> absolute (send an absolute position between 0 and 100)
    #       'i' -> incremental (move from the current position from a certain increment)
    #       's' -> status (with this mode, the rest of the message is ignored. It's purpose is only for the controller to send it's status)
    #       'c' -> calibrate vertical axis (rest of the message is ignored)
    # c: operation mode
    # 6H: position of all motors
    # ?: stop indicator for all motors
    # 3?: open/close drawers (True = open, False = close)
    # c: end-of-message character
    #TODO: try adding little endian (<) to struct definition
    structDefinition = 'c6H?3?c'
    s = struct.Struct(structDefinition)
    return s, struct.calcsize(structDefinition)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(app)
    app.exec_()
    sys.exit()