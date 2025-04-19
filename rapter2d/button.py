import pygame
from pygame.locals import *


class Button():
    STATE_IDLE = 'idle'
    STATE_ARMED = 'armed'
    STATE_DISARMED = 'disarmed'

    def __init__(self, window, loc, up, down):
        self.window = window
        self.loc = loc
        self.surfaceUp = up
        self.surfaceDown = down

        self.rect = self.surfaceUp.get_rect()
        self.rect[0] = loc[0]
        self.rect[1] = loc[1]

        self.state = Button.STATE_IDLE
    
    def getUpImage(self): return self.surfaceUp
    def getDownImage(self): return self.surfaceDown
    
    def setUpImage(self, up): self.surfaceUp = up
    def setDownImage(self, down): self.surfaceDown = down
    
    def handleEvent(self, eventObj):
        if eventObj.type not in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN):
            return False
        
        eventPointInButtonRect = self.rect.collidepoint(eventObj.pos)

        if self.state == Button.STATE_IDLE:
            if (eventObj.type == MOUSEBUTTONDOWN) and eventPointInButtonRect:
                self.state = Button.STATE_ARMED
            
        elif self.state == Button.STATE_ARMED:
            if (eventObj.type == MOUSEBUTTONUP) and eventPointInButtonRect:
                self.state = Button.STATE_IDLE
                return True

            if (eventObj.type == MOUSEMOTION) and (not eventPointInButtonRect):
                self.state = Button.STATE_DISARMED

        elif self.state == Button.STATE_DISARMED:
            if eventPointInButtonRect:
                self.state = Button.STATE_ARMED
            elif eventObj.type == MOUSEBUTTONUP:
                self.state = Button.STATE_IDLE

        return False
    
    def draw(self):
        if self.state == Button.STATE_ARMED:
            self.window.blit(self.surfaceDown, self.loc)
        else:
            self.window.blit(self.surfaceUp, self.loc)
