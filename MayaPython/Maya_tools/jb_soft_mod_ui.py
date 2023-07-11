from PySide2 import QtCore, QtWidgets, QtUiTools
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel
import logger as logging
import os
import math
import maya.api.OpenMaya as om
UI_NAME = "SoftModUi"
logger = logging.getLogger('Soft Mod Tool')


class SoftModUi(QtWidgets.QMainWindow):
    ui = None
    sel = None
    skin_cluster = None
    geo = None
    soft_mod = None
    def __init__(self):
        ui_file = "PATH TO MY COPY OF/jb_softModControl.ui")  # file path to qt designer file
        file = QtCore.QFile(ui_file)
        super(SoftModUi, self).__init__()
        try:
            cmds.deleteUI(UI_NAME)
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
        # Make window always appear on top
        window = QtWidgets.QWidget(maya_main_window)
        window.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        # Add the UI to the Maya main window
        self.setParent(maya_main_window)

        self.connect_buttons()
        self.set_default_state()
        self.ui.show()

    def set_default_state(self):
        self.ui.softMod_BTN.setVisible(False)
        self.ui.softMod_LBL.setVisible(False)
        self.ui.mode_CBX.setCurrentIndex(1)
        self.ui.prefix_LET.setVisible(False)
        self.ui.prefix_LBL.setVisible(False)
        self.ui.prefix_LBL.setText("Mirror Prefix (L or R):")

    def connect_buttons(self):
        self.ui.convert_BTN.clicked.connect(self.convert_soft_mod_to_control)
        self.ui.softMod_BTN.clicked.connect(enable_soft_mod)
        self.ui.mode_CBX.currentIndexChanged.connect(self.change_info_text)
        self.ui.mode_CBX.currentIndexChanged.connect(self.hide_soft_mod_btn)
        self.ui.none_RBT.toggled.connect(lambda: self.show_hide_prefix_let(not self.ui.none_RBT.isChecked()))

    def show_hide_prefix_let(self, value):
        self.ui.prefix_LET.setVisible(value)
        self.ui.prefix_LBL.setVisible(value)
        self.ui.prefix_LET.clear()

    def hide_soft_mod_btn(self):
        if self.ui.mode_CBX.currentIndex() == 0:
            self.ui.softMod_BTN.setVisible(False)
            self.ui.softMod_LBL.setVisible(False)
        else:
            self.ui.softMod_BTN.setVisible(True)
            self.ui.softMod_LBL.setVisible(True)

    def change_info_text(self):
        if self.ui.mode_CBX.currentIndex() == 0:

            self.ui.toolTip_LBL.setText("1. Soft select the area you want to influence")
        else:
            self.ui.toolTip_LBL.setText("1. Select softModHandle")

    def convert_soft_mod_to_control(self):
        """
            Creates a control and joint system based off the softMod selection
        """
        cmds.undoInfo(openChunk=True)
        prefix = self.ui.prefix_LET.text()
        if len(prefix) > 0:
            control_name = "{}_{}".format(prefix, self.ui.name_LET.text())
        else:
            control_name = self.ui.name_LET.text()

        if self.ui.mode_CBX.currentIndex() == 0:
            self.sel = cmds.ls(sl=True)
            self.geo = self.sel[0].split(".")[0]
            self.skin_cluster = get_skin_cluster(self.geo)
            soft_vertices = self.get_soft_select_weights()
            new_joint = self.create_joint_from_soft_selection("{}_JNT".format(control_name))
        else:
            self.soft_mod = cmds.ls(sl=True)[0]
            self.geo = cmds.softMod(self.soft_mod, q=True, g=True)[0]
            self.skin_cluster = get_skin_cluster(self.geo)
            soft_vertices = self.get_soft_select_weights(self.soft_mod)
            new_joint = self.add_cluster_from_soft_mod("{}_JNT".format(control_name))

        for vert in soft_vertices:
            cmds.skinPercent(self.skin_cluster, vert["index"], transformValue=[(new_joint, vert["weight"])], r=True)

        build_custom_control(new_joint, control_name)
        if not self.ui.none_RBT.isChecked():
            if self.ui.prefix_LET.text():
                mirrored_joint, mirror_control = mirror_joint(self.ui.xy_RBT,
                                                              self.ui.yz_RBT,
                                                              self.ui.xz_RBT,
                                                              new_joint, control_name, prefix)
                build_custom_control(mirrored_joint, mirror_control)
                cmds.skinCluster(self.skin_cluster, edit=True, addInfluence=mirrored_joint, lockWeights=True,
                                 weight=0.0)
                mirror_inverse = False
                if prefix == "R":
                    mirror_inverse = True
                if self.ui.xy_RBT.isChecked():
                    cmds.copySkinWeights(ss=self.skin_cluster, ds=self.skin_cluster, mirrorMode='XY',
                                         mirrorInverse=mirror_inverse,
                                         surfaceAssociation="closestPoint", influenceAssociation="closestJoint")
                elif self.ui.yz_RBT.isChecked():
                    cmds.copySkinWeights(ss=self.skin_cluster, ds=self.skin_cluster, mirrorMode='YZ',
                                         mirrorInverse=mirror_inverse,
                                         surfaceAssociation="closestPoint", influenceAssociation="closestJoint")
                elif self.ui.xz_RBT.isChecked():
                    cmds.copySkinWeights(ss=self.skin_cluster, ds=self.skin_cluster, mirrorMode='XZ',
                                         mirrorInverse=mirror_inverse,
                                         surfaceAssociation="closestPoint", influenceAssociation="closestJoint")
            else:
                logger.error("No Prefix set: Set prefix as L or R and retry")
        cmds.undoInfo(closeChunk=True)
        disable_current_tool()

    def create_joint_from_soft_selection(self, joint_name):
        cluster = cmds.cluster(self.sel, rel=True, en=1)
        joint = cmds.createNode('joint', name=joint_name, ss=1)
        cmds.delete(cmds.parentConstraint(cluster, joint, mo=False), cluster)

        cmds.skinCluster(self.skin_cluster, edit=True, addInfluence=joint_name, lockWeights=False, weight=0.0)
        return joint_name

    def add_cluster_from_soft_mod(self, joint_name):
        joint = cmds.createNode('joint', name=joint_name, ss=1)
        cmds.delete(cmds.parentConstraint(self.soft_mod, joint, mo=False), self.soft_mod)

        cmds.skinCluster(self.skin_cluster, edit=True, addInfluence=joint_name, lockWeights=True, weight=0.0)
        return joint_name

    def get_soft_select_weights(self, soft_mod_handle=None):
        # Set the center and radius of the sphere
        # Get point
        selected_vertex = cmds.ls(selection=True)

        if soft_mod_handle:
            soft_mod = cmds.listConnections(soft_mod_handle, d=True, t='softMod')
            radius = cmds.getAttr("{}.falloffRadius".format(soft_mod[0]))
            center = cmds.xform(soft_mod_handle, q=True, rp=True)
            vertices = find_vertex_range(self.geo)
        else:
            bounding_box = cmds.xform(selected_vertex, boundingBox=True, query=True)
            selection_radius = bounding_box_center(bounding_box)
            cluster = cmds.cluster(selected_vertex, rel=True, en=1)
            radius = cmds.softSelect(q=True, ssd=True)
            center = cmds.xform(cluster[1], q=True, rp=True)
            cmds.delete(cluster)
            radius = selection_radius + radius
            vertices = find_vertex_range(self.geo)

        vertices_weights = []
        for vertex in vertices:
            soft_select_vertex = {"index": 0,
                                  "weight": 0}
            # Get the position of the vertex
            position = cmds.pointPosition(vertex, w=True)

            point1 = om.MPoint(position)
            point2 = om.MPoint(center)

            # Calculate the distance between the two points
            distance = point1.distanceTo(point2)

            # If the distance is less than the radius, select the vertex
            if distance <= radius:
                weight = abs(mel.eval("smoothstep 0 1 {}".format((distance / radius))) - 1)
                soft_select_vertex["index"] = vertex
                soft_select_vertex["weight"] = weight
                vertices_weights.append(soft_select_vertex)
        return vertices_weights


def find_vertex_range(object_name):
    # Get all the vertices of the object
    vertices = cmds.ls(object_name + ".vtx[*]", fl=True)

    # Create a string that represents the vertex range
    return vertices

def enable_soft_mod():
    # set the tool mode to Soft Mod
    mel.eval('setToolTo ShowManips; performSoftMod 0 0 0 {0.0, 0.0, 0.0};')


def disable_current_tool():
    mel.eval('global string $gSelect; setToolTo $gSelect;')


def build_custom_control(joint, control_name):
    """
    Build Control hierarchy
    Args:
        joint(str): name of joint
        control_name(str): name of new control
    returns:
        offset_node: Offset grp of created control
    """
    offset_node = cmds.createNode('transform', name="{}_GRP".format(control_name))
    curve = cmds.curve(p=[(-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
                          (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5),
                          (0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5),
                          (-0.5, 0.5, 0.5), (-0.5, -0.5, 0.5)], per=False, d=1, name="{}_CTL".format(control_name), )
    cmds.parent(curve, offset_node, a=1)
    cmds.matchTransform(offset_node, joint)
    cmds.parentConstraint(curve, joint, mo=1, w=1)
    for axis in ["sx", "sy", "sz"]:
        cmds.connectAttr("{}.{}".format(curve, axis), "{}.{}".format(joint, axis))

    return offset_node


def mirror_joint(mirror_xy, mirror_yz, mirror_xz, new_joint, control_name, prefix):
    pivot_grp = cmds.createNode('transform', name="mirror_pivot")
    if prefix == "R":
        mirror_joint_name = cmds.createNode('joint', name=new_joint.replace("R_", "L_"))
        control_name = control_name.replace("R_", "L_")
    elif prefix == "L":
        mirror_joint_name = cmds.createNode('joint', name=new_joint.replace("L_", "R_"))
        control_name = control_name.replace("L_", "R_")
    elif prefix == "B":
        mirror_joint_name = cmds.createNode('joint', name=new_joint.replace("B_", "F_"))
        control_name = control_name.replace("B_", "F_")
    elif prefix == "F":
        mirror_joint_name = cmds.createNode('joint', name=new_joint.replace("F_", "B_"))
        control_name = control_name.replace("F_", "B_")
    else:
        mirror_joint_name = cmds.createNode('joint', name=new_joint)
    cmds.matchTransform(mirror_joint_name, new_joint)
    cmds.parent(mirror_joint_name, pivot_grp)
    if mirror_xy:
        cmds.setAttr("{}.scaleX".format(pivot_grp), -1)

    elif mirror_yz:
        cmds.setAttr("{}.scaleY".format(pivot_grp), -1)

    elif mirror_xz:
        cmds.setAttr("{}.scaleZ".format(pivot_grp), -1)
    cmds.makeIdentity(pivot_grp, apply=True, t=1, r=1, s=1, n=0, pn=1)
    cmds.parent(mirror_joint_name, w=1)
    cmds.delete(pivot_grp)
    return mirror_joint_name, control_name


def get_skin_cluster(geo):
    """
    Gets skin cluster attached to
    Args:
        geo(pynode): node to get skin cluster off

    Returns:
    """
    #deformer = cmds.listHistory(geo, type='skinCluster')[0]
    deformer = cmds.ls(cmds.listHistory(geo), type="skinCluster")[0]
    return deformer


def bounding_box_center(bounding_box):
    # Calculate the center of the bounding box
    center = [(bounding_box[0] + bounding_box[3]) / 2.0,
              (bounding_box[1] + bounding_box[4]) / 2.0,
              (bounding_box[2] + bounding_box[5]) / 2.0]

    # Calculate the distance between the center and one of the corners
    corner = [bounding_box[3], bounding_box[4], bounding_box[5]]
    radius = math.sqrt(sum([(c - c0) ** 2 for c, c0 in zip(corner, center)]))

    return radius
