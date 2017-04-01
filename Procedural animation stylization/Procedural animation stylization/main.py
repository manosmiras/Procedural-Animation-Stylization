import maya.cmds as cmds
import maya.mel as mel
import math
from functools import partial

# TODO: Add post frame when selecting range from timeslider, to next[] list (Half works right now)
# TODO: Dynamic deletion of interpolating keyframes
# TODO: General bug-fixing

# Global variables
framesPosed = []
init = [] # True
nextLoop = []
next = [] # Holds the value of the next keyframe
keyable = []
keys = [] # Interpolation keyframes
normalizedKeys = [] # Interpolation keyframes normalized
interpolatingKeysCount = 3
# https://www.desmos.com/calculator/hamwkcp1rh
def CalculatePos(x, n):
    #decimal.normalize(x)
    #print(str(x))
    #x*=0.01
    #position = math.pow((1 - math.cos(x)), n)
    position = (1 - x) ** n
    #position = 0.9 ** n
    #print("x is: " + str(x))
    #position = math.pow(1 - math.cos(math.pi/2 - x), n)
    return position

def NormalizeKey(interpolationKeyframe, firstKeyFrame, lastKeyFrame):
    return (interpolationKeyframe - firstKeyFrame) / (lastKeyFrame - firstKeyFrame)
    #return interpolationKeyframe * (lastKeyFrame - firstKeyFrame) + firstKeyFrame

def DeleteButtonPush(time, *args):
    global framesPosed
    global nextLoop
    # Remove the given frame from the framesPosed list.
    for i in range(0, len(framesPosed)):
        if (framesPosed[i] == time):
            
            framesPosed.remove(time)
            #nextLoop.pop(i)
            print(str(time) + " was removed.")

    # Remove the UI parts
    cmds.deleteUI('stylize'+ str(time).replace(".", ""))
    cmds.deleteUI('delete'+ str(time).replace(".", ""))
    # This will also delete the children
    cmds.deleteUI('pose'+ str(time).replace(".", ""))

    # TODO: Code to actually remove the keyframes

    #print("time associated with button pressed: " + str(time))

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
        #print("Frames posed: ")
        #print(framesPosed)
        for i in range(0, len(framesPosed)):
            if cmds.currentTime(query=True) == framesPosed[i]:
                print("This frame has already been posed, updating")
                alreadyPosed = True
        
        if alreadyPosed == False:
            # Access time slider
            aPlayBackSliderPython = maya.mel.eval('$tmpVar=$gPlayBackSlider')
            # Get the range the user selected
            print(cmds.timeControl(aPlayBackSliderPython,q=True, rangeArray=True))
            theFrames = cmds.timeControl(aPlayBackSliderPython,q=True, rangeArray=True)

            if PreAndPost:
                # Add the first frame to the array of frames that have been posed
                framesPosed.insert(len(framesPosed), theFrames[0])
            else:
                # Add current frame to the array of frames that have been posed
                framesPosed.insert(len(framesPosed), cmds.currentTime(query=True))

            cmds.rowLayout( numberOfColumns=2, adjustableColumn=1)

            if PreAndPost:
                frameNumber = str(theFrames[0]).replace(".", "")
            else:
                # Get the current frame, remove '.' from float to use as UI names
                frameNumber = str(cmds.currentTime( query=True )).replace(".", "")
            
            cmds.checkBox('stylize' + frameNumber, label='Stylize', bgc=[0.75,0.7,0.7], v = True )

            cmds.button('delete' + frameNumber, label='Delete Pose', bgc=[0.75,0.7,0.7], command = partial(DeleteButtonPush, cmds.currentTime(query=True)))

            cmds.setParent( '..' )
            if PreAndPost:
                cmds.frameLayout('pose' + frameNumber, label='Pose at frame: ' + str(theFrames[0]), labelAlign='top', cll = True, cl = True )
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
            keyable = cmds.listAttr( cmds.ls(sl=1), k=True)  
            for i in range(0, len(keyable)):
                cmds.textField(keyable[i] +"_"+ frameNumber, edit = True, text = str(cmds.getAttr(cmds.ls(sl=1)[0] + "." + keyable[i])))
        cmds.setParent( '..' )
    
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
                    
                    # 'Pre' keyframe
                    currentKeyFrameVal = cmds.keyframe(cmds.ls(sl=1), q = True, vc = 1, t = (currentKeyFrame, currentKeyFrame), at = keyable[attribute])
                    # 'Post' keyframe
                    nextKeyFrameVal = cmds.keyframe(cmds.ls(sl=1), q = True, vc = 1, t = (next[i], next[i]), at = keyable[attribute])

                    maxY = 0
                    minY = 0
                    # Used for 'de-normalization'
                    maxY = currentKeyFrameVal[0]
                    minY = nextKeyFrameVal[0]
    
                    global keys
                    global normalizedKeys
                    global interpolatingKeysCount
                    # Set size of lists
                    keys = [None] * interpolatingKeysCount
                    normalizedKeys = [None] * interpolatingKeysCount

                    for currentKey in range (0, interpolatingKeysCount):
                        if currentKey == 0:
                            # Middle
                            keys[currentKey] = (currentKeyFrame + next[i]) / 2
                        else:
                            # Even
                            if currentKey % 2 == 0:
                                # Right side
                                keys[currentKey] = (keys[currentKey - 2] + next[i]) / 2
                            # Odd
                            else:
                                if currentKey == 1:
                                    # Left side
                                    keys[currentKey] = (currentKeyFrame + keys[currentKey - 1]) / 2
                                else:
                                    keys[currentKey] = (currentKeyFrame + keys[currentKey - 2]) / 2
                            # Normalize
                        normalizedKeys[currentKey] = NormalizeKey(keys[currentKey], currentKeyFrame, next[i])
                           
                    #print(normalizedKeys)

                    valueFromSlider = cmds.floatSliderGrp('stylization_val', query=True, value = 1)

                    # Update number of keys specified by slider
                    for currentKey in range (0, interpolatingKeysCount):
                        cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v = CalculatePos(normalizedKeys[currentKey], valueFromSlider) * (maxY - minY) + minY, t = (keys[currentKey], keys[currentKey]), itt = "spline", ott = "spline" )

                    # TODO
                    print("Gonna delete from :" + str(cmds.findKeyframe(cmds.ls(sl=1), at = keyable[attribute], t = (keys[interpolatingKeysCount - 1], keys[interpolatingKeysCount - 1]), which = "next")) + " to " + str(cmds.findKeyframe(cmds.ls(sl=1), at = keyable[attribute], t = (next[i], next[i]), which = "previous")))

                    # Should delete right side...
                    #cmds.cutKey(cmds.ls(sl=1), at = keyable[attribute], t = (keys[interpolatingKeysCount - 1], cmds.findKeyframe(next[i], which = "previous")), clear = True)

def interpolation_slider_drag_callback(*args):
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

cmds.floatSliderGrp('stylization_val', label='Stylization Value', field=True, minValue=0.0, maxValue=30.0, fieldMinValue=0.0, fieldMaxValue=30.0, value=0, dc=stylization_slider_drag_callback)
cmds.intSliderGrp('interpolation_val', label='Number of interpolating keyframes', field=True, minValue=3, maxValue=30, fieldMinValue=3, fieldMaxValue=30, value=3, dc=interpolation_slider_drag_callback)
# Show the window
cmds.showWindow( window )