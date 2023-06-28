"""ParentConstraint control, by Julian Beiboer, 2019

Creates a control for each object selected, with options to: 
create a global control, set up scaleConstraints 
and change the controls colour.
"""
import maya.cmds as cmds

# get selected objects
selection = cmds.ls(sl=True)
# colour index, do not change these values
red = 13
yellow = 17
green = 14
light_blue = 18
blue = 6
# Modify these variables.
make_global_ctrl = True
joints_scalable = True
control_size = 1
global_ctrl_size = 5
colour = yellow  
# Specify suffix to be removed. 
suffix_tbr = 'bind'  

if cmds.objExists('do_not_touch'):
    cmds.warning('Constraints moved to existing do_not_touch group')
else:
    cmds.group(em=True, n='do_not_touch')    
if cmds.objExists('controls_grp'):
    make_global_ctrl = False
    cmds.warning('Global already exists')
if make_global_ctrl:
        cmds.group(em=True, n='controls_grp')
for sel in selection:
    if suffix_tbr not in sel:
        cmds.error('suffix_tbr not found, check joint names')
        
    ctrl = cmds.circle(c=(0, 0, 0), nr=(1, 0, 0), 
        n=sel.replace(suffix_tbr, '_ctrl'), r=control_size, ch=False)
    cmds.makeIdentity(apply=True)
    # Sets colour override to 'enabled' and changes colour.
    cmds.setAttr(ctrl[0] + '.overrideEnabled', 1)
    cmds.setAttr(ctrl[0] + '.overrideColor', colour)
    # Sets up constraints and groups.
    offset = cmds.group(n=sel.replace(suffix_tbr, '_offset'))
    cmds.delete(cmds.parentConstraint(sel, (offset)))
    cmds.parentConstraint(ctrl, sel, n=(sel + '_parentConstraint'))
    cmds.parent(sel+'_parentConstraint', 'do_not_touch')
    if joints_scalable:
        cmds.scaleConstraint(ctrl, sel, n=(sel + '_scaleConstraint'))
        cmds.parent(sel + '_scaleConstraint', 'do_not_touch')
        cmds.setAttr(sel + '.segmentScaleCompensate', 0)
    if make_global_ctrl:
        cmds.parent(offset, 'controls_grp')    
if make_global_ctrl:
    global_ctrl = cmds.circle(c=(0, 0, 0), nr=(1, 0, 0), 
	     n=selection[0].replace(suffix_tbr, '_global_ctrl'),
	     r=global_ctrl_size, ch=False)
    cmds.delete(cmds.parentConstraint(selection[0], (global_ctrl)))
    cmds.group(selection[0], n='skeleton_grp')
    cmds.parent('controls_grp', 'skeleton_grp', 
	    'do_not_touch', global_ctrl)