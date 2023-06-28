import databe
import maya.cmds as cmds


def main():
    scene_path = cmds.file(query=1, sceneName=1)
    print scene_path
    scene_path_split = scene_path.split("/")
    print scene_path_split
    exr_file = getLatestAsset(
        project_id=scene_path_split[1].split("_")[-1],  # 4220
        fin_type="Shots",
        fin_category=scene_path_split[6],
        item=scene_path_split[7],
        task="undistort",
        activity="camera",
        asset_type="Comp"
    )
    exr_filepath = exr_file.systemPath
    print exr_filepath
    # apply this to the domelight
    # setAttr on selected domelight

    #cmds.setAttr("domeLight.text1", exr_filepath)

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
    """
    Finds the latest file of the specified task.
    Args:
        project_id:
        fin_type:
        fin_category:
        item:
        activity:
        task:
        asset_type:
        cache_name:

    Returns:
    """
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
