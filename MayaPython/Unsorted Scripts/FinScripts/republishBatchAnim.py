import copy
import itertools

import databe
import maya.cmds

from fin_asset.export.exporter import genericExport
from fin_job.anim_scene import createBlasterFireForNamespace
from maya_core.common import namespace_utils as nsu
from maya_core.common.file import saveMayaSceneIncremented

JOB_ID = 4125
DEFAULT_ASSET_TYPES = ["MayaScene"]

def main(filter_list=None):
    import maya.standalone
    maya.standalone.initialize()
    anim_scene_assets = getAllAnimScenes()
    if filter_list:
        anim_scene_assets = [x for x in anim_scene_assets if x.logical_path["item"] in filter_list]
        anim_scene_assets.sort(key=lambda x: filter_list.index(x.logical_path["item"]))

    drones = {}
    latest_drone_rig_asset = getLatestDroneRig()
    latest_hornet_rig_asset = getLatestFA18HornetRig()
    latest_hybrid_rig_asset = getLatestHybridRig()

    for anim_scene in anim_scene_assets:

        maya.cmds.file(anim_scene.system_path, o=1, f=1, pmt=0, ignoreVersion=True)
        '''
        drones_roots = maya.cmds.ls("drone*:placement_ctl")
        namespace_refs = nsu.getSelectedReferences(selection=drones_roots)
        for ns, ref in namespace_refs.items():
            rn = maya.cmds.referenceQuery(ref, rfn=1)
            maya.cmds.file(latest_drone_rig_asset.system_path, loadReference=rn)


        hornet_roots = maya.cmds.ls("FA18Hornet*:placement_ctl")
        namespace_refs = nsu.getSelectedReferences(selection=hornet_roots)
        for ns, ref in namespace_refs.items():
            rn = maya.cmds.referenceQuery(ref, rfn=1)
            maya.cmds.file(latest_hornet_rig_asset.system_path, loadReference=rn)
        '''

        maya.cmds.showHidden(all=True)
        hybrid_roots = maya.cmds.ls("jetHybrid*:placement_ctl")
        namespace_refs = nsu.getSelectedReferences(selection=hybrid_roots)
        for ns, ref in namespace_refs.items():
            rn = maya.cmds.referenceQuery(ref, rfn=1)
            maya.cmds.file(latest_hybrid_rig_asset.system_path, loadReference=rn)

        working_file_basis = maya.cmds.file(q=1, sn=1)
        save_message = 'Republish latest jetHybrid (texture fix)'
        major_minor = "MINOR"
        saveMayaSceneIncremented(working_file_basis, major_minor, save_message)

        # duplicate above with hornet
        # make getLatestHornetRig function
        maya.cmds.select(hybrid_roots)
        # maya.cmds.select(hybrid_roots, drones_roots, hornet_roots)
        # select hornet roots
        genericExport(
            "animation",
            extra_data_dict={"skip_notification": True}
        )


def republishShotsWithLatest(latest_rig_assets, anim_scene_assets):

    for anim_scene in anim_scene_assets:

        maya.cmds.file(anim_scene.system_path, o=1, f=1, pmt=0, ignoreVersion=True)
        drones_roots = maya.cmds.ls("drone*:placement_ctl")
        namespace_refs = nsu.getSelectedReferences(selection=drones_roots)
        for ns, ref in namespace_refs.items():
            rn = maya.cmds.referenceQuery(ref, rfn=1)
            maya.cmds.file(latest_rig_assets.system_path, loadReference=rn)



def getAllAnimScenes(sequence="126"):
    maya_scene_assets = retrieveCategoryAssets(JOB_ID, sequence, "Shots")
    latest_maya_scenes = filterNonLatestAssets(maya_scene_assets)
    anim_maya_scenes = filterAnimOnly(latest_maya_scenes)
    return anim_maya_scenes

def retrieveCategoryAssets(
        job_id,
        category,
        fin_type,
        asset_types=None,
        hours=None,
):
    """

    Args:
        job_id (int):
        category (str):
        fin_type (str):
        asset_types (list[str]):

    Returns:
        list[OrderedDict]
    """
    kwargs = {}
    if hours:
        kwargs["hours"] = hours
    all_assets = databe.asset.getByCategory(
        job_id,
        fin_type,
        category,
        **kwargs
    )
    if not asset_types:
        asset_types = DEFAULT_ASSET_TYPES
    all_assets = [x for x in all_assets if x.type in asset_types]
    return all_assets


def filterAnimOnly(asset_list):
    out_list = []
    for asset in asset_list:
        lp = asset.logical_path

        if lp["activity"] ==  "anim" and lp["task"] == "animation":
            out_list.append(asset)
    return out_list


def filterNonLatestAssets(asset_list):
    """
    Removes assets which are older versions of another asset in the list.

    Args:
        asset_list (list [OrderedDict]):

    Returns:
        list [OrderedDict]: Filtered list of assets.
    """
    out_asset_list = []
    def access_key(asset):
        logical_path = copy.copy(asset.logical_path)
        if "version" in logical_path:
            del logical_path["version"]
        if "frame" in logical_path:
            del logical_path["frame"]
        return logical_path
    sorted_assets = sorted(asset_list, key=access_key)
    iterator = itertools.groupby(sorted_assets, key=access_key)
    for asset_descriptor, sub_asset_list in iterator:
        highest_version = -1
        highest_asset = None
        for asset in sub_asset_list:
            asset_version = asset.version
            if asset_version > highest_version:
                highest_asset = asset
                highest_version = asset_version
        out_asset_list.append(highest_asset)
    return out_asset_list

def getLatestMarcusRig():
    latest_asset = getLatestAsset(
        JOB_ID,
        "Globals",
        "Characters",
        "marcus",
        "rig",
        "master",
        "Rig",
    )
    return latest_asset


def getLatestDroneRig():
    latest_asset = getLatestAsset(
        JOB_ID,
        "Globals",
        "Vehicles",
        "drone",
        "rig",
        "rigging",
        "Rig",
    )
    return latest_asset

def getLatestHybridRig():
    latest_asset = getLatestAsset(
        JOB_ID,
        "Globals",
        "Vehicles",
        "jetHybrid",
        "rig",
        "rigging",
        "Rig",
    )
    return latest_asset

def getLatestFA18HornetRig():
    latest_asset = getLatestAsset(
        JOB_ID,
        "Globals",
        "Vehicles",
        "FA18Hornet",
        "rig",
        "rigging",
        "Rig",
    )
    return latest_asset


def getLatestAsset(
    project_id,
    fin_type,
    fin_category,
    item,
    activity,
    task,
    asset_type,
    cache_name=None,
):
    query_args = {
        "project_id": project_id,
        "fin_type": fin_type,
        "fin_category": fin_category,
        "item": item,
        "activity": activity,
        "task": task,
        "asset_type": asset_type,
    }
    assets = databe.asset.getByTask(**query_args)
    version_number = 0
    my_asset = None
    for asset in assets:
        if cache_name:
            if asset.logicalPath["asset_label"] != cache_name:
                continue
        asset_version = int(asset.version)
        if (asset.type == asset_type) and (asset_version > version_number):
            my_asset = asset
            version_number = asset_version
    return my_asset


def _initLogging():
    import logging.config
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,  # this fixes the problem
        'formatters': {
            'standard': {
                'format': '[%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': "DEBUG",
                'propagate': True
            }
        }
    })


if __name__ == "__main__":

    jetHybrid_filter_list = [
        '126-002',
        '126-013',
        '126-015',
        '126-017',
        '126-024',
        '126-026',
        '126-027',
        '126-030',
        '126-038',
        '126-041',
        '126-054',
        '126-058',
        '126-066',
        '126-068',
        '126-069',
        '126-070',
        '137-001']

    main(filter_list=jetHybrid_filter_list)



import pymel.core as pm
def test():
    drones_roots = []
    hornet_roots = maya.cmds.ls("FA18Hornet*:placement_ctl")

    maya.cmds.select(drones_roots, hornet_roots)

    print pm.selected()


'''
drone_hornet_filter_list = [
        '126-002',
        '126-013',
        '126-014',
        '126-015',
        '126-016',
        '126-017',
        '126-020',
        '126-021',
        '126-022',
        '126-023',
        '126-027',
        '126-028',
        '126-042',
        '126-064',
        '126-066',
        '126-068',
        '126-069',
        '126-070',
        '126-071',
        '126-072',
        '126-073',
        '126-074',
        '126-075',
        '126-076',
        '126-077',
        '126-078',
        '126-082']
    ['126-001',
    '126-002',
    '126-013',
    '126-014',
    '126-015',
    '126-016',
    '126-017',
    '126-020',
    '126-021',
    '126-022',
    '126-023',
    '126-027',
    '126-028',
    '126-042',
    '126-064',
    '126-066',
    '126-068',
    '126-069',
    '126-070',
    '126-071',
    '126-072',
    '126-073',
    '126-074',
    '126-075',
    '126-076',
    '126-077',
    '126-078',
    '126-082']'''
# remaining_list = [
#     "066-004",
#     "066-016",
#     "066-023",
# ]
# marcus_list = [
#     "066-012",
#     "066-016",
#     "066-018",
#     #"066-022",
#     "066-023",
#     "066-028",
#     "066-080",
# ]
# all_blaster_fire_list = [
#     # "066-043",
#     "066-004",
#     "066-005",
#     "066-006",
#     "066-008",
#     "066-012",
#     "066-014",
#     "066-020",
#     "066-023",
#     "066-025",
#     "066-028",
#     "066-029",
#     "066-030",
#     "066-032",
#     "066-038",
#     "066-047",
#     "066-048",
#     "066-065",
# ]


