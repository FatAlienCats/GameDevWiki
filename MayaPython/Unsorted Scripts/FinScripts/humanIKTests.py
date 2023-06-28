# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
## Copyright
"""
Copyright (C) Toshio Ishida. All rights reserved.
"""
#-------------------------------------------------------------------------------

__author__ = 'Toshio Ishida [isd.toshio@gmail.com]'


import os
import sys
sys.dont_write_bytecode = True
import re

#from maya.common.utils import getSourceNodeFromPlug
from maya import cmds,mel

# humanIK Crash Bug
cmds.evaluationManager(mode="off")
NAME_SPACE = "navySeal"
# reference
from maya.app.quickRig import quickRigUI as qr

def set_HumanIK(name):
    hikInitialize()
    if cmds.ls(name):
        hikDeleteControlRig(name)
        cmds.delete(name)

    hikCreateCharacter(name)
    hikSetCurrentCharacter(name)
    hikUpdateTool()

    set_definition(name, hik_info)

    #mel.eval('hikCreateControlRig;')
    hikUpdateTool()

    HIKCH = hikGetCurrentCharacter()
    mel.eval('hikToggleLockDefinition();')

    #HIKpp = cmds.listConnections(HIKCH + '.propertyState', s=1, d=0) or []
    #for roll in hikRolls:
    #    cmds.setAttr(HIKpp[0] + '.' + roll[0], roll[1])

    hikCreateCustomControlRig(name)
    #hikCreateControlRig( name )
    hikUpdateTool()


def get_definition(character):
    hikBones = {}
    hik_count = cmds.hikGetNodeCount()
    for i in range( hik_count ):
        bone = mel.eval( 'hikGetSkNode( "%s" , %d )' % ( character , i ) )
        #bone = getSourceNodeFromPlug( cmds.GetHIKNode( character , i ) )
        if bone:
            hik_name = cmds.GetHIKNodeName( i )
            hikBones[hik_name] = {'bone':bone, 'hikid' : i}
    return hikBones


def set_definition(character, definition_info):
    hikBones = {}
    for hik_name, d_info in definition_info.items():
        bone = d_info.get('bone')
        hikid = d_info.get('hikid')
        mel.eval('setCharacterObject("%s:%s", "%s", %s, 0)' % (NAME_SPACE, bone, character, hikid))


def assume_preferred_angle(definition_info):
    for hik_name, d_info in definition_info.items():
        bone = d_info.get('bone')
        try:
            cmds.joint(bone, e=1, apa=1, ch=1)
        except:
            pass

def hikui():
    mel.eval("HIKCharacterControlsTool;")


def hikUpdateTool():
    melCode = """
        if ( hikIsCharacterizationToolUICmdPluginLoaded() )
        {
            hikUpdateCharacterList();
            hikUpdateCurrentCharacterFromUI();
            hikUpdateContextualUI();
            hikControlRigSelectionChangedCallback;

            hikUpdateSourceList();
            hikUpdateCurrentSourceFromUI();
            hikUpdateContextualUI();
            hikControlRigSelectionChangedCallback;
        }
        """
    try:
        mel.eval(melCode)
    except:
        pass



def hikNoneString( ):
    return (mel.eval( 'hikNoneString()' ) or '')


def hikCreateCharacter( nameHint ):
    return ( mel.eval( 'hikCreateCharacter( "%s" )' % nameHint ) )


def hikInitialize():
    if mel.eval( 'exists hikGetCurrentCharacter' ):
        character = hikGetCurrentCharacter( )
    else:
        character = ''
    mel.eval( 'HIKCharacterControlsTool();' )
    cmds.refresh()
    hikSetCurrentCharacter( character )


def hikGetCurrentCharacter():
    return ( mel.eval( 'hikGetCurrentCharacter()' ) or '' )


def hikSetCurrentCharacter(character):
    return (mel.eval( 'hikSetCurrentCharacter( "%s" )' % character ))


def hikCreateControlRig(character):
    melCode = """hikSetCurrentCharacter( "%s" ); hikCreateControlRig();"""
    mel.eval( melCode % character )

def hikCreateCustomControlRig(character):
    melCode = 'hikSetCurrentCharacter( "{0}" ); hikCreateCustomRig("{0}");'.format(character)
    cmds.select('{0}:placement_ctl'.format(NAME_SPACE))
    mel.eval(melCode)

def hikDeleteControlRig( character ):
    melCode = """hikSetCurrentCharacter( "%s" ); hikDeleteControlRig();"""
    mel.eval( melCode % character )


def hikGetControlRig( character ):
    return ( mel.eval( 'hikGetControlRig( "%s" )' % character ) or '' )


def hikGetSkeletonNodesMap( character ):
    nodes = { }
    for i in range( cmds.hikGetNodeCount( ) ):
        sourceNode = mel.eval( 'hikGetSkNode( "%s" , %d )' % ( character , i ) )
        if sourceNode:
            nodes[ cmds.GetHIKNodeName( i ) ] = sourceNode
    return nodes


# def hikSetCurrentSourceFromCharacter(character):
#     melCode = """hikSetCurrentSourceFromCharacter( "%s" );"""
#     mel.eval( melCode % character )


def hikSetSource(character, typeid):
    hikSetCurrentCharacter( character )
    _HUMAN_IK_SOURCE_MENU = "hikSourceList"
    _HUMAN_IK_SOURCE_MENU_OPTION = _HUMAN_IK_SOURCE_MENU + "|OptionMenu"
    cmds.optionMenu(_HUMAN_IK_SOURCE_MENU_OPTION, e=True, sl=typeid)
    mel.eval('hikUpdateCurrentSourceFromUI()')
    mel.eval('hikUpdateContextualUI()')
    mel.eval('hikControlRigSelectionChangedCallback')


def getEffFromHikNode(hikNode='Hips'):
    effCount = cmds.GetHIKEffectorCount()
    effecter = None
    for effid in range(effCount):
        effecter = cmds.GetHIKEffectorName(effid)
        FKId = cmds.GetFKIdFromEffectorId( effid )
        if hikNode == cmds.GetHIKNodeName( FKId ):
            return effecter
    return None


def getCtrlFromHikCtrl(HIK_NAME, hikNode='Hips'):
    ctrlrig = hikGetControlRig( HIK_NAME )
    ctrl = cmds.listConnections(ctrlrig+'.'+hikNode) or []
    if ctrl:
        return ctrl[0]
    return None


hik_info = {
    "RightHandIndex1": {"hikid": 78, "bone": "R_index_001_jnt"},
    "RightHandIndex2": {"hikid": 79, "bone": "R_index_002_jnt"},
    "RightHandIndex3": {"hikid": 80, "bone": "R_index_003_jnt"},
    "RightInHandPinky": {"hikid": 156, "bone": "R_pinky_000_jnt"},
    "RightHandPinky1": {"hikid": 90, "bone": "R_pinky_001_jnt"},
    "RightHandPinky2": {"hikid": 91, "bone": "R_pinky_002_jnt"},
    "RightHandPinky3": {"hikid": 92, "bone": "R_pinky_003_jnt"},
    "LeftHandMiddle1": {"hikid": 58, "bone": "L_middle_001_jnt"},
    "LeftHandMiddle2": {"hikid": 59, "bone": "L_middle_002_jnt"},
    "LeftHandMiddle3": {"hikid": 60, "bone": "L_middle_003_jnt"},
    "LeftHandIndex1": {"hikid": 54, "bone": "L_index_001_jnt"},
    "LeftHandIndex2": {"hikid": 55, "bone": "L_index_002_jnt"},
    "LeftHandIndex3": {"hikid": 56, "bone": "L_index_003_jnt"},
    "RightInHandRing": {"hikid": 155, "bone": "R_ring_000_jnt"},
    "RightHandRing1": {"hikid": 86, "bone": "R_ring_001_jnt"},
    "RightHandRing2": {"hikid": 87, "bone": "R_ring_002_jnt"},
    "RightHandRing3": {"hikid": 88, "bone": "R_ring_003_jnt"},
    "LeftHandThumb1": {"hikid": 50, "bone": "L_thumb_001_jnt"},
    "LeftHandThumb2": {"hikid": 51, "bone": "L_thumb_002_jnt"},
    "LeftHandThumb3": {"hikid": 52, "bone": "L_thumb_003_jnt"},
    "RightHandThumb1": {"hikid": 74, "bone": "R_thumb_001_jnt"},
    "RightHandThumb2": {"hikid": 75, "bone": "R_thumb_002_jnt"},
    "RightHandThumb3": {"hikid": 76, "bone": "R_thumb_003_jnt"},
    "LeftInHandRing": {"hikid": 149, "bone": "L_ring_000_jnt"},
    "LeftHandRing1": {"hikid": 62, "bone": "L_ring_001_jnt"},
    "LeftHandRing2": {"hikid": 63, "bone": "L_ring_002_jnt"},
    "LeftHandRing3": {"hikid": 64, "bone": "L_ring_003_jnt"},
    "LeftInHandPinky": {"hikid": 150, "bone": "L_pinky_000_jnt"},
    "LeftHandPinky1": {"hikid": 66, "bone": "L_pinky_001_jnt"},
    "LeftHandPinky2": {"hikid": 67, "bone": "L_pinky_002_jnt"},
    "LeftHandPinky3": {"hikid": 68, "bone": "L_pinky_003_jnt"},
    "RightHandMiddle1": {"hikid": 82, "bone": "R_middle_001_jnt"},
    "RightHandMiddle2": {"hikid": 83, "bone": "R_middle_002_jnt"},
    "RightHandMiddle3": {"hikid": 84, "bone": "R_middle_003_jnt"},
    "Spine": {"hikid": 8, "bone": "torsoIkResult_001_jnt"},
    "Spine1": {"hikid": 23, "bone": "torsoIkResult_002_jnt"},
    "Spine2": {"hikid": 24, "bone": "torsoIkResult_003_jnt"},
    "Spine3": {"hikid": 25, "bone": "torsoIkResult_004_jnt"},
    "Spine4": {"hikid": 26, "bone": "torsoEnd_jnt"},
    "LeftHand": {"hikid": 11, "bone": "L_wristResult_jnt"},
    "RightHand": {"hikid": 14, "bone": "R_wristResult_jnt"},
    "Neck": {"hikid": 20, "bone": "neck_jnt"},
    "Head": {"hikid": 15, "bone": "head_jnt"},
    "LeftArm": {"hikid": 9, "bone": "L_shoulderResult_jnt"},
    "LeftUpLeg": {"hikid": 2, "bone": "L_hipResult_jnt"},
    "LeftLeg": {"hikid": 3, "bone": "L_kneeResult_jnt"},
    "LeftForeArm": {"hikid": 10, "bone": "L_elbowResult_jnt"},
    "RightForeArm": {"hikid": 13, "bone": "R_elbowResult_jnt"},
    "LeftShoulder": {"hikid": 18, "bone": "L_clav_jnt"},
    "RightShoulder": {"hikid": 19, "bone": "R_clav_jnt"},
    "Hips": {"hikid": 1, "bone": "torsoBase_jnt"},
    "RightArm": {"hikid": 12, "bone": "R_shoulderResult_jnt"},
    "LeftToeBase": {"hikid": 16, "bone": "L_ballResult_jnt"},
    "RightToeBase": {"hikid": 17, "bone": "R_ballResult_jnt"},
    "LeftFoot": {"hikid": 4, "bone": "L_ankleResult_jnt"},
    "RightUpLeg": {"hikid": 5, "bone": "L_hipResult_jnt"},
    "RightLeg": {"hikid": 6, "bone": "L_kneeResult_jnt"},
    "RightFoot": {"hikid": 7, "bone": "L_ankleResult_jnt"},
    'LeafLeftArmRoll1': {'bone': 'L_shoulderResultTwist_001_jnt', 'hikid': 176},
    'LeafLeftArmRoll2': {'bone': 'L_shoulderResultTwist_002_jnt', 'hikid': 184},

    'LeafLeftForeArmRoll1': {'bone': 'L_elbowResultTwist_001_jnt', 'hikid': 177},
    'LeafLeftForeArmRoll2': {'bone': 'L_elbowResultTwist_002_jnt', 'hikid': 185},

    'LeafLeftLegRoll1': {'bone': 'L_kneeResultTwist_001_jnt', 'hikid': 173},
    'LeafLeftLegRoll2': {'bone': 'L_kneeResultTwist_002_jnt', 'hikid': 181},
    'LeafLeftUpLegRoll1': {'bone': 'R_hipResultTwist_001_jnt', 'hikid': 172},
    'LeafLeftUpLegRoll2': {'bone': 'R_hipResultTwist_002_jnt', 'hikid': 180},
    'LeafRightArmRoll1': {'bone': 'R_shoulderResultTwist_001_jnt', 'hikid': 178},
    'LeafRightArmRoll2': {'bone': 'R_shoulderResultTwist_002_jnt', 'hikid': 186},

    'LeafRightForeArmRoll1': {'bone': 'R_elbowResultTwist_001_jnt', 'hikid': 179},
    'LeafRightForeArmRoll2': {'bone': 'R_elbowResultTwist_002_jnt', 'hikid': 187},
    'LeafRightLegRoll1': {'bone': 'R_kneeResultTwist_001_jnt', 'hikid': 175},
    'LeafRightLegRoll2': {'bone': 'R_kneeResultTwist_002_jnt', 'hikid': 183},
}

hikRolls = [
    ['ParamLeafLeftArmRoll1', 0],
    ['ParamLeafLeftArmRoll2', 0.25],
    ['ParamLeafLeftArmRoll3', 0.5],
    ['ParamLeafLeftArmRoll4', 0.75],
    ['ParamLeafLeftArmRoll5', 1],

    ['ParamLeafRightArmRoll1', 0],
    ['ParamLeafRightArmRoll2', 0.25],
    ['ParamLeafRightArmRoll3', 0.5],
    ['ParamLeafRightArmRoll4', 0.75],
    ['ParamLeafRightArmRoll5', 1],

    ['ParamLeafLeftForeArmRoll1', 0],
    ['ParamLeafLeftForeArmRoll2', 0.25],
    ['ParamLeafLeftForeArmRoll3', 0.5],
    ['ParamLeafLeftForeArmRoll4', 0.75],
    ['ParamLeafLeftForeArmRoll5', 1],

    ['ParamLeafRightForeArmRoll1', 0],
    ['ParamLeafRightForeArmRoll2', 0.25],
    ['ParamLeafRightForeArmRoll3', 0.5],
    ['ParamLeafRightForeArmRoll4', 0.75],
    ['ParamLeafRightForeArmRoll5', 1],

    ['ParamLeafLeftUpLegRoll1', 0],
    ['ParamLeafLeftUpLegRoll2', 0.2],
    ['ParamLeafLeftUpLegRoll3', 0.5],
    ['ParamLeafLeftUpLegRoll4', 0.75],
    ['ParamLeafLeftUpLegRoll5', 1],

    ['ParamLeafLeftLegRoll1', 0],
    ['ParamLeafLeftLegRoll2', 0.25],
    ['ParamLeafLeftLegRoll3', 0.5],
    ['ParamLeafLeftLegRoll4', 0.75],
    ['ParamLeafLeftLegRoll5', 1],

    ['ParamLeafRightUpLegRoll1', 0],
    ['ParamLeafRightUpLegRoll2', 0.2],
    ['ParamLeafRightUpLegRoll3', 0.5],
    ['ParamLeafRightUpLegRoll4', 0.75],
    ['ParamLeafRightUpLegRoll5', 1],

    ['ParamLeafRightLegRoll1', 0],
    ['ParamLeafRightLegRoll2', 0.25],
    ['ParamLeafRightLegRoll3', 0.5],
    ['ParamLeafRightLegRoll4', 0.75],
    ['ParamLeafRightLegRoll5', 1],
]
