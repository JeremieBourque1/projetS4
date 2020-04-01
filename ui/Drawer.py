class Drawer:
    """
    Class for drawers
    """
    def __init__(self, mainwindow, name=""):
        # True = open
        # False = closed
        self.mainwindow = mainwindow
        self.name = name
        self.state = False

    def open(self):
        """
        Send command to open the drawer
        """
        self.state = True
        self.mainwindow.sendMessage('a')
        print("opening " + self.name)

    def close(self):
        """
        Send command to close the drawer
        """
        self.state = False
        self.mainwindow.sendMessage('a')
        print("closing " + self.name)

    def getState(self):
        """
        Getter for the state of the drawer (open/closed)
        """
        return self.state

    def setState(self, state):
        """
        Setter for the state of the drawer (open/closed)
        """
        self.state = state
