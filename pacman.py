import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites

class Pacman(Entity):
    def __init__(self, node):
        super().__init__(node)
        self.name = PACMAN
        self.directions = {STOP:Vector2(), UP:Vector2(0,-1), DOWN:Vector2(0,1), LEFT:Vector2(-1,0), RIGHT:Vector2(1,0)}
        self.direction = STOP
        self.speed = 100 * TILE_WIDTH / 16
        self.radius = 10
        self.color = YELLOW
        self.direction = LEFT
        self.set_between_nodes(LEFT)
        self.node = node
        # self.setPosition()
        self.target = node
        self.collideRadius = 5
        self.alive = True
        self.sprites = PacmanSprites(self)
        
    def reset(self):
        super().reset()
        self.direction = LEFT
        self.set_between_nodes(LEFT)
        self.alive = True
        self.image = self.sprites.get_start_image()
        self.sprites.reset()
        
    def die(self):
        self.alive = False
        self.direction = STOP
        
    def set_position(self):
        self.position = self.node.position.copy()
        
    def update(self, dt):
        self.sprites.update(dt)	
        self.position += self.directions[self.direction] * self.speed * dt
        direction = self.get_valid_key()
        if self.overshot_target():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.get_new_target(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.get_new_target(self.direction)
            if self.target is self.node:
                self.direction = STOP
            self.set_position()
        else: 
            if self.opposite_direction(direction):
                self.reverse_direction()
            
    def valid_direction(self, direction):
        if direction is not STOP:
            if self.node.neighbors[direction] is not None:
                return True
        return False
    
    def get_new_target(self, direction):
        if self.valid_direction(direction):
            return self.node.neighbors[direction]
        return self.node
    
    def overshot_target(self):
        if self.target is not None:
            vec1 = self.target.position - self.node.position
            vec2 = self.position - self.node.position
            node_to_target = vec1.magnitude_squared()
            node_to_self = vec2.magnitude_squared()
            return node_to_self >= node_to_target
        return False
    
    def reverse_direction(self):
        self.direction *= -1
        temp = self.node
        self.node = self.target
        self.target = temp
        
    def opposite_direction(self, direction):
        if direction is not STOP:
            if direction == self.direction * -1:
                return True
        return False
    
    def get_valid_key(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP
    
    def eat_pellets(self, pellet_list):
        for pellet in pellet_list:
           if self.collide_check(pellet):
                return pellet
        return None
    
    def collide_ghost(self,ghost):
        return self.collide_check(ghost)
    
    def collide_check(self, other):
        d = self.position - other.position
        d_squared = d.magnitude_squared()
        r_squared = (self.collide_radius + other.collide_radius)
        if d_squared <= r_squared:
            return True
        return False
    