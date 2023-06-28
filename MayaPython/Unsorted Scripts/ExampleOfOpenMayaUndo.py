import maya.cmds as cmds

class ExampleClass(object):
    def __init__(self):
        super(ExampleClass, self).__init__()
        self.redo_text = ''
        self.undo_text = ''

        # run the command that will call the doIt, redoIt, undoIt functions at the appropriate times
        cmds.runUndoablePython(self)

    def doIt(self):
        # gather / store data to use during redo / undo, eg doIt is only called once, then redo/undo happen while
        # moving backwards/forward the undo stack... optionally you can do this work in your __init__ before
        # you call the cmd.runUndoablePython
        print('Preparing World!')
        self.redo_text = 'Hello World!'
        self.undo_text = 'Goodbye World!'

    def redoIt(self):
        # apply your changes here, usually something like MPlug.setValue, MFkSkinCluster.setWeights, etc
        print(self.redo_text)

    def undoIt(self):
        # undo the changes to restore the previous state
        print(self.undo_text)

# initializing the class will also run the command
ExampleClass()