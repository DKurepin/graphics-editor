from enum import Enum

from imageclasses import *


class ColorSpace(Enum):
    RGB = RGBImage(),
    HSL = HSLImage(),
    HSV = HSVImage(),
    YCbCr601 = YCbCr601Image(),
    YCbCr709 = YCbCr709Image(),
    YCoCg = YCoCgImage(),
    CMY = CMYImage()

