import os
import pprint

import pymel.core as pm
import pymel
import mutils
import animModules
import pprint as pp
import maya.cmds as cmd
import maya.cmds as cmds
import logging
import tempfile
logging.basicConfig()
logger = logging.getLogger('RiggingTools')
logger.setLevel(logging.DEBUG)

from Helpers.skin import Skin
import Helpers.api as api
import math


def constraint_selection_to_last():
    sel = pm.selected()
    last = sel.pop()

    for s in sel:
        pm.parentConstraint(last, s, mo=1, )


def toggle_all_orientation_axis(value):
    joints = pm.ls(type='joint')
    for joint in joints:
        pm.setAttr("{}.displayLocalAxis".format(joint), value)


def flood_select_to_jnt():
    sel = pm.selected()
    deformer = pm.listHistory(pm.selected()[0], type='skinCluster')[0]

    cmds.skinPercent(deformer, sel, transformValue=[(new_joint, sel)], r=True)
    pass


def disable_inherit_transforms():
    pm.setAttr("model.inheritsTransform", 0)
    #pm.setAttr("deformers.inheritsTransform", 0)
    pm.setAttr("doNotTouch_GRP.inheritsTransform", 0)
    save_increment_scene()


def offset_based_off_camera():
    camera = pm.PyNode("renderCam:shotCam")
    translation = camera.getTranslation(ws=True)

    logger.info("Old Camera position: {}".format(translation))
    pm.setAttr("scene.tx", -1*translation[0])
    pm.setAttr("scene.ty", -1*translation[1])
    pm.setAttr("scene.tz", -1*translation[2])
    logger.info("New Camera position: {}".format(camera.getTranslation(ws=True)))
    all_objects = cmds.ls()

    """# Filter the list to only include objects with ":model" in their name
    model_objects = [obj for obj in all_objects if ":model" in obj]
    deformer_objects = [obj for obj in all_objects if ":deformers" in obj]
    doNotTouch_GRP_objects = [obj for obj in all_objects if ":doNotTouch_GRP" in obj]

    for model, deformer, doNotTouch in zip(model_objects, deformer_objects, doNotTouch_GRP_objects):
        pm.setAttr("{}.inheritsTransform".format(model), 0)
        pm.setAttr("{}.inheritsTransform".format(deformer), 0)
        pm.setAttr("{}.inheritsTransform".format(doNotTouch), 0)"""

    """# might need to toggle inherits transforms on all objects
    children = pm.PyNode("scene").getChildren()
    for child in children:
        # get namespace for object
        namespace = child.namespace()
        if namespace:
            pm.setAttr("{}model.inheritsTransform".format(namespace), 0)
            pm.setAttr("{}deformers.inheritsTransform".format(namespace), 0)
            if pm.objExists("{}doNotTouch_GRP".format(namespace)):
                pm.setAttr("{}doNotTouch_GRP.inheritsTransform".format(namespace), 0)"""


def get_jnts_on_skincluster():
    sel = pm.selected()[0]
    deformers = pm.listHistory(sel, type='skinCluster')[0]
    jnts = pm.skinCluster(deformers, q=1, influence=1)
    pm.select(jnts, r=1)
    pprint.pprint(jnts)



def copy_shapes():
    #TODO:Modify to work with object with multiple shapes eg squares and cubes
    sel = pm.selected()
    source_obj = sel[0]
    target_obj = sel[1]

    translation = source_obj.getTranslation(space='world')
    rotation = source_obj.getRotation(space='world')
    scale = source_obj.getScale()

    rotation_pivot = pm.xform(target_obj, q=1, rp=1)
    source_shapes = pm.listRelatives(source_obj, shapes=True)
    print(source_shapes)
    # Get the old shape from the target object
    target_shapes = pm.listRelatives(target_obj, shapes=True)
    print(target_shapes)
    # Parent the new shape to the target object
    pm.parent(source_shapes, target_obj, shape=True, relative=True)
    target_obj.setTranslation(translation)
    target_obj.setRotation(rotation)
    target_obj.setScale(scale)

    pm.makeIdentity(target_obj, apply=True, t=1, r=1, s=1, n=0, pn=1)
    target_obj.setPivots(rotation_pivot, ws=True)
    # Delete the old shape and source transform
    pm.delete(target_shapes, source_obj)
    # Rename new shape
    for s, t in zip(source_shapes, target_shapes):
        s.rename(t.name())


def get_points_within_radius():
    # Set the center point and radius
    # Get the name of the selected vertex
    selected_vertex = pm.selected()[0]
    mesh_object = selected_vertex.node().getParent()
    # Get the position of the selected vertex
    vertex_position = cmds.pointPosition(selected_vertex, world=True)
    center_point = vertex_position

    # Get the radius from the dictionary
    radius = cmds.softSelect(q=True, ssd=True)
    print(radius, center_point)
    # Get all vertices of the mesh object
    vertices = cmds.ls("{0}.vtx[*]".format(mesh_object), flatten=True)

    # Loop through all vertices and check if they are within the radius
    result = []
    for vertex in vertices:
        # Get the position of the vertex
        vertex_position = cmds.pointPosition(vertex, world=True)

        # Calculate the distance between the center point and the current vertex
        distance = math.sqrt(
            (center_point[0] - vertex_position[0]) ** 2 + (center_point[1] - vertex_position[1]) ** 2 + (
                        center_point[2] - vertex_position[2]) ** 2)
        print(distance)
        # If the distance is within the radius, add the vertex to the result list
        if distance <= radius:
            result.append(vertex)

    # Select the vertices
    #cmds.select(cmds.filterExpand(result, sm=31))
    print(result)
    #cmds.select(result)

def get_vertex_within_sphere():
    # Set the center and radius of the sphere
    # Get point
    selected_vertex = cmds.ls(selection=True)[0]
    # Get the position of the selected vertex
    vertex_position = cmds.pointPosition(selected_vertex, world=True)
    # create sphere from soft select and point
    radius = cmds.softSelect(q=True, ssd=True)
    # Debug only
    #phere = pm.polySphere(n='mySphere', sx=12, sy=12)
    #sphere[0].setTranslation(vertex_position, space='world')
    #sphere[0].setScale([radius, radius, radius], space='world')
    # end debug only
    center = vertex_position

    # Get all the vertices within the sphere
    vertices = pm.ls(type='mesh')[0].vtx

    vertices_weights = []
    for vertex in vertices:
        soft_select_vertex = {"index": 0,
                              "weight": 0}
        # Get the position of the vertex
        position = vertex.getPosition(space='world')

        point1 = pm.datatypes.Point(position)
        point2 = pm.datatypes.Point(center)

        # Calculate the distance between the two points
        distance = point1.distanceTo(point2)
        # If the distance is less than the radius, select the vertex
        if distance <= radius:
            weight = abs((distance/radius)-1)
            soft_select_vertex["index"] = vertex.name()
            soft_select_vertex["weight"] = weight

            vertices_weights.append(soft_select_vertex)
    print(vertices_weights)
    return vertices_weights


def skinTest(skin_cluster):
    skin = Skin(node=skin_cluster)
    print(skin.influence_count())
    print(skin)
    skin._clear()
    print(skin.influence_count())
    print(skin)


def connect_up_blendshapes():

    sel = pm.selected()
    blend_shape_controller = "blendshape_hooks"
    blend_shape = "Face_BSP"
    num = 0
    for s in sel:
        target_name = s.replace("_TGT", "")
        # create target from selected
        pm.blendShape(blend_shape, e=True, t=["body_geo", num, s, 1], w=[num, 0])

        pm.connectAttr("{}.{}".format(blend_shape_controller, target_name), "{}.{}".format(blend_shape, s))
        # blendShape -e -tc on -t |rig|model|high|geo|body_geo|body_geoShape 0 M_pucker_TGT_Shape 1 -w 0 0  Face_BSP;
        # blendShape -e -tc on -t |rig|model|high|geo|body_geo|body_geoShape 1 L_mouth_narrow_TGT_Shape 1 -w 1 0  Face_BSP;
        # setAttr "Face_BSP.M_pucker_TGT_Shape" 0.743017;
        # Connect control driver to target weight
        num += 1
        pass


def save_increment_scene():
    # Get the current scene name
    current_scene = cmd.file(q=True, sceneName=True)

    # Get the new scene name
    new_scene_name = animModules.increment_scene_number(current_scene)

    # Save the new scene
    cmd.file(rename=new_scene_name)
    cmd.file(save=True, type='mayaAscii')

    print(f'Saved new scene: {new_scene_name}')


def get_all_objects_with_suffix(ctl_type, suffix, select=False):
    """
        Searches the scene and finds all transforms that end with the given suffix under a given group.
    Args:
        ctl_type(str): transform type to search for.
        suffix(str): suffix to look for.
    Returns: A list of transform nodes that end with a given suffix and are children of a given group.
    """
    # control specific atm
    objects = []
    for obj in pm.ls(type=ctl_type):
        if obj.name().endswith(suffix):
            objects.append(obj)
    if select:
        pm.select(objects, r=True)
    return objects


def return_rig_to_bind():
    default_pose = "/mnt/production-data/StudioLibrary/BBF/Library/z_Misc/BindPoseAllControls.pose/pose.json"
    sel = pm.selected()
    namespace = sel[0].namespace().replace(":", "")
    pm.currentTime(1001)
    pose = mutils.Pose.fromPath(default_pose)
    pose.load(namespaces=[namespace])
    rig_nodes = pm.ls(type=["animLayer"])
    pm.delete(rig_nodes)
    clear_anim_on_rig()

    #controls = get_all_objects_with_suffix(ctl_type='transform', suffix="CTL")

def select_all(suffix, type, add=True, replace=False):
    controls = get_all_objects_with_suffix(ctl_type=type, suffix=suffix)
    pm.select(controls, add=add, r=replace)
    return controls


def quicktestMatch():
    sel = pm.selected()  # 0 = ik 1 = fk
    print(sel[0], sel[1])
    target = pm.xform(sel[0], q=True, ro=True, ws=1)
    print(target)
    pm.setAttr("{}.rotateX".format(sel[0]), target[0])
    pm.setAttr("{}.rotateY".format(sel[0]), target[1])
    pm.setAttr("{}.rotateZ".format(sel[0]), target[2])


def copySkinWeight():
    '''
    Works only if the skinClusters are named the same
    '''
    sel = pymel.core.selected()

    for s in sel:
        destination = s.getShape().inputs()[0]
        source = pymel.core.PyNode("temp:{0}".format(destination))
        pm.copySkinWeights(ss=source, ds=destination, noMirror=False)


def export_skin_weights(character_name, base_path="/home/julianbeiboer/Documents/"):
    sel = pm.selected()
    for s in sel:
        save_dir = "{}/{}".format(base_path, character_name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        deformers = pm.listHistory(s, type='skinCluster')
        for deformer in deformers:
            export_name = "{}_{}.xml".format(s.name(), deformer)
            pm.deformerWeights(export_name, export=True, deformer=deformer, format="XML", path=save_dir)


def import_skin_weights(character_name, base_path="/home/julianbeiboer/Documents/"):
    skin_weights = os.listdir("{}/{}".format(base_path, character_name))

    for weights in skin_weights:

        pass
    #get file name,
    #extract object name
    #create skin bind
    #import skin weights

    pass

def align_guides_to_temp():
    for s in pm.selected():
        pm.matchTransform(s, "temp:{}".format(s), position=1, rotation=1, scale=1)
    pass
def mute_selected_ctrls(mute=True):
    sel = pm.selected()
    for s in sel:
        node = pm.PyNode(s)
        attr = s.listAttr(k=True)
        for a in attr:
            if mute:
                pm.mute(a)
            else:
                pm.mute(a, disable=True)


def temp_export():
    """
    Saves a temp .ma file to your computers temp folder
    :return:
    """
    sel = pymel.core.selected()
    file_path = tempfile.gettempdir()
    pymel.core.cmds.file("{0}\exportTemp.mb".format(file_path), force=True, options='v=0', typ="mayaBinary", pr=True, es=True)


def temp_import():
    """Imports temp file from your temp folder"""
    file_path = tempfile.gettempdir()
    pymel.core.cmds.file("{0}\exportTemp.mb".format(file_path), i=True, typ="mayaBinary", options="v=0;", pr=True,
                 ra=True, ignoreVersion=True, mergeNamespacesOnClash=True, namespace="temp")


def get_selected(only_first = True):
    """Returns list of selected"""
    sel = pymel.core.selected()
    if only_first:
        return sel[0]
    else:
        return sel


def match_all_transforms():
    """
    Matches first selection to second selection
    Returns:

    """
    sel = get_selected(only_first=False)
    pm.matchTransform(sel[0], sel[1], pos=True, rot=True, scale=False)


def create_joint_from_selection(cluster=False, world_parent=False):
    sel = pymel.core.selected()
    joint = []
    if cluster:
        cluster = pymel.core.cluster(sel, rel=True, en=1)
        joints = pymel.core.createNode('joint', ss=1)
        pymel.core.delete(pymel.core.parentConstraint(cluster, joints, mo=False), cluster)
        return joints
    else:
        for s in sel:
            joints = pymel.core.createNode('joint', ss=1)
            pymel.core.matchTransform(joints, s)
            #pymel.core.delete(pymel.core.parentConstraint(s, joints, mo=0))
            if not world_parent:
                pymel.core.parent(joints, s)
                parent_transform = joints.getParent()
                pymel.core.makeIdentity(parent_transform, apply=True, s=1, t=1, r=1, n=0, pn=1)
                pymel.core.parent(joints, s)
                if parent_transform.type() == "transform":
                    pymel.core.delete(parent_transform)


def clear_key_frames(sel):
    if not sel:
        sel = pm.selected()
    for s in sel:
        attr = s.listAttr(k=True)
        for a in attr:
            pm.cutKey(a)


def snap_select_to_position():
    sel = pm.selected()[0]


    pass


def load_studio_library_anim(anim_path, controls):
    anim = mutils.Animation.fromPath(anim_path)  # load animation data to anim Class object
    anim.load(objects=controls, namespaces=None)  # load data onto controls listed


def get_parents(control):
    parent_node = control.getParent()
    parent_names = []
    while parent_node is not None:
        # Add the name of the parent node to the list
        parent_names.append(parent_node.name())
        # Get the next parent node
        parent_node = parent_node.getParent()

    return parent_names


def clear_anim_on_rig():
    attr_vs_default_value = {'sx': 1, 'sy': 1, 'sz': 1, 'rx': 0, 'ry': 0, 'rz': 0, 'tx': 0, 'ty': 0, 'tz': 0}

    sel = pm.selected()[0]

    controls = get_all_objects_with_suffix(ctl_type='transform', suffix="_CTL")
    for ctl in controls:
        anim_curves = pm.keyframe(ctl, q=True, name=True)
        for curve in anim_curves:
            pm.delete(curve)
            for attr in attr_vs_default_value:
                try:
                    pm.setAttr('{0}.{1}'.format(ctl, attr), attr_vs_default_value[attr])
                except:
                    pass


def get_namespace(node):

    return node.namespace()


def force_delete_object():
    sel = pm.selected()[0]
    pm.lockNode(sel, lock=False)
    pm.delete(sel)


def fix_match_loc():  # Temporary fix for locator position
    # rigs need to be in default position for the alignment to work correctly
    ik_loc = ["arm_match_LOC", "leg_match_LOC"]
    ik_controls = ["hand_IK_CTL", "foot_IK_CTL"]
    side = ["L_", "R_"]

    for loc, ctrl in zip(ik_loc, ik_controls):
        for s in side:
            cmd.matchTransform(s + loc, s + ctrl, pos=True, rot=True, scale=False)
            logger.log(logging.DEBUG, "Matched loc:{0}{1} to {0}{2}".format(s, loc, ctrl))


def print_list_of_selected():
    sel = pm.selected()
    print(sel)
    for s in sel:
        print(s.name())


def setup_work_env():
    import sys
    sys.path.append("/mnt/user-share/julianbeiboer/PythonTools")
    sys.path.append("/mnt/user-share/julianbeiboer/pipelineLocalRepos/popauto/popauto/scripts")


def scale_quick_fix():
    # Get nodes needed
    scale_grp = pm.PyNode("global_scale_GRP")
    guides = pm.PyNode("guides")
    # print(scale)
    scale_constraint_name = guides + 'ScaleFixTemp_scaleConstraint'
    stored_value_name = "ScaleFixTemp_StoredValue_TEMP"

    # if no scale_constraint_name in scene make one and adjust size
    if not pm.objExists(scale_constraint_name):
        scale = scale_grp.getScale()  # store the scale for later use
        stored_value = pm.nt.Transform(name=stored_value_name)  # create a new node to store value
        stored_value.setScale(scale)

        # create scale constraint
        scale_constraint = pm.scaleConstraint(scale_grp, guides,
                                              mo=True, weight=1, name=scale_constraint_name)
        pm.parent(scale_constraint, stored_value)
        # scale down global_scale_GRP to 1
        new_scale = (1, 1, 1)
        scale_grp.setScale(new_scale)

    # else reset size based off storedValue
    else:
        stored_value = pm.PyNode(stored_value_name)
        scale_grp.setScale(stored_value.getScale())
        scale_constraint = pm.PyNode(scale_constraint_name)
        pm.delete(stored_value)


def clean_combine():
    """Combines selected objects and renames them to the first object in selection"""
    sel = pm.selected()  # gets selected objects
    name = sel[0].name()  # store object[0]'s name in variable
    combined = pm.polyUnite(sel, cp=True, name=sel[0])  # combines objects
    combined_name = combined[0].name()  # store combined object's name in variable
    pm.delete(combined, ch=True)  # delete construction history
    pm.rename(combined_name, name)  # rename to original


def space_out_objects(gap=10):
    """Spaces selected object in a row alone x axis ensuring not objects overlap"""
    sel = pm.selected()
    last_size = 0
    last_pos = 0
    size_list = []  # list of bounding box size
    for obj in sel:
        b_box = pm.exactWorldBoundingBox(obj, ii=True)
        size_x = b_box[3] - b_box[0]
        size_list.append(size_x)

    for obj, size in zip(sel, size_list):
        # print obj, size
        pm.xform(obj, t=[0, 0, 0], ws=True)
        # lastSize + currentSize + gap + lastPos
        move_x = (last_size / 2) + (size / 2) + gap + last_pos
        print(move_x)
        pm.xform(obj, t=[move_x, 0, 0], r=True)

        last_pos = obj.getTranslation()[0]
        last_size = size


def clean_separate(cut_out=False):
    """
    Separates out faces from a mesh, creating a new mesh. 
    cutOut(bool): should the faces be deleted from original mesh
    """
    # Separates out faces from a mesh, creating a new mesh.
    faces = pm.selected()
    shape = faces[0].node()
    transform = shape.getTransform()
    dup = transform.duplicate(name='splitMesh')
    dup_shape = dup[0].getShape()

    new_faces = []
    # selects the faces of the duplicated mesh identical to the original
    for obj in faces:
        face_index = obj.currentItemIndex()
        new_faces.append('{}.f[{}]'.format(dup_shape, face_index))

    if cut_out:
        # Cut out face from original mesh
        pm.cmds.polyDelFacet(faces)

    # Duplicate face from original mesh
    pm.select(new_faces, r=True)
    pm.select('{}.f[*]'.format(dup_shape), tgl=True)  # inverses selection
    pm.cmds.polyDelFacet(pm.selected())  # deletes selected faces


def bake_locator():
    sel = pm.selected()
    pp.pprint(dir(sel[0]))
    return
    start = pm.playbackOptions(q=True, min=True)
    end = pm.playbackOptions(q=True, max=True)
    print(start, end)
    for s in sel:
        locator = pm.spaceLocator(n="baked_loc")
        constraint = pm.parentConstraint(s, locator)
        pm.bakeResults(locator, sm=False, sr=[True, 5], time=[start, end])
        pm.delete(constraint)

def bake_selected(sel):
    start = pm.playbackOptions(q=True, min=True)
    end = pm.playbackOptions(q=True, max=True)
    print(start, end)
    for s in sel:

        #bakeResults -t "1001:1250" -sampleBy 1 -oversamplingRate 1 -disableImplicitControl true -preserveOutsideKeys true -sparseAnimCurveBake false -removeBakedAttributeFromLayer false -removeBakedAnimFromLayer false -bakeOnOverrideLayer false -minimizeRotation true -controlPoints false -shape true {"L_LowerLidTip_JNT", "L_ball_FK_JNT", "L_ball_IK_JNT", "L_ball_JNT", "L_ball_inner_JNT", "L_ball_outer_JNT", "L_browInnerMid_JNT", "L_browInner_JNT", "L_browInner_arc_DRV_JNT", "L_browMiddle_JNT", "L_browMiddle_arc_DRV_JNT", "L_browOuterMid_JNT", "L_browOuter_JNT", "L_browOuter_arc_DRV_JNT", "L_cheekZero_JNT", "L_cheek_JNT", "L_clavicle_JNT", "L_cornerLip_JNT", "L_earZero_JNT", "L_ear_JNT", "L_elbow_A_twistBend_JNT", "L_elbow_B_twistBend_JNT", "L_elbow_C_twistBend_JNT", "L_elbow_FK_JNT", "L_elbow_IK_JNT", "L_elbow_JNT", "L_elbow_bendA_JNT", "L_elbow_lowTwist1_JNT", "L_eyeMaster_JNT", "L_eye_JNT", "L_eye_lower1_JNT", "L_eye_lower1_tip_JNT", "L_eye_lower2_JNT", "L_eye_lower2_tip_JNT", "L_eye_lower3_JNT", "L_eye_lower3_tip_JNT", "L_eye_lower4_JNT", "L_eye_lower4_tip_JNT", "L_eye_lower5_JNT", "L_eye_lower5_tip_JNT", "L_eye_lower6_JNT", "L_eye_lower6_tip_JNT", "L_eye_lower7_JNT", "L_eye_lower7_tip_JNT", "L_eye_lower8_JNT", "L_eye_lower8_tip_JNT", "L_eye_lower9_JNT", "L_eye_lower9_tip_JNT", "L_eye_lower10_JNT", "L_eye_lower10_tip_JNT", "L_eye_lower11_JNT", "L_eye_lower11_tip_JNT", "L_eye_upper1_JNT", "L_eye_upper1_tip_JNT", "L_eye_upper2_JNT", "L_eye_upper2_tip_JNT", "L_eye_upper3_JNT", "L_eye_upper3_tip_JNT", "L_eye_upper4_JNT", "L_eye_upper4_tip_JNT", "L_eye_upper5_JNT", "L_eye_upper5_tip_JNT", "L_eye_upper6_JNT", "L_eye_upper6_tip_JNT", "L_eye_upper7_JNT", "L_eye_upper7_tip_JNT", "L_eye_upper8_JNT", "L_eye_upper8_tip_JNT", "L_eye_upper9_JNT", "L_eye_upper9_tip_JNT", "L_eye_upper10_JNT", "L_eye_upper10_tip_JNT", "L_eye_upper11_JNT", "L_eye_upper11_tip_JNT", "L_foot_A_twistBend_JNT", "L_foot_B_twistBend_JNT", "L_foot_C_twistBend_JNT", "L_foot_FK_JNT", "L_foot_IK_JNT", "L_foot_JNT", "L_foot_Mid_twist_JNT", "L_foot_bendA_JNT", "L_foot_bendE_JNT", "L_foot_lowTwist2_JNT", "L_front_cheekZero_JNT", "L_front_cheek_JNT", "L_hand_A_twistBend_JNT", "L_hand_B_twistBend_JNT", "L_hand_C_twistBend_JNT", "L_hand_FK_JNT", "L_hand_IK_JNT", "L_hand_JNT", "L_hand_Mid_twist_JNT", "L_hand_bendA_JNT", "L_hand_bendE_JNT", "L_hand_lowTwist2_JNT", "L_heel_JNT", "L_index1_JNT", "L_index2_JNT", "L_index3_JNT", "L_index4_JNT", "L_index5_JNT", "L_iris_JNT", "L_knee_A_twistBend_JNT", "L_knee_B_twistBend_JNT", "L_knee_C_twistBend_JNT", "L_knee_FK_JNT", "L_knee_IK_JNT", "L_knee_JNT", "L_knee_bendA_JNT", "L_knee_lowTwist1_JNT", "L_low_in_eyerimZero_JNT", "L_low_in_eyerim_JNT", "L_low_master_eyerimZero_JNT", "L_low_master_eyerim_JNT", "L_low_mid_eyerimZero_JNT", "L_low_mid_eyerim_JNT", "L_low_out_eyerimZero_JNT", "L_low_out_eyerim_JNT", "L_lowerInnerLip_JNT", "L_lowerLid_JNT", "L_lowerOuterLip_JNT", "L_lower_inner_teethZero_JNT", "L_lower_inner_teeth_JNT", "L_lower_outer_teethZero_JNT", "L_lower_outer_teeth_JNT", "L_middle1_JNT", "L_middle2_JNT", "L_middle3_JNT", "L_middle4_JNT", "L_middle5_JNT", "L_nostrilZero_JNT", "L_nostril_JNT", "L_pinky1_JNT", "L_pinky2_JNT", "L_pinky3_JNT", "L_pinky4_JNT", "L_pinky5_JNT", "L_pupil_JNT", "L_ring1_JNT", "L_ring2_JNT", "L_ring3_JNT", "L_ring4_JNT", "L_ring5_JNT", "L_shoulder_FK_JNT", "L_shoulder_IK_JNT", "L_shoulder_JNT", "L_shoulder_bendA_JNT", "L_shoulder_bendB_JNT", "L_shoulder_upTwist1_JNT", "L_shoulder_upTwist2_JNT", "L_thigh_FK_JNT", "L_thigh_IK_JNT", "L_thigh_JNT", "L_thigh_bendA_JNT", "L_thigh_bendB_JNT", "L_thigh_upTwist1_JNT", "L_thigh_upTwist2_JNT", "L_thumb1_JNT", "L_thumb2_JNT", "L_thumb3_JNT", "L_thumb4_JNT", "L_toe_FK_JNT", "L_toe_IK_JNT", "L_toe_JNT", "L_up_cheek_masterZero_JNT", "L_up_cheek_master_JNT", "L_up_in_cheekZero_JNT", "L_up_in_cheek_JNT", "L_up_in_eyerimZero_JNT", "L_up_in_eyerim_JNT", "L_up_master_eyerimZero_JNT", "L_up_master_eyerim_JNT", "L_up_mid_cheekZero_JNT", "L_up_mid_cheek_JNT", "L_up_mid_eyerimZero_JNT", "L_up_mid_eyerim_JNT", "L_up_out_cheekZero_JNT", "L_up_out_cheek_JNT", "L_up_out_eyerimZero_JNT", "L_up_out_eyerim_JNT", "L_upperInnerLip_JNT", "L_upperLidTip_JNT", "L_upperLid_JNT", "L_upperOuterLip_JNT", "L_upper_inner_teethZero_JNT", "L_upper_inner_teeth_JNT", "L_upper_outer_teethZero_JNT", "L_upper_outer_teeth_JNT", "M_brow_JNT", "M_chest_DRV_JNT", "M_chest_JNT", "M_chin_JNT", "M_head_DRV_JNT", "M_head_JNT", "M_head_top_JNT", "M_hips_DRV_JNT", "M_hips_JNT", "M_jaw_JNT", "M_low_SS_DRV_JNT", "M_lowerLip_JNT", "M_lower_teethZero_JNT", "M_lower_teeth_JNT", "M_lower_teeth_masterZero_JNT", "M_lower_teeth_master_JNT", "M_mid_SS_DRV_JNT", "M_muzzle_JNT", "M_neck1_DRV_JNT", "M_neck1_JNT", "M_neck2_JNT", "M_neck3_JNT", "M_neck4_IK_DRV_JNT", "M_neck4_JNT", "M_neck5_JNT", "M_neck6_JNT", "M_noseZero_JNT", "M_nose_JNT", "M_spine1_JNT", "M_spine2_JNT", "M_spine3_IK_DRV_JNT", "M_spine3_JNT", "M_spine4_IK_DRV_JNT", "M_spine4_JNT", "M_spine5_JNT", "M_tongue1_JNT", "M_tongue2_JNT", "M_tongue3_JNT", "M_tongue4_JNT", "M_tongue5_JNT", "M_tongue6_JNT", "M_tongue7_JNT", "M_up_SS_DRV_JNT", "M_upperLip_JNT", "M_upper_teethZero_JNT", "M_upper_teeth_JNT", "M_upper_teeth_masterZero_JNT", "M_upper_teeth_master_JNT", "R_LowerLidTip_JNT", "R_ball_FK_JNT", "R_ball_IK_JNT", "R_ball_JNT", "R_ball_inner_JNT", "R_ball_outer_JNT", "R_browInnerMid_JNT", "R_browInner_JNT", "R_browInner_arc_DRV_JNT", "R_browMiddle_JNT", "R_browMiddle_arc_DRV_JNT", "R_browOuterMid_JNT", "R_browOuter_JNT", "R_browOuter_arc_DRV_JNT", "R_cheekZero_JNT", "R_cheek_JNT", "R_clavicle_JNT", "R_cornerLip_JNT", "R_earZero_JNT", "R_ear_JNT", "R_elbow_A_twistBend_JNT", "R_elbow_B_twistBend_JNT", "R_elbow_C_twistBend_JNT", "R_elbow_FK_JNT", "R_elbow_IK_JNT", "R_elbow_JNT", "R_elbow_bendA_JNT", "R_elbow_lowTwist1_JNT", "R_eyeMaster_JNT", "R_eye_JNT", "R_eye_lower1_JNT", "R_eye_lower1_tip_JNT", "R_eye_lower2_JNT", "R_eye_lower2_tip_JNT", "R_eye_lower3_JNT", "R_eye_lower3_tip_JNT", "R_eye_lower4_JNT", "R_eye_lower4_tip_JNT", "R_eye_lower5_JNT", "R_eye_lower5_tip_JNT", "R_eye_lower6_JNT", "R_eye_lower6_tip_JNT", "R_eye_lower7_JNT", "R_eye_lower7_tip_JNT", "R_eye_lower8_JNT", "R_eye_lower8_tip_JNT", "R_eye_lower9_JNT", "R_eye_lower9_tip_JNT", "R_eye_lower10_JNT", "R_eye_lower10_tip_JNT", "R_eye_lower11_JNT", "R_eye_lower11_tip_JNT", "R_eye_upper1_JNT", "R_eye_upper1_tip_JNT", "R_eye_upper2_JNT", "R_eye_upper2_tip_JNT", "R_eye_upper3_JNT", "R_eye_upper3_tip_JNT", "R_eye_upper4_JNT", "R_eye_upper4_tip_JNT", "R_eye_upper5_JNT", "R_eye_upper5_tip_JNT", "R_eye_upper6_JNT", "R_eye_upper6_tip_JNT", "R_eye_upper7_JNT", "R_eye_upper7_tip_JNT", "R_eye_upper8_JNT", "R_eye_upper8_tip_JNT", "R_eye_upper9_JNT", "R_eye_upper9_tip_JNT", "R_eye_upper10_JNT", "R_eye_upper10_tip_JNT", "R_eye_upper11_JNT", "R_eye_upper11_tip_JNT", "R_foot_A_twistBend_JNT", "R_foot_B_twistBend_JNT", "R_foot_C_twistBend_JNT", "R_foot_FK_JNT", "R_foot_IK_JNT", "R_foot_JNT", "R_foot_Mid_twist_JNT", "R_foot_bendA_JNT", "R_foot_bendE_JNT", "R_foot_lowTwist2_JNT", "R_front_cheekZero_JNT", "R_front_cheek_JNT", "R_hand_A_twistBend_JNT", "R_hand_B_twistBend_JNT", "R_hand_C_twistBend_JNT", "R_hand_FK_JNT", "R_hand_IK_JNT", "R_hand_JNT", "R_hand_Mid_twist_JNT", "R_hand_bendA_JNT", "R_hand_bendE_JNT", "R_hand_lowTwist2_JNT", "R_heel_JNT", "R_index1_JNT", "R_index2_JNT", "R_index3_JNT", "R_index4_JNT", "R_index5_JNT", "R_iris_JNT", "R_knee_A_twistBend_JNT", "R_knee_B_twistBend_JNT", "R_knee_C_twistBend_JNT", "R_knee_FK_JNT", "R_knee_IK_JNT", "R_knee_JNT", "R_knee_bendA_JNT", "R_knee_lowTwist1_JNT", "R_low_in_eyerimZero_JNT", "R_low_in_eyerim_JNT", "R_low_master_eyerimZero_JNT", "R_low_master_eyerim_JNT", "R_low_mid_eyerimZero_JNT", "R_low_mid_eyerim_JNT", "R_low_out_eyerimZero_JNT", "R_low_out_eyerim_JNT", "R_lowerInnerLip_JNT", "R_lowerLid_JNT", "R_lowerOuterLip_JNT", "R_lower_inner_teethZero_JNT", "R_lower_inner_teeth_JNT", "R_lower_outer_teethZero_JNT", "R_lower_outer_teeth_JNT", "R_middle1_JNT", "R_middle2_JNT", "R_middle3_JNT", "R_middle4_JNT", "R_middle5_JNT", "R_nostrilZero_JNT", "R_nostril_JNT", "R_pinky1_JNT", "R_pinky2_JNT", "R_pinky3_JNT", "R_pinky4_JNT", "R_pinky5_JNT", "R_pupil_JNT", "R_ring1_JNT", "R_ring2_JNT", "R_ring3_JNT", "R_ring4_JNT", "R_ring5_JNT", "R_shoulder_FK_JNT", "R_shoulder_IK_JNT", "R_shoulder_JNT", "R_shoulder_bendA_JNT", "R_shoulder_bendB_JNT", "R_shoulder_upTwist1_JNT", "R_shoulder_upTwist2_JNT", "R_thigh_FK_JNT", "R_thigh_IK_JNT", "R_thigh_JNT", "R_thigh_bendA_JNT", "R_thigh_bendB_JNT", "R_thigh_upTwist1_JNT", "R_thigh_upTwist2_JNT", "R_thumb1_JNT", "R_thumb2_JNT", "R_thumb3_JNT", "R_thumb4_JNT", "R_toe_FK_JNT", "R_toe_IK_JNT", "R_toe_JNT", "R_up_cheek_masterZero_JNT", "R_up_cheek_master_JNT", "R_up_in_cheekZero_JNT", "R_up_in_cheek_JNT", "R_up_in_eyerimZero_JNT", "R_up_in_eyerim_JNT", "R_up_master_eyerimZero_JNT", "R_up_master_eyerim_JNT", "R_up_mid_cheekZero_JNT", "R_up_mid_cheek_JNT", "R_up_mid_eyerimZero_JNT", "R_up_mid_eyerim_JNT", "R_up_out_cheekZero_JNT", "R_up_out_cheek_JNT", "R_up_out_eyerimZero_JNT", "R_up_out_eyerim_JNT", "R_upperInnerLip_JNT", "R_upperLidTip_JNT", "R_upperLid_JNT", "R_upperOuterLip_JNT", "R_upper_inner_teethZero_JNT", "R_upper_inner_teeth_JNT", "R_upper_outer_teethZero_JNT", "R_upper_outer_teeth_JNT"};
        #bakeResults -t "1001:1250" -sampleBy 1 -oversamplingRate 1 -disableImplicitControl true -preserveOutsideKeys true -sparseAnimCurveBake false -removeBakedAttributeFromLayer false -removeBakedAnimFromLayer false -bakeOnOverrideLayer false -minimizeRotation true -controlPoints false -shape true {"L_LowerLidTip_JNT", "L_ball_FK_JNT", "L_ball_IK_JNT", "L_ball_JNT", "L_ball_inner_JNT", "L_ball_outer_JNT", "L_browInnerMid_JNT", "L_browInner_JNT", "L_browInner_arc_DRV_JNT", "L_browMiddle_JNT", "L_browMiddle_arc_DRV_JNT", "L_browOuterMid_JNT", "L_browOuter_JNT", "L_browOuter_arc_DRV_JNT", "L_cheekZero_JNT", "L_cheek_JNT", "L_clavicle_JNT", "L_cornerLip_JNT", "L_earZero_JNT", "L_ear_JNT", "L_elbow_A_twistBend_JNT", "L_elbow_B_twistBend_JNT", "L_elbow_C_twistBend_JNT", "L_elbow_FK_JNT", "L_elbow_IK_JNT", "L_elbow_JNT", "L_elbow_bendA_JNT", "L_elbow_lowTwist1_JNT", "L_eyeMaster_JNT", "L_eye_JNT", "L_eye_lower1_JNT", "L_eye_lower1_tip_JNT", "L_eye_lower2_JNT", "L_eye_lower2_tip_JNT", "L_eye_lower3_JNT", "L_eye_lower3_tip_JNT", "L_eye_lower4_JNT", "L_eye_lower4_tip_JNT", "L_eye_lower5_JNT", "L_eye_lower5_tip_JNT", "L_eye_lower6_JNT", "L_eye_lower6_tip_JNT", "L_eye_lower7_JNT", "L_eye_lower7_tip_JNT", "L_eye_lower8_JNT", "L_eye_lower8_tip_JNT", "L_eye_lower9_JNT", "L_eye_lower9_tip_JNT", "L_eye_lower10_JNT", "L_eye_lower10_tip_JNT", "L_eye_lower11_JNT", "L_eye_lower11_tip_JNT", "L_eye_upper1_JNT", "L_eye_upper1_tip_JNT", "L_eye_upper2_JNT", "L_eye_upper2_tip_JNT", "L_eye_upper3_JNT", "L_eye_upper3_tip_JNT", "L_eye_upper4_JNT", "L_eye_upper4_tip_JNT", "L_eye_upper5_JNT", "L_eye_upper5_tip_JNT", "L_eye_upper6_JNT", "L_eye_upper6_tip_JNT", "L_eye_upper7_JNT", "L_eye_upper7_tip_JNT", "L_eye_upper8_JNT", "L_eye_upper8_tip_JNT", "L_eye_upper9_JNT", "L_eye_upper9_tip_JNT", "L_eye_upper10_JNT", "L_eye_upper10_tip_JNT", "L_eye_upper11_JNT", "L_eye_upper11_tip_JNT", "L_foot_A_twistBend_JNT", "L_foot_B_twistBend_JNT", "L_foot_C_twistBend_JNT", "L_foot_FK_JNT", "L_foot_IK_JNT", "L_foot_JNT", "L_foot_Mid_twist_JNT", "L_foot_bendA_JNT", "L_foot_bendE_JNT", "L_foot_lowTwist2_JNT", "L_front_cheekZero_JNT", "L_front_cheek_JNT", "L_hand_A_twistBend_JNT", "L_hand_B_twistBend_JNT", "L_hand_C_twistBend_JNT", "L_hand_FK_JNT", "L_hand_IK_JNT", "L_hand_JNT", "L_hand_Mid_twist_JNT", "L_hand_bendA_JNT", "L_hand_bendE_JNT", "L_hand_lowTwist2_JNT", "L_heel_JNT", "L_index1_JNT", "L_index2_JNT", "L_index3_JNT", "L_index4_JNT", "L_index5_JNT", "L_iris_JNT", "L_knee_A_twistBend_JNT", "L_knee_B_twistBend_JNT", "L_knee_C_twistBend_JNT", "L_knee_FK_JNT", "L_knee_IK_JNT", "L_knee_JNT", "L_knee_bendA_JNT", "L_knee_lowTwist1_JNT", "L_low_in_eyerimZero_JNT", "L_low_in_eyerim_JNT", "L_low_master_eyerimZero_JNT", "L_low_master_eyerim_JNT", "L_low_mid_eyerimZero_JNT", "L_low_mid_eyerim_JNT", "L_low_out_eyerimZero_JNT", "L_low_out_eyerim_JNT", "L_lowerInnerLip_JNT", "L_lowerLid_JNT", "L_lowerOuterLip_JNT", "L_lower_inner_teethZero_JNT", "L_lower_inner_teeth_JNT", "L_lower_outer_teethZero_JNT", "L_lower_outer_teeth_JNT", "L_middle1_JNT", "L_middle2_JNT", "L_middle3_JNT", "L_middle4_JNT", "L_middle5_JNT", "L_nostrilZero_JNT", "L_nostril_JNT", "L_pinky1_JNT", "L_pinky2_JNT", "L_pinky3_JNT", "L_pinky4_JNT", "L_pinky5_JNT", "L_pupil_JNT", "L_ring1_JNT", "L_ring2_JNT", "L_ring3_JNT", "L_ring4_JNT", "L_ring5_JNT", "L_shoulder_FK_JNT", "L_shoulder_IK_JNT", "L_shoulder_JNT", "L_shoulder_bendA_JNT", "L_shoulder_bendB_JNT", "L_shoulder_upTwist1_JNT", "L_shoulder_upTwist2_JNT", "L_thigh_FK_JNT", "L_thigh_IK_JNT", "L_thigh_JNT", "L_thigh_bendA_JNT", "L_thigh_bendB_JNT", "L_thigh_upTwist1_JNT", "L_thigh_upTwist2_JNT", "L_thumb1_JNT", "L_thumb2_JNT", "L_thumb3_JNT", "L_thumb4_JNT", "L_toe_FK_JNT", "L_toe_IK_JNT", "L_toe_JNT", "L_up_cheek_masterZero_JNT", "L_up_cheek_master_JNT", "L_up_in_cheekZero_JNT", "L_up_in_cheek_JNT", "L_up_in_eyerimZero_JNT", "L_up_in_eyerim_JNT", "L_up_master_eyerimZero_JNT", "L_up_master_eyerim_JNT", "L_up_mid_cheekZero_JNT", "L_up_mid_cheek_JNT", "L_up_mid_eyerimZero_JNT", "L_up_mid_eyerim_JNT", "L_up_out_cheekZero_JNT", "L_up_out_cheek_JNT", "L_up_out_eyerimZero_JNT", "L_up_out_eyerim_JNT", "L_upperInnerLip_JNT", "L_upperLidTip_JNT", "L_upperLid_JNT", "L_upperOuterLip_JNT", "L_upper_inner_teethZero_JNT", "L_upper_inner_teeth_JNT", "L_upper_outer_teethZero_JNT", "L_upper_outer_teeth_JNT", "M_brow_JNT", "M_chest_DRV_JNT", "M_chest_JNT", "M_chin_JNT", "M_head_DRV_JNT", "M_head_JNT", "M_head_top_JNT", "M_hips_DRV_JNT", "M_hips_JNT", "M_jaw_JNT", "M_low_SS_DRV_JNT", "M_lowerLip_JNT", "M_lower_teethZero_JNT", "M_lower_teeth_JNT", "M_lower_teeth_masterZero_JNT", "M_lower_teeth_master_JNT", "M_mid_SS_DRV_JNT", "M_muzzle_JNT", "M_neck1_DRV_JNT", "M_neck1_JNT", "M_neck2_JNT", "M_neck3_JNT", "M_neck4_IK_DRV_JNT", "M_neck4_JNT", "M_neck5_JNT", "M_neck6_JNT", "M_noseZero_JNT", "M_nose_JNT", "M_spine1_JNT", "M_spine2_JNT", "M_spine3_IK_DRV_JNT", "M_spine3_JNT", "M_spine4_IK_DRV_JNT", "M_spine4_JNT", "M_spine5_JNT", "M_tongue1_JNT", "M_tongue2_JNT", "M_tongue3_JNT", "M_tongue4_JNT", "M_tongue5_JNT", "M_tongue6_JNT", "M_tongue7_JNT", "M_up_SS_DRV_JNT", "M_upperLip_JNT", "M_upper_teethZero_JNT", "M_upper_teeth_JNT", "M_upper_teeth_masterZero_JNT", "M_upper_teeth_master_JNT", "R_LowerLidTip_JNT", "R_ball_FK_JNT", "R_ball_IK_JNT", "R_ball_JNT", "R_ball_inner_JNT", "R_ball_outer_JNT", "R_browInnerMid_JNT", "R_browInner_JNT", "R_browInner_arc_DRV_JNT", "R_browMiddle_JNT", "R_browMiddle_arc_DRV_JNT", "R_browOuterMid_JNT", "R_browOuter_JNT", "R_browOuter_arc_DRV_JNT", "R_cheekZero_JNT", "R_cheek_JNT", "R_clavicle_JNT", "R_cornerLip_JNT", "R_earZero_JNT", "R_ear_JNT", "R_elbow_A_twistBend_JNT", "R_elbow_B_twistBend_JNT", "R_elbow_C_twistBend_JNT", "R_elbow_FK_JNT", "R_elbow_IK_JNT", "R_elbow_JNT", "R_elbow_bendA_JNT", "R_elbow_lowTwist1_JNT", "R_eyeMaster_JNT", "R_eye_JNT", "R_eye_lower1_JNT", "R_eye_lower1_tip_JNT", "R_eye_lower2_JNT", "R_eye_lower2_tip_JNT", "R_eye_lower3_JNT", "R_eye_lower3_tip_JNT", "R_eye_lower4_JNT", "R_eye_lower4_tip_JNT", "R_eye_lower5_JNT", "R_eye_lower5_tip_JNT", "R_eye_lower6_JNT", "R_eye_lower6_tip_JNT", "R_eye_lower7_JNT", "R_eye_lower7_tip_JNT", "R_eye_lower8_JNT", "R_eye_lower8_tip_JNT", "R_eye_lower9_JNT", "R_eye_lower9_tip_JNT", "R_eye_lower10_JNT", "R_eye_lower10_tip_JNT", "R_eye_lower11_JNT", "R_eye_lower11_tip_JNT", "R_eye_upper1_JNT", "R_eye_upper1_tip_JNT", "R_eye_upper2_JNT", "R_eye_upper2_tip_JNT", "R_eye_upper3_JNT", "R_eye_upper3_tip_JNT", "R_eye_upper4_JNT", "R_eye_upper4_tip_JNT", "R_eye_upper5_JNT", "R_eye_upper5_tip_JNT", "R_eye_upper6_JNT", "R_eye_upper6_tip_JNT", "R_eye_upper7_JNT", "R_eye_upper7_tip_JNT", "R_eye_upper8_JNT", "R_eye_upper8_tip_JNT", "R_eye_upper9_JNT", "R_eye_upper9_tip_JNT", "R_eye_upper10_JNT", "R_eye_upper10_tip_JNT", "R_eye_upper11_JNT", "R_eye_upper11_tip_JNT", "R_foot_A_twistBend_JNT", "R_foot_B_twistBend_JNT", "R_foot_C_twistBend_JNT", "R_foot_FK_JNT", "R_foot_IK_JNT", "R_foot_JNT", "R_foot_Mid_twist_JNT", "R_foot_bendA_JNT", "R_foot_bendE_JNT", "R_foot_lowTwist2_JNT", "R_front_cheekZero_JNT", "R_front_cheek_JNT", "R_hand_A_twistBend_JNT", "R_hand_B_twistBend_JNT", "R_hand_C_twistBend_JNT", "R_hand_FK_JNT", "R_hand_IK_JNT", "R_hand_JNT", "R_hand_Mid_twist_JNT", "R_hand_bendA_JNT", "R_hand_bendE_JNT", "R_hand_lowTwist2_JNT", "R_heel_JNT", "R_index1_JNT", "R_index2_JNT", "R_index3_JNT", "R_index4_JNT", "R_index5_JNT", "R_iris_JNT", "R_knee_A_twistBend_JNT", "R_knee_B_twistBend_JNT", "R_knee_C_twistBend_JNT", "R_knee_FK_JNT", "R_knee_IK_JNT", "R_knee_JNT", "R_knee_bendA_JNT", "R_knee_lowTwist1_JNT", "R_low_in_eyerimZero_JNT", "R_low_in_eyerim_JNT", "R_low_master_eyerimZero_JNT", "R_low_master_eyerim_JNT", "R_low_mid_eyerimZero_JNT", "R_low_mid_eyerim_JNT", "R_low_out_eyerimZero_JNT", "R_low_out_eyerim_JNT", "R_lowerInnerLip_JNT", "R_lowerLid_JNT", "R_lowerOuterLip_JNT", "R_lower_inner_teethZero_JNT", "R_lower_inner_teeth_JNT", "R_lower_outer_teethZero_JNT", "R_lower_outer_teeth_JNT", "R_middle1_JNT", "R_middle2_JNT", "R_middle3_JNT", "R_middle4_JNT", "R_middle5_JNT", "R_nostrilZero_JNT", "R_nostril_JNT", "R_pinky1_JNT", "R_pinky2_JNT", "R_pinky3_JNT", "R_pinky4_JNT", "R_pinky5_JNT", "R_pupil_JNT", "R_ring1_JNT", "R_ring2_JNT", "R_ring3_JNT", "R_ring4_JNT", "R_ring5_JNT", "R_shoulder_FK_JNT", "R_shoulder_IK_JNT", "R_shoulder_JNT", "R_shoulder_bendA_JNT", "R_shoulder_bendB_JNT", "R_shoulder_upTwist1_JNT", "R_shoulder_upTwist2_JNT", "R_thigh_FK_JNT", "R_thigh_IK_JNT", "R_thigh_JNT", "R_thigh_bendA_JNT", "R_thigh_bendB_JNT", "R_thigh_upTwist1_JNT", "R_thigh_upTwist2_JNT", "R_thumb1_JNT", "R_thumb2_JNT", "R_thumb3_JNT", "R_thumb4_JNT", "R_toe_FK_JNT", "R_toe_IK_JNT", "R_toe_JNT", "R_up_cheek_masterZero_JNT", "R_up_cheek_master_JNT", "R_up_in_cheekZero_JNT", "R_up_in_cheek_JNT", "R_up_in_eyerimZero_JNT", "R_up_in_eyerim_JNT", "R_up_master_eyerimZero_JNT", "R_up_master_eyerim_JNT", "R_up_mid_cheekZero_JNT", "R_up_mid_cheek_JNT", "R_up_mid_eyerimZero_JNT", "R_up_mid_eyerim_JNT", "R_up_out_cheekZero_JNT", "R_up_out_cheek_JNT", "R_up_out_eyerimZero_JNT", "R_up_out_eyerim_JNT", "R_upperInnerLip_JNT", "R_upperLidTip_JNT", "R_upperLid_JNT", "R_upperOuterLip_JNT", "R_upper_inner_teethZero_JNT", "R_upper_inner_teeth_JNT", "R_upper_outer_teethZero_JNT", "R_upper_outer_teeth_JNT"};

        pm.bakeResults(s, sampleBy=1, sm=False, sr=[False, 5], time=[start, end], oversamplingRate=1,
                       disableImplicitControl=1, preserveOutsideKeys=1, sparseAnimCurveBake=0,
                       removeBakedAttributeFromLayer=0, removeBakedAnimFromLayer=0, bakeOnOverrideLayer=0,
                       minimizeRotation=1, controlPoints=0, shape=1)

def create_locator_at_position():
    obj = pm.selected()
    for o in obj:
        loc = pm.spaceLocator(name="{}_locator".format(o))
        pm.delete(pm.parentConstraint(o, loc, mo=False))


def reorder_outliner():
    pm.select(ado=True)
    sel = pm.selected()
    sel.sort()
    print(sel)
    for s in sel:
        pm.reorder(s, b=True)
