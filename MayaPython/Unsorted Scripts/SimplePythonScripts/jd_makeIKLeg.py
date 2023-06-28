import maya.cmds as cmds
import math
from maya import cmds , OpenMaya 

def makeIkLeg():
    

    Sel = cmds.ls(sl=True)
    
    
    if len(Sel) < 2:
            OpenMaya.MGlobal.displayError("Please select start and end joint. (exactly 2 ik joints)")
            
    else:
        
        radius = 2
        radius_pv = cmds.floatSliderGrp("control_size", query=True, value=True)
    
        pv_distance = cmds.floatSliderGrp("control_distance", query=True, value=True)
        control_colour = cmds.colorIndexSliderGrp("control_colour", q=True, v=True)
        control_colour = control_colour - 1;
     
        leg_handle = cmds.ikHandle(sj=Sel[0], ee=Sel[1], n=Sel[1] + "_IKRP")
        
        thigh_joint = cmds.select(Sel[0])
        knee_joint = cmds.pickWalk(d="down")
        cmds.select(cl=True)
        
        ankle_joint = cmds.select(Sel[1])
        ball_joint = cmds.pickWalk(d="down")
        toe_joint = cmds.pickWalk(d="down")
        
        ball_handle = cmds.ikHandle(sj=Sel[1], ee=ball_joint[0], sol="ikSCsolver", n=ball_joint[0] + "_IKSC")
        toe_handle = cmds.ikHandle(sj=ball_joint[0], ee=toe_joint[0], sol="ikSCsolver",  n=toe_joint[0] + "_IKSC")
        cmds.select(cl=True)
        
        
        ball_group = cmds.group(empty=True, n=ball_joint[0] + "_GRP")
        cmds.delete(cmds.pointConstraint(ball_joint, ball_group, mo=False))
        toe_group = cmds.group(empty=True, n=toe_joint[0] + "_GRP")
        cmds.delete(cmds.pointConstraint(toe_joint, toe_group, mo=False))
        
        heel_group = cmds.group(empty=True, n=Sel[1] + "_GRP")
        cmds.delete(cmds.pointConstraint(Sel[1], heel_group, mo=False))
        
        skipList = ['x']
        skipList.append('z')
        
        cmds.delete(cmds.pointConstraint(ball_joint, heel_group, mo=False, skip=skipList))
        
        cmds.select(ball_joint[0] + "_IKSC", Sel[1] + "_IKRP")
        cmds.select(ball_group, add=True)
        cmds.parent()
        
        cmds.select(toe_joint[0] + "_IKSC", ball_group)
        cmds.select(toe_group, add=True)
        cmds.parent()
        
        cmds.select(toe_group)
        cmds.select(heel_group, add=True)
        cmds.parent()
        
        cmds.select(cl=True)
        
        
        startGrp = cmds.group(empty=True, n=Sel[1] + "_Start")
        endGrp = cmds.group(empty=True, n=toe_joint[0] + "_End")
       
        cmds.pointConstraint(Sel[1], startGrp, offset=(0,0,0), weight=1)
        cmds.pointConstraint(toe_joint[0], endGrp, offset=(0,0,0), weight=1)
        
        distance_node = cmds.createNode("distanceBetween", n=Sel[1] + "_dist")
        
        cmds.connectAttr(startGrp + ".translate", distance_node + ".point1", force=True)
        cmds.connectAttr(endGrp + ".translate", distance_node + ".point2", force=True)
       
        curve_size = cmds.getAttr(distance_node + ".distance")
        
        foot_control = cmds.circle(ch=False, nr=(0, 1, 0), n=Sel[1] + "_CTRL", r=curve_size*.75)
        cmds.scale(0.5, 1, 1, r=True)
        cmds.makeIdentity(apply=True, s=True)
        foot_group = cmds.group(foot_control, n=foot_control[0] + "_GRP")
        cmds.delete(cmds.parentConstraint(ball_group, foot_group, mo=False))
        cmds.delete(startGrp, endGrp)
        
        cmds.parent(heel_group, foot_control)
        cmds.addAttr(foot_control, ln="ballRoll", at="double", dv=0, k=True)
        cmds.addAttr(foot_control, ln="toePivot", at="double", dv=0, k=True)
        cmds.addAttr(foot_control, ln="heelPivot", at="double", dv=0, k=True)
        cmds.addAttr(foot_control, ln="lean", at="double", dv=0, k=True)
        cmds.addAttr(foot_control, ln="heelSpin", at="double", dv=0, k=True)
        cmds.addAttr(foot_control, ln="toeSpin", at="double", dv=0, k=True)
        
        cmds.connectAttr(foot_control[0] + ".ballRoll", ball_group + ".rx") 
        cmds.connectAttr(foot_control[0] + ".toePivot", toe_group + ".rx") 
        cmds.connectAttr(foot_control[0] + ".heelPivot", heel_group + ".rx")
        cmds.connectAttr(foot_control[0] + ".lean", ball_group + ".ry")
        cmds.connectAttr(foot_control[0] + ".heelSpin", heel_group + ".ry")
        cmds.connectAttr(foot_control[0] + ".toeSpin", toe_group + ".ry")
        
        
        
        start = cmds.xform(Sel[0] ,q= 1 ,ws = 1,t =1 )
        mid = cmds.xform(knee_joint[0] ,q= 1 ,ws = 1,t =1 )
        end = cmds.xform(Sel[1] ,q= 1 ,ws = 1,t =1 )
        startV = OpenMaya.MVector(start[0] ,start[1],start[2])
        midV = OpenMaya.MVector(mid[0] ,mid[1],mid[2])
        endV = OpenMaya.MVector(end[0] ,end[1],end[2])
        startEnd = endV - startV
        startMid = midV - startV
        dotP = startMid * startEnd
        proj = float(dotP) / float(startEnd.length())
        startEndN = startEnd.normal()
        projV = startEndN * proj
        arrowV = startMid - projV
        arrowV*= pv_distance 
        finalV = arrowV + midV
        cross1 = startEnd ^ startMid
        cross1.normalize()
        cross2 = cross1 ^ arrowV
        cross2.normalize()
        arrowV.normalize()
        matrixV = [arrowV.x , arrowV.y , arrowV.z , 0 , 
        cross1.x ,cross1.y , cross1.z , 0 ,
        cross2.x , cross2.y , cross2.z , 0,
        0,0,0,1]
        matrixM = OpenMaya.MMatrix()
        OpenMaya.MScriptUtil.createMatrixFromList(matrixV , matrixM)
        matrixFn = OpenMaya.MTransformationMatrix(matrixM)
        rot = matrixFn.eulerRotation()
        loc = cmds.spaceLocator(n=knee_joint[0] + "_LOC")[0]
        cmds.xform(loc , ws =1 , t= (finalV.x , finalV.y ,finalV.z))
        cmds.xform ( loc , ws = 1 , rotation = ((rot.x/math.pi*180.0),
        (rot.y/math.pi*180.0),
        (rot.z/math.pi*180.0)))
        
        first_curve = cmds.circle(ch=False, nr=(1, 0, 0), r=radius_pv, n=knee_joint[0] + "_CTRL")
        second_curve = cmds.circle(ch=False, nr=(0, 1, 0), r=radius_pv)
        third_curve = cmds.circle(ch=False, nr=(0, 0, 1), r=radius_pv)
        
        cmds.select(second_curve)
        second_shape = cmds.pickWalk(d="down")
        cmds.select(third_curve)
        third_shape = cmds.pickWalk(d="down")
        
        pv_curve = cmds.parent(third_shape, second_shape, first_curve, r=True, s=True) 
        cmds.delete(second_curve, third_curve)
        cmds.select(first_curve)
        pv_group = cmds.group(n=knee_joint[0] + "_GRP")
        
        cmds.delete(cmds.pointConstraint(loc, pv_group, mo=False))
        cmds.poleVectorConstraint(loc, leg_handle[0])
        cmds.parent(loc, first_curve)
        cmds.setAttr(loc + ".visibility", 0)
        
        cmds.select(cl=True)
        
        Sel_len = len(Sel)
        
        point_one = cmds.xform(first_curve, q=True, ws=True, piv=True)
        point_two = cmds.xform(knee_joint[0], q=True, ws=True, piv=True)
        
        cluster = []
        
        cluster_crv = cmds.curve(d=1, p=[(point_one[0], point_one[1], point_one[2]), (point_two[0], point_two[1], point_two[2])], k=[0, 1], n=Sel[0] + "_line_CRV")
        
        for i in range(1, Sel_len):
            
            first_sel = Sel[0]
            second_sel = Sel[1]
        
            point1 = cmds.ls( cluster_crv + ".cv[0]",fl=True)
            point2 = cmds.ls( cluster_crv + ".cv[1]",fl=True)
            
            clusterA_shape = cmds.cluster(point1) 
            clusterB_shape = cmds.cluster(point2)
            
            clusterA = (cmds.listConnections(clusterA_shape[0] + ".matrix") or [None])[0]
            clusterB = (cmds.listConnections(clusterB_shape[0] + ".matrix") or [None])[0]
            
            cmds.parent(clusterA, first_curve)
            cmds.parent(clusterB, knee_joint)
            cmds.setAttr(clusterA + ".visibility", 0)
            cmds.setAttr(clusterB + ".visibility", 0)
            
            cmds.rename(clusterA, (Sel[0]+"_Start_CLS")) 
            cmds.rename(clusterB, (Sel[0]+"_End_CLS"))
            
            cmds.select(cl=True)
            
            legIk_Grp =  cmds.group(empty=True, n="Leg_GRP")
            
            cmds.parent(cluster_crv, pv_group, foot_group, legIk_Grp)
            cmds.setAttr(legIk_Grp + ".overrideEnabled", 1)
            cmds.setAttr(legIk_Grp + ".overrideColor", control_colour)
            cmds.select(cl=True)
            
def makeIKLegWindow():
    
    legWindow = "makeIkLeg"
    
    if cmds.window(legWindow, exists=True):
        cmds.deleteUI(legWindow)
            
    cmds.window(legWindow, w=100, title="jd_makeIkLeg", rtf=True, sizeable=True, mxb=False)
    
    cmds.columnLayout(adj=True)
    
    cmds.text(l="To Use: Select 2 ik joint(s) in order of: (1) Thigh Joint, (2) Ankle Joint \n Then use the button below. Will setup ik foot and all roll attributes", al="center")
    
    cmds.floatSliderGrp("control_size",l="Control Size", field=True, min=.01, max=50.0, cw=(1, 80), fmn=.1, fmx=50, value=.5)
    cmds.floatSliderGrp("control_distance",l="Control Distance", field=True, min=.01, max=50.0, cw=(1, 80), fmn=.1, fmx=50, value=5)
    cmds.colorIndexSliderGrp("control_colour", label="Control Colour", cw=(1, 80), min=0, max=31, value=1)
    
    
    cmds.button(l="Make Ik Leg", c="makeIkLeg()")
    
    cmds.showWindow(legWindow)
    
makeIKLegWindow()
   