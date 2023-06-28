import maya.cmds

def spaceSwitch():

    Sel = cmds.ls(sl=True)
    
    selected = cmds.radioButtonGrp("radioGrp", q=True, select=True)
    
    First_Sel = Sel[0]
    Second_Sel = Sel[1]
    Third_Sel = Sel[2]
    Control_GRP = Sel[3]
    
    if (selected == 1):
    
        Parent_Constraint = cmds.parentConstraint(mo=True)
        cmds.select(cl=True)
        cmds.select(Control_GRP)
        Control = cmds.pickWalk(d="down")
        
        cmds.addAttr(Control, k=True, at="enum", en="1:2:3:", ln="follow") 
        
        
        cmds.setAttr(Control[0] + ".follow", 0) #Global Space
        cmds.setAttr(Control_GRP + "_parentConstraint1" + "." + First_Sel + "W0", 1)
        cmds.setAttr(Control_GRP + "_parentConstraint1" + "." + Second_Sel + "W1", 0)
        cmds.setAttr(Control_GRP + "_parentConstraint1" + "." + Third_Sel + "W2", 0)
        
        cmds.setDrivenKeyframe(Control_GRP + "_parentConstraint1" + "." + First_Sel + "W0", currentDriver=Control[0] + ".follow")
        cmds.setDrivenKeyframe(Control_GRP + "_parentConstraint1" + "." + Second_Sel + "W1", currentDriver=Control[0] + ".follow")
        cmds.setDrivenKeyframe(Control_GRP + "_parentConstraint1" + "." + Third_Sel + "W2", currentDriver=Control[0] + ".follow")
        
        cmds.setAttr(Control[0] + ".follow", 1) #COG Space
        cmds.setAttr(Control_GRP + "_parentConstraint1" + "." + First_Sel + "W0", 0)
        cmds.setAttr(Control_GRP + "_parentConstraint1" + "." + Second_Sel + "W1", 1)
        cmds.setAttr(Control_GRP + "_parentConstraint1" + "." + Third_Sel + "W2", 0)
        
        cmds.setDrivenKeyframe(Control_GRP + "_parentConstraint1" + "." + First_Sel + "W0", currentDriver=Control[0] + ".follow")
        cmds.setDrivenKeyframe(Control_GRP + "_parentConstraint1" + "." + Second_Sel + "W1", currentDriver=Control[0] + ".follow")
        cmds.setDrivenKeyframe(Control_GRP + "_parentConstraint1" + "." + Third_Sel + "W2", currentDriver=Control[0] + ".follow")
        
        cmds.setAttr(Control[0] + ".follow", 2) #Local Space
        cmds.setAttr(Control_GRP + "_parentConstraint1" + "." + First_Sel + "W0", 0)
        cmds.setAttr(Control_GRP + "_parentConstraint1" + "." + Second_Sel + "W1", 0)
        cmds.setAttr(Control_GRP + "_parentConstraint1" + "." + Third_Sel + "W2", 1)
        
        cmds.setDrivenKeyframe(Control_GRP + "_parentConstraint1" + "." + First_Sel + "W0", currentDriver=Control[0] + ".follow")
        cmds.setDrivenKeyframe(Control_GRP + "_parentConstraint1" + "." + Second_Sel + "W1", currentDriver=Control[0] + ".follow")
        cmds.setDrivenKeyframe(Control_GRP + "_parentConstraint1" + "." + Third_Sel + "W2", currentDriver=Control[0] + ".follow")
        
        cmds.setAttr(Control[0] + ".follow", 2) #Local2 Space
        cmds.setAttr(Control_GRP + "_parentConstraint1" + "." + First_Sel + "W0", 0)
        cmds.setAttr(Control_GRP + "_parentConstraint1" + "." + Second_Sel + "W1", 0)
        cmds.setAttr(Control_GRP + "_parentConstraint1" + "." + Third_Sel + "W2", 1)
        
        cmds.setDrivenKeyframe(Control_GRP + "_parentConstraint1" + "." + First_Sel + "W0", currentDriver=Control[0] + ".follow")
        cmds.setDrivenKeyframe(Control_GRP + "_parentConstraint1" + "." + Second_Sel + "W1", currentDriver=Control[0] + ".follow")
        cmds.setDrivenKeyframe(Control_GRP + "_parentConstraint1" + "." + Third_Sel + "W2", currentDriver=Control[0] + ".follow")
    
    if (selected == 2):

        Orient_Constraint = cmds.orientConstraint(mo=True)
        cmds.select(cl=True)
        cmds.select(Control_GRP)
        Control = cmds.pickWalk(d="down")
        cmds.addAttr(Control, k=True, at="enum", en="1:2:3:", ln="follow") 
        
        
        cmds.setAttr(Control[0] + ".follow", 0) #Global Space
        cmds.setAttr(Control_GRP + "_orientConstraint1" + "." + First_Sel + "W0", 1)
        cmds.setAttr(Control_GRP + "_orientConstraint1" + "." + Second_Sel + "W1", 0)
        cmds.setAttr(Control_GRP + "_orientConstraint1" + "." + Third_Sel + "W2", 0)
        
        cmds.setDrivenKeyframe(Control_GRP + "_orientConstraint1" + "." + First_Sel + "W0", currentDriver=Control[0] + ".follow")
        cmds.setDrivenKeyframe(Control_GRP + "_orientConstraint1" + "." + Second_Sel + "W1", currentDriver=Control[0] + ".follow")
        cmds.setDrivenKeyframe(Control_GRP + "_orientConstraint1" + "." + Third_Sel + "W2", currentDriver=Control[0] + ".follow")
        
        cmds.setAttr(Control[0] + ".follow", 1) #COG Space
        cmds.setAttr(Control_GRP + "_orientConstraint1" + "." + First_Sel + "W0", 0)
        cmds.setAttr(Control_GRP + "_orientConstraint1" + "." + Second_Sel + "W1", 1)
        cmds.setAttr(Control_GRP + "_orientConstraint1" + "." + Third_Sel + "W2", 0)
        
        cmds.setDrivenKeyframe(Control_GRP + "_orientConstraint1" + "." + First_Sel + "W0", currentDriver=Control[0] + ".follow")
        cmds.setDrivenKeyframe(Control_GRP + "_orientConstraint1" + "." + Second_Sel + "W1", currentDriver=Control[0] + ".follow")
        cmds.setDrivenKeyframe(Control_GRP + "_orientConstraint1" + "." + Third_Sel + "W2", currentDriver=Control[0] + ".follow")
        
        cmds.setAttr(Control[0] + ".follow", 2) #Local Space
        cmds.setAttr(Control_GRP + "_orientConstraint1" + "." + First_Sel + "W0", 0)
        cmds.setAttr(Control_GRP + "_orientConstraint1" + "." + Second_Sel + "W1", 0)
        cmds.setAttr(Control_GRP + "_orientConstraint1" + "." + Third_Sel + "W2", 1)
        
        cmds.setDrivenKeyframe(Control_GRP + "_orientConstraint1" + "." + First_Sel + "W0", currentDriver=Control[0] + ".follow")
        cmds.setDrivenKeyframe(Control_GRP + "_orientConstraint1" + "." + Second_Sel + "W1", currentDriver=Control[0] + ".follow")
        cmds.setDrivenKeyframe(Control_GRP + "_orientConstraint1" + "." + Third_Sel + "W2", currentDriver=Control[0] + ".follow")
   
def loadSelections():
    
    Sel = cmds.ls(sl=True)
    
    First_Sel = Sel[0]
    Second_Sel = Sel[1]
    Third_Sel = Sel[2]
    Control_GRP = Sel[3]
    
    First_Space_Name = cmds.textFieldGrp("first_Space", e=True, text=First_Sel)
    Second_Space_Name = cmds.textFieldGrp("second_Space", e=True, text=Second_Sel)
    Third_Space_Name = cmds.textFieldGrp("third_Space", e=True, text=Third_Sel)
    

def spaceSwitchWindow():
    
    spaceSwitchWindow = "spaceSwitch"
    
    if cmds.window(spaceSwitchWindow, exists=True):
        cmds.deleteUI(spaceSwitchWindow)
            
    cmds.window(spaceSwitchWindow, w=100, title="jd_spaceSwitch", rtf=True, sizeable=True, mxb=False)
    
    mainLayout = cmds.columnLayout(adj=True)
    
    cmds.text(l="To Use:  Select 3 Controls that you wish to have follow a space\n then select one offset group, Press button below", al="center")
    cmds.radioButtonGrp("radioGrp",numberOfRadioButtons=2, l="Operation", labelArray2=['IK', 'FK'], cw=(1, 80), select=1)
    cmds.textFieldGrp("first_Space", l="First Space",  cw=(1, 80))
    cmds.textFieldGrp("second_Space", l="Second Space",  cw=(1, 80))
    cmds.textFieldGrp("third_Space", l="Third Space",  cw=(1, 80))
    cmds.button(l="Load", c="loadSelections()")
    cmds.button(l="Space Switch", c="spaceSwitch()")
    
    cmds.showWindow(spaceSwitchWindow)
    
spaceSwitchWindow()
    
