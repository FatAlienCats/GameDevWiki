import maya.cmds as cmds 

def hideSets():
    
    Sel = cmds.ls(sl=True)
     

    for s in Sel:
        
        outliner = cmds.getPanel(wf=True)
        cmds.setAttr(s + ".verticesOnlySet", True)
        cmds.outlinerEditor(outliner, e=True, showSetMembers=False)
        cmds.outlinerEditor(outliner, e=True, showSetMembers=True)
        
        print "Hiding "  + s + " from " + outliner 
        #cmds.warning("Hiding "  + s + " from " + outliner)
    
def hideWindow():
    
    hideWindow = "hideSetsWindow"
    
    if cmds.window(hideWindow, exists=True):
        cmds.deleteUI(hideWindow)
        
    cmds.window(hideWindow, t="jd_hideSets", sizeable=True, rtf=True)
    cmds.columnLayout(adj=True)
    
    cmds.button(l="Hide Sets", c="hideSets()")
    
    cmds.showWindow(hideWindow)
hideWindow()
  