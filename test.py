# coding: utf-8

"""
Plusieurs tests ici :

- Pong basique
- affichage de sprites dans les coins
- texte
"""

from machine import Pin, SPI, Signal, DAC
import st7735
import rgb

import framebuf
import random
import utime
import time
import struct

_CASET=const(0x2A)
_RASET=const(0x2B)


"""
cs = 18
rst = 5
rs (dc) = 19
sck = 14
mosi = 13
miso = 12 -> pas branché
"""
# spi = SPI(1, baudrate=4000000, polarity=0, phase=0, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
# spi = SPI(1, baudrate=59000000, polarity=0, phase=0, sck=Pin(14), mosi=Pin(13), miso=Pin(12)) # ok
spi = SPI(1, baudrate=59000000, polarity=0, phase=0, sck=Pin(14), mosi=Pin(13), miso=Pin(12)) # 35 ok pour 128^2, trop haut + frmcrt bas = blanchi
display = st7735.ST7735R(spi, dc=Pin(19), cs=Pin(18), rst=Pin(5), width=130, height=130)
#display = st7735.ST7735R(SPI(1, baudrate=40000000), dc=Pin(12), cs=Pin(15), rst=Pin(16))
# display.fill(0x7521)
# display.pixel(64, 64, 0)

# dac = DAC(25)


# display.fill(rgb.color565(255,255,0))

black = rgb.color565(0,0,0)#rgb.color565(0,0,0)
red = rgb.color565(255,0,0)


fb = framebuf.FrameBuffer(bytearray(130*130*2), 130, 130, framebuf.RGB565)
fb.fill_rect(int(0),    int(0),    130,130, black)


pad = framebuf.FrameBuffer(bytearray(5*30*2), 5, 30, framebuf.RGB565)
pad.fill_rect(int(0),      int(0),      5,30, rgb.color565(255,125,0))
pad_erase = framebuf.FrameBuffer(bytearray(5*30*2), 5, 30, framebuf.RGB565)
pad_erase.fill_rect(int(0),      int(0),      5,30, rgb.color565(0,0,0))

# while True:
#     fb.fill_rect(int(0),    int(0),    128,128, rgb.color565(random.randint(0,100),random.randint(0,100),0))
#     t1 = utime.ticks_ms()
#     display.blit_buffer(fb, 0, 0, 128, 128)
#     print(utime.ticks_diff(t1, utime.ticks_ms()))


up = Signal(32, Pin.IN, Pin.PULL_UP, invert=True)
down = Signal(33, Pin.IN, Pin.PULL_UP, invert=True)

player_size = 8#16#8


with open("smile.raw", "rb") as f:
    smile_buf = f.read()
    smile = framebuf.FrameBuffer(bytearray(list(smile_buf)), 32, 32, framebuf.RGB565)
   

with open("ball.raw", "rb") as f:
# with open("bigball.raw", "rb") as f:
    ball_buf = f.read()
    player = framebuf.FrameBuffer(bytearray(list(ball_buf)), player_size, player_size, framebuf.RGB565)

# player = framebuf.FrameBuffer(bytearray(player_size*player_size*2), player_size, player_size, framebuf.RGB565)
# player.fill_rect(int(0),      int(0),      player_size,player_size, rgb.color565(255,255,255))
player_erase = framebuf.FrameBuffer(bytearray(player_size*player_size*2), player_size, player_size, framebuf.RGB565)
player_erase.fill_rect(int(0),      int(0),      player_size,player_size, black)


def collision(pad_x,pad_y,pad_width,pad_height,
                  player_x,player_y,player_width,player_height):

    if (float(pad_x) < float(player_x) + float(player_width) and
            float(pad_x) + float(pad_width) > float(player_x) and
            float(pad_y) < float(player_y) + float(player_height) and
            float(pad_height) + float(pad_y) > float(player_y)):
        return True
    else:
        return False

def move(display, speed_x, speed_y):
    bound = 128
    x = y = old_x = old_y = 0.0
    x = 30
    move_x = speed_x
    move_y = speed_y

    pad_x = 0.0
    pad_old_x = 0.0

    counter = 0

    times = []

    # display._write(_CASET, b'\x00\x02\x00\x81')
    # display._write(_RASET, b'\x00\x01\x00\x80')

   
    

    while True:
        t1 = utime.ticks_ms()

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
            # dac.wavplay('test.wav', 3)
        if y > bound-player_size or y < 0:
            move_y = -move_y
            # dac.wavplay('test.wav', 3)
        x += move_x
        y += move_y


        

        
        fb.blit(player_erase,int(old_x),int(old_y)) # OK
        fb.blit(player,int(x),int(y)) # OK

        fb.blit(pad_erase, 0, int(pad_old_x)) # OK
        fb.blit(pad, 0, int(pad_x)) # OK

        # display.blit_buffer(fb, 0, 0, display.width, display.height)
        display.blit_buffer(fb, 0, 0, 128, 128)
        

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


        # au delà de 40 fps, l'écran laisse des lignes blanches
        # utime.sleep_ms(15) 

        utime.sleep_ms(35 - abs(utime.ticks_diff(t1, utime.ticks_ms())))
        # time.sleep_ms(35 - abs(utime.ticks_diff(t1, utime.ticks_ms()))) # lobo
        # time.sleep_ms(500)
        # utime.sleep_ms(30)

        times.append(utime.ticks_diff(t1, utime.ticks_ms()))
        counter += 1
        if counter > 10:
            counter = 0
            print(sum(times) / len(times))
            times = []

def test(display):
    # display.fill(black)
    # sw = True
    # display._write(_CASET, b'\x00\x02\x00\x81')
    # display._write(_RASET, b'\x00\x03\x00\x82')
    fb.blit(player,2,1) # OK
    fb.blit(player,122, 121) # OK
    display.blit_buffer(fb, 0,0, 130,130)
    # while True:
    #     sw = not sw
    #     if sw:
    #         display.blit_buffer(player_erase, 50, 50, 8, 8)
    #         display.blit_buffer(player, 50, 58, 8, 8)
    #     else:
    #         display.blit_buffer(player_erase, 50, 58, 8, 8)
    #         display.blit_buffer(player, 50, 50, 8, 8)
    #     utime.sleep_ms(20)

def text(display):
    display.fill(black)
    with open("text.raw", "rb") as f:
        ball_buf = f.read()
        player = framebuf.FrameBuffer(bytearray(list(ball_buf)), 16, 16, framebuf.RGB565)
    display.blit_buffer(player, 50, 50, 16, 16)

    with open("isyou.raw", "rb") as f:
        ball_buf = f.read()
        player = framebuf.FrameBuffer(bytearray(list(ball_buf)), 16, 16, framebuf.RGB565)
    display.blit_buffer(player, 50, 80, 16, 16)
    

test(display)
# move(display, 1,1)
# text(display)