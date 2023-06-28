import os
import maya.cmds as mc
import maya.mel as mm
import layoutHud


def mf_playblast(renderCam='renderCam_geo:shotCam'):
    if not mc.objExists(renderCam):
        mc.inViewMessage(assistMessage='Camera {0} does not exist. Aborting playblast.'.format(renderCam),
                         position='midCenterBot', fade=True, fadeStayTime=5000, backColor=0xFF00FF00)
        return

    isScene = mc.file(q=True, exists=True)

    if isScene:

        try:
            myPanel = mc.getPanel(withFocus=True)
            current_mode = mc.evaluationManager(query=True, mode=True)
            mc.evaluationManager(mode='off')
            mc.modelPanel(myPanel, e=True, cam=renderCam)
            mc.modelEditor(myPanel, e=True, displayTextures=True)
            f = mc.file(q=True, sn=True).split(".")[0] + ".mov"
            mc.camera(renderCam, e=True, displayFilmGate=0, displayGateMask=0, displayResolution=0,
                      displaySafeAction=0, displaySafeTitle=0, displayFieldChart=0)
            mc.setAttr('{0}.ovr'.format(renderCam), 1)
            layoutHud.go()
            current_scene = mc.file(q=True, sn=True)
            filename = os.path.basename(current_scene)
            f = current_scene.split("work")[0]
            fname = "work/playblast/" + filename.split(".")[0] + ".mov"
            fullname = f + fname
            xRes = 1280
            yRes = 536
            mc.setAttr("defaultResolution.aspectLock", 0)
            mc.setAttr("defaultResolution.w", 1280)
            mc.setAttr("defaultResolution.h", 536)
            mc.setAttr('defaultResolution.deviceAspectRatio', ((1280) / (536)))
            print(fullname)
            mc.select(cl=True)
            mc.playblast(format="qt", filename=fullname, os=True, showOrnaments=True, fp=4, percent=100,
                         compression="jpeg", fo=True,
                         widthHeight=(xRes, yRes))
            mm.eval("ToggleCameraNames;")
            mm.eval("ToggleCurrentFrame;")
            mm.eval("ToggleFocalLength;")
            mc.headsUpDisplay("lhUser", remove=True)
            mc.headsUpDisplay("lhFile", remove=True)
            mc.headsUpDisplay("lhStep", remove=True)
            mc.playbackOptions(playbackSpeed="playEveryFrame")
        except Exception as e:
            mc.error(str(e))
    else:
        mc.inViewMessage(assistMessage='You need to save your file first before playblasting,', position='midCenterBot',
                         fade=True, fadeStayTime=5000, backColor=0xFF00FF00)


if __name__ == "__main__":
    mf_playblast()
