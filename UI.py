from ursina.prefabs.health_bar import HealthBar
from ursina import *
import sys

colourH = color.rgba(18, 152, 255, 180)
colourN = color.rgba(0, 0, 0, 0.7)
highlighted = lambda button: button.color == colourH


class UI:
    def __init__(self, editor_camera, player, gun, grappleGun, resetEnemies):
        self.editor_camera = editor_camera
        self.player = player
        self.gun = gun
        self.grappleGun = grappleGun
        self.resetEnemies = resetEnemies
        
        
        self.death_scene_setup()
        self.pause_menu_setup()
        self.main_menu_setup()

        pauseHandler = Entity(ignore_paused=True, input=self.editor_menu)
        
    def create_healthbar(self):
        return HealthBar(self.player.hp, bar_color=color.hex("E80000"), roundness=0.5, y= window.top_left[1] - 0.01, scale_y=0.03, scale_x=0.3)

    def set_player_state(self):
        self.editor_camera.enabled = not self.editor_camera.enabled

        self.player.visible_self = self.editor_camera.enabled
        self.player.cursor.enabled = not self.editor_camera.enabled
        self.gun.enabled = not self.editor_camera.enabled
        self.grappleGun.enabled = not self.editor_camera.enabled
        mouse.locked = not self.editor_camera.enabled
        self.editor_camera.position = self.player.position

        application.paused = self.editor_camera.enabled

    def main_menu_setup(self):
        self.mainmenu = Panel(scale = 2, model='quad', color=color.rgba(0,0,0,150))
        self.start_button = Button(parent=self.mainmenu, text='Start', position=(.05, 0), 
                                            highlight_color= color.yellow, scale = 0.06, 
                                            on_click=self.on_respawn)
        self.quit_button = Button(parent=self.mainmenu, text='Quit', position=(-.05,0), 
                                            highlight_color= color.green, scale = 0.06, 
                                            on_click=application.quit)
        self.mainmenu.visible = True
        self.start_button.enabled = True
        self.quit_button.enabled = True

    def mainmenu(self):
        if self.mainmenu.visible:
            self.set_player_state()

            self.mainmenu.visible = True
            self.start_button.enabled = True
            self.quit_button.enabled = True
        else:
            self.mainmenu.visible = False
            self.start_button.enabled = False
            self.quit_button.enabled = False



    def pause_menu_setup(self):
        self.pause_menu = Panel(scale = 2, model='quad', color=color.rgba(0,0,0,150))
            
        self.pause_menu.retry = Button( parent=self.pause_menu, text='Restart', position=(.05, 0), 
                                            highlight_color= color.yellow, scale = 0.06, 
                                            on_click=self.on_respawn)
        self.pause_menu.exit = Button( parent=self.pause_menu, text='Exit', position=(-.05,0), 
                                            highlight_color= color.green, scale = 0.06, 
                                            on_click=application.quit)
        self.pause_menu.visible = False
        self.pause_menu.retry.enabled = False
        self.pause_menu.exit.enabled = False  
        
        
    def editor_menu(self, key):
        if key == 'escape':  # press tab to toggle edit/play mode
            self.set_player_state()
            
            if self.editor_camera.enabled:
                print('pausing')
                self.pause_menu.retry.enabled = True
                self.pause_menu.exit.enabled = True
                self.pause_menu.visible = True
            else:
                print('unpausing')
                self.pause_menu.retry.enabled = False
                self.pause_menu.exit.enabled = False
                self.pause_menu.visible = False

    def death_scene_setup(self):
        self.death_panel = Panel(scale=2, model='quad')
        self.death_panel.retry = Button(parent=self.death_panel, color=color.red, position=(0, 0), text = "Retry")
        self.death_panel.retry.on_click = self.on_respawn
        self.death_panel.visible = False
        self.death_panel.retry.enabled = False


    def on_respawn(self):
        print("respawning")
        self.set_player_state()
                
        self.pause_menu.visible = False
        self.pause_menu.retry.enabled = False
        self.pause_menu.exit.enabled = False
        self.mainmenu.visible = False
        self.start_button.visible = False
        self.quit_button.visible = False
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
        self.set_player_state()
