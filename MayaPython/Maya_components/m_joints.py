"""
m_joints
Tools relating to the joint manipulation
Auther: Julian Beiboer
"""
import pymel.core
import os
import tempfile
import maya.cmds
import logging

import logging
logging.basicConfig()
logger = logging.getLogger('m_joints')
logger.setLevel(logging.DEBUG)


def toggle_all_orientation_axis(value):
    """
    Toggles orientation axis on all joints in scene
    Args:
        value(bool): True or False
    """
    joints = maya.cmds.ls(type='joint')
    for joint in joints:
        maya.cmds.setAttr("{}.displayLocalAxis".format(joint), value)


def get_jnts_on_skin_cluster(select=False):
    """
    Gets all the joints assigned to selected meshes skin cluster and selects those jnts
    Args:
        select(bool): select jnts from cluster
    Returns:
        jnts(list[str]): list of joint names
    """
    sel = pymel.core.selected()[0]
    deformers = pymel.core.listHistory(sel, type='skinCluster')[0]
    jnts = pymel.core.skinCluster(deformers, q=1, influence=1)
    if select:
        pymel.core.select(jnts, r=1)
    logger.info(jnts)
    return jnts


def flood_select_to_jnt():
    """Select the jnt and the verts and flood the values of the verts to be 1 for that joint
    needs worl
    """
    sel = pymel.core.selected()
    deformer = pymel.core.listHistory(pymel.core.selected()[0], type='skinCluster')[0]

    #cmds.skinPercent(deformer, sel, transformValue=[(new_joint, sel)], r=True)
    pass


def create_joint_on_each_vertex(world_parent=False):
    """
    Creates a joint on each vertex selected
    Args:
        world_parent:

    Returns:

    """
    # TODO: Test out as it may not be working
    sel = pymel.core.selected()
    for s in sel:
        joints = pymel.core.createNode('joint', ss=1)
        pymel.core.matchTransform(joints, s)
        # pymel.core.delete(pymel.core.parentConstraint(s, joints, mo=0))
        if not world_parent:
            pymel.core.parent(joints, s)
            parent_transform = joints.getParent()
            pymel.core.makeIdentity(parent_transform, apply=True, s=1, t=1, r=1, n=0, pn=1)
            pymel.core.parent(joints, s)
            if parent_transform.type() == "transform":
                pymel.core.delete(parent_transform)


def create_joint_from_selection():
    """
    Create a joint at the center point of the selection using a cluster deformer to get the center point.
    """

    sel = maya.cmds.ls(sl=True)
    cluster = maya.cmds.cluster(sel, rel=True, en=1)
    joints = maya.cmds.createNode('joint', ss=1)
    maya.cmds.delete(maya.cmds.parentConstraint(cluster, joints, mo=False), cluster)


def add_joint_to_hierarchy(has_parent_constraint=False):
    sel = pymel.core.selected()
    child = sel[0]

    print(child)
    if has_parent_constraint:
        constraints = child.listConnections(type='parentConstraint')[0]
        source_object = constraints.listConnections(source=True, plugs=False)[0]
        destination_object = constraints.listConnections(destination=True, plugs=False)[0]

        parent = source_object
        pymel.core.delete(constraints)
    else:
        print("reree")
        parent = sel[1]
    print(child, parent, destination_object)

    child.setParent(parent)

def parent_all_to_last():
    sel = pymel.core.selected()
    for s in sel:
        if s != sel[-1]:
            s.setParent(sel[-1])


