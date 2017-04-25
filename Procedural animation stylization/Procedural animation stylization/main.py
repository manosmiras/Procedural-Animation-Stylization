# This piece of code allows to procedurally stylize the curves of an animation using a simple GUI.
# Developed by Emmanuel Miras
# http://miras.uk/ | https://github.com/prezolov

import maya.cmds as cmds
import maya.mel as mel
import math
# partial is imported to allow for passing arguments to callbacks
from functools import partial

# Global variables
framesPosed = [] # Used to keep track of poses
init = [] # List of initialized 'post' or next keyframes, used along with the next list
next = [] # Holds the value of the next keyframe
keyable = [] # List of keyable attributes
keys = [] # Interpolation keyframes
normalizedKeys = [] # Interpolation keyframes normalized
keyframesWithPreAndPost = [] # Used to track if a keyframe is part of a pose created using the range slider or just 1 keyframe
PreAndPostInbetweenKey = {} # Dictionary containing the inbetween keyframe of a pre and post pose
interpolatingKeysCount = 3 # Number of interpolating keys currently tracked
# https://www.desmos.com/calculator/hamwkcp1rh
# Calculates the position of a keyframe on the Y - Axis (Height)
def CalculatePos(x, n, reverse):
    # Reverse curve
    if reverse:
        # 1 - x ^ n
        position = 1 - x ** n
    # Normal curve
    else:
        # (1 - x) ^ n
        position = (1 - x) ** n

    return position
# Used to set/adjust the position (on Y-Axis) of interpolating keyframes
def SetKeyframes(currentKeyFrame, nextKeyFrame, attribute, reverse):
    print(next)
    # 'Pre' keyframe
    currentKeyFrameVal = cmds.keyframe(cmds.ls(sl=1), q = True, vc = 1, t = (currentKeyFrame, currentKeyFrame), at = keyable[attribute])
    # 'Post' keyframe
    nextKeyFrameVal = cmds.keyframe(cmds.ls(sl=1), q = True, vc = 1, t = (nextKeyFrame, nextKeyFrame), at = keyable[attribute])

    maxY = 0
    minY = 0
    # Used for 'de-normalization'
    maxY = currentKeyFrameVal[0]
    minY = nextKeyFrameVal[0]
    print(maxY)
    print(minY)
    global keys
    global normalizedKeys
    global interpolatingKeysCount
    # Set size of lists
    keys = [None] * interpolatingKeysCount
    normalizedKeys = [None] * interpolatingKeysCount

    for currentKey in range (0, interpolatingKeysCount):
        if currentKey == 0:
            # Middle keyframe
            keys[currentKey] = (currentKeyFrame + nextKeyFrame) / 2
        else:
            # Even
            if currentKey % 2 == 0:
                # Right side
                keys[currentKey] = (keys[currentKey - 2] + nextKeyFrame) / 2
            # Odd
            else:
                if currentKey == 1:
                    # Left side
                    keys[currentKey] = (currentKeyFrame + keys[currentKey - 1]) / 2
                else:
                    keys[currentKey] = (currentKeyFrame + keys[currentKey - 2]) / 2
        # Normalize
        normalizedKeys[currentKey] = NormalizeKey(keys[currentKey], currentKeyFrame, nextKeyFrame)

    # Get value from slider
    valueFromSlider = cmds.floatSliderGrp('stylization_val', query=True, value = 1)

    # Position all keys appropriately
    for currentKey in range (0, interpolatingKeysCount):
        # Set the key position
        cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v = CalculatePos(normalizedKeys[currentKey], valueFromSlider, reverse) * (maxY - minY) + minY, t = (keys[currentKey], keys[currentKey]), itt = "spline", ott = "spline" )
        # Make sure the tangents are always spline based
        cmds.keyTangent( cmds.ls(sl=1), edit=True, time=(keys[currentKey], keys[currentKey]), at = keyable[attribute],  itt = "spline", ott = "spline")
        if reverse:
            if (currentKey == interpolatingKeysCount - 2 and cmds.setKeyframe(cmds.ls(sl=1), at = True, query = True, v = 1) < 0.1):
                # Set the most left keyframe tangent to a certain angle and weight to avoid a rough curve
                cmds.keyTangent( cmds.ls(sl=1), edit=True, time=(keys[currentKey], keys[currentKey]), at = keyable[attribute], outAngle=0, outWeight=0, inAngle=0, inWeight=0 )
        else:
            if (currentKey == interpolatingKeysCount - 1 and cmds.setKeyframe(cmds.ls(sl=1), at = True, query = True, v = 1) < 0.1):
                # Set the most right keyframe tangent to a certain angle and weight to avoid a rough curve
                cmds.keyTangent( cmds.ls(sl=1), edit=True, time=(keys[currentKey], keys[currentKey]), at = keyable[attribute], outAngle=0, outWeight=0, inAngle=0, inWeight=0 )
    # Get the number of inbetween keys
    keysInbetween = cmds.keyframe( cmds.ls(sl=1), attribute=keyable[attribute], query=True, keyframeCount=True, t = (currentKeyFrame, nextKeyFrame)) - 2
    # Number of keys to remove
    keysToRemove = keysInbetween - interpolatingKeysCount
    # Remove extra interpolating keys
    for currentKey in range (0, keysToRemove):
        # interpolatingKeysCount is an even number
        if (interpolatingKeysCount % 2 == 0):
            # keysToRemove is an even number
            if (currentKey % 2 == 0):
                # Delete right key
                # print("Delete right key")
                # Gets the far right key, which is to the left(previous) of the post key
                rightKey = cmds.findKeyframe(cmds.ls(sl=1), time=(nextKeyFrame,nextKeyFrame), which="previous")
                cmds.cutKey(cmds.ls(sl=1), time=(rightKey, rightKey))
            # keysToRemove is an odd number
            else:
                # Delete left key
                # print("Delete left key")
                # Gets the far left key, which is to the right(next) of the pre key
                leftKey = cmds.findKeyframe(cmds.ls(sl=1), time=(currentKeyFrame,currentKeyFrame), which="next")
                cmds.cutKey(cmds.ls(sl=1), time=(leftKey, leftKey))
        # interpolatingKeysCount is an odd number
        else:
            if (currentKey % 2 == 0):
                # Delete left key
                # print("Delete left key")
                # Gets the far left key, which is to the right(next) of the pre key
                leftKey = cmds.findKeyframe(cmds.ls(sl=1), time=(currentKeyFrame,currentKeyFrame), which="next")
                cmds.cutKey(cmds.ls(sl=1), time=(leftKey, leftKey))
            # keysToRemove is an odd number
            else:
                # Delete right key
                # print("Delete right key")
                # Gets the far right key, which is to the left(previous) of the post key
                rightKey = cmds.findKeyframe(cmds.ls(sl=1), time=(nextKeyFrame,nextKeyFrame), which="previous")
                cmds.cutKey(cmds.ls(sl=1), time=(rightKey, rightKey))
# Normalizes a key
def NormalizeKey(interpolationKeyframe, firstKeyFrame, lastKeyFrame):
    return (interpolationKeyframe - firstKeyFrame) / (lastKeyFrame - firstKeyFrame)
# Callback for deleting the UI and interpolating keyframes related to a pose
def DeleteButtonPush(time, *args):
    global framesPosed
    global keys
    global next
    global init
    # Make copy of list so elements can be dynamically removed as iterating through it.
    framesPosedCopy = list(framesPosed)
    for i in range(0, len(framesPosedCopy)):
        #print(len(framesPosed))
        #print(i)
        if (framesPosedCopy[i] == time):
            # Pose was set using range slider
            if keyframesWithPreAndPost[i]:
                nextKeyframe = time
                # Delete left hand side
                for keyToDelete in range(0, len(keys)):
                    nextKeyframe = cmds.findKeyframe(cmds.ls(sl=1), time=(time,time), which="next")
                    cmds.cutKey(cmds.ls(sl=1), time=(nextKeyframe, nextKeyframe))
                # Get next keyframe, but will be ignored, this is the middle keyframe
                nextKeyframe = cmds.findKeyframe(cmds.ls(sl=1), time=(time,time), which="next")
                # Delete right hand side
                for keyToDelete in range(0, len(keys)):
                    nextKeyframe = cmds.findKeyframe(cmds.ls(sl=1), time=(nextKeyframe,nextKeyframe), which="next")
                    cmds.cutKey(cmds.ls(sl=1), time=(nextKeyframe, nextKeyframe))

                # Remove from framesPosed list
                framesPosed.remove(time)
                print(str(time) + " was removed.")
            # Pose was set using 1 keyframe
            else:
                # Removes interpolating keyframes
                nextKeyframe = time
                print("time is: " + str(time))
                for keyToDelete in range(0, len(keys)):
                    nextKeyframe = cmds.findKeyframe(cmds.ls(sl=1), time=(time,time), which="next")
                    cmds.cutKey(cmds.ls(sl=1), time=(nextKeyframe, nextKeyframe))

                # Remove from framesPosed list
                framesPosed.remove(time)
                print(str(time) + " was removed.")
            # Remove instance from list
            keyframesWithPreAndPost.pop(i)
            # Remove from next list, make sure list is not empty
            if len(next) > 0:
                next.pop(i)
            # Remove from init list, make sure list is not empty
            if len(init) > 0:
                init.pop(i)

    # Remove the UI parts
    cmds.deleteUI('stylize'+ str(time).replace(".", ""))
    cmds.deleteUI('delete'+ str(time).replace(".", ""))
    # This will also delete the children
    cmds.deleteUI('pose'+ str(time).replace(".", ""))

# Save button callback
def SavePoseButtonPush(PreAndPost, *args):
    print(PreAndPost)

    # This is the initial inWeight of each Key Tangent
    selected = []
    selected = cmds.ls(sl=1)
    # User did not select anything, issue warning.
    if len(selected) < 1:
        cmds.warning("No object selected.")
        cmds.confirmDialog(title="Warning", message = "No object selected.")
    else:
        #print(initIW)
        print("Pose saved...")
        
        global framesPosed
        alreadyPosed = False

        for i in range(0, len(framesPosed)):
            if cmds.currentTime(query=True) == framesPosed[i]:
                print("This frame has already been posed.")
                alreadyPosed = True
        frameNumber = ""
        if alreadyPosed == False:  
            # Access time slider
            aPlayBackSliderPython = maya.mel.eval('$tmpVar=$gPlayBackSlider')
            # Get the range the user selected
            print(cmds.timeControl(aPlayBackSliderPython,q=True, rangeArray=True))
            theFrames = cmds.timeControl(aPlayBackSliderPython,q=True, rangeArray=True)
            if (PreAndPost and (math.fabs(theFrames[0] - theFrames[1]) > 1)) or (not PreAndPost):
                if PreAndPost and (math.fabs(theFrames[0] - theFrames[1]) > 1):
                    global init
                    global next
                    
                    # Add the first frame to the array of frames that have been posed
                    framesPosed.insert(len(framesPosed), theFrames[0])
                    # The post keyframe to list of post keyframes
                    init.insert(len(next), False)
                    next.insert(len(next), theFrames[1])
                    keyframesWithPreAndPost.insert(len(keyframesWithPreAndPost), True)
                    # Add keyframe that is between pre and post to dictionary
                    PreAndPostInbetweenKey[theFrames[0]] = cmds.findKeyframe(cmds.ls(sl=1), time=(theFrames[0],theFrames[0]), which="next")
                else:
                    # Add current frame to the array of frames that have been posed
                    framesPosed.insert(len(framesPosed), cmds.currentTime(query=True))
                    keyframesWithPreAndPost.insert(len(keyframesWithPreAndPost), False)
                
                cmds.rowLayout( numberOfColumns=2, adjustableColumn=1)
                
                if PreAndPost and (math.fabs(theFrames[0] - theFrames[1]) > 1):
                    frameNumber = str(theFrames[0]).replace(".", "")
                else:
                    # Get the current frame, remove '.' from float to use as UI names
                    frameNumber = str(cmds.currentTime( query=True )).replace(".", "")

                # Checkbox to determine if pose will be stylized
                cmds.checkBox('stylize' + frameNumber, label='Stylize', bgc=[0.75,0.7,0.7], v = True )
                
                # Add delete button
                # The time associated with the pose is passed on differently based on if it was a single or pre and post selection
                if PreAndPost and (math.fabs(theFrames[0] - theFrames[1]) > 1):
                    cmds.button('delete' + frameNumber, label='Delete Pose', bgc=[0.75,0.7,0.7], command = partial(DeleteButtonPush,  theFrames[0]))
                else:
                    cmds.button('delete' + frameNumber, label='Delete Pose', bgc=[0.75,0.7,0.7], command = partial(DeleteButtonPush, cmds.currentTime(query=True)))
                
                cmds.setParent( '..' )
                if PreAndPost and (math.fabs(theFrames[0] - theFrames[1]) > 1):
                    cmds.frameLayout('pose' + frameNumber, label='Pose at frame: ' + str(theFrames[0]) + " - " + str(theFrames[1]), labelAlign='top', cll = True, cl = True )
                else:
                    cmds.frameLayout('pose' + frameNumber, label='Pose at frame: ' + str(cmds.currentTime( query=True )), labelAlign='top', cll = True, cl = True )

                
                global keyable
                keyable = cmds.listAttr(cmds.ls(sl=1), k=True)
                for i in range(0, len(keyable)):
                    if i == 2:
                        cmds.checkBox(keyable[i] + frameNumber, label=keyable[i], v = True )
                    else:
                        cmds.checkBox(keyable[i] + frameNumber, label=keyable[i], v = False )
                    cmds.textField(keyable[i] +"_"+ frameNumber)
                    cmds.textField(keyable[i] +"_"+ frameNumber, edit = True, enable = False, text = str(cmds.getAttr(cmds.ls(sl=1)[0] + "." + keyable[i])))
            else:
                cmds.warning("Make sure you have selected a range of 3 keyframes, using the timeslider: Starting at the 'pre' keyframe, containing a 'middle' keyframe, which will be ignored and ending with the 'post' keyframe.")
                cmds.confirmDialog(title="Warning", message = "Make sure you have selected a range of 3 keyframes, using the timeslider: Starting at the 'pre' keyframe, containing a 'middle' keyframe, which will be ignored and ending with the 'post' keyframe.")
            
        #else:
            #keyable = cmds.listAttr( cmds.ls(sl=1), k=True)  
            #for i in range(0, len(keyable)):
            #    cmds.textField(keyable[i] +"_"+ frameNumber, edit = True, text = str(cmds.getAttr(cmds.ls(sl=1)[0] + "." + keyable[i])))
        cmds.setParent( '..' )
# Callback for when the stylization slider is moved
def stylization_slider_drag_callback(*args):
    #print("Slider Dragged")
    global framesPosed
    #print(framesPosed)
     #cmds.currentTime( query=True )
    for i in range(0, len(framesPosed)):
        currentKeyFrame = framesPosed[i]
        if cmds.checkBox('stylize' + str(framesPosed[i]).replace(".", ""), q = True, value = True) == True:
            global next
            global init
            #print(i)
            #print(len(init))
            if(i == len(init)):
                init.insert(i, True)

            if init[i] == True: 
                next.insert(i, cmds.findKeyframe(cmds.ls(sl=1), time=(currentKeyFrame,currentKeyFrame), which="next"))
                init[i] = False
            global keyable
            # Go through each keyable attribute
            for attribute in range(0, len(keyable)):
                # For each check box that is checked
                if cmds.checkBox(keyable[attribute] + str(framesPosed[i]).replace(".", ""), q = True, value = True) == True:
                    # Pose was set using range slider
                    if keyframesWithPreAndPost[i]: 
                        # Set both
                        SetKeyframes(currentKeyFrame, PreAndPostInbetweenKey[currentKeyFrame], attribute, True)
                        SetKeyframes(PreAndPostInbetweenKey[currentKeyFrame], next[i], attribute, False)
                    # Pose was set with 1 keyframe
                    else:
                         SetKeyframes(currentKeyFrame, next[i], attribute, False)
# interpolation_val slider callback
def interpolation_slider_drag_callback(*args):
    # Changes the number of interpolating keyframes
    # Update value
    global interpolatingKeysCount
    interpolatingKeysCount = cmds.intSliderGrp('interpolation_val', query=True, value = 3)

# Make a new window
window = cmds.window( title="Animation Stylization", iconName='Short Name', widthHeight=(500, 500), sizeable = True)
# Assign a layout
cmds.columnLayout( adjustableColumn=True )
# Add save button for pre only
cmds.button( label='Save Pose using one keyframe only', command=partial(SavePoseButtonPush, False))
# Add save button for pre and post
cmds.button( label='Save Pose using range of keyframes', command=partial(SavePoseButtonPush, True))
# Stylization slider, range = (0 - 5), step = 0.01 
cmds.floatSliderGrp('stylization_val', label='Stylization Value', field=True, minValue=0.0, maxValue=5.0, fieldMinValue=0.0, fieldMaxValue=5.0, step = 0.01, value=0, dc=stylization_slider_drag_callback)
# Number of interpolating keyframes slider
cmds.intSliderGrp('interpolation_val', label='Interpolating keyframes', field=True, minValue=3, maxValue=20, fieldMinValue=3, fieldMaxValue=20, value=3, dc=interpolation_slider_drag_callback)
# Show the window
cmds.showWindow( window )