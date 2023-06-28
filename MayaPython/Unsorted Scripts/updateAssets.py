"""
Asset Checker
Contains functions for checking if assets in the scene are the latest.

Auther: Julian Beiboer
Date Created(dd/mm/yy): 28/03/23
"""
import json
from kore import shotgrid, authorization, location, utils
from maya import cmds
from kore import logger as logging
import os
logger = logging.getLogger('Asset Checker')


def check_assets(open_ui=True):
    """
    Searches through all referenced assets in the scene and compares them to the versions on shotgrid. Adding them to a
    list if they are not the latest version.
    Args:
        open_ui(bool): opens the asset warning ui if there are out of date assets.

    Returns:
        assets_to_update(list[dict]): A list of dictionaries contain the relevant data for each asset to update.
    """
    assets_to_update = []
    scene_assets = find_assets_in_scene()  # dictionary of assets and their version
    for asset in scene_assets:
        if asset["submission_type"] == "checkin":
            asset_versions = find_asset_versions(asset["entity"]["name"], asset["code"], asset["submission_type"])
            latest_asset = asset_versions[-1]
            asset["latest_version"] = latest_asset
            if int(latest_asset) != int(asset["version"]):
                logger.warning("{0} is version {1}, latest version is {2}. Asset not up to date".format(
                    asset["reference_name"], asset["version"], latest_asset))
                assets_to_update.append(asset)
        else:
            logger.warning("{} has no checkin asset loaded".format(asset["reference_name"]))
            latest_asset = "Change to checkin asset"
            asset["latest_version"] = latest_asset
            assets_to_update.append(asset)

    return assets_to_update


def update_asset(asset):
    """
    Updates the provided asset to the latest version, replacing the reference.
    Args:
        asset(dict): Dictionary containing relevant data about the asset and latest version.
    """
    asset_versions = find_asset_versions(asset["entity"]["name"], asset["code"], asset["submission_type"])
    latest_asset = asset_versions[-1]
    replacement_filepath = asset["filepath"].replace(asset["version"], latest_asset)
    update_file = utils.getEnvPath(replacement_filepath)
    logger.info("Updating {0} to latest {1}".format(asset["filepath"], update_file))
    cmds.file(update_file, loadReference=asset["reference_name"], type="mayaAscii", options="v=0;")


def find_asset_versions(asset_code, task_name, sub_type):
    """
    Finds all the asset checked in versions for a given character's task.
    Args:
        asset_code(str): characters name in the pipeline
        task_name(str): task type that the asset belongs to
        sub_type(str): submission type of asset -> submit or checkin
    Returns: a list of version numbers for the asset provided

    """
    with authorization.ShotGrid() as sg:
        session = shotgrid.Session(sg)
        asset = session.findAsset(asset_code, fields=["id"])
        criteria = [
            ["project", "is", session.getPrjectContext()],
            ["entity", "is", asset],
            ["content", "is", task_name],
        ]

        task = session.find("Task", filters=criteria, fields=["content"], first=True)
        versions = session.findVersions(task, fields=["code"], publishType=sub_type)
        return [version["code"] for version in versions]


def find_assets_in_scene():
    """
    Finds all the referenced assets in a scene and adds them to a dictionary with their version number
    Returns:
        scene_assets(dict[string]): name for referenced asset and its version number.
    """
    scene_assets = []
    ref_files = cmds.ls(references=True)

    for ref in ref_files:
        filename = cmds.referenceQuery(ref, filename=True)
        manifest_file = filename.replace(filename.split("/")[-1], "manifest.json")
        asset_data = extract_asset_manifest_data(manifest_file)
        version_number = filename.split("/")[-2]
        code = asset_data["Task"]["content"]
        entity = asset_data["Task"]["entity"]
        if "checkin" in filename:
            sub_type = "checkin"
        else:
            sub_type = "submit"
        asset_stored_data = {"reference_name": ref,
                             "filepath": filename,
                             "entity": entity,
                             "code": code,
                             "submission_type": sub_type,
                             "version": version_number,
                             "latest_version": ""}
        scene_assets.append(asset_stored_data)
    return scene_assets


def extract_asset_manifest_data(filepath):
    """
    Reads the manifest file and returns a dictionary of data
    Args:
        filepath(str): path the manifest.json file

    Returns: A dictionary of data for the asset
    """
    filename = os.path.expandvars(filepath) #Expands $Variables to a full path
    with open(filename, 'r') as f:
        asset_data = json.load(f)
    return asset_data
