#Colour Override# Julian Beiboer 2018
import maya.cmds as cmds

def colourOverride():
    selection = cmds.ls(sl=True)
    # set rgbcolour to tile selected
    rgbcolour = cmds.palettePort( 'palette', query=True, rgb=True )
    
    #Assign 'colour' a index value based of colour selection
    #RED
    if rgbcolour == [1.0,0.0,0.0]:
        colour = 13
    #YELLOW
    if rgbcolour == [0.9375, 1.0, 0.0]:
        colour = 17
    #GREEN
    if rgbcolour == [0.0, 1.0, 0.125]:
        colour = 14
    #LIGHT BLUE
    if rgbcolour == [0.0, 0.8125, 1.0]:
        colour = 18
    #BLUE    
    if rgbcolour == [0.25, 0.0, 1.0]:
        colour = 6
    #for each curve selected assign override colour to variable 'colour'
    for sel in selection:
        shape = cmds.listRelatives(sel, children = True)
        # set colour override to enabled
        cmds.setAttr(shape[0] + '.overrideEnabled', 1)
        #change colour
        cmds.setAttr(shape[0] + '.overrideColor', colour)
    

     
def OverrideWindow():
    
    #variable to call window
    ocWindow = "ocWindow"
    
    #if the window is already open, delete that instance
    if cmds.window(ocWindow, exists=True):
        cmds.deleteUI(ocWindow)
    
    #window parameters     
    cmds.window(ocWindow, w=150, title="Colour Override", rtf=True, sizeable=True)
    
    #needs a column layout for text field
    cmds.columnLayout(adj=True)

    #text for description
    cmds.text(l="Select a Colour ", al="center")
    
    #Colour palette UI
    cmds.frameLayout(h=75,labelVisible=0)
    # create a palette of 5 columns and 1 rows
    cmds.palettePort( 'palette', dim=(5, 1) )

    #button
    cmds.button(l="Override Colour", c="colourOverride()")
    
    cmds.showWindow(ocWindow)
    
OverrideWindow()
