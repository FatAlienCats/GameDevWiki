import pymel.core
import pprint

NAME_SPACE = ['mixamorig', '']
RETARGETING_DICTIONARY = {
    'L_ankleResult': {'fin': 'L_ankleResult_jnt', 'mixamo': 'LeftFoot'},
    'L_ballResult': {'fin': 'L_ballResult_jnt', 'mixamo': 'LeftToeBase'},
    'L_clav': {'fin': 'L_clav_jnt', 'mixamo': 'LeftShoulder'},
    'L_elbowResult': {'fin': 'L_elbowResult_jnt', 'mixamo': 'LeftForeArm'},
    'L_hipResult': {'fin': 'L_hipResult_jnt', 'mixamo': 'LeftUpLeg'},
    'L_kneeResult': {'fin': 'L_kneeResult_jnt', 'mixamo': 'LeftLeg'},
    'L_shoulderResult': {'fin': 'L_shoulderResult_jnt', 'mixamo': 'LeftArm'},
    'L_wristResult': {'fin': 'L_wristResult_jnt', 'mixamo': 'LeftHand'},

    'R_ankleResult': {'fin': 'R_ankleResult_jnt', 'mixamo': 'RightFoot'},
    'R_ballResult': {'fin': 'R_ballResult_jnt', 'mixamo': 'RightToeBase'},
    'R_clav': {'fin': 'R_clav_jnt', 'mixamo': 'RightShoulder'},
    'R_elbowResult': {'fin': 'R_elbowResult_jnt', 'mixamo': 'RightForeArm'},
    'R_hipResult': {'fin': 'R_hipResult_jnt', 'mixamo': 'RightUpLeg'},
    'R_kneeResult': {'fin': 'R_kneeResult_jnt', 'mixamo': 'RightLeg'},
    'R_shoulderResult': {'fin': 'R_shoulderResult_jnt', 'mixamo': 'RightArm'},
    'R_wristResult': {'fin': 'R_wristResult_jnt', 'mixamo': 'RightHand'},

    'torsoBase_jnt': {'fin': 'torsoBase_jnt', 'mixamo': 'Hips'},
    'torsoEnd_jnt': {'fin': 'torsoEnd_jnt', 'mixamo': 'Spine2'},
    'torsoIkResult_001': {'fin': 'torsoIkResult_001_jnt', 'mixamo': 'Spine'},

    'head_jnt': {'fin': 'head_jnt', 'mixamo': 'Head'},
    'neck_jnt': {'fin': 'neck_jnt', 'mixamo': 'Neck'}

}


class MixamoToFinRetargeting:
    constraint_type = ""
    dictionary = {}

    def __init__(self):
        pass


class OrientConstaintRetargeting(MixamoToFinRetargeting):
    constraint_type = "orient"
    dictionary = {
        'L_ankleFK': {'fin': 'L_ankleFK_ctl', 'mixamo': 'LeftFoot'},
        'L_ballFK': {'fin': 'L_ballFK_ctl', 'mixamo': 'LeftToeBase'},
        #'L_ballIK': {'fin': 'L_legRoll_ctl', 'mixamo': 'LeftToeBase'},
        'L_hipFK': {'fin': 'L_hipFK_ctl', 'mixamo': 'LeftUpLeg'},
        'L_kneeFK': {'fin': 'L_kneeFK_ctl', 'mixamo': 'LeftLeg'},
        'L_clav': {'fin': 'L_clav_ctl', 'mixamo': 'LeftShoulder'},
        'L_elbowFK': {'fin': 'L_elbowFK_ctl', 'mixamo': 'LeftForeArm'},
        'L_shoulderFK': {'fin': 'L_shoulderFK_ctl', 'mixamo': 'LeftArm'},
        'L_wristFK': {'fin': 'L_wristFK_ctl', 'mixamo': 'LeftHand'},
        'R_ankleFK': {'fin': 'R_ankleFK_ctl', 'mixamo': 'RightFoot'},
        'R_ballFK': {'fin': 'R_ballFK_ctl', 'mixamo': 'RightToeBase'},
        #'R_ballIK': {'fin': 'R_legRoll_ctl', 'mixamo': 'RightToeBase'},
        'R_hipFK': {'fin': 'R_hipFK_ctl', 'mixamo': 'RightUpLeg'},
        'R_kneeFK': {'fin': 'R_kneeFK_ctl', 'mixamo': 'RightLeg'},
        'R_clav': {'fin': 'R_clav_ctl', 'mixamo': 'RightShoulder'},
        'R_elbowFK': {'fin': 'R_elbowFK_ctl', 'mixamo': 'RightForeArm'},
        'R_shoulderFK': {'fin': 'R_shoulderFK_ctl', 'mixamo': 'RightArm'},
        'R_wristFK': {'fin': 'R_wristFK_ctl', 'mixamo': 'RightHand'},
        'head_ctl': {'fin': 'head_ctl', 'mixamo': 'Head'},
        'neck_ctl': {'fin': 'neck_ctl', 'mixamo': 'Neck'},
        'torsofk_002': {'fin': 'torsofk_002_ctl', 'mixamo': 'Spine'},
        'torsofk_003': {'fin': 'torsofk_003_ctl', 'mixamo': 'Spine1'},
        'torsofk_005': {'fin': 'torsofk_005_ctl', 'mixamo': 'Spine2'},
        'cog_ctl': {'fin': 'cog_ctl', 'mixamo': 'Hips'},
        'R_ankleIK': {'fin': 'R_ankleIK_ctl', 'mixamo': 'RightFoot'},
        'L_ankleIK': {'fin': 'L_ankleIK_ctl', 'mixamo': 'LeftFoot'},
        }


class PointConstraintRetargeting(MixamoToFinRetargeting):
    constraint_type = "point"
    dictionary = {'R_ankleIK': {'fin': 'R_ankleIK_ctl', 'mixamo': 'RightFoot'},
                  'L_ankleIK': {'fin': 'L_ankleIK_ctl', 'mixamo': 'LeftFoot'},
                  'cog_ctl': {'fin': 'cog_ctl', 'mixamo': 'Hips'}}

"""orientConstraint_dict = {
    'L_ankleFK': {'fin': 'L_ankleFK_ctl', 'mixamo': 'LeftFoot'},
    'L_ballFK': {'fin': 'L_ballFK_ctl', 'mixamo': 'LeftToeBase'},
    'L_ballIK': {'fin': 'L_legRoll_ctl', 'mixamo': 'LeftToeBase'},
    'L_hipFK': {'fin': 'L_hipFK_ctl', 'mixamo': 'LeftUpLeg'},
    'L_kneeFK': {'fin': 'L_kneeFK_ctl', 'mixamo': 'LeftLeg'},
    'L_clav': {'fin': 'L_clav_ctl', 'mixamo': 'LeftShoulder'},
    'L_elbowFK': {'fin': 'L_elbowFK_ctl', 'mixamo': 'LeftForeArm'},
    'L_shoulderFK': {'fin': 'L_shoulderFK_ctl', 'mixamo': 'LeftArm'},
    'L_wristFK': {'fin': 'L_wristFK_ctl', 'mixamo': 'LeftHand'},
    'R_ankleFK': {'fin': 'R_ankleFK_ctl', 'mixamo': 'RightFoot'},
    'R_ballFK': {'fin': 'R_ballFK_ctl', 'mixamo': 'RightToeBase'},
    'R_ballIK': {'fin': 'R_legRoll_ctl', 'mixamo': 'RightToeBase'},
    'R_hipFK': {'fin': 'R_hipFK_ctl', 'mixamo': 'RightUpLeg'},
    'R_kneeFK': {'fin': 'R_kneeFK_ctl', 'mixamo': 'RightLeg'},
    'R_clav': {'fin': 'R_clav_ctl', 'mixamo': 'RightShoulder'},
    'R_elbowFK': {'fin': 'R_elbowFK_ctl', 'mixamo': 'RightForeArm'},
    'R_shoulderFK': {'fin': 'R_shoulderFK_ctl', 'mixamo': 'RightArm'},
    'R_wristFK': {'fin': 'R_wristFK_ctl', 'mixamo': 'RightHand'},
    'head_ctl': {'fin': 'head_ctl', 'mixamo': 'Head'},
    'neck_ctl': {'fin': 'neck_ctl', 'mixamo': 'Neck'},
    'torsofk_002': {'fin': 'torsofk_002_ctl', 'mixamo': 'Spine'},
    'torsofk_003': {'fin': 'torsofk_003_ctl', 'mixamo': 'Spine1'},
    'torsofk_005': {'fin': 'torsofk_005_ctl', 'mixamo': 'Spine2'}
}
parentConstraint_dict = {'cog_ctl': {'fin': 'cog_ctl', 'mixamo': 'Hips'}}
pointConstraint_dict = {'R_ankleIK': {'fin': 'R_ankleIK_ctl', 'mixamo': 'RightFoot'},
                        'L_ankleIK': {'fin': 'L_ankleIK_ctl', 'mixamo': 'LeftFoot'}, }

""" # old

def main():
    locator_grp = pymel.core.group(empty=1)
    connectMixamoToFin(locator_grp, OrientConstaintRetargeting)
    connectMixamoToFin(locator_grp, PointConstraintRetargeting)

    #bakeAnimationToControls([OrientConstaintRetargeting, PointConstraintRetargeting])


def connectMixamoToFin(locator_grp, retargeting_class):
    dictionary = retargeting_class.dictionary
    constraint_type = retargeting_class.constraint_type
    for hik_name, d_info in dictionary.items():
        ctrl = "{0}:{1}".format(NAME_SPACE[1], d_info.get('fin'))
        mixa = "{0}:{1}".format(NAME_SPACE[0], d_info.get('mixamo'))

        #pymel.core.setAttr(ctrl
        if constraint_type == "point":
            pymel.core.matchTransform(ctrl, mixa, pos=1, rot=0, scl=0)  # get cog_ctl at mixamo hips position

        mixa_loc = createLocator(mixa, locator_grp)
        ctrl_loc = createLocator(ctrl, locator_grp)

        pymel.core.parentConstraint(mixa, mixa_loc, mo=0)

        if constraint_type == "orient":
            mixa_loc.r.connect(ctrl_loc.r)
            pymel.core.orientConstraint(ctrl_loc, ctrl, mo=1)
        if constraint_type == "point":
            mixa_loc.t.connect(ctrl_loc.t)
            pymel.core.pointConstraint(ctrl_loc, ctrl, mo=1)


def createLocator(targertObject, parent_grp):
    loc = pymel.core.spaceLocator(name="{}_Loc".format(targertObject))
    pymel.core.matchTransform(loc, targertObject)
    loc.setParent(parent_grp)
    return loc


def bakeAnimationToControls(retargeting_classes):
    controls_to_bake = []
    for classes in retargeting_classes:
        dictionary = classes.dictionary

        for hik_name, d_info in dictionary.items():
            ctrl = "{0}:{1}".format(NAME_SPACE[1], d_info.get('fin'))
            controls_to_bake.append(ctrl)
            mixa = "{0}:{1}".format(NAME_SPACE[0], d_info.get('mixamo'))

    all_keys = sorted(pymel.core.keyframe(mixa, q=True) or [])  # sort frames to find first and last

    if all_keys:
        start_time = all_keys[0]
        end_time = all_keys[-1]
        pymel.core.bakeResults(controls_to_bake, t=(start_time, end_time), simulation=0, sampleBy=1, )




DICT = {}


def resetDict():
    DICT = None


def printDict():
    pprint.pprint(DICT)


def addToDictionary():
    sel = pymel.core.selected()
    split = "{0}_{1}".format(sel[1].split("_")[0], sel[1].split("_")[1])
    DICT["{}".format(split)] = {"mixamo": "{}".format(sel[0]), "fin": "{}".format(sel[1])}
