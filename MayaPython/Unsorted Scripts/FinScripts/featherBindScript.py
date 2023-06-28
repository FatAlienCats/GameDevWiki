import maya
import pymel.core as pm
import pprint as pp
import maya_rig.builder.lib.deformers as lib
import ast
def bind_feathers_to_joints(FK=True):
    """
    Finds Geo with span_name and binds it to to joints with corresponding name
    :param FK:
    :return:
    """
    span_names = [
        "L_flightPrimary",
        "L_flightSecondary",
        "L_flightTertial",
        "L_covertDorsalPrimary",
        "L_covertDorsalSecondary",
        "L_covertDorsalTertial",
        "L_covertVentralPrimary",
        "L_covertVentralSecondary",
        "L_covertVentralTertial",
        "L_alula",
        "R_flightPrimary",
        "R_flightSecondary",
        "R_flightTertial",
        "R_covertDorsalPrimary",
        "R_covertDorsalSecondary",
        "R_covertDorsalTertial",
        "R_covertVentralPrimary",
        "R_covertVentralSecondary",
        "R_covertVentralTertial",
        "R_alula",
        "tailFeather",
        "crestSpan",
        "crestFeather"
    ]

    for span_name in span_names:
        feather_geos = maya.cmds.ls("{0}_*geo".format(span_name), type="transform")
        for feather_geo in feather_geos:
            counter = feather_geo.split('_')[-2]
            fkJoints = maya.cmds.ls("{0}{1}*jnt".format(span_name, counter), type="joint")
            joints = maya.cmds.ls("{0}Twist_{1}*jnt".format(span_name, counter), type="joint")
            bendJoints = maya.cmds.ls("{0}Bend_{1}*jnt".format(span_name, counter), type="joint")
            kwargs = {
                "skinMethod": 0,
                "toSelectedBones": True,
            }
            if span_name == "crestFeather":
                args = [feather_geo] + fkJoints
                print fkJoints
                print feather_geo
            else:
                args = [feather_geo] + joints
                print feather_geo
                print joints

            # Bind geo to skin
            skin = maya.cmds.skinCluster(*args, **kwargs)
            # selects newly created skin and re assigns it to skin so that is is an object instead of unicode
            pm.select(skin, replace=True)
            skin = pm.selected()[0]
            print skin
            print bendJoints
            if span_name == "crestFeather":
                lib.skinFullyToClosest(skin, dict(zip(fkJoints, bendJoints)))
            else:
                lib.skinFullyToClosest(skin, dict(zip(joints, bendJoints)))


    print 'Done'



def copySkinWeightsToFeathers():
    """
    Usage: First select the source geo then the destination geo
    :return:
    """
    sel = pm.selected()
    original = sel[0]
    shape = original.getShape()
    inputs = shape.inputs()
    #print pp.pprint(dir(original))
    print original, inputs
    sel.remove(sel[0])

    for s in sel:
        shape = s.getShape()
        skinCluster = shape.inputs()
        pp.pprint(dir(shape))
        #print s, skinCluster
        pm.copySkinWeights(ss='skinCluster13', ds=skinCluster[4], noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='closestJoint')
        print "copying {} to {}".format(original, s)
        return



