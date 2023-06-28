## Space out Objects evenly in a line##

import maya.cmds as cmds

#globle variables
start_position = [0,0,0]
together = True

total_distance = 0
PADDING = 5

#get selection
selection = cmds.ls(sl=True)

#determine if selection is together
for selected in selection:
    curr_position = cmds.xform(selected, q=True, ws=True, rp=True)
   
    if curr_position != start_position:
        together = False
        break
        
for selected in selection:
    if together:
        #do the seperation
        xmin, ymin, zmin, xmax,ymax, zmax = cmds.xform(selected, q=True, ws=True, bb=True)
        width = abs(xmax - xmin)
        
        if selected != selection[0]:
            total_distance += width/2
            cmds.move(total_distance, selected, r=True, x=True)
       
        total_distance += width/2 + PADDING  #padding between objects
    else:
        #move them together
        cmds.move(start_position[0],start_position[1],start_position[2], selected, a=True)
       