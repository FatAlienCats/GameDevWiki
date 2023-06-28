import pymel.core as pm
import pprint as pp

def main():
    selected = pm.selected()

    for s in selected:
        mirrorFeather = duplicateFeathers(s)
        featherGrp = createLocators(s)

        pm.xform(featherGrp, s=[-1, 1, 1])
        # move and constrain mirrored feather to new locator position
        pm.delete(pm.parentConstraint('featherLocator01', mirrorFeather, mo=False))
        pm.delete(pm.aimConstraint('featherLocator03', mirrorFeather, mo=False, aim=[0, 0, 1], u=[-1, 0, 0],
                                   wuo='featherLocator02',
                                   wut="object"))

        pm.delete(featherGrp)




def createLocators(sel):
    """
    Creates three locators and moves them to feather locations
    :return:

    """
    featherGrp = pm.group(n="locator_grp", em=True)
    for x in range(0, 3):
        locator1 = pm.spaceLocator(n='featherLocator01')
        pm.parent(locator1, sel)

        if x == 1:
            pm.xform(locator1, t=[1, 0, 0], ro=[0, 0, 0], s=[1, 1, 1])
        elif x == 2:
            pm.xform(locator1, t=[0, 0, 1], ro=[0, 0, 0], s=[1, 1, 1])
        else:
            pm.xform(locator1, t=[0, 0, 0], ro=[0, 0, 0], s=[1, 1, 1])
        pm.parent(locator1, w=True)
        pm.parent(locator1, featherGrp)


    return featherGrp

def duplicateFeathers(sel):
    """
    Duplicates feathers and renames it to be the opposite side
    :return:
    """
    mirrorName = "R_"
    duplicate = pm.duplicate(sel, n="{}{}".format(mirrorName, sel))
    pm.rename(sel, "L_{}".format(sel))
    return duplicate

