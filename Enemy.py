from direct.actor.Actor import Actor
from ursina import *

class Enemy(Entity):
    shootables_parent = Entity()

    def __init__(self, target, **kwargs):
        super().__init__(parent=Enemy.shootables_parent, model='cube', origin_y=-.5, color=color.light_gray, collider='box',
                         **kwargs)
        self.target = target
        self.height = 2
        self.setScale(1, 2.4, 3)
        self.leap_on_cooldown = True
        self.collider = 'box'
        self.alpha = 0
        self.actor = Actor("Entities/ODIUS/ODIUS.glb")
        self.actor.reparent_to(self)
        self.actor.setPos(0, 0.4, 0)
        self.actor.setScale(1 / self.scale_x, 1 / self.scale_y, 1 / self.scale_z)
        self.actor.setHpr(180, 0, 0)
        # use .play() instead of loop() to play it once.
        self.healthBar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5, .1, .1))
        self.maxHp = 100
        self.hp = self.maxHp
        self.speed = 2
        self.actor.setPlayRate(0.15, 'Leap')
        self.actor.play('Leap',fromFrame=3, toFrame=3)
        self.gravity = 0.3
        self.grounded = False
        self.jumpHeight = 3
        self.jumpUpDuration = .5
        self.fallAfter = .35  # will interrupt jump up
        self.jumping = False
        self.airTime = 0
        self.damage = 30
        invoke(setattr, self, 'leap_on_cooldown', False, delay=5)

    def start_fall(self):
        self.y_animator.pause()
        self.jumping = False
    def jump(self):
        if not self.grounded:
            return

        self.grounded = False
        self.animate_y(self.y + self.jumpHeight, self.jumpUpDuration, resolution=int(1 // time.dt),
                       curve=curve.out_expo)
        invoke(self.start_fall, delay=self.fallAfter)

    
    def leap(self):
        self.leap_on_cooldown = True
        self.actor.play('Leap',fromFrame=4, toFrame=6)
        #self.jump()
        invoke(self.jump, delay=0.2)
        invoke(setattr, self, 'speed', 6, delay=0.2)
        invoke(setattr, self, 'speed', 2, delay=0.2+self.jumpUpDuration)
        invoke(setattr, self, 'leap_on_cooldown', False, delay=5)
        
    def land(self):
        # print('land')
        self.airTime = 0
        self.grounded = True

    def update(self):
        target = self.target
        dist = distance_xz(self.target.position, self.position)
        if dist > 40:
            return
        if dist < 2 and target.immuneTimer <= 0:
            target.hp -= 30
            target.immuneTimer = target.maxImmuneTimer
            target.healthbar.value -= 30
        #            healthbar.blink(color.tred)
        self.healthBar.alpha = max(0, self.healthBar.alpha - time.dt)
        if dist <15 and self.leap_on_cooldown ==False:
            self.leap()
        self.look_at_2d(target.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0, 1, 0), self.forward, 30, ignore=(self,))
        if hit_info.entity == target or self.grounded==False:
            if dist > 2:
                self.position += self.forward * time.dt * self.speed
        
        if self.gravity:
            # gravity
            ray = raycast(self.world_position + (0, self.height, 0), self.down, ignore=(self,))
            # ray = boxcast(self.world_position+(0,2,0), self.down, ignore=(self,))

            if ray.distance <= self.height + .1:
                if not self.grounded:
                    self.land()
                self.grounded = True
                # make sure it's not a wall and that the point is not too far up
                if ray.world_normal.y > .7 and ray.world_point.y - self.world_y < .5:  # walk up slope
                    self.y = ray.world_point[1]
                return
            else:
                self.grounded = False

            # if not on ground and not on way up in jump, fall
            self.y -= min(self.airTime, ray.distance - .05) * time.dt * 100
            self.airTime += time.dt * .25 * self.gravity

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            return
        
        self.healthBar.world_scale_x = self.hp / self.maxHp * 1.5
        self.healthBar.alpha = 1
