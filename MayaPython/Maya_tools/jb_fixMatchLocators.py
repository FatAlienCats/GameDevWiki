import logging

from maya import cmds as cmd

logger = logging.getLogger(__name__)


def fix_match_loc():  # Temporary fix for locator position
    # rigs need to be in default position for the alignment to work correctly
    ik_loc = ["arm_match_LOC", "leg_match_LOC"]
    ik_controls = ["hand_IK_CTL", "foot_IK_CTL"]
    side = ["L_", "R_"]
    if does_match_loc_exist():
        for loc, ctrl in zip(ik_loc, ik_controls):
            for s in side:
                cmd.matchTransform(s + loc, s + ctrl, pos=True, rot=True, scale=False)
                logger.log(logging.DEBUG, "Matched loc:{0}{1} to {0}{2}".format(s, loc, ctrl))
    else:
        create_locators()


def create_locators():
    """
    Create test locators to compare against ones currently in rig
    Returns:

    """
    temp_locators = []
    for side in ['L_', 'R_']:
        fk_arm_control = side + 'hand_FK_CTL'
        ik_arm_control = side + 'hand_IK_CTL'
        fk_leg_control = side + 'foot_FK_CTL'
        ik_leg_control = side + 'foot_IK_CTL'

        arm_loc = cmd.spaceLocator(n=side + 'arm_match_LOC')
        leg_loc = cmd.spaceLocator(n=side + 'leg_match_LOC')

        cmd.matchTransform(arm_loc, ik_arm_control, pos=True, rot=True, scale=False)
        cmd.parent(arm_loc, fk_arm_control)

        cmd.matchTransform(leg_loc, ik_leg_control, pos=True, rot=True, scale=False)
        cmd.parent(leg_loc, fk_leg_control)
        temp_locators.append(arm_loc)
        temp_locators.append(leg_loc)

    return temp_locators


def does_match_loc_exist():
    for side in ["L", "R"]:
        if not cmd.objExists("{}_arm_match_LOC".format(side)):
            return False
        elif not cmd.objExists("{}_leg_match_LOC".format(side)):
            return False
    return True

if __name__ == "__main__":
    fix_match_loc()
