from direct.actor.Actor import Actor
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader

app = Ursina()

random.seed(2023)
Entity.default_shader = lit_with_shadows_shader

ground = Entity(model='plane', collider='box', scale=64)

editor_camera = EditorCamera(enabled=False, ignore_paused=True)
player = FirstPersonController(model='cube', z=-10, color=color.orange, origin_y=-.5, speed=8)
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

gun = Entity(model='cube', parent=camera, position=(.5,-.25,.25), scale=(.3,.2,1), origin_z=-.5, color=color.red, on_cooldown=False)
gun.muzzle_flash = Entity(parent=gun, z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False)

grappleGun = Entity(model='cube', parent=camera, position=(-.5,-.25,.25), scale=(.3,.2,1), origin_z=-.5, color=color.green, on_cooldown=False)
grappleGun.flash = Entity(parent=grappleGun, z=1, world_scale=.5, model='quad', color=color.blue, enabled=False)

shootables_parent = Entity()
mouse.traverse_target = shootables_parent

def update():
    if held_keys['left mouse']:
        shoot()
    if held_keys['right mouse']:
        grapple()

def shoot():
    if not gun.on_cooldown:
        # print('shoot')
        gun.on_cooldown = True
        gun.muzzle_flash.enabled=True
        from ursina.prefabs.ursfx import ursfx
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise', pitch=random.uniform(-13,-12), pitch_change=-12, speed=3.0)
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)
            
def grapple():
    if not grappleGun.on_cooldown:
        grappleGun.on_cooldown = True
        grappleGun.flash.enabled = True
        
        # calc direction
        direction = mouse.position - grappleGun.flash.world_position
        direction = direction.normalized()
        
        max_distance = 100
        
        # detect the point of impact
        hit_info = raycast(grappleGun.flash.world_position, direction, max_distance, ignore=[player])
        print(hit_info.entity)
        
        if hit_info.hit:
            # create line from the player to point of impact
            grapple_line = Entity(model='quad', texture='white_cube', scale=(0.1, hit_info.distance, 0.1), position=player.position, rotation=(0, 0, -player.rotation_y), color=color.green)
            grapple_line.animate_scale((0.1, 0.1, 0.1), duration=0.2, curve=curve.in_expo)
            grapple_line.animate_position(hit_info.world_point, duration=0.2, curve=curve.in_expo)

            invoke(grappleGun.flash.disable, delay=.05)
            invoke(setattr, grappleGun, 'on_cooldown', False, delay=.15)

            destroy(grapple_line, delay=3.0)
        else:
            # if the grapple didn't hit anything
            invoke(grappleGun.flash.disable, delay=.05)
            invoke(setattr, grappleGun, 'on_cooldown', False, delay=.15)

from ursina.prefabs.health_bar import HealthBar

class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=shootables_parent, model='cube', origin_y=-.5, color=color.light_gray, collider='box', **kwargs)
        self.setScale(1,2.4,3)

        self.alpha = 0
        self.actor = Actor("Entities/ODIUS/ODIUS.glb")
        self.actor.reparent_to(self)
        self.actor.setPos(0,0.4,0)
        self.actor.setScale(1/self.scale_x,1/self.scale_y,1/self.scale_z)
        self.actor.setHpr(180, 0, 0)
        self.actor.loop("Leap")  # use .play() instead of loop() to play it once.

        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5,.1,.1))
        self.max_hp = 100
        self.hp = self.max_hp
        self.speed = 2
    def update(self):
        dist = distance_xz(player.position, self.position)
        if dist > 40:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)


        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 30, ignore=(self,))
        if hit_info.entity == player:
            if dist > 2:
                self.position += self.forward * time.dt * self.speed

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1

# Enemy()
enemies = [Enemy(x=x*4) for x in range(4)]


def pause_input(key):
    if key == 'tab':    # press tab to toggle edit/play mode
        editor_camera.enabled = not editor_camera.enabled

        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position

        application.paused = editor_camera.enabled

pause_handler = Entity(ignore_paused=True, input=pause_input)


sun = DirectionalLight()
sun.look_at(Vec3(1,-1,-1))
Sky()

app.run()
