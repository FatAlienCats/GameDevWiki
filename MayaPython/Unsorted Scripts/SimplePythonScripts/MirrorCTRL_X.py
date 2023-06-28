#  mirror CTRL across X  #
import maya.cmds as cmds


def mirrorControl():
    selection =  cmds.ls(sl=True)
    
    # create an empty group node with no children
    cmds.group( em=True, name='temp' )
    for sel in selection:
        #parent selected
       
        cmds.parent(sel, 'temp')
        #scale temp x=-1
        cmds.xform('temp', scale=(-1,1,1))
        
        #parent selected to world
        cmds.parent(sel, w=True)
    #delete 'temp'    
    cmds.delete('temp')
       
    
def MirrorWindow():
    
    #variable to call window
    mirrorWindow = "MirrorCTRLWindow"
    
    #if the window is already open, delete that instance
    if cmds.window(mirrorWindow , exists=True):
        cmds.deleteUI(mirrorWindow )
    #window parameters     
    cmds.window(mirrorWindow, w=150, title="Mirror CTRL", rtf=True, sizeable=True)
    
    #needs a column layout for text field
    cmds.columnLayout(adj=True)
    
    #text for description
    cmds.text(l="To use: select duplicate of CTRL(top of hierarchy) in the scene to mirror", al="center")
   
    #slider to control FK size
   # cmds.floatSliderGrp("control_size", l="Control Size", field=True, min= 0.1, max=50.0, cw =(1,80), fmn=0.1,fmx=50, value=True)
   
    #button
    cmds.button(l="Mirror", c="mirrorControl()")
    
    #show window
    cmds.showWindow(mirrorWindow)
    
MirrorWindow()

  
  
