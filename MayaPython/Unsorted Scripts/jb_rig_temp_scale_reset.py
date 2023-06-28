"""
jb_rig_temp_scale_reset.py

Toggles on and off a temporary scale adjustment to the rig hierarchy to allow for accurate face builds to be applied to
pre-built rigs. Only for use on rigs that have been scaled up due to model size inconsistencies.

Auther: Julian Beiboer
Date Created(dd/mm/yy): 27/02/23
"""

import pymel.core as pm


def scale_quick_fix():
    """
    Creates a temporary scale adjustment to the rig hierarchy to allow for accurate face builds to be applied to
    pre-built rigs.
    """
    # Get nodes needed
    scale_grp = pm.PyNode("global_scale_GRP")
    guides = pm.PyNode("guides")
    scale_constraint_name = guides + 'ScaleFixTemp_scaleConstraint'
    stored_value_name = "ScaleFixTemp_StoredValue_TEMP"

    # if no stored_value_name in scene make one and adjust size
    if not pm.objExists(scale_constraint_name):
        scale = scale_grp.getScale()  # store the scale for later use
        stored_value = pm.nt.Transform(name=stored_value_name)  # create a new node to store value
        stored_value.setScale(scale)

        # create scale constraint
        scale_constraint = pm.scaleConstraint(scale_grp, guides,
                                              mo=True, weight=1, name=scale_constraint_name)
        pm.parent(scale_constraint, stored_value)
        # scale down global_scale_GRP to 1
        new_scale = (1, 1, 1)
        scale_grp.setScale(new_scale)

    # else reset size based off storedValue and delete temporary node
    else:
        stored_value = pm.PyNode(stored_value_name)
        scale_grp.setScale(stored_value.getScale())
        pm.delete(stored_value)


if __name__ == "__main__":
    scale_quick_fix()
