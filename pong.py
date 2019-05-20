# coding: utf-8

"""
Pong solo
"""

from machine import Pin, SPI, Signal,
import st7735
import rgb
import framebuf
import utime

"""
cs = 18
rst = 5
rs (dc) = 19
sck = 14
mosi = 13
"""

spi = SPI(1, baudrate=59000000, polarity=0, phase=0, sck=Pin(14), mosi=Pin(13), miso=Pin(12)) # 35 ok pour 128^2, trop haut + frmcrt bas = blanchi
display = st7735.ST7735R(spi, dc=Pin(19), cs=Pin(18), rst=Pin(5), width=130, height=130)


# Convertion RGB vers 565 des couleurs.
black = rgb.color565(0,0,0)
red = rgb.color565(255,0,0)

# Le framebuffer principal sur lequel on blit tout. 
# Ce FB sera lui-même blité à la fin sur l'écran via SPI en intégralité.
fb = framebuf.FrameBuffer(bytearray(130*130*2), 130, 130, framebuf.RGB565)
fb.fill_rect(int(0),    int(0),    130,130, red)

# Le palet (joueur).
pad = framebuf.FrameBuffer(bytearray(5*30*2), 5, 30, framebuf.RGB565)
pad.fill_rect(int(0),      int(0),      5,30, rgb.color565(255,125,0))
# Un rectangle de la taille du palet et de la couleur du fond pour effacer
# le palet après un mouvement.
pad_erase = framebuf.FrameBuffer(bytearray(5*30*2), 5, 30, framebuf.RGB565)
pad_erase.fill_rect(int(0),      int(0),      5,30, rgb.color565(0,0,0))


# Les boutons de déplacement.
"""
La classe Signal est utilisée plutôt que Pin afin de pouvoir inverser les valeurs.
Un bouton mis à la masse va renvoyer True (si on appele up() par exemple) plutôt que
False, ce qui est plus logique d'un point de vue programmation.
"""
up = Signal(32, Pin.IN, Pin.PULL_UP, invert=True)
down = Signal(33, Pin.IN, Pin.PULL_UP, invert=True)

player_size = 8

# Buffer pour le sourir de la victoire.
with open("smile.raw", "rb") as f:
    smile_buf = f.read()
    smile = framebuf.FrameBuffer(bytearray(list(smile_buf)), # buffer
                                 32, # width
                                 32, # height
                                 framebuf.RGB565) # encodage couleur
   
# Buffer pour la balle.
with open("ball.raw", "rb") as f:
    ball_buf = f.read()
    player = framebuf.FrameBuffer(bytearray(list(ball_buf)), 
                                  player_size, 
                                  player_size, 
                                  framebuf.RGB565)

# Buffer de la taille de celui de ball.raw pour effacer la balle après déplacement.
player_erase = framebuf.FrameBuffer(bytearray(player_size*player_size*2), 
                                    player_size, 
                                    player_size, 
                                    framebuf.RGB565)
player_erase.fill_rect(int(0), int(0), player_size, player_size, black)


def collision(pad_x, pad_y, pad_width,pad_height,
              player_x, player_y, player_width, player_height):
    """
    Détection simple de collision (pour deux rectangles).
    """

    if (float(pad_x) < float(player_x) + float(player_width) and
            float(pad_x) + float(pad_width) > float(player_x) and
            float(pad_y) < float(player_y) + float(player_height) and
            float(pad_height) + float(pad_y) > float(player_y)):
        return True
    else:
        return False


def move(display, speed_x, speed_y):
    t1 = utime.ticks_ms()

    bound = 128
    x = y = old_x = old_y = 0.0
    x = 30
    move_x = speed_x
    move_y = speed_y
    pad_x = 0.0
    pad_old_x = 0.0

    while True:
        pad_old_x = pad_x
        if up():
            pad_x += 5
            pad_x = min(98, pad_x)
        if down():
            pad_x -= 5
            pad_x = max(0, pad_x)
       
        old_x = x
        old_y = y
        if x > bound-player_size or x < 0:
            move_x = -move_x
        if y > bound-player_size or y < 0:
            move_y = -move_y
        x += move_x
        y += move_y

        offset_x = 2
        offset_y = 1

        fb.blit(player_erase, 
                int(old_x)+offset_x,
                int(old_y)+offset_y) # OK
        fb.blit(player,
                int(x)+offset_x,
                int(y)+offset_y,0) # Le 0 est l'argument 'key' pour la transparence.

        fb.blit(pad_erase, 
                0+offset_x, 
                int(pad_old_x)+offset_y) # OK
        fb.blit(pad, 
                0+offset_x, 
                int(pad_x)+offset_y) # OK

        # display.blit_buffer(fb, 0, 0, 128, 128)
        display.blit_buffer(fb, 0,0, 130,130)
        
        if collision(pad_x=0,pad_y=pad_x,pad_width=5,pad_height=30,
                  player_x=x,player_y=y,player_width=player_size,player_height=player_size):
                  display.blit_buffer(smile, 50, 50, 32, 32)
                  utime.sleep_ms(1000)
                  smile_erase = framebuf.FrameBuffer(bytearray(32*32*2), 32,32, framebuf.RGB565)
                  smile_erase.fill_rect(int(0),      int(0),      32,32, black)
                  display.blit_buffer(smile_erase, 50, 50, 32, 32)
                  move_x = -move_x
                  fb.blit(player_erase,int(old_x),int(old_y)) # OK
                  fb.blit(player_erase,int(x),int(y)) # OK
                  x = 5
                  old_x = x

        utime.sleep_ms(35 - abs(utime.ticks_diff(t1, utime.ticks_ms())))
        

move(display, 1,1)