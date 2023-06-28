from functools import partial
import os
import logging
import pymel
from Qt import QtWidgets, QtGui, QtCompat, QtCore
from fin_ui.widgets.expander.expander import PersistentExpanderGroupWidget
from fin_ui.widgets.persistent_settings import PersistentSettings
from fin_ui.widgets.replace import replaceWidget
from maya import OpenMayaUI as omu
from maya_core.command_executer.ui_lib.flow_layout import FlowLayout
from maya_rig.builder import build_core
from maya_rig.control_shapes import replace_shapes
from maya_rig.control_shapes.color_controls import colorControlsRGB, colorOutlinerRGB, removeSelectedOutlinerColor
from maya_rig.control_shapes.rigged_two_headed_arrow import riggedTwoHeadedArrow
from maya_rig.control_shapes.serialised_curve_lib import listSerialisedShapes, loadSerialisedShapeAtSelected,\
    serialiseShape, _getSerialisedShapeIconPath

logger = logging.getLogger(__name__)


class ControlShapesWidget(QtWidgets.QWidget):

    UI_FILE = "control_shapes_widget.ui"  # save file next to this module
    _instance = None
    color_palette = None
    line = None
    flow_layout = None
    @classmethod
    def showWindow(cls):
        cls.makeInstance(parent=getMayaMainWindow())
        cls._instance.show()
        cls._instance.raise_()
        cls._instance.setDefaultPosition()

        return cls._instance

    @classmethod
    def makeInstance(cls, parent=None):
        if not cls._instance:
            cls._instance = cls(parent=parent)
        return cls._instance

    def __init__(self, parent=None):
        super(ControlShapesWidget, self).__init__(parent=parent)
        QtCompat.loadUi(self._getUiFilePath(), self)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setWindowTitle("Control Shapes Tools")
        self._buildUI()
        self._buildConnections()

    def _buildUI(self):
        self._replaceCheckBoxWithExpandable()
        self._buildColorChanger()
        self._buildCreateControlShape()
        self.createLineEdit()

    def _replaceCheckBoxWithExpandable(self):
        widgets_to_replace = [self.builderExpanderTemp, self.colorControlsExpanderTemp, self.createControlsExpanderTemp,
                              self.tempRiggedControlShapeButton]
        widgets_to_group = [self.builderGroup, self.colorControlsGroup, self.serialiseControlShapeGroup,
                            self.riggedControlShapesGroup]
        storage = PersistentSettings("control_shapes_tools")
        for widgets, groupBox in zip(widgets_to_replace, widgets_to_group):
            name = widgets.text()
            tool_tip = widgets.toolTip()
            t = PersistentExpanderGroupWidget(name, storage)
            t.setToolTip(tool_tip)
            replaceWidget(widgets, t)
            t.addWidget(groupBox)

    def _buildColorChanger(self):
        self.color_palette = QtWidgets.QColorDialog()
        self.color_palette.setOptions(QtWidgets.QColorDialog.NoButtons)
        self.color_palette.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        replaceWidget(self.colorPickerTemp, self.color_palette)

    def _buildCreateControlShape(self, initial_build=True):
        if initial_build:
            self.flow_layout = FlowLayout()
        for item in listSerialisedShapes():
            icon = _getSerialisedShapeIconPath(item)
            template_btn = self.createControlShapeIconButton(item, icon_path=icon)
            self.flow_layout.addWidget(template_btn)
        self.scrollGroup.setLayout(self.flow_layout)

    def createControlShapeIconButton(self, item, icon_path=None):
        button = CustomControlShapeWidget(item, icon_path)
        button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        button.clicked.connect(partial(loadSerialisedShapeAtSelected, item))
        return button

    def rebuildControlShapeLibrary(self):
        for i in reversed(range(self.flow_layout.count())):
            self.flow_layout.itemAt(i).widget().setParent(None)
        self._buildCreateControlShape(initial_build=False)

    def createLineEdit(self):
        self.line = QtWidgets.QLineEdit(self)
        self.line.resize(200, 32)
        replaceWidget(self.controlNameLineEdit, self.line)

    def _buildConnections(self):
        logger.info("Building Connections...")
        self.setColorButton.clicked.connect(self.setColor)
        self.saveControlsButton.clicked.connect(self.saveControls)
        self.mirrorControlsButton.clicked.connect(self.mirrorControls)
        self.liftControlsButton.clicked.connect(self.liftControlShape)
        self.combineControlsButton.clicked.connect(self.combineShapes)
        self.addToShapeButton.clicked.connect(self.addToShapes)
        self.replaceShapesButton.clicked.connect(self.replaceShapes)
        self.replaceByNameButton.clicked.connect(self.replaceByName)
        self.serialiseControlShapeButton.clicked.connect(self.saveNewShape)
        self.setColorInOutlinerButton.clicked.connect(self.setColorInOutliner)
        self.removeOutlinerColorButton.clicked.connect(self.removeColorFromOutliner)
        self.riggedTwoHeadedArrowButton.clicked.connect(self.riggedTwoHeadedArrow)
        self.name = self.controlNameLineEdit

    def setDefaultPosition(self):
        self.move(100, 100)

    def _getUiFilePath(self):
        this_dir = os.path.dirname(__file__)
        return os.path.join(this_dir, self.UI_FILE)

    def setInitialValues(self):
        pass

    def saveControls(self):
        build_core.saveControlShapes()

    def mirrorControls(self):
        replace_shapes.mirrorSelectedCtrlShapes()

    def liftControlShape(self):
        replace_shapes.liftControlShapesOnSelected()

    def combineShapes(self):
        replace_shapes.combineShapesSelected()

    def addToShapes(self):
        replace_shapes.addToShapeSelected()

    def replaceShapes(self):
        replace_shapes.replaceTargetChildShapesSelected()

    def replaceByName(self):
        replace_shapes.returnLiftedShapesToOrigNodes()

    def saveNewShape(self):
        name = self.line.text()
        serialiseShape(node_name=name)
        self.rebuildControlShapeLibrary()

    def setColor(self):
        color = self.color_palette.currentColor()
        color_tuple = (color.red()/255.0, color.green()/255.0, color.blue()/255.0)
        controls = pymel.core.ls(sl=1)
        colorControlsRGB(controls, color_tuple)

    def setColorInOutliner(self):
        color = self.color_palette.currentColor()
        color_tuple = (color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0)
        controls = pymel.core.ls(sl=1)
        colorOutlinerRGB(controls, color_tuple)

    def removeColorFromOutliner(self):
        removeSelectedOutlinerColor()

    def riggedTwoHeadedArrow(self):
        riggedTwoHeadedArrow()

def getMayaMainWindow():
    pointer = omu.MQtUtil.mainWindow()
    return QtCompat.wrapInstance(long(pointer), QtWidgets.QWidget)


class CustomControlShapeWidget(QtWidgets.QWidget):

    clicked = QtCore.Signal()

    def __init__(self, name, image_path=None, parent=None):

        super(CustomControlShapeWidget, self).__init__(parent)
        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        image = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(image_path)
        image.setPixmap(pixmap)
        self.layout().addWidget(image)

        label = QtWidgets.QLabel(name)
        self.layout().addWidget(label)

        self.layout().addStretch()

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)  # tells the widget to use the style bg color below...
        self.setStyleSheet("background-color: rgb(80,80,80); margin:2px;")
        label.setStyleSheet("background-color: rgb(100,100,100); ")

    def mousePressEvent(self, *args, **kwargs):
        self.clicked.emit()
        self.setStyleSheet("background-color: rgb(60,60,60); margin:2px;")

    def mouseReleaseEvent(self, *args, **kwargs):
        self.setStyleSheet("background-color: rgb(80,80,80); margin:2px;")
