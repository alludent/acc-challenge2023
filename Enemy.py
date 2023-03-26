from direct.actor.Actor import Actor
from ursina import *

class Enemy(Entity):
    shootables_parent = Entity()

    def __init__(self, target, **kwargs):
        super().__init__(parent=Enemy.shootables_parent, model='cube', origin_y=-.5, color=color.light_gray, collider='box',
                         **kwargs)
        self.target = target
        self.setScale(1, 2.4, 3)

        self.collider = 'box'
        self.alpha = 0
        self.actor = Actor("Entities/ODIUS/ODIUS.glb")
        self.actor.reparent_to(self)
        self.actor.setPos(0, 0.4, 0)
        self.actor.setScale(1 / self.scale_x, 1 / self.scale_y, 1 / self.scale_z)
        self.actor.setHpr(180, 0, 0)
        self.actor.loop("Leap")  # use .play() instead of loop() to play it once.

        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5, .1, .1))
        self.max_hp = 100
        self.hp = self.max_hp
        self.speed = 2

    def update(self):
        target = self.target
        dist = distance_xz(self.target.position, self.position)
        if dist > 40:
            return
        if dist < 2 and target.immune_timer <= 0:
            target.hp -= 30
            target.immune_timer = target.max_immune_timer
        #            healthbar.blink(color.tred)
        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)

        self.look_at_2d(target.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0, 1, 0), self.forward, 30, ignore=(self,))
        if hit_info.entity == target:
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
