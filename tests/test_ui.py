import unittest
import sys
import time
import json

from ui import RoboAide
from ui.Drawer import Drawer
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QComboBox

# based on : https://bitbucket.org/jmcgeheeiv/pyqttestexample/src/default/src/

# Start a Qt App to create a window
app = QApplication(sys.argv)

class TestMove(unittest.TestCase):
    def setUp(self):
        self.testWindow = RoboAide.MainWindow(app)
        self.testWindow.serialConnected = True
        self.testWindow.comm = DummyComm()
        self.testMove = RoboAide.Move(self.testWindow.dictMot)

    def test_get_position(self):
        for motor in self.testWindow.dictMot:
            self.assertEqual(self.testMove.getMotorPosition(motor), -1)

    def test_set_position(self):
        for motor in self.testWindow.dictMot:
           self.testMove.setMotorPosition(motor,10)

        for motor in self.testWindow.dictMot:
            self.assertEqual(self.testMove.getMotorPosition(motor), 10)

    def test_wrong_motor_name(self):
        self.assertEqual(self.testMove.getMotorPosition("moteur 1"), "There's no motor named that way")

class TestMotor(unittest.TestCase):
    def setUp(self):
        self.testWindow = RoboAide.MainWindow(app)
        self.testWindow.serialConnected = True
        self.testWindow.comm = DummyComm()
        # self.testWindow.msgTransmission.start()
        self.testMotor = RoboAide.Motor(self.testWindow, "testMotor", 500, True)

    def test_get_position(self):
        self.assertEqual(self.testMotor.getGoalPosition(), 500)

    def test_is_enabled(self):
        self.assertTrue(self.testMotor.isEnabled(),"Motor is not enabled")

    def test_set_status(self):
        self.testMotor.setStatus(False)
        self.assertFalse(self.testMotor.isEnabled(),"Motor is enabled, set status doesn't work")

    def test_get_name(self):
        self.assertEqual(self.testMotor.getName(),"testMotor")

    def test_set_name(self):
        self.testMotor.setName("Nom")
        self.assertEqual(self.testMotor.getName(),"Nom")

class TestSequence(unittest.TestCase):
    def setUp(self):
        self.testWindow = RoboAide.MainWindow(app)
        self.testWindow.serialConnected = True
        self.testWindow.comm = DummyComm()
        self.testSequence = RoboAide.Sequence(self.testWindow.dictMot,"testSequence")

    def test_getName(self):
        self.assertEqual(self.testSequence.getName(),"testSequence")

    def test_setName(self):
        self.testSequence.setName("pogo")
        self.assertEqual(self.testSequence.getName(),"pogo")

    def test_getNumberOfMoves(self):
        self.assertEqual(self.testSequence.getNumberofMoves(), 0)

    def test_addMove(self):
        self.testSequence.addMove(RoboAide.Move(self.testWindow.dictMot))
        self.assertEqual(self.testSequence.getNumberofMoves(), 1)

    def test_getMoves(self):
        self.testSequence.addMove(RoboAide.Move(self.testWindow.dictMot))
        self.testSequence.addMove(RoboAide.Move(self.testWindow.dictMot))
        self.assertEqual(self.testSequence.getNumberofMoves(), 2)

    def test_deleteMove(self):
        move = RoboAide.Move(self.testWindow.dictMot)
        self.testSequence.addMove(move)
        self.testSequence.deleteMove(move)
        self.assertEqual(self.testSequence.getNumberofMoves(), 0)

class TestCreateSequenceWindow(unittest.TestCase):
    def setUp(self):
        self.testWindow = RoboAide.MainWindow(app)
        self.testWindow.serialConnected = True
        self.testWindow.comm = DummyComm()
        self.testSequenceWindow = RoboAide.CreateSequenceWindow(self.testWindow.dictMot,
                                                                self.testWindow.listOfSequencesHandler,
                                                                RoboAide.Sequence(self.testWindow.dictMot))

    def test_addMovetoSequence(self):

        for counterMotors in range(len(self.testWindow.dictMot)):
            self.testSequenceWindow.listOfSliders[counterMotors].setValue(40)

        self.testSequenceWindow.addMovetoSequence()

        self.assertEqual(self.testSequenceWindow.getSequence().getNumberofMoves(),1)


    def test_updateSlidersPositions(self):
        for motor in self.testWindow.dictMot:
            self.testWindow.dictMot[motor].setGoalPosition(30)

        self.testSequenceWindow.updateSlidersPositions()

        for counterMotors in range(len(self.testWindow.dictMot)):
            self.assertEqual(self.testSequenceWindow.listOfSliders[counterMotors].value(),30)

    def test_deleteMove(self):
        for counterMotors in range(len(self.testWindow.dictMot)):
            self.testSequenceWindow.listOfSliders[counterMotors].setValue(40)

        self.testSequenceWindow.addMovetoSequence()

        self.assertEqual(self.testSequenceWindow.getSequence().getNumberofMoves(),1)

        self.testSequenceWindow.deleteMove(self.testSequenceWindow.getListofMoveLabels().item(0))

        self.assertEqual(self.testSequenceWindow.getSequence().getNumberofMoves(), 0)

    def test_setName(self):
        self.testSequenceWindow.setName("bob")
        self.assertEqual(self.testSequenceWindow.getSequence().getName(), "bob")

    def test_addSequenceToList(self):
        row = self.testWindow.ui.listOfSequences.count()

        for counterMotors in range(len(self.testWindow.dictMot)):
            self.testSequenceWindow.listOfSliders[counterMotors].setValue(40)
        self.testSequenceWindow.nameEntry.setText("bob")
        self.testSequenceWindow.addMovetoSequence()

        self.testSequenceWindow.addSequenceToList()

        self.assertEqual(self.testWindow.ui.listOfSequences.count(), row+1)

        foundSequenceInSaveFile = False
        try:
            with open('SaveSequence.json') as save:
                savedListOfSequences = json.load(save)
                for sequence in savedListOfSequences:
                    if self.testSequenceWindow.getSequence().getName() in sequence:
                        foundSequenceInSaveFile = True

            self.assertTrue(foundSequenceInSaveFile)
        except FileNotFoundError:
            print("No file saved")

        self.testWindow.ui.listOfSequences.setCurrentItem(self.testSequenceWindow.getSequence())

        self.testWindow.listOfSequencesHandler.removeSelectedItem()

        self.assertEqual(self.testWindow.ui.listOfSequences.count(), row)

class TestListOfSequencesHandler(unittest.TestCase):
    def setUp(self):
        self.testWindow = RoboAide.MainWindow(app)
        self.testWindow.serialConnected = True
        self.testWindow.comm = DummyComm()
        self.testListofSequencesHandler = RoboAide.ListOfSequencesHandler(self.testWindow,
                                                                          self.testWindow.dictMot)
        self.testSequence = RoboAide.Sequence(self.testWindow.dictMot, "testSequence")
        self.testMove = RoboAide.Move(self.testWindow.dictMot)
        for motor in self.testWindow.dictMot:
           self.testMove.setMotorPosition(motor,10)
        self.testSequence.addMove(self.testMove)

    def test_addItem(self):
        row = self.testWindow.ui.listOfSequences.count()
        self.testListofSequencesHandler.addItem(self.testSequence)
        self.assertEqual(self.testWindow.ui.listOfSequences.count(), row + 1)


    def test_playSequence(self):
        row = self.testWindow.ui.listOfSequences.count()
        self.testListofSequencesHandler.addItem(self.testSequence)
        self.testWindow.ui.listOfSequences.setCurrentItem(self.testWindow.ui.listOfSequences.item(row))
        self.assertTrue(self.testWindow.ui.listOfSequences.item(row).isSelected())
        self.testListofSequencesHandler.playSequence()
        time.sleep(1)
        self.testWindow.shouldStop = True
        for motor in self.testWindow.dictMot:
            self.assertEqual(self.testWindow.dictMot[motor].getGoalPosition(),10)




class TestMainWindow(unittest.TestCase):
    def setUp(self):
        self.testWindow = RoboAide.MainWindow(app)
        self.testWindow.serialConnected = True

    def test_sendMessage(self):
        # This test needs to be updated everytime the struct is modified.
        # More specifically, every instance of expectedResult needs to be updated.
        # send absolute move message for every motor
        i = 0
        valueList = [0, 0, 0, 0, 0, 0]
        for motor in self.testWindow.dictMot:
            value = 100 * (i+1)
            valueList[i] = value
            print(*valueList)
            self.testWindow.dictMot[motor].setGoalPosition(value)  # Every time a goal is set, a message is sent
            expectedResult = self.testWindow.s.pack(b'a', *valueList, False, False, False, False, b'\0')
            self.assertEqual(self.testWindow.msgDeque[-1], expectedResult)
            i += 1

        # send status message
        self.testWindow.sendMessage('s')
        expectedResult = self.testWindow.s.pack(b's', *valueList, False, False, False, False, b'\0')
        self.assertEqual(self.testWindow.msgDeque[-1], expectedResult)

        # send calibration message
        self.testWindow.sendMessage('c')
        expectedResult = self.testWindow.s.pack(b'c', *valueList, False, False, False, False, b'\0')
        self.assertEqual(self.testWindow.msgDeque[-1], expectedResult)

    def test_populatePortsList(self):
        dummyPortsList = ["COM1", "COM2"]
        self.testWindow.ports_list = dummyPortsList
        self.testWindow.ui.portselection = QComboBox()
        self.testWindow.populatePortsList()
        AllItems = [self.testWindow.ui.portselection.itemText(i) for i in range(self.testWindow.ui.portselection.count())]
        self.assertEqual(dummyPortsList, AllItems)


class TestMessageReception(unittest.TestCase):
    def setUp(self):
        self.testWindow = RoboAide.MainWindow(app)
        self.testWindow.serialConnected = True
        self.testWindow.comm = DummyComm()
        self.testWindow.msgReception.start()

    def testRun(self):
        """
        Test for reading incoming message and updating the motors' current posisition
        """
        self.motorValues = [100, 200, 300, 400, 500, 600]
        message = self.testWindow.s.pack(b'a', *self.motorValues, False, False, False, False, b'\0')
        self.testWindow.comm.loadMessage(message)
        time.sleep(1)
        i = 0
        for motor in self.testWindow.dictMot:
            self.assertEqual(self.testWindow.dictMot[motor].getCurrentPosition(), self.motorValues[i])
            i += 1

    def tearDown(self):
        self.testWindow.msgReception.stop()
        while self.testWindow.msgReception.isRunning():  # Make sure the thread has exited before continuing tests
            pass

class TestMessageTransmission(unittest.TestCase):
    def setUp(self):
        self.testWindow = RoboAide.MainWindow(app)
        self.testWindow.serialConnected = True
        self.testWindow.comm = DummyComm()
        self.testWindow.msgTransmission.start()

    def testRun(self):
        # Add a message to the msgDeque
        motorValues = [100, 200, 300, 400, 500, 600]
        message = self.testWindow.s.pack(b'a', *motorValues, False, False, False, False, b'\0')
        self.testWindow.msgDeque.append(message)
        time.sleep(1)
        self.assertEqual(self.testWindow.comm.lastSentMessage, message)

    def tearDown(self):
        self.testWindow.msgTransmission.stop()
        while self.testWindow.msgTransmission.isRunning():  # Make sure the thread has exited before continuing tests
            pass


class TestDrawers(unittest.TestCase):
    def setUp(self):
        self.testWindow = RoboAide.MainWindow(app)
        self.testDrawer = Drawer(self.testWindow, "test")

    def testOpen(self):
        self.testDrawer.open()
        self.assertEqual(self.testDrawer.state, True)

    def testClose(self):
        self.testDrawer.close()
        self.assertEqual(self.testDrawer.state, False)

    def testSetState(self):
        self.testDrawer.setState(True)
        self.assertEqual(self.testDrawer.state, True)
        self.testDrawer.setState(False)
        self.assertEqual(self.testDrawer.state, False)

    def testGetState(self):
        self.testDrawer.setState(True)
        self.assertEqual(self.testDrawer.getState(), True)
        self.testDrawer.setState(False)
        self.assertEqual(self.testDrawer.getState(), False)


class DummyComm:
    def __init__(self, message=""):
        self.message = message
        self.lastSentMessage = None

    def loadMessage(self, message):
        self.message = message

    def read(self, messageSize):
        timeout = time.time() + 0.1
        while len(self.message) != messageSize and time.time() < timeout:
            pass
        tempMsg = self.message
        self.message = ""
        return tempMsg

    def write(self, message):
        self.lastSentMessage = message

    def close(self):
        pass


if __name__ == '__main__':
    unittest.main()
