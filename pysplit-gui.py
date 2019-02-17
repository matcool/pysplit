import pygame, sys
from pygame.locals import *
import keyboard
from pysplit import *

# yes hardcoded file great code
run = Run.from_json('test.json')
timer = Timer(run)
width, height = 300, 100
segHeight = 50
segGap = 10
height += len(run.segments)*segHeight
size = (width, height)
screen = pygame.display.set_mode(size, pygame.RESIZABLE)
pygame.display.set_caption('PySplit')
pygame.init()

def start_or_split(*args):
    if timer.state == TimerState.NOTHING:
        timer.start()
    elif timer.state == TimerState.RUNNING:
        timer.split()
    elif timer.state == TimerState.ENDED:
        timer.reset()

keyboard.on_press_key('f5',start_or_split)

def draw_text(text,x,y,size,color=(255,255,255),font=None,align=None,alignY=None):
    try:
        font = pygame.font.SysFont(font, size)
        surface = font.render(text,1,color)
        xoff = 0
        yoff = 0
        if align == 'center':
            xoff = -surface.get_width()/2
            if alignY == None:
                yoff = -surface.get_height()/2
        if align == 'right':
            xoff = -surface.get_width()
        if alignY == 'center':
            yoff = -surface.get_height()/2
        screen.blit(surface,(x+xoff,y+yoff))
    except pygame.error:
        pass

def draw_segments():
    current_seg = len(timer.times)
    s = 0
    for i, seg in enumerate(run.segments):
        color = (255,255,255)
        if timer.state != TimerState.NOTHING:
            if i == current_seg:
                color = (82,159,206)
            elif i < current_seg:
                color = (109,206,82)
        draw_text(seg.name,0,segHeight*i+50,segHeight-segGap,color=color)
        if seg.pb != None:
            t = seg.pb
            if i > current_seg - 1:
                draw_text(format_time(t+s,decimal_places=2) if t+s < 60 else format_time(int(t+s),decimal_places=2),
                    width-5,segHeight*i+50+segHeight//6,segHeight//3,align='right',alignY='center',font='ubuntumedium')
            s += t

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.display.quit()
            sys.exit(0)
        elif event.type == VIDEORESIZE:
            size = width,height = event.size
            screen = pygame.display.set_mode(size, pygame.RESIZABLE)
    screen.fill((0,0,0))

    draw_segments()
    draw_text(run.name,width/2,13,26,align='center')
    draw_text(run.category,width/2,30,20,align='center')
    draw_text(format_time(timer.time(force=True),decimal_places=2),width-10,height-50,40,font='ubuntumedium',align='right')

    pygame.display.update() 