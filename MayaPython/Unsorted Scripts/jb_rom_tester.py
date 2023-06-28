"""
jb_rom_tester.py

This module allows for easy non-destructive testing of a rigs range of motion(rom). It creates an anim layer and
applies the Calisthenics animation from the studio library to the selected rig.

Auther: Julian Beiboer
Date Created(dd/mm/yy): 27/02/23
"""
import pprint

import pymel.core as pm
import mutils  # studio library tools
import logging
logging.basicConfig()
logger = logging.getLogger('RiggingTools')
logger.setLevel(logging.DEBUG)

ANIM = '/mnt/production-data/StudioLibrary/BBF/Library/z_Misc/Calisthenics/Betty_Calisthenics.anim'


def apply_rom_to_rig():
    """
    This function applies the Calisthenics animation to the rig.
    """
    set_time_range(1001, 1945)
    controls = get_all_objects_with_suffix(ctl_type='transform', parent_grp='body_rig_GRP', suffix="_CTL")
    create_anim_layer()
    load_studio_library_anim(ANIM, controls)


def remove_rom_from_rig():
    """
    Removes the ROM animations from the rig and removes the temporary layer.
    """

    pm.currentTime(1001)
    rig_nodes = pm.ls(type=["animLayer"])
    print(rig_nodes)
    filtered_nodes = [node for node in rig_nodes if "rig_rom_layer" in node.name().lower()]
    pm.delete(filtered_nodes)
    set_time_range()


def get_parents(control):
    """
    Gets parent nodes of a given node
    Args:
        control(node): child node to find all parents of.

    Returns: A list of all the nodes above the given child node.

    """
    parent_node = control.getParent()
    parent_names = []
    while parent_node is not None:
        # Add the name of the parent node to the list
        parent_names.append(parent_node.name())
        # Get the next parent node
        parent_node = parent_node.getParent()

    return parent_names


def get_all_objects_with_suffix(ctl_type, parent_grp, suffix):
    """
        Searches the scene and finds all transforms that end with the given suffix under a given group.
    Args:
        ctl_type(str): transform type to search for.
        parent_grp(str): parent group it must be a child of.
        suffix(str): suffix to look for.

    Returns: A list of transform nodes that end with a given suffix and are children of a given group.

    """
    # control specific atm
    objects = []

    for obj in pm.ls(type=ctl_type):
        if obj.name().endswith(suffix):
            if parent_grp in get_parents(obj):
                objects.append(obj)

    pm.select(objects)
    return objects


def set_time_range(start=1001, end=1045):
    """
    Adjusts time range on time-slider based on input.
    Args:
        start(int): start frame for time slider
        end(int): end frame for time slider
    """
    pm.playbackOptions(e=True, minTime=start, maxTime=end, animationStartTime=start, animationEndTime=end,)


def create_anim_layer():
    """
    Creates a new anim layer and sets it to the selected layer.
    """
    pm.animLayer("rig_rom_layer", override=True, weight=1, solo=False, mute=False,
                 addSelectedObjects=True, selected=True, prf=True)


def load_studio_library_anim(anim_path, rig_controls):
    """
    Loads given animation path onto controls.
    Args:
        anim_path(string): path to stored animation
        rig_controls(list(transforms)): Rig controls to apply animation to.
    """
    anim = mutils.Animation.fromPath(anim_path)
    anim.load(objects=rig_controls,
              namespaces=None)



