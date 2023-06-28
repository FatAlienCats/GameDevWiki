import mutils

def load_anim(anim_path, controls):
    """
    Loads given animation path onto controls.
    Args:
        anim_path(string): path to stored animation
        rig_controls(list(transforms)): Rig controls to apply animation to.
    """

    anim = mutils.Animation.fromPath(anim_path)
    anim.load(objects=controls, namespaces=None)


def load_pose(pose_path, namespace):
    pose = mutils.Pose.fromPath(pose_path)
    pose.load(namespaces=[namespace])
