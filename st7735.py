# coding: utf-8

"""
Un module de gestion de l'écran que je reprends directement d'un ancien dépôt
d'Adafruit : https://github.com/adafruit/micropython-adafruit-rgb-display

À remplacer par quelque chose de plus actuel.

Largement hacké pour faire fonctionner les écrans que j'ai à ma disposition
actuellement :

- un 128x160 en red tab (languette rouge), uniquement pour tester car je souhaite 128x128
- un 128x128 en red tab
- un 128x128 en green tab

Le green tab est celui qui donne les meilleurs résultats, mais l'offset qu'on 
paramètre avec CASET et RASET laisse toujour une ligne en « noise ».
J'ai trouvé un contournement pour ça mais il faudrait régler correctement le problème.

"""

from rgb import DisplaySPI, color565
import ustruct


_NOP=const(0x00)
_SWRESET=const(0x01)
_RDDID=const(0x04)
_RDDST=const(0x09)

_SLPIN=const(0x10)
_SLPOUT=const(0x11)
_PTLON=const(0x12)
_NORON=const(0x13)

_INVOFF=const(0x20)
_INVON=const(0x21)
_DISPOFF=const(0x28)
_DISPON=const(0x29)
_CASET=const(0x2A)
_RASET=const(0x2B)
_RAMWR=const(0x2C)
_RAMRD=const(0x2E)

_PTLAR=const(0x30)
_COLMOD=const(0x3A)
_MADCTL=const(0x36)

_FRMCTR1=const(0xB1)
_FRMCTR2=const(0xB2)
_FRMCTR3=const(0xB3)
_INVCTR=const(0xB4)
_DISSET5=const(0xB6)

_PWCTR1=const(0xC0)
_PWCTR2=const(0xC1)
_PWCTR3=const(0xC2)
_PWCTR4=const(0xC3)
_PWCTR5=const(0xC4)
_VMCTR1=const(0xC5)

_RDID1=const(0xDA)
_RDID2=const(0xDB)
_RDID3=const(0xDC)
_RDID4=const(0xDD)

_PWCTR6=const(0xFC)

_GMCTRP1=const(0xE0)
_GMCTRN1=const(0xE1)

_TEOFF=const(0x34)
_TEON=const(0x35)
_IDMOFF=const(0x38)
_IDMON=const(0x39)
_GAMSET=const(0x26)


class ST7735(DisplaySPI):
    """
    A simple driver for the ST7735-based displays.

    >>> from machine import Pin, SPI
    >>> import st7735
    >>> display = st7735.ST7735(SPI(1), dc=Pin(12), cs=Pin(15), rst=Pin(16))
    >>> display = st7735.ST7735R(SPI(1, baudrate=40000000), dc=Pin(12), cs=Pin(15), rst=Pin(16))
    >>> display.fill(0x7521)
    >>> display.pixel(64, 64, 0)

    """
    _COLUMN_SET = _CASET
    _PAGE_SET = _RASET
    _RAM_WRITE = _RAMWR
    _RAM_READ = _RAMRD
    _INIT = (
        (_SWRESET, None),
        (_SLPOUT, None),

        # custom ###############################

        (_COLMOD, b'\x05'), # 16bit color
        (_DISPON, None),
        (_MADCTL, b'\x08'), # bottom to top refresh
        (_CASET, b'\x00\x02\x00\x81'), # XSTART = 2, XEND = 129
        (_RASET, b'\x00\x02\x00\x81'), # YSTART = 2, YEND = 129
        

        # end custom ###########################

        # (_MADCTL, b'\x08'), # bottom to top refresh
        # (_COLMOD, b'\x05'), # 16bit color
        # (_INVCTR, b'0x00'), # line inversion

        # # 1 clk cycle nonoverlap, 2 cycle gate rise, 3 sycle osc equalie,
        # # fix on VTL
        # (_DISSET5, b'\x15\x02'),
        # # fastest refresh, 6 lines front porch, 3 line back porch
        # (_FRMCTR1, b'\x00\x06\x03'),

        # (_PWCTR1, b'\x02\x70'), # GVDD = 4.7V, 1.0uA
        # (_PWCTR2, b'\x05'), # VGH=14.7V, VGL=-7.35V
        # (_PWCTR3, b'\x01\x02'), # Opamp current small, Boost frequency
        # (_PWCTR6, b'\x11\x15'),

        # (_VMCTR1, b'\x3c\x38'), # VCOMH = 4V, VOML = -1.1V

        # (_GMCTRP1, b'\x09\x16\x09\x20\x21\x1b\x13\x19'
        #            b'\x17\x15\x1e\x2b\x04\x05\x02\x0e'), # Gamma
        # (_GMCTRN1, b'\x08\x14\x08\x1e\x22\x1d\x18\x1e'
        #            b'\x18\x1a\x24\x2b\x06\x06\x02\x0f'),

        # (_CASET, b'\x00\x02\x00\x81'), # XSTART = 2, XEND = 129
        # (_RASET, b'\x00\x02\x00\x81'), # YSTART = 2, YEND = 129

        # (_NORON, None),
        # (_DISPON, None),
    )
    _ENCODE_PIXEL = ">H"
    _ENCODE_POS = ">HH"

    def __init__(self, spi, dc, cs, rst=None, width=128, height=128):
        super().__init__(spi, dc, cs, rst, width, height)


class ST7735R(ST7735):
    _INIT = (
        (_SWRESET, None),
        
        # (_IDMON,None), # avec ça lag, mais les traits noirs disparaissent
        (_SLPOUT, None),
        (_INVOFF, None),
        # (_INVON, None), # À RETIRER : INVERSION DES COULEURS

        # (_TEON, b'\x01'),

        # custom ###############################

        (_COLMOD, b'\x05'), # 16bit color
        # (_COLMOD, b'\x03'), # 12bit color
        # (_FRMCTR1, b'\x01\x2c\x2d'),
        # (_FRMCTR2, b'\x01\x2c\x2d'),
        # (_FRMCTR3, b'\x01\x2c\x2d\x01\x2c\x2d'),
        (_DISPON, None),
        # (_MADCTL, bytearray([0b10110000])), # fonctionnel 160 -> RGB
        # (_MADCTL, bytearray([0b10111000])), # fonctionnel -> BGR
        # (_MADCTL, bytearray([0b01111000])), # fonctionnel -> BGR
        
        # (_MADCTL, bytearray([0b01100000])), # 
        (_MADCTL, b'\x08'), # 

        # (_MADCTL, bytearray([0b01000100])), # bottom to top refresh
        (_DISSET5, b'\x15\x02'), # ok 160
        # (_FRMCTR1, b'\x06\x01\x00'), # 128x128 blue
        (_FRMCTR1, b'\x00\x00\x00'), # 128x160 et 128^2 green tab ABSOLUMENT NECESSAIRE POUR NE PAS AVOIR LES TRAITS NOIRS
        # (_FRMCTR1, b'\x00\x06\x03'),
        # (_IDMOFF,None),


        # (_PWCTR1, b'\x00\x00\x00'),
        ################# si je désactive les pwctr ci-dessous, c'est mieux pour les lignes noires
        # (_PWCTR1, b'\xa2\x02\x44'),
        # (_PWCTR2, b'\xc5'),
        # (_PWCTR3, b'\x0a\x00'),
        # (_PWCTR4, b'\x8a\x2a'),
        # (_PWCTR5, b'\x8a\xee'),


        # (_CASET, b'\x00\x02\x00\x81'), 
        # (_RASET, b'\x00\x02\x00\x81'), 
        (_CASET, b'\x00\x00\x00\x7F'), 
        (_RASET, b'\x00\x00\x00\x7F'), 


        # (_CASET, b'\x00\x01\x00\x30'), # XSTART = 2, XEND = 129
        # (_RASET, b'\x00\x05\x00\x30'), # YSTART = 2, YEND = 129
        # (_RAMWR, None),

        (_GAMSET, b'\x02'),

        (_GMCTRP1, b'\x09\x16\x09\x20\x21\x1b\x13\x19'
                   b'\x17\x15\x1e\x2b\x04\x05\x02\x0e'), # Gamma
        (_GMCTRN1, b'\x08\x14\x08\x1e\x22\x1d\x18\x1e'
                   b'\x18\x1a\x24\x2b\x06\x06\x02\x0f'),
        

        # end custom ###########################

        # (_MADCTL, b'\xc8'),
        # (_COLMOD, b'\x05'), # 16bit color
        # (_INVCTR, b'\x07'),

        # (_FRMCTR1, b'\x01\x2c\x2d'),
        # (_FRMCTR2, b'\x01\x2c\x2d'),
        # (_FRMCTR3, b'\x01\x2c\x2d\x01\x2c\x2d'),

        # (_PWCTR1, b'\x02\x02\x84'),
        # (_PWCTR2, b'\xc5'),
        # (_PWCTR3, b'\x0a\x00'),
        # (_PWCTR4, b'\x8a\x2a'),
        # (_PWCTR5, b'\x8a\xee'),

        # (_VMCTR1, b'\x0e'),
        # (_INVOFF, None),

        # (_GMCTRP1, b'\x02\x1c\x07\x12\x37\x32\x29\x2d'
        #            b'\x29\x25\x2B\x39\x00\x01\x03\x10'), # Gamma
        # (_GMCTRN1, b'\x03\x1d\x07\x06\x2E\x2C\x29\x2D'
        #            b'\x2E\x2E\x37\x3F\x00\x00\x02\x10'),
        # (_NORON, None),
        # (_DISPON, None),
    )

    def __init__(self, spi, dc, cs, rst=None, width=128, height=128):
        super().__init__(spi, dc, cs, rst, width, height)

    def init(self):
        super().init()
        cols = ustruct.pack('>HH', 0, self.width - 1)
        rows = ustruct.pack('>HH', 0, self.height - 1)
        for command, data in (
            # (_CASET, cols),
            # (_RASET, rows),

            (_NORON, None),
            (_DISPON, None),
        ):
            self._write(command, data)
