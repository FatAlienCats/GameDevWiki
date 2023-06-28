import maya.cmds as cmds 
import maya.mel as mel

if cmds.window("connectBC", exists=True):
    cmds.deleteUI("connectBC")
    
cmds.window("connectBC", title="jd_connectBlendColors", wh=(200, 200))

cmds.columnLayout(adj=True)
cmds.text(l="To use select three joints in the order of \n (1) IK, (2) FK, (3) Bind Joint - Button Below", al="center")
cmds.separator()
cmds.button(l="Connect", command="blendColorsStuff()")
cmds.separator()
    
cmds.showWindow("connectBC")

def blendColorsStuff():

    objSel = cmds.ls(selection=True)
    
    cmds.shadingNode("blendColors", asUtility=True, n=(objSel[2] + "_Rotate_BLC"))
    cmds.connectAttr((objSel[0] + ".rotate"), (objSel[2] + "_Rotate_BLC.color1"),  force=True) 
    cmds.connectAttr((objSel[1] + ".rotate"), (objSel[2] + "_Rotate_BLC.color2"),  force=True) 
    cmds.connectAttr((objSel[2] + "_Rotate_BLC.output"), (objSel[2] + ".rotate"),  force=True) 
    
    mel.eval(' searchReplaceNames "_JNT" "" "selected"; ')
      
    cmds.shadingNode("blendColors", asUtility=True, n=(objSel[2] + "_Translate_BLC"))
    cmds.connectAttr((objSel[0] + ".translate"), (objSel[2] + "_Translate_BLC.color1"),  force=True) 
    cmds.connectAttr((objSel[1] + ".translate"), (objSel[2] + "_Translate_BLC.color2"),  force=True) 
    cmds.connectAttr((objSel[2] + "_Translate_BLC.output"), (objSel[2] + ".translate"),  force=True)
    
    mel.eval(' searchReplaceNames "_JNT" "" "selected"; ')
