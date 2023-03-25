from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from math import sin, cos, pi


from panda3d.core import NodePath
from panda3d.core import CardMaker
from panda3d.core import WindowProperties
from panda3d.core import Vec3

# from panda3d.core import *


# showbase is a base class for the game window
# contains various aspects of game management
# eg scene management, input handling 
class GrappleDoom(ShowBase):
    def __init__(self):
        # init subclass of ShowBase
        super().__init__()

        # player settings----------------------------------------------------------------------------------------------------------------
        self.SPEED = 5.0
        self.mouseSens = 15.0
        self.cameraOffset = Vec3(0, 0, 0)
        self.gunTypes = ["pistol", "shotgun", "rifle"]
        self.currGunType = self.gunTypes[1]

        # modify window dimensions; default is 800 640------------------------------------------------------------------------------------------
        self.init_windowProperties()

        # world.xxx -- panda automatically detects which world file to load-------------------------------------------------------------
        # loader is used to load different types of non animated models
        # load the environemnt (doesn't show anything if not attached to scene)
        self.world = base.loader.loadModel("World/world")
        self.world.reparentTo(base.render)

        # Actor is used for animated models ------------------------------------------------------------------------------------------
        # panda automatically detects player file type
        self.player = Actor("Entities/Player/player", {"walk" : "Entities/player/player_walk"})
        self.player.reparentTo(base.render)

        # animate actor
        # self.player.loop("walk")

        # load the gun tex -----------------------------------------------------------------------------------------------------------------
        self.aspectRatio = self.getAspectRatio()
        self.loadGunTex(self.currGunType)

        self.bullet_node = NodePath("bullet")
        self.bullet_model = base.loader.loadModel("Entities/Player/WeaponTex/bullet.bam")
        self.bullet_model.reparentTo(self.bullet_node)
        self.bullet_node.reparentTo(base.render)

        # mouse camera -------------------------------------------------------------------------------------------------------------
        self.camera = base.camera
        self.cameraHpr = self.camera.getHpr()

        # keymap ------------------------------------------------------------------------------------------------------------------
        self.init_keyMap()

        # self.update added to task manager -------------------------------------------------------------------------------------------
        # self.updateTask :: variable assigned to the task object
        # self.taskMgr.add :: identifies the task 
        self.updateTask = taskMgr.add(self.update, "update")


    def update(self, task):
         # Get the global clock and compute the time since the last frame ------------------------------------------------------
        deltaT = globalClock.getDt()

        # camera mouse movement --------------------------------------------------------------------------------------------------------
        self.updateCamera()

        # player movement-------------------------------------------------------------------------------------------------------------
        self.updatePlayer(deltaT)
        
        # guntypes = [pistol, shotgun]
        if self.keyMap["shoot"]:
            self.updateBullets(deltaT, self.currGunType)

        # continue the task -----------------------------------------------------------------------------------------------------------------
        return task.cont

    def init_windowProperties(self):
        self.properties = WindowProperties()
        self.properties.setSize(800, 640)
        self.win.requestProperties(self.properties)
        self.properties.setCursorHidden(False)

        # confined mouse can't leave window
        self.properties.setMouseMode(WindowProperties.MConfined)
        self.win.requestProperties(self.properties)

        # disable default mouse controls
        base.disableMouse()

    def init_keyMap(self):
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

    def updateKeyMap(self, controlName, controlState):
        self.keyMap[controlName] = controlState

    def updateCamera(self):
        # reset to center
        base.win.movePointer(0, base.win.getProperties().getXSize()//2, base.win.getProperties().getYSize()//2)

        # check if camera is inside the window----------------------------------------------------------------------------------------
        if base.mouseWatcherNode.hasMouse():
            # get mouse data
            deltaX = base.mouseWatcherNode.getMouseX()
            deltaY = base.mouseWatcherNode.getMouseY()
            
            # set camera settings
            cameraPos = self.player.getPos() + self.cameraOffset

            # calculate camera movement
            self.cameraHpr.setX(self.cameraHpr.getX() - deltaX * self.mouseSens)
            self.cameraHpr.setY(self.cameraHpr.getY() + deltaY * self.mouseSens)
            
            # update camera
            self.camera.setPos(cameraPos)
            self.camera.setHpr(self.cameraHpr)

    def updatePlayer(self, deltaT):
        # player movement---------------------------------------------------------------------------------------------------------
        # get input direction from key map
        inputDir = Vec3(self.keyMap["right"] - self.keyMap["left"], 0, self.keyMap["up"] - self.keyMap["down"]).normalized()

        # calculate camera heading in radians 
        # heading is the left and right movement (Panda3D Hpr sphere illustration)
        self.camHeading = self.cameraHpr.getX() * pi / 180.0

        # calculate the direction based on the camera's rotation
        forwardDir = Vec3(-sin(self.camHeading), cos(self.camHeading), 0)
        sideDir = Vec3(cos(self.camHeading), sin(self.camHeading), 0)

        # calculate the move direction based on input direction and camera direction
        moveDir = forwardDir * inputDir.z + sideDir * inputDir.x

        # update player position
        self.player.setPos(self.player.getPos() + moveDir * self.SPEED * deltaT)

    def loadGunTex(self, gunType):
        # name the file to match gun type
        self.gunTex = base.loader.loadTexture("Entities/Player/WeaponTex/" + self.currGunType + ".png")

        if gunType == "pistol":
            pass

        elif gunType == "shotgun":
            # create a card to display the gun image
            # aspect2d is used to position textures on the 2d screen space
            # create a card and attaches it to aspect2d node 
            gun = base.aspect2d.attachNewNode(CardMaker("gun").generate())

            # changes texture of that node
            gun.setTexture(self.gunTex)

            # transparent background for the texture
            gun.setTransparency(True)

            # scale the card
            gun.setScale(self.aspectRatio)  

            # Set the position of the gun card to the bottom right corner of the screen
            y = -1 + 0.1 / self.aspectRatio 
            gun.setPos(0, y, -1)

        elif gunType == "rifle":
            pass

    def updateBullets(self, deltaT, gunType):
            
        velocity = Vec3(0, 0, 0)
        if gunType == "pistol":
            bulletCount = 1
            bulletSpread = 0
            bulletInterval = 0.3
        elif gunType == "shotgun":
            bulletCount = 5
            bulletSpread = 1.3
            bulletInterval = 1
        elif gunType == "rifle":
            bulletCount = 1
            bulletSpread = 0.3
            bulletInterval = 0.5

        # Get the camera's heading and pitch angles
        heading = self.cameraHpr.getX() * pi / 180.0
        pitch = self.cameraHpr.getY() * pi / 180.0
        
        # Calculate the direction vector of the bullet
        direction = Vec3(-sin(heading)*cos(pitch), cos(heading)*cos(pitch), -sin(pitch))
        
        # Set the velocity of the bullet in the direction vector
        velocity += direction * deltaT * 100.0
        
        # Move the bullet by its velocity
        self.bullet_node.setPos(self.bullet_node.getPos() + velocity * deltaT)
        
        # Remove the bullet if it goes out of bounds
        if self.bullet_node.getPos().getX() < -50 or self.bullet_node.getPos().getX() > 50 or \
           self.bullet_node.getPos().getY() < -50 or self.bullet_node.getPos().getY() > 50 or \
           self.bullet_node.getPos().getZ() < -50 or self.bullet_node.getPos().getZ() > 50:
            self.bullet_node.removeNode()

            

game = GrappleDoom()
game.run()

