import maya.cmds as cmds
import maya.mel as mel
initIW = []
framesPosed = []
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

def CartoonifyButtonPush(*args):
    print("Cartoonifying...")
    #print(cmds.currentTime( query=True ))
    #Selects all the keys in the graph editor
    #cmds.selectKey( cmds.ls(sl=1), time=())
    #cmds.findKeyframe( timeSlider=True, which="next" )
    #cmds.keyTangent(cmds.ls(sl=1), edit = True, iw = 10)
    currentKeyFrame = cmds.currentTime( query=True )
    next = cmds.findKeyframe( timeSlider=True, which="next")
    previous = cmds.findKeyframe( timeSlider=True, which="previous")
    # Set the inWeights and outWeights of the pose to 0
    valueFromSlider = cmds.floatSliderGrp('float', query=True, value = 1)
    print(cmds.keyTangent(cmds.ls(sl=1), edit = True, time = (previous, next), attribute = 'translateY', outWeight = valueFromSlider * 10))
    print(cmds.keyTangent(cmds.ls(sl=1), edit = True, time = (previous, next), attribute = 'translateY', inWeight = valueFromSlider * 10))
    cmds.keyTangent(cmds.ls(sl=1), edit = True, time = (currentKeyFrame, currentKeyFrame), attribute = 'translateY', itt = 'flat', ott = 'flat')
    #if valueFromSlider==1.0:
        
    


def ResetButtonPush(*args):
    print("Resetting the values")
    print(initIW)
    for i in range(len(initIW)):
        print(i)
        cmds.keyTangent(cmds.ls(sl=1), edit = True, index = (i, i), iw = float(initIW[i]))
    

# Make a new window
window = cmds.window( title="Animation Stylization", iconName='Short Name', widthHeight=(500, 500) )
# Assign a layout
cmds.columnLayout( adjustableColumn=True )

# Add a button
cmds.button( label='Save Pose', command=SavePoseButtonPush)
# Add a button
cmds.button( label='Cartoonify', command=CartoonifyButtonPush)
cmds.floatSliderGrp('float', label='Cartoonification Value', field=True, minValue=0.0, maxValue=1.0, fieldMinValue=0.0, fieldMaxValue=1.0, value=0.5 )
# Add a button
cmds.button( label='Reset', command=ResetButtonPush)



# Show the window
cmds.showWindow( window )