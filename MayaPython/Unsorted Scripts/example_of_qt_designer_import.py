from PySide2 import QtCore, QtWidgets, QtUiTools

from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui


class TestQtUi(QtWidgets.QWidget):

    def __init__(self, ):
        ui = "/mnt/user-share/julianbeiboer/PythonTools/assetChecker.ui"
        file = QtCore.QFile(ui)
        super(TestQtUi, self).__init__()
        try:
            file.open(QtCore.QFile.ReadOnly)
            loader = QtUiTools.QUiLoader()
            ui = loader.load(file, wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget))
        finally:
            file.close()

        ui.show()