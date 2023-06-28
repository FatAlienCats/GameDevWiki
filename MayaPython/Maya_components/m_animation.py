"""
m_animation
Tools relating to the animation
Auther: Julian Beiboer
"""
import pymel.core
import os
import tempfile
import maya.cmds
import logging
import mutils
import m_select
import logging
logging.basicConfig()
logger = logging.getLogger('m_animation')
logger.setLevel(logging.DEBUG)


def clear_key_frames(sel):
    if not sel:
        sel = pymel.core.selected()
    for s in sel:
        attr = s.listAttr(k=True)
        for a in attr:
            pymel.core.cutKey(a)


def return_rig_to_bind(default_pose):
    """
    Resets the rig to bind pose and removes all animation from rig.
    """
    default_pose = "/mnt/production-data/StudioLibrary/BBF/Library/z_Misc/BindPoseAllControls.pose/pose.json"
    sel = pymel.core.selected()
    namespace = sel[0].namespace().replace(":", "")
    pymel.core.currentTime(1001)
    pose = mutils.Pose.fromPath(default_pose)
    pose.load(namespaces=[namespace])
    rig_nodes =  pymel.core.ls(type=["animLayer"])
    pymel.core.delete(rig_nodes)
    clear_anim_on_rig()


def clear_anim_on_rig():
    """
        Clears all the animations on the transforms with the suffix _CTL
    """
    attr_vs_default_value = {'sx': 1, 'sy': 1, 'sz': 1, 'rx': 0, 'ry': 0, 'rz': 0, 'tx': 0, 'ty': 0, 'tz': 0}

    sel = pymel.core.selected()[0]

    controls = m_select.get_all_objects_with_suffix(ctl_type='transform', suffix="_CTL")
    for ctl in controls:
        anim_curves =  pymel.core.keyframe(ctl, q=True, name=True)
        for curve in anim_curves:
            pymel.core.delete(curve)
            for attr in attr_vs_default_value:
                try:
                     pymel.core.setAttr('{0}.{1}'.format(ctl, attr), attr_vs_default_value[attr])
                except:
                    pass