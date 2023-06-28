import functools
from maya import cmds
from maya.api import OpenMaya


class RunUndoablePython(OpenMaya.MPxCommand):
    call_class = None
    kCommandName = 'runUndoablePython'

    def __init__(self):
        """
        Allows you to run cmds.runUndoablePython(self) during the __init__ of your custom python class, which will
        cause maya to see it as an undoable command.  Then this class will call into the doIt, redoIt, and undoIt of
        your class.  This helps prevent the need to create a bunch of random plug-ins for various operations.
        """
        super(RunUndoablePython, self).__init__()
        self.py_class = None

    def isUndoable(self):
        """
        Make sure we support undoing.
        """
        return True

    def doIt(self, args):
        """
        Your doIt should do the bulk of the work, eg calculating values to apply during the redoIt/undoIt call.  You
        do not have to specify a doIt method if you already had the information on self.py_class and are ready to apply.
        """
        self.py_class = self.call_class
        if hasattr(self.py_class, 'doIt'):
            result = self.py_class.doIt()
            if result is not None:
                self.setResult(result)
        self.redoIt()

    def redoIt(self):
        """
        Just calls your class's required redoIt method.  Although this can use setResult, normally this is not needed.
        """
        result = self.py_class.redoIt()
        if result is not None:
            self.setResult(result)

    def undoIt(self):
        """
        Just calls your class's required undoIt.
        """
        # the undo queue can get into a bad state, so this is normally disabled, might want to add an option to skip
        state = cmds.undoInfo(query=True, state=True)
        if state:
            cmds.undoInfo(stateWithoutFlush=False)
        try:
            result = self.py_class.undoIt()
            if result is not None:
                self.setResult(result)
        finally:
            if state:
                cmds.undoInfo(stateWithoutFlush=True)

    @classmethod
    def wrap_command(cls):
        """
        In order to bypass the normal argument required for commands due to trying to be compatible with MEL, we have
        to wrap the created cmds.runUndoablePython so the class can be passed.
        """
        cmd_func = getattr(cmds, cls.kCommandName)

        @functools.wraps(cmd_func)
        def wrapped(py_class):
            # make sure we store the class so it wont go out of scope and then call it
            cls.call_class = py_class
            cmds.undoInfo(openChunk=True, chunkName=cls.kCommandName)
            try:
                return cmd_func()
            finally:
                cmds.undoInfo(closeChunk=True)

        # now overwrite the one in cmds with this new wrapped version
        wrapped.__wrapped__ = cmd_func
        setattr(cmds, cls.kCommandName, wrapped)


def maya_useNewAPI():
    pass


def creator():
    return RunUndoablePython()


def initializePlugin(m_object):
    m_plugin = OpenMaya.MFnPlugin(m_object)
    try:
        # let maya create the command, and then replace it with a wrapped version that can accept a python class
        m_plugin.registerCommand(RunUndoablePython.kCommandName, creator)
        RunUndoablePython.wrap_command()
    except:
        raise Exception('Unable to initialize: {}'.format(RunUndoablePython.kCommandName))


def uninitializePlugin(m_object):
    m_plugin = OpenMaya.MFnPlugin(m_object)
    try:
        m_plugin.deregisterCommand(RunUndoablePython.kCommandName)
    except:
        raise Exception('Unable to uninitialize: {}'.format(RunUndoablePython.kCommandName))