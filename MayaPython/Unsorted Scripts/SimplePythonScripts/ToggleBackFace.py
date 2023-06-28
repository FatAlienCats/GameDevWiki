## BackCulling Object Toggle ##
import maya.cmds as cmds

selection = cmds.ls(sl=True)
for selected in selection:
    #Query if back Culling 
    backface = cmds.polyOptions(selected, q=True, bc = True)
    
    ##if backculling is off
    if backface[0] :
        cmds.polyOptions(selected, fb =True)
      
    #if backculling is on
    else:
        cmds.polyOptions(selected, bc=True)
