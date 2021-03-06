import pygame, sys
from pygame.locals import *
import keyboard
from pysplit import *
from sys import argv
try:
    import configmenu
except ImportError:
    print('Error while importing config menu, wxpython is probably not installed')
    configmenu = None

# how many digits to show
N_DECIMAL = 2
# used to get if key is pressed
KEYS_DOWN = []

def rgb(h):
    return (
        (h & 0xff0000) >> 16,
        (h & 0x00ff00) >> 8,
        (h & 0x0000ff)
    )
class colors:
    background = rgb(0),
    backgroundalt = rgb(0x070707)
    text = rgb(0xffffff),
    faster = rgb(0x6dce52),
    slower = rgb(0xf2463a),
    gold = rgb(0xf2d235),
    current = rgb(0x59a6d6)

if len(argv) == 2:
    name = argv[1]
else:
    name = input('Splits file: ')
if name in ('none','None',''):
    run = None
elif name.endswith('.lss'):
    run = Run.from_lss(name)
else:
    run = Run.from_json(name)
timer = Timer(run)

# space for the title / timer
offset = 50
# remove title space if run is none
if timer.run == None: offset //= 2
width, height = 300, offset*2
segHeight = 50
if timer.run: height += len(run.segments)*segHeight
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

def reset(*args):
    timer.reset()

keyboard.on_press_key('f6', reset)

def open_config():
    global height
    global size
    global screen
    if timer.state != TimerState.NOTHING:
        print('Cannot open config menu while running')
        return
    if timer.run == None:
        print('Cannot open config menu for non existent run')
        return
    configmenu.configMenu.open(timer.run)
    height = offset*2 + len(run.segments) * segHeight
    size = (width, height)
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)

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
        return surface, x+xoff, y+yoff
    except pygame.error:
        pass

def draw_segments():
    current_seg = len(timer.times)
    s = 0
    for i, seg in enumerate(run.segments):
        color = colors.background if i % 2 == 0 else colors.backgroundalt
        if timer.state != TimerState.NOTHING and i == current_seg:
            color = colors.current
        pygame.draw.rect(screen, color, (0,segHeight*i+offset,width,segHeight),0)
        draw_text(seg.name,5,int(segHeight*(i+0.5))+offset,int(segHeight//1.5),alignY='center')
        if seg.pb != None:
            s += seg.pb
            time = s if i > current_seg - 1 else sum(timer.times[:i+1])
            draw_text(format_time(time,decimal_places=N_DECIMAL if time < 60 else False),
                width-5,int(segHeight*(i+0.5))+offset,segHeight//3,align='right',alignY='center',font='ubuntumedium,ubuntumono')
            if i < current_seg and timer.state != TimerState.NOTHING:
                color = colors.slower
                if seg.best >= timer.times[i]:
                    color = colors.gold
                elif seg.pb > timer.times[i]:
                    color = colors.faster
                dt = sum(timer.times[:i+1])-s
                dt = ('+' if dt > 0 else '') + format_time(dt, decimal_places=N_DECIMAL)

                draw_text(dt, width*2//3, int(segHeight*(i+0.5))+offset, segHeight//3,
                    color=color, align='center', font='ubuntumedium,ubuntumono')
        elif i < current_seg:
            time = sum(timer.times[:i+1])
            draw_text(format_time(time,decimal_places=N_DECIMAL if time < 60 else False),
                width-5,int(segHeight*(i+0.5))+offset,segHeight//3,align='right',alignY='center',font='ubuntumedium,ubuntumono')
def isPressed(key):
    # returns true if the key has just been pressed
    try:
        tmp = KEYS_DOWN[key]
    except IndexError:
        return pygame.key.get_pressed()[key]
    else:
        return not tmp and pygame.key.get_pressed()[key]

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.display.quit()
            sys.exit(0)
        elif event.type == VIDEORESIZE:
            size = width,height = event.size
            screen = pygame.display.set_mode(size, pygame.RESIZABLE)

    if configmenu != None and isPressed(pygame.K_F7):
        open_config()

    screen.fill(colors.background)

    if timer.run != None:
        draw_segments()
        pygame.draw.rect(screen,colors.backgroundalt,(0,0,width,offset),0)
        draw_text(run.name,width/2,13,26,align='center')
        draw_text(run.category,width/2,30,20,align='center')
    draw_text(format_time(timer.time(force=True),decimal_places=N_DECIMAL),width-5,height-offset//(2 if timer.run else 1),40,font='ubuntumedium,ubuntu',align='right',alignY='center')
 
    pygame.display.update()
    KEYS_DOWN = pygame.key.get_pressed()