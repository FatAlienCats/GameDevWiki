import maya.cmds as cmds
import math
import operator
from maya.OpenMaya import MVector


myWindowName = "ModellingToolKit"
dockedWindow = "DockedWindow"

if cmds.window("myWindowName", exists=True):
	cmds.deleteUI("myWindowName")

if cmds.dockControl(dockedWindow, exists = True):
		cmds.deleteUI(dockedWindow)

cmds.window(myWindowName, title="Jason's Modelling Tool", rtf=True, sizeable=True)
column_layout = cmds.columnLayout(adj=True)

cmds.text(" ")
cmds.text("Vertex Operations")
cmds.text(" ")
cmds.separator()

cmds.button(l="Make Circle", parent = column_layout, h=30, w=25, command="perfectCircle()")
cmds.separator()
cmds.text(" ")
cmds.text(" Planar Verts")
cmds.text(" ")
cmds.separator()
cmds.button( l="Planar X", parent = column_layout, h=22, w=25, command = "move_average(\"x\", verts)")
cmds.button(  l="Planar Y", parent = column_layout, h=22, w=25, command = "move_average(\"y\", verts)")
cmds.button(  l="Planar Z", parent = column_layout, h=22, w=25, command = "move_average(\"z\", verts)")
cmds.separator()


cmds.text(" ")
cmds.text("Mesh Operations")
cmds.text(" ")
cmds.separator()

cmds.button( l="Clean Combine", parent = column_layout, h=25, w=25, command="cleanCombine()")
cmds.button( l="Clean Extract", parent = column_layout, h=25, w=25, command="cleanExtract()")
cmds.separator()

cmds.text(" ")
cmds.text("Display Operations")
cmds.text(" ")
cmds.separator()

cmds.button( l="Xray", parent = column_layout, h=25, w=25, command="xrayObj()")
cmds.button( l="Backface", parent = column_layout, h=25, w=25, command="bfcObj()")
cmds.separator()

cmds.text(" ")
cmds.text("Pivot Operations")
cmds.text(" ")
cmds.separator()

cmds.button( l="Reset", parent = column_layout, h=25, w=25, command="resetPivot()")
cmds.button( l="Bottom Pivot", parent = column_layout,h=25, w=25, command="bottomPivot()")
cmds.separator()

allowedAreas = ['right', 'left', 'bottom']
cmds.showWindow(myWindowName)


cmds.dockControl(dockedWindow, l="Jason's Modelling Tool", area='left', content=myWindowName, allowedArea=allowedAreas )

#--------------Circle Tool-------------------------

def perfectCircle(unused=True):
	select = cmds.ls(selection=True)

	if (len(select) == 0):
		print "No verts"
		return
	
	# We determine what kind of selection is being made.
	# edge selection?
	selVerts = []
	selEdges = cmds.filterExpand(selectionMask=32, expand=True) or []
	if len(selEdges) > 0:
		cmds.ConvertSelectionToVertices()

	selVerts = cmds.filterExpand(selectionMask=31, expand=True) or []

	if len(selVerts) == 0:
		print "No verts selected"
		return

	# Find the number of verts in the currently selected node
	# and store the current vertex selection in a list.
	numVerts = cmds.polyEvaluate(select[0], vertex=True)
	print ("Number of verts in node: " + str(numVerts) + "\n")
	print ("Number of verts selected: " + str(len(selVerts)) + "\n");
	
	# In order to place the verts in a perfect circle, we need a world
	# space position to use as the centre of the circle. Let's use the
	# average world space position of the currently selected verts.

	avgPos = MVector(0,0,0)
	numSel = len(selVerts)
	wsVerts = []

	for i in range(0, numSel):
		vec = MVector(*cmds.xform(selVerts[i], query=True, worldSpace=True, translation=True))
		wsVerts.append(vec)
		print (str(vec.x) + "," + str(vec.y) + "," + str(vec.z))
		avgPos = avgPos + vec

	avgPos = avgPos/(1.0*numSel)
	
	print ("Average pos: " + str(avgPos.x) + "," + str(avgPos.y) + "," + str(avgPos.z))

	# So we have the average position now. We need to calculate the average distance from 
	# this centre point and use this as the radius of the circle.
	# We also calculate the point that is the furthest distance from the average position.
	radius = 0
	furthestPt = MVector(0,0,0)
	curDist = -1
	for i in range(0, numSel):
		vec = wsVerts[i]
		vec = vec-avgPos
		radius = radius + vec.length()
		if (vec.length() > curDist):
			curDist = vec.length()
			furthestPt = vec

	radius = radius/(1.0*numSel)

	print ("Radius: " + str(radius))

	# Ok, we have the furthest point from the average position, and we use this vector as one of the
	# vectors for our basis. We need to iterate over the rest of the vectors to find the
	# vector which is most orthogonal to the existing basis vector
	dot1 = furthestPt.normal()
	print ("dot1 found: " + str(dot1.x) + "," + str(dot1.y) + "," + str(dot1.z))	
	dot2 = MVector(0,0,0)
	curDP = 1
	for i in range(0, numSel):
		vec = wsVerts[i]
		vec = vec - avgPos
		vec = vec.normal()
		dp = dot1*vec
		if dp < 0:
			dp = -dp
		if dp < curDP:
			curDP = dp
			dot2 = vec

	print "DP found: " + str(curDP)
	print ("dot2 found: " + str(dot2.x) + "," + str(dot2.y) + "," + str(dot2.z))	

	# Ok so we now have two vectors. We create a basis by taking the cross product
	normal = dot1 ^ dot2
	dot2 = normal ^ dot1
	
	print ("normal: " + str(normal.x) + "," + str(normal.y) + "," + str(normal.z))	
	print ("dot1: " + str(dot1.x) + "," + str(dot1.y) + "," + str(dot1.z))	
	print ("dot2: " + str(dot2.x) + "," + str(dot2.y) + "," + str(dot2.z))	
	# Now that we have an appropriate coordinate system for the vertex selection,
	# we sort the vertex selection based on the angle of each vertex from the centre of the selection.
	vertAngles = {}

	for i in range(0, numSel):
		angleDot1 = (wsVerts[i]-avgPos)*dot1
		angleDot2 = (wsVerts[i]-avgPos)*dot2
		angle = (180*math.atan2(angleDot1, angleDot2))/math.pi
	
		vertAngles[selVerts[i]] = angle

	print vertAngles

	sortedAngles = sorted(vertAngles.iteritems(), key=operator.itemgetter(1))
	print sortedAngles

	# Now that we have the vertices sorted by their angle, we place them evenly around the circle
	firstAngle = (math.pi*sortedAngles[0][1])/180.0
	for i in range(0, len(sortedAngles)):
		vert1 = dot1*radius*math.sin((i*2*math.pi)/(1.0*len(sortedAngles)) + firstAngle)
		vert2 = dot2*radius*math.cos((i*2*math.pi)/(1.0*len(sortedAngles)) + firstAngle)
		vert1 = vert1 + vert2 + avgPos
		print sortedAngles[i][0]
		print (str(vert1.x) + "," + str(vert1.y) + "," + str(vert1.z))
		# Now set the vert position
		cmds.xform(sortedAngles[i][0], ws=True, t=[vert1.x, vert1.y, vert1.z])

#----------------------------Planar----------------------------------------		

verts = cmds.ls(sl=True, flatten = True)

# you can make variables inside of a function
def get_average(vertList):
    
    xAVG = 0
    yAVG = 0
    zAVG = 0
    
    # for how long the vert list happens to be
    for i in range (0, len(vertList)):
        
        # point position 
        pos = cmds.pointPosition(vertList[i])
        xAVG += pos[0]
        yAVG += pos[1]
        zAVG += pos[2]
        
    #averages the len of vert list by dividing
    xAVG = xAVG/len(vertList)
    yAVG = yAVG/len(vertList)
    zAVG = zAVG/len(vertList)
    
    avg = [xAVG, yAVG, zAVG]
    
    return avg
    
def move_average(axis, vertList):
    
    if axis == "x":
        
        avg = get_average(vertList)
        newPos = avg[0]
    
        for i in range (0, len(vertList)):
            
            currentPos = cmds.pointPosition(vertList[i])
            distance = newPos - currentPos[0] 
            
            cmds.select(vertList[i], replace =  True)
            cmds.move(distance, 0, 0, relative = True)
            cmds.select(cl = True)
    
    if axis == "y":
        
        avg = get_average(vertList)
        newPos = avg[1]
        
        for i in range (0, len(vertList)):
            
            currentPos = cmds.pointPosition(vertList[i])
            distance = newPos - currentPos[1] 
            
            cmds.select(vertList[i], replace =  True)
            cmds.move(0, distance, 0, relative = True)
            cmds.select(cl = True)
            
    if axis == "z":
        
            avg = get_average(vertList)
            newPos = avg[2]
        
            for i in range (0, len(vertList)):
                
                currentPos = cmds.pointPosition(vertList[i])
                distance = newPos - currentPos[2] 
                
                cmds.select(vertList[i], replace =  True)
                cmds.move(0, 0, distance, relative = True)
                cmds.select(cl = True)

#--------------------Clean Combine---------------------

def cleanCombine(unused=True):
    
    objSel = cmds.ls(sl=True)
    
    if len(objSel) < 0:
        cmds.warning("you must select at least two mesh(s)")
    else:
    
    #gets the selection
        
        
        #first_object = objSel[0] can only get the first object
        # so i used the tail flag to get the last selection
        first_object = cmds.ls(sl=True, tail=True)
        #queries the xform
        pivot = cmds.xform(first_object, q=True, ws=True, rotatePivot=True)
        #store display layers
        display_layers = cmds.listConnections(first_object, type="displayLayer")
        # combines objects without the construction history
        new_mesh = cmds.polyUnite(ch=False)
        # reset pivot of the new mesh as by default the pivot
        # is snapped to the origin 
        cmds.xform(new_mesh, rotatePivot=pivot)
        # if has a display layer assign the new combined object to the 
        # last selected display layer
        if display_layers:
            cmds.editDisplayLayerMembers(display_layers[0], new_mesh)
        
        #renames the mesh to last selected    
        cmds.rename(new_mesh, first_object)
        
#------------------Extract Faces----------------------------

def cleanExtract():
                                                                                                                
    # selected faces
    face_objects = {}
    # object of selected faces
    dup_objects = {}
    
    # selection of faces / iterations
    selected_faces = cmds.filterExpand(selectionMask = 34)
    for face in selected_faces:
        object, face_index = face.split(".")
        
        if object not in face_objects:
            face_objects[object] = []
    
        face_objects[object].append(face_index)
    
    for object in face_objects:
        dup_objects[object] = cmds.duplicate(object)[0]
    
    cmds.delete(selected_faces)
    
    new_objects = []
    
    for object in dup_objects:
        # select all the faces on the new object 
        cmds.select(dup_objects[object] + ".f[*]")
        
        for face in face_objects[object]:
            cmds.select(dup_objects[object] +"." +  face, d=True)
    
        cmds.delete(cmds.ls(sl=True))
        new_obj = cmds.rename(dup_objects[object], object + "_1")
        cmds.xform(new_obj, cp=True)
        new_objects.append(new_obj)
    	
    cmds.selectMode(object=True)
    cmds.select(new_objects)

#-------------------Xray------------------------------------------

def xrayObj(usused=True):
    objSel = cmds.ls(sl=True)
    for Sel in objSel:
        
        xRay = cmds.displaySurface(Sel, q=True, xRay=True)
        cmds.displaySurface(Sel, xRay = not xRay[0])

#------------------Back Face-----------------------------

def bfcObj(usused=True):

    objSel = cmds.ls(sl=True)
    for Sel in objSel:
        
        backface = cmds.polyOptions(Sel, q = True, backCulling = True)
        if backface[0]:
            cmds.polyOptions(Sel, fullBack = True)
        else:
            cmds.polyOptions(Sel, backCulling = True)
            
#------------------------Reset--------------------------------------

def resetPivot(usused=True):
# global variables
    Padding = 5
    start_position = [0, 0, 0]
    together = True
    
    total_distance = 0
    
    # get the selection
    objSel = cmds.ls(sl=True)
    
    #determine if the selection is together
    for Sel in objSel:
        current_position = cmds.xform(Sel, q=True, ws=True, rp=True)
        #print current_position
        if current_position != start_position:
            together = False
            break
            
    #print together
    for Sel in objSel:
        if together:
            #do separation
            print "Separating Apart " + Sel
            
            #finds bounding box
            # bb stands for bounding box
            xmin, ymin, zmin, xmax, ymax, zmax = cmds.xform(Sel, q=True, ws=True, bb=True)
            width = abs(xmax - xmin)
          
            if Sel != objSel[0]:
                total_distance += width/2
                cmds.move(total_distance, Sel, r=True, x=True)
            
            #print width
            
            #padding of ...
            total_distance += width/2 + Padding
             
            
        else:
            print "Joining Together " + Sel
            cmds.move(start_position[0], start_position[0], start_position[0], Sel, a=True)
  
#-------------------Bottom Pivot------------------------------------

def bottomPivot(usused=True):

    objSel = cmds.ls(sl=True)
    for Sel in objSel:
        cmds.xform(cp=True)
        
        bounding_box = cmds.xform(Sel, query = True, boundingBox = True, worldSpace = True)
        
        xmin, ymin, zmin, xmax, ymax, zmax = bounding_box
        
        cmds.move(bounding_box[1], [Sel + ".scalePivot", Sel + ".rotatePivot"], y=True, absolute=True)
      
     