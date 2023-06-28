"""
m_file
Tools relating to the file manipulation: save, load, export, import, etc
Auther: Julian Beiboer
"""
import pymel.core
import os
import tempfile
import maya.cmds
import logging

import logging
logging.basicConfig()
logger = logging.getLogger('m_file')
logger.setLevel(logging.DEBUG)


def temp_export():
    """
    Saves a temp .ma file to your computers temp folder
    :return:
    """
    sel = pymel.core.selected()
    file_path = tempfile.gettempdir()
    pymel.core.cmds.file("{0}\exportTemp.mb".format(file_path), force=True, options='v=0', typ="mayaBinary", pr=True, es=True)


def temp_import():
    """Imports temp file from your temp folder"""
    file_path = tempfile.gettempdir()
    pymel.core.cmds.file("{0}\exportTemp.mb".format(file_path), i=True, typ="mayaBinary", options="v=0;", pr=True,
                         ra=True, ignoreVersion=True, mergeNamespacesOnClash=True, namespace="temp")


def save_increment_scene():
    # Get the current scene name
    current_scene = maya.cmds.file(q=True, sceneName=True)

    # Get the new scene name
    new_scene_name = increment_scene_number(current_scene)

    # Save the new scene
    maya.cmds.file(rename=new_scene_name)
    maya.cmds.file(save=True, type='mayaAscii')

    logger.info(f'Saved new scene: {new_scene_name}')


def increment_scene_number(current_scene):
    """
    Takes current scene and returns the new scene with incremented name
    """
    base_name, ext = os.path.splitext(current_scene)
    parts = base_name.split('-')
    number_str = parts[-1]
    number = int(number_str) + 1
    new_number_str = f'{number:05d}'
    parts[-1] = new_number_str
    new_base_name = '-'.join(parts)
    new_scene_name = f'{new_base_name}{ext}'

    return new_scene_name
