
from ursina import *
from ursina.shaders import lit_with_shadows_shader
from ursina.prefabs.health_bar import HealthBar

from FirstPersonController import FirstPersonController
from Enemy import Enemy
from UI import UI



# ======================================================= WORLD ======================================================================
def environmentSetup():
    print("creating sky")
    sun = DirectionalLight()
    Sky()
    print ("creating buildings")
    ground = Entity(model='plane', texture='Assets/Map/CityTexture.png', collider='box', scale=256)
    building = Entity(model='RuinedBuilding', texture='Assets/Map/CityTexture.png', collider='mesh', scale=4)
    # ground = Entity(model='plane', collider='box', scale=64, color = color.green)

enemies = []

def enemySetup():
    global enemies
    print ("Spawning enemies")
    enemies = [Enemy(x=x * 10, target= player) for x in range(1)]
    mouse.traverse_target = Enemy.shootables_parent

def resetEnemies():
    global enemies
    print ("resetting enemies")
    for i in enemies:
        destroy(i)
    enemies = [Enemy(x=x * 8, target= player) for x in range(2)]


def worldSetup():
    random.seed(2023)
    Entity.default_shader = lit_with_shadows_shader

    environmentSetup()
    enemySetup()
    print("World created")



# ======================================================= WINDOW SETUP =========================================================================
app = Ursina()

# ======================================================= PLAYER/CAMERA ======================================================================
editor_camera = EditorCamera(enabled=False, ignore_paused=True)

player = FirstPersonController(model='cube', z=-10, color=color.orange, origin_y=-.5, speed=12)
player.collider = BoxCollider(player, Vec3(0, 1, 0), Vec3(1, 2, 1))

player.hp = 100
player.maxImmuneTimer = 0.8
player.immuneTimer = 0.8

print("player initiated")

gun = Entity(model='cube', parent=camera, position=(.5, -.25, .25), scale=(.3, .2, 1), origin_z=-.5, color=color.red,
             on_cooldown=False)
gun.muzzle_flash = Entity(parent=gun, z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False)

grappleGun = Entity(model='cube', parent=camera, position=(-.5, -.25, .25), scale=(.3, .2, 1), origin_z=-.5, color=color.green, 
                    range = 25, grappling = False)
grappleGun.flash = Entity(parent=grappleGun, z=1, world_scale=.5, model='quad', color=color.blue, enabled=False)

print("weapons loaded")

# ======================================================= GAME SETUP ======================================================================
ui = UI(editor_camera, player, gun, grappleGun, resetEnemies)
player.healthbar = ui.create_health_bar()
worldSetup()


#   ======================================================= GAME FUNCS ======================================================================
def update():
    player.immuneTimer -= time.dt

    # in relation to players spawn position, +x = right, +z = forward, +y = upward
    if player.hp <= 0 or player.position.y < -50:
        ui.on_player_death()

    if held_keys['left mouse']:
        shoot()

    if held_keys['right mouse']:
        grapple()
    elif not held_keys['right mouse'] and grappleGun.grappling:
        release_grapple()


def grapple():
# only detect point of impact if not already grappling
    if not grappleGun.grappling:  
        player.stop()
        grappleGun.hitData = raycast(camera.world_position, camera.forward, grappleGun.range, ignore=[player], debug= True)

        # start grappling animation
        if grappleGun.hitData.hit:
            grappleGun.flash.enabled = True
            grappleGun.grappling = True
            grappleGun.grappleStart = time.time()

            # create vector towards point of impact
            grappleGun.line = grappleGun.hitData.world_point - player.position 

            # how fast to move the plyaer toward point of impact
            grappleGun.velocity = grappleGun.line.normalized() * 20

            print("grapple started")
            print("grapple vec ", grappleGun.line)

            # finetuning, tolerance has to increase for higher grappling points (only here bc collisions are not in place yet)
            if grappleGun.line.y - player.position.y > 15: 
                grappleGun.tolerance = 2
            else:
                grappleGun.tolerance = 2

        else:
            player.resume()

    # player is already grappling, update their position towards the point of impact
    elif grappleGun.grappling and held_keys['right mouse']:
        if time.time() - grappleGun.grappleStart >= 0.3:
            # update player's velocity based on the grapple point
            feet_ray = raycast(player.position + Vec3(0, 0.5, 0), grappleGun.line, ignore=(player,), distance=.5, debug=False)
            head_ray = raycast(player.position + Vec3(0, player.height - .1, 0), grappleGun.line, ignore=(player,), distance=.5,
                           debug=False)
            if not feet_ray.hit and not head_ray.hit:
                player.position += grappleGun.velocity * time.dt
                

            
            # player.animate_position(grappleGun.hitData.world_point, duration = .5)
            # release_grapple()

            # check if player has reached the grapple point
            distanceToPointOfImpact = (grappleGun.flash.world_position - grappleGun.hitData.world_point).length()

            # tolerance is distance from point of impact
            if distanceToPointOfImpact <= grappleGun.tolerance:
                # stop grappling
                grappleGun.velocity = Vec3(0, 0, 0)
                print("grapple ended")


def release_grapple():
    if grappleGun.grappling:
        player.resume()

        grappleGun.flash.enabled = False
        grappleGun.grappling = False

        print("grapple released")


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



app.run()
