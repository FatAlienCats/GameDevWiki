import maya.cmds as cmds

def makeIkStretchy():
    
    sel = cmds.ls(sl=True)
    ikHandle = sel[0]
    ikControl = sel[1]
    globalControl = sel[2]
    
    stretch_attribute = cmds.addAttr(ikControl, ln="stretchy", at="double", min=0, max=1, dv=0, k=True)
    
    
    endPoint = []
    ikRelatives = cmds.listConnections(ikHandle, connections=True)
    endEffector = cmds.select(ikRelatives[3])
    
    middleJoint = cmds.pickWalk(d="up")
    endJoint = cmds.pickWalk(d="down")
    cmds.pickWalk(d="up")
    startJoint = cmds.pickWalk(d="up")
    
    startPos = cmds.getAttr(startJoint[0]+".translateX")
    middlePos = cmds.getAttr(middleJoint[0]+".translateX")
    endPos = cmds.getAttr(endJoint[0]+".translateX")
    
    cmds.select(ikHandle)
    cmds.pickWalk(d="down")
    pv = cmds.poleVectorConstraint(q=True, targetList=True)
    
    cmds.select(d=True)
    
         
    startGrp = cmds.group(empty=True, n=ikHandle + "_endPoint")
    
    endGrp = cmds.group(empty=True, n=ikHandle + "_startPoint")
    
    cmds.pointConstraint(startJoint[0], startGrp, offset=(0,0,0), weight=1)
    cmds.matchTransform(endGrp, endJoint[0],pos=True)
    cmds.pointConstraint(ikControl, endGrp, offset=(0,0,0), weight=1, mo=True)
    
    
    distance_node = cmds.createNode("distanceBetween", n=ikHandle + "_dist")
    
    cmds.connectAttr(startGrp + ".translate", distance_node + ".point1", force=True)
    cmds.connectAttr(endGrp + ".translate", distance_node + ".point2", force=True)
    
    cmds.parent(startGrp, endGrp, globalControl) 
    
    condition_node = cmds.shadingNode("condition", asUtility=True, n=ikHandle + "_stretch_cnd")
    multiply_node = cmds.shadingNode("multiplyDivide", asUtility=True, n=ikHandle + "_stretch_MULT")
    divide_node = cmds.shadingNode("multiplyDivide", asUtility=True, n=ikHandle + "_stretch_DIV")
    global_scale_node = cmds.shadingNode("multiplyDivide", asUtility=True, n=ikHandle + "_stretch_global_DIV")
    stretch_toggle_node = cmds.shadingNode("blendColors", asUtility=True, n=ikHandle + "_stretch_BC")
    
    distance_length = cmds.getAttr(distance_node + ".distance")
    
    cmds.connectAttr(globalControl + ".scaleY", global_scale_node + ".input2X")
    cmds.connectAttr(distance_node + ".distance", global_scale_node + ".input1X")
    cmds.connectAttr(global_scale_node + ".outputX", divide_node + ".input1X") 
    cmds.setAttr(global_scale_node + ".operation", 2)
    
    total_length = math.fabs(middlePos + endPos)
    
    #cmds.connectAttr(global_scale_node + ".outputX", divide_node + ".input1X")
    cmds.setAttr(divide_node + ".input2X", total_length)
    cmds.setAttr(divide_node + ".operation", 2) 
    
    
    cmds.setAttr(condition_node + ".operation", 3)
    cmds.connectAttr(distance_node + ".distance", condition_node + ".firstTerm")
    cmds.setAttr(condition_node + ".secondTerm", total_length)
    cmds.connectAttr(divide_node + ".outputX", condition_node + ".colorIfTrueR")
    #cmds.connectAttr(condition_node + ".colorIfFalseR", 1)
    
    
    
    cmds.connectAttr(condition_node + ".outColorR", stretch_toggle_node + ".color1R")
    cmds.setAttr(stretch_toggle_node + ".color2R", 1)
    cmds.connectAttr(stretch_toggle_node + ".outputR", multiply_node + ".input2X") 
    cmds.connectAttr(stretch_toggle_node + ".outputR", multiply_node + ".input2Y")
    
    
    cmds.setAttr(multiply_node + ".input1X", middlePos)
    cmds.setAttr(multiply_node + ".input1Y", endPos)
    
    cmds.connectAttr(multiply_node + ".outputX", middleJoint[0] + ".translateX")
    cmds.connectAttr(multiply_node + ".outputY", endJoint[0] + ".translateX")
    cmds.connectAttr(ikControl + ".stretchy", stretch_toggle_node + ".blender")
    
    
def makeStretchWindow():
    
    stretchWindow = "makeStretch"
    
    if cmds.window(stretchWindow, exists=True):
        cmds.deleteUI(stretchWindow)
            
    cmds.window(stretchWindow, w=100, title="jd_makeIkStretchy", rtf=True, sizeable=True, mxb=False)
    
    cmds.columnLayout(adj=True)
    
    cmds.text(l="To Use: Select 3 Objects in the order of:\n (1) ikHandle, (2) ikControl, (3) Global Control\n Then use the button below", al="center")
    
    cmds.button(l="Make Stretch", c="makeIkStretchy()")
    cmds.checkBox(l="snap attribute", value=False)
    
    cmds.showWindow(stretchWindow)
    
makeStretchWindow()
    
    
    
    
    
    
    