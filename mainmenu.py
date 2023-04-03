from ursina import *
from ursina import curve
from UI import *


colourH = color.rgba(18, 152, 255, 180)
colourN = color.rgba(0, 0, 0, 0.7)
highlighted = lambda button: button.color == colourH

class MainMenu(Entity):
    def __init__(self, player):
        super().__init__(
            parent = camera.ui
        )

        self.player = player

        self.mainmenu = Entity(parent = self, enabled = False)

        self.menus = [self.mainmenu]
        self.index = 0

        for menu in self.menus:
            def animate_in_menu(menu = menu):
                for i, e in enumerate(menu.children):
                    e.original_scale = e.scale
                    e.scale -= 0.01
                    e.animate_scale(e.original_scale, delay = i *0.05, duration = 0.1, curve = curve.out_quad)

                    e.alpha = 0
                    e.animate("alpha", 0.7, delay = i * 0.05, duration = 0.1, curve = curve.out_quad)

                    if hasattr(e, "text_entity"):
                        e.text_entity.alpha = 0
                        e.text_entity.animate("alpha", 1, delay = i * 0.05, duration = 0.1)

        self.mainmenu.enable()
        self.start_button = Button(text = "Start", color = colourH, highlight_color = colourH, scale_y = 0.1, scale_x = 0.3, y = 0.05, parent = self.mainmenu)
        self.quit_button = Button(text = "Quit", color = colourN, highlight_color = colourN, scale_y = 0.1, scale_x = 0.3, y = -0.19, parent = self.mainmenu)

        invoke(setattr, self.start_button, "color", colourH, delay = 0.5)

    def input(self, key):
        if key == "up arrow":
            for menu in self.menus:
                if menu.enabled:
                    self.index -= 1
                    if self.index <= -1:
                        self.index = 0
                    if isinstance(menu.children[self.index], Button):
                        menu.children[self.index].color = colourH
                        menu.children[self.index].highlight_color = colourH
                        for button in menu.children:
                            if menu.children[self.index] != button:
                                button.color = colourN
                                button.highlight_color = colourN
                    else:
                        self.index += 1

        elif key == "down arrow":
            for menu in self.menus:
                if menu.enabled:
                    self.index += 1
                    if self.index > len(menu.children) - 1:
                        self.index = len(menu.children) - 1
                    if isinstance(menu.children[self.index], Button):
                        menu.children[self.index].color = colourH
                        menu.children[self.index].highlight_color = colourH
                        for button in menu.children:
                            if menu.children[self.index] != button:
                                button.color = colourN
                                button.highlight_color = colourN
                    else:
                        self.index -= 1

        if key == "enter":
            # Main Menu
            if self.mainmenu.enabled:
                if highlighted(self.start_button):
                    self.set_player_state()
                elif highlighted(self.shop_button):
                    self.gun_menu.enable()
                    self.mainmenu.disable()
                    self.update_menu(self.gun_menu)
                elif highlighted(self.quit_button):
                    application.quit()

    def start(self):
        self.mainmenu.disable()
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

    def update_menu(self, menu):
        for c in menu.children:
            c.color = colourN
            c.highlighted_color = colourN
        menu.children[0].color = colourH
        menu.children[0].highlighted_color = colourH
        self.index = 0
        
