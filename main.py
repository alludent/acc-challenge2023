from direct.actor.Actor import Actor
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader


class FirstPersonController(Entity):
    def __init__(self, **kwargs):
        self.cursor = Entity(parent=camera.ui, model='quad', color=color.pink, scale=.008, rotation_z=45)
        super().__init__()
        self.speed = 8
        self.height = 2
        self.camera_pivot = Entity(parent=self, y=self.height)

        camera.parent = self.camera_pivot
        camera.position = (0,0,0)
        camera.rotation = (0,0,0)
        camera.fov = 130
        mouse.locked = True
        self.mouse_sensitivity = Vec2(40, 40)

        self.gravity = 0.3
        self.grounded = False
        self.jump_height = 2
        self.jump_up_duration = .5
        self.fall_after = .35 # will interrupt jump up
        self.jumping = False
        self.air_time = 0

        for key, value in kwargs.items():
            setattr(self, key ,value)

        # make sure we don't fall through the ground if we start inside it
        if self.gravity:
            ray = raycast(self.world_position+(0,self.height,0), self.down, ignore=(self,))
            if ray.hit:
                self.y = ray.world_point.y


    def update(self):
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]

        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
        self.camera_pivot.rotation_x= clamp(self.camera_pivot.rotation_x, -90, 90)

        self.direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            ).normalized()

        feet_ray = raycast(self.position+Vec3(0,0.5,0), self.direction, ignore=(self,), distance=.5, debug=False)
        head_ray = raycast(self.position+Vec3(0,self.height-.1,0), self.direction, ignore=(self,), distance=.5, debug=False)
        if not feet_ray.hit and not head_ray.hit:
            move_amount = self.direction * time.dt * self.speed

            if raycast(self.position+Vec3(-.0,1,0), Vec3(1,0,0), distance=.5, ignore=(self,)).hit:
                move_amount[0] = min(move_amount[0], 0)
            if raycast(self.position+Vec3(-.0,1,0), Vec3(-1,0,0), distance=.5, ignore=(self,)).hit:
                move_amount[0] = max(move_amount[0], 0)
            if raycast(self.position+Vec3(-.0,1,0), Vec3(0,0,1), distance=.5, ignore=(self,)).hit:
                move_amount[2] = min(move_amount[2], 0)
            if raycast(self.position+Vec3(-.0,1,0), Vec3(0,0,-1), distance=.5, ignore=(self,)).hit:
                move_amount[2] = max(move_amount[2], 0)
            self.position += move_amount

            # self.position += self.direction * self.speed * time.dt

        if self.gravity:
            # gravity
            ray = raycast(self.world_position+(0,self.height,0), self.down, ignore=(self,))
            # ray = boxcast(self.world_position+(0,2,0), self.down, ignore=(self,))

            if ray.distance <= self.height+.1:
                if not self.grounded:
                    self.land()
                self.grounded = True
                # make sure it's not a wall and that the point is not too far up
                if ray.world_normal.y > .7 and ray.world_point.y - self.world_y < .5: # walk up slope
                    self.y = ray.world_point[1]
                return
            else:
                self.grounded = False

            # if not on ground and not on way up in jump, fall
            self.y -= min(self.air_time, ray.distance-.05) * time.dt * 100
            self.air_time += time.dt * .25 * self.gravity

    def input(self, key):
        if key == 'space':
            self.jump()

    def jump(self):
        if not self.grounded:
            return

        self.grounded = False
        self.animate_y(self.y+self.jump_height, self.jump_up_duration, resolution=int(1//time.dt), curve=curve.out_expo)
        invoke(self.start_fall, delay=self.fall_after)

    def start_fall(self):
        self.y_animator.pause()
        self.jumping = False

    def land(self):
        # print('land')
        self.air_time = 0
        self.grounded = True

    def on_enable(self):
        mouse.locked = True
        self.cursor.enabled = True

    def on_disable(self):
        mouse.locked = False
        self.cursor.enabled = False



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

for i in range(16):
    Entity(model='cube', origin_y=-.5, scale=2, texture='brick', texture_scale=(1,2),
        x=random.uniform(-20,20),
        z=random.uniform(-8,8) + 18,
        collider='box',
        scale_y = random.uniform(15,25),
        color=color.hsv(0, 0, random.uniform(.9, 1))
    )


def update():    
    if held_keys['left mouse']:
        shoot()
        
    if held_keys['right mouse']:
        grapple()


def grapple():
    
    if not grappleGun.on_cooldown:
        grappleGun.on_cooldown = True
        grappleGun.flash.enabled = True
        
        direction = camera.forward
        maxGrappleDistance = 50
        
        # detect the point of impact
        hit_info = raycast(grappleGun.flash.world_position, direction, maxGrappleDistance, ignore=[player])
        
        if hit_info.hit:
            # create line from the player to point of impact
            grappleLine = Entity(model='quad', texture='white_cube', scale=(hit_info.distance, 0.1, 0.1), position=camera.forward+Vec3(0,0,10), rotation = (player.rotation_x, player.rotation_y, 0), color=color.green)

            grappleLine.animate_scale((0.1, 0.1, 0.1), duration=0.2, curve=curve.in_expo)
            grappleLine.animate_position(hit_info.world_point, duration=0.2, curve=curve.in_expo)

            pull_dir = hit_info.world_point - player.position
            pull_factor = .5
            player.animate_position(player.position + pull_dir * pull_factor, duration=.5)


            invoke(grappleGun.flash.disable, delay=.05)
            invoke(setattr, grappleGun, 'on_cooldown', False, delay=.15)
        else:
            # if the grapple didn't hit anything
            invoke(grappleGun.flash.disable, delay=.05)
            invoke(setattr, grappleGun, 'on_cooldown', False, delay=.15)
            

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
            mouse.hovered_entity.hp -= 1000
            mouse.hovered_entity.blink(color.red)
            
# def grapple():
#     if not grappleGun.on_cooldown:
#         grappleGun.on_cooldown = True
#         grappleGun.flash.enabled = True
        
#         direction = camera.forward
#         max_distance = 50
        
#         # detect the point of impact
#         hit_info = raycast(grappleGun.flash.world_position, direction, max_distance, ignore=[player])
        
#         if hit_info.hit:
#             # create line from the player to point of impact
#             grappleLine = Entity(model='quad', texture='white_cube', scale=(0.1, hit_info.distance, 0.1), position=player.position, rotation=(0, 0, -player.rotation_y), color=color.green)
#             grappleLine.animate_scale((0.1, 0.1, 0.1), duration=0.2, curve=curve.in_expo)
#             grappleLine.animate_position(hit_info.world_point, duration=0.2, curve=curve.in_expo)

#             pull = hit_info.world_point - player.position
#             pull_factor = 1
#             player.animate_position(player.position + pull * pull_factor, duration=1)

#             invoke(grappleGun.flash.disable, delay=.05)
#             invoke(setattr, grappleGun, 'on_cooldown', False, delay=.15)

#             destroy(grappleLine, delay=3.0)
#         else:
#             # if the grapple didn't hit anything
#             invoke(grappleGun.flash.disable, delay=.05)
#             invoke(setattr, grappleGun, 'on_cooldown', False, delay=.15)

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
