"""
Fair Warning: This will be the most complex example in the course using more advanced maya features alongside
              more advanced python features than previous examples.
"""

import json
import os
import Qt
from Qt import QtWidgets, QtCore, QtGui
import logging
from maya_rig.builder.templates import core
logging.basicConfig()

logger = logging.getLogger('RiggingTools')

logger.setLevel(logging.DEBUG)

if Qt.__binding__.startswith('PyQt'):
    # If we're using PyQt4 or PyQt5 we need to import sip
    logger.debug('Using sip')
    # So we import wrapInstance from sip and alias it to wrapInstance so that it's the same as the others
    from sip import wrapinstance as wrapInstance
    # Also PyQt uses pyqtSignal instead of Signal so we will import it and alias it to Signal
    from Qt.QtCore import pyqtSignal as Signal
elif Qt.__binding__ == 'PySide':
    # If we're using PySide (Maya 2016 and earlier), we'll use shiboken instead
    logger.debug('Using shiboken')
    # Shiboken already uses the correct names for both wrapInstance and Signal so we just need to import them without aliasing them
    from shiboken import wrapInstance
    from Qt.QtCore import Signal
else:
    # Finally, the only option left is PySide2(Maya 2017 and higher) which uses shiboken2
    logger.debug('Using shiboken2')
    # Again, this uses the correct naming so we just import without aliasing
    from shiboken2 import wrapInstance
    from Qt.QtCore import Signal

from maya import OpenMayaUI as omui
import pymel.core as pm
from functools import partial


class CreateTemplateButton(QtWidgets.QPushButton):

    specialClicked = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        super(CreateTemplateButton, self).__init__(*args, **kwargs)
        self._linked_template = None
        self.clicked.connect(self.emitSpecialClicked)

    def setLinkedTemplate(self, template):
        self._linked_template = template

    def emitSpecialClicked(self):
        self.specialClicked.emit(self._linked_template)


class RiggingTools(QtWidgets.QWidget):
    """
    This is the main Template Manager.
    To call it we just do

    RiggingTools(dock=True) and it will display docked, otherwise dock=False will display it as a window

    """
    # The Key is the name that will be displayed in the UI
    # The Value is the function that will be called

    def __init__(self, dock=False):

        if dock:
            parent = getDock()
        else:
            deleteDock()
            try:
                pm.deleteUI('riggingTools')
            except:
                logger.debug('No previous UI exists')

            parent = QtWidgets.QDialog(parent=getMayaMainWindow())

            parent.setObjectName('riggingTools')

            parent.setWindowTitle('Template Manager')

            dlgLayout = QtWidgets.QVBoxLayout(parent)

        super(RiggingTools, self).__init__(parent=parent)

        self.buildUI()

        self.parent().layout().addWidget(self)

        if not dock:
            parent.show()

    def buildUI(self):
        """Creates UI Widgets"""
        layout = QtWidgets.QGridLayout(self)

        self.buildBuilderUI(layout, 0)

        self.buildTemplatesUI(layout, 1)

        self.buildControlShapesUI(layout, 2)
        #layout.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        #layout.setRowStretch(3, 1)

        #self.setLayout(layout)

    def buildBuilderUI(self, layout, position):
        # Dictionary of templates: "name": (row, column, command)
        builder_tools = {
            "Build": (0, 0, self.buildRig),
            "Build Config": (0, 1, self.buildConfig),
            "Reload Build Scripts": (1, 0, self.reloadBuildScripts),
            "Save Bindings": (1, 1, self.saveRigBindings),
            "Save Control Shapes": (2, 0, self.saveControlShapes),
            "Configure Geo": (1, 0, self.setUpImportedGeo),
        }
        # setup group box
        template_grp = QtWidgets.QGroupBox("Builder")
        template_grp.setAlignment(4)
        template_grp.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        layout.addWidget(template_grp, position, 0)  # add group box to larger layout
        # add grid layout to group box
        vbox = QtWidgets.QGridLayout()

        template_grp.setLayout(vbox)

        self.createButtonsFromDictionaryManual(builder_tools, vbox)

    def createTemplateFromButtonPress(self, special_string):

        template_names = {
            "global_template": self.globalTemplate,
            "cog": self.cogTemplate,
            "worldspace_control": self.worldSpaceTemplate,
            "fk_chain": self.fkChainTemplate,
            "ik_spline": self.ikSplineTemplate,
            "torso": self.torsoTemplate,
            "arm": self.armTemplate,
            "leg": self.legTemplate,
            "fingers": self.fingersTemplate,
        }
        print template_names[special_string]
        template_names[special_string]()

    def buildTemplatesUI(self, layout, position):
        # Dictionary of templates: "name": (row, column, command)

        template_names = {}
        for templates in core.TEMPLATE_MODULE_NAMES:
            template_names.update({templates: templates})


        template_names_sorted = dict(sorted(template_names.items(), key=lambda x: x[0].upper()))
        print template_names_sorted
        # setup group box
        template_grp = QtWidgets.QGroupBox("Templates")
        template_grp.setAlignment(4)
        template_grp.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        layout.addWidget(template_grp, position, 0)  # add group box to larger layout
        # add grid layout to group box
        vbox = QtWidgets.QGridLayout()

        template_grp.setLayout(vbox)

        self.createButtonsFromDictionary(template_names_sorted, vbox)

    def buildControlShapesUI(self, layout, position):
        # Dictionary of templates: "name": (row, column, command)
        shape_tools = {
            "Lift": (0, 0, self.liftControlShapes),
            "Replace": (0, 1, self.replaceShape),
            "Replace By Name": (0, 2, self.replaceShapeByName),
            "Mirror": (1, 0, self.mirrorControlShapes),
            "Load Serialised": (1, 1, self.loadSerialisedShapes),
            "Combine": (1, 2, self.combineShapes),
            "Color": (2, 0, self.colorControlShapes),
        }
        # setup group box
        template_grp = QtWidgets.QGroupBox("Shape Tools")
        template_grp.setAlignment(4)
        template_grp.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        layout.addWidget(template_grp, position, 0)  # add group box to larger layout
        # add grid layout to group box
        vbox = QtWidgets.QGridLayout()

        template_grp.setLayout(vbox)

        self.createButtonsFromDictionaryManual(shape_tools, vbox)

    def createButtonsFromDictionary(self, template_names, vbox):
        row = 0
        column = 0
        for name, templates in sorted(template_names.items()):
            #template_btn = QtWidgets.QPushButton(templates[0])
            template_btn = CreateTemplateButton(name)
            template_btn.setLinkedTemplate(templates)
            template_btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            template_btn.specialClicked.connect(self.createTemplateFromButtonPress)
            vbox.addWidget(template_btn, row, column)
            column += 1
            if column == 2:
                column = 0
                row += 1

    def createButtonsFromDictionaryManual(self, template_names, vbox):
        row = 0
        column = 0
        for templates in sorted(template_names.items()):
            template_btn = QtWidgets.QPushButton(templates[0])
            #template_btn = CreateTemplateButton(name)
            #template_btn.setLinkedTemplate(templates)
            template_btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            #template_btn.specialClicked.connect(self.createTemplateFromButtonPress)
            template_btn.clicked.connect(templates[-1][-1])
            vbox.addWidget(template_btn, row, column)
            column += 1
            if column == 2:
                column = 0
                row += 1

    def testButton(self, button):
        print button.text()

    def buildRig(self):
        from maya_rig.builder import build_core
        build_core.buildFromConfig()

    def setUpImportedGeo(self):
        from maya_rig.general import scene_setup
        scene_setup.configureMainGeo()

    def buildConfig(self):
        from maya_rig.builder import build_config_widget
        build_config_widget.BuildConfigWidget.showWindow()

    def reloadBuildScripts(self):
        from maya_rig.dev_utils import reload_rig_builder
        reload_rig_builder.reloadRigBuilder()

    def saveRigBindings(self):
        from maya_rig.builder import bindings
        bindings.storeGeoBindings()

    def saveControlShapes(self):
        from maya_rig.builder import build_core
        build_core.saveControlShapes()

    def liftControlShapes(self):
        from maya_rig.control_shapes import replace_shapes
        replace_shapes.liftControlShapesOnSelected()

    def replaceShape(self):
        from maya_rig.control_shapes import replace_shapes
        replace_shapes.replaceTargetChildShapesSelected()

    def replaceShapeByName(self):
        from maya_rig.control_shapes import replace_shapes
        import pymel
        nodes = pymel.core.selected()
        for node in nodes:
            if "_LiftedShape" in node.name():
                shape_to_replace = node.nodeName().replace("_LiftedShape", "")  # starts with then recompile with
                replace_shapes.replaceTargetChildShapes(pymel.core.PyNode(shape_to_replace), [node])

    def mirrorControlShapes(self):
        from maya_rig.control_shapes import replace_shapes
        replace_shapes.mirrorSelectedCtrlShapes()

    def loadSerialisedShapes(self):
        from maya_rig.control_shapes import serialised_curve_lib
        serialised_curve_lib.showCurveMenu()

    def combineShapes(self):
        from maya_rig.control_shapes import replace_shapes
        replace_shapes.combineShapesSelected()

    def colorControlShapes(self):
        from maya_rig.control_shapes import color_controls
        color_controls.colorSelectedControlsInteractive()

    def globalTemplate(self):
        core.createTemplate("global")

    def cogTemplate(self):
        core.createTemplate("cog")

    def worldSpaceTemplate(self):
        core.createTemplate("worldspaceControl")

    def fkChainTemplate(self):
        core.createTemplate("fkChain")

    def ikSplineTemplate(self):
        core.createTemplate("ikSpline")

    def torsoTemplate(self):
        core.createTemplate("torso")

    def armTemplate(self):
        core.createTemplate("arm")

    def legTemplate(self):
        core.createTemplate("leg")

    def fingersTemplate(self):
        core.createTemplate("fingers")


def getMayaMainWindow():
    """
    Since Maya is Qt, we can parent our UIs to it.
    This means that we don't have to manage our UI and can leave it to Maya.

    Returns:
        QtWidgets.QMainWindow: The Maya MainWindow
    """
    win = omui.MQtUtil_mainWindow()

    ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
    return ptr


def getDock(name='RiggingToolsDock'):
    """
    This function creates a dock with the given name.
    It's an example of how we can mix Maya's UI elements with Qt elements
    Args:
        name: The name of the dock to create

    Returns:
        QtWidget.QWidget: The dock's widget
    """
    deleteDock(name)
    ctrl = pm.workspaceControl(name, dockToMainWindow=('right', 1), label="Template Manager")

    qtCtrl = omui.MQtUtil_findControl(ctrl)

    ptr = wrapInstance(long(qtCtrl), QtWidgets.QWidget)

    return ptr


def deleteDock(name='RiggingToolsDock'):
    """
    A simple function to delete the given dock
    Args:
        name: the name of the dock
    """
    if pm.workspaceControl(name, query=True, exists=True):
        pm.deleteUI(name)

