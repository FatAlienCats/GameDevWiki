import maya.cmds as cmds
import os


def convert_movie_to_image_sequence():
    # Prompt the user for the movie file location
    result = cmds.fileDialog2(fileMode=1, caption="Select Movie File")

    # Check if the user selected a movie file
    if result is None:
        # The user clicked on the 'Cancel' button, so we return early
        return

    # Get the selected movie file
    movie_file = result[0]

    # Set the path to the ffmpeg executable
    ffmpeg_path = "/mnt/software/production/ffmpeg/ffmpeg-git-20220910-amd64-static/ffmpeg"

    # Set the output directory for the image sequence
    output_dir = os.path.splitext(movie_file)[0]

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Construct the ffmpeg command
    cmd = f'"{ffmpeg_path}" -i "{movie_file}" "{output_dir}/image%04d.png"'

    # Execute the ffmpeg command
    os.system(cmd)

    # Create a plane in Maya and rename it to 'ReferencePlane'
    plane = cmds.polyPlane(name='ReferencePlane')[0]

    # Place the plane in a group called 'temp'
    if not cmds.objExists('temp'):
        cmds.group(name='temp', empty=True)
    cmds.parent(plane, 'temp')

    # Create a parent constraint between the plane and the 'renderCam:camRoot' node with maintain offset turned off
    cmds.parentConstraint('renderCam:camRoot', plane, mo=False)

    # Create a new material for the plane
    material = cmds.shadingNode('lambert', asShader=True)

    # Create a file node and set its 'fileTextureName' attribute to the first frame of the image sequence
    file_node = cmds.shadingNode('file', asTexture=True)
    cmds.setAttr(f'{file_node}.fileTextureName', f'{output_dir}/image0001.png', type='string')

    # Set the 'useFrameExtension' attribute of the file node to 1
    cmds.setAttr(f'{file_node}.useFrameExtension', 1)
    cmds.setAttr(f'{file_node}.frameOffset', -1000)
    # Connect the file node's 'outColor' attribute to the material's 'color' attribute
    cmds.connectAttr(f'{file_node}.outColor', f'{material}.color')

    # Create a shading group and connect the material's 'outColor' attribute to its 'surfaceShader' attribute
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
    cmds.connectAttr(f'{material}.outColor', f'{shading_group}.surfaceShader')

    # Assign the material to the plane
    cmds.sets(plane, edit=True, forceElement=shading_group)


# Create a new window in Maya
window = cmds.window(title="Convert Movie to Image Sequence")
cmds.columnLayout()

# Add a button to the window to run the script
cmds.button(label="Convert Movie to Image Sequence", command=lambda x: convert_movie_to_image_sequence())

# Show the window
cmds.showWindow(window)
