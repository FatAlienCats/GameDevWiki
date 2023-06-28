## Center joint in loop ##

import maya.cmds as cmds

selection = cmds.ls(sl=True)

for sel in selection:
    ClusterTemp = cmds.cluster (en=1, n='clustertemp' ) # Create Cluster after selecting vertices
    JointTemp = cmds.joint(p=(0,0,0),name='jointtemp') # Create Joint
     
    cmds.pointConstraint(ClusterTemp, JointTemp, offset= (0,0,0), mo = False) #Pointconstrain Joint to move position to Cluster
    
    cmds.parent(JointTemp, w =True) # unparent Joint
    cmds.delete(ClusterTemp) # delete Cluster