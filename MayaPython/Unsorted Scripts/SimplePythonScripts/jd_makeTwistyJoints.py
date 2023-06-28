import maya.cmds as cmds 

twistJointsWindow = "twist_joints"
      
if cmds.window(twistJointsWindow, exists=True):
    cmds.deleteUI(twistJointsWindow)
    
    
cmds.window(twistJointsWindow, w=100, title="jd_makeTwistyJoints", rtf=True, sizeable=True, mxb=False)

cmds.columnLayout(adj=True)

cmds.text(l="To Use: Select 3 Objects in the order of:\n (1) start joint, (2) mid joint, (3) end joint, Click button below", al="center")

cmds.frameLayout(l="Primary Axis", la="top", bgc=(0.3, 0.3, 0.3), cll=False, cl=False)

cmds.radioCollection()

Xaxis = cmds.radioButton( label='X', select=True)
Yaxis = cmds.radioButton( label='Y', select=False)
Zaxis = cmds.radioButton( label='Z', select=False)

cmds.button(l="Make Twist", c="twist_joints()")
    
cmds.showWindow(twistJointsWindow)



def twist_joints():
    

    Sel = cmds.ls(sl=True)
    
    #selection list
    start_joint = Sel[0]
    mid_joint = Sel[1]
    end_joint = Sel[2]
    
    #duplicates copies of the low joints and parents them appropriately
    start_forearm_joint = cmds.duplicate(mid_joint, n=mid_joint + "_low_TWIST", parentOnly=True)
    end_forearm_joint = cmds.duplicate(end_joint, n=end_joint + "_low_TWIST", parentOnly=True)
    cmds.parent(end_forearm_joint, start_forearm_joint)
    
    cmds.select(start_forearm_joint[0])
    cmds.select(mid_joint, add=True)
    cmds.parent()
    
    #duplicates copies of the upp joints and parents them appropriately
    start_upperarm_joint = cmds.duplicate(start_joint, n=start_joint + "_upp_TWIST", parentOnly=True)
    end_upperarm_joint = cmds.duplicate(mid_joint, n=mid_joint + "_upp_TWIST", parentOnly=True)
    cmds.parent(start_upperarm_joint, end_upperarm_joint)
    
    #selects the last joint
    cmds.select(start_joint, r=True)
    last_joint = cmds.pickWalk(d="up")
    
    #creates sc solvers and parents them under the respected joints
    forearm_twist_handle = cmds.ikHandle(sol="ikSCsolver", sj=start_forearm_joint[0], ee=end_forearm_joint[0], n=end_joint + "_twist_HDL")
    cmds.select(forearm_twist_handle[0])
    cmds.select(end_joint, add=True)
    cmds.parent()
    
    #creates sc solvers and parents them under the respected joints
    upperarm_twist_handle = cmds.ikHandle(sol="ikSCsolver", sj=end_upperarm_joint[0], ee=start_upperarm_joint[0], n=start_joint + "_twist_HDL")
    cmds.select(upperarm_twist_handle[0])
    cmds.select(last_joint, add=True)
    cmds.parent()
    
    #duplicates twist joints / Low
    
    twist_low_a = cmds.duplicate(end_joint, n=end_joint + "_A_twist_JNT", parentOnly=True)
    cmds.setAttr(twist_low_a[0] + ".translateX", (12 *.75))
    
    twist_low_b = cmds.duplicate(end_joint, n=end_joint + "_B_twist_JNT", parentOnly=True)
    cmds.setAttr(twist_low_b[0] + ".translateX", (12 *.5))
    
    twist_low_c = cmds.duplicate(end_joint, n=end_joint + "_C_twist_JNT", parentOnly=True)
    cmds.setAttr(twist_low_c[0] + ".translateX", (12 *.25))
    
    cmds.delete(cmds.orientConstraint(mid_joint, twist_low_a, mo=False))
    cmds.makeIdentity(twist_low_a, apply=True)
    cmds.delete(cmds.orientConstraint(mid_joint, twist_low_b, mo=False))
    cmds.makeIdentity(twist_low_b, apply=True)
    cmds.delete(cmds.orientConstraint(mid_joint, twist_low_c, mo=False))
    cmds.makeIdentity(twist_low_c, apply=True)
    
    #creates the multiplydivide node for twisting and hooks up the respected paths.
    twist_low_node = cmds.createNode("multiplyDivide", n=end_joint + "_twist_MULT")
    cmds.setAttr(twist_low_node + ".input2X", 0.75)
    cmds.setAttr(twist_low_node + ".input2Y", 0.5)
    cmds.setAttr(twist_low_node + ".input2Z", 0.25)
    
    cmds.connectAttr(start_forearm_joint[0] + ".rx", twist_low_node + ".input1X")
    cmds.connectAttr(start_forearm_joint[0] + ".rx", twist_low_node + ".input1Y")
    cmds.connectAttr(start_forearm_joint[0] + ".rx", twist_low_node + ".input1Z")
    
    cmds.connectAttr(twist_low_node + ".outputX", twist_low_a[0] + ".rx")
    cmds.connectAttr(twist_low_node + ".outputY", twist_low_b[0] + ".rx")
    cmds.connectAttr(twist_low_node + ".outputZ", twist_low_c[0] + ".rx")
    
    #stretch node
    
    stretch_low_node = cmds.createNode("multiplyDivide", n=end_joint + "_stretch_MULT")
    cmds.setAttr(stretch_low_node + ".input2X", 0.75)
    cmds.setAttr(stretch_low_node + ".input2Y", 0.5)
    cmds.setAttr(stretch_low_node + ".input2Z", 0.25)
    
    cmds.connectAttr(end_joint + ".tx", stretch_low_node + ".input1X")
    cmds.connectAttr(end_joint + ".tx", stretch_low_node + ".input1Y")
    cmds.connectAttr(end_joint + ".tx", stretch_low_node + ".input1Z")
    
    cmds.connectAttr(stretch_low_node + ".outputX", twist_low_a[0] + ".tx")
    cmds.connectAttr(stretch_low_node + ".outputY", twist_low_b[0] + ".tx")
    cmds.connectAttr(stretch_low_node + ".outputZ", twist_low_c[0] + ".tx")
    
    
    #duplicates twist joints / Upp
    
    twist_upp_a = cmds.duplicate(mid_joint, n=mid_joint + "_A_twist_JNT", parentOnly=True)
    cmds.setAttr(twist_upp_a[0] + ".translateX", (12 *.75))
    
    twist_upp_b = cmds.duplicate(mid_joint, n=mid_joint + "_B_twist_JNT", parentOnly=True)
    cmds.setAttr(twist_upp_b[0] + ".translateX", (12 *.5))
    
    twist_upp_c = cmds.duplicate(mid_joint, n=mid_joint + "_C_twist_JNT", parentOnly=True)
    cmds.setAttr(twist_upp_c[0] + ".translateX", (12 *.25))
    
    cmds.delete(cmds.orientConstraint(start_joint, twist_upp_a, mo=False))
    cmds.makeIdentity(twist_upp_a, apply=True)
    cmds.delete(cmds.orientConstraint(start_joint, twist_upp_b, mo=False))
    cmds.makeIdentity(twist_upp_b, apply=True)
    cmds.delete(cmds.orientConstraint(start_joint, twist_upp_c, mo=False))
    cmds.makeIdentity(twist_upp_c, apply=True)
    
    twist_upp_node = cmds.createNode("multiplyDivide", n=start_joint + "_twist_MULT")
    cmds.setAttr(twist_upp_node + ".input2X", 0.25)
    cmds.setAttr(twist_upp_node + ".input2Y", 0.5)
    cmds.setAttr(twist_upp_node + ".input2Z", 0.75)
    
    cmds.connectAttr(end_upperarm_joint[0] + ".rx", twist_upp_node + ".input1X")
    cmds.connectAttr(end_upperarm_joint[0] + ".rx", twist_upp_node + ".input1Y")
    cmds.connectAttr(end_upperarm_joint[0] + ".rx", twist_upp_node + ".input1Z")
    
    cmds.connectAttr(twist_upp_node + ".outputX", twist_upp_c[0] + ".rx")
    cmds.connectAttr(twist_upp_node + ".outputY", twist_upp_b[0] + ".rx")
    cmds.connectAttr(twist_upp_node + ".outputZ", twist_upp_a[0] + ".rx")

    #stretch node
    
    stretch_upp_node = cmds.createNode("multiplyDivide", n=end_joint + "_stretch_MULT")
    cmds.setAttr(stretch_upp_node + ".input2X", 0.25)
    cmds.setAttr(stretch_upp_node + ".input2Y", 0.5)
    cmds.setAttr(stretch_upp_node + ".input2Z", 0.75)
    
    cmds.connectAttr(mid_joint + ".tx", stretch_upp_node + ".input1X")
    cmds.connectAttr(mid_joint + ".tx", stretch_upp_node + ".input1Y")
    cmds.connectAttr(mid_joint + ".tx", stretch_upp_node + ".input1Z")
    
    cmds.connectAttr(stretch_upp_node + ".outputX", twist_upp_a[0] + ".tx")
    cmds.connectAttr(stretch_upp_node + ".outputY", twist_upp_b[0] + ".tx")
    cmds.connectAttr(stretch_upp_node + ".outputZ", twist_upp_c[0] + ".tx")

