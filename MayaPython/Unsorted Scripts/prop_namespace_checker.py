# import maya.standalone
import os.path
import pprint

# maya.standalone.initialize()
import maya.cmds
import modeling
from MayaTools import m_namespace, m_standalone
import logging

from kore import shotgrid, authorization, location, utils
import animModules
from common.mayaScene import Scene

logging.basicConfig()
logger = logging.getLogger('batch namespace')
logger.setLevel(logging.DEBUG)

BROKEN_NAMESPACE = []
CORRECT_NAMESPACE = []
NO_CHECKIN_FILE = []
DATA = []
cleared = []
def batch_check_rig_namespaces():
    for prop in PROPS:
        data = {"name": prop["code"], "Broken": False, 'No Checkin': False, "Cleared": False}
        latest = find_asset_versions(prop["code"], 'rigging')
        if latest:
            filepath = "/mnt/production-data/projects/BBF/asset/" \
                       "prop/{0}/rigging/default/checkin/{1}/{0}.ma".format(prop["code"], latest["code"])
            if os.path.exists(filepath):
                maya.cmds.file(filepath, o=True, f=True)
                if checkNodesNames():
                    CORRECT_NAMESPACE.append(prop['code'])
                    data["Cleared"] = True
                    print("Cleared")
                    cleared.append("Cleared")
                else:
                    data["Broken"] = True
                    BROKEN_NAMESPACE.append(prop['code'])
                    print("Broken")
                    cleared.append("Broken")
            else:
                NO_CHECKIN_FILE.append(prop['code'])
                data["No Checkin"] = True
                print("No Checkin")
                cleared.append("No Checkin")

        else:
            NO_CHECKIN_FILE.append(prop['code'])
            data["No Checkin"] = True
            print("No Checkin")
            cleared.append("No Checkin")

        DATA.append(data)
    pprint.pprint(DATA)
    for c in cleared:
        print(c)


def checkNodesNames():
    from maya import cmds
    nodes = cmds.ls()
    context = {}
    for node in nodes:
        if ":" not in node:
            continue
        context.setdefault('Detected ":" (name-space) in the nodes', []).append(node)

    if context:
        valid = False
    else:
        valid = True

    return valid


def find_asset_versions(asset_code, task_name, sub_type="checkin"):
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
        try:
            asset = session.findAsset(asset_code, fields=["id"])
        except:
            return
        criteria = [
            ["project", "is", session.getPrjectContext()],
            ["entity", "is", asset],
            ["content", "is", task_name],
        ]

        task = session.find("Task", filters=criteria, fields=["content"], first=True)
        latest = session.findLatestVersion(task, sub_type, fields=["code"])
        return latest

t = [{"id": "3936", "code": "iceChunk_main", },]
TEST = [{"id": "3795", "code": "skidoo_main", },
        {"id": "3931", "code": "coach_main", },
        {"id": "3932", "code": "coach_skis", },
        ]

PROPS = [{"id": "3795", "code": "skidoo_main", },
         {"id": "3931", "code": "coach_main", },
         {"id": "3932", "code": "coach_skis", },
         {"id": "3933", "code": "crossbow_main", },
         {"id": "3934", "code": "arrow_main", },
         {"id": "3935", "code": "skidoo_sidecar", },
         {"id": "3936", "code": "iceChunk_main", },
         {"id": "3937", "code": "rock_main", },
         {"id": "3938", "code": "machineGun_main", },
         {"id": "3939", "code": "volosSpear_main", },
         {"id": "3940", "code": "violinNerlin_main", },
         {"id": "3942", "code": "pot_main", },
         {"id": "3943", "code": "pan_main", },
         {"id": "3944", "code": "bassinet_main", },
         {"id": "3945", "code": "highChair_main", },
         {"id": "3946", "code": "milk_main", },
         {"id": "3947", "code": "sippyCup_main", },
         {"id": "3948", "code": "swingSet_main", },
         {"id": "3949", "code": "ukelele_main", },
         {"id": "3950", "code": "musicStand_main", },
         {"id": "3951", "code": "musicSheet_main", },
         {"id": "3952", "code": "drumKit_main", },
         {"id": "3953", "code": "drumSticks_main", },
         {"id": "3954", "code": "saxophone_main", },
         {"id": "3955", "code": "clarinet_main", },
         {"id": "3956", "code": "tuba_main", },
         {"id": "3957", "code": "trumpet_main", },
         {"id": "3958", "code": "flute_main", },
         {"id": "3959", "code": "harmonica_main", },
         {"id": "3960", "code": "trombone_main", },
         {"id": "3961", "code": "guitar_main", },
         {"id": "3962", "code": "violinBetty_main", },
         {"id": "3963", "code": "violinBow_main", },
         {"id": "3964", "code": "bikeA_main", },
         {"id": "3965", "code": "bikeB_main", },
         {"id": "3966", "code": "folder_main", },

         {"id": "3967", "code": "notebook_main", },
         {"id": "3968", "code": "leaf_main", },
         {"id": "3969", "code": "earbuds_main", },
         {"id": "3970", "code": "carA_main", },
         {"id": "3971", "code": "carB_main", },
         {"id": "3972", "code": "carC_main", },
         {"id": "3973", "code": "carD_main", },
         {"id": "3974", "code": "carE_main", },
         {"id": "3975", "code": "carF_main", },
         {"id": "3976", "code": "icecream_main", },
         {"id": "3977", "code": "icecream_splat", },
         {"id": "3978", "code": "icecreamMagic_main", },
         {"id": "3979", "code": "backpackBetty_main", },
         {"id": "3980", "code": "photoSiblings_main", },
         {"id": "3981", "code": "photoAneska_main", },
         {"id": "3982", "code": "homework_main", },
         {"id": "3983", "code": "pen_main", },
         {"id": "3984", "code": "piano_main", },
         {"id": "3985", "code": "mirror_main", },
         {"id": "3986", "code": "unicornStew_main", },
         {"id": "3987", "code": "chair_main", },
         {"id": "3988", "code": "dogChair_main", },
         {"id": "3989", "code": "ladle_main", },
         {"id": "3990", "code": "plate_main", },
         {"id": "3991", "code": "spoon_main", },
         {"id": "3992", "code": "spoon_stew", },
         {"id": "3993", "code": "knife_main", },
         {"id": "3994", "code": "fork_main", },
         {"id": "3995", "code": "glass_main", },
         {"id": "3996", "code": "candle_main", },
         {"id": "3997", "code": "violinStand_main", },
         {"id": "3998", "code": "chest_main", },
         {"id": "3999", "code": "scroll_main", },
         {"id": "4000", "code": "blowTorch_main", },
         {"id": "4001", "code": "weldingMask_main", },
         {"id": "4002", "code": "zombieBody_main", },
         {"id": "4003", "code": "candle_melted", },
         {"id": "4004", "code": "bones_main", },
         {"id": "4005", "code": "bodyParts_main", },
         {"id": "4006", "code": "weights_main", },
         {"id": "4007", "code": "dumbells_main", },
         {"id": "4008", "code": "globe_main", },
         {"id": "4009", "code": "egg_main", },
         {"id": "4010", "code": "eggShell_cracked", },
         {"id": "4011", "code": "eggShell_main", },
         {"id": "4012", "code": "fryPan_main", },
         {"id": "4013", "code": "spatula_main", },
         {"id": "4014", "code": "breakfastFood_main", },
         {"id": "4016", "code": "baton_main", },
         {"id": "4017", "code": "phoneSnitch_main", },
         {"id": "4018", "code": "skidoo_motorbike", },
         {"id": "4019", "code": "pistol_main", },
         {"id": "4020", "code": "pistolBolt_main", },
         {"id": "4021", "code": "carB_wrecked", },
         {"id": "4022", "code": "carChunk_main", },
         {"id": "4023", "code": "paperBag_main", },
         {"id": "4024", "code": "magicCarpet_main", },
         {"id": "4025", "code": "cyclopsLight_main", },
         {"id": "4026", "code": "handVacuum_main", },
         {"id": "4027", "code": "snacks_main", },
         {"id": "4028", "code": "vacuum_giant", },
         {"id": "4029", "code": "fairyFloss_main", },
         {"id": "4030", "code": "jumbotron_main", },
         {"id": "4031", "code": "trophy_main", },
         {"id": "4032", "code": "teddy_main", },
         {"id": "4033", "code": "carvingKnife_main", },
         {"id": "4034", "code": "sharpener_main", },
         {"id": "4035", "code": "rockChunk_main", },
         {"id": "4036", "code": "metalDetector_main", },
         {"id": "4037", "code": "screwDriver_main", },
         {"id": "4038", "code": "goggles_main", },
         {"id": "4039", "code": "rubberChicken_main", },
         {"id": "4040", "code": "tableCloth_main", },
         {"id": "4041", "code": "clipBoard_main", },
         {"id": "4042", "code": "punchBowl_main", },
         {"id": "4043", "code": "jukeBox_main", },
         {"id": "4044", "code": "presentA_main", },
         {"id": "4045", "code": "presentB_main", },
         {"id": "4046", "code": "presentC_main", },
         {"id": "4047", "code": "presentD_main", },
         {"id": "4048", "code": "chocolates_main", },
         {"id": "4049", "code": "hotDogBun_main", },
         {"id": "4050", "code": "sausage_main", },
         {"id": "4051", "code": "presentGuitar_main", },
         {"id": "4052", "code": "cake_main", },
         {"id": "4053", "code": "partyPie_main", },
         {"id": "4054", "code": "plate_partyPies", },
         {"id": "4055", "code": "partyTable_main", },
         {"id": "4056", "code": "violinNerlin_smashed", },
         {"id": "4057", "code": "partyDebris_main", },
         {"id": "4058", "code": "mug_main", },
         {"id": "4059", "code": "mobileNat_main", },
         {"id": "4060", "code": "cane_main", },
         {"id": "4061", "code": "torch_main", },
         {"id": "4062", "code": "trash_main", },
         {"id": "4063", "code": "manacles_main", },
         {"id": "4064", "code": "throne_main", },
         {"id": "4065", "code": "throneBetty_main", },
         {"id": "4066", "code": "manacledChair_main", },
         {"id": "4067", "code": "goblet_main", },
         {"id": "4068", "code": "plateFancy_main", },
         {"id": "4069", "code": "cupFancy_main", },
         {"id": "4070", "code": "washtubeBass_main", },
         {"id": "4071", "code": "clefInstrumentA_main", },
         {"id": "4072", "code": "clefInstrumentB_main", },
         {"id": "4073", "code": "clefInstrumentC_main", },
         {"id": "4074", "code": "clefInstrumentD_main", },
         {"id": "4075", "code": "clefInstrumentE_main", },
         {"id": "4076", "code": "houseParts_main", },
         {"id": "4077", "code": "electricGuitar_main", },
         {"id": "4078", "code": "electricBass_main", },
         {"id": "4079", "code": "microphone_main", },
         {"id": "4080", "code": "cupcake_main", },
         {"id": "4081", "code": "broom_main", },
         {"id": "4082", "code": "wormPoop_main", },
         {"id": "4083", "code": "trayPartyFood_main", },
         {"id": "4084", "code": "sandwich_main", },
         {"id": "4085", "code": "crate_main", },
         {"id": "4117", "code": "houseDebris_main", },
         {"id": "4118", "code": "stage_main", },
         {"id": "4119", "code": "moleskinNotebook_main", },
         {"id": "4122", "code": "mobileBetty_main", },
         {"id": "4124", "code": "brokenDoor_main", },
         {"id": "4125", "code": "drawingBetty_main", },
         {"id": "4126", "code": "pencilBetty_main", },
         {"id": "4127", "code": "booksNerlin_main", },
         {"id": "4128", "code": "candelabra_main", },
         {"id": "4129", "code": "helmetA_main", },
         {"id": "4130", "code": "helmetB_main", },
         {"id": "4131", "code": "grapplingHook_main", },
         {"id": "4132", "code": "cupcakeMagic_main", },
         {"id": "4133", "code": "carG_main", },
         {"id": "4134", "code": "carH_main", },
         {"id": "4136", "code": "razorNerlin_main", },
         {"id": "4137", "code": "skateBoard_main", },
         {"id": "4138", "code": "bus_main", },
         {"id": "4139", "code": "violaNerlin_main", },
         {"id": "4140", "code": "flag_main", },
         {"id": "4141", "code": "lamp_main", },
         {"id": "4143", "code": "cage_main", },
         {"id": "4144", "code": "soda_main", },
         {"id": "4145", "code": "icecream_Troll", },
         {"id": "4151", "code": "photoKnute_main", },
         {"id": "4154", "code": "amp_main", },
         {"id": "4156", "code": "tableFancy_main", },
         {"id": "4157", "code": "wheelChair_main", },
         {"id": "4162", "code": "triangle_main", },
         {"id": "4167", "code": "violinElectric_main", },
         {"id": "4168", "code": "presentViolin_main", },
         {"id": "4176", "code": "sandwich_bullfrog", },
         {"id": "4178", "code": "basketBall_main", },
         {"id": "4877", "code": "lectern_main", },
         {"id": "4878", "code": "ironGate_main", },
         {"id": "4879", "code": "woodenLever", },
         {"id": "4880", "code": "sign_recital", },
         {"id": "4881", "code": "gateBroken_main", },
         {"id": "4910", "code": "musicSheet_clean", },
         {"id": "5009", "code": "brownViolinStand", },
         {"id": "5011", "code": "darkBrownViolinStand", },
         {"id": "5141", "code": "chair_Betty", },
         {"id": "5142", "code": "laptop_Betty", },
         {"id": "5174", "code": "bowl_stew", },
         {"id": "5175", "code": "bowl_empty", },
         {"id": "5177", "code": "unicornHead_stew", },
         {"id": "5178", "code": "laptop_main", },
         {"id": "5179", "code": "colouredPencil", },
         {"id": "5240", "code": "plate_bread", },
         {"id": "5241", "code": "bread_Slice", },
         {"id": "5242", "code": "truck_main", },
         {"id": "5243", "code": "beaker_main", },
         {"id": "5244", "code": "microscope_main", },
         {"id": "5246", "code": "radioDevice_main", },
         {"id": "5247", "code": "ladle_stew", },
         {"id": "5248", "code": "musicStand_school", },
         {"id": "5250", "code": "labChair_main", },
         {"id": "5274", "code": "howardTank_main", },
         {"id": "5276", "code": "labDoor_main", },
         {"id": "5277", "code": "labWindow_main", },
         {"id": "5306", "code": "labLadder_main", },
         {"id": "5339", "code": "oldPc_main", },
         {"id": "5372", "code": "powerboard_main", },
         {"id": "5405", "code": "chair_school", },
         {"id": "5407", "code": "helmetC_main", },
         {"id": "5438", "code": "chair_winchflat", },
         {"id": "5439", "code": "chair_Aneska", },
         {"id": "5440", "code": "chair_Silent", },
         {"id": "5441", "code": "chair_morbid", },
         {"id": "5442", "code": "chair_Nerlin", },
         {"id": "5443", "code": "chair_BettyKitchen", },
         {"id": "5444", "code": "houseDoor_main", },
         {"id": "5572", "code": "labStool_main", },
         {"id": "5768", "code": "fairyWing_main", },
         {"id": "5770", "code": "waterJug_main", },
         {"id": "5801", "code": "saltShaker_main", },
         {"id": "5802", "code": "pepperShaker_main", },
         {"id": "5834", "code": "fireExtinguisher_main", },
         {"id": "5835", "code": "cupPunch_main", },
         {"id": "5836", "code": "bbqGrill_main", },
         {"id": "5837", "code": "tongs_main", },
         {"id": "5838", "code": "rockingChair_main", },
         {"id": "5839", "code": "teaTable_main", },
         {"id": "5840", "code": "ruggrave_main", },
         {"id": "5841", "code": "tableStool_main", },
         {"id": "5842", "code": "teaPot_main", },
         {"id": "5843", "code": "chainsSewer_main", },
         {"id": "5844", "code": "cagesHanging_main", },
         {"id": "5966", "code": "crate_blue", },
         {"id": "5967", "code": "arrow_bad", },
         {"id": "6065", "code": "drumKit_small", },
         {"id": "6132", "code": "manacles_small", },
         {"id": "6164", "code": "recordPlayer_main", },
         {"id": "6268", "code": "bowl_empty_2", },
         {"id": "6269", "code": "bowl_empty_3", },
         {"id": "6270", "code": "bowl_empty_4", },
         {"id": "6271", "code": "bowl_empty_5", },
         {"id": "6272", "code": "bowl_empty_6", },
         {"id": "6273", "code": "bowl_empty_7", },
         {"id": "6275", "code": "bowl_stew_2", },
         {"id": "6276", "code": "bowl_stew_3", },
         {"id": "6277", "code": "bowl_stew_4", },
         {"id": "6278", "code": "bowl_stew_5", },
         {"id": "6279", "code": "bowl_stew_6", },
         {"id": "6280", "code": "bowl_stew_7", },
         {"id": "6281", "code": "bread_Slice_2", },
         {"id": "6282", "code": "bread_Slice_3", },
         {"id": "6283", "code": "bread_Slice_4", },
         {"id": "6284", "code": "bread_Slice_5", },
         {"id": "6285", "code": "fork_main_2", },
         {"id": "6286", "code": "fork_main_3", },
         {"id": "6287", "code": "fork_main_4", },
         {"id": "6288", "code": "fork_main_6", },
         {"id": "6289", "code": "fork_main_5", },
         {"id": "6290", "code": "fork_main_7", },
         {"id": "6291", "code": "glass_main_2", },
         {"id": "6292", "code": "glass_main_5", },
         {"id": "6293", "code": "glass_main_3", },
         {"id": "6294", "code": "glass_main_6", },
         {"id": "6295", "code": "glass_main_4", },
         {"id": "6296", "code": "glass_main_7", },
         {"id": "6297", "code": "knife_main_2", },
         {"id": "6298", "code": "knife_main_3", },
         {"id": "6299", "code": "knife_main_4", },
         {"id": "6300", "code": "knife_main_5", },
         {"id": "6301", "code": "knife_main_6", },
         {"id": "6303", "code": "knife_main_7", },
         {"id": "6305", "code": "plate_main_2", },
         {"id": "6306", "code": "plate_main_3", },
         {"id": "6307", "code": "plate_main_4", },
         {"id": "6308", "code": "plate_main_6", },
         {"id": "6309", "code": "plate_main_5", },
         {"id": "6310", "code": "plate_main_7", },
         {"id": "6311", "code": "spoon_main_2", },
         {"id": "6312", "code": "spoon_main_3", },
         {"id": "6313", "code": "spoon_main_4", },
         {"id": "6314", "code": "spoon_main_6", },
         {"id": "6315", "code": "spoon_main_5", },
         {"id": "6316", "code": "spoon_main_7", },
         {"id": "6317", "code": "spoon_stew_2", },
         {"id": "6318", "code": "spoon_stew_3", },
         {"id": "6319", "code": "spoon_stew_4", },
         {"id": "6320", "code": "spoon_stew_6", },
         {"id": "6321", "code": "spoon_stew_5", },
         {"id": "6322", "code": "spoon_stew_7", },
         {"id": "6336", "code": "cyclopsLight_2", },
         {"id": "6337", "code": "fairyFloss_2", },
         {"id": "6338", "code": "fairyFloss_3", },
         {"id": "6339", "code": "fairyFloss_4", },
         {"id": "6340", "code": "fairyFloss_5", },
         {"id": "6341", "code": "bodyParts_main_2", },
         {"id": "6342", "code": "cagesHanging_2", },
         {"id": "6343", "code": "cagesHanging_3", },
         {"id": "6344", "code": "chocolates_2", },
         {"id": "6345", "code": "chocolates_3", },
         {"id": "6346", "code": "crossbow_2", },
         {"id": "6347", "code": "crossbow_3", },
         {"id": "6348", "code": "cupcake_2", },
         {"id": "6349", "code": "cupcake_3", },
         {"id": "6350", "code": "cupFancy_2", },
         {"id": "6351", "code": "cupFancy_3", },
         {"id": "6352", "code": "cupFancy_4", },
         {"id": "6353", "code": "cupFancy_6", },
         {"id": "6354", "code": "cupFancy_5", },
         {"id": "6355", "code": "cupFancy_7", },
         {"id": "6356", "code": "cupFancy_8", },
         {"id": "6359", "code": "cupPunch_2", },
         {"id": "6360", "code": "cupPunch_3", },
         {"id": "6361", "code": "cupPunch_4", },
         {"id": "6362", "code": "cupPunch_6", },
         {"id": "6363", "code": "cupPunch_5", },
         {"id": "6364", "code": "cupPunch_7", },
         {"id": "6365", "code": "cupPunch_8", },
         {"id": "6366", "code": "cupPunch_9", },
         {"id": "6367", "code": "cupPunch_10", },
         {"id": "6368", "code": "flag_2", },
         {"id": "6369", "code": "flag_3", },
         {"id": "6370", "code": "flag_4", },
         {"id": "6371", "code": "flag_6", },
         {"id": "6372", "code": "flag_5", },
         {"id": "6373", "code": "flag_7", },
         {"id": "6374", "code": "flag_8", },
         {"id": "6375", "code": "flag_9", },
         {"id": "6376", "code": "flag_10", },
         {"id": "6377", "code": "goblet_2", },
         {"id": "6378", "code": "goblet_3", },
         {"id": "6379", "code": "goblet_4", },
         {"id": "6380", "code": "goblet_5", },
         {"id": "6381", "code": "goblet_6", },
         {"id": "6382", "code": "goblet_7", },
         {"id": "6383", "code": "goblet_8", },
         {"id": "6385", "code": "folder_2", },
         {"id": "6386", "code": "folder_3", },
         {"id": "6387", "code": "folder_4", },
         {"id": "6388", "code": "folder_5", },
         {"id": "6389", "code": "hotDogBun_3", },
         {"id": "6390", "code": "hotDogBun_4", },
         {"id": "6391", "code": "hotDogBun_2", },
         {"id": "6392", "code": "hotDogBun_5", },
         {"id": "6393", "code": "icecream_Troll_2", },
         {"id": "6394", "code": "icecream_Troll_3", },
         {"id": "6395", "code": "icecream_Troll_4", },
         {"id": "6396", "code": "icecream_Troll_5", },
         {"id": "6397", "code": "manacles_2", },
         {"id": "6398", "code": "manacles_3", },
         {"id": "6399", "code": "manacles_4", },
         {"id": "6400", "code": "manacles_5", },
         {"id": "6401", "code": "musicSheet_clean_2", },
         {"id": "6402", "code": "musicSheet_clean_3", },
         {"id": "6403", "code": "musicSheet_clean_4", },
         {"id": "6404", "code": "musicSheet_clean_5", },
         {"id": "6405", "code": "musicSheet_clean_6", },
         {"id": "6406", "code": "musicSheet_clean_7", },
         {"id": "6407", "code": "musicSheet_clean_8", },
         {"id": "6408", "code": "musicStand_school_2", },
         {"id": "6409", "code": "musicStand_school_3", },
         {"id": "6410", "code": "musicStand_school_4", },
         {"id": "6411", "code": "musicStand_school_7", },
         {"id": "6412", "code": "musicStand_school_5", },
         {"id": "6413", "code": "musicStand_school_8", },
         {"id": "6414", "code": "musicStand_school_6", },
         {"id": "6415", "code": "notebook_2", },
         {"id": "6416", "code": "notebook_3", },
         {"id": "6417", "code": "notebook_4", },
         {"id": "6418", "code": "notebook_5", },
         {"id": "6419", "code": "plateFancy_2", },
         {"id": "6420", "code": "plateFancy_3", },
         {"id": "6421", "code": "plateFancy_4", },
         {"id": "6422", "code": "plateFancy_6", },
         {"id": "6423", "code": "plateFancy_5", },
         {"id": "6424", "code": "plateFancy_8", },
         {"id": "6425", "code": "plateFancy_7", },
         {"id": "6426", "code": "soda_main_2", },
         {"id": "6427", "code": "soda_main_3", },
         {"id": "6428", "code": "soda_main_4", },
         {"id": "6429", "code": "soda_main_5", },
         {"id": "6430", "code": "torch_main_2", },
         {"id": "6431", "code": "torch_main_3", },
         {"id": "6432", "code": "torch_main_4", },
         {"id": "6433", "code": "torch_main_6", },
         {"id": "6434", "code": "torch_main_5", },
         {"id": "6435", "code": "torch_main_7", },
         {"id": "6436", "code": "torch_main_8", },
         {"id": "6437", "code": "torch_main_9", },
         {"id": "6438", "code": "torch_main_10", },
         {"id": "6439", "code": "trayPartyFood_2", },
         {"id": "6440", "code": "trayPartyFood_3", },
         {"id": "6441", "code": "wormPoop_2", },
         {"id": "6442", "code": "wormPoop_3", },
         {"id": "6443", "code": "wormPoop_4", },
         {"id": "6444", "code": "wormPoop_6", },
         {"id": "6445", "code": "wormPoop_5", },
         {"id": "6446", "code": "wormPoop_7", },
         {"id": "6447", "code": "wormPoop_9", },
         {"id": "6448", "code": "wormPoop_8", },
         {"id": "6449", "code": "wormPoop_10", },
         {"id": "6507", "code": "invention_main", },
         {"id": "6527", "code": "egg_main_2", },
         {"id": "6528", "code": "egg_main_3", },
         {"id": "6791", "code": "z_TestAsset", },
         {"id": "6824", "code": "broomWitch_main", },
         {"id": "6825", "code": "broomWitch_2", },
         {"id": "6826", "code": "sword_main", },
         {"id": "6956", "code": "violinCase", },
         {"id": "7022", "code": "mistyFallsSign_main", },
         {"id": "7056", "code": "cushion_main", },
         {"id": "7057", "code": "crate_table", },
         {"id": "7088", "code": "coach_reigns", },
         {"id": "7089", "code": "direWolfReigns_main", },
         {"id": "7232", "code": "arrow_bad_02", },
         {"id": "7233", "code": "arrow_bad_03", },
         {"id": "7234", "code": "arrow_bad_04", },
         {"id": "7235", "code": "arrow_bad_05", },
         {"id": "7236", "code": "arrow_bad_06", },
         {"id": "7237", "code": "arrow_bad_07", },
         {"id": "7238", "code": "arrow_bad_08", },
         {"id": "7239", "code": "arrow_bad_09", },
         {"id": "7240", "code": "arrow_bad_10", },
         {"id": "7241", "code": "arrow_bad_11", },
         {"id": "7242", "code": "arrow_bad_12", },
         {"id": "7243", "code": "arrow_bad_13", },
         {"id": "7244", "code": "arrow_bad_14", },
         {"id": "7245", "code": "arrow_bad_15", },
         {"id": "7246", "code": "arrow_bad_16", },
         {"id": "7247", "code": "arrow_bad_17", },
         {"id": "7248", "code": "arrow_bad_18", },
         {"id": "7249", "code": "arrow_bad_19", },
         {"id": "7250", "code": "arrow_bad_20", },
         {"id": "7251", "code": "arrow_bad_21", },
         {"id": "7252", "code": "arrow_main_02", },
         {"id": "7253", "code": "arrow_main_03", },
         {"id": "7254", "code": "arrow_main_04", },
         {"id": "7255", "code": "arrow_main_05", },
         {"id": "7256", "code": "arrow_main_06", },
         {"id": "7319", "code": "photoBabybetty_main", },
         {"id": "7320", "code": "photoWedding_main", },
         {"id": "7352", "code": "arrow_main_07", },
         {"id": "7353", "code": "arrow_main_08", },
         {"id": "7354", "code": "arrow_main_09", },
         {"id": "7355", "code": "arrow_main_10", },
         {"id": "7356", "code": "arrow_main_11", },
         {"id": "7357", "code": "arrow_main_12", },
         {"id": "7358", "code": "arrow_main_13", },
         {"id": "7359", "code": "arrow_main_14", },
         {"id": "7360", "code": "arrow_main_15", },
         {"id": "7361", "code": "arrow_main_16", },
         {"id": "7362", "code": "arrow_main_17", },
         {"id": "7363", "code": "arrow_main_18", },
         {"id": "7364", "code": "arrow_main_19", },
         {"id": "7365", "code": "arrow_main_20", },
         {"id": "7366", "code": "arrow_main_21", },
         {"id": "7385", "code": "murkartCastle_2D", },
         {"id": "7451", "code": "plate_partyFood", },
         {"id": "7550", "code": "wormPoopCasing", },
         {"id": "7583", "code": "wormPoopCasing_2", },
         {"id": "7649", "code": "lightsParty_main", },
         {"id": "7684", "code": "saxophone_2", },
         {"id": "7687", "code": "broomWitch_3", },
         {"id": "7688", "code": "broomWitch_4", }, ]
