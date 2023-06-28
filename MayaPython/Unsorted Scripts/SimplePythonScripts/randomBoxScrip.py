#RandomBox


import maya.cmds as cmds
import random


def randomiser():
    Number = cmds.intSliderGrp("Num", query=True, value=True)
    #blue cubes
    for i in range(Number):
         #Size
        Xs = cmds.floatSliderGrp("X", query=True, value=True)
        Ys = cmds.floatSliderGrp("Y", query=True, value=True)
        Zs = cmds.floatSliderGrp("Z", query=True, value=True)
        #Positio
        x = random.uniform(-10*Xs,10*Xs)
        y = random.uniform(-10*Ys,10*Ys)
        z = random.uniform(-10*Zs,10*Zs)
       
      
        mycube1 = cmds.polyCube(h=3, w=3, d=3, n="BlueCube#")
        cmds.move(x, y, z, mycube1)
        cmds.sets(forceElement = 'aiStandard2SG')
        cmds.scale(Xs,Xs,Xs, mycube1)
     #red cubes
    for i in range(Number):
        Xs = cmds.floatSliderGrp("X", query=True, value=True)
        Ys = cmds.floatSliderGrp("Y", query=True, value=True)
        Zs = cmds.floatSliderGrp("Z", query=True, value=True)
        #Position
        x = random.uniform(-10*Xs,10*Xs)
        y = random.uniform(-10*Ys,10*Ys)
        z = random.uniform(-10*Zs,10*Zs)
       
     
       
     
      
        mycube1 = cmds.polyCube(h=3, w=3, d=3, n="RedCube#")
        cmds.move(x, y, z, mycube1)
        cmds.sets(forceElement = 'aiStandard1SG')
        cmds.scale(Ys,Ys,Ys, mycube1)
       
            
        #Green cubes
    for i in range(Number):
        Xs = cmds.floatSliderGrp("X", query=True, value=True)
        Ys = cmds.floatSliderGrp("Y", query=True, value=True)
        Zs = cmds.floatSliderGrp("Z", query=True, value=True)
        #Position
        x = random.uniform(-10*Xs,10*Xs)
        y = random.uniform(-10*Ys,10*Ys)
        z = random.uniform(-10*Zs,10*Zs)
       
        #Size
       
        
        mycube1 = cmds.polyCube(h=3, w=3, d=3, n="GreenCube#")
        cmds.move(x, y, z, mycube1)
        cmds.sets(forceElement = 'aiStandard3SG')
        cmds.scale(Zs,Zs,Zs, mycube1)
       
   
    

      
      
def OverrideWindow():
    
    #variable to call window
    ocWindow = "DataWindow"
    
    #if the window is already open, delete that instance
    if cmds.window(ocWindow, exists=True):
        cmds.deleteUI(ocWindow)
    #window parameters     
    cmds.window(ocWindow, w=150, title="Legit data!", rtf=True, sizeable=True)
    
    #needs a column layout for text field
    cmds.columnLayout(adj=True)
    
    #text for description
    cmds.text(l="Adjust arguements accordingly", al="center")
   
    #slider to control colour distribution
    cmds.floatSliderGrp("X", l="Suppport", field=True, min= 0, max=10, cw =(1,80), fmn=0,fmx=10, pre=0, value=True)
    cmds.floatSliderGrp("Y", l="Opposition", field=True, min= 0, max=5, cw =(1,80), fmn=0,fmx=5, pre=0, value=True)
    cmds.floatSliderGrp("Z", l="Other", field=True, min= 0, max=5, cw =(1,80), fmn=0,fmx=5, pre=0, value=True)
    cmds.intSliderGrp("Num", l="Sample Size", field=True, min= 0, max=100, cw =(1,80), fmn=0,fmx=100, value=True)
 
    #button
    cmds.button(l="Create", c="randomiser()")
    
    #show window
    cmds.showWindow(ocWindow)
    
OverrideWindow()
