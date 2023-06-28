import datetime
import pprint
#import maya.standalone as standalone
#standalone.initialize("Python")

import json
import publish
import os
import maya.cmds as mc
import animModules
import mutils  # studio library tools
import pymel.core as pm
import logging
logging.basicConfig()
logger = logging.getLogger('RiggingTools')
logger.setLevel(logging.DEBUG)
# list of all the rigs
# find out the file path to the working version of the rigs
# Folder of characters: /mnt/production-data/projects/BBF/asset/character
#
# string format to get the correct name
#find a way to get the latest version of the rig

# open scene
# check if locators are correct
# if yes pass, if not add to list.
#print full list of effected characters

BASE_PATH = "/mnt/production-data/projects/BBF/asset/character"

DEFAULT_BIND_POSE = "/mnt/production-data/StudioLibrary/BBF/Library/z_Misc/CharFX/bindPose.pose/pose.json"
TestPath = "/mnt/user-share/julianbeiboer/TempWork/BatchTest"

OUTPUT_FILE = "/mnt/user-share/julianbeiboer/TempWork/BatchTest"

characters_to_ignore =["Spherery_test", "Staniel_formal", "Staniel_gag", "Staniel_main", "Volos_main", "Wigwam_main",
                       "direWolf_main", "direWolf_other", "fairyDrone_main", "pieMonster_main", "rainbow_main",
                       "sentientCloud_main", "squid_main", "wigwam_hat", "worm_main",  "direWolf_main",
                       "direWolf_other", "fairyDrone_main", "Howard_main", "Betty_main", "loveHeart_main",
                       "skeletalHands_main", "Knucklehead_main"]


def save_increment_scene():
    # Get the current scene name
    current_scene = mc.file(q=True, sceneName=True)

    # Get the new scene name
    new_scene_name = animModules.increment_scene_number(current_scene)

    # Save the new scene
    mc.file(rename=new_scene_name)
    mc.file(save=True, type='mayaAscii')

    print(f'Saved new scene: {new_scene_name}')


def submit_to_farm():
    # WIP not currently used
    farm = publish.SubmitToFarm()
    farm.execute()


def batch_update_match_locators(fix_issues=False, base_path="/mnt/production-data/projects/BBF/asset/character"):

    character_to_update = []
    character_to_add_match = []
    files_not_opening = []

    # Find all Characters
    characters = get_list_of_all_characters(base_path)  # change for testing
    #characters = [ "kidE_main", "kidF_main", "kidI_helmet", "kidI_main", "kidJ_gym", "kidK_main", "kidM_main"] #for testing

    for character in characters:
        if character not in characters_to_ignore:
            # Get working director of character and laster maya save
            work_directory = "{0}/{1}/rigging/default/work".format(base_path, character)  # Change for testing

            maya_file = get_latest_version(work_directory)
            if not maya_file:
                logger.log(logging.INFO, "{} no file found".format(character))
                continue
            try:
                pm.cmds.file('{0}/{1}'.format(work_directory, maya_file), o=True, f=True)
            except:
                logger.log(logging.INFO, "{} file not opening".format(character))
                files_not_opening.append(character)
                continue

            # Make sure rig is in default position
            controls = get_all_objects_with_suffix(ctl_type='transform', suffix="_CTL")

            if not does_match_loc_exist():
                character_to_add_match.append(character)

                if fix_issues:
                    create_locators(name="LOC")
                    logger.log(logging.INFO, "Created new match LOC for {}".format(character))
                    save_increment_scene()
                    #submit_to_farm()
                continue

            # Create a pose object from disc
            pm.currentTime(1001)
            pose = mutils.Pose.fromPath(DEFAULT_BIND_POSE)
            pose.load(objects=controls)
            # Create test locators
            temp_locators = create_locators(name="TEMP")

            # Compare test locators to rig locators
            if is_rig_correctly_aligned():
                logger.log(logging.INFO, "Character Rig: {0} Cleared".format(character))
                pm.delete(temp_locators)
            else:
                logger.log(logging.INFO, "Character Rig: {0} Not Cleared applying fix".format(character))
                pm.delete(temp_locators)
                character_to_update.append(character)
                if fix_issues:
                    fix_match_loc()
                    save_increment_scene()

            if not fix_issues:
                write_data_out_as_json(character_to_update, character_to_add_match, files_not_opening)


def write_data_out_as_json(characters_to_update_loc, character_to_create_loc, files_not_opening):
    # Data to be written
    total_fixes = len(characters_to_update_loc)
    total_created = len(character_to_create_loc)
    dictionary = {
        "Fix Loc": characters_to_update_loc,
        "Create Loc": character_to_create_loc,
        "File not opening": files_not_opening,
        "total fixes": total_fixes,
        "total creations": total_created
    }

    with open("{}/characterData2.json".format(OUTPUT_FILE), "w") as outfile:
        json.dump(dictionary, outfile)


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


def does_match_loc_exist():
    for side in ["L", "R"]:
        if not pm.objExists("{}_arm_match_LOC".format(side)):
            return False
        elif not pm.objExists("{}_leg_match_LOC".format(side)):
            return False
    return True


def is_rig_correctly_aligned():
    for side in ["L", "R"]:
        arm = pm.PyNode("{}_arm_match_LOC".format(side))
        leg = pm.PyNode("{}_leg_match_LOC".format(side))
        arm_temp = pm.PyNode("{}_arm_match_TEMP".format(side))
        leg_temp = pm.PyNode("{}_leg_match_TEMP".format(side))

        for real, temp in zip([arm, leg], [arm_temp, leg_temp]):
            real_rot = pm.xform(real, q=True, ro=True, ws=1)
            real_tran = pm.xform(real, q=True, t=True, ws=1)
            temp_rot = pm.xform(temp, q=True, ro=True, ws=1)
            temp_tran = pm.xform(temp, q=True, t=True, ws=1)

            for v, t in zip(real_rot, temp_rot):
                round_v = round(v, 4)
                round_t = round(t, 4)
                if round_t != round_v:
                    print("rot: {0}: {1} != {2}: {3}".format(real, round_v, temp, round_t))
                    return False
            for v, t in zip(real_tran, temp_tran):
                round_v = round(v, 2)
                round_t = round(t, 2)
                if round_t != round_v:
                    print("tran: {0}: {1} != {2}: {3}".format(real, round_v, temp, round_t))
                    return False

    return True


def create_locators(name="TEMP"):
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

        arm_loc = mc.spaceLocator(n=side + 'arm_match_{}'.format(name))
        leg_loc = mc.spaceLocator(n=side + 'leg_match_{}'.format(name))

        mc.matchTransform(arm_loc, ik_arm_control, pos=True, rot=True, scale=False)
        mc.parent(arm_loc, fk_arm_control)

        mc.matchTransform(leg_loc, ik_leg_control, pos=True, rot=True, scale=False)
        mc.parent(leg_loc, fk_leg_control)
        temp_locators.append(arm_loc)
        temp_locators.append(leg_loc)
    return temp_locators


def get_list_of_all_characters(directory):
    directories = os.listdir(directory)
    characters = []
    for d in directories:
        if os.path.isdir("{}/{}".format(BASE_PATH, d)):
            characters.append(d)
    sorted_dir = sorted(characters)
    return sorted_dir


def get_latest_version(directory):
    if os.path.exists(directory):
        versions = os.listdir(directory)
        versions.sort()
        if len(versions) > 0:
            latest_version = versions[-1]
            return latest_version
        else:
            return


def fix_match_loc():
    # rigs need to be in default position for the alignment to work correctly
    ik_loc = ["arm_match_LOC", "leg_match_LOC"]
    ik_controls = ["hand_IK_CTL", "foot_IK_CTL"]
    side = ["L_", "R_"]

    for loc, ctrl in zip(ik_loc, ik_controls):
        for s in side:
            pm.matchTransform(s + loc, s + ctrl, pos=True, rot=True, scale=False)
            logger.log(logging.DEBUG, "Matched loc:{0}{1} to {0}{2}".format(s, loc, ctrl))

if __name__ == '__main__':

    batch_update_match_locators()
