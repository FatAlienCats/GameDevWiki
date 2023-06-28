import json
#import publish
import os
import maya.cmds as cmds
#import animModules
#import mutils  # studio library tools
import pymel.core as pm
from kore import shotgrid, authorization, utils
from MayaTools import studio_library_utils
import quick_fixes
import logging
logging.basicConfig()
logger = logging.getLogger('BATCH_FBX')
logger.setLevel(logging.DEBUG)

CROWD_CHARACTERS = ['adultA_main', 'adultB_main', 'adultC_main', 'adultD_main', 'adultE_main', 'adultF_main',
                    'adultG_main', 'adultH_main', 'adultI_main', 'adultK_main', 'adultJ_main', 'kidA_main',
                    'kidD_main', 'kidD_backpack', 'kidE_main', 'kidF_main', 'kidH_main', 'kidH_backpack', 'kidL_main',
                    'kidM_main', 'kidB_main', 'kidB_backpack', 'kidB_helmet', 'kidC_main', 'kidC_backpack',
                    'kidG_main', 'kidG_helmet', 'kidI_main', 'kidI_helmet', 'kidJ_main', 'kidJ_gym', 'kidK_main',
                    'normalDad_main', 'normalKid_main', 'normalMum_main', 'contestantA_main', 'contestantB_main',
                    'contestantC_main', 'contestantD_main', 'contestantE_main', 'contestantF_main', 'contestantG_main',
                    'contestantH_main', 'contestantI_main', 'contestantJ_main', 'cranialMonkA_main',
                    'cranialMonkB_main', 'cranialMonkC_main', 'cupcakeCreature_main', 'blobMagi_main',
                    'kittenHead_prop', 'Knucklehead_main', 'snackVendor_main', 'magiA_main', 'magiB_main',
                    'magiC_main', 'magiD_main', 'magiE_main', 'magiF_main', 'magiG_main', 'magiH_main',
                    'loyalistB_main', 'loyalistC_main', 'loyalistD_main', 'loyalistE_main', 'loyalistF_main',
                    'loyalistG_main', 'loyalistH_main', 'loyalistA_main', 'clefA_main', 'clefB_main', 'clefC_main',
                    'clefD_main', 'clefE_main', 'clefF_main', 'clefG_main', 'clefH_main', 'clefI_main', 'clefJ_main',
                    ]

ADULTS = ['adultA_main', 'adultB_main', 'adultC_main', 'adultD_main', 'adultE_main', 'adultF_main',
                         'adultG_main', 'adultH_main', 'adultI_main', 'adultK_main', 'adultJ_main']
KIDS = ['kidA_main', 'kidD_main', 'kidD_backpack', 'kidE_main', 'kidF_main', 'kidH_main', 'kidH_backpack', 'kidL_main',
        'kidM_main', 'kidB_main', 'kidB_backpack', 'kidB_helmet', 'kidC_main', 'kidC_backpack',
        'kidG_main', 'kidG_helmet', 'kidI_main', 'kidI_helmet', 'kidJ_main', 'kidJ_gym', 'kidK_main']
NORMAL = ['normalDad_main', 'normalKid_main', 'normalMum_main']

CONTESTANTS = ['contestantA_main', 'contestantB_main', 'contestantC_main', 'contestantD_main', 'contestantE_main',
               'contestantF_main', 'contestantG_main', 'contestantH_main', 'contestantI_main', 'contestantJ_main']
CRANIAL = ['cranialMonkA_main', 'cranialMonkB_main', 'cranialMonkC_main']

MISC = ['cupcakeCreature_main', 'blobMagi_main', 'kittenHead_prop', 'Knucklehead_main', 'snackVendor_main']

MAGI = ['magiA_main', 'magiB_main', 'magiC_main', 'magiD_main', 'magiE_main', 'magiF_main', 'magiG_main', 'magiH_main']

LOYALISTS = ['loyalistB_main', 'loyalistF_main']
            # 'loyalistB_main', 'loyalistC_main', 'loyalistD_main', 'loyalistE_main', 'loyalistF_main', 'loyalistG_main',
            # 'loyalistH_main', ]

CLEF = ['clefA_main', 'clefB_main', 'clefC_main', 'clefD_main', 'clefE_main', 'clefF_main', 'clefG_main', 'clefH_main',
        'clefI_main', 'clefJ_main']

#TEST_CROWD_CHARACTERS = ["Spherery_test"]
TEST_CROWD_CHARACTERS = ['adultA_main', 'adultB_main']
#BASE_PATH = "/mnt/production-data/projects/BBF/scene/z_TestSpherery/z_TestSpherery-0010/animation/checkin/00005/Spherery_test-geo.abc"

BASE_PATH = "/mnt/production-data/projects/BBF/asset/character" #Spherery_test/rigging/default/checkin/00004/Spherery_test.ma"


def export_fbx(file_path):
    """
    Exports selected as fbx into the same file path as original abc export
    Returns:
        Path(str): Path of new fbx file
    """
    cmds.file(file_path, force=True, options="", typ="FBX export", pr=True, es=True)
    #file -force -options "" -typ "FBX export" -pr -es "/home/julianbeiboer/Desktop/test.fbx";


def batch_anim_cycle_fbx_exporter(cycle_name, group):
    cmds.refresh(suspend=True)
    for character in LOYALISTS:
        cmds.file(force=True, new=True)

        asset = get_asset_data(character)
        asset_versions = find_asset_versions(asset["entity"]["name"], asset["code"], asset["submission_type"])
        latest_asset = asset_versions[-1]
        replacement_filepath = asset["filepath"].replace(asset["version"], latest_asset)
        import_file = utils.getEnvPath(replacement_filepath)
        print(import_file)
        cmds.file(import_file, i=True, )

        cmds.select("model", "M_hips_JNT")
        # delete FFDs
        if cmds.objExists('ffd1'):
            cmds.delete('ffd1')
        # replace with anim cycle name
        orig_fbx_file = import_file.replace(".ma", ".fbx")
        fbx_file = orig_fbx_file.replace(character, "{}_{}".format(character, cycle_name))
        fbx_file = "/mnt/user-share/julianbeiboer/Crowd/Cycles/{0}/{1}".format(group, fbx_file.split('/')[-1])
        print(fbx_file)
        #/mnt/user-share/julianbeiboer/Crowd/Cycles/Adults/

        # apply animation
        anim_path = "/mnt/production-data/Dreamlight/BBF/Library/JulianB/Crowd_Cycles/{0}.anim".format(cycle_name)
        namespace = pm.selected()[0].namespace().replace(":", "")
        print(anim_path, namespace)
        controls = quick_fixes.get_all_objects_with_suffix(ctl_type='transform', suffix="_CTL")
        #/mnt/production-data/Dreamlight/BBF/Library/JulianB/Crowd_Cycles/Loyalists_cheeringCycle.anim
        studio_library_utils.load_anim(anim_path, controls)
        #set Frame range
        keyframes = cmds.keyframe(controls, query=True)
        sorted_keyframes = sorted(keyframes)
        cmds.playbackOptions(min=sorted_keyframes[0], max=sorted_keyframes[-1])
        # bake animation onto joints
        pm.bakeResults(quick_fixes.select_all("JNT", "joint",False, True), sampleBy=1, sm=True, #sr=[False, 5],
                       time=[sorted_keyframes[0], sorted_keyframes[-1]], oversamplingRate=1,
                       disableImplicitControl=1, preserveOutsideKeys=1, sparseAnimCurveBake=0,
                       removeBakedAttributeFromLayer=0, removeBakedAnimFromLayer=0, bakeOnOverrideLayer=0,
                       minimizeRotation=1, controlPoints=0, shape=1)
        #quick_fixes.bake_selected(quick_fixes.select_all("JNT", "joint"))
        cmds.refresh(suspend=False)
        cmds.select("model", "M_hips_JNT", r=1)
        export_fbx(fbx_file)


def batch_rig_fbx_exporter():
    """
    This function is called in maya or in standalone version
    Returns:

    """
    # List of characters to export
    # in FOR LOOP
    # base path to checked in version of rig
    # get the latest version
    # pull the latest version into empty scene
    # remove any namespaces
    # remove ffd deformers
    # select Model grp and root joint
    # export FBX

    for character in LOYALISTS:
        cmds.file(force=True, new=True)
        asset = get_asset_data(character)
        asset_versions = find_asset_versions(asset["entity"]["name"], asset["code"], asset["submission_type"])
        latest_asset = asset_versions[-1]
        replacement_filepath = asset["filepath"].replace(asset["version"], latest_asset)
        import_file = utils.getEnvPath(replacement_filepath)
        print(import_file)
        cmds.file(import_file, i=True)

        cmds.select("model", "M_hips_JNT")
        # delete FFDs
        if cmds.objExists('ffd1'):
            cmds.delete('ffd1')
        #cmds.select("model", "M_body_JNT")
        fbx_file = import_file.replace(".ma", ".fbx")
        export_fbx(fbx_file)


def select_root_joint():
    # Get all joints in the scene
    joints = cmds.ls(type='joint')

    if not joints:
        print("No joints found in the scene.")
        return

    # Find the joint with no parent (root joint)
    root_joint = None
    for joint in joints:
        print()
        if cmds.listRelatives(joint, parent=True, type='transform'):
            root_joint = joint
            return root_joint


def get_asset_data(character):
    rig_file = "{0}/{1}/rigging/default/checkin/{2}/{1}.ma".format(BASE_PATH, character, "00001")
    manifest_file = rig_file.replace(rig_file.split("/")[-1], "manifest.json")
    asset_data = extract_asset_manifest_data(manifest_file)
    version_number = rig_file.split("/")[-2]
    code = asset_data["Task"]["content"]
    entity = asset_data["Task"]["entity"]
    asset_stored_data = {"reference_name": character,
                         "filepath": rig_file,
                         "entity": entity,
                         "code": code,
                         "submission_type": "checkin",
                         "version": version_number,
                         "latest_version": ""}

    return asset_stored_data


def extract_asset_manifest_data(filepath):
    """
    Reads the manifest file and returns a dictionary of data
    Args:
        filepath(str): path the manifest.json file

    Returns: A dictionary of data for the asset
    """
    filename = os.path.expandvars(filepath)  # Expands $Variables to a full path
    with open(filename, 'r') as f:
        asset_data = json.load(f)
    return asset_data


def find_asset_versions(asset_code, task_name, sub_type):
    """
    Finds all the asset checked in versions for a given character's task.
    Args:
        asset_code(str): characters name in the pipeline
        task_name(str): task type that the asset belongs to
        sub_type(str): submission type of asset -> submit or checkin
    Returns: a list of version numbers for the asset provided

    """
    with authorization.ShotGrid() as sg:
        session = shotgrid.Session(sg)
        asset = session.findAsset(asset_code, fields=["id"])
        criteria = [
            ["project", "is", session.getPrjectContext()],
            ["entity", "is", asset],
            ["content", "is", task_name],
        ]

        task = session.find("Task", filters=criteria, fields=["content"], first=True)
        versions = session.findVersions(task, fields=["code"], publishType=sub_type)
        return [version["code"] for version in versions]