import maya.cmds as cmds
from pipe.widgets import publish
import os
import animModules
import pymel.core as pm
import mutils

basePath = "/mnt/production-data/projects/BBF/asset/prop/"

test =["z_TestAsset"]
rigs =[
#"arrow_bad",
#"arrow_main",
#"coach_main",
"coach_reigns",
"coach_skis",
"crossbow_2",
"crossbow_3",
"crossbow_main",
"direWolfReigns_main",
"ext_eurasianSteppe_main",
"fryPan_main",
"grapplingHook_main",
"iceChunk_main",
"machineGun_main",
"pan_main",
"pot_main",
"rock_main",
"rockChunk_main",
"sandwich_bullfrog",
"skidoo_main",
"skidoo_sidecar",
"treePineA_main",
"violaNerlin_main",
]
def main():
    #import maya.standalone
    #maya.standalone.initialize()
    #import maya.mel as mm
    #print(mm.eval("getenv MAYA_SCRIPT_PATH"))
    for rig in rigs:
        # Get working director of character and laster maya save
        work_directory = "{0}/{1}/{2}".format(basePath, rig, "rigging/default/work")  # Change for testing

        maya_file = get_latest_version(work_directory)
        print(maya_file, work_directory)

        cmds.file('{0}/{1}'.format(work_directory, maya_file), o=True, f=True)

        #do thing
        pm.setAttr("model.inheritsTransform", 0)
        pm.setAttr("deformers.inheritsTransform", 0)
        print(rig + "--DONE--"+"Model = "+pm.getAttr("model.inheritsTransform")+"deformers = "+pm.getAttr("deformers.inheritsTransform"))
        save_increment_scene()
        #submit_to_farm()


def submit_to_farm():
    # WIP not currently used
    farm = publish.PublishTab.SubmitToFarm()
    farm.execute()

def save_increment_scene():
    # Get the current scene name
    current_scene = cmds.file(q=True, sceneName=True)

    # Get the new scene name
    new_scene_name = animModules.increment_scene_number(current_scene)

    # Save the new scene
    cmds.file(rename=new_scene_name)
    cmds.file(save=True, type='mayaAscii')

    print(f'Saved new scene: {new_scene_name}')

def get_latest_version(directory):
    versions = os.listdir(directory)
    versions.sort()
    latest_version = versions[-1]
    return latest_version


if __name__ == "__main__":
    main()