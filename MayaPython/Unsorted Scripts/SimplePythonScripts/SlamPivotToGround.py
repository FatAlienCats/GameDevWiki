## Center and shift pivot to bottom of object ##

import maya.cmds as cmds

#Selection objects
selection = cmds.ls(sl=True)
for selected in selection:
    #Center Pivot
    cmds.xform(cp=True)
    #Query max and min values for selection
    bounding_box = cmds.xform(selected, q=True, boundingBox=True, worldSpace=True)
    
    xmin, ymin, zmin, xmax, ymax, zmax = bounding_box
    #move pivot to bottom
    cmds.move(bounding_box[1], [selected + ".scalePivot", selected + ".rotatePivot"], y=True, absolute=True)