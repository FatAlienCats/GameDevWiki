##Collision Box/Sphere/Cylinder creator##
import maya.cmds as cmds
import logging

def generateCollisionUI():
    window_name ="collisionUI"
    
    if cmds.window(window_name, q=True, exists =True):
        cmds.deleteUI(window_name)
        
    
    my_window = cmds.window(window_name, title ="CollisionUI")
    
    cmds.columnLayout(adj=True)
    
    cmds.button(label ="Sphere", c=generateSphere)
    cmds.text(label = "")
    cmds.button(label ="Box", c= generateBox)
    cmds.text(label = "")
    cmds.button(label ="Cylinder", c= generateCylinder)
    
    
    cmds.showWindow(my_window)


def generateBox(unused =None):
    generateCollision("box")
    
def generateSphere(unused =None):
    generateCollision("sphere")

def generateCylinder(unused =None):
    generateCollision("cylinder") 

#create collision poly
def generateCollision(mode="box"):
    
    selected = cmds.ls(sl=True)
    
    if not selected:
        logging.error("Please Select Target Object")
        return
    
    xmin,ymin,zmin,xmax,ymax,zmax = cmds.xform(selected[0], q=True, ws=True, bb=True)
   
    width = abs(xmax -xmin)
    height = abs(ymax- ymin)
    depth = abs (zmax -zmin)

    name = selected[0] + "_COL"
    
    if mode == "box":
        mesh= cmds.polyCube(w=width, h=height, d=depth, n= name)[0]
        
    if mode == "sphere":
        radius = max([width,height,depth])/2
        mesh = cmds.polySphere(r = radius, sx= 10, sy=10 , n= name)
        
    if mode == "cylinder":
        radius = max([width,depth])/2
        mesh = cmds.polyCylinder(r= radius, h=height, n=name, sc =1, sx= 12, sy=1)
        
    xPos = xmax - width/2
    yPos = ymax - height/2
    zPos = zmax - depth/2
    
    #set mesh_COL position to selected object
    cmds.xform(mesh, ws=True, t=[xPos,yPos,zPos])

generateCollisionUI()