import maya.cmds
def main():

    output_basepath = "C:\Users\julian.beiboer\Documents\FIN"
    output_path = "{0}/interactive_load.ma".format(output_basepath)
    if maya.cmds.about(batch=True):
        maya.cmds.loadPlugin("fbxmaya")
        output_path = "{0}/standalone_load.ma".format(output_basepath)
    maya.cmds.file(new=1, f=1, pmt=0)  # new, force, no prompt
    fbx_file = "J:/INTERCEPTOR_4137/depts/Reallusion/export to unreal/Alexander_06/Alexander_06.Fbx"
    maya.cmds.file(
        fbx_file,
        i=True,
        type="FBX",
        ignoreVersion=True,
        mergeNamespacesOnClash=False,
        rpr="MocapImported",
        options="fbx",
        pr=True,
        importFrameRate=False,
        importTimeRange="override"
    )
    maya.cmds.file(rn=output_path)
    maya.cmds.file(save=True, type="mayaAscii")

if __name__ == "__main__":
    import maya.standalone
    maya.standalone.initialize()
    main()

if False:  # just keeping this here to easily copy in to script editor

    import test
    test.main()