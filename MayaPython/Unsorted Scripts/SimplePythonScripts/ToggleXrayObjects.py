#Toggle Xray Mode for object##
import maya.cmds as cmds

selection = cmds.ls(sl=True)
for selected in selection:
    #check current state
    xray = cmds.displaySurface(selected, q=True, xRay=True)
    # set xray to opposite current state
    cmds.displaySurface(selected, xRay=not xray[0])
    
    