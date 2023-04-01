
from ursina.prefabs.health_bar import HealthBar
from ursina import *

class UI:
    def __init__(self, editor_camera, player, gun, grappleGun, resetEnemies):
        self.editor_camera = editor_camera
        self.player = player
        self.gun = gun
        self.grappleGun = grappleGun
        self.resetEnemies = resetEnemies
        
        pause_handler = Entity(ignore_paused=True, input=self.on_pause)

        self.deathSceneSetup()
        self.pauseMenuSetup()

    def createHealthBar(self):
        return HealthBar(self.player.hp, bar_color=color.hex("E80000"), roundness=0.5, y= window.top_left[1] - 0.01, scale_y=0.03, scale_x=0.3)

    def on_pause(self, key):
        if key == 'tab':  # press tab to toggle edit/play mode
            self.editor_camera.enabled = not self.editor_camera.enabled

            self.player.visible_self = self.editor_camera.enabled
            self.player.cursor.enabled = not self.editor_camera.enabled
            self.gun.enabled = not self.editor_camera.enabled
            self.grappleGun.enabled = not self.editor_camera.enabled
            mouse.locked = not self.editor_camera.enabled
            self.editor_camera.position = self.player.position

            application.paused = self.editor_camera.enabled
            
            print('pausing')
            self.pause_menu.retry.enabled = True
            self.pause_menu.exit.enabled = True
            self.pause_menu.visible = True
            
            
    def pauseMenuSetup(self):
        self.pause_menu = Entity( parent=camera.ui, enabled=False, model='quad', scale=(.6, .8), position=(0, 0), 
                            color=color.rgba(0, 0, 0, 200), origin=(-.5, .5))
            
        self.pause_menu.retry = Button( parent=self.pause_menu, text='Restart', position=(0, .1), on_click=self.restart_game)
        self.pause_menu.exit = Button( parent=self.pause_menu, text='Exit', position=(0, -.1), on_click=application.quit)
        self.pause_menu.visible = False
        self.pause_menu.retry.enabled = False
        self.pause_menu.exit.enabled = False    

    def restart_game(self):
        print("restarting")
        self.pause_menu.visible = False
        self.pause_menu.retry.enabled = False
        self.pause_menu.exit.enabled = False
        self.player.cursor.enabled = False


    def deathSceneSetup(self):
        self.death_panel = Panel(scale=2, model='quad')
        self.death_panel.retry = Button(parent=self.death_panel, color=color.red, position=(0, 0), text = "Retry")
        self.death_panel.retry.on_click = self.on_respawn
        self.death_panel.visible = False
        self.death_panel.retry.enabled = False


    def on_respawn(self):
        print("respawning")
        self.death_panel.visible = False
        self.death_panel.retry.enabled = False

        self.player.position = Vec3(0, .5, -10)
        
        self.player.hp = 100
        self.player.healthbar.value = self.player.hp

        self.resetEnemies()


    def on_player_death(self):
        print("u died")
        self.death_panel.retry.enabled = True
        self.death_panel.visible = True
        self.player.cursor.enabled = True

