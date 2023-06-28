import maya
import maya.cmds as mc
from maya import cmds, OpenMaya
import math
import pymel.core as pm
import logging

logging.basicConfig()

logger = logging.getLogger('RiggingTools')

logger.setLevel(logging.DEBUG)

"""
    Notes:
    1. (DONE!)Need to add clavicle to check list as animators will select it a run the script
    2. (DONE)Add timeline and set key on new controls
    3. (On HOLD)Find a way to accommodate custom rigs like staniel 
    4. (DONE)Fix the match Loc so that it lines up with the IK hand and foot for accurate FK -> IK
    5. Toe need to match
"""
MOVEMENT_ATTR = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]

# Bespoke Rigs
BESPOKE_CHAR_RIGS = ["Staniel", "Volos"]


class IkFkSwitcher:
    selected = None
    frame_range = None
    number_of_loops = None
    frame_before = None

    def __init__(self):
        if pm.selected():
            self.selected = pm.selected()  # Gets selected object
        else:
            logger.log(logging.ERROR, "No control selected")
            return

        self.frame_range, self.number_of_loops, self.frame_before = get_frame_range_selected()
        cmds.undoInfo(openChunk=True)
        self.execute()
        cmds.undoInfo(closeChunk=True)

    def execute(self):
        for sel in self.selected:
            namespace = sel.namespace()  # gets namespace from pynode

            if len(namespace) >= 1:
                split_up_name = sel.name().split(":")[1].split("_")
                logger.log(logging.DEBUG, "Character Rig: {0} found".format(namespace))
            else:
                split_up_name = sel.name().split("_")
                logger.log(logging.WARNING,
                           "There is no namespace on this rig. Animation rigs should be referenced into scenes not imported")

            # check name of character and if it is a bespoke or standard humanoid
            character_name = namespace.split("_")[0]  # e.g. splits Betty_main into Betty

            side = split_up_name[0]
            if character_name in BESPOKE_CHAR_RIGS:
                logger.log(logging.WARNING, "Bespoke")
                if character_name == "Staniel":
                    logger.log(logging.WARNING, "Staniel Rig(bespoke rig), IK/FK switching not yet setup")
                elif character_name == "Volos":
                    logger.log(logging.INFO, "Volos Rig(bespoke rig), IK/FK switching not yet setup")

            else:
                logger.log(logging.INFO, "Humanoid Rig")
                fk_controls, ik_controls, ik_jnts, settings_ctrl = get_limb_type_humanoid(namespace, sel, side)
                self.humanoid_ikfk_switch(fk_controls, ik_controls, ik_jnts, namespace, settings_ctrl, side)


    def humanoid_ikfk_switch(self, fk_controls, ik_controls, ik_jnts, namespace, settings_ctrl, side):
        """
        Checks if arm or leg is in ik or fk and runs the switcher
        Args:
            fk_controls(list[str]): fk controls to use
            ik_controls(list[str]): ik controls to use
            ik_jnts(list[str]): ik jnts to use
            namespace(str): namespace of selected rig
            settings_ctrl(str): IKFK switcher control
            side(str): side prefix
        """
        # Check if Settings set to IK or FK
        if pm.getAttr(settings_ctrl + ".FkIk") < 0.5:  # fk

            self.switch_to_ik(namespace=namespace, side=side, fk_ctrls=fk_controls, ik_ctrls=ik_controls,
                              settings_ctrl=settings_ctrl)

        else:
            self.switch_to_fk(namespace=namespace, side=side, fk_ctrls=fk_controls, ik_jnts=ik_jnts,
                              settings_ctrl=settings_ctrl)

    def switch_to_fk(self, namespace, side, fk_ctrls, ik_jnts, settings_ctrl):
        """
        Checks if arm or leg is in ik or fk and runs the switcher
        Args:
            namespace(str): namespace of selected rig
            side(str): side prefix
            fk_ctrls(list[str]): fk controls to use
            ik_jnts(list[str]): ik jnts to use
            settings_ctrl(str): IKFK switcher control
        """

        # Get highlighted time range

        set_frame_before(settings_ctrl=settings_ctrl, frame_before=self.frame_before,
                         ikfk_value=1)  # key setting control before transition to ensure earlier anim not effected.

        pm.currentTime(self.frame_range[0])  # set current time back to start of range

        for x in range(int(self.number_of_loops)):
            current_frame = pm.currentTime(q=True)
            # switch IK control to FK control
            for ctrl, jnt in zip(fk_ctrls, ik_jnts):
                target = "{0}{1}_{2}".format(namespace, side, ctrl)
                source = "{0}{1}_{2}".format(namespace, side, jnt)
                mc.matchTransform(target, source, scale=False)
                pm.setKeyframe(pm.PyNode(target), attribute=MOVEMENT_ATTR)

            setting_ctrl_node = pm.PyNode(settings_ctrl)
            setting_ctrl_node.FkIk.set(0)
            pm.setKeyframe(setting_ctrl_node, attribute="FkIk")

            next_frame(self.number_of_loops, current_frame, self.frame_range)

            logger.log(logging.DEBUG, "SUCCESS! IK pose converted to FK pose")
        pm.currentTime(self.frame_range[0])

    def switch_to_ik(self, namespace, side, fk_ctrls, ik_ctrls, settings_ctrl):
        """
        Switched FK controls to IK
        Args:
            namespace: namespace of the rig
            side: side prefix
            fk_ctrls(list[str]): fk controls
            ik_ctrls(list[str]): ik controls
            settings_ctrl: setting control
        """
        # Switch FK pose to IK pose

        hand_foot_loc = "{0}{1}_{2}".format(namespace, side, ik_ctrls[0])
        hand_foot_ctl = "{0}{1}_{2}".format(namespace, side, ik_ctrls[1])
        pole_vector_ctl = "{0}{1}_{2}".format(namespace, side, ik_ctrls[2])

        top_fk_ctrl = "{0}{1}_{2}".format(namespace, side, fk_ctrls[0])
        mid_fk_ctrl = "{0}{1}_{2}".format(namespace, side, fk_ctrls[1])
        end_fk_ctrl = "{0}{1}_{2}".format(namespace, side, fk_ctrls[2])

        set_frame_before(settings_ctrl=settings_ctrl, frame_before=self.frame_before, ikfk_value=0)

        pm.currentTime(self.frame_range[0])  # set current time back to start of range
        for x in range(int(self.number_of_loops)):
            current_frame = pm.currentTime(q=True)
            mc.matchTransform(hand_foot_ctl, hand_foot_loc, scale=False)

            start = cmds.xform(top_fk_ctrl, q=1, ws=1, t=1)
            mid = cmds.xform(mid_fk_ctrl, q=1, ws=1, t=1)
            end = cmds.xform(end_fk_ctrl, q=1, ws=1, t=1)

            dist_value = 5

            start_v = OpenMaya.MVector(start[0], start[1], start[2])
            mid_v = OpenMaya.MVector(mid[0], mid[1], mid[2])
            end_v = OpenMaya.MVector(end[0], end[1], end[2])
            start_end = end_v - start_v
            start_mid = mid_v - start_v
            dot_p = start_mid * start_end
            proj = float(dot_p) / float(start_end.length())
            start_end_n = start_end.normal()
            proj_v = start_end_n * proj
            arrow_v = start_mid - proj_v
            arrow_v *= dist_value
            final_v = arrow_v + mid_v
            cross1 = start_end ^ start_mid
            cross1.normalize()
            cross2 = cross1 ^ arrow_v
            cross2.normalize()
            arrow_v.normalize()
            matrix_v = [arrow_v.x, arrow_v.y, arrow_v.z, 0,
                        cross1.x, cross1.y, cross1.z, 0,
                        cross2.x, cross2.y, cross2.z, 0,
                        0, 0, 0, 1]
            matrix_m = OpenMaya.MMatrix()
            OpenMaya.MScriptUtil.createMatrixFromList(matrix_v, matrix_m)
            matrix_fn = OpenMaya.MTransformationMatrix(matrix_m)
            rot = matrix_fn.eulerRotation()
            loc = cmds.spaceLocator()[0]
            cmds.xform(loc, ws=1, t=(final_v.x, final_v.y, final_v.z))
            cmds.xform(loc, ws=1, rotation=((rot.x / math.pi * 180.0),
                                            (rot.y / math.pi * 180.0),
                                            (rot.z / math.pi * 180.0)))
            mc.matchTransform(pole_vector_ctl, loc, scale=False)
            mc.delete(loc)
            for attr in ['.scaleX', '.scaleY', '.scaleZ']:
                mc.setAttr('{}{}'.format(hand_foot_ctl, attr), 1)

            pm.setKeyframe(pm.PyNode(pole_vector_ctl), attribute=MOVEMENT_ATTR)
            pm.setKeyframe(pm.PyNode(hand_foot_ctl), attribute=MOVEMENT_ATTR)

            setting_ctrl_node = pm.PyNode(settings_ctrl)
            setting_ctrl_node.FkIk.set(1)
            pm.setKeyframe(setting_ctrl_node, attribute="FkIk")

            next_frame(self.number_of_loops, current_frame, self.frame_range)

            logger.log(logging.DEBUG, "SUCCESS! FK pose converted to IK pose")
        pm.currentTime(self.frame_range[0])


def get_limb_type_humanoid(namespace, sel, side):
    """
    Takes the namespace and selected obj and returns lists of controls to apply switching to.
    Args:
        namespace(str): namespace of the rig
        sel(pyNode): selected object
        side(str): Side of the control selected
    Returns:
        fk_controls(list[str]): list of fk controls to apply changes to
        ik_controls(list[str]): list of ik controls to apply changes to
        ik_jnts(list[str]): list of ik controls to use in calculations
        settings_ctrl(str): settings control
    """
    parents = get_parents(sel)
    if "{0}{1}_{2}".format(namespace, side, "leg_rig_GRP") in parents:
        limb_type = "leg"
        settings_ctrl = "{0}{1}_{2}".format(namespace, side, '{0}_settings_CTL'.format(limb_type))
        fk_controls = ["thigh_FK_CTL", "knee_FK_CTL", "foot_FK_CTL"]
        ik_controls = ["leg_match_LOC", "foot_IK_CTL", "knee_IK_CTL"]
        ik_jnts = ["thigh_IK_JNT", "knee_IK_JNT", "foot_IK_JNT"]

    elif "{0}{1}_{2}".format(namespace, side, "arm_rig_GRP") in parents:
        limb_type = "arm"
        settings_ctrl = "{0}{1}_{2}".format(namespace, side, '{0}_settings_CTL'.format(limb_type))
        fk_controls = ["shoulder_FK_CTL", "elbow_FK_CTL", "hand_FK_CTL"]
        ik_controls = ["arm_match_LOC", "hand_IK_CTL", "elbow_IK_CTL"]
        ik_jnts = ["shoulder_IK_JNT", "elbow_IK_JNT", "hand_IK_JNT"]

    else:
        logger.log(logging.ERROR, sel + "is not apart of an IK/FK arm or leg. Please select a control on the arm "
                                        "or leg and try again")
        return
    return fk_controls, ik_controls, ik_jnts, settings_ctrl


def next_frame(number_of_loops, current_frame, frame_range):
    """
    Moves along the timeline until it reaches the total number
    Args:
        number_of_loops(int): number of frames to loop through
        current_frame(int): current frame
        frame_range(list[int]): range selected on the timeslider
    """
    if number_of_loops > 1 and current_frame < frame_range[1] - 1:
        new_frame = current_frame + 1
        pm.currentTime(new_frame)


def get_list_of_keyframes(sel, frame_range):
    """
    Find all the keyed frames within a selection range
    Args:
        sel: selected object
        frame_range(list[int]): range to find keys in
    Returns:
        keyframe(list[int]): list of keyed frames on selected
    """
    keyframes = pm.keyframe(sel, q=True, time=frame_range)
    # Remove duplicates from the list of keyframes
    keyframes = list(set(keyframes))
    keyframes.sort()
    return keyframes


def get_frame_range_selected():
    # Get the currently selected time range in the time slider
    playback_slider = maya.mel.eval('$tmpVar=$gPlayBackSlider')
    selected_range = pm.timeControl(playback_slider, q=True, ra=True)
    number_of_loops = selected_range[1] - selected_range[0]
    frame_before = selected_range[0] - 1
    return selected_range, number_of_loops, frame_before


def set_frame_before(settings_ctrl, frame_before, ikfk_value):
    setting_ctrl_node = pm.PyNode(settings_ctrl)
    setting_ctrl_node.FkIk.set(ikfk_value)
    pm.setKeyframe(setting_ctrl_node, attribute="FkIk", t=frame_before)


def get_parents(control):
    parent_node = control.getParent()
    parent_names = []
    while parent_node is not None:
        # Add the name of the parent node to the list
        parent_names.append(parent_node.name())
        # Get the next parent node
        parent_node = parent_node.getParent()

    return parent_names
