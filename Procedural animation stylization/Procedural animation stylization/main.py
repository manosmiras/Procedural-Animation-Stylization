import maya.cmds as cmds
import maya.mel as mel
import math
framesPosed = []
init = []#True
nextLoop = []
next = [] # Holds the value of the next keyframe
keyable = []
# https://www.desmos.com/calculator/hamwkcp1rh
def CalculatePos(x, n):
    #decimal.normalize(x)
    #print(str(x))
    #x*=0.01
    #position = math.pow((1 - math.cos(x)), n)
    position = (1 - x ) ** n
    #position = 0.9 ** n
    print("x is: " + str(x))
    #position = math.pow(1 - math.cos(math.pi/2 - x), n)
    return position

def NormalizeKey(interpolationKeyframe, firstKeyFrame, lastKeyFrame):
    return (interpolationKeyframe - firstKeyFrame) / (lastKeyFrame - firstKeyFrame)
    #return interpolationKeyframe * (lastKeyFrame - firstKeyFrame) + firstKeyFrame

def SavePoseButtonPush(*args):
    
    # This is the initial inWeight of each Key Tangent
    selected = []
    selected = cmds.ls(sl=1)
    if len(selected) < 1:
        cmds.warning("No object selected.")
    else:
        #print(initIW)
        print("Pose saved...")
        
        global framesPosed
        alreadyPosed = False
        print("Frames posed: ")
        print(framesPosed)
        for i in range(0, len(framesPosed)):
            if cmds.currentTime(query=True) == framesPosed[i]:
                print("This frame has already been posed, updating")
                alreadyPosed = True
        
        if alreadyPosed == False:
            # Add current frame to the array of frames that have been posed
            # Adds to end of array
            framesPosed.insert(len(framesPosed), cmds.currentTime(query=True))
            print(framesPosed)
            #cmds.text( label='Pose at frame: ' + str(cmds.currentTime( query=True )), bgc=[1,0,0])
            #cmds.button( label='Pose at frame: ' + str(cmds.currentTime( query=True )), command=SavePoseButtonPush)
            #cmds.columnLayout( adjustableColumn=True )
            cmds.checkBox('stylize' + str(int(cmds.currentTime( query=True ))), label='Stylize', bgc=[0.75,0.7,0.7], v = True )
            cmds.frameLayout('pose' + str(int(cmds.currentTime( query=True ))), label='Pose at frame: ' + str(cmds.currentTime( query=True )), labelAlign='top', cll = True, cl = True )
            global keyable
            keyable = cmds.listAttr(cmds.ls(sl=1), k=True)
            for i in range(0, len(keyable)):
                if i == 2:
                    cmds.checkBox(keyable[i] + str(int(cmds.currentTime( query=True ))), label=keyable[i], v = True )
                else:
                    cmds.checkBox(keyable[i] + str(int(cmds.currentTime( query=True ))), label=keyable[i], v = False )
                cmds.textField(keyable[i] +"_"+ str(int(cmds.currentTime( query=True ))))
                cmds.textField(keyable[i] +"_"+ str(int(cmds.currentTime( query=True ))), edit = True, enable = False, text = str(cmds.getAttr(cmds.ls(sl=1)[0] + "." + keyable[i])))

        else:
            keyable = cmds.listAttr( cmds.ls(sl=1), k=True)  
            for i in range(0, len(keyable)):
                cmds.textField(keyable[i] +"_"+ str(int(cmds.currentTime( query=True ))), edit = True, text = str(cmds.getAttr(cmds.ls(sl=1)[0] + "." + keyable[i])))
        cmds.setParent( '..' )

def slider_drag_callback(*args):
    print("Slider Dragged")
    global framesPosed
    print(framesPosed)
     #cmds.currentTime( query=True )
    for i in range(0, len(framesPosed)):
        currentKeyFrame = framesPosed[i]
        if cmds.checkBox('stylize' + str(int(framesPosed[i])), q = True, value = True) == True:
            global next
            global init
            print(i)
            print(len(init))
            if(i == len(init)):
                init.insert(i, True)

            if init[i] == True: 
                next.insert(i, cmds.findKeyframe(cmds.ls(sl=1), time=(currentKeyFrame,currentKeyFrame), which="next"))
                init[i] = False
            global keyable
            # Go through each keyable attribute
            for attribute in range(0, len(keyable)):
                # For each check box that is checked
                if cmds.checkBox(keyable[attribute] + str(int(framesPosed[i])), q = True, value = True) == True:
                    
                    #print(keyable)
                    # Get value of currentKeyFrame
                    currentKeyFrameVal = cmds.keyframe(cmds.ls(sl=1), q = True, vc = 1, t = (currentKeyFrame, currentKeyFrame), at = keyable[attribute])
                    nextKeyFrameVal = cmds.keyframe(cmds.ls(sl=1), q = True, vc = 1, t = (next[i], next[i]), at = keyable[attribute])
                    distance = nextKeyFrameVal[0] - currentKeyFrameVal[0]
                    #print(currentKeyFrameVal)

                    
                    # Put keyframe one after current
                    key2 = (currentKeyFrame + next[i]) / 2 #currentKeyFrame + 1 #(currentKeyFrame + key1) / 2
                    key1 = (currentKeyFrame + key2) / 2
                    # Put keyframe one before next
                    key3 = (key2 + next[i]) / 2

                    valueFromSlider = cmds.floatSliderGrp('float', query=True, value = 1)
                    #print("value from slider is: " + str(valueFromSlider))
                    print("key1 is: " + str(key1), ", normalized: " + str(NormalizeKey(key1, currentKeyFrame, next[i])))
                    print("key2 is: " + str(key2), ", normalized: " + str(NormalizeKey(key2, currentKeyFrame, next[i])))
                    print("key3 is: " + str(key3), ", normalized: " + str(NormalizeKey(key3, currentKeyFrame, next[i])))
                   
                    # Normalize the keyframes
                    normalKey1 = NormalizeKey(key1, currentKeyFrame, next[i])
                    normalKey2 = NormalizeKey(key2, currentKeyFrame, next[i])
                    normalKey3 = NormalizeKey(key3, currentKeyFrame, next[i])

                    # Set the keyframe values (For some reason, adding the value of normalKey3 as an input value to the CalculatePos function, 
                    # for the frame key1 and vice versa, makes the system behave in the way originally expected.)
                    cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=currentKeyFrameVal[0] + CalculatePos(normalKey3, valueFromSlider) * distance, t = (key1, key1), itt = "spline", ott = "spline" )
                    cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=currentKeyFrameVal[0] + CalculatePos(normalKey2, valueFromSlider) * distance, t = (key2, key2), itt = "spline", ott = "spline" )
                    cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=currentKeyFrameVal[0] + CalculatePos(normalKey1, valueFromSlider) * distance, t = (key3, key3), itt = "spline", ott = "spline" )

                    #if distance > 0:
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=CalculatePos(key1, valueFromSlider) * distance - distance / 1.5, t = (key1, key1), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=CalculatePos(key2, valueFromSlider) * distance - distance / 3, t = (key2, key2), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=CalculatePos(key3, valueFromSlider) * distance - distance / 4, t = (key3, key3), itt = "spline", ott = "spline" )
                        
                         
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=currentKeyFrameVal[0] + CalculatePos(normalKey3, valueFromSlider) * distance, t = (key1, key1), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=currentKeyFrameVal[0] + CalculatePos(normalKey2, valueFromSlider) * distance, t = (key2, key2), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=currentKeyFrameVal[0] + CalculatePos(normalKey1, valueFromSlider) * distance, t = (key3, key3), itt = "spline", ott = "spline" )
                   #else:
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=CalculatePos(key1, valueFromSlider) * (-distance) + distance / 4, t = (key1, key1), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=CalculatePos(key2, valueFromSlider) * (-distance) + distance / 3, t = (key2, key2), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=CalculatePos(key3, valueFromSlider) * (-distance) + distance / 1.5, t = (key3, key3), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=currentKeyFrameVal[0] + CalculatePos(normalKey1, valueFromSlider) * (distance), t = (key1, key1), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=currentKeyFrameVal[0] + CalculatePos(normalKey2, valueFromSlider) * (distance), t = (key2, key2), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = keyable[attribute], v=currentKeyFrameVal[0] + CalculatePos(normalKey3, valueFromSlider) * (distance), t = (key3, key3), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = 'translateY', v=calculatePos(key2, valueFromSlider) * (-distance), t = (key2, key2), itt = "spline", ott = "spline" )
                        #cmds.setKeyframe( cmds.ls(sl=1), at = 'translateY', v=calculatePos(key3, valueFromSlider) * (-distance) - (currentKeyFrameVal[0] - distance)/4, t = (key3, key3), itt = "spline", ott = "spline" )


# Make a new window
window = cmds.window( title="Animation Stylization", iconName='Short Name', widthHeight=(500, 500) )
# Assign a layout
cmds.columnLayout( adjustableColumn=True )
# Add a button
cmds.button( label='Save Pose', command=SavePoseButtonPush)

cmds.floatSliderGrp('float', label='Stylization Value', field=True, minValue=0.0, maxValue=30.0, fieldMinValue=0.0, fieldMaxValue=30.0, value=0, dc=slider_drag_callback)

# Show the window
cmds.showWindow( window )