from Helpers.skin import Skin
import Helpers.api as api
import pymel.core as pm
import maya.cmds as cmds
import tempfile


class SimpleSkinUndo(object):
    control_name = None
    skin = None
    soft_mod = None
    skin_cluster = None
    skin_dict = None
    file_path = "/home/julianbeiboer/Documents/softMod/testskin.json"

    def __init__(self, control_name, skin_cluster):
        super(SimpleSkinUndo, self).__init__()
        self.redo_text = ''
        self.undo_text = ''
        self.control_name = control_name
        self.skin_cluster = skin_cluster
        # run the command that will call the doIt, redoIt, undoIt functions at the appropriate times
        cmds.runUndoablePython(self)

    def doIt(self):
        # gather / store data to use during redo / undo, eg doIt is only called once, then redo/undo happen while
        # moving backwards/forward the undo stack... optionally you can do this work in your __init__ before
        # you call the cmd.runUndoablePython
        print('Preparing World!')
        self.redo_text = 'Hello World!'
        self.undo_text = 'Goodbye World!'
        #selection = pm.selected()
        self.skin = Skin(node=self.skin_cluster)
        print(self.skin)
        self.save_skin_to_temp()
        # Getting just the name of the object as the Helper scripts don't work with pymel objects.
        #soft_mod = pm.listConnections(selection[0], d=True)[0].name()
        #skin_cluster = get_skin_cluster(selection[0]).name()

        #build_custom_control(new_joint_name, self.control_name)


    def redoIt(self):
        # apply your changes here, usually something like MPlug.setValue, MFkSkinCluster.setWeights, etc
        print("redoit")
        print(self.skin)
        #skin = Skin().from_dict(self.skin_dict)
        new_joint = self.skin.add_cluster_from_soft_selection("{}_JNT".format(self.control_name))
        pass

    def undoIt(self):
        self.skin = Skin(node="skinCluster5").read(self.file_path)
        print(self.undo_text)

    def save_skin_to_temp(self):
        self.skin.save(self.file_path)


def get_skin_cluster(geo):
    """
    Gets skin cluster attached to
    Args:
        geo(pynode): node to get skin cluster off

    Returns:

    """
    deformer = pm.listHistory(geo, type='skinCluster')[0]
    return deformer



