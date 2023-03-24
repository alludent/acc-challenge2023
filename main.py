from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from panda3d.core import WindowProperties
from panda3d.core import ClockObject
from panda3d.core import Vec3
# from direct.task.TaskManager import TaskManager


SPEED = 5.0


# showbase is a base class for the game window
# contains various aspects of game management
# eg scene management, input handling 
class GrappleDoom(ShowBase):
    def __init__(self):
        # subclass initialized 
        ShowBase.__init__(self)

        # by default, panda uses mouse based control
        self.disableMouse()

        # modify window dimensions
        properties = WindowProperties()
        properties.setSize(1000, 750)
        self.win.requestProperties(properties)

        # world.xxx -- panda automatically detects which world file to load
        # loader is used to load different types of non animated models
        # load the environemnt (doesn't show anything if not attached to scene)
        self.environment = self.loader.loadModel("World/world")
        # attach to scene (make it a child of NodePath)
        self.environment.reparentTo(self.render)

        # Actor is used for animated models 
        # panda automatically detects player file type
        self.tempActor = Actor("EntityTex/Player/player", {"walk" : "EntityTex/Player/player_walk"})
        self.tempActor.reparentTo(self.render)

        # camera default is (0,0,0), won't show actor
        self.tempActor.setPos(0, 7, 0)

        # animate actor
        self.tempActor.loop("walk")

        # create keymap
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

        # self.update added to task manager 
        # self.updateTask :: variable assigned to the task object
        # self.taskMgr.add :: identifies the task 
        self.updateTask = self.taskMgr.add(self.update, "update")

    def updateKeyMap(self, controlName, controlState):
        self.keyMap[controlName] = controlState
    

    def update(self, task):
         # Get the global clock and compute the time since the last frame
        self.clock = ClockObject.getGlobalClock()
        dt = self.clock.getDt()

        # check for player movement
        if self.keyMap["up"]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(0, SPEED*dt, 0))
        if self.keyMap["down"]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(0, -SPEED*dt, 0))
        if self.keyMap["left"]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(-SPEED*dt, 0, 0))
        if self.keyMap["right"]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(SPEED*dt, 0, 0))
        if self.keyMap["shoot"]:
            print ("Zap!")

        # Tell the task manager to continue running this task
        return task.cont


game = GrappleDoom()
game.run()

