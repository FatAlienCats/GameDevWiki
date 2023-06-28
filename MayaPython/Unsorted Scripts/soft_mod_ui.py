from PySide2 import QtCore, QtWidgets, QtUiTools
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
from kore import logger as logging
import math
UI_NAME = "SoftModUi"
logger = logging.getLogger('Soft Mod Tool')


class SoftModUi(QtWidgets.QMainWindow):
    ui = None
    sel = None
    skin_cluster = None

    def __init__(self):
        ui_file = "/mnt/user-share/julianbeiboer/UI/softModControl.ui"  # file path to qt designer file
        file = QtCore.QFile(ui_file)
        super(SoftModUi, self).__init__()
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

    def connect_buttons(self):
        self.ui.convert_BTN.clicked.connect(self.convert_soft_mod_to_control)
        self.ui.softMod_BTN.clicked.connect(enable_soft_mod)
        self.ui.mode_CBX.currentIndexChanged.connect(self.change_info_text)
        self.ui.mode_CBX.currentIndexChanged.connect(self.hide_soft_mod_btn)

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
            self.ui.toolTip_LBL.setText("1. Select geo and then softModHandle")

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
        self.sel = pm.selected()
        self.skin_cluster = get_skin_cluster(self.sel[0]).name()

        if self.ui.mode_CBX.currentIndex() == 0:
            soft_vertices = self.get_soft_select_weights()
            new_joint = self.create_joint_from_soft_selection("{}_JNT".format(control_name))
        else:
            soft_vertices = self.get_soft_select_weights(self.sel[1])
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
                cmds.skinCluster(self.skin_cluster, edit=True, addInfluence=mirrored_joint, lockWeights=True, weight=0.0)
                mirror_inverse = False
                if prefix == "R":
                    mirror_inverse = True
                if self.ui.xy_RBT.isChecked():
                    cmds.copySkinWeights(ss=self.skin_cluster, ds=self.skin_cluster, mirrorMode='XY', mirrorInverse=mirror_inverse,
                                         surfaceAssociation="closestPoint", influenceAssociation="closestJoint")
                elif self.ui.yz_RBT.isChecked():
                    cmds.copySkinWeights(ss=self.skin_cluster, ds=self.skin_cluster, mirrorMode='YZ', mirrorInverse=mirror_inverse,
                                         surfaceAssociation="closestPoint", influenceAssociation="closestJoint")
                elif self.ui.xz_RBT.isChecked():
                    cmds.copySkinWeights(ss=self.skin_cluster, ds=self.skin_cluster, mirrorMode='XZ', mirrorInverse=mirror_inverse,
                                         surfaceAssociation="closestPoint", influenceAssociation="closestJoint")
            else:
                logger.error("No Prefix set: Set prefix as L or R and retry")
        cmds.undoInfo(closeChunk=True)

    def create_joint_from_soft_selection(self, joint_name):
        cluster = pm.cluster(self.sel, rel=True, en=1)
        joint = pm.createNode('joint', name=joint_name, ss=1)
        pm.delete(pm.parentConstraint(cluster, joint, mo=False), cluster)

        cmds.skinCluster(self.skin_cluster, edit=True, addInfluence=joint_name, lockWeights=False, weight=0.0)
        return joint_name

    def add_cluster_from_soft_mod(self, joint_name):
        joint = pm.createNode('joint', name=joint_name, ss=1)
        pm.delete(pm.parentConstraint(self.sel[1], joint, mo=False), self.sel[1])

        cmds.skinCluster(self.skin_cluster, edit=True, addInfluence=joint_name, lockWeights=True, weight=0.0)
        return joint_name

    def get_soft_select_weights(self, soft_mod_handle=None):
        # Set the center and radius of the sphere
        # Get point
        selected_vertex = cmds.ls(selection=True)

        if soft_mod_handle:
            soft_mod = pm.listConnections(soft_mod_handle, d=True, t='softMod')
            radius = cmds.getAttr("{}.falloffRadius".format(soft_mod[0].name()))
            center = cmds.xform(soft_mod_handle.name(), q=True, rp=True)
            vertices = self.sel[0].vtx
        else:
            bounding_box = pm.xform(selected_vertex, boundingBox=True, query=True)
            selection_radius = bounding_box_center(bounding_box)
            cluster = pm.cluster(selected_vertex, rel=True, en=1)
            radius = cmds.softSelect(q=True, ssd=True)
            center = cmds.xform(cluster[1].name(), q=True, rp=True)
            pm.delete(cluster)
            radius = selection_radius + radius
            vertices = self.sel[0].node().getParent().vtx
        vertices_weights = []
        for vertex in vertices:
            soft_select_vertex = {"index": 0,
                                  "weight": 0}
            # Get the position of the vertex
            position = vertex.getPosition(space='world')

            point1 = pm.datatypes.Point(position)
            point2 = pm.datatypes.Point(center)

            # Calculate the distance between the two points
            distance = point1.distanceTo(point2)
            # If the distance is less than the radius, select the vertex
            if distance <= radius:
                weight = abs(mel.eval("smoothstep 0 1 {}".format((distance/radius)))-1)
                soft_select_vertex["index"] = vertex.name()
                soft_select_vertex["weight"] = weight
                vertices_weights.append(soft_select_vertex)
        return vertices_weights


def enable_soft_mod():
    # set the tool mode to Soft Mod
    mel.eval('setToolTo ShowManips; performSoftMod 0 0 0 {0.0, 0.0, 0.0};')


def build_custom_control(joint, control_name):
    """
    Build Control hierarchy
    Args:
        joint(str): name of joint
        control_name(str): name of new control
    returns:
        offset_node: Offset grp of created control
    """
    offset_node = pm.createNode('transform', name="{}_GRP".format(control_name))
    curve = cmds.curve(p=[(-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
                          (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5),
                          (0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5),
                          (-0.5, 0.5, 0.5), (-0.5, -0.5, 0.5)], per=False, d=1, name="{}_CTL".format(control_name), )
    pm.parent(curve, offset_node, a=1)
    pm.matchTransform(offset_node, joint)
    pm.parentConstraint(curve, joint, mo=1, w=1)

    return offset_node


def mirror_joint(mirror_xy, mirror_yz, mirror_xz, new_joint, control_name, prefix):
    pivot_grp = pm.createNode('transform', name="mirror_pivot")
    if prefix == "R":
        mirror_joint_name = pm.createNode('joint', name=new_joint.replace("R_", "L_"))
        control_name = control_name.replace("R_", "L_")
    elif prefix == "L":
        mirror_joint_name = pm.createNode('joint', name=new_joint.replace("L_", "R_"))
        control_name = control_name.replace("L_", "R_")
    elif prefix == "B":
        mirror_joint_name = pm.createNode('joint', name=new_joint.replace("B_", "F_"))
        control_name = control_name.replace("B_", "F_")
    elif prefix == "F":
        mirror_joint_name = pm.createNode('joint', name=new_joint.replace("F_", "B_"))
        control_name = control_name.replace("F_", "B_")
    else:
        mirror_joint_name = pm.createNode('joint', name=new_joint)
    pm.matchTransform(mirror_joint_name, new_joint)
    pm.parent(mirror_joint_name, pivot_grp)
    if mirror_xy:
        pm.setAttr("{}.scaleX".format(pivot_grp.name()), -1)

    elif mirror_yz:
        pm.setAttr("{}.scaleY".format(pivot_grp.name()), -1)

    elif mirror_xz:
        pm.setAttr("{}.scaleZ".format(pivot_grp.name()), -1)
    pm.makeIdentity(pivot_grp, apply=True, t=1, r=1, s=1, n=0, pn=1)
    pm.parent(mirror_joint_name, w=1)
    pm.delete(pivot_grp)
    return mirror_joint_name.name(), control_name


def get_skin_cluster(geo):
    """
    Gets skin cluster attached to
    Args:
        geo(pynode): node to get skin cluster off

    Returns:
    """
    deformer = pm.listHistory(geo, type='skinCluster')[0]
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