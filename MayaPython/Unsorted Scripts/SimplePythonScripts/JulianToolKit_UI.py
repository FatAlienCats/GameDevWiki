#----------Modelling/Rigging Toolkit by Julian Beiboer 2018-----------------------#

import maya.cmds as cmds
myWindowName = "ModellingToolKit"
dockedWindow = "DockedWindow"

if cmds.window("myWindowName", exists=True):
	cmds.deleteUI("myWindowName")

if cmds.dockControl(dockedWindow, exists = True):
		cmds.deleteUI(dockedWindow)

cmds.window(myWindowName, title="Julian's Toolkit", rtf=True, sizeable=True)
column_layout = cmds.columnLayout(adj=True)

cmds.text(" ")
cmds.text("Mesh Operations")
cmds.text(" ")
cmds.separator()

cmds.button( l="Clean Combine", parent = column_layout, h=25, w=25, command="cleanCombine()")
cmds.button( l="Seperate", parent = column_layout, h=25, w=25, command="seperateObj()")
cmds.button( l="Freeze Transformations", parent = column_layout, h=25, w=25, command="freezeTransforms()")
cmds.button( l="Delete History(NonDeform)", parent = column_layout, h=25, w=25, command="delectHistory()")
cmds.separator()

cmds.text(" ")
cmds.text("Display Operations")
cmds.text(" ")
cmds.separator()

cmds.button( l="Xray", parent = column_layout, h=25, w=25, command="xrayObj()")
cmds.button( l="Toggle Local Axis", parent = column_layout,h=25, w=25, command="toggleLA()")
cmds.separator()

cmds.text(" ")
cmds.text("Pivot Operations")
cmds.text(" ")
cmds.separator()

cmds.button( l="Center", parent = column_layout, h=25, w=25, command="centerPivot()")
cmds.button( l="Bottom Pivot", parent = column_layout,h=25, w=25, command="bottomPivot()")
cmds.separator()

cmds.text(" ")
cmds.text("Rigging")
cmds.text(" ")
cmds.separator()

cmds.button( l="Center Joint", parent = column_layout, h=25, w=25, command="centerJoint()")

cmds.button( l="Select Hierarchy", parent = column_layout,h=25, w=25, command="selectHi()")
cmds.button( l="Mirror Controls", parent = column_layout,h=25, w=25, command="mirrorControl()")
cmds.button( l="Colour Override", parent = column_layout,h=25, w=25, command="colourOverride()")
#text for description
cmds.text(l="Select a Colour for Override ", al="center") 
#Colour palette UI
cmds.frameLayout(h=50,labelVisible=0)
# create a palette of 5 columns and 1 rows
cmds.palettePort( 'palette', dim=(5, 1) )

allowedAreas = ['right', 'left', 'bottom']
cmds.showWindow(myWindowName)


cmds.dockControl(dockedWindow, l="Julian's Toolkit", area='left', content=myWindowName, allowedArea=allowedAreas )

#--------Clean Combine----------------

def cleanCombine(unused=True):
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
        cmds.editDisplayLayerMembers(display_layers[0], n = 'new_mesh')
    
    #rename new mesh to first object          
    cmds.rename(new_mesh, first_object)  
#----------Seperate Objects-------------
def seperateObj(unused =True):
    selection = cmds.ls(sl=True)
    first_object = selection[0]
    
    for sel in selection:
        cmds.polySeparate(object =True ,n = first_object)
        #cmds.parent(sel, w =True)
        cmds.bakePartialHistory(ppt=True)
        cmds.parent(w=True)
    cmds.bakePartialHistory(ppt=True)
    cmds.delete(first_object)
    

#----------Freeze Transformations---------
def freezeTransforms(unused=True):
    selection = cmds.ls(sl=True)
    for selected in selection:
        cmds.makeIdentity(a=True)

#----------Delete History---------------
def delectHistory(unused =True):
    selection = cmds.ls(sl=True)
    for selected in selection:
        cmds.bakePartialHistory(ppt=True)

#----------Xray----------------
def xrayObj(usused=True):
    selection = cmds.ls(sl=True)
    for selected in selection:
        #check current state
        xray = cmds.displaySurface(selected, q=True, xRay=True)
        # set xray to opposite current state
        cmds.displaySurface(selected, xRay=not xray[0])


#----------Center pivot----------
def centerPivot(unused=True):
    #Selection objects
    selection = cmds.ls(sl=True)
    for selected in selection:
        #Center Pivot
        cmds.xform(cp=True)
        
#----------Bottom Pivot-----------
def bottomPivot(unused=True):
    
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

#----------Center Joint----------
def centerJoint(unused=True):
    selection = cmds.ls(sl=True)

    for sel in selection:
        ClusterTemp = cmds.cluster (en=1, n='clustertemp' ) # Create Cluster after selecting vertices
        JointTemp = cmds.joint(p=(0,0,0),name='jointtemp') # Create Joint
     
        cmds.pointConstraint(ClusterTemp, JointTemp, offset= (0,0,0), mo = False) #Pointconstrain Joint to move position to Cluster
    
        cmds.parent(JointTemp, w =True) # unparent Joint
        cmds.delete(ClusterTemp) # delete Cluster

#----------Toggle Local Axis---------
def toggleLA(unused=True):
    selection = cmds.ls(sl=True)
    cmds.toggle(selection, la=True)
    
#---------Select Hierarchy---------
def selectHi(unused=True):
    selection = cmds.ls(sl=True)
    cmds.select(selection, hi =True)

#----------Colour Override------------
def colourOverride(unused =True):
      
    selection = cmds.ls(sl=True)
    # set rgbcolour to tile selected
    rgbcolour = cmds.palettePort( 'palette', query=True, rgb=True )
    
    #Assign 'colour' a index value based of colour selection
    #RED
    if rgbcolour == [1.0,0.0,0.0]:
        colour = 13
    #YELLOW
    if rgbcolour == [0.9375, 1.0, 0.0]:
        colour = 17
    #GREEN
    if rgbcolour == [0.0, 1.0, 0.125]:
        colour = 14
    #LIGHT BLUE
    if rgbcolour == [0.0, 0.8125, 1.0]:
        colour = 18
    #BLUE    
    if rgbcolour == [0.25, 0.0, 1.0]:
        colour = 6
    #for each curve selected assign override colour to variable 'colour'
    for sel in selection:
        shape = cmds.listRelatives(sel, children = True)
        # set colour override to enabled
        cmds.setAttr(shape[0] + '.overrideEnabled', 1)
        #change colour
        cmds.setAttr(shape[0] + '.overrideColor', colour) 

#----------Mirror Controls on X----------
def mirrorControl(unused=True):
    selection =  cmds.duplicate(cmds.ls(sl=True))
    
    # create an empty group node with no children
    cmds.group( em=True, name='temp' )
    for sel in selection:
        #parent selected
       
        cmds.parent(sel, 'temp')
        #cmds.duplicate('temp')
        #scale temp x=-1
        cmds.xform('temp', scale=(-1,1,1))
        
        #parent selected to world
        cmds.parent(sel, w=True)
        #delete 'temp'& freeze transforms
        cmds.delete('temp')
        cmds.makeIdentity(a=True)
        
