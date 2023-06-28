import pymel.core as pm
import re


def save_shape():
    # Save shape to disk so that it can be reused
    pass


def load_shape():
    # Load shape from disk to selected control
    pass


def mirror_shapes():
    selected = pm.selected()
    extracted_shapes = extract_shapes(selected)

    group = pm.group(em=True, name="mirror_GRP_TEMP")
    pm.parent(extracted_shapes, group)
    pm.setAttr("{}.sx".format(group), -1)
    for shape in extracted_shapes:
        split = shape.name().split("_")
        if split[0] == "L":

            new_name = re.sub(r'\bL_', 'R_', shape.name())
            shape.rename(new_name)
            # color
            shape_node = pm.listRelatives(shape, shapes=True)
            color_of_mirror = pm.listRelatives(new_name.replace("_COPY", ""), shapes=True)[0]
            for s in shape_node:
                color = pm.getAttr("{}.overrideColor".format(color_of_mirror))
                pm.setAttr("{}.overrideColor".format(s), color)
        elif split[0] == "R":
            new_name = re.sub(r'\bR_', 'L_', shape.name())
            shape.rename(new_name)
            # color
            shape_node = pm.listRelatives(shape, shapes=True)
            color_of_mirror = pm.listRelatives(new_name.replace("_COPY", ""), shapes=True)[0]
            for s in shape_node:
                color = pm.getAttr("{}.overrideColor".format(color_of_mirror))
                pm.setAttr("{}.overrideColor".format(s), color)

    copy_shapes_back_to_original(extracted_shapes)
    pm.delete(group)


def extract_shape_from_selected():
    sel = pm.selected()
    extract_shapes(sel)


def copy_selected_back_to_original():
    selected = pm.selected()
    for s in selected:
        copy_shapes(s, pm.PyNode(s.replace("_COPY", "")))

def extract_shapes(selected):
    extracted_shapes = []
    for s in selected:
        dup = pm.duplicate(s, name="{}_COPY".format(s), ilf=False)[0]
        shapes = pm.listRelatives(dup, shapes=True)
        child_transforms = pm.listRelatives(dup, children=True, type='transform')
        pm.delete(child_transforms)
        for shape in shapes:
            pm.rename(shape, "{}_COPY".format(shape))
        pm.parent(dup, w=1)
        extracted_shapes.append(dup)

    return extracted_shapes


def copy_shapes_back_to_original(selected):
    for s in selected:
        copy_shapes(s, pm.PyNode(s.replace("_COPY", "")))


def copy_shape_to_selected():
    sel = pm.selected()
    copy_shapes(sel[0], sel[-1])


def copy_shapes(source_obj, target_obj):
    parent = pm.listRelatives(target_obj, parent=True)
    pm.parent(source_obj, parent)
    pm.makeIdentity(source_obj, apply=True, t=1, r=1, s=1, n=0, pn=1)  # is this needed?

    rotation_pivot = pm.xform(target_obj, q=1, rp=1, ws=1)
    if pm.listRelatives(source_obj, shapes=True):
        source_shapes = pm.listRelatives(source_obj, shapes=True)
    else:
        children = pm.listRelatives(source_obj, type="transform")
        source_shapes = []
        for child in children:
            source_shapes.append(pm.listRelatives(child, shapes=True)[0])
    # Get the old shape from the target object
    target_shapes = pm.listRelatives(target_obj, shapes=True)
    # Parent the new shape to the target object
    pm.parent(source_shapes, target_obj, shape=True, relative=True, add=True)
    # Delete the old shape and source transform
    pm.delete(target_shapes, source_obj)
    # Rename new shape
    for s, t in zip(source_shapes, target_shapes):
        s.rename(t.name())

    pm.xform(target_obj, piv=rotation_pivot, ws=True)
