from PySide import QtCore

"""Source: http://www.commandprompt.com/community/pyqt/x5255.htm
"""

class ConnectionBox(QtCore.QObject):

    def __init__(self, *args):
        apply(QtCore.QObject.__init__,(self,)+args)
        self.signalArrived = 0
        self.args = []

    def slotSlot(self, *args):
        self.signalArrived = 1
        self.args = args

    def assertSignalArrived(self, signal=None):
        if  not self.signalArrived:
            raise AssertionError, ("signal %s did not arrive" % signal)

    def assertNumberOfArguments(self, number):
        if number <> len(self.args):
            raise AssertionError, \
                  ("Signal generated %i arguments, but %i were expected" %
                                    (len(self.args), number))

    def assertArgumentTypes(self, *args):
        if len(args) <> len(self.args):
            raise AssertionError, \
         ("Signal generated %i arguments, but %i were given to this function" %
                                 (len(self.args), len(args)))
        for i in range(len(args)):
            if type(self.args[i]) != args[i]:
                raise AssertionError, \
                      ( "Arguments don't match: %s received, should be %s." %
                                      (type(self.args[i]), args[i]))