## Copy Light Attributes- intensity/colour##

import maya.cmds as cmds

selection = cmds.ls(sl=True)

for selected in selection:
    first_object = selection[0]
    #get values of first_object
    intensity = cmds.getAttr(first_object + ".intensity")
    light_color = cmds.getAttr(first_object + ".color")[0]
    # set attribute
    cmds.setAttr(selected + ".intensity", intensity)
    cmds.setAttr(selected + ".color", light_color[0], light_color[1], light_color[2], type ="double3")