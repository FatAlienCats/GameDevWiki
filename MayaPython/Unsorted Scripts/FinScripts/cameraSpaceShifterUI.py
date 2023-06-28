import json
import os
import PySide2
import time
import pymel.core.datatypes as dt
import pprint as pp
from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance
from PySide2.QtCore import Signal
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI

import logging
logging.basicConfig()
logger = logging.getLogger('CameraSpaceShifter')
logger.setLevel(logging.DEBUG)

from maya import OpenMayaUI as omui
import pymel.core as pm
from functools import partial

class CameraSpaceUI(QtWidgets.QWidget):

    previousValue = 0
    step = 1

    def __init__(self):
        # remove existing intances
        try:
            pm.deleteUI('CameraSpaceShifter')
        except:
            logger.debug('No previous UI exists')


        # Create dialog with main maya window as parent
        parent = QtWidgets.QDialog(parent=getMayaMainWindow())
        parent.setObjectName('CameraSpaceShifter')
        parent.setWindowTitle('Camera Space Shifter')

        # if doesn't dock try QVBoxLayout
        dlgLayout = QtWidgets.QVBoxLayout(parent)


        super(CameraSpaceUI, self).__init__(parent=parent)

        self.buildUI()

        self.parent().layout().addWidget(self)
        # get active camera panel
        self.connectCamera()

        parent.show()

    def buildUI(self):
        """Creates UI Widgets"""
        layout = QtWidgets.QGridLayout(self)

        # Dial to control X movement
        xDial = QtWidgets.QDial()
        xDial.setNotchesVisible(True)
        xDial.setWrapping(True)
        xDial.setTracking(True)
        xDial.sliderPressed.connect(self.startUndoBlock)
        xDial.sliderReleased.connect(self.endUndoBlock)
        xDial.valueChanged.connect(lambda val: self.moveObject(val, 'x'))
        layout.addWidget(xDial, 1, 0)

        # Dial to control Y movement
        yDial = QtWidgets.QDial()
        yDial.setNotchesVisible(True)
        yDial.setWrapping(True)
        yDial.setTracking(True)
        yDial.sliderPressed.connect(self.startUndoBlock)
        yDial.sliderReleased.connect(self.endUndoBlock)
        yDial.valueChanged.connect(lambda val: self.moveObject(val, 'y'))
        layout.addWidget(yDial, 1, 1)

        # Dial to control Y movement
        zDial = QtWidgets.QDial()
        zDial.setNotchesVisible(True)
        zDial.setWrapping(True)
        zDial.setTracking(True)
        zDial.sliderPressed.connect(self.startUndoBlock)
        zDial.sliderReleased.connect(self.endUndoBlock)
        zDial.valueChanged.connect(lambda val: self.moveObject(val, 'z'))
        layout.addWidget(zDial, 1, 2)

        # SpinBox to control step value
        stepBox = QtWidgets.QSpinBox()
        stepBox.setValue(1)
        stepBox.setMinimum(1)
        stepBox.setMaximum(100)
        stepBox.valueChanged.connect(lambda val: self.setStepValue(val))
        layout.addWidget(stepBox, 0, 2)
        label = QtWidgets.QLabel('Step Value')
        label.setAlignment(5)
        layout.addWidget(label, 0, 1)


        self.setLayout(layout)

    def moveObject(self, value, axis):
        """Moves object in camera space"""
        if self.camera.getTranslation() != self.cameraTranslation:
            logger.debug("Camera position changed, reloading camera")
            self.connectCamera()
        if not pm.selected():
            return
        if axis == 'x':
            if self.previousValue > value:
                pm.pixelMove(self.step, 0)
            else:
                pm.pixelMove(-self.step, 0)

        elif axis == 'y':
            if self.previousValue > value:
                pm.pixelMove(0, self.step)
            else:
                pm.pixelMove(0, -self.step)
        elif axis == 'z':
            adjustedVal = float(self.step * 0.01)
            if self.previousValue > value:
                self.moveZ(adjustedVal)
            else:
                self.moveZ(-adjustedVal)
        self.previousValue = value

    def startUndoBlock(self):
        """Starts an undo chunk"""
        pm.undoInfo(ock=True)


    def endUndoBlock(self):
        """Ends undo chunk"""
        pm.undoInfo(cck=True)

    def setStepValue(self, val):
        """Sets the step value to the value of the stepBox widget"""
        self.step = val
        print (self.step)

    def moveZ(self, val):
        """
        Gets the vector between the object and the camera. The moves the object along the vector the step amount.
        :param val: the adjusted value given by the slider
        :return: None
        """
        obj = pm.selected()[0]
        objTranslation = obj.getTranslation(ws=True)
        a = dt.Vector(objTranslation)
        b = dt.Vector(self.cameraTranslation)
        vector = b-a
        c = a + (vector*(val))
        obj.setTranslation(c)

    def connectCamera(self):
        """
        Gets the camera of the last active model viewport
        :return: CameraTranslation for use in the MoveZ function
        """
        try:
            obj = pm.selected()[0]
        except:
            pass
        # gets active 3dView
        view = OpenMayaUI.M3dView.active3dView()
        cam = OpenMaya.MDagPath()
        view.getCamera(cam)
        # gets partial name
        camShapeName = cam.partialPathName()
        pm.select(camShapeName)
        shp = pm.selected()[0]
        try:
            pm.select(obj)
        except:
            pm.select(clear=True)
        self.camera = shp.getParent()
        # gets camera translation
        self.cameraTranslation = self.camera.getTranslation()
        logger.debug("Current camera space: {}".format(self.camera))

def getMayaMainWindow():
    """
    Converts window to QMainWindow
    Returns:
        QtWidgets.QMainWindow: The Maya MainWindow
    """
    # Get a reference to Maya's MainWindow
    win = omui.MQtUtil_mainWindow()
    # Converting it to a QMainWindow
    ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
    return ptr
