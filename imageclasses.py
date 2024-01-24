from abc import ABC, abstractmethod

from PyQt6.QtGui import QPixmap, QImage

from canalclasses import *
from conversions import *


class AbstractImage(ABC):
    def __init__(self, width=None, height=None, pixels=None):
        self.width = width
        self.height = height
        self.pixels = pixels
        self.rgb_pixels = None

    def to_qpixmap(self):
        return self.to_rgb().to_qpixmap()

    def get_wh(self):
        return self.width, self.height

    @abstractmethod
    def to_rgb(self):
        pass

    @abstractmethod
    def canal(self, canal):
        pass

    @abstractmethod
    def write_to_file(self, file_path):
        pass


class RGBImage(AbstractImage):

    def __init__(self, width=None, height=None, pixels=None):
        super().__init__(width, height, pixels)
        color_space = ["RGB", "HSL", "HSV", "YCbCr601", "YCbCr709", "YCoCg", "CMY"]
        conversions = [self.to_rgb, self.to_hsl, self.to_hsv, self.to_ycbcr601,
                       self.to_ycbcr709, self.to_ycocg, self.to_cmy]
        self.conversions_map = dict(zip(color_space, conversions))

    def canal(self, canal):
        pixels = bytearray(len(self.pixels) // 3)
        for i in range(canal, len(self.pixels), 3):
            pixels[i // 3] = self.pixels[i]
        return bytecanal(self.width, self.height, pixels)

    def convert_to(self, color_space):
        if color_space not in self.conversions_map.keys():
            raise Exception('Invalid color space format!')
        return self.conversions_map[color_space]()

    def to_hsl(self):
        return HSLImage(self.width, self.height, rgb_to_hsl(self.pixels))

    def to_hsv(self):
        return HSVImage(self.width, self.height, rgb_to_hsv(self.pixels))

    def to_ycbcr601(self):
        return YCbCr601Image(self.width, self.height, rgb_to_ycbcr601(self.pixels))

    def to_ycbcr709(self):
        return YCbCr709Image(self.width, self.height, rgb_to_ycbcr709(self.pixels))

    def to_ycocg(self):
        return YCoCgImage(self.width, self.height, rgb_to_ycocg(self.pixels))

    def to_cmy(self):
        return CMYImage(self.width, self.height, rgb_to_cmy(self.pixels))

    def to_rgb(self):
        return self

    def to_qpixmap(self):
        return QPixmap.fromImage(QImage(self.pixels, self.width, self.height, QImage.Format.Format_RGB888))

    def write_to_file(self, file_path):
        with open(file_path, 'wb') as file:
            file.write(f'{__class__.__name__[:-5]}\n'.encode())
            file.write(f'{self.width} {self.height}\n'.encode())
            file.write(self.pixels)

    @staticmethod
    def read_from_file(file_path):
        with open(file_path, 'rb') as file:
            first_string = file.readline().decode().rstrip('\n')
            if first_string == 'P6':
                width, height = map(int, file.readline().decode().split())
                max_value = int(file.readline().decode().rstrip('\n'))
                pixels = file.read()
                return RGBImage(width, height, pixels)
            elif first_string == 'P5':
                width, height = map(int, file.readline().decode().split())
                max_value = int(file.readline().decode().rstrip('\n'))
                pixels = file.read()
                return GrayImage(width, height, pixels)
            else:
                if first_string != 'RGB':
                    raise Exception('Invalid color format')
                width, height = map(int, file.readline().decode().split())
                return RGBImage(width, height, file.read())



class CMYImage(AbstractImage):


    def canal(self, canal):
        pixels = bytearray(len(self.pixels) // 3)
        for i in range(canal, len(self.pixels), 3):
            pixels[i // 3] = self.pixels[i]
        return bytecanal(self.width, self.height, pixels)

    def to_rgb(self):
        if self.rgb_pixels is None:
            self.rgb_pixels = cmy_to_rgb(self.pixels)
        return RGBImage(self.width, self.height, self.rgb_pixels)

    def write_to_file(self, file_path):
        with open(file_path, 'wb') as file:
            file.write(f'{__class__.__name__[:-5]}\n'.encode())
            file.write(f'{self.width} {self.height}\n'.encode())
            file.write(self.pixels)

    @staticmethod
    def read_from_file(file_path):
        with open(file_path, 'rb') as file:
            color_space = file.readline().decode().rstrip('\n')
            width, height = map(int, file.readline().decode().split())
            return CMYImage(width, height, bytearray(file.read()))


class HSLImage(AbstractImage):

    def canal(self, canal):
        pixels = [self.pixels[i] for i in range(canal, len(self.pixels), 3)]
        if canal == 0:
            return huecanal(self.width, self.height, pixels)
        else:
            return zerotoonecanal(self.width, self.height, pixels)

    def to_rgb(self):
        if self.rgb_pixels is None:
            self.rgb_pixels = hsl_to_rgb(self.pixels)
        return RGBImage(self.width, self.height, self.rgb_pixels)

    def write_to_file(self, file_path):
        with open(file_path, 'wb') as file:
            file.write(f'{__class__.__name__[:-5]}\n'.encode())
            file.write(f'{self.width} {self.height}\n'.encode())
            write_pixels = bytearray(len(self.pixels))
            for i in range(0, len(self.pixels), 3):
                write_pixels[i] = int(self.pixels[i] / 360 * 255 + 0.5)
                write_pixels[i + 1] = int(self.pixels[i + 1] * 255 + 0.5)
                write_pixels[i + 2] = int(self.pixels[i + 2] * 255 + 0.5)
            file.write(write_pixels)

    @staticmethod
    def read_from_file(file_path):
        with open(file_path, 'rb') as file:
            color_space = file.readline().decode().rstrip('\n')
            width, height = map(int, file.readline().decode().split())
            byte_pixels = bytearray(file.read())
            pixels = [0] * len(byte_pixels)
            for i in range(0, len(byte_pixels), 3):
                pixels[i] = byte_pixels[i] / 255 * 360
                pixels[i + 1] = byte_pixels[i + 1] / 255
                pixels[i + 2] = byte_pixels[i + 2] / 255
            return HSLImage(width, height, pixels)


class HSVImage(AbstractImage):

    def canal(self, canal):
        pixels = [self.pixels[i] for i in range(canal, len(self.pixels), 3)]
        if canal == 0:
            return huecanal(self.width, self.height, pixels)
        else:
            return zerotoonecanal(self.width, self.height, pixels)

    def to_rgb(self):
        if self.rgb_pixels is None:
            self.rgb_pixels = hsv_to_rgb(self.pixels)
        return RGBImage(self.width, self.height, self.rgb_pixels)

    def write_to_file(self, file_path):
        with open(file_path, 'wb') as file:
            file.write(f'{__class__.__name__[:-5]}\n'.encode())
            file.write(f'{self.width} {self.height}\n'.encode())
            write_pixels = bytearray(len(self.pixels))
            for i in range(0, len(self.pixels), 3):
                write_pixels[i] = int(self.pixels[i] / 360 * 255 + 0.5)
                write_pixels[i + 1] = int(self.pixels[i + 1] * 255 + 0.5)
                write_pixels[i + 2] = int(self.pixels[i + 2] * 255 + 0.5)
            file.write(write_pixels)

    @staticmethod
    def read_from_file(file_path):
        with open(file_path, 'rb') as file:
            color_space = file.readline().decode().rstrip('\n')
            width, height = map(int, file.readline().decode().split())
            byte_pixels = bytearray(file.read())
            pixels = [0] * len(byte_pixels)
            for i in range(0, len(byte_pixels), 3):
                pixels[i] = byte_pixels[i] / 255 * 360
                pixels[i + 1] = byte_pixels[i + 1] / 255
                pixels[i + 2] = byte_pixels[i + 2] / 255
            return HSVImage(width, height, pixels)


class YCbCr601Image(AbstractImage):

    def canal(self, canal):
        pixels = bytearray(len(self.pixels) // 3)
        for i in range(canal, len(self.pixels), 3):
            pixels[i // 3] = self.pixels[i]
        return bytecanal(self.width, self.height, pixels)

    def to_rgb(self):
        if self.rgb_pixels is None:
            self.rgb_pixels = ycbcr601_to_rgb(self.pixels)
        return RGBImage(self.width, self.height, self.rgb_pixels)

    def write_to_file(self, file_path):
        with open(file_path, 'wb') as file:
            file.write(f'{__class__.__name__[:-5]}\n'.encode())
            file.write(f'{self.width} {self.height}\n'.encode())
            file.write(self.pixels)

    @staticmethod
    def read_from_file(file_path):
        with open(file_path, 'rb') as file:
            color_space = file.readline().decode().rstrip('\n')
            width, height = map(int, file.readline().decode().split())
            return YCbCr601Image(width, height, bytearray(file.read()))


class YCbCr709Image(AbstractImage):
    def canal(self, canal):
        pixels = bytearray(len(self.pixels) // 3)
        for i in range(canal, len(self.pixels), 3):
            pixels[i // 3] = self.pixels[i]
        return bytecanal(self.width, self.height, pixels)

    def to_rgb(self):
        if self.rgb_pixels is None:
            self.rgb_pixels = ycbcr709_to_rgb(self.pixels)
        return RGBImage(self.width, self.height, self.rgb_pixels)

    def write_to_file(self, file_path):
        with open(file_path, 'wb') as file:
            file.write(f'{__class__.__name__[:-5]}\n'.encode())
            file.write(f'{self.width} {self.height}\n'.encode())
            file.write(self.pixels)

    @staticmethod
    def read_from_file(file_path):
        with open(file_path, 'rb') as file:
            color_space = file.readline().decode().rstrip('\n')
            width, height = map(int, file.readline().decode().split())
            return YCbCr709Image(width, height, bytearray(file.read()))


class YCoCgImage(AbstractImage):

    def canal(self, canal):
        pixels = [self.pixels[i] for i in range(canal, len(self.pixels), 3)]
        if canal == 0:
            return zerotoonecanal(self.width, self.height, pixels)
        else:
            return halftohalfcanal(self.width, self.height, pixels)

    def to_rgb(self):
        if self.rgb_pixels is None:
            self.rgb_pixels = ycocg_to_rgb(self.pixels)
        return RGBImage(self.width, self.height, self.rgb_pixels)

    def write_to_file(self, file_path):
        with open(file_path, 'wb') as file:
            file.write(f'{__class__.__name__[:-5]}\n'.encode())
            file.write(f'{self.width} {self.height}\n'.encode())
            write_pixels = bytearray(len(self.pixels))
            for i in range(0, len(self.pixels), 3):
                write_pixels[i] = int(self.pixels[i] * 255)
                write_pixels[i + 1] = int((self.pixels[i + 1] + 0.5) * 255)
                write_pixels[i + 2] = int((self.pixels[i + 2] + 0.5) * 255)
            file.write(write_pixels)

    @staticmethod
    def read_from_file(file_path):
        with open(file_path, 'rb') as file:
            color_space = file.readline().decode().rstrip('\n')
            width, height = map(int, file.readline().decode().split())
            byte_pixels = bytearray(file.read())
            pixels = [0] * len(byte_pixels)
            for i in range(0, len(byte_pixels), 3):
                pixels[i] = byte_pixels[i] / 255
                pixels[i + 1] = byte_pixels[i + 1] / 255 - 0.5
                pixels[i + 2] = byte_pixels[i + 2] / 255 - 0.5
            return YCoCgImage(width, height, pixels)
