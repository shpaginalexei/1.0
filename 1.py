#Author-
#Description-
import adsk.core, adsk.fusion, adsk.cam, traceback
import math

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)

# Command inputs
_Image = adsk.core.ImageCommandInput.cast(None)
#_RestartValueButton = adsk.core.BoolValueCommandInput.cast(None)
_WhatGear = adsk.core.ButtonRowCommandInput.cast(None)
_Joints = adsk.core.BoolValueCommandInput.cast(None)
_PinionNumTeeth = adsk.core.StringValueCommandInput.cast(None)
_WheelNumTeeth = adsk.core.StringValueCommandInput.cast(None)
_Module = adsk.core.ValueInput.cast(None)
_PressureAngle = adsk.core.DropDownCommandInput.cast(None)
_ToothWidthDefault = adsk.core.BoolValueCommandInput.cast(None)
_ToothWidth = adsk.core.ValueInput.cast(None)
_Backlash = adsk.core.ValueInput.cast(None)
_errMessage = adsk.core.TextBoxCommandInput.cast(None)

# Example values
ExampleValues = {
    'WhatGear': ['Both Gears', 2],
    'Position' : 'One',
    'Joints': False,
    'PinionNumTeeth': '18',
    'WheelNumTeeth': '20',
    'Module': 0.5,
    'PressureAngle' : ['20 deg', 1],
    'ToothWidthDefault' : True,
    'ToothWidth': 2,
    'Backlash': 0
}

handlers = []

def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        
        
        cmdDef = _ui.commandDefinitions.itemById('BevelGearPythonScript')
        if not cmdDef:
            # Create a command definition.
            cmdDef = _ui.commandDefinitions.addButtonDefinition('BevelGearPythonScript', 'Bevel Gear Creator', 'Creates a pair of bevel gears', 'resources')
        
        # Connect to the command created event.
        onCommandCreated = GearCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)
        
        # Execute the command.
        cmdDef.execute()

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)

    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the commandCreated event.
class GearCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs
            design = adsk.fusion.Design.cast(_app.activeProduct)
            rootComp = design.rootComponent

            #
            global _Image, _RestartValueButton, _WhatGear, _Joints, _PinionNumTeeth, _WheelNumTeeth, _Module, _PressureAngle, _ToothWidthDefault, _ToothWidth, _Backlash, _errMessage

            # Creatу a menu for data entry
            _Image = inputs.addImageCommandInput('Image', '', "resources/image.png")
            _Image.isFullWidth = True

            _RestartValueButton = inputs.addBoolValueInput('RestartValueButton', 'Restart Value', False, 'resources/_Restart/version4', True)

            _WhatGear = inputs.addButtonRowCommandInput('WhatGear', 'Pinion/Wheel/Both Gears', False)
            if ExampleValues['WhatGear'][0] == 'Pinion':
                _WhatGear.listItems.add('Pinion', True, 'resources/_WhatGear/pinion')
            else:
                _WhatGear.listItems.add('Pinion', False, 'resources/_WhatGear/pinion')

            if ExampleValues['WhatGear'][0] == 'Wheel':
                _WhatGear.listItems.add('Wheel', True, 'resources/_WhatGear/whell')
            else:
                _WhatGear.listItems.add('Wheel', False, 'resources/_WhatGear/whell')

            if ExampleValues['WhatGear'][0] == 'Both Gears':
                _WhatGear.listItems.add('Both Gears', True, 'resources/_WhatGear/both')
            else:
                _WhatGear.listItems.add('Both Gears', False, 'resources/_WhatGear/both')

            _Joints = inputs.addBoolValueInput('Joints', 'Add joints?', True, '', ExampleValues['Joints'])
            if _WhatGear.selectedItem.name != 'Both Gears':
                _Joints.isEnabled = False
            else:
                _Joints.isEnabled = True

            _PinionNumTeeth = inputs.addStringValueInput('PinionNumTeeth', 'Pinion NumTeeth', ExampleValues['PinionNumTeeth'])
            _WheelNumTeeth = inputs.addStringValueInput('WheelNumTeeth', 'Wheel NumTeeth', ExampleValues['WheelNumTeeth'])
            _Module = inputs.addValueInput('Module', 'Module', 'mm', adsk.core.ValueInput.createByReal(ExampleValues['Module']))

            _PressureAngle = inputs.addDropDownCommandInput('PressureAngle', 'Pressure Angle', adsk.core.DropDownStyles.TextListDropDownStyle)
            _PressureAngleItems = _PressureAngle.listItems
            if ExampleValues['PressureAngle'][0] == '14.5 deg':
                _PressureAngleItems.add('14.5 deg', True, '')
            else:
                _PressureAngleItems.add('14.5 deg', False, '')

            if ExampleValues['PressureAngle'][0] == '20 deg':
                _PressureAngleItems.add('20 deg', True, '')
            else:
                _PressureAngleItems.add('20 deg', False, '')

            if ExampleValues['PressureAngle'][0] == '25 deg':
                _PressureAngleItems.add('25 deg', True, '')
            else:
                _PressureAngleItems.add('25 deg', False, '')


            _ToothWidthDefault = inputs.addBoolValueInput('ToothWidth', 'Default Tooth Width?', True, '', ExampleValues['ToothWidthDefault'])
            _ToothWidth = inputs.addValueInput('ToothWidthCustom', 'Tooth Width', 'mm', adsk.core.ValueInput.createByReal(ExampleValues['ToothWidth']))
            if _ToothWidthDefault.value:
                _ToothWidth.isEnabled = False
            else:
                _ToothWidth.isEnabled = True

            _Backlash = inputs.addValueInput('Backlash', 'Backlash', 'mm', adsk.core.ValueInput.createByReal(ExampleValues['Backlash']))
            _Backlash.isEnabled = False

            _errMessage = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
            #

            # Connect to the command related events.
            onValidateInputs = GearCommandValidateInputsHandler()
            cmd.validateInputs.add(onValidateInputs)
            handlers.append(onValidateInputs)
            
            onInputChanged = GearCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            handlers.append(onInputChanged)

            onExecute = GearCommandExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)

            onDestroy = GearCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            handlers.append(onDestroy)
            #

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the inputChanged event.
class GearCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input

            #
            if changedInput.id == 'WhatGear':
                if _WhatGear.selectedItem.name != 'Both Gears':
                    _Joints.isEnabled = False
                else:
                    _Joints.isEnabled = True

            if changedInput.id == 'PinionNumTeeth' or changedInput.id == 'WheelNumTeeth' or changedInput.id == 'Module':
                if _PinionNumTeeth.value.isdigit() and _WheelNumTeeth.value.isdigit():
                    _ToothWidth.value = CalcToothWidth(int(_PinionNumTeeth.value), int(_WheelNumTeeth.value), _Module.value)
                

            if changedInput.id == 'ToothWidth':
                if _ToothWidthDefault.value:
                    _ToothWidth.isEnabled = False
                    if _PinionNumTeeth.value.isdigit() and _WheelNumTeeth.value.isdigit():
                        _ToothWidth.value = CalcToothWidth(int(_PinionNumTeeth.value), int(_WheelNumTeeth.value), _Module.value)
                else:
                    _ToothWidth.isEnabled = True

            if changedInput.id == 'RestartValueButton':
                _WhatGear.selectedItem.isSelected = False
                _WhatGear.listItems.item(ExampleValues['WhatGear'][1]).isSelected = True
                _Joints.isEnabled = True
                _Joints.value = ExampleValues['Joints']
                _PinionNumTeeth.value = ExampleValues['PinionNumTeeth']
                _WheelNumTeeth.value = ExampleValues['WheelNumTeeth']
                _Module.unitType = 'mm'
                _Module.value = ExampleValues['Module']
                _PressureAngle.listItems.item(ExampleValues['PressureAngle'][1]).isSelected = True
                _ToothWidthDefault.value = ExampleValues['ToothWidthDefault']
                _ToothWidth.unitType = 'mm'
                _ToothWidth.value = ExampleValues['ToothWidth']
                _ToothWidth.isEnabled = False
                _Backlash.unitType = 'mm'
                _Backlash.value = ExampleValues['Backlash']
            #

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the validateInputs event.
class GearCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)
            
            _errMessage.text = ''
            #
            if not _PinionNumTeeth.value.isdigit() or not _WheelNumTeeth.value.isdigit():
                _errMessage.text = 'The number of teeth must be a whole number.'
                if not _PinionNumTeeth.value.isdigit():
                    _errMessage.text += ' {' + _PinionNumTeeth.name + '}'
                if not _WheelNumTeeth.value.isdigit():
                    _errMessage.text += ' {' + _WheelNumTeeth.name + '}'
                eventArgs.areInputsValid = False
                return
            else:
                PinionNumTeeth = int(_PinionNumTeeth.value)
                WheelNumTeeth = int(_WheelNumTeeth.value)
            
            if PinionNumTeeth < 8 or WheelNumTeeth < 8:
                _errMessage.text = 'The number of teeth must be 8 or more.'
                if PinionNumTeeth < 8:
                    _errMessage.text += ' {' + _PinionNumTeeth.name + '}'
                if WheelNumTeeth < 8:
                    _errMessage.text += ' {' + _WheelNumTeeth.name + '}'
                eventArgs.areInputsValid = False
                return
            

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the execute event.
class GearCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            #
            design = adsk.fusion.Design.cast(_app.activeProduct)

            WhatGear = _WhatGear.selectedItem.name
            if WhatGear == 'Both Gears':
                Joints = _Joints.value
            else:
                Joints = False
            PinionNumTeeth = int(_PinionNumTeeth.value)
            WheelNumTeeth = int(_WheelNumTeeth.value)
            Module = _Module.value
            if _PressureAngle.selectedItem.name == '14.5 deg':
                PressureAngle = 14.5 * math.pi / 180
            elif _PressureAngle.selectedItem.name == '20 deg':
                PressureAngle = 20 * math.pi / 180
            elif _PressureAngle.selectedItem.name == '25 deg':
                PressureAngle = 25 * math.pi / 180
            ToothWidth = _ToothWidth.value
            Backlash = _Backlash.value

            if WhatGear == 'Pinion':
                pinionComp = DrawGears(design, 'Pinion', Joints, PinionNumTeeth, WheelNumTeeth, Module, PressureAngle, ToothWidth, Backlash, False)
                wheelComp = None
            elif WhatGear == 'Wheel':
                pinionComp = None
                wheelComp = DrawGears(design, 'Wheel', Joints, PinionNumTeeth, WheelNumTeeth, Module, PressureAngle, ToothWidth, Backlash, False)
            else:
                foo = design.rootComponent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
                foo.isGrounded = True

                pinionComp = DrawGears(foo, design, 'Pinion', Joints, PinionNumTeeth, WheelNumTeeth, Module, PressureAngle, ToothWidth, Backlash, True)
                pinionComp.isBodiesFolderLightBulbOn = False
                wheelComp = DrawGears(foo, design, 'Wheel', Joints, PinionNumTeeth, WheelNumTeeth, Module, PressureAngle, ToothWidth, Backlash, False)
                pinionComp.isBodiesFolderLightBulbOn = True

                
            #

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class GearCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def CalcToothWidth(PinionNumTeeth, WheelNumTeeth, Module):
    VerticesConeDist = 0.5 * Module * math.sqrt(math.pow(PinionNumTeeth, 2) + math.pow(WheelNumTeeth, 2))
    ToothWidth = int(0.3 * VerticesConeDist * 10) / 10
    return ToothWidth

def addDistantionDimension(dimensions, startSketchPoint, endSketchPoint, orientation):
    startPoint = startSketchPoint.geometry
    endPoint = endSketchPoint.geometry
    (startReturnValue, startX, startY, startZ) = startPoint.getData()
    (endReturnValue, endX, endY, endZ) = endPoint.getData()
    if orientation == 0:
        if startX > endX:
            distPointX = (startX - endX) / 2 + endX 
        else: 
            distPointX = (endX - startX) / 2 + startX 
                
        if startY > endY:
            distPointY = (startY - endY) / 2 + endY 
        else:
            distPointY = (endY - startY) / 2 + startY 
    elif orientation == 1:
        if startY > endY:
            distPointY = startY 
        else: 
            distPointY = endY 
        if startX > endX:
            distPointX = (startX - endX) / 2 + endX 
        else:
            distPointX = (endX - startX) / 2 + startX 
    elif orientation == 2:
        if startX > endX:
            distPointX = startX 
        else:
            distPointX = endX 

        if startY > endY:
            distPointY = (startY - endY) / 2 + endY 
        else:
            distPointY = (endY - startY) / 2 + startY
    else:
        _ui.messageBox('F A I L:\n{}addDistantionDimension is failed.')

    distPoint = adsk.core.Point3D.create(distPointX, distPointY, 0)
    dimensions.addDistanceDimension(startSketchPoint, endSketchPoint, orientation, distPoint)

def involutePoint(baseCircleRadius, argument, deltaX, deltaY):
    try:
        # Calculate the coordinates of the involute point
        x = baseCircleRadius * (math.cos(argument) + argument * math.sin(argument)) + deltaX
        y = baseCircleRadius * (math.sin(argument) - argument * math.cos(argument)) + deltaY

        # Create a point to return
        return adsk.core.Point3D.create(x, y, 0)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

#"range()" like function which accept float type
def frange(start, stop, _step):
    i = start
    while i < stop:
        yield i
        i += _step

def DrawGears(foo, design, WhatDraw, Joints, PinionNumTeeth, WheelNumTeeth, Module, PressureAngle, ToothWidth, Backlash, Rotate):

    # ----------Create a new component by creating an occurrence---------- #
    occs = design.rootComponent.occurrences
    mat = adsk.core.Matrix3D.create()
    newOcc = occs.addNewComponent(mat)
    newComp = adsk.fusion.Component.cast(newOcc.component)
    if WhatDraw == 'Pinion':
        newComp.name = 'Pinion'
    else:
        newComp.name = 'Wheel'

    # ----------Calculate values---------- #
    if WhatDraw == 'Pinion':
        PitchConeAngle = math.atan(PinionNumTeeth / WheelNumTeeth)
        OuterPitchDiameter = Module * PinionNumTeeth
    else:
        PitchConeAngle = math.atan(WheelNumTeeth / PinionNumTeeth)
        OuterPitchDiameter = Module * WheelNumTeeth
    PitchCircleDiameter = OuterPitchDiameter / math.cos(PitchConeAngle)

    ToothHeadHeight = 1.0 * Module
    ToothLegHeight = 1.2 * Module

    PitchCircleRadius = PitchCircleDiameter / 2
    OuterPitchRadius = OuterPitchDiameter / 2
    VerticesCircleRadius = (PitchCircleDiameter + 2 * ToothHeadHeight) / 2
    RecessCircleRadius = (PitchCircleDiameter - 2 * ToothLegHeight) / 2
    BaseCircleRadius = (OuterPitchDiameter * math.cos(PressureAngle) / math.cos(PitchConeAngle)) / 2

    sin = math.sin(PitchConeAngle)
    sin2 = math.sin(2 * PitchConeAngle)
    cos = math.cos(PitchConeAngle)
    tan = math.tan(PitchConeAngle)

    # -----------D R A W   S K E T C H _ 1---------- #

    # ----------Create a new sketch on the YZ plane---------- #
    sketches = newComp.sketches
    yzPlane = newComp.yZConstructionPlane
    sketch1 = sketches.add(yzPlane)

    # -----------Add collections to sketch1---------- #
    sketchPoints = sketch1.sketchPoints
    lines = sketch1.sketchCurves.sketchLines
    constraints = sketch1.geometricConstraints
    dimensions = sketch1.sketchDimensions

    # -----------Creating points and lines to a sketch1---------- #
    point1 = adsk.core.Point3D.create(OuterPitchDiameter / sin2, 0, 0)
    sketchPoint1 = sketchPoints.add(point1)

    line1 = lines.addByTwoPoints(sketch1.originPoint, sketchPoint1)
    line1.isConstruction = True
    #constraints.addHorizontal(line1)

    point2 = adsk.core.Point3D.create(OuterPitchRadius / tan, OuterPitchRadius, 0)
    sketchPoint2 = sketchPoints.add(point2)

    line2 = lines.addByTwoPoints(sketch1.originPoint, sketchPoint2)
    line2.isConstruction = True

    #dimensions.addAngularDimension(line2, line1, adsk.core.Point3D.create(1, tan / 2, 0))
    #addDistantionDimension(dimensions, sketch1.originPoint, sketchPoint2, 2)

    point3 = adsk.core.Point3D.create(point1.getData()[1] - VerticesCircleRadius * sin, VerticesCircleRadius * cos, 0)
    sketchPoint3 = sketchPoints.add(point3)

    line3 = lines.addByTwoPoints(sketchPoint1, sketchPoint3)
    line3.isConstruction = True

    #constraints.addCoincident(sketchPoint2, line3)
    #constraints.addPerpendicular(line2, line3)

    line4 = lines.addByTwoPoints(sketch1.originPoint, sketchPoint3)
    line4.isConstruction = True

    #addDistantionDimension(dimensions, sketchPoint2, sketchPoint3, 0)
        
    point4 = adsk.core.Point3D.create(point1.getData()[1] - RecessCircleRadius * sin, RecessCircleRadius * cos, 0)
    sketchPoint4 = sketchPoints.add(point4)

    #constraints.addCoincident(sketchPoint4, line3)

    line5 = lines.addByTwoPoints(sketch1.originPoint, sketchPoint4)
    line5.isConstruction = True

    #addDistantionDimension(dimensions, sketchPoint2, sketchPoint4, 0)

    point5Radius = RecessCircleRadius - ToothLegHeight - ToothHeadHeight
    point5 = adsk.core.Point3D.create(point1.getData()[1] - point5Radius * sin, point5Radius * cos, 0)
    sketchPoint5 = sketchPoints.add(point5)

    line6 = lines.addByTwoPoints(sketch1.originPoint, sketchPoint5)
    line6.isConstruction = True

    line7 = lines.addByTwoPoints(sketchPoint3, sketchPoint5)

    #constraints.addMidPoint(sketchPoint4, line7)

    VerticesConeAngle = PitchConeAngle + math.atan((ToothHeadHeight * sin) / OuterPitchRadius)
    point6 = adsk.core.Point3D.create(point3.getData()[1] - ToothWidth * math.cos(VerticesConeAngle), point3.getData()[2] - ToothWidth * math.sin(VerticesConeAngle), 0)
    sketchPoint6 = sketchPoints.add(point6)

    #constraints.addCoincident(sketchPoint6, line4)

    line8 = lines.addByTwoPoints(sketchPoint3, sketchPoint6)

    #addDistantionDimension(dimensions, sketchPoint3, sketchPoint6, 0)

    point7 = adsk.core.Point3D.create(point5.getData()[1], 0, 0)
    sketchPoint7 = sketchPoints.add(point7)

    #constraints.addCoincident(sketchPoint7, line1)

    line9 = lines.addByTwoPoints(sketchPoint5, sketchPoint7)

    #constraints.addPerpendicular(line9, line1)

    coefficient_k = 1 - (ToothWidth / math.sqrt((math.pow(OuterPitchRadius / sin, 2) + math.pow(ToothHeadHeight, 2))))
    point8 = adsk.core.Point3D.create(point5.getData()[1] * coefficient_k, point5.getData()[2] * coefficient_k, 0)
    sketchPoint8 = sketchPoints.add(point8)

    #constraints.addCoincident(sketchPoint8, line6)
        
    line10 = lines.addByTwoPoints(sketchPoint6, sketchPoint8)

    #constraints.addParallel(line10, line3)

    point9 = adsk.core.Point3D.create(point5.getData()[1] * coefficient_k, 0, 0)
    sketchPoint9 = sketchPoints.add(point9)

    #constraints.addCoincident(sketchPoint9, line1)

    line11 = lines.addByTwoPoints(sketchPoint8, sketchPoint9)

    #constraints.addPerpendicular(line11, line1)

    line12 = lines.addByTwoPoints(sketchPoint7, sketchPoint9)

    # -----------C R E A T E   R O T A T I O N   ( I F   N E E D E D )---------- #
    if Rotate:
        # ----------Create a collection of entities for move---------- #
        obj = adsk.core.ObjectCollection.create()
        for i in range(0, lines.count):
            obj.add(lines.item(i))

        # ----------Create a transform to do move---------- #
        transform1 = adsk.core.Matrix3D.create()
        transform1.setToRotation(math.pi / 2,adsk.core.Vector3D.create (0, 0, 1),adsk.core.Point3D.create(0, 0, 0))
        transform2 = adsk.core.Matrix3D.create()
        transform2.setToRotation(math.pi,adsk.core.Vector3D.create (0, 1, 0),adsk.core.Point3D.create(0, 0, 0))

        # ----------Create a move---------- #
        sketch1.move(obj, transform1)
        sketch1.move(obj, transform2)
    # -----------Add constraints, and dimensions to sketch1---------- #
    if Rotate:
        constraints.addVertical(line1)
        dimensions.addAngularDimension(line2, line1, adsk.core.Point3D.create(-tan / 2, 1, 0))
        addDistantionDimension(dimensions, sketch1.originPoint, sketchPoint2, 1)
    else:
        constraints.addHorizontal(line1)
        dimensions.addAngularDimension(line2, line1, adsk.core.Point3D.create(1, tan / 2, 0))
        addDistantionDimension(dimensions, sketch1.originPoint, sketchPoint2, 2)
    constraints.addCoincident(sketchPoint2, line3)
    constraints.addPerpendicular(line2, line3)
    addDistantionDimension(dimensions, sketchPoint2, sketchPoint3, 0)
    constraints.addCoincident(sketchPoint4, line3)
    addDistantionDimension(dimensions, sketchPoint2, sketchPoint4, 0)
    constraints.addMidPoint(sketchPoint4, line7)
    constraints.addCoincident(sketchPoint6, line4)
    addDistantionDimension(dimensions, sketchPoint3, sketchPoint6, 0)
    constraints.addCoincident(sketchPoint7, line1)
    constraints.addPerpendicular(line9, line1)
    constraints.addCoincident(sketchPoint8, line6)
    constraints.addParallel(line10, line3)
    constraints.addCoincident(sketchPoint9, line1)
    constraints.addPerpendicular(line11, line1)

    # -----------C R E A T E   E X T R U D E---------- #
    # ----------Get the profile---------- # 
    prof1 = sketch1.profiles.item(0)

    # Create an revolution input to be able to define the input needed for a revolution #
    # while specifying the profile and that a new component is to be created 
    revolves = newComp.features.revolveFeatures
    revInput = revolves.createInput(prof1, line1, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

    # Define that the extent is an angle of pi to get half of a torus #
    extAngle = adsk.core.ValueInput.createByReal(2 * math.pi)
    revInput.setAngleExtent(False, extAngle)

    # ----------Create the extrusion---------- #
    ext = revolves.add(revInput)
    body = ext.bodies.item(0) 

    # -----------C R E A T E   C O N S T R U C T I O N   P L A N E---------- #
    # ----------Get construction planes---------- #
    planes = newComp.constructionPlanes

    # ----------Create construction plane input---------- #
    planeInput = planes.createInput()

    # ----------Add construction plane by angle---------- #
    angle = adsk.core.ValueInput.createByString('270.0 deg')
    planeInput.setByAngle(line3, angle, prof1)
    constPlane = planes.add(planeInput)

    # -----------D R A W   S K E T C H _ 2---------- #
    sketch2 = sketches.add(constPlane)

    sketch2Points = sketch2.sketchPoints
    lines2 = sketch2.sketchCurves.sketchLines
    circles2 = sketch2.sketchCurves.sketchCircles
    arcs2 = sketch2.sketchCurves.sketchArcs
    constraints2 = sketch2.geometricConstraints
    dimensions2 = sketch2.sketchDimensions

    newOriginPoint = sketch2.project(sketchPoint1).item(0)
    deltaX = newOriginPoint.geometry.getData()[1]
    deltaY = newOriginPoint.geometry.getData()[2]

    PitchCirclePoint = sketch2.project(sketchPoint2).item(0)
    VerticesCirclePoint = sketch2.project(sketchPoint3).item(0)
    RecessCirclePoint = sketch2.project(sketchPoint4).item(0)

    #Draw circles
    PitchCircle = circles2.addByCenterRadius(newOriginPoint, PitchCircleRadius)
    PitchCircle.isConstruction = True

    VerticesCircle = circles2.addByCenterRadius(newOriginPoint, VerticesCircleRadius)
    VerticesCircle.isConstruction = True

    RecessCircle = circles2.addByCenterRadius(newOriginPoint, RecessCircleRadius)
    RecessCircle.isConstruction = True

    BaseCircle = circles2.addByCenterRadius(newOriginPoint, BaseCircleRadius)
    BaseCircle.isConstruction = True

    dimensions2.addDiameterDimension(BaseCircle, adsk.core.Point3D.create(BaseCircleRadius / 2 + deltaX, -BaseCircleRadius / 2 + deltaY, 0))

    constraints2.addCoincident(PitchCirclePoint, PitchCircle)
    constraints2.addCoincident(VerticesCirclePoint, VerticesCircle)
    constraints2.addCoincident(RecessCirclePoint, RecessCircle)

    # ----------- ---------- #

    # -----------Create an object collection for the points---------- #
    involutePoints1 = adsk.core.ObjectCollection.create()
    involutePoints2 = adsk.core.ObjectCollection.create()

    # ----------- ---------- #
    involutePointCount = 15

    if BaseCircleRadius < RecessCircleRadius:
        tmin = math.sqrt(math.pow(RecessCircleRadius, 2) / math.pow(BaseCircleRadius, 2) - 1)
    else:
        tmin = 0
    
    tmax = math.sqrt(math.pow(VerticesCircleRadius, 2) / math.pow(BaseCircleRadius, 2) - 1)
    step = (tmax - tmin) / (involutePointCount - 1)

    # ----------- ---------- #
    t_pitchInvolutePoint = math.sqrt(math.pow(PitchCircleRadius, 2) / math.pow(BaseCircleRadius, 2) - 1)
    pitchInvolutePoint = involutePoint(BaseCircleRadius, t_pitchInvolutePoint, deltaX, deltaY)
    pitchPointAngle = math.atan(pitchInvolutePoint.y / (pitchInvolutePoint.x + abs(deltaX)))

    # ----------- ---------- #
    involutePoints = []
    for t in frange(tmin, tmax + 2 * step, step):
        newPoint1 = involutePoint(BaseCircleRadius, t, deltaX, deltaY)
        involutePoints.append(newPoint1)
        if t < t_pitchInvolutePoint and t_pitchInvolutePoint < (t + step):
            involutePoints.append(pitchInvolutePoint)

    # ----------- ---------- #
    toothThickness = 0.5 * math.pi * Module
    Theta = (toothThickness * math.cos(PitchConeAngle)) / OuterPitchDiameter

    for i in range(0, involutePointCount + 2):
        rotateCircleRadius = math.sqrt(math.pow(involutePoints[i].y + abs(deltaY), 2) + math.pow(involutePoints[i].x + abs(deltaX), 2))
        Alpha = math.atan((involutePoints[i].y + abs(deltaY)) / (involutePoints[i].x + abs(deltaX)))
        rotateAngle = Alpha - pitchPointAngle + Theta
        newX = rotateCircleRadius * math.cos(rotateAngle) + deltaX
        newY = rotateCircleRadius * math.sin(rotateAngle) + deltaY
        involutePoints[i] = adsk.core.Point3D.create(newX, newY, 0)

    # ----------- ---------- #
    for i in range(0, involutePointCount + 2):
        involutePoints1.add(involutePoints[i])
    # Create the first spline.
    spline1 = sketch2.sketchCurves.sketchFittedSplines.add(involutePoints1)
    spline1.isFixed = True

    # ----------- ---------- #
    for i in range(0, involutePointCount + 2):
        involutePoints[i] = adsk.core.Point3D.create(involutePoints[i].x, -involutePoints[i].y, 0)

    for i in range(0, involutePointCount + 2):
        involutePoints2.add(involutePoints[i])

    # Create the first spline.
    spline2 = sketch2.sketchCurves.sketchFittedSplines.add(involutePoints2)
    spline2.isFixed = True

    # ----------- ---------- #

    #arcIn = arcs2.addByThreePoints(spline1.startSketchPoint, RecessCirclePoint.geometry, spline2.startSketchPoint)
    arcOutPoint = adsk.core.Point3D.create(VerticesCircleRadius + deltaX + 1, 0, 0)
    arcOut = arcs2.addByThreePoints(spline1.endSketchPoint, arcOutPoint, spline2.endSketchPoint)
    constraints2.addConcentric(arcOut, VerticesCircle)
    arcOut.isFixed = True

    if BaseCircleRadius > RecessCircleRadius:
        Angle = math.atan((involutePoints1.item(0).y + abs(deltaY)) / (involutePoints1.item(0).x + abs(deltaX)))
        arcInPoint1 = adsk.core.Point3D.create(RecessCircleRadius * math.cos(Angle) + deltaX, RecessCircleRadius * math.sin(Angle) + deltaY, 0)
        arcInPoint2 = adsk.core.Point3D.create(arcInPoint1.x, -arcInPoint1.y, 0)
        lline1 = lines2.addByTwoPoints(spline1.startSketchPoint, arcInPoint1)
        lline2 = lines2.addByTwoPoints(spline2.startSketchPoint, arcInPoint2)
        lline1.isFixed = True
        lline2.isFixed = True
    
        arcIn = arcs2.addByThreePoints(arcInPoint1, RecessCirclePoint.geometry, arcInPoint2)
        arcIn.isFixed = True
    else:
        #t_arcInPoint = math.sqrt(math.pow(RecessCircleRadius, 2) / math.pow(BaseCircleRadius, 2) - 1)
        #arcInPoint1 = involutePoint(BaseCircleRadius, t_arcInPoint, deltaX, deltaY)
        #Alpha = math.atan((arcInPoint1.y + abs(deltaY)) / (arcInPoint1.x + abs(deltaX)))
        #Angle = Alpha - pitchPointAngle + Theta
        #arcInPoint1 = adsk.core.Point3D.create(RecessCircleRadius * math.cos(Angle) + deltaX, RecessCircleRadius * math.sin(Angle) + deltaY, 0)
        #arcInPoint2 = adsk.core.Point3D.create(arcInPoint1.x, -arcInPoint1.y, 0)

        arcIn = arcs2.addByThreePoints(spline1.startSketchPoint, RecessCirclePoint.geometry, spline2.startSketchPoint)
        arcIn.isFixed = True


    prof2 = sketch2.profiles.item(0)

    sketch2.isVisible = False

    # -----------L O F T---------- #
     
    # ----------- ---------- #
    loftFeats = newComp.features.loftFeatures
    loftInput = loftFeats.createInput(adsk.fusion.FeatureOperations.CutFeatureOperation)
    loftSectionsObj = loftInput.loftSections
    loftSectionsObj.add(prof2)
    loftSectionsObj.add(newComp.originConstructionPoint)
    loft = loftFeats.add(loftInput)

    # ----------- ---------- #
    # Create input entities for circular pattern
    inputEntites = adsk.core.ObjectCollection.create()
    inputEntites.add(loft)

    # Create the input for circular pattern
    circularFeats = newComp.features.circularPatternFeatures
    if WhatDraw == "Pinion" and Rotate:
        circularFeatInput = circularFeats.createInput(inputEntites, newComp.yConstructionAxis)
    else:
        circularFeatInput = circularFeats.createInput(inputEntites, newComp.zConstructionAxis)

    # Set the quantity of the elements
    if WhatDraw == "Pinion":
        circularFeatInput.quantity = adsk.core.ValueInput.createByReal(PinionNumTeeth)
    else:
        circularFeatInput.quantity = adsk.core.ValueInput.createByReal(WheelNumTeeth)

    # Set the angle of the circular pattern
    circularFeatInput.totalAngle = adsk.core.ValueInput.createByString('360 deg')

    # Create the circular pattern
    circularFeat = circularFeats.add(circularFeatInput)

    # ----------- ---------- #
    if Rotate:
        body = adsk.core.ObjectCollection.create()
        body.add(newComp.bRepBodies.item(0))

        transform = adsk.core.Matrix3D.create()
        transform.setToRotation(math.pi / PinionNumTeeth,adsk.core.Vector3D.create (0, 1, 0),adsk.core.Point3D.create(0, 0, 0))

        moveFeats = newComp.features.moveFeatures
        moveFeatureInput = moveFeats.createInput(body, transform)
        moveFeats.add(moveFeatureInput)

    
    # Group everything used to create the gear in the timeline.
    timelineGroups = design.timeline.timelineGroups
    newOccIndex = newOcc.timelineObject.index
    circularFeatIndex = circularFeat.timelineObject.index
    # ui.messageBox("Indices: " + str(newOccIndex) + ", " + str(pitchSketchIndex))
    timelineGroup = timelineGroups.add(newOccIndex, circularFeatIndex)
    timelineGroup.name = WhatDraw

    if Joints:
       asBuiltJoints = newComp.asBuiltJoints
       JointGeometry = adsk.fusion.JointGeometry.createByPoint(sketchPoint9)
       asBuiltJointInput = asBuiltJoints.createInput(newOcc, foo, JointGeometry)
       if WhatDraw == "Pinion" and Rotate:
           asBuiltJointInput.setAsRevoluteJointMotion(1)
       else:
           asBuiltJointInput.setAsRevoluteJointMotion(0)
       joint = asBuiltJoints.add(asBuiltJointInput)
       joint.name = WhatDraw + ' joint'

    return newComp
