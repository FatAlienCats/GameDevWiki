##/************ Clean Combine **********************/


import maya.cmds as cmds

selection = cmds.ls(sl=True)

first_object = selection[0]

#gathering info
pivot = cmds.xform(first_object, q=True, worldSpace=True, rotatePivot=True)
display_layers = cmds.listConnections(first_object, type="displayLayer")
print display_layers
#combine
new_mesh = cmds.polyUnite(ch=False)
#reset pivot        
cmds.xform(new_mesh, rotatePivot=pivot)   

if display_layers:
    cmds.editDisplayLayerMembers(display_layers[0], new_mesh)
    
#rename new mesh to first object          
cmds.rename(new_mesh, first_object)  


    
 