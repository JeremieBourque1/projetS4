import unittest
import sys
import os

from ui import RoboAide
from PySide2.QtWidgets import QApplication
from PySide2.QtTest import QTest
from PySide2.QtCore import Qt

# based on : https://bitbucket.org/jmcgeheeiv/pyqttestexample/src/default/src/

# Start a Qt App to create a window
app = QApplication(sys.argv)

# Change directory to be able to load the .ui
os.chdir("..")

class TestMove(unittest.TestCase):
    def setUp(self):
        self.testWindow = RoboAide.MainWindow()
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
        self.testWindow = RoboAide.MainWindow()
        self.testMotor = RoboAide.Motor(self.testWindow, "testMotor", 500, True)

    def test_get_position(self):
        self.assertEqual(self.testMotor.getPosition(),500)

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

if __name__ == '__main__':
    unittest.main()
