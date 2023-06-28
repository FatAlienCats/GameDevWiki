import maya.cmds as cmds 

Sel = cmds.ls(sl=True)

for s in Sel:
    controls = s
    cmds.addAttr(controls, at="enum", en="xyz:xyz:zxy:xzy:yxz:zyx:", ln="rotateOrders", nn="Rotate Orders", k=True)
    cmds.connectAttr(controls + ".rotateOrders", controls + ".rotateOrder", f=True)
    
    
    

