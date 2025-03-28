import pygame
from vector import Vector2
from constants import *

class Text(object):
    def __init__(self, text, color, x, y, size, time=None, id=None, visible=True):
        self.id = id
        self.text = text
        self.color = color
        self.size = size
        self.visible = visible
        self.position = Vector2(x, y)
        self.timer = 0
        self.lifespan = time
        self.label = None
        self.destroy = False
        self.setup_font("PressStart2P-Regular.ttf")
        self.create_label()


    def setup_font(self, fontpath):
        self.font = pygame.font.Font(fontpath, self.size)
        
    
    def create_label(self):
        self.label = self.font.render(self.text, 1, self.color)
        
        
    def set_text(self, new_text):
        self.text = str(new_text)
        self.create_label()
        
        
    def update(self, dt):
        if self.lifespan is not None:
            self.timer += dt
            if self.timer >= self.lifespan:
                self.timer = 0
                self.lifespan = None
                self.destroy = True
                    
                    
    def render(self, screen):
        if self.visible:
            x, y = self.position.as_tuple()
            screen.blit(self.label, (x, y))
            
            
class TextGroup(object):
    def __init__(self):
        self.next_id = 10
        self.all_text = {}
        self.setup_text()
        self.show_text(READY_TXT)
        
    
    def add_text(self, text, color, x, y, size, time=None, id=None):
        self.next_id += 1
        self.all_text[self.next_id] = Text(text, color, x, y, size, time=time, id=id)
        return self.next_id
    
    def remove_text(self, id):
        self.all_text.pop(id)
    
    
    def setup_text(self):
        size = TILE_HEIGHT
        self.all_text[SCORE_TXT] = Text("0".zfill(8), WHITE, 0, TILE_HEIGHT, size)
        self.all_text[LEVEL_TXT] = Text(str(1).zfill(3), WHITE, 23 * TILE_WIDTH, TILE_HEIGHT, size)
        self.all_text[READY_TXT] = Text("READY!",  YELLOW, 11.5 * TILE_WIDTH, 20 * TILE_HEIGHT, size, visible=False)
        self.all_text[PAUSE_TXT] = Text("PAUSED!", YELLOW, 10.625 * TILE_WIDTH, 20 * TILE_HEIGHT, size, visible=False)
        self.all_text[GAME_OVER_TXT] = Text("GAMEOVER!", YELLOW, 10 * TILE_WIDTH, 20 * TILE_HEIGHT, size, visible=False)
        self.add_text("SCORE", WHITE, 0, 0, size)
        self.add_text("LEVEL", WHITE, 23 * TILE_WIDTH, 0, size)
        
    
    def update(self, dt):
        for tkey in list(self.all_text.keys()):
            self.all_text[tkey].update(dt)
            if self.all_text[tkey].destroy:
                self.remove_text(tkey)
                
                
    def show_text(self, id):
        self.hide_text()
        self.all_text[id].visible = True
        
        
    def hide_text(self):
        self.all_text[READY_TXT].visible = False
        self.all_text[PAUSE_TXT].visible = False
        self.all_text[GAME_OVER_TXT].visible = False
        
        
    def update_score(self, score):
        self.update_text(SCORE_TXT, str(score).zfill(8))
        
        
    def update_level(self, level):
        self.update_text(LEVEL_TXT, str(level + 1).zfill(3))
        
        
    def update_text(self, id, value):
        if id in self.all_text.keys():
            self.all_text[id].set_text(value)
            
    
    def render(self, screen):
        for tkey in list(self.all_text.keys()):
            self.all_text[tkey].render(screen)