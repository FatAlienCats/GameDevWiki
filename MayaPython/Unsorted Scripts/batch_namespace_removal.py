import maya.standalone

maya.standalone.initialize()
import maya.cmds
from MayaTools import m_namespace, m_standalone
import logging

from kore import shotgrid, authorization, location, utils
import animModules
from common.mayaScene import Scene

logging.basicConfig()
logger = logging.getLogger('batch namespace')
logger.setLevel(logging.DEBUG)
UKELELE_BND = ["BBF01BND-0020", "BBF01BND-0030", "BBF01BND-0090", "BBF01BND-0100", "BBF01BND-0120", "BBF01BND-0150",
               "BBF01BND-0160", "BBF01BND-0190", "BBF01BND-0200", "BBF01BND-0210", "BBF01BND-0220", "BBF01BND-0280", ]

UKELELE_CPK = ["BBF03CPK-0220", "BBF03CPK-0230", "BBF03CPK-0260", "BBF03CPK-0290", "BBF03CPK-0310", "BBF03CPK-0330",
               "BBF03CPK-0390", "BBF03CPK-0410", ]

UKELELE_REC = ["BBF03REC-0300", "BBF03REC-0330", "BBF03REC-0350", "BBF03REC-0380",
               "BBF03REC-0400", "BBF03REC-0440", "BBF03REC-0520", ]

UKELELE_MON = ["BBF05MON-0100", "BBF05MON-0120", "BBF05MON-0140", "BBF05MON-0160", "BBF05MON-0170", "BBF05MON-0180",
               "BBF05MON-0190", "BBF05MON-0200", "BBF05MON-0220","BBF05MON-0230", "BBF05MON-0260", "BBF05MON-0290",
               "BBF05MON-0300", "BBF05MON-0310", "BBF05MON-0320","BBF05MON-0330", "BBF05MON-0370", "BBF05MON-0390",
               "BBF05MON-0400", "BBF05MON-0410", ]

UKELELE_DPT = ["BBF07DPT-0110", "BBF07DPT-0120", "BBF07DPT-0130", "BBF07DPT-0140", "BBF07DPT-0150", "BBF07DPT-0152",
               "BBF07DPT-0155", "BBF07DPT-0160", "BBF07DPT-0170", "BBF07DPT-0175", "BBF07DPT-0180", "BBF07DPT-0190",
               "BBF07DPT-0200", "BBF07DPT-0210", "BBF07DPT-0220", "BBF07DPT-0230", "BBF07DPT-0235", "BBF07DPT-0240",
               "BBF07DPT-0250", "BBF07DPT-0260", "BBF07DPT-0270", "BBF07DPT-0280", "BBF07DPT-0290", "BBF07DPT-0300",
               "BBF07DPT-0310", "BBF07DPT-0320", "BBF07DPT-0330", "BBF07DPT-0340", ]

UKELELE_SEW = ["BBF07SEW-0010", "BBF07SEW-0020", "BBF07SEW-0040", "BBF07SEW-0050", "BBF07SEW-0060", "BBF07SEW-0070",
               "BBF07SEW-0080", "BBF07SEW-0090", "BBF07SEW-0100",
               "BBF07SEW-0110", "BBF07SEW-0120", "BBF07SEW-0130", "BBF07SEW-0140", "BBF07SEW-0150", "BBF07SEW-0160",
               "BBF07SEW-0170", "BBF07SEW-0180", "BBF07SEW-0190", "BBF07SEW-0210", "BBF07SEW-0230", "BBF07SEW-0240",
               "BBF07SEW-0260", "BBF07SEW-0280", "BBF07SEW-0320", "BBF07SEW-0340", "BBF07SEW-0380", "BBF07SEW-0400",
               "BBF07SEW-0410", "BBF07SEW-0430", "BBF07SEW-0450", "BBF07SEW-0470", "BBF07SEW-0480", "BBF07SEW-0500",
               "BBF07SEW-0530", "BBF07SEW-0560", "BBF07SEW-0590", ]

UKELELE_TRD = ["BBF07TRD-0160", "BBF07TRD-0170", "BBF07TRD-0180", "BBF07TRD-0190", "BBF07TRD-0200", "BBF07TRD-0210",
               "BBF07TRD-0220", "BBF07TRD-0230", "BBF08FIN-0240", "BBF08FIN-0250", ]

UKELELE_SHOTS_OLD = ["BBF01BND-0020", "BBF01BND-0030", "BBF01BND-0090", "BBF01BND-0100", "BBF01BND-0120", "BBF01BND-0150",
                 "BBF01BND-0160", "BBF01BND-0190", "BBF01BND-0200", "BBF01BND-0210", "BBF01BND-0220", "BBF01BND-0280",
                 "BBF03CPK-0220", "BBF03CPK-0230", "BBF03CPK-0260", "BBF03CPK-0310", "BBF03CPK-0390", "BBF03CPK-0410",
                 "BBF07DPT-0110", "BBF07DPT-0130", "BBF07DPT-0140", "BBF07DPT-0150", "BBF07DPT-0155", "BBF07DPT-0160",
                 "BBF07DPT-0210", "BBF07DPT-0220", "BBF07DPT-0235", "BBF07DPT-0250", "BBF07DPT-0260", "BBF07DPT-0270",
                 "BBF07DPT-0280", "BBF07DPT-0300", "BBF07DPT-0320"]

# Shots with flute, bass, triangle, harmonica or tuba
SHOTS_FBTHT = ["BBF01BND-0020", "BBF01BND-0030", "BBF01BND-0050", "BBF01BND-0070", "BBF01BND-0120", "BBF01BND-0140",
               "BBF01BND-0150", "BBF01BND-0160", "BBF01BND-0190", "BBF01BND-0200", "BBF01BND-0210", "BBF01BND-0220",
               "BBF01BND-0240", "BBF01BND-0250", "BBF01BND-0260", "BBF01BND-0270", "BBF01BND-0280", "BBF03REC-0300",
               "BBF03REC-0320", "BBF03REC-0330", "BBF03REC-0340", "BBF03REC-0380", "BBF03REC-0390", "BBF03REC-0400",
               "BBF03REC-0420", "BBF03REC-0440", "BBF03REC-0520", "BBF03CPK-0220", "BBF03CPK-0230", "BBF03CPK-0260",
               "BBF03CPK-0290", "BBF03CPK-0310", "BBF03CPK-0330", "BBF03CPK-0390", "BBF03CPK-0410", ]

DONE = ["BBF01BND-0030", ]
TEST = ["z_TestSpherery-0010", ]  

# /mnt/production-data/projects/BBF/scene/
# BBF01BND/BBF01BND-0020/
# animation/work/
# BBF01BND-0020-animation-00013.ma
BASE_PATH = "/mnt/production-data/projects/BBF/scene"
# /mnt/production-data/projects/BBF/scene/z_TestSpherery/z_TestSpherery-0010/animation/work
# TODO: Add flute, bass, triangle, harmonica and tuba to namespaces
NAMESPACE_REMOVAL = ['ukelele_main:ukulele:', 'electricBass_main:electricBass:',
                     'triangle_main:triangle:', 'tuba_main:tuba:']




def batch_remove_namespace():
    for shot in TEST:
        filepath = find_latest_shot(shot)
        open_shot(filepath)
        latest_workspace = find_latest_workspace(shot)
        version_up = animModules.increment_scene_number(latest_workspace)
        for namespace in NAMESPACE_REMOVAL:
            m_namespace.remove_namespace(namespace, mergeWithParent=True, mergeWithRoot=False)
        save_scene(version_up)


def save_scene(version_up):
    saveContext = {'type': 'mayaAscii', 'save': True, 'force': True, 'defaultExtensions': False}
    Scene.saveScene(version_up, **saveContext)
    create_comment(version_up, "removing Namespace issue")


def open_shot(filepath):
    maya.cmds.file(filepath, o=True, f=True)


def create_comment(filepath, comment=None):
    if comment:
        with open('{0}.comment'.format(filepath), 'w') as f:
            f.write(comment)


def find_latest_shot(code):
    with authorization.ShotGrid() as sg:
        session = shotgrid.Session(sg)
        shot = session.findShot(code, fields=["id"])

    criteria = [
        ["project", "is", session.getPrjectContext()],
        ["entity", "is", shot],
        ["content", "is", "animation"],
    ]

    task = session.find("Task", filters=criteria, fields=["content"], first=True)
    if session.findLatestVersion(task, 'checkin', fields=["code"]):
        latest = session.findLatestVersion(task, 'checkin', fields=["code"])
        publish_type = 'checkin'
    else:
        latest = session.findLatestVersion(task, 'submit', fields=["code"])
        publish_type = 'submit'

    sequence = code.split('-')[0]
    logger.info("Latest Shot: ", "{0}/{1}/{2}/animation/{3}/{4}/{2}.ma".format(BASE_PATH, sequence, code,
                                                                               publish_type, latest["code"]))
    return "{0}/{1}/{2}/animation/{3}/{4}/{2}.ma".format(BASE_PATH, sequence, code, publish_type, latest["code"])


def find_latest_workspace(code):
    sequence = code.split('-')[0]
    work_dir = "{0}/{1}/{2}/animation/{3}/".format(BASE_PATH, sequence, code, 'work')

    workFiles = utils.getFiles(
        work_dir,
        'ma',
        filename=None,
        reverse=True,
    )
    logger.info("Work files:", workFiles[0])
    return workFiles[0]


if __name__ == '__main__':
    # m_standalone.initiate_standalone()
    batch_remove_namespace()
