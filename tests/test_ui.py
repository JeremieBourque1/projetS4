import unittest
import sys
import time

from ui import RoboAide
from ui.Communication import initSerialConnection
from PySide2.QtWidgets import QApplication

# based on : https://bitbucket.org/jmcgeheeiv/pyqttestexample/src/default/src/

# Start a Qt App to create a window
app = QApplication(sys.argv)


class TestMove(unittest.TestCase):
    def setUp(self):
        self.testComm, serialConnected = RoboAide.initSerialConnection('COM3')
        self.testWindow = RoboAide.MainWindow(app)
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
            expectedResult = self.testWindow.s.pack(b'a', *valueList, b'\0')
            self.assertEqual(self.testWindow.msgDeque[-1], expectedResult)
            i += 1

        # send status message
        self.testWindow.sendMessage('s')
        expectedResult = self.testWindow.s.pack(b's', *valueList, b'\0')
        self.assertEqual(self.testWindow.msgDeque[-1], expectedResult)

        # send calibration message
        self.testWindow.sendMessage('c')
        expectedResult = self.testWindow.s.pack(b'c', *valueList, b'\0')
        self.assertEqual(self.testWindow.msgDeque[-1], expectedResult)

class TestMessageReception(unittest.TestCase):
    def setUp(self):
        self.testWindow = RoboAide.MainWindow(app)
        self.testWindow.serialConnected = True
        self.testWindow.comm = dummyComm()
        self.testWindow.msgReception.start()

    def testRun(self):
        """
        Test for reading incoming message and updating the motors' current posisition
        """
        self.motorValues = [100, 200, 300, 400, 500, 600]
        message = self.testWindow.s.pack(b'a', *self.motorValues, b'\0')
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


class dummyComm:
    def __init__(self, message=""):
        self.message = message

    def loadMessage(self, message):
        self.message = message

    def read(self, messageSize):
        timeout = time.time() + 0.1
        while len(self.message) != messageSize and time.time() < timeout:
            pass
        tempMsg = self.message
        self.message = ""
        return tempMsg


if __name__ == '__main__':
    unittest.main()
