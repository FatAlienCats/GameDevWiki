## detach faces + renaming detach object and centering pivot##

import maya.cmds as cmds
# pSphere and a bunch of faces
face_objects ={}
# pSphere : pSphere_1
dupe_objects = {}

selected_faces = cmds.filterExpand(selectionMask = 34) 

for face in selected_faces:
   object, face_index = face.split(".")
   
   
   if object not in face_objects:#make and array containing objects
       face_objects[object] = []
       
   face_objects[object].append(face_index)
   
for face in face_objects: #duplicate object and delete selected faces 
    dupe_objects[object] = cmds.duplicate(object)[0]
    
cmds.delete(selected_faces)    


for object in dupe_objects:
    cmds.select(dupe_objects[object]+ ".f[*]")
    
    for face in face_objects[object]:
        cmds.select(dupe_objects[object]+"."+ face, d=True)
    
    cmds.delete(cmds.ls(sl=True))      #delete non-selected faces of copy
    new_obj = cmds.rename(dupe_objects[object], object + "_copy")        #rename new Object "_copy"
    cmds.xform(new_obj, cp=True)