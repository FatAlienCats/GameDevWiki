"""
jb_reset_to_bind.py

For rig use. Resets the rig to bind pose and removes all animation from rig.

Auther: Julian Beiboer
Date Created(dd/mm/yy): 22/03/23
"""
import pymel.core as pm
import mutils


def return_rig_to_bind():
    """
    Resets the rig to bind pose and removes all animation from rig.
    """
    default_pose = "/mnt/production-data/StudioLibrary/BBF/Library/z_Misc/BindPoseAllControls.pose/pose.json"
    sel = pm.selected()
    namespace = sel[0].namespace().replace(":", "")
    pm.currentTime(1001)
    pose = mutils.Pose.fromPath(default_pose)
    pose.load(namespaces=[namespace])
    rig_nodes = pm.ls(type=["animLayer"])
    pm.delete(rig_nodes)
    clear_anim_on_rig()


def clear_anim_on_rig():
    """
        Clears all the animations on the transforms with the suffix _CTL
    """
    attr_vs_default_value = {'sx': 1, 'sy': 1, 'sz': 1, 'rx': 0, 'ry': 0, 'rz': 0, 'tx': 0, 'ty': 0, 'tz': 0}

    sel = pm.selected()[0]

    controls = get_all_objects_with_suffix(ctl_type='transform', suffix="_CTL")
    for ctl in controls:
        anim_curves = pm.keyframe(ctl, q=True, name=True)
        for curve in anim_curves:
            pm.delete(curve)
            for attr in attr_vs_default_value:
                try:
                    pm.setAttr('{0}.{1}'.format(ctl, attr), attr_vs_default_value[attr])
                except:
                    pass


def get_all_objects_with_suffix(ctl_type, suffix):
    """
        Searches the scene and finds all transforms that end with the given suffix under a given group.
    Args:
        ctl_type(str): transform type to search for.
        suffix(str): suffix to look for.
    Returns: A list of transform nodes that end with a given suffix and are children of a given group.
    """
    # control specific atm
    objects = []
    for obj in pm.ls(type=ctl_type):
        if obj.name().endswith(suffix):
            objects.append(obj)
    return objects
