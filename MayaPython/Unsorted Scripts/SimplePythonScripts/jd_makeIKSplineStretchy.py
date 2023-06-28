import maya.cmds as cmds

    
stretchWindow = "makeStretch"
      
if cmds.window(stretchWindow, exists=True):
    cmds.deleteUI(stretchWindow)
    
    
cmds.window(stretchWindow, w=100, title="jd_makeIKSplineStretchy", rtf=True, sizeable=True, mxb=False)

cmds.columnLayout(adj=True)

cmds.text(l="To Use: Select 4 Objects in the order of:\n (1) ikHandle, (2) Up Object 2, (3) Global Control\n Then use the button below", al="center")

cmds.frameLayout(l="Primary Axis", la="top", bgc=(0.3, 0.3, 0.3), cll=False, cl=False)

cmds.radioCollection()

Xaxis = cmds.radioButton( label='X', select=True)
Yaxis = cmds.radioButton( label='Y', select=True)
Zaxis = cmds.radioButton( label='Z', select=True)

cmds.button(l="Make Stretch", c="makeIkSplineStretchy()")
    
cmds.showWindow(stretchWindow)

def makeIkSplineStretchy():
    
    sel = cmds.ls(sl=True)
    
    #should return the joints the ikHandle is effecting
    
    #print joints
    
    #if len(sel) < 4:
        #om.MGlobal.displayError("Please read instructions and start again. (invalid amount of joints)")
    
    #else:
    splineHandle = sel[0]
    worldUp2 = sel[1]
    globalControl = sel[2]
    
    stretch_attribute = cmds.addAttr(worldUp2, ln="SS", at="double", min=0, max=1, dv=0, k=True)
    
    ikRelatives = cmds.listConnections(splineHandle, connections=True)
    
    endEffector = cmds.select(ikRelatives[3])
    spline_curve = cmds.select(ikRelatives[7], r=True)
    spline_shape = cmds.pickWalk(d="down")[0]
    
    #joints are found in ikHandle with jointList flag
    
    spline_info = cmds.shadingNode("curveInfo", asUtility=True, n=splineHandle + "_info")
    spline_stretch_mult = cmds.shadingNode("multiplyDivide", asUtility=True, n=splineHandle + "stretch_DIV")
    global_scale_node = cmds.shadingNode("multiplyDivide", asUtility=True, n=splineHandle + "_stretch_global_DIV")
    
    sqrRt_pow = cmds.shadingNode("multiplyDivide", asUtility=True, n=splineHandle + "sqrRt_POW")
    invert_Div = cmds.shadingNode("multiplyDivide", asUtility=True, n=splineHandle + "invert_DIV")
    SS_toggle_node = cmds.shadingNode("blendColors", asUtility=True, n=splineHandle + "_SS_BC")
    
    cmds.connectAttr(spline_shape + ".worldSpace", spline_info + ".inputCurve")
    cmds.setAttr(spline_stretch_mult + ".operation", 2)
    
    cmds.connectAttr(globalControl + ".scaleY", global_scale_node + ".input2X")
    cmds.connectAttr(spline_info + ".arcLength", global_scale_node + ".input1X")
    cmds.connectAttr(global_scale_node + ".outputX", spline_stretch_mult + ".input1X")
    
    cmds.setAttr(global_scale_node + ".operation", 2)
    
    spline_distance = cmds.getAttr(spline_info + ".arcLength")
    cmds.setAttr(spline_stretch_mult + ".input2X", spline_distance)
    
    cmds.connectAttr(spline_stretch_mult + ".outputX", sqrRt_pow + ".input1X")
    cmds.setAttr(sqrRt_pow + ".input2X", 0.5)
    cmds.setAttr(sqrRt_pow + ".operation", 3)
    
    cmds.connectAttr(sqrRt_pow + ".outputX", SS_toggle_node + ".color1R")
    cmds.setAttr(SS_toggle_node + ".color2R", 1)
     
    cmds.connectAttr(worldUp2 + ".SS", SS_toggle_node + ".blender") 
     
    cmds.connectAttr(SS_toggle_node + ".outputR", invert_Div + ".input2X")
    cmds.setAttr(invert_Div + ".input1X", 1)
    cmds.setAttr(invert_Div + ".operation", 2)
    
    jointList = []
    
    jointsList = cmds.ikHandle(splineHandle, q=True, jl=True) 
    selectedJoints = cmds.select(jointsList, r=True)
    
    jointsList.append(selectedJoints)
    
    if cmds.radioButton(Xaxis, q=True, select=True):
        for joints in jointsList:
            
            cmds.connectAttr(spline_stretch_mult + ".outputX", joints + ".scaleX")
            cmds.connectAttr(invert_Div + ".outputX", joints + ".scaleY")
            cmds.connectAttr(invert_Div + ".outputX", joints + ".scaleZ")
            
    if cmds.radioButton(Yaxis, q=True, select=True):
        for joints in jointsList:
  
            cmds.connectAttr(spline_stretch_mult + ".outputX", joints + ".scaleY")
            cmds.connectAttr(invert_Div + ".outputX", joints + ".scaleX")
            cmds.connectAttr(invert_Div + ".outputX", joints + ".scaleZ") 
    
    if cmds.radioButton(Zaxis, q=True, select=True):
        for joints in jointsList:
            cmds.connectAttr(spline_stretch_mult + ".outputX", joints + ".scaleZ")
            cmds.connectAttr(invert_Div + ".outputX", joints + ".scaleX")
            cmds.connectAttr(invert_Div + ".outputX", joints + ".scaleY") 
           
           
         
   

    





