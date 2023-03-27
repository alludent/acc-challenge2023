from direct.showbase.ShowBase import ShowBase
from ursina import *
from ursina.shaders import lit_with_shadows_shader
from FirstPersonController import FirstPersonController
from Enemy import Enemy
import time as pytime

# Setups
app = Ursina()
stage = 1
random.seed(2023)
Entity.default_shader = lit_with_shadows_shader
#Environment
ground = Entity(model='plane', collider='box', scale=128)

for i in range(16):
    Entity(model='cube', origin_y=-.5, scale=2, texture='brick', texture_scale=(1, 2),
           x=random.uniform(-20, 20),
           z=random.uniform(-8, 8) + 18,
           collider='box',
           scale_y=random.uniform(15, 25),
           color=color.hsv(0, 0, random.uniform(.9, 1))
           )


def enemySetup():
    enemies = [Enemy(x=x * 10, target= player) for x in range(4)]
    mouse.traverse_target = Enemy.shootables_parent


def worldSetup():
    random.seed(2023)
    Entity.default_shader = lit_with_shadows_shader

    skySetup()
    buildingSetup()
    enemySetup()


app = Ursina()

# ======================================================= PLAYER/CAMERA ======================================================================
editor_camera = EditorCamera(enabled=False, ignore_paused=True)
player = FirstPersonController(model='cube', z=-20, color=color.orange, origin_y=-.5, speed=8)
player.collider = BoxCollider(player, Vec3(0, 1, 0), Vec3(1, 2, 1))

player.hp = 100
player.max_immune_timer = 0.8
player.immune_timer = 0.8
healthbar = Panel(scale=20, model='quad')
healthbar.alpha = 0

gun = Entity(model='cube', parent=camera, position=(.5, -.25, .25), scale=(.3, .2, 1), origin_z=-.5, color=color.red,
             on_cooldown=False)
gun.muzzle_flash = Entity(parent=gun, z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False)

grappleGun = Entity(model='cube', parent=camera, position=(-.5, -.25, .25), scale=(.3, .2, 1), origin_z=-.5,
                    color=color.green, grappling = False)
grappleGun.flash = Entity(parent=grappleGun, z=1, world_scale=.5, model='quad', color=color.blue, enabled=False)



# ======================================================= SETUP ======================================================================
ui = UI()
worldSetup()



#   ======================================================= GAME FUNCS ======================================================================
def update():
    player.immune_timer -= time.dt
    if player.hp <= 0:
        ui.on_player_death()

    if held_keys['left mouse']:
        shoot()

    if held_keys['right mouse']:
        grapple()
    if held_keys['escape']:
        app.destroy()
        exit()
    if player.hp <= 0:
        on_player_death()
    if player.y<0: #fall out of bounds
        on_player_death()

from ursina.prefabs.health_bar import HealthBar


def shoot():
    if not gun.on_cooldown:
        # print('shoot')
        gun.on_cooldown = True
        gun.muzzle_flash.enabled = True
        from ursina.prefabs.ursfx import ursfx
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise',
              pitch=random.uniform(-13, -12), pitch_change=-12, speed=3.0)
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 100
            mouse.hovered_entity.blink(color.red)


def grapple():
    grappleGun.flash.enabled = True

    direction = camera.forward
    maxGrappleDistance = 50

    # detect the point of impact
    hitData = raycast(grappleGun.flash.world_position, direction, maxGrappleDistance, ignore=[player])

    if hitData.hit and held_keys['right mouse']:
        # in grappling animation
        print("grappling")

            grappleLine.animate_scale((0.1, 0.1, 0.1), duration=0.2, curve=curve.in_expo)
            grappleLine.animate_position(hit_info.world_point, duration=0.2, curve=curve.in_expo)

            pull_dir = hit_info.world_point - player.position
            pull_factor = .5
            player.animate_position(player.position + pull_dir * pull_factor, duration=.5)

            invoke(grappleGun.flash.disable, delay=.05)
            invoke(setattr, grappleGun, 'on_cooldown', False, delay=.15)
        else:
            # if the grapple didn't hit anything
            print("Didn't hit")
            invoke(grappleGun.flash.disable, delay=.05)
            invoke(setattr, grappleGun, 'on_cooldown', False, delay=.15)

# Enemy()
enemies = [Enemy(x=x * 8, target= player) for x in range(4)]

#Death stuff
def on_respawn():
    print("respawning")
    death_panel.visible = False
    death_panel.retry.enabled = False
    player.hp = 100
    player.z = -10
    player.x = 0
    player.y = 0.8
    if stage ==1:
        global enemies
        for i in enemies:
            destroy(i)
        enemies = [Enemy(x=x * 8, target= player) for x in range(4)]
    invoke(setattr, gun, 'on_cooldown', False, delay=.1)

death_panel = Panel(scale=2, model='quad')
death_panel.retry = Button(parent=death_panel, color=color.red, position=(0, 0), text = "Retry")
death_panel.retry.on_click = on_respawn
death_panel.visible = False
death_panel.retry.enabled = False
def on_player_death():
    death_panel.retry.enabled = True
    death_panel.visible = True
    player.cursor.enabled = True
    gun.on_cooldown = True



# Pausing
def pause_input(key):
    if key == 'tab':  # press tab to toggle edit/play mode
        editor_camera.enabled = not editor_camera.enabled

        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position

        application.paused = editor_camera.enabled


pause_handler = Entity(ignore_paused=True, input=pause_input)

# Lighting
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, -1))
Sky()


app.run()
