from PySide2.QtCore import QThread
import serial
import serial.tools.list_ports
import struct

class MessageReception(QThread):
    """
    Class for a thread that handles incoming serial messages
    """
    def __init__(self, mainWindow):
        super(MessageReception, self).__init__()
        self.mainWindow = mainWindow
        self.shouldRun = True
        self.counter = 0
        self.firstMessage = True

    def run(self):
        print("Message Reception thread started")
        while self.shouldRun:
            message = self.mainWindow.comm.read(self.mainWindow.messageSize)  # TODO: Find out why an extra byte is received (only happens with openCr)
            if len(message) == self.mainWindow.messageSize:
                print("message received")
                unpacked_msg = self.mainWindow.s.unpack(message)  # Unpack message
                print(str(self.counter) + ": ", end='')
                print(unpacked_msg)
                self.counter += 1
                self.setMotorCurrentPosition(unpacked_msg)
        print("done")

    def stop(self):
        self.shouldRun = False
        print("Stopping Message Reception thread")

    def setMotorCurrentPosition(self, msg):
        for i in range(self.mainWindow.numberOfMotors):
            self.mainWindow.dictMot["motor" + str(i+1)].setCurrentPosition(msg[i+1])
        if self.firstMessage:
            self.mainWindow.updateSliderPositions()
            self.firstMessage = False


class MessageTransmission(QThread):
    """
    Class for a thread that handles outgoing serial messages
    """
    def __init__(self, mainWindow):
        super(MessageTransmission, self).__init__()
        self.mainWindow = mainWindow
        self.shouldRun = True
        self.counter = 0
        self.firstMessage = True

    def run(self):
        print("Message Transmission thread started")
        while self.shouldRun:
            self.msleep(500)
            if len(self.mainWindow.msgDeque) > 0:
                self.mainWindow.msgMu.lock()
                print("deque length: %d" % len(self.mainWindow.msgDeque))
                self.mainWindow.comm.write(self.mainWindow.msgDeque.popleft())
                self.mainWindow.msgMu.unlock()

    def stop(self):
        self.shouldRun = False
        print("Stopping Message Transmission thread")


def initSerialConnection(port):
    """
    Initialize serial communication with a specified port
    :param port: serial port name
    :return: serial object and bool indicating if connection was successful
    """
    try:
        ser = serial.Serial(port, 9600, timeout=0.1)
        print("Connected to %s" % port)
        connected = True
    except serial.serialutil.SerialException:
        print("Failed to connect to %s." % port)
        ser = None
        connected = False
    return ser, connected

def scanAvailablePorts():
    ports = serial.tools.list_ports.comports()
    ports_list = ['Select a communication port']
    ports_list.extend(ports)
    return ports_list