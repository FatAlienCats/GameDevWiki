import os
import logging
from Qt import QtWidgets, QtGui, QtCompat, QtCore
from maya import OpenMayaUI as omu

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
logger = logging.getLogger(__name__)


class TestShapesWidget(MayaQWidgetDockableMixin, QtWidgets.QWidget):

    ui_file = "assetChecker.ui"
    _instance = None
    color_palette = None
    line = None
    flow_layout = None
    @classmethod
    def showWindow(cls):
        if not cls._instance:
            cls._instance = cls(parent=getMayaMainWindow())
        cls._instance.show()
        cls._instance.raise_()
        cls._instance.setDefaultPosition()
        return cls._instance

    def __init__(self, *args, **kwargs):
        super(TestShapesWidget, self).__init__(*args, **kwargs)
        QtCompat.loadUi(self._getUiFilePath(), self)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setWindowTitle("Control Shapes Tools")
        self._buildUI()
        #self._buildConnections()

    def _buildUI(self):
        pass
    def setDefaultPosition(self):
        self.move(100, 100)

    def _getUiFilePath(self):
        this_dir = os.path.dirname(__file__)
        return os.path.join(this_dir, self.UI_FILE)


def getMayaMainWindow():
    pointer = omu.MQtUtil.mainWindow()
    return QtCompat.wrapInstance(int(pointer), QtWidgets.QWidget)

