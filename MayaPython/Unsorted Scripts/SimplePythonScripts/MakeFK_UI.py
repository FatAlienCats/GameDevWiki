import maya.cmds as cmds

def makeFKCTRL():
    
    selection =  cmds.ls(sl=True)
    
    controlSize = cmds.floatSliderGrp("control_size", query=True, value=True)
    
    previous_sel = None
    
    for s in selection:
        ctrl = cmds.circle(c=(0,0,0), nr=(1,0,0),  n = (s + "_CTRL"), r=controlSize)
        cmds.makeIdentity (apply=True)
        #cmds.DeleteHistory()
        offset = cmds.group (n=(s + "_offset"))
        cmds.parentConstraint(s, (offset), n = "deleteMe")
        cmds.delete("deleteMe")
        
        cmds.orientConstraint(ctrl, s, n=(s + "_orientContraint"))
      
        if previous_sel:
            cmds.parent(s + "_offset", previous_sel +"_CTRL")
        previous_sel = s
      
      
def FKWindow():
    
    #variable to call window
    fkWindow = "fkWindow"
    
    #if the window is already open, delete that instance
    if cmds.window(fkWindow, exists=True):
        cmds.deleteUI(fkWindow)
    #window parameters     
    cmds.window(fkWindow, w=150, title="Make FK", rtf=True, sizeable=True)
    
    #needs a column layout for text field
    cmds.columnLayout(adj=True)
    
    #text for description
    cmds.text(l="To use: select Joint(s) in the scene to make FK's", al="center")
   
    #slider to control FK size
    cmds.floatSliderGrp("control_size", l="Control Size", field=True, min= 0.1, max=50.0, cw =(1,80), fmn=0.1,fmx=50, value=True)
   
    #button
    cmds.button(l="Make FK Control(s)", c="makeFKCTRL()")
    
    #show window
    cmds.showWindow(fkWindow)
    
FKWindow()



            