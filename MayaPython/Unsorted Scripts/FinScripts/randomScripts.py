import os
import shutil
import maya_rig
from maya_animation import bake_locators
from maya_rig.builder.lib.space_switching import orientSpaceSwitch, createSpaceDefinition
from maya_rig.control_shapes.replace_shapes import combineShapes, replaceTargetChildShapes, liftControlShapes
import pymel.core
import pymel.core
import pprint as pp
import maya.cmds
import tempfile
import logging
from maya_rig.control_shapes import replace_shapes
from maya_rig.control_shapes import color_controls
import maya_rig.builder.templates.core as core
import maya_rig.builder.bindings as bindings
from maya_core.common.tags import tagNodeAsNonDeforming, isNodeDeforming
from maya_core.context_managers import nonIntermediateShapes
from maya_core.decorators import setCurrentFrame, unifyUndo
from maya_rig.builder import root_manager
from maya_rig.builder.build_common import (
    getAssetRigDataRoot,
    PREVIOUS_PARENT_ATTR,
    PREVIOUS_TRANSFORM_ATTR,
    GEO_BINDING_TAG_ATTR
)

from maya_rig.builder.lib.deformers import (
    getMeshAlembicFile,
    remapJointsInWeightsMap,
    applySkinWeightsMap,
    applyDeltaMushWeights,
    createWrap,
    getBaseFromWrapWithTransform,
    getSkinWeightsMap,
    getPrebindsFromTransforms,
    getDeltaMushWeights,
    getWrapTargetData,
    getDeformers)
from maya_rig.general import component_naming
from maya_rig.general.constraint_utils import (
    getConstraintsFromTransform,
    getConstraintTargets,
    getConstraintTargetsFromTransform,
)
from itertools import islice
import logging

logger = logging.getLogger(__name__)


def count():
    sel = pymel.core.selected()
    print(len(sel))


def buildFkFeathers():
    """
    Takes selected Twist jnts, parents constraint proxy jnts to them. Then connects the proxyJnts to the
    driven grp of FK ctrls.
    :return:
    """
    sel = pymel.core.selected() # select Twist jnts
    print (sel[0])
    print (sel[0].split("_"))
    num = 1

    for s in sel:
        split = s.split("_")
        ctrl = "00{}".format(num)
        pymel.core.setAttr('crestSpanBend_{}_{}_proxyJnt.rotateOrder'.format(split[1], ctrl), 3)  # sets to xzy
        pymel.core.parentConstraint('crestSpanTwist_{}_{}_jnt'.format(split[1], split[2]),
                            'crestSpanBend_{}_{}_proxyJnt'.format(split[1], ctrl), mo=False)

        # Connects Proxy rotations to drivenGrp
        pymel.core.connectAttr("crestSpanBend_{}_{}_proxyJnt.rotateX".format(split[1], ctrl),
                       "crestFeather{}_{}_drivenGrp.rotateX".format(split[1], ctrl))
        pymel.core.connectAttr("crestSpanBend_{}_{}_proxyJnt.rotateY".format(split[1], ctrl),
                       "crestFeather{}_{}_drivenGrp.rotateY".format(split[1], ctrl))
        pymel.core.connectAttr("crestSpanBend_{}_{}_proxyJnt.rotateZ".format(split[1], ctrl),
                       "crestFeather{}_{}_drivenGrp.rotateZ".format(split[1], ctrl))
        num += 1

        #if split[2] == '000':
        #    pymel.core.parent("crestSpanBend_{}_001_proxyJnt".format(split[1]), "crestFeather{}_interface".format(split[1]))


def connectAttributes(output=None, input=None, all=False):
    """
    Connects two attributes together
    :param output: output attr str
    :param input: input attr str
    :return:
    """
    sel = pymel.core.selected()

    print (sel)
    keyableOut = sel[0].listAttr(k=True)
    #keyableOut = pymel.core.getAttr('{}'.format(sel[0]), keyable=True)
    print (keyableOut)
    keyableIn = sel[1].listAttr(k=True)
    #pymel.core.connectAttr(output, input)
    if all:
        for kin, kout in zip(keyableIn,keyableOut):
            pymel.core.connectAttr(kout, kin)
            #pymel.core.connectAttr(output, "{0}.{1}".format(s, input))
    else:
        pymel.core.connectAttr(output, input)


def createAttr(name, loop, max, min):
    """
    Creates a series of attributes on a selected ctrl
    :param name: Attribute name
    :param loop: number of attributes to create
    :param max: maximum value
    :param min: minimum value
    :return:
    """
    sel= pymel.core.selected()[0]
    for x in range(0, loop):

        if x > 8:
            pymel.core.addAttr(sel, ln="{}0{}".format(name, x + 1), k=True, dv=0.0, max=max, min=min)
            #pymel.core.connectAttr("{}.{}0{}".format(sel,name, x + 1), "crestSpanRoot_0{}_grp.blendParam".format(x + 1))
        else:
            pymel.core.addAttr(sel, ln="{}00{}".format(name, x+1), k=True, dv=0.0, max=max, min=min)
            #pymel.core.connectAttr("{}.{}00{}".format(sel, name, x+1), "crestSpanRoot_00{}_grp.blendParam".format(x+1))


def cleanCombine():
    """Combines selected objects and renames them to the first object in selection"""
    sel = pymel.core.selected()  # gets selected objects
    name = sel[0].name()  # store object[0]'s name in variable
    combined = pymel.core.polyUnite(sel, cp=True, name=sel[0])  # combines objects
    combinedName = combined[0].name()  # store combined object's name in variable
    pymel.core.delete(combined, ch=True)  # delete construction history
    pymel.core.rename(combinedName, name)  # rename to original


def tempExport():
    """
    Saves a temp .ma file to your computers temp folder
    :return:
    """
    sel = pymel.core.selected()
    filePath = tempfile.gettempdir()
    pymel.core.cmds.file("{0}\exportTemp.mb".format(filePath), force=True, options='v=0', typ="mayaBinary", pr=True, es=True)


def tempImport():
    """Imports temp file from your temp folder"""
    filePath = tempfile.gettempdir()
    pymel.core.cmds.file("{0}\exportTemp.mb".format(filePath), i=True, typ="mayaBinary", options="v=0;", pr=True,
                 ra=True, ignoreVersion=True, mergeNamespacesOnClash=True, namespace="temp")


def parentInOrder(sel=None, selection=True):
    """
    Selecting Children first
    :return:
    """
    if sel is None:
        sel = []
    if selection:
        sel = pymel.core.selected()

    num = 1
    for s in sel:
        if s != sel[-1]:
            pymel.core.parent(sel[num], s)

        num += 1


def zeroCtrl():
    sel = pymel.core.selected()
    keyableAttr = [
        #"visibility",
        "translateX",
        "translateY",
        "translateZ",
        "rotateX",
        "rotateY",
        "rotateZ",
        "scaleX",
        "scaleY",
        "scaleZ",
    ]
    for s in sel:
        attr = s.listAttr(k=True)
        for a, b in zip(attr, keyableAttr):
            split = a.name().split('.')[-1]
            #pymel.core.cutKey(a)
            if split == b:
                if split == 'scaleX':
                    a.set(1)
                elif split == 'scaleY':
                    a.set(1)
                elif split == 'scaleZ':
                    a.set(1)
                elif split == 'visibility':
                    a.set(1)
                else:
                    a.set(0)


def clearKeyFrames():
    sel = pymel.core.selected()
    for s in sel:
        attr = s.listAttr(k=True)
        for a in attr:
            pymel.core.cutKey(a)


import maya.mel as mel
def cleanSeparate(cutOut=False):
    """
    Separates selected faces from mesh
    :param cutOut: Determines whether the faces should be cut out or duplicated out
    :return:
    """
    faces = pymel.core.selected()
    split = faces[0].split('.')
    shape = faces[0].node()
    transform = shape.getTransform() # gets transform for duplication
    dup = transform.duplicate(name='splitMesh')
    dupShape = dup[0].getShape()

    newFaces = "{0}.{1}".format(dupShape, split[1]) # Store faces for selection swap to duplicate mesh

    if cutOut:
        # Cut out face from original mesh, deletes oriinal face selection
        pymel.core.cmds.polyDelFacet(faces)

    # Duplicate face from original mesh
    pymel.core.select(newFaces) # Selects faces on duplicate object
    mel.eval("source invertSelection;") # Inverts selection using mel
    mel.eval("invertSelection;")
    pymel.core.cmds.polyDelFacet(pymel.core.selected())  # deletes selected faces
    pymel.core.delete(transform, dup, ch=True)


def reorderOutliner():
    pymel.core.select(ado=True)
    sel = pymel.core.selected()
    sel.sort()
    for s in sel:
        pymel.core.reorder(s, b=True)


def linkMultipleTemplatesToOne():
    """
    Links a selection of templates to the last selected template.
    """
    selection = pymel.core.ls(sl=1)
    for s in selection:
        if s != selection[-1]:
            first_template = core.getTemplateFromEventualParent(s)
            second_node = selection[-1]
            second_template = core.getTemplateFromEventualParent(second_node)
            parents = second_template.getParentPlugs()
            childs = first_template.getChildPlugs()
            if parents and childs:
                parent_target = parents[0]
                child_target = childs[0]
                if (len(parents) > 1) or (len(childs) > 1):
                    parent_target, child_target = core.plug_chooser.PlugChooserDialog.choosePlugs(
                        childs,
                        parents,
                    )
                else:
                    parent_target = parents[0]
                    child_target = childs[0]
                if parent_target and child_target:
                    parent_target.connect(child_target)


def scaleSelected(num, world):
    """Scales selected evenly by the value num"""
    sel = pymel.core.selected()[0]
    pymel.core.scale(sel, num, num, num, ws=world, r=not world)


def blackBox():
    """Toggles on and off blackbox mode"""

    if pymel.core.getAttr("*placement_ctl.blackBox"):
        pymel.core.setAttr("*placement_ctl.blackBox", False)
    else:
        pymel.core.setAttr("*placement_ctl.blackBox", True)


def parentBindManyToMultipleSelections(tag_non_deforming=True):
    """"""
    selection = pymel.core.ls(sl=1)


    createTransformBinding( selection, tag_non_deforming=tag_non_deforming)


def createTransformBinding(mesh_transforms, tag_non_deforming=True):
    """

    Args:
        rig_transform (str):
        mesh_transforms (list[str]):
        tag_non_deforming (bool):

    Returns:

    """
    current_parents = set()
    reparent_meshes = []
    binding_parent = None

    for mesh_transform in mesh_transforms:
        split = mesh_transform.split('_')
        meshStr = str(mesh_transform)
        rig_transform = "{}_{}_{}_jnt".format(split[0], split[1], split[2])

        geo_root = maya.cmds.listRelatives(meshStr, p=1, pa=1)[0]
        binding_parent = bindings.getBindingParentFor(rig_transform, geo_root)
        current_parent = maya.cmds.listRelatives(meshStr, p=1, pa=1)[0]

        if current_parent != binding_parent:
            current_parents.add(current_parent)
            reparent_meshes.append(meshStr)


        pymel.core.parent(meshStr, binding_parent)

    if reparent_meshes and binding_parent:
        bindings.storePreviousParentOnMeshes(reparent_meshes)
        #maya.cmds.parent(reparent_meshes, binding_parent)

        """Not sure why this is need so removed 
        for current_parent in current_parents:
            print "currentParent in current"
            if component_naming.isUtility(current_parent, "geoBind"):
                print "is Utility"
                children = maya.cmds.listRelatives(current_parent, ad=1, type="mesh")
                if not children:
                    print "not children"
                    maya.cmds.delete(current_parent)
        """
        if tag_non_deforming:
            for mesh_transform in mesh_transforms:
                meshStr = str(mesh_transform)
                tagNodeAsNonDeforming(meshStr)


def renameClientRigCtls():
    sel = pymel.core.selected()

    for s in sel:
        split = s.split("_")

        secondStr = split[0][0].lower() + split[0][1:]
        #print "{} renamed to ".format(s), "{}_{}_ctl".format(split[1], secondStr)


        s.rename("{}_{}_ctl".format(split[1], secondStr))


def addSuffix():
    sel = pymel.core.selected()

    for s in sel:
        s.rename("{}_geo".format(s))


def postBuild():
    pass



def lockAndHide(hide_attrs):
    sel = pymel.core.selected()[0]
    translateAttrs = ['translateX', 'translateY', 'translateZ']
    rotateAttrs = ['rotateX', 'rotateY', 'rotateZ']
    scaleAttrs = ['scaleX', 'scaleY', 'scaleZ']
    attrsToHide = []
    for hide in hide_attrs:
        if hide == 's':
            attrsToHide.append(scaleAttrs)
        elif hide == 't':
            attrsToHide.append(translateAttrs)
        elif hide == 'r':
            attrsToHide.append(rotateAttrs)
    #print attrsToHide

    attrs = pymel.core.listAttr(sel, k=True)

    for a in attrs:
        for hide in attrsToHide:
            for h in hide:
                if a == h:
                    pymel.core.setAttr("{}.{}".format(sel, a), lock=True, channelBox=False, k=False)


def createLocatorAtPosition():
    obj = pymel.core.selected()
    for o in obj:
        loc = pymel.core.spaceLocator(name="{}_locator".format(o))
        pymel.core.delete(pymel.core.parentConstraint(o, loc, mo=False))
        


def copySoldier():
    sel = pymel.core.selected()[0]

    obj = pymel.core.ls("soldier*")

    for o in obj:
        pymel.core.geometryConstraint(sel,o,w=1)
    return
    for o in obj:
        dup = pymel.core.duplicate(sel)
        pymel.core.delete(pymel.core.parentConstraint(o, dup, mo=False))
        pymel.core.parent(dup, o)


def mirrorAnim():
    #Required Fin components
    from maya_animation import mirror_anim
    controls = maya.cmds.ls("*ctl", type="transform")
    max = maya.cmds.playbackOptions(q=True, max=True)
    min = maya.cmds.playbackOptions(q=True, min=True)
    frame_range = range(int(min), int(max) + 1)

    for frame in frame_range:
        maya.cmds.currentTime(frame)
        mirror_anim.mirrorControls(controls, swap=True)


def crowdQC():
    sel = pymel.core.ls('redshiftProxy*')

    for s in sel:
        pymel.core.setAttr('{}.displayMode'.format(s), 1)
        pymel.core.setAttr('{}.displayPercent'.format(s), 50)


def nPrint(node):
    pp.pprint(node)


def getMaterial():
    sel = pymel.core.selected()[0]
    shape_node = pymel.core.listRelatives(sel, children=True)
    shader_grp = pymel.core.listConnections(shape_node, type='shadingEngine')
    shader = pymel.core.listConnections('{}.surfaceShader'.format(shader_grp[0]))


def tests():
    sel = pymel.core.selected()[0]
    parent_transform = pymel.core.listRelatives(sel, parent=1)


def createJointsOnPoints():

    selection = maya.cmds.ls(sl=1)
    vertex_ids = bake_locators.getVertexIDsFromSelection()
    #transform = bake_locators.getTransformFromSelection()
    component_type = "vtx"
    if not selection:
        raise Exception("Unable to find selected transform node")
    transform = selection[0].split('.')[0]
    if maya.cmds.listRelatives(selection, type="nurbsCurve", c=1):
        component_type = "cv"
    joints = [maya.cmds.joint() for x in vertex_ids]

    for joint, vertex_id in zip(joints, vertex_ids):
        component_string = "{0}.{1}[{2}]".format(
            transform,
            component_type,
            vertex_id
        )
        position = maya.cmds.xform(component_string, q=1, t=1, ws=1)
        # print component_string, frame_number, position
        #pos_x, pos_y, pos_z = position
        pymel.core.xform(joint, t=position, ws=1)
        pymel.core.parent(pymel.core.PyNode(joint), w=1)


    #maya.cmds.select(new_locators)

    #parentInOrder(joints)


def createJointFromSelection(cluster=False, worldParent = False):
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
            if not worldParent:
                pymel.core.parent(joints, s)
                parent_transform = joints.getParent()
                pymel.core.makeIdentity(parent_transform, apply=True, s=1, t=1, r=1, n=0, pn=1)
                pymel.core.parent(joints, s)
                if parent_transform.type() == "transform":
                    pymel.core.delete(parent_transform)



def copySkinWeight():
    '''
    Works only if the skinClusters are named the same
    '''
    sel = pymel.core.selected()

    for s in sel:
        destination = s.getShape().inputs()[0]
        source = pymel.core.PyNode("temp:{0}".format(destination))
        return
        pymel.core.copySkinWeights(ss=source, ds=destination, noMirror=True )


#from maya_animation.copy_anim import CopiedAnim
def copyAnim(fileName,namespace):
    sel = pymel.core.selected()
    orig_node = []
    for s in sel:
        orig_node.append(s.name())
    new_node = []

    for nodes in orig_node:
        tokens = component_naming.parseComponentNodeTokens(nodes)  # tokenise the name  (the "index" component will become a list of integers, regardless of padding)
        new_name = component_naming.createNameFromTokens(*tokens)  # rebuild the name (automatically using he latest padding amount)
        new_node.append("{0}{1}".format(namespace, new_name))

    transfer_filepath = "C:/Temp/{0}.pickle".format(fileName)
    anim = CopiedAnim.fromNodes(orig_node)
    anim.remapNodes(new_node)
    anim.toFile(transfer_filepath)


def pasteAnim(fileName):
    transfer_filepath = "C:/Temp/{0}.pickle".format(fileName)
    anim = CopiedAnim.fromFile(transfer_filepath)
    anim.toScene()



def printSelected():
    sel = pymel.core.ls(sl=1)
    for s in sel:
        print('"{}",'.format(s.name()))


from maya_rig.builder.bindings import RigBindings

def copySkinWeightsOver(geo_root):
    # Load original reallusion rig
    geo = pymel.core.ls(geo_root, type='transform')

    rb = RigBindings.fromScene(geo)
    # Load your built rig (where geo and joint names are hopefully all the same)


    rb.setApplySkinInWorldSpace(False)
    rb.toScene()


def matchTransformations():
    sel = pymel.core.selected()
    for s in sel:
        pymel.core.matchTransform(s,)


def importReallusionRig(filePath, rigFrame):
    pymel.core.importFile(filepath=filePath, defaultNamespace=0)

    pymel.core.currentTime(rigFrame)


def inputsTest():
    sel=pymel.core.selected()[0]

    constraint = sel.inputs()[0]

    print (constraint.inputs()[4])


def turnOffLocalAxis():

    sel = pymel.core.selected()

    for s in sel:
        s.displayLocalAxis.set(0)


def getWorldPosition():
    sel = pymel.core.selected()[0]

    pos = pymel.core.move(1, sel, moveZ=1, ws=1)
    print (pos)


def copyFiles(character):
    characterFolder = "Z:/3d_data/rigBuildData/INTERCEPTOR_4137/{0}".format(character)
    masterFolder = "Z:/3d_data/rigBuildData/INTERCEPTOR_4137/{0}/master/".format(character)
    controlShapesFolder = "Z:/3d_data/rigBuildData/INTERCEPTOR_4137/{0}/master/controlShapes/".format(character)
    shapesToCopy = "Z:/3d_data/rigBuildData/INTERCEPTOR_4137/JJprevis/master/controlShapes/"
    inbetweenLocation = "C:/Users/julian.beiboer/Documents/FIN"
    if not os.path.exists(characterFolder):

        os.mkdir(characterFolder)

    if not os.path.exists(masterFolder):
        masterFolder = os.mkdir(masterFolder)

    if not os.path.exists(controlShapesFolder):
        folder = os.mkdir(controlShapesFolder)

    print (shapesToCopy, masterFolder, inbetweenLocation)
    files = os.listdir(shapesToCopy)
    print (files)

    for f in files:
        shutil.copy(shapesToCopy + f, controlShapesFolder)


def printAllGeo():
    sel = pymel.core.ls(sl=1,type='transform', g=1)
    pp.pprint(sel)


def currentScene():
    scene = pymel.core.cmds.file(q=1, sceneName=1).split('/')[7]


def snapObjectsToGeo(deleteConstraint=True):
    """Select ground first then all cubes"""
    sel = pymel.core.selected()
    ground = sel[0]
    sel.pop(0)
    bottomPivot(sel)
    geoConstraint(sel, ground, deleteConstraint=True)


def geoConstraint(sel, ground, deleteConstraint=True):
    for s in sel:
        if deleteConstraint:
            pymel.core.delete(pymel.core.geometryConstraint(ground, s))
        else:
            pymel.core.geometryConstraint(ground, s)


def bottomPivot(sel):
    for s in sel:
        bbox = pymel.core.exactWorldBoundingBox(s)
        bottom = [(bbox[0] + bbox[3]) / 2, bbox[1], (bbox[2] + bbox[5]) / 2]
        pymel.core.xform(s, piv=bottom, ws=True)


def printFilePath():
    filepath = "J:/INTERCEPTOR_4137/_Globals/Characters/alexander/cache/rig/master/FBX/0026/alexander-master-master.fbx"
    project = pymel.core.cmds.file(q=1, sceneName=1).split('/')[1]
    split = filepath.split('/')
    swiss_type = split[2]
    swiss_category = split[3]
    swiss_item = split[4]
    swiss_activity = split[6]
    swiss_task = split[7]
    project_ID = int(project.split('_')[-1])
    print (project_ID, project, swiss_type, swiss_category, swiss_item, swiss_activity, swiss_task)


def shaderSwitch():
    shaderSwitchNums = {
        "L_boot_geoShape": 4,
        "L_glove_geoShape": 3,
        "R_boot_geoShape": 4,
        "R_glove_geoShape": 3,
        "belt_geoShape": 9,
        "buttons_geoShape": 7,
        "glassesFrame_geoShape": 0,
        "glassesLenses_geoShape": 0,
        "head_geoShape": 1,
        "jacket_lvl02_geoShape": 5,
        "liner_geoShape": 2,
        "pants_lvl01_geoShape": 6,
        "shell_geoShape": 2,
        "strap_geoShape": 2,
        "studs_geoShape": 2,
        "trim_geoShape": 2,
        "tshirt_geoShape": 10,
        "zips_geoShape": 8
    }
    for item, key in zip(shaderSwitchNums.keys(), shaderSwitchNums.values()):
        node = pymel.core.PyNode(item)

        node.addAttr("shaderSwitch", dv=key, k=1, at="long")


def moveToOrigin():
    sel = pymel.core.selected()
    for s in sel:
        pymel.core.xform(s, centerPivots=1)
        tr = pymel.core.xform(s, q=1, rp=1)
        pymel.core.xform(s, t=[-tr[0], -tr[1], -tr[2]])
        pymel.core.makeIdentity(s, apply=True, t=1, r=1, s=1, n=0, pn=1, )
        pymel.core.delete(ch=1)  # clears history


def saveBlendShapes():
    '''
    1. Get all blendshapes attached to the geo
    2. Create for loop which applies each blendshape then duplicates the mesh creates a new blend shape
    3.
    Returns:
    '''
    sel = pymel.core.ls(type="blendShape")
    pymel.core.currentTime(24)
    base_objects = []
    shape_files = []
    groups = []

    for s in sel:
        base_object = s.getGeometry()[0]
        base_objects.append(base_object)
        targets = s.getTarget()
        num_weights = s.numWeights()
        target_grp = pymel.core.group(empty=1, name="{0}_GRP".format(base_object))
        for target, index in zip(targets, range(num_weights)):
            s.setWeight(index, 1)
            dup_obj = pymel.core.PyNode(base_object).duplicate()[0]
            rename = dup_obj.rename("{0}_TGT".format(target))
            s.setWeight(index, 0)
            pymel.core.delete(dup_obj, ch=1)
            dup_obj.setParent(target_grp)

        #new_blendShape = pymel.core.blendShape(targets, base_object, frontOfChain=1, name="{0}_BSP".format(base_object))[0]
        export_path ="C:/Users/julian.beiboer/Documents/FIN/shapeTestExport/{0}".format("{0}_BSP".format(base_object))
        #pymel.core.blendShape(new_blendShape, e=1, export=export_path)

        #export_path = "{0}/{1}.mb".format(blend_shapes_folder, new_blend_shape)
        pymel.core.select(target_grp)
        pymel.core.cmds.file(export_path, exportSelected=1, f=1, type="mayaBinary")
        pymel.core.select(clear=1)
        groups.append(target_grp)
        shape_files.append(export_path)
        #pymel.core.delete(target_grp)
    return shape_files, base_objects, groups


def loadBlendShapes(shape_files, base_objects, groups):
    for shape_file, base_object, group in zip(shape_files, base_objects, groups):
        blendshape_name = shape_file.split('/')[-1]
        pymel.core.importFile("{0}.mb".format(shape_file))
        children = pymel.core.listRelatives(group, children=1)

        new_blend_shapes = pymel.core.blendShape(children, base_object, frontOfChain=1, name=blendshape_name)[0]


def loadBlends():
    sel = pymel.core.selected()
    base_object = sel[-1]
    sel.pop(-1)
    targets = sel
    new_blendShape = pymel.core.blendSwhape(targets, base_object, frontOfChain=1, name="{0}_BSP".format(base_object))[0]
    pass


def projectId():
    project_name = os.environ["PROJECT_DIRECTORY"]
    project_id = int(os.environ["PROJECT_DIRECTORY"].split("_")[-1])
    alt = pymel.core.cmds.file(q=1, sceneName=1).split('/')[1].split('_')[-1]
    return project_id


def replaceControlShapesByName():
    nodes = pymel.core.selected()
    for node in nodes:
        if "_LiftedShape" in node.name():
            shape_to_replace = node.nodeName().replace("_LiftedShape", "")  # starts with then recompile with
            replace_shapes.replaceTargetChildShapes(pymel.core.PyNode(shape_to_replace), [node])



def deleteAttrOnObj(attrToDel):
    sel = pymel.core.selected()

    for s in sel:
        shape = s.getShape()
        attr = pymel.core.listAttr(shape, ud=1)
        for a in attr:
            if a.startswith(attrToDel):
                pymel.core.deleteAttr("{0}.{1}".format(s, a))


def addNumberToTemplate():
    #sel = pymel.core.selected()
    sel = pymel.core.ls(sl=1, sn=1)

    for s in sel:
        obj = s.split("|")[-1]
        components = obj.split("_")
        if len(components) == 3:
            pymel.core.rename(s, "{0}1_{1}_{2}".format(components[0], components[1], components[2]))
        elif len(components) == 4:
            pymel.core.rename(s, "{0}1_{1}_{2}_{3}".format(components[0], components[1], components[2], components[3]))


def orientJointsSel(secondaryAxisOrient="zdown"):
    sel = pymel.core.selected()

    pymel.core.makeIdentity(sel, t=1, r=1, s=1, n=0, pn=1)
    for s in sel:
        #pymel.core.makeIdentity(s, t=1, r=1, s=1, n=0, pn=1)
        pymel.core.joint(s, e=1, orientJoint='xyz', secondaryAxisOrient=secondaryAxisOrient, zso=1)

        if s == sel[-1]:
            pymel.core.joint(s, e=1, orientJoint='none', zso=1)


def bindingsTransfer():
    import maya_rig.builder.bindings as bd
    FILEPATH = "Z:/3d_data/rigBuildData/LIBRARY_11/emma/master/bindings"
    bd.loadGeoBindingsOnSelection(FILEPATH)


def deleteNonEssentualAttr():
    sel = pymel.core.selected()
    for s in sel:
        attr = s.listAttr(k=1)
        other_attrs = ["visibility", "message"]
        scale_attrs = ["s", "sx", "sy", "sz"]
        rotate_attr = ["rx", "ry", "rz"]
        translate_attr = ["tx", "ty", "tz"]
        for attribute_name in attr:
            if not scale_attrs or other_attrs or rotate_attr or translate_attr:
                pymel.core.deleteAttr("{0}".format(attribute_name))


from maya_rig.builder.templates import core
def printModules():
    for template_module in core.TEMPLATE_MODULE_NAMES:
        module = core.importlib.import_module(".{0}".format(template_module), "maya_rig.builder.templates")

"""
from maya_rig.builder.bindings import RigBindings
from maya_rig.general import component_naming
rb = RigBindings.fromFileForCurrentScene()
joint_subs = {
"fishSplineIK_001_jnt": "fishFK_001_jnt",
"fishSplineIK_002_jnt": "fishFK_002_jnt",
"fishSplineIK_003_jnt": "fishFK_003_jnt",
"fishSplineIK_004_jnt": "fishFK_004_jnt",
"fishSplineIK_005_jnt": "fishFK_005_jnt",
"fishSplineIK_006_jnt": "fishFK_006_jnt",
"fishSplineIK_007_jnt": "fishFK_007_jnt",

}
rb.setJointSubstitutions(joint_subs)
rb.toScene()
"""
from maya_rig.builder.templates import core

def createFKtemplateOnSelected(name, template, sideId=""):
    sel = pymel.core.selected()
    num = 1
    for s in sel:
        core.createTemplate(template, side_id=sideId, no_prompt=1)
        if sideId:
            pymel.core.matchTransform("{0}_{1}_template".format(sideId, template), s)
            if num < 10:
                pymel.core.rename("{0}_{1}_template".format(sideId, template),
                                  "{0}_{1}_00{2}_template".format(sideId, name, num))
            elif num >= 10:
                pymel.core.rename("{0}_{1}_template".format(sideId, template),
                                  "{0}_{1}_0{2}_template".format(sideId, name, num))
        else:
            pymel.core.matchTransform("{1}_template".format(sideId, template), s)
            if num < 10:
                pymel.core.rename("{1}_template".format(sideId, template),
                                  "{1}_00{2}_template".format(sideId, name, num))
            elif num >= 10:
                pymel.core.rename("{1}_template".format(sideId, template),
                                  "{1}_0{2}_template".format(sideId, name, num))
        num += 1

import maya_rig.builder.lib.deformers as lib
def shiftSkinWeightsToTemplatePivots():

    selected = pymel.core.selected()
    for side in "L", "R":
        short_feather_front = maya.cmds.ls("{0}_shortFeatherFront_*_proxyGeo".format(side), type="transform")
        short_feather_back = maya.cmds.ls("{0}_shortFeatherBack_*_proxyGeo".format(side), type="transform")
        print (short_feather_back, short_feather_front)

        for geo in short_feather_front:
            split = geo.split("_")
            joint = "{0}_{1}_{2}_jnt".format(split[0], split[1], split[2])
            print (geo, joint)
            bindings.createTransformBinding(
                                            joint,
                                            [geo],
                                            tag_non_deforming=True
                                            )
    print (short_feather_back, short_feather_front)



    return
    """L_feather_007_geo"""
    name = "L_feather001_001_jnt"
    fkJoints = maya.cmds.ls("{0}_{1}_*jnt".format(counter[0], counter[1]), type="joint")
    bendJoints = maya.cmds.ls("{0}_{1}_*templateJoint".format(counter[0], counter[1]), type="joint")
    kwargs = {
        "skinMethod": 0,
        "toSelectedBones": True,
    }

    args = [geo] + fkJoints

    # Bind geo to skin
    skin = maya.cmds.skinCluster(*args, **kwargs)
    # selects newly created skin and re assigns it to skin so that is is an object instead of unicode
    pymel.core.select(skin, replace=True)
    skin = pymel.core.selected()[0]

    lib.skinFullyToClosest(skin, dict(zip(fkJoints, bendJoints)))


def matchPosFromName():
    name = "L_feather_001Root_ctl_LiftedShape"

    sel = pymel.core.selected()

    for s in sel:
        split = s.split("_")
        pymel.core.matchTransform(s, "{0}_{1}_{2}_{3}".format(split[0], split[1], split[2], split[3]))


def connectAttrThing():
    for side in "L", "R":
        for num in range(1, 16):
            if num < 10:
                pymel.core.setAttr("{0}_feather00{1}_001_jnt.inheritsTransform".format(side, num), 0)
            elif num >= 10:
                pymel.core.setAttr("{0}_feather0{1}_001_jnt.inheritsTransform".format(side, num), 0)

def rigidBindGeo():
    sel = pymel.core.selected()
    for s in sel:
        split = s.split("_")
        jnt = "{0}_{1}_{2}_jnt".format(split[0], split[1], split[2])
        pymel.core.select(jnt, r=1)
        pymel.core.bindSkin(s, jnt, tsb=1)
        #bindings.createTransformBinding(jnt, [pymel.core.PyNode(s)])

def fkTorsoTest():
    for num in range(1, 6):
        fk_grp = pymel.core.PyNode("fkChain_00{0}_drivenGrp".format(num))
        """if num == 5:
            torso_joint = pymel.core.PyNode("torsoEndTip_jnt")
            aim_constraint = pymel.core.aimConstraint(
                torso_joint,
                fk_grp,
                upVector=(0, 1, 0),
                worldUpType="vector", mo=1
            )
        else:"""
        torso_joint = pymel.core.PyNode("torsoIkResult_00{0}_jnt".format(num))
        torso_joint.r.connect(fk_grp.r)
    pass

def deleteXgen():
    import pymel.core
    import pprint
    pprint.pprint(pymel.core.listAttr("generate_xgen_geoShape"))
    name = "generate_xgen_geoShape.xgen_Pref"
    pymel.core.deleteAttr(name)

def addInfluenceWrap():
    name = "generate_xgen_geo"
    sel = pymel.core.selected()
    #for s in sel:

def connectPorximityWrapBaseGeo():
    sel = pymel.core.selected()
    num = 0
    for s in sel:
        shape = s.getShape()
        name = "generate_xgen_geo"
        pymel.core.connectAttr("{0}.worldMesh[0]".format(shape),
                               "proximityWrap1.drivers[{0}].driverBindGeometry".format(num), force=1)
        num += 1
        # Connected L_feather_001_smoothProxyBaseShape.worldMesh to proximityWrap1.drivers.driverBindGeometry.

def createAttrsOnGeo():
    sel = pymel.core.selected()
    pymel.core.addAttr(sel, longName="mouth", enumName="open:closed", at='enum', dv=0, k=1)
    pymel.core.addAttr(sel, longName="eyes", enumName="open:closed", at='enum', dv=0, k=1)
    pymel.core.addAttr(sel, longName="L_eye_pupilU", at='float', dv=0, k=1)
    pymel.core.addAttr(sel, longName="L_eye_pupilV", at='float', dv=0, k=1)
    pymel.core.addAttr(sel, longName="R_eye_pupilU", at='float', dv=0, k=1)
    pymel.core.addAttr(sel, longName="R_eye_pupilV", at='float', dv=0, k=1)


def addPrebindJoints():
    skin_joint = ["C_lowerLip_001_jnt" ,
                    "R_lowerLip_002_jnt" ,
                    "R_lowerLip_001_jnt" ,
                    "L_lowerLip_002_jnt" ,
                    "L_lowerLip_001_jnt" ,
                    "C_upperLip_001_jnt" ,
                    "L_upperLip_002_jnt" ,
                    "L_upperLip_001_jnt" ,
                    "R_upperLip_002_jnt" ,
                    "R_upperLip_001_jnt",]

    prebind_joint = ["C_lowerLip_001_prebindJnt" ,
                    "R_lowerLip_002_prebindJnt" ,
                    "R_lowerLip_001_prebindJnt" ,
                    "L_lowerLip_002_prebindJnt" ,
                    "L_lowerLip_001_prebindJnt" ,
                    "C_upperLip_001_prebindJnt" ,
                    "L_upperLip_002_prebindJnt" ,
                    "L_upperLip_001_prebindJnt" ,
                    "R_upperLip_002_prebindJnt" ,
                    "R_upperLip_001_prebindJnt",]

    maya_rig.builder.lib.skinning.addPrebindJointsToSkin(skin_joint, prebind_joint)


def relativeRotate(x,y,z):
    sel = pymel.core.selected()
    for s in sel:
        pymel.core.rotate(s, (x, y, x), r=1)


def getSpaceNameFor(space, control_node):
    # part_name, indices, utility = component_naming.parseTokens(control_node.name())
    # new_part_name = "{0}{1}".format(part_name, space.capitalize())
    # new_name = component_naming.nameFromTokens(
    #     new_part_name,
    #     indices,
    #     "spaceReference"
    # )
    new_name = control_node.name() + "{0}_{1}".format(space.capitalize(), "spaceReference")
    return new_name


def removeRigidBindOnSelected():
    sel = pymel.core.selected()

    for s in sel:
        selected_object = pymel.core.PyNode(s)
        if pymel.core.attributeQuery("previousTransformValues", node=s, exists=1):
            previous_parent = pymel.core.getAttr("{0}.previousMeshParent".format(s))

            pymel.core.setAttr("{0}.previousTransformValues".format(s), lock=0)
            pymel.core.deleteAttr("{0}.previousTransformValues".format(s))
            pymel.core.deleteAttr("{0}.previousMeshParent".format(s))
            pymel.core.parent(s, previous_parent)


from maya_rig.builder.bindings import RigBindings
from maya_rig.general import component_naming
def replaceSingleJointHierarchy():
    rb = RigBindings.fromFileForCurrentScene()
    joints = pymel.core.ls("*_outputJnt", type='joint')
    new_joints = []
    for joint in joints:
        new_j = str(joint.name().replace('_outputJnt', '_jnt'))
        new_joints.append(new_j)
    joint_subs = { }

    for joint, new_joint in zip(joints, new_joints):
        if 'torso' in str(joint):
            if '001' in str(joint):
                joint_subs[str(joint)] = 'torsoBase_jnt'
            if '002' in str(joint):
                joint_subs[str(joint)] = 'torsoIkResult_001_jnt'
            if '003' in str(joint):
                joint_subs[str(joint)] = 'torsoIkResult_002_jnt'
            if '004' in str(joint):
                joint_subs[str(joint)] = 'torsoIkResult_003_jnt'
            if '005' in str(joint):
                joint_subs[str(joint)] = 'torsoIkResult_004_jnt'
            if '006' in str(joint):
                joint_subs[str(joint)] = 'torsoEnd_jnt'
        else:
            joint_subs[str(joint)] = new_joint
    rb.setJointSubstitutions(joint_subs)
    rb.toScene()


def orientJointWithAimConstraint(aim_vector=(-1, 0, 0), up_vector=(0, 1, 0)):
    sel = pymel.core.selected()
    target_joint = sel[-1]
    aim_joints = sel[:-1]
    for joint in aim_joints:
        aim_constraint = pymel.core.aimConstraint(
            target_joint,
            joint,
            aimVector=aim_vector,
            upVector=up_vector,
            worldUpVector=(0, 1, 0),
            worldUpType="vector",
        )
        pymel.core.delete(aim_constraint)



def duplicateShapeNode():
    selection = pymel.core.ls(sl=1)
    name = str(selection[0].name())
    lifted_shape = liftControlShapes(selection)[0]
    dup = pymel.core.duplicate(lifted_shape)[0]
    dup.getShape().rename(name+"IntermediateShape")

    combined_shape = combineShapes([lifted_shape.getShape(), dup.getShape()])
    pymel.core.delete(lifted_shape, dup)
    target_transform = selection[0]
    source_transforms = combined_shape
    replaceTargetChildShapes(target_transform, [source_transforms])

def deleteAllExtraAttrs():
    selected = pymel.core.selected()

    for s in selected:
        attr = pymel.core.listAttr(s, userDefined=1)
        for a in attr:
            try:
                pymel.core.deleteAttr(s, at=a)
            except:
                continue

def massParentConstraint():
    number = "00"
    for num in range(1, 41):
        if num < 10:
            number ='00{}'.format(num)
        elif num >= 10:
            number ='0{}'.format(num)

        try:
            print(number)
            pymel.core.parentConstraint('spin1:frenchfry:chip_{}_ctl'.format(number),
                                        'frenchfry1:chip_{}_ctl'.format(number), mo=0)
            pymel.core.scaleConstraint('spin1:frenchfry:chip_{}_ctl'.format(number),
                                        'frenchfry1:chip_{}_ctl'.format(number), mo=0)

        except:
            continue


def createSetDrivenKeys():
    driver = "doorMainOffset_ctl"
    driven_nodes = ["doorHinge_ctl", "doorMain_ctl"]

    if not pymel.core.attributeQuery("door", node="{0}".format(driver), ex=1):
        doorAttr = pymel.core.PyNode(driver).addAttr("door", k=1, max=10, min=0, dv=0)
    doorMain = [-5.555, -3.445, -19.210, 0, 0, 2.974]
    hingeMain = [0, 0, 0, -180, 0, 0]
    # set door value to 0
    # set driven key controls
    #set door value to 10,
    for node, values in zip(driven_nodes, [hingeMain, doorMain,]):
        attrs = pymel.core.listAttr(node, k=1)
        attrs = attrs[1:-3]
        print (attrs)
        for attr in attrs:
            pymel.core.setDrivenKeyframe("{0}.{1}".format(node, attr), cd="{0}.door".format(driver), dv=0, v=0)

        for attr, value in zip(attrs, values):
            pymel.core.setDrivenKeyframe("{0}.{1}".format(node, attr), cd="{0}.door".format(driver), dv=10, v=value)


    """maya.cmds.setDrivenKeyframe(
        attribute,
        cd=driver,
        dv=key_time,
        v=value,
    )"""


def addGeoSuffix(suffix="geo"):
    sel = pymel.core.selected()
    for s in sel:
        name = s.nodeName()
        new_name = name+("_{0}".format(suffix))
        s.setName(new_name)