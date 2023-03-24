from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from math import sin, cos, pi
from panda3d.core import WindowProperties
from panda3d.core import ClockObject
from panda3d.core import Vec3
# from panda3d.core import *


# showbase is a base class for the game window
# contains various aspects of game management
# eg scene management, input handling 
class GrappleDoom(ShowBase):
    def __init__(self):
        # subclass initialized 
        super().__init__()

        # player settings
        self.SPEED = 5.0
        self.mouseSens = 15.0

        # modify window dimensions; default is 800 640----------------------------------------------------------------------------
        properties = WindowProperties()
        properties.setSize(800, 640)
        self.win.requestProperties(properties)
        properties.setCursorHidden(False)

        # confined mouse can't leave window
        properties.setMouseMode(WindowProperties.MConfined)
        self.win.requestProperties(properties)

        # disable default mouse controls
        base.disableMouse()

        # world.xxx -- panda automatically detects which world file to load-------------------------------------------------------------
        # loader is used to load different types of non animated models
        # load the environemnt (doesn't show anything if not attached to scene)
        self.environment = base.loader.loadModel("World/world")
        # attach to scene (make it a child of NodePath)
        self.environment.reparentTo(base.render)

        # Actor is used for animated models ------------------------------------------------------------------------------------------
        # panda automatically detects player file type
        self.DoomDude = Actor("Entities/Player/player", {"walk" : "Entities/player/player_walk"})
        self.DoomDude.reparentTo(base.render)

        # animate actor
        # self.DoomDude.loop("walk")

        # mouse camera -------------------------------------------------------------------------------------------------------------
        self.camera = base.camera
        self.horizontal = 0
        self.vertical = 0
        self.camera.setHpr(self.horizontal, self.vertical, 0)
        self.cameraHpr = self.camera.getHpr()

        # create cam node to attach to player movement
        # self.cameraNode = NodePath("cameraNode")
        # self.cameraNode.reparentTo(base.render)
        # self.camera.reparentTo(cameraNode)


        
        # keymap ------------------------------------------------------------------------------------------------------------------
        self.keyMap = {
            "up" : False,
            "down" : False,
            "left" : False,
            "right" : False,
            "shoot" : False,
            "grapple" : False
        }

        # listen to key input 
        self.accept("w", self.updateKeyMap, ["up", True])
        self.accept("w-up", self.updateKeyMap, ["up", False])
        self.accept("s", self.updateKeyMap, ["down", True])
        self.accept("s-up", self.updateKeyMap, ["down", False])
        self.accept("a", self.updateKeyMap, ["left", True])
        self.accept("a-up", self.updateKeyMap, ["left", False])
        self.accept("d", self.updateKeyMap, ["right", True])
        self.accept("d-up", self.updateKeyMap, ["right", False])
        self.accept("mouse1", self.updateKeyMap, ["shoot", True])
        self.accept("mouse1-up", self.updateKeyMap, ["shoot", False])

        # self.update added to task manager ----------------------------------------------------------------------------
        # self.updateTask :: variable assigned to the task object
        # self.taskMgr.add :: identifies the task 
        self.updateTask = taskMgr.add(self.update, "update")



    def update(self, task):
         # Get the global clock and compute the time since the last frame ------------------------------------------------------
        self.clock = ClockObject.getGlobalClock()
        self.deltaT = self.clock.getDt()

        # camera mouse movement --------------------------------------------------------------------------------------------------------
        self.updateCamera()

        # player movement----------------------------------------------------------------------------------------------
        self.updatePlayer(self.deltaT)

        if self.keyMap["shoot"]:
            print ("Shoot!")

        # continue the task --------------------------------------------------------------------
        return task.cont

    def updateKeyMap(self, controlName, controlState):
        self.keyMap[controlName] = controlState

    def updatePlayer(self, deltaT):
        # get input direction from key map
        inputDir = Vec3(self.keyMap["right"] - self.keyMap["left"], 0, self.keyMap["up"] - self.keyMap["down"]).normalized()

        # calculate camera heading in radians 
        # heading is the left and right movement (Panda3D Hpr sphere illustration)
        camHeading = self.cameraHpr.getX() * pi / 180.0

        # calculate the direction based on the camera's rotation
        forwardDir = Vec3(-sin(camHeading), cos(camHeading), 0)
        sideDir = Vec3(cos(camHeading), sin(camHeading), 0)

        # calculate the move direction based on input direction and camera direction
        moveDir = forwardDir * inputDir.z + sideDir * inputDir.x

        # update player position
        self.DoomDude.setPos(self.DoomDude.getPos() + moveDir * self.SPEED * self.deltaT)

    def updateCamera(self):
        if base.mouseWatcherNode.hasMouse():
            # get mouse data
            self.deltaX = base.mouseWatcherNode.getMouseX()
            self.deltaY = base.mouseWatcherNode.getMouseY()

            # get player data
            playerPos = self.DoomDude.getPos()
            playerHpr = self.DoomDude.getHpr()
            
            # set camera settings
            cameraOffset = Vec3(0, 0, 0)
            cameraPos = playerPos + cameraOffset

            # calculate camera movement
            self.cameraHpr.setX(self.cameraHpr.getX() - self.deltaX * self.mouseSens)
            self.cameraHpr.setY(self.cameraHpr.getY() + self.deltaY * self.mouseSens)
            
            # update camera
            self.camera.setPos(cameraPos)
            self.camera.setHpr(self.cameraHpr)
      
        # reset to center
        base.win.movePointer(0, base.win.getProperties().getXSize()//2, base.win.getProperties().getYSize()//2)


game = GrappleDoom()
game.run()

