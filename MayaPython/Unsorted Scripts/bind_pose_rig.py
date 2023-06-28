import mutils
import pymel as pm


def return_rig_to_bind():
    default_pose = "/mnt/production-data/Dreamlight/BBF/Library/JulianB/DefaultPose.pose/pose.json"
    controls = get_all_objects_with_suffix(ctl_type='transform', suffix="CTL")

    pm.currentTime(1001)
    pose = mutils.Pose.fromPath(default_pose)
    pose.load(objects=controls)
    rig_nodes = pm.ls(type=["animLayer"])
    pm.delete(rig_nodes)
    clear_anim_on_rig()


def clear_anim_on_rig():
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


if __name__ == "__main__":
    return_rig_to_bind()