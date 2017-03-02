import maya.cmds as cmds
import maya.mel as mel
import math
initIW = []
framesPosed = []
init = True
next = 0 # Holds the value of the next keyframe
# https://www.desmos.com/calculator/hamwkcp1rh
def calculatePos(x, n):
    position = math.pow((1 - math.cos(x)), n)
    #position = (1 - x + 0j) ** n
    #position = math.pow(1 - math.cos(math.pi/2 - x), n)
    return position

def SavePoseButtonPush(*args):
    
    # This is the initial inWeight of each Key Tangent
    selected = []
    selected = cmds.ls(sl=1)
    if len(selected) < 1:
        cmds.warning("No object selected.")
    else:
        global initIW
        initIW = cmds.keyTangent(cmds.ls(sl=1), query = True, iw = 1)
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
            # Add current frame to the list of frames that have been posed
            
            framesPosed.insert(0, cmds.currentTime(query=True))
            print(framesPosed)
            #cmds.text( label='Pose at frame: ' + str(cmds.currentTime( query=True )), bgc=[1,0,0])
            cmds.button( label='Pose at frame: ' + str(cmds.currentTime( query=True )), command=SavePoseButtonPush)
            #cmds.columnLayout( adjustableColumn=True )
            #cmds.frameLayout( label='Pose at frame: ' + str(cmds.currentTime( query=True )), labelAlign='top', borderStyle='in' )
            #cmds.columnLayout()

            keyable = cmds.listAttr(cmds.ls(sl=1), k=True)
            for i in range(0, len(keyable)):
                cmds.checkBox( label=keyable[i] )
                cmds.textField(keyable[i] +"_"+ str(int(cmds.currentTime( query=True ))))
                cmds.textField(keyable[i] +"_"+ str(int(cmds.currentTime( query=True ))), edit = True, enable = False, text = str(cmds.getAttr(cmds.ls(sl=1)[0] + "." + keyable[i])))

        else:
            keyable = cmds.listAttr( cmds.ls(sl=1), k=True)  
            for i in range(0, len(keyable)):
                cmds.textField(keyable[i] +"_"+ str(int(cmds.currentTime( query=True ))), edit = True, text = str(cmds.getAttr(cmds.ls(sl=1)[0] + "." + keyable[i])))

def ResetButtonPush(*args):
    print("Resetting the values")
    print(initIW)
    for i in range(len(initIW)):
        print(i)
        cmds.keyTangent(cmds.ls(sl=1), edit = True, index = (i, i), iw = float(initIW[i]))

def slider_drag_callback(*args):
    print("Slider Dragged")
    global framesPosed
    print(framesPosed)
    currentKeyFrame = framesPosed[0] #cmds.currentTime( query=True )
    global next
    global init
    if init == True: 
        next = cmds.findKeyframe(cmds.ls(sl=1), time=(framesPosed[0],framesPosed[0]), which="next")
        init = False
    #previous = cmds.findKeyframe(cmds.ls(sl=1), time=(framesPosed[0],framesPosed[0]), which="previous")
    #key1 = 0
    #if (len(framesPosed) > 0):
    
    key1 = (currentKeyFrame + next) / 2
    key2 = (currentKeyFrame + key1) / 2
    key3 = (key1 + next) / 2
    print("key1 is: " + str(key1))
    print("key2 is: " + str(key2))
    print("key3 is: " + str(key3))

    valueFromSlider = cmds.floatSliderGrp('float', query=True, value = 1)
    # print(calculatePos(key1, valueFromSlider))
    cmds.setKeyframe( cmds.ls(sl=1), at = 'translateY', v=float(calculatePos(key1, valueFromSlider)), t = (key1, key1), itt = "spline", ott = "spline" )
    cmds.setKeyframe( cmds.ls(sl=1), at = 'translateY', v=float(calculatePos(key2, valueFromSlider)), t = (key2, key2), itt = "spline", ott = "spline" )
    cmds.setKeyframe( cmds.ls(sl=1), at = 'translateY', v=float(calculatePos(key3, valueFromSlider)), t = (key3, key3), itt = "spline", ott = "spline" )
    #cmds.setAttr()
    #cmds.keyTangent(cmds.ls(sl=1), edit = True, time = (previous, next), attribute = 'translateY', outWeight = valueFromSlider * 10)
    #cmds.keyTangent(cmds.ls(sl=1), edit = True, time = (previous, next), attribute = 'translateY', inWeight = valueFromSlider * 10)
    #cmds.keyTangent(cmds.ls(sl=1), edit = True, time = (currentKeyFrame, currentKeyFrame), attribute = 'translateY', itt = 'flat', ott = 'flat')
    #if valueFromSlider==1.0:

# Make a new window
window = cmds.window( title="Animation Stylization", iconName='Short Name', widthHeight=(500, 500) )
# Assign a layout
cmds.columnLayout( adjustableColumn=True )

# Add a button
cmds.button( label='Save Pose', command=SavePoseButtonPush)

cmds.floatSliderGrp('float', label='Cartoonification Value', field=True, minValue=-10.0, maxValue=10.0, fieldMinValue=-10.0, fieldMaxValue=10.0, value=0, dc=slider_drag_callback)
# Add a button
cmds.button( label='Reset', command=ResetButtonPush)

# Show the window
cmds.showWindow( window )