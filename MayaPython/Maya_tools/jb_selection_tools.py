"""
m_select
Tools relating to the selection of assets in maya.
Auther: Julian Beiboer
"""
import pymel.core
import maya.cmds
import logging
logging.basicConfig()
logger = logging.getLogger('m_select')
logger.setLevel(logging.DEBUG)


def get_all_objects_with_suffix(ctl_type, suffix, select=False, in_selection=False):
    """
        Searches the scene and finds all transforms that end with the given suffix under a given group.
    Args:
        ctl_type(str): transform type to search for.
        suffix(str): suffix to look for.
    Returns: A list of transform nodes that end with a given suffix and are children of a given group.
    """
    # control specific atm
    initial_selection = pymel.core.selected()
    objects = []
    for obj in pymel.core.ls(type=ctl_type):
        if obj.name().endswith(suffix):
            if in_selection:
                if obj in initial_selection:
                    print("selexcted obj: ", obj.name())
                    objects.append(obj)
            else:
                print("here")
                objects.append(obj)

    if select:
        pymel.core.select(objects, r=True)
    return objects


def select_all(suffix, obj_type, add=True, replace=False):
    """
    Gets all the selected controls on a specified type with the given Suffix
    Args:
        suffix:
        obj_type:
        add:
        replace:

    Returns:
        controls(list[str]): List of controls names.
    """
    controls = get_all_objects_with_suffix(ctl_type=obj_type, suffix=suffix)
    pymel.core.select(controls, add=add, r=replace)
    return controls


def get_selected(only_first=True):
    """Returns list of selected"""
    sel = pymel.core.selected()
    if only_first:
        return sel[0]
    else:
        return sel


def get_parents(control):
    """
    Creates a list of parent names of the selected obj
    Args:
        control(PyNode): control to get parent of

    Returns:
        parent_names(list[str]): list of parent names.
    """
    parent_node = control.getParent()
    parent_names = []
    while parent_node is not None:
        # Add the name of the parent node to the list
        parent_names.append(parent_node.name())
        # Get the next parent node
        parent_node = parent_node.getParent()

    return parent_names


def select_all_of_type_under_selected(suffix="_CTL"):
    """
    Selects all controls under given parent
    Returns:
    """
    selection = pymel.core.selected()
    if not selection:
        print("No object selected.")
        return

    objects = []
    for selected_obj in selection:
        children = maya.cmds.listRelatives(selected_obj.name(), allDescendents=True, fullPath=False)
        if not children:
            return

        for child in children:
            if child.endswith(suffix):
                objects.append(child)

    pymel.core.select(objects, r=True)

