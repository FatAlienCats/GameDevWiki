from PySide2 import QtCore, QtWidgets, QtUiTools

from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm
UI_NAME = "TemplateUI"

import logging
logging.basicConfig()
logger = logging.getLogger('uiTemplate')
logger.setLevel(logging.DEBUG)


class TemplateUI(QtWidgets.QMainWindow):
    ui = None
    assets_to_update = None

    def __init__(self, assets_to_update):
        ui_file = "/mnt/user-share/julianbeiboer/UI/assetChecker.ui"  #file path to qt designer file
        file = QtCore.QFile(ui_file)
        self.assets_to_update = assets_to_update

        super(TemplateUI, self).__init__()
        try:
            pm.deleteUI(UI_NAME)

        except:
            logger.debug('No previous UI called {} exists'.format(UI_NAME))

        try:
            # Load qt designer file
            file.open(QtCore.QFile.ReadOnly)
            loader = QtUiTools.QUiLoader()
            self.ui = loader.load(file, wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget))

        finally:
            file.close()

        # Get a pointer to the Maya main window
        maya_main_window_ptr = omui.MQtUtil.mainWindow()
        maya_main_window = wrapInstance(int(maya_main_window_ptr), QtWidgets.QWidget)
        # Add the UI to the Maya main window
        self.setParent(maya_main_window)

        self.build_ui()
        self.connect_buttons()
        self.ui.show()

    def build_ui(self):
        pass

    def connect_buttons(self):
        pass  # connect functions to buttons
        #self.ui.close_BTN.clicked.connect(self.ui.close)
        #self.ui.updateAll_BTN.clicked.connect(self.test)


