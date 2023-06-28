"""
m_deformers
Tools relating to the deformers. Eg: skinclusters, clusters, blendshapes, ffds, etc
Auther: Julian Beiboer
"""
import pymel.core
import os
import logging
logging.basicConfig()
logger = logging.getLogger('m_deformers')
logger.setLevel(logging.DEBUG)

def export_skin_weights(character_name, base_path="/home/julianbeiboer/Documents/"):
    sel = pymel.core.selected()
    for s in sel:
        save_dir = "{}/{}".format(base_path, character_name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        deformers = pymel.core.listHistory(s, type='skinCluster')
        for deformer in deformers:
            export_name = "{}_{}.xml".format(s.name(), deformer)
            pymel.core.deformerWeights(export_name, export=True, deformer=deformer, format="XML", path=save_dir)


def import_skin_weights(character_name, base_path="/home/julianbeiboer/Documents/"):
    skin_weights = os.listdir("{}/{}".format(base_path, character_name))

    for weights in skin_weights:

        pass
    #get file name,
    #extract object name
    #create skin bind
    #import skin weights

    pass
